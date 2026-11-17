"""The sidebar panel: its files, served once, and its registration while Show in sidebar is on.

The files are served below a version (a hash of their contents), so a browser never keeps an old
panel after an update.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Final

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant, callback

from .const import PANEL_ELEMENT, PANEL_ICON, PANEL_URL_PATH, STATIC_URL, TITLE

FRONTEND: Final = Path(__file__).parent / "frontend"


def frontend_version() -> str:
    h = hashlib.sha256()
    for path in sorted(FRONTEND.rglob("*")):
        if path.is_file():
            h.update(path.relative_to(FRONTEND).as_posix().encode() + b"\0" + path.read_bytes())
    return h.hexdigest()[:12]


async def async_serve_frontend(hass: HomeAssistant) -> str:
    """Serve the panel's files; returns the version in their URL."""
    version = await hass.async_add_executor_job(frontend_version)
    await hass.http.async_register_static_paths(
        [StaticPathConfig(f"{STATIC_URL}/{version}", str(FRONTEND), cache_headers=True)]
    )
    return version


async def async_register_panel(hass: HomeAssistant, version: str) -> None:
    await panel_custom.async_register_panel(
        hass,
        frontend_url_path=PANEL_URL_PATH,
        webcomponent_name=PANEL_ELEMENT,
        sidebar_title=TITLE,
        sidebar_icon=PANEL_ICON,
        module_url=f"{STATIC_URL}/{version}/{PANEL_ELEMENT}.js",
        require_admin=True,
        config={"version": version},
    )


@callback
def async_remove_panel(hass: HomeAssistant) -> None:
    frontend.async_remove_panel(hass, PANEL_URL_PATH, warn_if_unknown=False)
