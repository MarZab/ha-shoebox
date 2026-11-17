from __future__ import annotations

from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from aiohttp import FormData
from aiohttp.test_utils import TestClient
from homeassistant.components.frontend import DATA_PANELS, EVENT_PANELS_UPDATED
from homeassistant.config_entries import ConfigEntryDisabler
from homeassistant.core import HomeAssistant
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_capture_events
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator, WebSocketGenerator

from custom_components.shoebox import websocket
from custom_components.shoebox.const import (
    CONF_CACHE_SIZE,
    CONF_CLEAR_CACHE,
    CONF_SHOW_IN_SIDEBAR,
    DOWNLOAD_URL,
    RENDER_URL,
    UPLOAD_URL,
)

from ..conftest import Tree
from ..images import colour_at, write_image

type Ws = Callable[..., Awaitable[Any]]


@pytest.fixture
async def ws(hass_ws_client: WebSocketGenerator, loaded: MockConfigEntry) -> Ws:
    client = await hass_ws_client()

    async def send(type_: str, **data: Any) -> Any:
        await client.send_json_auto_id({"type": f"shoebox/{type_}", **data})
        return await client.receive_json()

    return send


@pytest.fixture
async def client(hass_client: ClientSessionGenerator, loaded: MockConfigEntry) -> TestClient:
    return await hass_client()


# ---------------------------------------------------------------- the panel


async def test_panel_follows_show_in_sidebar(hass: HomeAssistant, loaded: MockConfigEntry) -> None:
    panel = hass.data[DATA_PANELS]["shoebox"]
    assert (panel.sidebar_title, panel.require_admin) == ("Shoebox", True)
    for show in (False, True):
        flow = await hass.config_entries.options.async_init(loaded.entry_id)
        await hass.config_entries.options.async_configure(
            flow["flow_id"],
            {CONF_CACHE_SIZE: 512, CONF_CLEAR_CACHE: False, CONF_SHOW_IN_SIDEBAR: show},
        )
        await hass.async_block_till_done()
        assert ("shoebox" in hass.data[DATA_PANELS]) is show
    # a reload (options, rotations) keeps it: an open panel fails while it is gone
    updates = async_capture_events(hass, EVENT_PANELS_UPDATED)
    assert await hass.config_entries.async_reload(loaded.entry_id)
    assert "shoebox" in hass.data[DATA_PANELS]
    assert updates == []
    # disabling takes it away, enabling brings it back, removing takes it away
    for disabled_by, shown in ((ConfigEntryDisabler.USER, False), (None, True)):
        await hass.config_entries.async_set_disabled_by(loaded.entry_id, disabled_by)
        await hass.async_block_till_done()
        assert ("shoebox" in hass.data[DATA_PANELS]) is shown
    assert await hass.config_entries.async_remove(loaded.entry_id)
    assert "shoebox" not in hass.data[DATA_PANELS]


async def test_panel_files_are_served(hass: HomeAssistant, client: TestClient) -> None:
    url = hass.data[DATA_PANELS]["shoebox"].config["_panel_custom"]["module_url"]
    response = await client.get(url)
    assert response.status == 200
    assert "customElements.define" in await response.text()


# ---------------------------------------------------------------- render view


async def test_render(client: TestClient, media_root: Path, loaded: MockConfigEntry) -> None:
    write_image(media_root / "a.jpg", (80, 40), crop=(0.5, 0.5, 1.0, 1.0))
    response = await client.get(
        RENDER_URL, params={"path": "local/a.jpg", "size": "30x30", "fit": "cover"}
    )
    assert response.status == 200
    assert response.headers["Content-Type"] == "image/jpeg"
    assert response.headers["ETag"]
    data = await response.read()
    assert colour_at(data, 0.5, 0.5) == "white"
    whole = await client.get(
        RENDER_URL, params={"path": "local/a.jpg", "size": "30x30", "crop": "0"}
    )
    assert colour_at(await whole.read(), 0.2, 0.2) == "red"
    # the display preview: the device URL's options, prepared without filling the cache
    stored = loaded.runtime_data.cache.usage()
    epaper = await client.get(
        RENDER_URL, params={"path": "local/a.jpg", "size": "30x30", "colors": "bw", "cache": "0"}
    )
    assert (epaper.status, epaper.headers["Content-Type"]) == (200, "image/png")
    assert loaded.runtime_data.cache.usage() == stored


