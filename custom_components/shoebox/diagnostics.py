"""Diagnostics: options, cache usage and rotations. Rotation patterns may name folders; no file
contents and no listings."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from . import ShoeboxConfigEntry
from .const import CONF_ORDER, CONF_PATTERNS, ORDER_PATH, SUBENTRY_ROTATION


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ShoeboxConfigEntry
) -> dict[str, Any]:
    shoebox = entry.runtime_data
    files, size = await hass.async_add_executor_job(shoebox.cache.usage)
    rotations = []
    for sub in entry.subentries.values():
        if sub.subentry_type == SUBENTRY_ROTATION:
            state = shoebox.rotations.state(sub.subentry_id)
            rotations.append(
                {
                    "patterns": list(sub.data.get(CONF_PATTERNS, [])),
                    "order": sub.data.get(CONF_ORDER, ORDER_PATH),
                    "position": state.position,
                    "count": state.count,
                    "updated": state.updated,
                }
            )
    return {
        "options": dict(entry.options),
        "cache": {"files": files, "bytes": size, "limit_bytes": shoebox.cache.limit_bytes},
        "rotations": rotations,
    }
