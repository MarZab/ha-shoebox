"""HTTP views: for the panel (pictures at a size, uploads, downloads), for devices (a rotation's
current picture) and for the media browser (a rotation's pictures)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import BinaryIO
from urllib.parse import quote

from aiohttp import BodyPartReader, hdrs, web
from homeassistant.components.http import (
    KEY_AUTHENTICATED,
    KEY_HASS,
    KEY_HASS_USER,
    HomeAssistantView,
    require_admin,
)
from homeassistant.components.image.const import DATA_COMPONENT as IMAGE_COMPONENT
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util import dt as dt_util

from . import imaging, upload
from .const import (
    CONF_PATTERNS,
    DEVICE_IMAGE_URL,
    DOMAIN,
    DOWNLOAD_URL,
    ENTITY_SIZE,
    MAX_SIDE,
    MAX_UPLOAD_BYTES,
    MEDIA_SIZE,
    MEDIA_URL,
    RENDER_URL,
    UPLOAD_URL,
)
from .runtime import Shoebox, loaded_entry, loaded_shoebox, rotations_of

_LOGGER = logging.getLogger(__name__)
_CHUNK = 1024 * 1024


LOOK_HELP = (
    "colors: a palette (" + ", ".join(imaging.PALETTES) + ") or 2 to 256 hex colours;"
    " dither floyd or none; format jpeg, png or bmp;"
    f" contrast, saturation, brightness 0..{imaging.MAX_ENHANCE:g}"
)


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
    """A picture in the chosen media folders, prepared at a size, for the panel's images.

    The panel reaches it with signed URLs (an <img> cannot send the Authorization header).
    Query: path, size=WxH, fit=cover|contain, crop=0 to ignore the crop, and the display options
    of the device URL (colors, dither, format, contrast, saturation, brightness), which the
    panel's display preview tries out. cache=0 prepares the picture without keeping it.
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
            look = imaging.parse_look(q)
        except ValueError:
            return self.json_message(LOOK_HELP, 400)
        try:
            variant = await loaded_shoebox(hass).picture(
                q.get("path", ""),
                width,
                height,
                fit,
                use_crop=q.get("crop") != "0",
                look=look,
                store=q.get("cache") != "0",
            )
        except HomeAssistantError as err:
            return self.json_message(str(err), 404)
        response = jpeg(variant.data, variant.key, 3600)
        response.content_type = look.mime
        return response


class DeviceImageView(HomeAssistantView):
    """The current picture of a rotation, for devices outside Home Assistant.

    The URL stays the same while the rotation advances. Query: width, height (default the entity
    size), fit=cover|contain (default contain). ETag and Last-Modified let a device skip a picture
    it already has.

    A device authenticates as Home Assistant's own image view allows: any logged-in user or
    long-lived token, or ?token= with the image entity's current access token (the one in its
    entity_picture, which Home Assistant changes every 5 minutes and keeps the last two of). A
    device that talks to Home Assistant, such as ESPHome, reads that token and needs no long-lived
    token of its own. The token opens only its own entity. The request URL holds the token: this
    view logs no URLs.
    """

    url = DEVICE_IMAGE_URL
    name = "api:shoebox:image"
    requires_auth = False  # authenticated below, as homeassistant.components.image.ImageView

    async def get(self, request: web.Request, entity_id: str) -> web.StreamResponse:
        hass = request.app[KEY_HASS]
        q = request.query
        rotation_id = self._authenticate(request, entity_id)
        try:
            size = f"{q.get('width', ENTITY_SIZE[0])}x{q.get('height', ENTITY_SIZE[1])}"
            width, height, fit = parse_size(size, q.get("fit", "contain"))
        except ValueError:
            return self.json_message(f"width and height 1..{MAX_SIDE}, fit cover or contain", 400)
        try:
            look = imaging.parse_look(q)
        except ValueError:
            return self.json_message(LOOK_HELP, 400)
        try:
            shoebox = loaded_shoebox(hass)
            state = shoebox.rotations.state(rotation_id)
            if state.file is None:
                return self.json_message("the rotation shows no picture yet", 404)
            # a device that has the picture already gets 304 before anything is prepared
            etag = f'"{await shoebox.picture_key(state.file, width, height, fit, look)}"'
            headers = {hdrs.ETAG: etag, hdrs.CACHE_CONTROL: "no-cache"}
            if updated := dt_util.parse_datetime(state.updated or ""):
                headers[hdrs.LAST_MODIFIED] = updated.strftime("%a, %d %b %Y %H:%M:%S GMT")
            if etag in request.headers.get(hdrs.IF_NONE_MATCH, ""):
                return web.Response(status=304, headers=headers)
            variant = await shoebox.picture(state.file, width, height, fit, look=look)
        except HomeAssistantError as err:
            return self.json_message(str(err), 404)
        headers[hdrs.ETAG] = f'"{variant.key}"'
        return web.Response(body=variant.data, content_type=look.mime, headers=headers)

    @staticmethod
    def _authenticate(request: web.Request, entity_id: str) -> str:
        """The rotation (subentry id) of the image entity, if the request may see it; refusals
        as ImageView's."""
        authenticated: bool = request[KEY_AUTHENTICATED]
        component = request.app[KEY_HASS].data.get(IMAGE_COMPONENT)
        image = component.get_entity(entity_id) if component else None
        entry = image.registry_entry if image else None
        if (
            image is None
            or entry is None
            or entry.platform != DOMAIN
            or not entry.config_subentry_id
        ):
            # not ours or not there: only a logged-in caller learns which
            raise web.HTTPNotFound if authenticated else web.HTTPUnauthorized
        if authenticated or request.query.get("token") in image.access_tokens:
            return entry.config_subentry_id
        if hdrs.AUTHORIZATION in request.headers:
            raise web.HTTPUnauthorized  # a wrong login: the ban middleware counts it
        raise web.HTTPForbidden  # an expired or wrong token: not a login attempt


