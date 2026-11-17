"""Shoebox: media manager and picture organizer for Home Assistant."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.storage import Store
from homeassistant.helpers.typing import ConfigType
from homeassistant.util.hass_dict import HassKey

from .const import DOMAIN, STORAGE_KEY, STORAGE_VERSION, SUBENTRY_ROTATION
from .panel import async_register_panel, async_remove_panel, async_serve_frontend
from .runtime import Shoebox, variant_cache
from .services import async_setup_services
from .views import DeviceImageView, MediaView, RenderView, UploadView
from .websocket import async_setup_websocket

DATA_FRONTEND_VERSION: HassKey[str] = HassKey(f"{DOMAIN}_frontend_version")

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
PLATFORMS = [Platform.BUTTON, Platform.IMAGE]

type ShoeboxConfigEntry = ConfigEntry[Shoebox]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    async_setup_services(hass)
    async_setup_websocket(hass)
    hass.http.register_view(RenderView())
    hass.http.register_view(UploadView())
    hass.http.register_view(DeviceImageView())
    hass.http.register_view(MediaView())
    hass.data[DATA_FRONTEND_VERSION] = await async_serve_frontend(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ShoeboxConfigEntry) -> bool:
    shoebox = Shoebox(hass, entry.options)
    if not await hass.async_add_executor_job(shoebox.root.is_dir):
        raise ConfigEntryNotReady(
            translation_domain=DOMAIN,
            translation_key="media_folder_missing",
            translation_placeholders={"path": str(shoebox.root)},
        )
    await hass.async_add_executor_job(shoebox.cache.evict)
    await shoebox.rotations.async_load(
        sub.subentry_id
        for sub in entry.subentries.values()
        if sub.subentry_type == SUBENTRY_ROTATION
    )
    entry.runtime_data = shoebox
    entry.async_on_unload(entry.add_update_listener(_async_reload))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    if shoebox.show_in_sidebar:
        await async_register_panel(hass, hass.data[DATA_FRONTEND_VERSION])
        entry.async_on_unload(lambda: async_remove_panel(hass))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ShoeboxConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    await entry.runtime_data.rotations.async_save()
    return unloaded


async def async_remove_entry(hass: HomeAssistant, entry: ShoeboxConfigEntry) -> None:
    """Removing the integration removes its rotation state and cache; media files stay."""
    await Store[dict[str, object]](hass, STORAGE_VERSION, STORAGE_KEY).async_remove()
    await hass.async_add_executor_job(variant_cache(hass, entry.options).clear)


async def _async_reload(hass: HomeAssistant, entry: ShoeboxConfigEntry) -> None:
    """Options or rotations changed."""
    await hass.config_entries.async_reload(entry.entry_id)
