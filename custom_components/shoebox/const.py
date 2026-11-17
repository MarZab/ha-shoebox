"""Constants for Shoebox."""

from __future__ import annotations

from typing import Final

DOMAIN: Final = "shoebox"
TITLE: Final = "Shoebox"
PANEL_ICON: Final = "mdi:image-album"

CONF_CACHE_SIZE: Final = "cache_size"
CONF_CLEAR_CACHE: Final = "clear_cache"
CONF_SHOW_IN_SIDEBAR: Final = "show_in_sidebar"
DEFAULT_CACHE_SIZE_MB: Final = 512
MIN_CACHE_SIZE_MB: Final = 0

# Prepared pictures; Home Assistant backups leave out ".cache"
CACHE_FOLDER: Final = ".cache/" + DOMAIN