@pytest.mark.parametrize(
    ("params", "status"),
    [
        ({"path": "a.jpg", "size": "0x10"}, 400),
        ({"path": "a.jpg", "size": "5000x10"}, 400),
        ({"path": "a.jpg", "size": "10"}, 400),
        ({"path": "a.jpg", "size": "10x10", "fit": "stretch"}, 400),
        ({"path": "local/a.jpg", "size": "10x10", "colors": "rainbow"}, 400),
        ({"path": "../etc/passwd", "size": "10x10"}, 400),  # Home Assistant's security filter
        ({"path": "/etc/passwd", "size": "10x10"}, 404),
        ({"path": "missing.jpg", "size": "10x10"}, 404),
    ],
)
async def test_render_refuses(
    client: TestClient, tree: Tree, params: dict[str, str], status: int
) -> None:
    tree("a.jpg")
    assert (await client.get(RENDER_URL, params=params)).status == status


# ---------------------------------------------------------------- upload view


def form(name: str = "a.jpg", content_type: str = "image/jpeg", data: bytes = b"jpeg") -> FormData:
    body = FormData()
    body.add_field("file", data, filename=name, content_type=content_type)
    return body


async def test_upload_never_overwrites(client: TestClient, tree: Tree) -> None:
    root = tree("x/a.jpg")
    response = await client.post(UPLOAD_URL, params={"folder": "local/x"}, data=form())
    assert (response.status, await response.json()) == (200, {"path": "local/x/a-1.jpg"})
    assert (root / "x/a-1.jpg").read_bytes() == b"jpeg"
    assert [p.name for p in (root / "x").iterdir() if p.name.startswith(".")] == []


def without_file() -> FormData:
    body = FormData()
    body.add_field("other", b"x", filename="x.jpg", content_type="image/jpeg")  # multipart
    return body


@pytest.mark.parametrize(
    ("folder", "body", "message"),
    [
        ("local", form(content_type="text/html"), "only pictures, videos and audio"),
        ("local", form(name=".."), "not a valid file name"),
        ("local", without_file(), "file"),
        ("local", FormData({"file": "x"}), "multipart"),
        ("", form(), "Choose a media folder first"),
        ("missing", form(), "not a media folder"),
    ],
)
async def test_upload_refuses(
    client: TestClient, media_root: Path, folder: str, body: FormData, message: str
) -> None:
    response = await client.post(UPLOAD_URL, params={"folder": folder}, data=body)
    assert response.status == 400
    assert message in (await response.json())["message"]
    assert list(media_root.iterdir()) == []


# ---------------------------------------------------------------- WebSocket commands


async def test_browse_and_signed_thumbnails(
    ws: Ws, tree: Tree, hass_client_no_auth: ClientSessionGenerator
) -> None:
    tree("x/b.jpg", "x/a.txt", "x/sub/")
    top = (await ws("browse"))["result"]
    # shown by the directory's name, as Home Assistant's media browser does; the path keeps the ID
    assert [(i["name"], i["path"]) for i in top["items"]] == [("media", "local")]
    assert top["titles"] == {"local": "media"}
    msg = await ws("browse", path="local/x")
    assert msg["success"]
    assert msg["result"]["path"] == "local/x"
    items = msg["result"]["items"]
    assert [(i["name"], i["type"]) for i in items] == [
        ("sub", "folder"),
        ("a.txt", "file"),
        ("b.jpg", "image"),
    ]
    assert "thumb" not in items[1]
    anonymous = await hass_client_no_auth()
    assert (await anonymous.get(items[2]["thumb"])).status == 200
    assert (await anonymous.get(items[2]["thumb"].split("&authSig")[0])).status == 401


async def test_folders(ws: Ws, tree: Tree) -> None:
    tree("a/b/", "c/")
    assert (await ws("folders"))["result"] == {
        "folders": ["local", "local/a", "local/a/b", "local/c"]
    }


