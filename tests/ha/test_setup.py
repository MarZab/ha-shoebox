from __future__ import annotations

from pathlib import Path
from typing import Any

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.shoebox.const import DOMAIN


async def test_setup_unload_and_reload(hass: HomeAssistant, loaded: MockConfigEntry) -> None:
    assert loaded.state is ConfigEntryState.LOADED
    assert loaded.runtime_data.library.folders["local"].name == "media"
    assert await hass.config_entries.async_reload(loaded.entry_id)
    assert loaded.state is ConfigEntryState.LOADED
    assert await hass.config_entries.async_unload(loaded.entry_id)
    assert loaded.state is ConfigEntryState.NOT_LOADED


async def test_removing_keeps_media_and_drops_state_and_cache(
    hass: HomeAssistant, loaded: MockConfigEntry, media_root: Path, hass_storage: dict[str, Any]
) -> None:
    (media_root / "a.jpg").write_bytes(b"jpeg")
    cache = Path(hass.config.path(".cache/shoebox"))
    cache.mkdir(parents=True)
    (cache / f"{0:064x}.jpg").write_bytes(b"v")
    await loaded.runtime_data.rotations.async_save()
    assert "shoebox.rotations" in hass_storage
    assert await hass.config_entries.async_remove(loaded.entry_id)
    await hass.async_block_till_done()
    assert "shoebox.rotations" not in hass_storage
    assert list(cache.iterdir()) == []
    assert (media_root / "a.jpg").exists()


@pytest.mark.parametrize(
    ("media_dirs", "chosen", "missing"),
    [({"local": "missing"}, ["local"], "local"), ({"local": ""}, ["local", "nas"], "nas")],
)
async def test_setup_waits_for_its_media_folders(
    hass: HomeAssistant,
    media_root: Path,
    media_dirs: dict[str, str],
    chosen: list[str],
    missing: str,
) -> None:
    hass.config.media_dirs = {name: str(media_root / sub) for name, sub in media_dirs.items()}
    entry = MockConfigEntry(domain=DOMAIN, data={}, options={"folders": chosen})
    entry.add_to_hass(hass)
    assert not await hass.config_entries.async_setup(entry.entry_id)
    assert entry.state is ConfigEntryState.SETUP_RETRY
    assert f'"{missing}"' in (entry.reason or "")
