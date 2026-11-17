"""HTTP views of the panel: pictures prepared at a size, and uploads into the media folder."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import BinaryIO

from aiohttp import BodyPartReader, hdrs, web
from homeassistant.components.http import (
    KEY_HASS,
    KEY_HASS_USER,
    HomeAssistantView,
    require_admin,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from . import imaging, upload
from .const import DOMAIN, MAX_SIDE, MAX_UPLOAD_BYTES, RENDER_URL, UPLOAD_URL
from .runtime import Shoebox

_LOGGER = logging.getLogger(__name__)
_CHUNK = 1024 * 1024


def loaded_shoebox(hass: HomeAssistant) -> Shoebox:
    if entries := hass.config_entries.async_loaded_entries(DOMAIN):
        shoebox: Shoebox = entries[0].runtime_data
        return shoebox
    raise ServiceValidationError(translation_domain=DOMAIN, translation_key="not_loaded")


def parse_size(size: str, fit: str) -> tuple[int, int, imaging.Fit]:
    """Width and height from "WxH", and the fit; ValueError when out of range."""
    width, height = (int(v) for v in size.split("x"))
    if not (0 < width <= MAX_SIDE and 0 < height <= MAX_SIDE):
        raise ValueError(size)
    if fit == "cover":
        return width, height, "cover"
    if fit == "contain":
        return width, height, "contain"
    raise ValueError(fit)


def jpeg(data: bytes, etag: str, max_age: int) -> web.Response:
    return web.Response(
        body=data,
        content_type="image/jpeg",
        headers={hdrs.CACHE_CONTROL: f"private, max-age={max_age}", hdrs.ETAG: f'"{etag}"'},
    )


class RenderView(HomeAssistantView):
    """A picture below the media folder, prepared at a size, for the panel's images.

    The panel reaches it with signed URLs (an <img> cannot send the Authorization header).
    Query: path, size=WxH, fit=cover|contain, crop=0 to ignore the crop.
    """

    url = RENDER_URL
    name = "api:shoebox:render"
    requires_auth = True

    @require_admin
    async def get(self, request: web.Request) -> web.Response:
        hass = request.app[KEY_HASS]
        q = request.query
        try:
            width, height, fit = parse_size(q.get("size", ""), q.get("fit", "contain"))
        except ValueError:
            return self.json_message(f"size is WxH (1..{MAX_SIDE}), fit cover or contain", 400)
        try:
            variant = await loaded_shoebox(hass).picture(
                q.get("path", ""), width, height, fit, use_crop=q.get("crop") != "0"
            )
        except HomeAssistantError as err:
            return self.json_message(str(err), 404)
        return jpeg(variant.data, variant.key, 3600)


class _TooLarge(Exception):
    pass


class UploadView(HomeAssistantView):
    """POST multipart/form-data with a part named "file" to ?folder=<folder below the media folder>.

    The declared type must be a picture, video or audio. The body streams into a hidden temporary
    file in the folder, which then moves to a free name: an existing file is never replaced.
    """

    url = UPLOAD_URL
    name = "api:shoebox:upload"
    requires_auth = True

    @require_admin
    async def post(self, request: web.Request) -> web.Response:
        hass = request.app[KEY_HASS]
        too_large = f"larger than {MAX_UPLOAD_BYTES // 1024 // 1024} MB"
        if request.content_length and request.content_length > MAX_UPLOAD_BYTES + _CHUNK:
            return self.json_message(too_large, 413)
        try:
            shoebox = loaded_shoebox(hass)
            if not request.content_type.startswith("multipart/"):
                return self.json_message("send multipart/form-data with a part named file", 400)
            folder = await shoebox.run(
                upload.target_folder, shoebox.root, request.query.get("folder", "")
            )
            reader = await request.multipart()
            part = await reader.next()
            while part is not None and not (
                isinstance(part, BodyPartReader) and part.name == "file"
            ):
                part = await reader.next()
            if not isinstance(part, BodyPartReader) or not part.filename:
                return self.json_message("no file: send a multipart part named file", 400)
            name = await shoebox.run(upload.safe_name, part.filename)
            await shoebox.run(upload.check_type, name, part.headers.get(hdrs.CONTENT_TYPE))
            rel = await self._store(shoebox, part, folder, name)
        except HomeAssistantError as err:
            return self.json_message(str(err), 400)
        except _TooLarge:
            return self.json_message(too_large, 413)
        _LOGGER.info("%s uploaded %s", request[KEY_HASS_USER].name, rel)
        return self.json({"path": rel})

    @staticmethod
    async def _store(shoebox: Shoebox, part: BodyPartReader, folder: Path, name: str) -> str:
        hass = shoebox.hass
        fd, tmp = await shoebox.run(upload.temp_file, folder)
        f = await hass.async_add_executor_job(_open, fd)
        try:
            size = 0
            while chunk := await part.read_chunk(_CHUNK):
                size += len(chunk)
                if size > MAX_UPLOAD_BYTES:
                    raise _TooLarge
                await hass.async_add_executor_job(f.write, chunk)
            await hass.async_add_executor_job(f.close)
            return await shoebox.run(upload.finish, shoebox.root, folder, tmp, name)
        finally:
            await hass.async_add_executor_job(_discard, f, tmp)


def _open(fd: int) -> BinaryIO:
    return open(fd, "wb")


def _discard(f: BinaryIO, tmp: Path) -> None:
    """Close the file and remove the temporary file, if they are still there."""
    f.close()
    tmp.unlink(missing_ok=True)
