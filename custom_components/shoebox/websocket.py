"""WebSocket commands of the panel. All are admin-only.

Pictures for the panel's images come back as URLs to the render view, signed for the user's
connection, because an <img> cannot send the Authorization header.
"""

from __future__ import annotations

from collections import OrderedDict
from collections.abc import Awaitable, Callable
from datetime import timedelta
from functools import partial
import time
from typing import Any, Final

from homeassistant.components import websocket_api
from homeassistant.components.http.auth import async_sign_path
from homeassistant.core import HomeAssistant, callback
from homeassistant.util.hass_dict import HassKey
import probatio as vol
from yarl import URL

from . import imaging, media
from .const import PANEL_URL_LIFETIME_S, RENDER_URL
from .runtime import Shoebox, loaded_shoebox
from .services import FRACTION

THUMB: Final = (320, 320, "cover")
VIEW: Final = (2048, 2048, "contain")
BASE: Final = (1600, 1600, "contain")  # the editor draws a new crop on the whole picture
SEARCH_LIMIT: Final = 100  # as in Home Assistant's media search


type _Message = dict[str, Any]
type _Handler = Callable[[HomeAssistant, websocket_api.ActiveConnection, _Message], Awaitable[None]]


# Signed thumbnail URLs per user, reused for half their lifetime: a new signature is a new URL,
# and the browser would download every thumbnail again on each listing. The panel lists again
# before they expire.
_SIGNED: Final[HassKey[OrderedDict[tuple[str, str], tuple[str, float]]]] = HassKey("shoebox_signed")
_SIGNED_MAX: Final = 20_000


def picture_url(
    hass: HomeAssistant,
    path: str,
    size: tuple[int, int, str],
    *,
    crop: bool = True,
    version: float | None = None,
) -> str:
    """A signed render URL. With `version` (the file's mtime, so an edit changes the URL) it is
    the same URL for the same user until half its lifetime is over."""
    width, height, fit = size
    query = {"path": path, "size": f"{width}x{height}", "fit": fit}
    if not crop:
        query["crop"] = "0"
    if version is not None:
        query["v"] = f"{version:.3f}"
    url = str(URL(RENDER_URL).with_query(query))
    lifetime = timedelta(seconds=PANEL_URL_LIFETIME_S)
    connection = websocket_api.current_connection.get()
    user = connection.refresh_token_id if connection else None
    if version is None or not user:
        return async_sign_path(hass, url, lifetime)
    signed = hass.data.setdefault(_SIGNED, OrderedDict())
    now = time.monotonic()
    hit = signed.get((user, url))
    if hit and now - hit[1] < PANEL_URL_LIFETIME_S / 2:
        signed.move_to_end((user, url))
        return hit[0]
    signed[(user, url)] = (async_sign_path(hass, url, lifetime), now)
    signed.move_to_end((user, url))
    while len(signed) > _SIGNED_MAX:
        signed.popitem(last=False)
    return signed[(user, url)][0]


def _command(schema: dict[Any, Any]) -> Callable[[_Handler], websocket_api.WebSocketCommandHandler]:
    """An admin-only command. Errors go through core's handling, which sends the translated
    message with its translation key and placeholders."""

    def wrap(func: _Handler) -> websocket_api.WebSocketCommandHandler:
        return websocket_api.websocket_command(schema)(
            websocket_api.require_admin(websocket_api.async_response(func))
        )

    return wrap


def _item(hass: HomeAssistant, entry: media.Entry) -> dict[str, Any]:
    item: dict[str, Any] = dict(entry.as_dict()) | {"name": entry.name}
    if entry.type == "image":
        item["thumb"] = picture_url(hass, entry.path, THUMB, version=entry.modified)
    return item


@_command(
    {
        vol.Required("type"): "shoebox/search",
        vol.Optional("path", default=""): str,
        vol.Required("query"): vol.All(str, vol.Length(min=1, max=200)),
    }
)
async def ws_search(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: _Message
) -> None:
    """Names containing the query in a folder and every folder below it, as Home Assistant's
    media search: at most SEARCH_LIMIT, and whether there were more."""
    box = loaded_shoebox(hass)
    found, more = await box.run(box.library.search, msg["path"], msg["query"], SEARCH_LIMIT)
    items = [_item(hass, e) for e in found]
    connection.send_result(msg["id"], {"items": items, "more": more, "titles": box.library.titles})


@_command({vol.Required("type"): "shoebox/browse", vol.Optional("path", default=""): str})
async def ws_browse(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: _Message
) -> None:
    box = loaded_shoebox(hass)
    rel, entries = await box.run(box.library.list_folder, msg["path"])
    titles = box.library.titles
    items = [_item(hass, e) for e in entries]
    if not rel:
        for item in items:
            item["name"] = titles[item["path"]]
    connection.send_result(msg["id"], {"path": rel, "items": items, "titles": titles})


@_command({vol.Required("type"): "shoebox/folders"})
async def ws_folders(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: _Message
) -> None:
    box = loaded_shoebox(hass)
    entries = await box.run(box.library.walk)
    folders = sorted(box.library.folders) + [e.path for e in entries if e.type == "folder"]
    connection.send_result(msg["id"], {"folders": folders})


async def _info(hass: HomeAssistant, box: Shoebox, path: str) -> dict[str, Any]:
    real = await box.run(box.library.resolve_file, path)
    rel = box.library.relative(real)
    info = await box.run(imaging.info, real)
    return dict(info) | {
        "path": rel,
        "view": picture_url(hass, rel, VIEW),
        "base": picture_url(hass, rel, BASE, crop=False),
    }


@_command({vol.Required("type"): "shoebox/info", vol.Required("path"): str})
async def ws_info(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: _Message
) -> None:
    connection.send_result(msg["id"], await _info(hass, loaded_shoebox(hass), msg["path"]))


@_command(
    {
        vol.Required("type"): "shoebox/edit",
        vol.Required("path"): str,
        vol.Optional("rotate", default=0): vol.All(
            vol.Coerce(int), vol.In([-270, -180, -90, 0, 90, 180, 270])
        ),
        vol.Optional("orientation"): vol.All(vol.Coerce(int), vol.Range(min=1, max=8)),
        vol.Required("crop"): vol.Any(None, vol.All([FRACTION], vol.Length(min=4, max=4))),
    }
)
async def ws_edit(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: _Message
) -> None:
    """Save the editor: turn (or set the orientation), then crop as shown, or remove the crop."""
    box = loaded_shoebox(hass)
    real = await box.run(box.library.resolve_file, msg["path"])
    crop = tuple(msg["crop"]) if msg["crop"] is not None else None
    await box.run(
        partial(imaging.edit, real, msg["rotate"], crop, orientation=msg.get("orientation"))
    )
    box.rotations.async_file_changed(box.library.relative(real))
    connection.send_result(msg["id"], await _info(hass, box, msg["path"]))


@callback
def async_setup_websocket(hass: HomeAssistant) -> None:
    for command in (ws_browse, ws_search, ws_folders, ws_info, ws_edit):
        websocket_api.async_register_command(hass, command)
