"""Shoebox: media manager and picture organizer for Home Assistant."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType
from homeassistant.util.hass_dict import HassKey

from .const import DOMAIN
from .panel import async_register_panel, async_remove_panel, async_serve_frontend
from .runtime import Shoebox
from .services import async_setup_services
from .views import RenderView, UploadView
from .websocket import async_setup_websocket

DATA_FRONTEND_VERSION: HassKey[str] = HassKey(f"{DOMAIN}_frontend_version")

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type ShoeboxConfigEntry = ConfigEntry[Shoebox]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    async_setup_services(hass)
    async_setup_websocket(hass)
    hass.http.register_view(RenderView())
    hass.http.register_view(UploadView())
    hass.data[DATA_FRONTEND_VERSION] = await async_serve_frontend(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ShoeboxConfigEntry) -> bool:
    shoebox = Shoebox(hass, entry.options)
    await hass.async_add_executor_job(shoebox.cache.evict)
    entry.runtime_data = shoebox
    if shoebox.show_in_sidebar:
        await async_register_panel(hass, hass.data[DATA_FRONTEND_VERSION])
        entry.async_on_unload(lambda: async_remove_panel(hass))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ShoeboxConfigEntry) -> bool:
    return True
