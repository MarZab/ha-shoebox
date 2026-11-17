from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from pathlib import Path
import threading
from typing import Any

from aiohttp import FormData
from aiohttp.test_utils import TestClient
from homeassistant.components.frontend import DATA_PANELS
from homeassistant.core import HomeAssistant
from PIL import Image
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator, WebSocketGenerator

from custom_components.shoebox import imaging
from custom_components.shoebox.const import (
    CONCURRENT_RENDERS,
    CONF_CACHE_SIZE,
    CONF_CLEAR_CACHE,
    CONF_SHOW_IN_SIDEBAR,
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
    assert await hass.config_entries.async_unload(loaded.entry_id)
    assert "shoebox" not in hass.data[DATA_PANELS]


async def test_panel_files_are_served(hass: HomeAssistant, client: TestClient) -> None:
    url = hass.data[DATA_PANELS]["shoebox"].config["_panel_custom"]["module_url"]
    response = await client.get(url)
    assert response.status == 200
    assert "customElements.define" in await response.text()


# ---------------------------------------------------------------- render view


async def test_render(client: TestClient, media_root: Path) -> None:
    write_image(media_root / "a.jpg", (80, 40), crop=(0.5, 0.5, 1.0, 1.0))
    response = await client.get(
        RENDER_URL, params={"path": "a.jpg", "size": "30x30", "fit": "cover"}
    )
    assert response.status == 200
    assert response.headers["Content-Type"] == "image/jpeg"
    assert response.headers["ETag"]
    data = await response.read()
    assert colour_at(data, 0.5, 0.5) == "white"
    whole = await client.get(RENDER_URL, params={"path": "a.jpg", "size": "30x30", "crop": "0"})
    assert colour_at(await whole.read(), 0.2, 0.2) == "red"


@pytest.mark.parametrize(
    ("params", "status"),
    [
        ({"path": "a.jpg", "size": "0x10"}, 400),
        ({"path": "a.jpg", "size": "5000x10"}, 400),
        ({"path": "a.jpg", "size": "10"}, 400),
        ({"path": "a.jpg", "size": "10x10", "fit": "stretch"}, 400),
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


async def test_render_is_admin_only(
    hass_client: ClientSessionGenerator,
    hass_read_only_access_token: str,
    loaded: MockConfigEntry,
    tree: Tree,
) -> None:
    tree("a.jpg")
    client = await hass_client(hass_read_only_access_token)
    assert (await client.get(RENDER_URL, params={"path": "a.jpg", "size": "10x10"})).status == 401


async def test_renders_are_capped(
    hass: HomeAssistant, loaded: MockConfigEntry, tree: Tree, monkeypatch: pytest.MonkeyPatch
) -> None:
    tree(*(f"{i}.jpg" for i in range(CONCURRENT_RENDERS + 3)))
    release = threading.Event()
    lock = threading.Lock()
    active = [0, 0]  # now, most at once

    def render(*_: object) -> bytes:
        with lock:
            active[0] += 1
            active[1] = max(active)
        release.wait(5)
        with lock:
            active[0] -= 1
        return b"jpeg"

    monkeypatch.setattr(imaging, "render", render)
    box = loaded.runtime_data
    tasks = [
        hass.async_create_task(box.picture(f"{i}.jpg", 10, 10, "cover"))
        for i in range(CONCURRENT_RENDERS + 3)
    ]
    for _ in range(200):
        if active[0] == CONCURRENT_RENDERS:
            break
        await asyncio.sleep(0.01)
    await asyncio.sleep(0.05)
    assert active[1] == CONCURRENT_RENDERS
    release.set()
    assert all(v.data == b"jpeg" for v in await asyncio.gather(*tasks))


# ---------------------------------------------------------------- upload view


def form(name: str = "a.jpg", content_type: str = "image/jpeg", data: bytes = b"jpeg") -> FormData:
    body = FormData()
    body.add_field("file", data, filename=name, content_type=content_type)
    return body


async def test_upload_never_overwrites(client: TestClient, tree: Tree) -> None:
    root = tree("x/a.jpg")
    response = await client.post(UPLOAD_URL, params={"folder": "x"}, data=form())
    assert (response.status, await response.json()) == (200, {"path": "x/a-1.jpg"})
    assert (root / "x/a-1.jpg").read_bytes() == b"jpeg"
    assert [p.name for p in (root / "x").iterdir() if p.name.startswith(".")] == []


@pytest.mark.parametrize(
    ("folder", "body", "status"),
    [
        ("", form(content_type="text/html"), 400),
        ("missing", form(), 400),
        ("../x", form(), 400),
        ("", form(name=""), 400),
    ],
)
async def test_upload_refuses(
    client: TestClient, media_root: Path, folder: str, body: FormData, status: int
) -> None:
    response = await client.post(UPLOAD_URL, params={"folder": folder}, data=body)
    assert response.status == status
    assert list(media_root.iterdir()) == []


async def test_upload_without_a_file_part(client: TestClient) -> None:
    body = FormData()
    body.add_field("other", "x")
    assert (await client.post(UPLOAD_URL, data=body)).status == 400


async def test_upload_too_large(
    client: TestClient, media_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("custom_components.shoebox.views.MAX_UPLOAD_BYTES", 10)
    response = await client.post(UPLOAD_URL, data=form(data=b"x" * 2_000_000))
    assert response.status == 413
    response = await client.post(UPLOAD_URL, data=form(data=b"x" * 100), chunked=True)
    assert response.status in (413, 400)
    assert list(media_root.iterdir()) == []


async def test_upload_is_admin_only(
    hass_client: ClientSessionGenerator, hass_read_only_access_token: str, loaded: MockConfigEntry
) -> None:
    client = await hass_client(hass_read_only_access_token)
    assert (await client.post(UPLOAD_URL, data=form())).status == 401


# ---------------------------------------------------------------- WebSocket commands


async def test_browse_and_signed_thumbnails(
    ws: Ws, tree: Tree, hass_client_no_auth: ClientSessionGenerator
) -> None:
    tree("x/b.jpg", "x/a.txt", "x/sub/")
    msg = await ws("browse", path="x")
    assert msg["success"]
    assert msg["result"]["path"] == "x"
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
    assert (await ws("folders"))["result"] == {"folders": ["a", "a/b", "c"]}


async def test_info_and_edit(ws: Ws, media_root: Path) -> None:
    write_image(media_root / "a.jpg", (80, 40))
    info = (await ws("info", path="a.jpg"))["result"]
    assert (info["width"], info["height"], info["editable"], info["path"]) == (
        80,
        40,
        True,
        "a.jpg",
    )
    assert info["view"].startswith(RENDER_URL)
    assert "crop=0" in info["base"]
    edited = (await ws("edit", path="a.jpg", rotate=90, crop=[0, 0, 0.5, 1]))["result"]
    assert (edited["width"], edited["height"], edited["orientation"]) == (40, 80, 6)
    assert edited["crop"] == pytest.approx([0, 0, 0.5, 1])


async def test_rotations_without_any(ws: Ws) -> None:
    assert (await ws("rotations"))["result"] == {"rotations": []}


@pytest.mark.parametrize(
    ("type_", "data"),
    [
        ("browse", {"path": "../x"}),
        ("info", {"path": "missing.jpg"}),
        ("edit", {"path": "a.png", "crop": None}),
    ],
)
async def test_refusals_come_back_as_errors(
    ws: Ws, tree: Tree, type_: str, data: dict[str, Any]
) -> None:
    tree("a.png")
    msg = await ws(type_, **data)
    assert not msg["success"]
    assert msg["error"]["code"] == "invalid"
    assert msg["error"]["message"]


async def test_commands_are_admin_only(
    hass_ws_client: WebSocketGenerator, hass_read_only_access_token: str, loaded: MockConfigEntry
) -> None:
    client = await hass_ws_client(access_token=hass_read_only_access_token)
    await client.send_json_auto_id({"type": "shoebox/folders"})
    msg = await client.receive_json()
    assert msg["error"]["code"] == "unauthorized"


def test_png_info_is_not_editable(tmp_path: Path) -> None:
    path = tmp_path / "a.png"
    Image.new("RGB", (4, 4)).save(path)
    assert imaging.info(path)["editable"] is False
