"""WebSocket commands of the panel. All are admin-only.

Pictures for the panel's images come back as URLs to the render view, signed for the user's
connection, because an <img> cannot send the Authorization header.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import timedelta
from functools import partial
from typing import Any, Final

from homeassistant.components import websocket_api
from homeassistant.components.http.auth import async_sign_path
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
import probatio as vol
from yarl import URL

from . import imaging, media
from .const import DOMAIN, PANEL_URL_LIFETIME_S, RENDER_URL
from .runtime import Shoebox
from .views import loaded_shoebox

THUMB: Final = (320, 320, "cover")
VIEW: Final = (2048, 2048, "contain")
BASE: Final = (1600, 1600, "contain")  # the editor draws a new crop on the whole picture
ROTATION: Final = "rotation"

_FRACTION: Final = vol.All(vol.Coerce(float), vol.Range(min=0, max=1))

type _Message = dict[str, Any]
type _Handler = Callable[[HomeAssistant, websocket_api.ActiveConnection, _Message], Awaitable[None]]


def picture_url(
    hass: HomeAssistant, path: str, size: tuple[int, int, str], *, crop: bool = True
) -> str:
    width, height, fit = size
    query = {"path": path, "size": f"{width}x{height}", "fit": fit}
    if not crop:
        query["crop"] = "0"
    url = str(URL(RENDER_URL).with_query(query))
    return async_sign_path(hass, url, timedelta(seconds=PANEL_URL_LIFETIME_S))


def _command(schema: dict[Any, Any]) -> Callable[[_Handler], websocket_api.WebSocketCommandHandler]:
    """An admin-only command; refusals come back as an error with the translated message."""

    def wrap(func: _Handler) -> websocket_api.WebSocketCommandHandler:
        async def handler(
            hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: _Message
        ) -> None:
            try:
                await func(hass, connection, msg)
            except HomeAssistantError as err:
                connection.send_error(msg["id"], "invalid", str(err))

        handler.__name__ = func.__name__
        return websocket_api.websocket_command(schema)(
            websocket_api.require_admin(websocket_api.async_response(handler))
        )

    return wrap


def _item(hass: HomeAssistant, entry: media.Entry) -> dict[str, Any]:
    item: dict[str, Any] = dict(entry.as_dict()) | {"name": entry.name}
    if entry.type == "image":
        item["thumb"] = picture_url(hass, entry.path, THUMB)
    return item


@_command({vol.Required("type"): "shoebox/browse", vol.Optional("path", default=""): str})
async def ws_browse(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: _Message
) -> None:
    box = loaded_shoebox(hass)
    rel, entries = await box.run(media.list_folder, box.root, msg["path"])
    connection.send_result(msg["id"], {"path": rel, "items": [_item(hass, e) for e in entries]})


@_command({vol.Required("type"): "shoebox/folders"})
async def ws_folders(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: _Message
) -> None:
    box = loaded_shoebox(hass)
    entries = await box.run(media.walk, box.root)
    connection.send_result(msg["id"], {"folders": [e.path for e in entries if e.type == "folder"]})


async def _info(hass: HomeAssistant, box: Shoebox, path: str) -> dict[str, Any]:
    real = await box.run(media.resolve_file, box.root, path)
    rel = media.relative(box.root, real)
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
        vol.Required("crop"): vol.Any(None, vol.All([_FRACTION], vol.Length(min=4, max=4))),
    }
)
async def ws_edit(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: _Message
) -> None:
    """Save the editor: turn (or set the orientation), then crop as shown, or remove the crop."""
    box = loaded_shoebox(hass)
    real = await box.run(media.resolve_file, box.root, msg["path"])
    crop = tuple(msg["crop"]) if msg["crop"] is not None else None
    await box.run(
        partial(imaging.edit, real, msg["rotate"], crop, orientation=msg.get("orientation"))
    )
    connection.send_result(msg["id"], await _info(hass, box, msg["path"]))


def _rotation_patterns(entry: ConfigEntry) -> list[tuple[str, str, list[str]]]:
    """(subentry id, title, patterns) of each rotation."""
    return [
        (sub.subentry_id, sub.title, list(sub.data.get("patterns", [])))
        for sub in entry.subentries.values()
        if sub.subentry_type == ROTATION
    ]


@_command({vol.Required("type"): "shoebox/rotations"})
async def ws_rotations(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: _Message
) -> None:
    box = loaded_shoebox(hass)
    entry = hass.config_entries.async_loaded_entries(DOMAIN)[0]
    entries = await box.run(media.walk, box.root)
    out = []
    for subentry_id, title, patterns in _rotation_patterns(entry):
        used, files = await box.run(media.first_match, entries, patterns)
        out.append(
            {
                "id": subentry_id,
                "title": title,
                "patterns": patterns,
                "pattern": used,
                "count": len(files),
            }
        )
    connection.send_result(msg["id"], {"rotations": out})


@_command(
    {
        vol.Required("type"): "shoebox/match",
        vol.Required("pattern"): vol.All([str], vol.Length(min=1)),
        vol.Optional("limit", default=24): vol.All(vol.Coerce(int), vol.Range(min=0, max=200)),
    }
)
async def ws_match(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: _Message
) -> None:
    """What patterns select: the pattern used, how many pictures, and the first few."""
    box = loaded_shoebox(hass)
    patterns = [p for p in msg["pattern"] if p.strip()]
    for pattern in patterns:
        await box.run(media.compile_pattern, pattern)
    entries = await box.run(media.walk, box.root)
    used, files = await box.run(media.first_match, entries, patterns)
    items = [{"path": f, "thumb": picture_url(hass, f, THUMB)} for f in files[: msg["limit"]]]
    connection.send_result(msg["id"], {"pattern": used, "count": len(files), "items": items})


@callback
def async_setup_websocket(hass: HomeAssistant) -> None:
    for command in (ws_browse, ws_folders, ws_info, ws_edit, ws_rotations, ws_match):
        websocket_api.async_register_command(hass, command)
