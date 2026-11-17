from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from custom_components.shoebox.const import DOMAIN

from ..conftest import Tree
from ..images import colour_at
from .conftest import rotation_id

IMAGE = "image.evening"
NEXT = "button.evening_next"


async def press(hass: HomeAssistant) -> None:
    await hass.services.async_call("button", "press", {"entity_id": NEXT}, blocking=True)
    await hass.async_block_till_done()


async def test_a_device_with_an_image_and_a_next_button_per_rotation(
    hass: HomeAssistant,
    with_rotation: MockConfigEntry,
    device_registry: dr.DeviceRegistry,
    entity_registry: er.EntityRegistry,
) -> None:
    rid = rotation_id(with_rotation)
    device = device_registry.async_get_device_by_identifier((DOMAIN, rid), with_rotation.entry_id)
    assert device is not None
    assert (device.name, device.entry_type) == ("Evening", dr.DeviceEntryType.SERVICE)
    for entity_id in (IMAGE, NEXT):
        entry = entity_registry.async_get(entity_id)
        assert entry is not None
        assert (entry.device_id, entry.config_subentry_id) == (device.id, rid)

    hass.config_entries.async_update_subentry(
        with_rotation, with_rotation.subentries[rid], title="Night"
    )
    await hass.async_block_till_done()
    renamed = device_registry.async_get_device_by_identifier((DOMAIN, rid), with_rotation.entry_id)
    assert renamed is not None
    assert renamed.name == "Night"
    assert hass.states.get(IMAGE) is not None  # the entity id stays

    hass.config_entries.async_remove_subentry(with_rotation, rid)
    await hass.async_block_till_done()
    assert (
        device_registry.async_get_device_by_identifier((DOMAIN, rid), with_rotation.entry_id)
        is None
    )
    assert entity_registry.async_get(IMAGE) is None
    assert entity_registry.async_get(NEXT) is None


async def test_next_shows_the_next_picture(
    hass: HomeAssistant,
    with_rotation: MockConfigEntry,
    tree: Tree,
    hass_client: ClientSessionGenerator,
) -> None:
    tree("evening/a.jpg", "evening/b.jpg")
    client = await hass_client()
    assert (await client.get(f"/api/image_proxy/{IMAGE}")).status == 500  # nothing shown yet
    await press(hass)
    response = await client.get(f"/api/image_proxy/{IMAGE}")
    assert response.status == 200
    assert colour_at(await response.read(), 0.25, 0.25) == "red"
    await press(hass)
    state = hass.states.get(IMAGE)
    assert state is not None
    assert {k: state.attributes[k] for k in ("file", "position", "count", "patterns")} == {
        "file": "local/evening/b.jpg",
        "position": 2,
        "count": 2,
        "patterns": ["local/evening/*"],
    }


async def test_editing_the_current_picture_updates_the_image(
    hass: HomeAssistant, with_rotation: MockConfigEntry, tree: Tree
) -> None:
    tree("evening/a.jpg")
    await press(hass)
    first = hass.states.get(IMAGE).state  # type: ignore[union-attr]
    await hass.services.async_call(
        DOMAIN, "rotate", {"path": "local/evening/a.jpg", "by": 90}, blocking=True
    )
    await hass.async_block_till_done()
    assert hass.states.get(IMAGE).state > first  # type: ignore[union-attr]


@pytest.mark.parametrize(
    ("action", "data", "file"),
    [
        ("rename", {"path": "local/evening/a.jpg", "name": "c.jpg"}, "local/evening/c.jpg"),
        ("move", {"path": "local/evening", "to": "local/other"}, "local/other/evening/a.jpg"),
        ("delete", {"path": "local/evening/a.jpg"}, None),
    ],
)
async def test_the_rotation_follows_its_picture(
    hass: HomeAssistant,
    with_rotation: MockConfigEntry,
    tree: Tree,
    action: str,
    data: dict[str, Any],
    file: str | None,
) -> None:
    tree("evening/a.jpg", "evening/b.jpg", "other/")
    await press(hass)
    await hass.services.async_call(DOMAIN, action, data, blocking=True, return_response=True)
    await hass.async_block_till_done()
    state = hass.states.get(IMAGE)
    assert state is not None
    assert state.attributes["file"] == file
