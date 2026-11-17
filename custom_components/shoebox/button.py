"""One Next button per rotation: pressing it moves the rotation to its next picture."""

from __future__ import annotations

from typing import override

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import ShoeboxConfigEntry
from .const import SUBENTRY_ROTATION
from .entity import RotationEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ShoeboxConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    for subentry in entry.subentries.values():
        if subentry.subentry_type == SUBENTRY_ROTATION:
            async_add_entities(
                [NextButton(entry.runtime_data, subentry)],
                config_subentry_id=subentry.subentry_id,
            )


class NextButton(RotationEntity, ButtonEntity):
    _attr_translation_key = "next"
    _unique_suffix = "next"

    @override
    async def async_press(self) -> None:
        await self.shoebox.rotations.async_advance(self.rotation_id, self.patterns)
