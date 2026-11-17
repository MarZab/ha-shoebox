from __future__ import annotations

from pathlib import Path
from typing import Any

from homeassistant.core import Context, HomeAssistant
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError, Unauthorized
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry, MockUser

from custom_components.shoebox import imaging
from custom_components.shoebox.const import DOMAIN

from ..conftest import Tree
from ..images import write_image


async def call(hass: HomeAssistant, service: str, **data: Any) -> Any:
    return await hass.services.async_call(
        DOMAIN, service, data, blocking=True, return_response=True
    )


async def refused(hass: HomeAssistant, service: str, **data: Any) -> str | None:
    with pytest.raises(ServiceValidationError) as err:
        await call(hass, service, **data)
    return err.value.translation_key


@pytest.mark.usefixtures("loaded")
async def test_list(hass: HomeAssistant, tree: Tree) -> None:
    tree("Family/a.jpg", "Family/b.txt", "Other/")
    result = await call(hass, "list", pattern="Family/*", type="image")
    assert result["count"] == 1
    assert {k: v for k, v in result["items"][0].items() if k != "modified"} == {
        "path": "Family/a.jpg",
        "type": "image",
        "size": (tree() / "Family/a.jpg").stat().st_size,
    }
    assert (await call(hass, "list"))["count"] == 4
    assert await refused(hass, "list", pattern="re:(") == "invalid_pattern"


@pytest.mark.usefixtures("loaded")
async def test_folder_actions(hass: HomeAssistant, tree: Tree) -> None:
    root = tree("a.jpg", "b.jpg")
    assert await call(hass, "create_folder", path="Family/2025") == {"path": "Family/2025"}
    assert await call(hass, "move", path="a.jpg", to="Family") == {"path": "Family/a.jpg"}
    assert await call(hass, "rename", path="Family/a.jpg", name="c.jpg") == {"path": "Family/c.jpg"}
    assert await call(hass, "delete", path="Family") == {"deleted": "Family"}
    assert sorted(p.name for p in root.iterdir()) == ["b.jpg"]


@pytest.mark.usefixtures("loaded")
@pytest.mark.parametrize(
    ("service", "data", "key"),
    [
        ("create_folder", {"path": "../x"}, "parent_not_allowed"),
        ("move", {"path": "a.jpg", "to": "missing"}, "not_a_folder"),
        ("rename", {"path": "a.jpg", "name": "b.jpg"}, "already_exists"),
        ("delete", {"path": "missing.jpg"}, "not_found"),
        ("rotate", {"path": "folder", "by": 90}, "not_a_file"),
        ("rotate", {"path": "a.png", "by": 90}, "jpeg_only"),
        ("crop", {"path": "a.jpg", "left": 0.1}, "crop_sides"),
        ("crop", {"path": "a.jpg", "left": 0.5, "top": 0, "right": 0.2, "bottom": 1}, "crop_range"),
    ],
)
async def test_refusals_carry_translation_keys(
    hass: HomeAssistant, tree: Tree, service: str, data: dict[str, Any], key: str
) -> None:
    tree("a.jpg", "b.jpg", "a.png", "folder/")
    assert await refused(hass, service, **data) == key


@pytest.mark.usefixtures("loaded")
async def test_rotate(hass: HomeAssistant, media_root: Path) -> None:
    path = write_image(media_root / "a.jpg")
    assert await call(hass, "rotate", path="a.jpg", by=90) == {"path": "a.jpg", "orientation": 6}
    assert await call(hass, "rotate", path="a.jpg", orientation=3) == {
        "path": "a.jpg",
        "orientation": 3,
    }
    assert imaging.get_orientation(path) == 3


@pytest.mark.usefixtures("loaded")
async def test_crop(hass: HomeAssistant, media_root: Path) -> None:
    path = write_image(media_root / "a.jpg")
    box = {"left": 0.1, "top": 0.2, "right": 0.6, "bottom": 0.9}
    result = await call(hass, "crop", path="a.jpg", **box)
    assert result["path"] == "a.jpg"
    assert result["crop"] == pytest.approx([0.1, 0.2, 0.6, 0.9])
    assert await call(hass, "crop", path="a.jpg", clear=True) == {"path": "a.jpg", "crop": None}
    assert imaging.get_crop(path) is None


@pytest.mark.usefixtures("loaded")
async def test_non_admin_is_refused(
    hass: HomeAssistant, hass_read_only_user: MockUser, tree: Tree
) -> None:
    tree("a.jpg")
    with pytest.raises(Unauthorized):
        await hass.services.async_call(
            DOMAIN,
            "delete",
            {"path": "a.jpg"},
            blocking=True,
            context=Context(user_id=hass_read_only_user.id),
        )


async def test_not_set_up(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    assert await hass.config_entries.async_setup(entry.entry_id)
    assert await hass.config_entries.async_unload(entry.entry_id)
    assert await refused(hass, "delete", path="a.jpg") == "not_loaded"


@pytest.mark.usefixtures("loaded")
async def test_file_system_errors(
    hass: HomeAssistant, tree: Tree, monkeypatch: pytest.MonkeyPatch
) -> None:
    tree("a.jpg")

    def denied(*_: object) -> None:
        raise PermissionError(13, "Permission denied", "/media/a.jpg")

    monkeypatch.setattr("custom_components.shoebox.media.delete", denied)
    with pytest.raises(HomeAssistantError) as err:
        await call(hass, "delete", path="a.jpg")
    assert err.value.translation_key == "file_error"
    assert err.value.translation_placeholders == {
        "error": "Permission denied",
        "path": "/media/a.jpg",
    }
