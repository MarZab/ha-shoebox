from __future__ import annotations

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr, entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from custom_components.shoebox.const import DOMAIN

from ..conftest import Tree
from ..images import colour_at
from .conftest import rotation_id

ENTITY = "image.evening"


async def test_device_and_entity_per_rotation(
    hass: HomeAssistant,
    with_rotation: MockConfigEntry,
    device_registry: dr.DeviceRegistry,
    entity_registry: er.EntityRegistry,
) -> None:
    rid = rotation_id(with_rotation)
    device = device_registry.async_get_device_by_identifier((DOMAIN, rid), with_rotation.entry_id)
    assert device is not None
    assert (device.name, device.entry_type) == ("Evening", dr.DeviceEntryType.SERVICE)
    entity = entity_registry.async_get(ENTITY)
    assert entity is not None
    assert (entity.unique_id, entity.device_id, entity.config_subentry_id) == (rid, device.id, rid)

    hass.config_entries.async_update_subentry(
        with_rotation, with_rotation.subentries[rid], title="Night"
    )
    await hass.async_block_till_done()
    assert (
        device_registry.async_get_device_by_identifier((DOMAIN, rid), with_rotation.entry_id).name
        == "Night"
    )  # type: ignore[union-attr]
    assert hass.states.get(ENTITY) is not None


async def test_deleting_the_rotation_removes_device_and_entity(
    hass: HomeAssistant,
    with_rotation: MockConfigEntry,
    device_registry: dr.DeviceRegistry,
    entity_registry: er.EntityRegistry,
) -> None:
    rid = rotation_id(with_rotation)
    hass.config_entries.async_remove_subentry(with_rotation, rid)
    await hass.async_block_till_done()
    assert (
        device_registry.async_get_device_by_identifier((DOMAIN, rid), with_rotation.entry_id)
        is None
    )
    assert entity_registry.async_get(ENTITY) is None


async def test_image_shows_the_current_picture(
    hass: HomeAssistant,
    with_rotation: MockConfigEntry,
    tree: Tree,
    hass_client: ClientSessionGenerator,
) -> None:
    tree("evening/a.jpg", "evening/b.jpg")
    client = await hass_client()
    assert (await client.get(f"/api/image_proxy/{ENTITY}")).status == 500  # nothing shown yet
    await with_rotation.runtime_data.rotations.async_advance(
        rotation_id(with_rotation), ["local/evening/*"]
    )
    await hass.async_block_till_done()
    response = await client.get(f"/api/image_proxy/{ENTITY}")
    assert response.status == 200
    data = await response.read()
    assert colour_at(data, 0.25, 0.25) == "red"
    state = hass.states.get(ENTITY)
    assert state is not None
    assert state.attributes["file"] == "local/evening/a.jpg"
    assert (state.attributes["position"], state.attributes["count"]) == (1, 2)
    assert (state.attributes["patterns"], state.attributes["pattern"]) == (
        ["local/evening/*"],
        "local/evening/*",
    )


async def test_last_updated_follows_steps_and_edits(
    hass: HomeAssistant, with_rotation: MockConfigEntry, tree: Tree
) -> None:
    tree("evening/a.jpg")
    rid = rotation_id(with_rotation)
    await with_rotation.runtime_data.rotations.async_advance(rid, ["local/evening/*"])
    await hass.async_block_till_done()
    first = hass.states.get(ENTITY).state  # type: ignore[union-attr]
    assert first not in ("unknown", "unavailable")
    await hass.services.async_call(
        DOMAIN, "rotate", {"path": "local/evening/a.jpg", "by": 90}, blocking=True
    )
    await hass.async_block_till_done()
    assert hass.states.get(ENTITY).state > first  # type: ignore[union-attr]
