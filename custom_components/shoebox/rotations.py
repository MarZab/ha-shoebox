"""Rotations: which picture each rotation shows now, kept in Home Assistant storage.

A rotation's configuration (title, patterns) is its config subentry; this module keeps its state,
keyed by the subentry id.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Iterable, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, override

from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from . import media
from .const import SIGNAL_ROTATION, STORAGE_KEY, STORAGE_VERSION

type Runner = Callable[..., Awaitable[Any]]


@dataclass
class RotationState:
    file: str | None = None  # below the media folder
    position: int = 0  # 1-based; 0 before the first step
    count: int = 0
    pattern: str | None = None  # the pattern that selected the pictures
    updated: str | None = None  # ISO time of the last step


class RotationStore(Store[dict[str, Any]]):
    @override
    async def _async_migrate_func(
        self, old_major_version: int, old_minor_version: int, old_data: dict[str, Any]
    ) -> dict[str, Any]:
        if old_major_version > STORAGE_VERSION:
            raise NotImplementedError
        return old_data


class Rotations:
    def __init__(self, hass: HomeAssistant, root: Path, run: Runner) -> None:
        self.hass = hass
        self.root = root
        self._run = run
        self._store = RotationStore(hass, STORAGE_VERSION, STORAGE_KEY)
        self._states: dict[str, RotationState] = {}
        self._lock = asyncio.Lock()

    async def async_load(self, ids: Iterable[str]) -> None:
        """Load the state of these rotations; state of rotations that are gone is dropped."""
        stored = (await self._store.async_load() or {}).get("rotations", {})
        known = set(ids)
        self._states = {i: RotationState(**s) for i, s in stored.items() if i in known}
        if set(stored) - known:
            await self.async_save()

    async def async_save(self) -> None:
        await self._store.async_save(self._data())

    def _data(self) -> dict[str, Any]:
        return {"rotations": {i: asdict(s) for i, s in self._states.items()}}

    def state(self, rotation_id: str) -> RotationState:
        return self._states.get(rotation_id) or RotationState()

    async def async_advance(self, rotation_id: str, patterns: Sequence[str]) -> RotationState:
        """Move a rotation to its next picture, in path order, wrapping around."""
        async with self._lock:
            entries = await self._run(media.walk, self.root)
            used, files = await self._run(media.first_match, entries, list(patterns))
            index = media.advance(files, self.state(rotation_id).file)
            state = RotationState(
                file=files[index] if files else None,
                position=index + 1,
                count=len(files),
                pattern=used,
                updated=dt_util.utcnow().isoformat(),
            )
            self._states[rotation_id] = state
            self._store.async_delay_save(self._data, 1)
        async_dispatcher_send(self.hass, SIGNAL_ROTATION.format(rotation_id))
        return state

    def async_touch(self, rotation_id: str) -> None:
        """Tell listeners the rotation's current picture changed in place, e.g. after an edit."""
        async_dispatcher_send(self.hass, SIGNAL_ROTATION.format(rotation_id))
