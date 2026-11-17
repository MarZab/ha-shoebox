from __future__ import annotations

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import DOMAIN as HOMEASSISTANT_DOMAIN, HomeAssistant
from homeassistant.helpers import issue_registry as ir
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.shoebox.const import DOMAIN


async def test_setup_unload_and_reload(hass: HomeAssistant, loaded: MockConfigEntry) -> None:
    assert loaded.state is ConfigEntryState.LOADED
    assert loaded.runtime_data.root.name == "media"
    assert await hass.config_entries.async_reload(loaded.entry_id)
    assert loaded.state is ConfigEntryState.LOADED
    assert await hass.config_entries.async_unload(loaded.entry_id)
    assert loaded.state is ConfigEntryState.NOT_LOADED


async def test_yaml_raises_a_repair_issue(
    hass: HomeAssistant, issue_registry: ir.IssueRegistry
) -> None:
    assert await async_setup_component(hass, DOMAIN, {DOMAIN: {}})
    assert issue_registry.async_get_issue(HOMEASSISTANT_DOMAIN, f"config_entry_only_{DOMAIN}")
