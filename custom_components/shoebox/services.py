"""The file actions. All are admin-only and work on paths below the media folder."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any, Final

from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
    callback,
)
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.service import async_register_admin_service
import probatio as vol

from . import imaging, media
from .const import DOMAIN
from .runtime import Shoebox

_FRACTION: Final = vol.All(vol.Coerce(float), vol.Range(min=0, max=1))
_PATH: Final = {vol.Required("path"): cv.string}

LIST_SCHEMA: Final = vol.Schema(
    {
        vol.Optional("pattern", default="**"): cv.string,
        vol.Optional("type", default="all"): vol.In(media.TYPES),
    }
)
PATH_SCHEMA: Final = vol.Schema(_PATH)
MOVE_SCHEMA: Final = vol.Schema({**_PATH, vol.Required("to"): cv.string})
RENAME_SCHEMA: Final = vol.Schema({**_PATH, vol.Required("name"): cv.string})
ROTATE_SCHEMA: Final = vol.All(
    vol.Schema(
        {
            **_PATH,
            vol.Exclusive("by", "rotate"): vol.All(
                vol.Coerce(int), vol.In([-270, -180, -90, 90, 180, 270])
            ),
            vol.Exclusive("orientation", "rotate"): vol.All(
                vol.Coerce(int), vol.Range(min=1, max=8)
            ),
        }
    ),
    cv.has_at_least_one_key("by", "orientation"),
)
CROP_SCHEMA: Final = vol.Schema(
    {
        **_PATH,
        vol.Optional("left"): _FRACTION,
        vol.Optional("top"): _FRACTION,
        vol.Optional("right"): _FRACTION,
        vol.Optional("bottom"): _FRACTION,
        vol.Optional("clear", default=False): cv.boolean,
    }
)
_SIDES: Final = ("left", "top", "right", "bottom")


def _shoebox(call: ServiceCall) -> Shoebox:
    if entries := call.hass.config_entries.async_loaded_entries(DOMAIN):
        shoebox: Shoebox = entries[0].runtime_data
        return shoebox
    raise ServiceValidationError(translation_domain=DOMAIN, translation_key="not_loaded")


async def _list(call: ServiceCall) -> ServiceResponse:
    box = _shoebox(call)
    entries = await box.run(media.walk, box.root)
    items = await box.run(media.select, entries, call.data["pattern"], call.data["type"])
    return {"count": len(items), "items": [dict(e.as_dict()) for e in items]}


async def _create_folder(call: ServiceCall) -> ServiceResponse:
    box = _shoebox(call)
    return {"path": await box.run(media.create_folder, box.root, call.data["path"])}


async def _move(call: ServiceCall) -> ServiceResponse:
    box = _shoebox(call)
    return {"path": await box.run(media.move, box.root, call.data["path"], call.data["to"])}


async def _rename(call: ServiceCall) -> ServiceResponse:
    box = _shoebox(call)
    return {"path": await box.run(media.rename, box.root, call.data["path"], call.data["name"])}


async def _delete(call: ServiceCall) -> ServiceResponse:
    box = _shoebox(call)
    return {"deleted": await box.run(media.delete, box.root, call.data["path"])}


async def _rotate(call: ServiceCall) -> ServiceResponse:
    box = _shoebox(call)
    real = await box.run(media.resolve_file, box.root, call.data["path"])
    if "orientation" in call.data:
        orientation: int = call.data["orientation"]
        await box.run(imaging.set_orientation, real, orientation)
    else:
        orientation = await box.run(imaging.rotate, real, call.data["by"])
    return {"path": media.relative(box.root, real), "orientation": orientation}


async def _crop(call: ServiceCall) -> ServiceResponse:
    box = _shoebox(call)
    real = await box.run(media.resolve_file, box.root, call.data["path"])
    crop: imaging.Box | None = None
    if not call.data["clear"]:
        if not all(side in call.data for side in _SIDES):
            raise ServiceValidationError(translation_domain=DOMAIN, translation_key="crop_sides")
        crop = (call.data["left"], call.data["top"], call.data["right"], call.data["bottom"])
    stored = await box.run(imaging.crop_shown, real, crop)
    return {"path": media.relative(box.root, real), "crop": list(stored) if stored else None}


type _Handler = Callable[[ServiceCall], Coroutine[Any, Any, ServiceResponse]]

SERVICES: Final[dict[str, tuple[_Handler, Any, SupportsResponse]]] = {
    "list": (_list, LIST_SCHEMA, SupportsResponse.ONLY),
    "create_folder": (_create_folder, PATH_SCHEMA, SupportsResponse.OPTIONAL),
    "move": (_move, MOVE_SCHEMA, SupportsResponse.OPTIONAL),
    "rename": (_rename, RENAME_SCHEMA, SupportsResponse.OPTIONAL),
    "delete": (_delete, PATH_SCHEMA, SupportsResponse.OPTIONAL),
    "rotate": (_rotate, ROTATE_SCHEMA, SupportsResponse.OPTIONAL),
    "crop": (_crop, CROP_SCHEMA, SupportsResponse.OPTIONAL),
}


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    for name, (handler, schema, response) in SERVICES.items():
        async_register_admin_service(hass, DOMAIN, name, handler, schema, response)
