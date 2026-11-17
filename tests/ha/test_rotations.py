from __future__ import annotations

from typing import Any

from homeassistant.config_entries import SOURCE_RECONFIGURE, SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.shoebox.const import SUBENTRY_ROTATION

from ..conftest import Tree
from .conftest import rotation_id


async def subentry_flow(
    hass: HomeAssistant, entry: MockConfigEntry, **context: Any
) -> dict[str, Any]:
    result = await hass.config_entries.subentries.async_init(
        (entry.entry_id, SUBENTRY_ROTATION), context={"source": SOURCE_USER} | context
    )
    return dict(result)


async def test_add_rotation_with_preview(
    hass: HomeAssistant, loaded: MockConfigEntry, tree: Tree
) -> None:
    tree("evening/a.jpg", "evening/b.jpg", "evening/c.txt")
    flow = await subentry_flow(hass, loaded)
    assert flow["step_id"] == "user"
    flow = await hass.config_entries.subentries.async_configure(
        flow["flow_id"], {"name": " Living room ", "patterns": ["morning/*", " evening/* ", ""]}
    )
    assert flow["step_id"] == "preview"
    assert flow["description_placeholders"] == {
        "count": "2",
        "pattern": "evening/*",
        "examples": "- evening/a.jpg\n- evening/b.jpg",
    }
    flow = await hass.config_entries.subentries.async_configure(flow["flow_id"], {})
    await hass.async_block_till_done()
    assert flow["type"] is FlowResultType.CREATE_ENTRY
    sub = next(iter(loaded.subentries.values()))
    assert (sub.title, dict(sub.data)) == ("Living room", {"patterns": ["morning/*", "evening/*"]})


@pytest.mark.parametrize(
    ("patterns", "error"), [(["re:("], "invalid_pattern"), ([" "], "no_pattern")]
)
async def test_add_rotation_refuses_bad_patterns(
    hass: HomeAssistant, loaded: MockConfigEntry, patterns: list[str], error: str
) -> None:
    flow = await subentry_flow(hass, loaded)
    flow = await hass.config_entries.subentries.async_configure(
        flow["flow_id"], {"name": "x", "patterns": patterns}
    )
    assert flow["errors"] == {"patterns": error}


async def test_preview_without_matches(hass: HomeAssistant, loaded: MockConfigEntry) -> None:
    flow = await subentry_flow(hass, loaded)
    flow = await hass.config_entries.subentries.async_configure(
        flow["flow_id"], {"name": "x", "patterns": ["nothing/*"]}
    )
    assert flow["description_placeholders"] == {"count": "0", "pattern": "-", "examples": "-"}


async def test_reconfigure_keeps_the_state(
    hass: HomeAssistant, with_rotation: MockConfigEntry, tree: Tree
) -> None:
    tree("evening/a.jpg", "night/b.jpg")
    rid = rotation_id(with_rotation)
    await with_rotation.runtime_data.rotations.async_advance(rid, ["evening/*"])
    flow = await subentry_flow(hass, with_rotation, source=SOURCE_RECONFIGURE, subentry_id=rid)
    assert flow["data_schema"]({})["patterns"] == ["evening/*"]
    flow = await hass.config_entries.subentries.async_configure(
        flow["flow_id"], {"name": "Night", "patterns": ["night/*"]}
    )
    flow = await hass.config_entries.subentries.async_configure(flow["flow_id"], {})
    await hass.async_block_till_done()
    assert flow["reason"] == "reconfigure_successful"
    assert with_rotation.subentries[rid].title == "Night"
    assert with_rotation.runtime_data.rotations.state(rid).file == "evening/a.jpg"


async def test_rotation_steps_wraps_and_survives_removed_files(
    hass: HomeAssistant, with_rotation: MockConfigEntry, tree: Tree
) -> None:
    root = tree("evening/a.jpg", "evening/b.jpg", "evening/c.jpg", "evening/notes.txt")
    rotations = with_rotation.runtime_data.rotations
    rid = rotation_id(with_rotation)
    steps = [(await rotations.async_advance(rid, ["evening/*"])).file for _ in range(4)]
    assert steps == ["evening/a.jpg", "evening/b.jpg", "evening/c.jpg", "evening/a.jpg"]
    (root / "evening/b.jpg").unlink()
    (root / "evening/a.jpg").unlink()
    state = await rotations.async_advance(rid, ["evening/*"])
    assert (state.file, state.position, state.count, state.pattern) == (
        "evening/c.jpg",
        1,
        1,
        "evening/*",
    )


async def test_rotation_falls_back_and_empties(
    hass: HomeAssistant, with_rotation: MockConfigEntry, tree: Tree
) -> None:
    tree("night/a.jpg")
    rotations = with_rotation.runtime_data.rotations
    rid = rotation_id(with_rotation)
    assert (await rotations.async_advance(rid, ["evening/*", "night/*"])).file == "night/a.jpg"
    state = await rotations.async_advance(rid, ["morning/*"])
    assert (state.file, state.position, state.count, state.pattern) == (None, 0, 0, None)


async def test_state_survives_a_reload(
    hass: HomeAssistant, with_rotation: MockConfigEntry, tree: Tree
) -> None:
    tree("evening/a.jpg", "evening/b.jpg")
    rid = rotation_id(with_rotation)
    await with_rotation.runtime_data.rotations.async_advance(rid, ["evening/*"])
    assert await hass.config_entries.async_reload(with_rotation.entry_id)
    assert with_rotation.runtime_data.rotations.state(rid).file == "evening/a.jpg"


async def test_deleting_the_rotation_drops_its_state(
    hass: HomeAssistant, with_rotation: MockConfigEntry, tree: Tree, hass_storage: dict[str, Any]
) -> None:
    tree("evening/a.jpg")
    rid = rotation_id(with_rotation)
    await with_rotation.runtime_data.rotations.async_advance(rid, ["evening/*"])
    assert hass.config_entries.async_remove_subentry(with_rotation, rid)
    await hass.async_block_till_done()
    assert with_rotation.runtime_data.rotations.state(rid).file is None
    assert hass_storage["shoebox.rotations"]["data"] == {"rotations": {}}


async def test_rotations_command_lists_subentries(
    hass: HomeAssistant, with_rotation: MockConfigEntry, tree: Tree, hass_ws_client: Any
) -> None:
    tree("evening/a.jpg")
    client = await hass_ws_client()
    await client.send_json_auto_id({"type": "shoebox/rotations"})
    result = (await client.receive_json())["result"]["rotations"]
    assert result == [
        {
            "id": rotation_id(with_rotation),
            "title": "Evening",
            "patterns": ["evening/*"],
            "pattern": "evening/*",
            "count": 1,
        }
    ]