class MediaView(HomeAssistantView):
    """A picture of a rotation, for the media browser and media players.

    Media players fetch it with a URL that Home Assistant signs for its content user, so any user
    may fetch it; only pictures the rotation selects are served.
    """

    url = MEDIA_URL
    name = "api:shoebox:media"
    requires_auth = True

    async def get(self, request: web.Request, rotation_id: str, path: str) -> web.StreamResponse:
        hass = request.app[KEY_HASS]
        thumb = request.query.get("thumb") == "1"
        try:
            shoebox = loaded_shoebox(hass)
            entry = loaded_entry(hass)
            rotation = rotations_of(entry).get(rotation_id) if entry else None
            if rotation is None:
                return self.json_message("no such rotation", 404)
            patterns = rotation.data.get(CONF_PATTERNS, [])
            if not await shoebox.run(shoebox.library.selects, path, patterns):
                return self.json_message("not a picture of this rotation", 404)
            if thumb:
                variant = await shoebox.picture(path, 320, 320, "cover")
            else:
                variant = await shoebox.picture(path, *MEDIA_SIZE, "contain")
        except HomeAssistantError as err:
            return self.json_message(str(err), 404)
        return jpeg(variant.data, variant.key, 3600)


class DownloadView(HomeAssistantView):
    """A file from the chosen media folders, as it is: ?path=<path>. Admins only, like the panel.

    The panel saves files through a signed URL, and reads the start of text files with a Range
    request through fetchWithAuth.
    """

    url = DOWNLOAD_URL
    name = "api:shoebox:download"
    requires_auth = True

    @require_admin
    async def get(self, request: web.Request) -> web.StreamResponse:
        hass = request.app[KEY_HASS]
        try:
            shoebox = loaded_shoebox(hass)
            real = await shoebox.run(shoebox.library.resolve_file, request.query.get("path", ""))
        except HomeAssistantError as err:
            return self.json_message(str(err), 404)
        disposition = f"attachment; filename*=UTF-8''{quote(real.name)}"
        return web.FileResponse(real, headers={hdrs.CONTENT_DISPOSITION: disposition})


class _TooLarge(Exception):
    pass


class UploadView(HomeAssistantView):
    """POST multipart/form-data with a part named "file" to ?folder=<folder>, such as local/Family.

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
                shoebox.library.upload_folder, request.query.get("folder", "")
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
            return await shoebox.run(shoebox.library.finish_upload, folder, tmp, name)
        finally:
            await hass.async_add_executor_job(_discard, f, tmp)


def _open(fd: int) -> BinaryIO:
    return open(fd, "wb")


def _discard(f: BinaryIO, tmp: Path) -> None:
    """Close the file and remove the temporary file, if they are still there."""
    f.close()
    tmp.unlink(missing_ok=True)
