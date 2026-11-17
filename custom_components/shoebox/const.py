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

PANEL_URL_PATH: Final = "shoebox"
PANEL_ELEMENT: Final = "shoebox-panel"
STATIC_URL: Final = "/shoebox_static"
RENDER_URL: Final = "/api/shoebox/render"
UPLOAD_URL: Final = "/api/shoebox/upload"
# How long the panel's picture URLs work; it asks for new ones whenever it lists a folder again
PANEL_URL_LIFETIME_S: Final = 3600
MAX_SIDE: Final = 4096
# Uploads larger than this are refused; phone photos and short videos fit well within it
MAX_UPLOAD_BYTES: Final = 200 * 1024 * 1024
# Pictures prepared at the same time; more requests wait, so thumbnails cannot exhaust a small host
CONCURRENT_RENDERS: Final = 2
