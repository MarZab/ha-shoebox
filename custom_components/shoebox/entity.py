"""What every rotation entity shares: its device and its rotation."""

from __future__ import annotations

from typing import ClassVar

from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from .const import CONF_ORDER, CONF_PATTERNS, DOMAIN, ORDER_PATH, SIGNAL_ROTATION
from .rotations import RotationState
from .runtime import Shoebox


class RotationEntity(Entity):
    _attr_has_entity_name = True
    _attr_should_poll = False
    _unique_suffix: ClassVar[str] = ""  # tells apart the entities of one rotation

    def __init__(self, shoebox: Shoebox, subentry: ConfigSubentry) -> None:
        self.shoebox = shoebox
        self.rotation_id = subentry.subentry_id
        self._attr_unique_id = "_".join(filter(None, (subentry.subentry_id, self._unique_suffix)))
        self.patterns: list[str] = list(subentry.data.get(CONF_PATTERNS, []))
        self.order: str = subentry.data.get(CONF_ORDER, ORDER_PATH)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, subentry.subentry_id)},
            name=subentry.title,
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def rotation(self) -> RotationState:
        return self.shoebox.rotations.state(self.rotation_id)

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_ROTATION.format(self.rotation_id), self._rotation_changed
            )
        )

    @callback
    def _rotation_changed(self) -> None:
        self.async_write_ha_state()