async def test_info_and_edit(ws: Ws, media_root: Path) -> None:
    write_image(media_root / "a.jpg", (80, 40))
    info = (await ws("info", path="local/a.jpg"))["result"]
    assert (info["width"], info["height"], info["editable"], info["path"]) == (
        80,
        40,
        True,
        "local/a.jpg",
    )
    assert info["view"].startswith(RENDER_URL)
    assert "crop=0" in info["base"]
    edited = (await ws("edit", path="local/a.jpg", rotate=90, crop=[0, 0, 0.5, 1]))["result"]
    assert (edited["width"], edited["height"], edited["orientation"]) == (40, 80, 6)
    assert edited["crop"] == pytest.approx([0, 0, 0.5, 1])


@pytest.mark.parametrize(
    ("path", "query", "found", "more"),
    [
        (
            "local/x",
            "BEACH",
            ["local/x/beach.jpg", "local/x/sub/Beach 2/"],
            False,
        ),
        ("", "beach.jpg", ["local/x/beach.jpg"], False),  # every media folder
        ("local/x/sub", "beach", ["local/x/sub/Beach 2/"], False),
        ("local", "a", None, True),  # more than the limit
    ],
)
async def test_search_below_a_folder(
    ws: Ws,
    tree: Tree,
    monkeypatch: pytest.MonkeyPatch,
    path: str,
    query: str,
    found: list[str] | None,
    more: bool,
) -> None:
    monkeypatch.setattr(websocket, "SEARCH_LIMIT", 3)
    tree(
        "x/beach.jpg",
        "x/.beach-hidden.jpg",
        "x/sub/Beach 2/c.jpg",
        "x/a1.txt",
        "x/a2.txt",
        "x/a3.txt",
    )
    msg = await ws("search", path=path, query=query)
    assert msg["success"], msg
    result = msg["result"]
    paths = [i["path"] + ("/" if i["type"] == "folder" else "") for i in result["items"]]
    if found is not None:
        assert paths == found
    else:
        assert len(paths) == 3
    assert result["more"] is more
    assert all("thumb" in i for i in result["items"] if i["type"] == "image")


@pytest.mark.parametrize(
    ("type_", "data"),
    [
        ("browse", {"path": "../x"}),
        ("info", {"path": "missing.jpg"}),
        ("edit", {"path": "local/a.png", "crop": None}),
    ],
)
async def test_refusals_come_back_as_errors(
    ws: Ws, tree: Tree, type_: str, data: dict[str, Any]
) -> None:
    tree("a.png")
    msg = await ws(type_, **data)
    assert not msg["success"]
    assert msg["error"]["code"] == "home_assistant_error"
    assert msg["error"]["message"]
    assert msg["error"]["translation_domain"] == "shoebox"  # the panel could translate it


async def test_everything_is_admin_only(
    hass_client: ClientSessionGenerator,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
    loaded: MockConfigEntry,
    tree: Tree,
) -> None:
    tree("a.jpg")
    client = await hass_client(hass_read_only_access_token)
    assert (
        await client.get(RENDER_URL, params={"path": "local/a.jpg", "size": "10x10"})
    ).status == 401
    assert (await client.post(UPLOAD_URL, params={"folder": "local"}, data=form())).status == 401
    assert (await client.get(DOWNLOAD_URL, params={"path": "local/a.jpg"})).status == 401
    ws = await hass_ws_client(access_token=hass_read_only_access_token)
    await ws.send_json_auto_id({"type": "shoebox/folders"})
    assert (await ws.receive_json())["error"]["code"] == "unauthorized"


async def test_download_gives_the_original_file(client: TestClient, media_root: Path) -> None:
    (media_root / "Notes").mkdir()
    (media_root / "Notes/a b.txt").write_bytes(b"original")
    response = await client.get(DOWNLOAD_URL, params={"path": "local/Notes/a b.txt"})
    assert response.status == 200
    assert await response.read() == b"original"
    assert response.headers["Content-Disposition"] == "attachment; filename*=UTF-8''a%20b.txt"
    start = await client.get(  # how the panel reads the start of a text file
        DOWNLOAD_URL, params={"path": "local/Notes/a b.txt"}, headers={"Range": "bytes=0-3"}
    )
    assert (start.status, await start.read()) == (206, b"orig")
    assert start.headers["Content-Range"] == "bytes 0-3/8"
    assert (await client.get(DOWNLOAD_URL, params={"path": "local/missing.txt"})).status == 404
