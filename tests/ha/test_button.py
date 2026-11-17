from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from ..conftest import Tree
from .conftest import rotation_id

BUTTON = "button.evening_next"


async def press(hass: HomeAssistant) -> None:
    await hass.services.async_call("button", "press", {"entity_id": BUTTON}, blocking=True)
    await hass.async_block_till_done()


async def test_next_advances_the_rotation(
    hass: HomeAssistant, with_rotation: MockConfigEntry, tree: Tree
) -> None:
    tree("evening/a.jpg", "evening/b.jpg")
    await press(hass)
    assert hass.states.get("image.evening").attributes["file"] == "local/evening/a.jpg"  # type: ignore[union-attr]
    await press(hass)
    image = hass.states.get("image.evening")
    assert image is not None
    assert (image.attributes["file"], image.attributes["position"]) == ("local/evening/b.jpg", 2)


async def test_button_lives_and_goes_with_its_rotation(
    hass: HomeAssistant, with_rotation: MockConfigEntry, entity_registry: er.EntityRegistry
) -> None:
    rid = rotation_id(with_rotation)
    entry = entity_registry.async_get(BUTTON)
    assert entry is not None
    assert (entry.unique_id, entry.config_subentry_id, entry.translation_key) == (
        f"{rid}_next",
        rid,
        "next",
    )
    hass.config_entries.async_remove_subentry(with_rotation, rid)
    await hass.async_block_till_done()
    assert entity_registry.async_get(BUTTON) is None
