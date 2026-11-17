from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import Any

from homeassistant.config_entries import SOURCE_RECONFIGURE, SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.util import dt as dt_util
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_fire_time_changed

from custom_components.shoebox import config_flow
from custom_components.shoebox.const import DOMAIN, SUBENTRY_ROTATION

from ..conftest import Tree
from ..images import write_image
from .conftest import rotation, rotation_id


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
        flow["flow_id"],
        {"name": " Living room ", "patterns": ["local/morning/*", " local/evening/* ", ""]},
    )
    assert flow["step_id"] == "preview"
    assert flow["description_placeholders"] == {
        "count": "2",
        "examples": "- local/evening/a.jpg\n- local/evening/b.jpg",
    }
    flow = await hass.config_entries.subentries.async_configure(flow["flow_id"], {})
    await hass.async_block_till_done()
    assert flow["type"] is FlowResultType.CREATE_ENTRY
    sub = next(iter(loaded.subentries.values()))
    assert (sub.title, dict(sub.data)) == (
        "Living room",
        {"patterns": ["local/morning/*", "local/evening/*"], "order": "path"},
    )


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


async def test_add_rotation_refuses_slow_patterns(
    hass: HomeAssistant, loaded: MockConfigEntry, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Really slow patterns take seconds; with no time allowed, any pattern is too slow
    monkeypatch.setattr(config_flow, "SLOW_MATCH_S", -1.0)
    flow = await subentry_flow(hass, loaded)
    flow = await hass.config_entries.subentries.async_configure(
        flow["flow_id"], {"name": "x", "patterns": ["local/**"]}
    )
    assert flow["errors"] == {"patterns": "slow_patterns"}


async def test_a_rotation_without_matches_can_still_be_saved(
    hass: HomeAssistant, loaded: MockConfigEntry
) -> None:
    flow = await subentry_flow(hass, loaded)
    flow = await hass.config_entries.subentries.async_configure(
        flow["flow_id"], {"name": "Later", "patterns": ["local/nothing/*"]}
    )
    assert flow["description_placeholders"] == {"count": "0", "examples": "-"}
    flow = await hass.config_entries.subentries.async_configure(flow["flow_id"], {})
    assert flow["type"] is FlowResultType.CREATE_ENTRY


async def test_reconfigure_keeps_the_state(
    hass: HomeAssistant, with_rotation: MockConfigEntry, tree: Tree
) -> None:
    tree("evening/a.jpg", "night/b.jpg")
    rid = rotation_id(with_rotation)
    await with_rotation.runtime_data.rotations.async_advance(rid, ["local/evening/*"])
    flow = await subentry_flow(hass, with_rotation, source=SOURCE_RECONFIGURE, subentry_id=rid)
    assert flow["data_schema"]({})["patterns"] == ["local/evening/*"]
    flow = await hass.config_entries.subentries.async_configure(
        flow["flow_id"], {"name": "Night", "patterns": ["local/night/*"]}
    )
    flow = await hass.config_entries.subentries.async_configure(flow["flow_id"], {})
    await hass.async_block_till_done()
    assert flow["reason"] == "reconfigure_successful"
    assert with_rotation.subentries[rid].title == "Night"
    assert with_rotation.runtime_data.rotations.state(rid).file == "local/evening/a.jpg"


async def test_rotation_steps_wraps_and_survives_removed_files(
    hass: HomeAssistant, with_rotation: MockConfigEntry, tree: Tree
) -> None:
    root = tree("evening/a.jpg", "evening/b.jpg", "evening/c.jpg", "evening/notes.txt")
    rotations = with_rotation.runtime_data.rotations
    rid = rotation_id(with_rotation)
    steps = [(await rotations.async_advance(rid, ["local/evening/*"])).file for _ in range(4)]
    assert steps == [
        "local/evening/a.jpg",
        "local/evening/b.jpg",
        "local/evening/c.jpg",
        "local/evening/a.jpg",
    ]
    (root / "evening/b.jpg").unlink()
    (root / "evening/a.jpg").unlink()
    state = await rotations.async_advance(rid, ["local/evening/*"])
    assert (state.file, state.position, state.count) == ("local/evening/c.jpg", 1, 1)


async def test_rotation_combines_patterns_and_empties(
    hass: HomeAssistant, with_rotation: MockConfigEntry, tree: Tree
) -> None:
    tree("evening/a.jpg", "night/b.jpg", "night/private/c.jpg")
    rotations = with_rotation.runtime_data.rotations
    rid = rotation_id(with_rotation)
    patterns = ["local/evening/*", "local/night/**", "!**/private/**"]
    files = [(await rotations.async_advance(rid, patterns)).file for _ in range(3)]
    assert files == ["local/evening/a.jpg", "local/night/b.jpg", "local/evening/a.jpg"]
    state = await rotations.async_advance(rid, ["local/morning/*"])
    assert (state.file, state.position, state.count) == (None, 0, 0)


async def test_state_survives_a_reload(
    hass: HomeAssistant, with_rotation: MockConfigEntry, tree: Tree
) -> None:
    tree("evening/a.jpg", "evening/b.jpg")
    rid = rotation_id(with_rotation)
    await with_rotation.runtime_data.rotations.async_advance(rid, ["local/evening/*"])
    assert await hass.config_entries.async_reload(with_rotation.entry_id)
    assert with_rotation.runtime_data.rotations.state(rid).file == "local/evening/a.jpg"


async def test_deleting_the_rotation_drops_its_state(
    hass: HomeAssistant, with_rotation: MockConfigEntry, tree: Tree, hass_storage: dict[str, Any]
) -> None:
    tree("evening/a.jpg")
    rid = rotation_id(with_rotation)
    await with_rotation.runtime_data.rotations.async_advance(rid, ["local/evening/*"])
    assert hass.config_entries.async_remove_subentry(with_rotation, rid)
    await hass.async_block_till_done()
    assert with_rotation.runtime_data.rotations.state(rid).file is None
    assert hass_storage["shoebox.rotations"]["data"] == {"rotations": {}}


async def test_a_rotation_spans_media_folders(
    hass: HomeAssistant, media_root: Path, tmp_path: Path
) -> None:
    hass.config.media_dirs = {"local": str(media_root), "nas": str(tmp_path / "nas")}
    write_image(media_root / "Family/a.jpg")
    write_image(tmp_path / "nas/Family/b.jpg")
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={},
        options={"folders": ["local", "nas"]},
        subentries_data=[rotation("Family", "*/Family/*")],
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    rotations = entry.runtime_data.rotations
    files = [
        (await rotations.async_advance(rotation_id(entry), ["*/Family/*"])).file for _ in range(2)
    ]
    assert files == ["local/Family/a.jpg", "nas/Family/b.jpg"]


async def test_shuffle_shows_every_picture_once_per_round(
    hass: HomeAssistant, with_rotation: MockConfigEntry, tree: Tree
) -> None:
    files = [f"local/evening/{n}.jpg" for n in "abcd"]
    tree(*(f.removeprefix("local/") for f in files))
    rotations = with_rotation.runtime_data.rotations
    rid = rotation_id(with_rotation)
    last = None
    for _ in range(20):
        round_ = [await rotations.async_advance(rid, ["local/evening/*"], "shuffle") for _ in files]
        assert sorted(s.file for s in round_) == files  # type: ignore[type-var]
        assert [s.position for s in round_] == [1, 2, 3, 4]
        assert round_[0].file != last
        last = round_[-1].file


async def test_shuffle_takes_in_new_pictures_and_path_order_continues(
    hass: HomeAssistant, with_rotation: MockConfigEntry, tree: Tree
) -> None:
    root = tree("evening/a.jpg", "evening/b.jpg", "evening/c.jpg")
    rotations = with_rotation.runtime_data.rotations
    rid = rotation_id(with_rotation)
    seen = [
        (await rotations.async_advance(rid, ["local/evening/*"], "shuffle")).file for _ in range(2)
    ]
    tree("evening/new.jpg")
    seen += [
        (await rotations.async_advance(rid, ["local/evening/*"], "shuffle")).file for _ in range(2)
    ]
    assert sorted(seen) == [f"local/evening/{n}.jpg" for n in ("a", "b", "c", "new")]  # type: ignore[type-var]
    files = sorted(f"local/{p.relative_to(root).as_posix()}" for p in (root / "evening").iterdir())
    after = files[(files.index(seen[-1]) + 1) % len(files)]  # type: ignore[arg-type]
    assert (await rotations.async_advance(rid, ["local/evening/*"])).file == after


async def test_removing_shoebox_leaves_no_state_behind(
    hass: HomeAssistant, with_rotation: MockConfigEntry, tree: Tree, hass_storage: dict[str, Any]
) -> None:
    tree("evening/a.jpg")
    await with_rotation.runtime_data.rotations.async_advance(
        rotation_id(with_rotation), ["local/evening/*"]
    )  # its save is still waiting
    assert await hass.config_entries.async_remove(with_rotation.entry_id)
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(minutes=1))
    await hass.async_block_till_done()
    assert "shoebox.rotations" not in hass_storage


async def test_state_stored_by_an_older_version_still_loads(
    hass: HomeAssistant, tree: Tree, hass_storage: dict[str, Any]
) -> None:
    tree("evening/a.jpg", "evening/b.jpg")
    entry = MockConfigEntry(domain=DOMAIN, data={}, subentries_data=[rotation()])
    rid = next(iter(entry.subentries))
    hass_storage["shoebox.rotations"] = {
        "version": 1,
        "minor_version": 1,
        "key": "shoebox.rotations",
        "data": {
            "rotations": {rid: {"file": "local/evening/a.jpg", "position": 1, "pattern": "x"}}
        },
    }
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    state = await entry.runtime_data.rotations.async_advance(rid, ["local/evening/*"])
    assert state.file == "local/evening/b.jpg"  # went on from where it was
