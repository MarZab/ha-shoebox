"""The running integration: the media folder and the cache of prepared pictures."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Mapping
from functools import partial
import os
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from . import imaging
from .cache import Variant, VariantCache
from .const import (
    CACHE_FOLDER,
    CONCURRENT_RENDERS,
    CONF_CACHE_SIZE,
    CONF_FOLDERS,
    CONF_SHOW_IN_SIDEBAR,
    DEFAULT_CACHE_SIZE_MB,
    DEFAULT_FOLDERS,
    DOMAIN,
)
from .errors import MediaError, ShoeboxError
from .library import Library
from .rotations import Rotations

MB = 1024 * 1024


def chosen_folders(options: Mapping[str, Any]) -> list[str]:
    return list(options.get(CONF_FOLDERS, DEFAULT_FOLDERS))


def media_folders(hass: HomeAssistant, options: Mapping[str, Any]) -> dict[str, Path]:
    """The chosen media folders that Home Assistant knows, by name ("local" is My media)."""
    known = hass.config.media_dirs
    return {name: Path(known[name]) for name in chosen_folders(options) if name in known}


def variant_cache(hass: HomeAssistant, options: Mapping[str, Any]) -> VariantCache:
    size_mb = int(options.get(CONF_CACHE_SIZE, DEFAULT_CACHE_SIZE_MB))
    return VariantCache(Path(hass.config.path(CACHE_FOLDER)), size_mb * MB)


class Shoebox:
    def __init__(self, hass: HomeAssistant, options: Mapping[str, Any]) -> None:
        self.hass = hass
        self.library = Library(media_folders(hass, options))
        self.cache = variant_cache(hass, options)
        self.show_in_sidebar = bool(options.get(CONF_SHOW_IN_SIDEBAR, True))
        self._renders = asyncio.Semaphore(CONCURRENT_RENDERS)
        self.rotations = Rotations(hass, self.library, self.run)

    async def picture(
        self, path: str, width: int, height: int, fit: imaging.Fit, *, use_crop: bool = True
    ) -> Variant:
        """A picture in a media folder prepared at a size, through the cache."""
        source = await self.run(self.library.resolve_file, path)
        make = partial(imaging.render, source, width, height, fit, use_crop)
        async with self._renders:
            return await self.run(
                self.cache.get, source, width, height, fit, make, "" if use_crop else "nocrop"
            )

    def _shown(self, filename: object) -> str:
        """A path for messages: prefixed below a media folder, else only its name; never the
        host's layout, which non-admin users of the device and media views would see."""
        if not filename:
            return ""
        path = Path(os.fsdecode(filename))  # type: ignore[arg-type]  # str, bytes or PathLike
        try:
            return self.library.relative(path)
        except MediaError:
            return path.name

    async def run[T](self, func: Callable[..., T], *args: Any) -> T:
        """Run file or picture work in the executor; its errors become translated HA errors."""
        try:
            return await self.hass.async_add_executor_job(func, *args)
        except ShoeboxError as err:
            raise ServiceValidationError(
                translation_domain=DOMAIN,
                translation_key=err.key,
                translation_placeholders=err.placeholders,
            ) from err
        except OSError as err:
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="file_error",
                translation_placeholders={
                    "error": err.strerror or str(err),
                    "path": self._shown(err.filename),
                },
            ) from err
