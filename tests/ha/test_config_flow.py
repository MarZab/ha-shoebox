from __future__ import annotations

import os
from pathlib import Path

from homeassistant.config_entries import SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.shoebox.const import (
    CONF_CACHE_SIZE,
    CONF_CLEAR_CACHE,
    CONF_FOLDERS,
    CONF_SHOW_IN_SIDEBAR,
    DOMAIN,
)

MB = 1024 * 1024


def put_variants(hass: HomeAssistant, *sizes: int) -> Path:
    folder = Path(hass.config.path(".cache/shoebox"))
    folder.mkdir(parents=True, exist_ok=True)
    for i, size in enumerate(sizes):
        path = folder / f"{i:064x}.jpg"
        path.write_bytes(b"\0" * size)
        os.utime(path, (i, i))
    return folder


async def test_user_flow_creates_the_entry(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    assert result["type"] is FlowResultType.FORM
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Shoebox"
    assert result["options"] == {"folders": ["local"]}


async def test_user_flow_needs_a_folder(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})
    result = await hass.config_entries.flow.async_configure(result["flow_id"], {"folders": []})
    assert result["errors"] == {"folders": "no_folder"}


async def options(
    hass: HomeAssistant, entry: MockConfigEntry, **values: object
) -> dict[str, object]:
    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    data = {
        CONF_FOLDERS: ["local"],
        CONF_CACHE_SIZE: 512,
        CONF_CLEAR_CACHE: False,
        CONF_SHOW_IN_SIDEBAR: True,
    } | values
    result = await hass.config_entries.options.async_configure(result["flow_id"], data)
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    return dict(entry.options)


async def test_options_defaults_and_usage(hass: HomeAssistant, loaded: MockConfigEntry) -> None:
    put_variants(hass, MB)
    result = await hass.config_entries.options.async_init(loaded.entry_id)
    assert result["description_placeholders"] == {"files": "1", "size": "1.0"}
    defaults = {str(key): key.default() for key in result["data_schema"].schema}
    assert defaults == {
        CONF_FOLDERS: ["local"],
        CONF_CACHE_SIZE: 512,
        CONF_CLEAR_CACHE: False,
        CONF_SHOW_IN_SIDEBAR: True,
    }
    assert loaded.runtime_data.show_in_sidebar is True


async def test_options_store_size_and_sidebar(hass: HomeAssistant, loaded: MockConfigEntry) -> None:
    stored = await options(hass, loaded, **{CONF_CACHE_SIZE: 64, CONF_SHOW_IN_SIDEBAR: False})
    assert stored == {CONF_FOLDERS: ["local"], CONF_CACHE_SIZE: 64, CONF_SHOW_IN_SIDEBAR: False}
    assert loaded.runtime_data.show_in_sidebar is False
    assert loaded.runtime_data.cache.limit_bytes == 64 * MB


async def test_options_change_the_folders(
    hass: HomeAssistant, loaded: MockConfigEntry, tmp_path: Path
) -> None:
    (tmp_path / "nas").mkdir()
    hass.config.media_dirs = hass.config.media_dirs | {"nas": str(tmp_path / "nas")}
    await options(hass, loaded, **{CONF_FOLDERS: ["local", "nas"]})
    assert set(loaded.runtime_data.library.folders) == {"local", "nas"}
    flow = await hass.config_entries.options.async_init(loaded.entry_id)
    flow = await hass.config_entries.options.async_configure(
        flow["flow_id"],
        {
            CONF_FOLDERS: [],
            CONF_CACHE_SIZE: 512,
            CONF_CLEAR_CACHE: False,
            CONF_SHOW_IN_SIDEBAR: True,
        },
    )
    assert flow["errors"] == {CONF_FOLDERS: "no_folder"}


@pytest.mark.parametrize(
    ("values", "kept", "enabled"),
    [
        ({CONF_CLEAR_CACHE: True}, [], True),
        ({CONF_CACHE_SIZE: 16}, [f"{1:064x}.jpg"], True),  # least recently used goes first
        ({CONF_CACHE_SIZE: 0}, [], False),  # 0 turns the cache off
    ],
)
async def test_cache_options(
    hass: HomeAssistant,
    loaded: MockConfigEntry,
    values: dict[str, object],
    kept: list[str],
    enabled: bool,
) -> None:
    folder = put_variants(hass, 10 * MB, 10 * MB)
    await options(hass, loaded, **values)
    assert [p.name for p in folder.iterdir()] == kept
    assert loaded.runtime_data.cache.enabled is enabled
