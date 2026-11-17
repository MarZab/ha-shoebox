from __future__ import annotations

from pathlib import Path

from homeassistant.core import HomeAssistant
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.shoebox.const import DOMAIN, TITLE


@pytest.fixture(autouse=True)
def folders(
    hass: HomeAssistant, enable_custom_integrations: None, tmp_path: Path, media_root: Path
) -> None:
    """Each test gets its own config folder (for the cache) and media folder."""
    config = tmp_path / "config"
    config.mkdir()
    hass.config.config_dir = str(config)
    hass.config.media_dirs = {"local": str(media_root)}


@pytest.fixture
def entry(hass: HomeAssistant) -> MockConfigEntry:
    entry = MockConfigEntry(domain=DOMAIN, title=TITLE, data={})
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
async def loaded(hass: HomeAssistant, entry: MockConfigEntry) -> MockConfigEntry:
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry
