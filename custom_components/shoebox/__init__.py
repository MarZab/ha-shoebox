"""Shoebox: media manager and picture organizer for Home Assistant."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .runtime import Shoebox
from .services import async_setup_services

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

type ShoeboxConfigEntry = ConfigEntry[Shoebox]


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    async_setup_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ShoeboxConfigEntry) -> bool:
    shoebox = Shoebox(hass, entry.options)
    await hass.async_add_executor_job(shoebox.cache.evict)
    entry.runtime_data = shoebox
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ShoeboxConfigEntry) -> bool:
    return True
