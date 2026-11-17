"""The running integration: the media folder and the cache of prepared pictures."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant

from .cache import VariantCache
from .const import (
    CACHE_FOLDER,
    CONF_CACHE_SIZE,
    CONF_SHOW_IN_SIDEBAR,
    DEFAULT_CACHE_SIZE_MB,
)

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
