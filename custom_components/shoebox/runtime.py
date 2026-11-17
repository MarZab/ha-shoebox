"""The running integration: the media folder and the cache of prepared pictures."""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Mapping
from functools import partial
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError

from . import imaging, media
from .cache import Variant, VariantCache
from .const import (
    CACHE_FOLDER,
    CONCURRENT_RENDERS,
    CONF_CACHE_SIZE,
    CONF_SHOW_IN_SIDEBAR,
    DEFAULT_CACHE_SIZE_MB,
    DOMAIN,
)
from .errors import ShoeboxError
from .rotations import Rotations

MB = 1024 * 1024


def media_root(hass: HomeAssistant) -> Path:
    """Home Assistant's local media folder ("My media")."""
    return Path(hass.config.media_dirs.get("local") or hass.config.path("media"))


def variant_cache(hass: HomeAssistant, options: Mapping[str, Any]) -> VariantCache:
    size_mb = int(options.get(CONF_CACHE_SIZE, DEFAULT_CACHE_SIZE_MB))
    return VariantCache(Path(hass.config.path(CACHE_FOLDER)), size_mb * MB)


class Shoebox:
    def __init__(self, hass: HomeAssistant, options: Mapping[str, Any]) -> None:
        self.hass = hass
        self.root = media_root(hass)
        self.cache = variant_cache(hass, options)
        self.show_in_sidebar = bool(options.get(CONF_SHOW_IN_SIDEBAR, True))
        self._renders = asyncio.Semaphore(CONCURRENT_RENDERS)
        self.rotations = Rotations(hass, self.root, self.run)

    async def picture(
        self, path: str, width: int, height: int, fit: imaging.Fit, *, use_crop: bool = True
    ) -> Variant:
        """A picture below the media folder prepared at a size, through the cache."""
        source = await self.run(media.resolve_file, self.root, path)
        make = partial(imaging.render, source, width, height, fit, use_crop)
        async with self._renders:
            return await self.run(
                self.cache.get, source, width, height, fit, make, "" if use_crop else "nocrop"
            )

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
                    "path": str(err.filename or ""),
                },
            ) from err
