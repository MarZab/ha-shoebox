from __future__ import annotations

from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.shoebox.const import DOMAIN, TITLE

from ..images import write_image
from .conftest import rotation, rotation_id


@pytest.fixture
async def two_folders(hass: HomeAssistant, media_root: Path, tmp_path: Path) -> MockConfigEntry:
    nas = tmp_path / "nas"
    hass.config.media_dirs = {"local": str(media_root), "nas": str(nas)}
    write_image(media_root / "Family/a.jpg")
    write_image(nas / "Family/b.jpg")
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=TITLE,
        data={},
        options={"folders": ["local", "nas"]},
        subentries_data=[rotation("Family", "*/Family/*")],
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def call(hass: HomeAssistant, service: str, **data: Any) -> Any:
    return await hass.services.async_call(
        DOMAIN, service, data, blocking=True, return_response=True
    )


async def test_a_rotation_spans_folders(hass: HomeAssistant, two_folders: MockConfigEntry) -> None:
    rotations = two_folders.runtime_data.rotations
    rid = rotation_id(two_folders)
    files = [(await rotations.async_advance(rid, ["*/Family/*"])).file for _ in range(2)]
    assert files == ["local/Family/a.jpg", "nas/Family/b.jpg"]


async def test_move_between_folders(
    hass: HomeAssistant, two_folders: MockConfigEntry, tmp_path: Path
) -> None:
    assert await call(hass, "move", path="local/Family/a.jpg", to="nas") == {"path": "nas/a.jpg"}
    assert (tmp_path / "nas/a.jpg").exists()
    listed = await call(hass, "list", pattern="nas/**", type="image")
    assert [i["path"] for i in listed["items"]] == ["nas/Family/b.jpg", "nas/a.jpg"]


async def test_panel_lists_both_folders(
    two_folders: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await hass_ws_client()
    await client.send_json_auto_id({"type": "shoebox/browse"})
    items = (await client.receive_json())["result"]["items"]
    assert [i["name"] for i in items] == ["local", "nas"]
