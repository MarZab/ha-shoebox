from __future__ import annotations

import io

from homeassistant.components import media_source
from homeassistant.components.media_player import BrowseError
from homeassistant.core import HomeAssistant
from PIL import Image
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from ..conftest import Tree
from .conftest import rotation_id

ROOT = "media-source://shoebox"


async def test_browse_rotations_and_their_pictures(
    hass: HomeAssistant, with_rotation: MockConfigEntry, tree: Tree
) -> None:
    tree("evening/a.jpg", "evening/b.jpg", "evening/notes.txt", "other/c.jpg")
    rid = rotation_id(with_rotation)
    root = await media_source.async_browse_media(hass, ROOT)
    assert [(c.title, c.can_expand, c.thumbnail) for c in root.children] == [
        ("Evening", True, None)
    ]
    folder = await media_source.async_browse_media(hass, f"{ROOT}/{rid}")
    assert [(c.title, c.can_play, c.media_content_id) for c in folder.children] == [
        ("a.jpg", True, f"{ROOT}/{rid}/local/evening/a.jpg"),
        ("b.jpg", True, f"{ROOT}/{rid}/local/evening/b.jpg"),
    ]
    assert folder.children[0].thumbnail == f"/api/shoebox/media/{rid}/local/evening/a.jpg?thumb=1"


async def test_rotation_shows_its_current_picture(
    hass: HomeAssistant, with_rotation: MockConfigEntry, tree: Tree
) -> None:
    tree("evening/a.jpg")
    await hass.services.async_call(
        "button", "press", {"entity_id": "button.evening_next"}, blocking=True
    )
    root = await media_source.async_browse_media(hass, ROOT)
    assert root.children[0].thumbnail is not None


async def test_play_a_picture(
    hass: HomeAssistant,
    with_rotation: MockConfigEntry,
    tree: Tree,
    hass_client: ClientSessionGenerator,
    hass_read_only_access_token: str,
) -> None:
    tree("evening/a b.jpg")
    rid = rotation_id(with_rotation)
    play = await media_source.async_resolve_media(hass, f"{ROOT}/{rid}/local/evening/a b.jpg", None)
    assert play.mime_type == "image/jpeg"
    client = await hass_client(hass_read_only_access_token)
    response = await client.get(play.url)
    assert response.status == 200
    with Image.open(io.BytesIO(await response.read())) as im:
        assert im.size[0] == 1920 or im.size[1] == 1080
    thumb = await client.get(play.url + "?thumb=1")
    with Image.open(io.BytesIO(await thumb.read())) as im:
        assert im.size == (320, 320)


@pytest.mark.parametrize(
    "path", ["local/other/c.jpg", "local/evening/missing.jpg", "../etc/passwd"]
)
async def test_only_pictures_of_the_rotation_are_served(
    hass: HomeAssistant,
    with_rotation: MockConfigEntry,
    tree: Tree,
    hass_client: ClientSessionGenerator,
    path: str,
) -> None:
    tree("evening/a.jpg", "other/c.jpg")
    client = await hass_client()
    response = await client.get(f"/api/shoebox/media/{rotation_id(with_rotation)}/{path}")
    assert response.status in (400, 404)


async def test_unknown_rotation(
    hass: HomeAssistant, with_rotation: MockConfigEntry, hass_client: ClientSessionGenerator
) -> None:
    with pytest.raises(BrowseError):
        await media_source.async_browse_media(hass, f"{ROOT}/missing")
    client = await hass_client()
    assert (await client.get("/api/shoebox/media/missing/a.jpg")).status == 404


async def test_a_rotation_is_not_playable(
    hass: HomeAssistant, with_rotation: MockConfigEntry
) -> None:
    with pytest.raises(media_source.Unresolvable):
        await media_source.async_resolve_media(hass, f"{ROOT}/{rotation_id(with_rotation)}", None)


async def test_not_set_up(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    assert await hass.config_entries.async_setup(entry.entry_id)
    assert await hass.config_entries.async_unload(entry.entry_id)
    with pytest.raises(BrowseError):
        await media_source.async_browse_media(hass, ROOT)
