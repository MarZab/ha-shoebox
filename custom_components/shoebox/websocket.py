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
from homeassistant.helpers import entity_registry as er
import probatio as vol
from yarl import URL

from . import imaging, media
from .const import CONF_ORDER, DOMAIN, ORDER_PATH, PANEL_URL_LIFETIME_S, RENDER_URL
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
    rel, entries = await box.run(box.library.list_folder, msg["path"])
    connection.send_result(msg["id"], {"path": rel, "items": [_item(hass, e) for e in entries]})


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
        vol.Required("crop"): vol.Any(None, vol.All([_FRACTION], vol.Length(min=4, max=4))),
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


def _rotation_patterns(entry: ConfigEntry) -> list[tuple[str, str, list[str], str]]:
    """(subentry id, title, patterns, order) of each rotation."""
    return [
        (
            sub.subentry_id,
            sub.title,
            list(sub.data.get("patterns", [])),
            sub.data.get(CONF_ORDER, ORDER_PATH),
        )
        for sub in entry.subentries.values()
        if sub.subentry_type == ROTATION
    ]


@_command({vol.Required("type"): "shoebox/rotations"})
async def ws_rotations(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: _Message
) -> None:
    """Each rotation: what its patterns select now, its current picture and its entities."""
    box = loaded_shoebox(hass)
    entry = hass.config_entries.async_loaded_entries(DOMAIN)[0]
    registry = er.async_get(hass)
    entries = await box.run(box.library.walk)
    out = []
    for subentry_id, title, patterns, order in _rotation_patterns(entry):
        files = await box.run(media.select_pictures, entries, patterns)
        state = box.rotations.state(subentry_id)
        out.append(
            {
                "id": subentry_id,
                "title": title,
                "patterns": patterns,
                "order": order,
                "count": len(files),
                "position": state.position,
                "file": state.file,
                "thumb": picture_url(hass, state.file, THUMB) if state.file else None,
                "entity_id": registry.async_get_entity_id("image", DOMAIN, subentry_id),
                "next_entity_id": registry.async_get_entity_id(
                    "button", DOMAIN, f"{subentry_id}_next"
                ),
            }
        )
    connection.send_result(msg["id"], {"rotations": out})


@callback
def async_setup_websocket(hass: HomeAssistant) -> None:
    for command in (ws_browse, ws_folders, ws_info, ws_edit, ws_rotations):
        websocket_api.async_register_command(hass, command)
