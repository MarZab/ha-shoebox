"""One image entity per rotation, showing its current picture."""

from __future__ import annotations

from datetime import datetime
from typing import Any, override

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from . import ShoeboxConfigEntry
from .const import ENTITY_SIZE, SUBENTRY_ROTATION
from .entity import RotationEntity
from .runtime import Shoebox

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ShoeboxConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    for subentry in entry.subentries.values():
        if subentry.subentry_type == SUBENTRY_ROTATION:
            async_add_entities(
                [RotationImage(hass, entry.runtime_data, subentry)],
                config_subentry_id=subentry.subentry_id,
            )


class RotationImage(RotationEntity, ImageEntity):
    _attr_name = None
    _attr_translation_key = "rotation"
    _attr_content_type = "image/jpeg"

    def __init__(self, hass: HomeAssistant, shoebox: Shoebox, subentry: ConfigSubentry) -> None:
        ImageEntity.__init__(self, hass)
        RotationEntity.__init__(self, shoebox, subentry)

    @property
    @override
    def image_last_updated(self) -> datetime | None:
        updated = self.rotation.updated
        return dt_util.parse_datetime(updated) if updated else None

    @property
    @override
    def extra_state_attributes(self) -> dict[str, Any]:
        state = self.rotation
        return {
            "patterns": self.patterns,
            "order": self.order,
            "pattern": state.pattern,
            "file": state.file,
            "position": state.position,
            "count": state.count,
        }

    @override
    async def async_image(self) -> bytes | None:
        if not (file := self.rotation.file):
            return None
        variant = await self.shoebox.picture(file, *ENTITY_SIZE, "contain")
        return variant.data
