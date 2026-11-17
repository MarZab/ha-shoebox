from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.components.diagnostics import (
    get_diagnostics_for_config_entry,
)
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from ..conftest import Tree


async def test_diagnostics(
    hass: HomeAssistant,
    with_rotation: MockConfigEntry,
    tree: Tree,
    hass_client: ClientSessionGenerator,
) -> None:
    tree("evening/secret-name.jpg")
    assert await async_setup_component(hass, "diagnostics", {})
    await hass.services.async_call(
        "button", "press", {"entity_id": "button.evening_next"}, blocking=True
    )
    result = await get_diagnostics_for_config_entry(hass, hass_client, with_rotation)
    assert result["options"] == {}
    assert result["cache"]["files"] == 0
    assert result["cache"]["limit_bytes"] == 512 * 1024 * 1024
    rotation = result["rotations"][0]
    assert (rotation["patterns"], rotation["position"], rotation["count"]) == (
        ["local/evening/*"],
        1,
        1,
    )
    assert "secret-name" not in str(result)
