"""Rotations: which picture each rotation shows now, kept in Home Assistant storage.

A rotation's configuration (title, patterns) is its config subentry; this module keeps its state,
keyed by the subentry id.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Iterable, Sequence
from dataclasses import asdict, dataclass, field, fields as dataclass_fields
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.storage import Store
from homeassistant.util import dt as dt_util

from . import media
from .const import ORDER_PATH, ORDER_SHUFFLE, SIGNAL_ROTATION, STORAGE_KEY, STORAGE_VERSION
from .library import Library

type Runner = Callable[..., Awaitable[Any]]


@dataclass
class RotationState:
    file: str | None = None  # "local/Family/a.jpg"
    position: int = 0  # 1-based; 0 before the first step
    count: int = 0
    updated: str | None = None  # ISO time of the last step
    shown: list[str] = field(default_factory=list)  # shuffle: pictures shown in this round


class Rotations:
    def __init__(self, hass: HomeAssistant, library: Library, run: Runner) -> None:
        self.hass = hass
        self.library = library
        self._run = run
        self._store = Store[dict[str, Any]](hass, STORAGE_VERSION, STORAGE_KEY)
        self._states: dict[str, RotationState] = {}
        self._lock = asyncio.Lock()
        self._closed = False

    async def async_load(self, ids: Iterable[str]) -> None:
        """Load the state of these rotations; state of rotations that are gone is dropped."""
        stored = (await self._store.async_load() or {}).get("rotations", {})
        known = set(ids)
        fields = {f.name for f in dataclass_fields(RotationState)}
        self._states = {
            i: RotationState(**{k: v for k, v in s.items() if k in fields})
            for i, s in stored.items()
            if i in known
        }
        if set(stored) - known:
            await self.async_save()

    async def async_save(self) -> None:
        await self._store.async_save(self._data())

    def _data(self) -> dict[str, Any]:
        return {"rotations": {i: asdict(s) for i, s in self._states.items()}}

    def state(self, rotation_id: str) -> RotationState:
        return self._states.get(rotation_id) or RotationState()

    async def async_advance(
        self, rotation_id: str, patterns: Sequence[str], order: str = ORDER_PATH
    ) -> RotationState:
        """Move a rotation to its next picture: in path order, wrapping around, or shuffled."""
        async with self._lock:
            if self._closed:  # unloading: the next instance owns the state now
                return self.state(rotation_id)
            current = self.state(rotation_id)
            state: RotationState = await self._run(self._next, current, list(patterns), order)
            self._states[rotation_id] = state
            self._store.async_delay_save(self._data, 1)
        async_dispatcher_send(self.hass, SIGNAL_ROTATION.format(rotation_id))
        return state

    def _next(self, current: RotationState, patterns: list[str], order: str) -> RotationState:
        """Walk, select and choose: one job in the executor."""
        files = self.library.pictures(patterns)
        shown: list[str] = []
        if order == ORDER_SHUFFLE:
            file, shown = media.shuffle_next(files, current.shown, current.file)
            position = len(shown)
        else:
            index = media.advance(files, current.file)
            file, position = (files[index] if files else None), index + 1
        return RotationState(
            file=file,
            position=position,
            count=len(files),
            updated=dt_util.utcnow().isoformat(),
            shown=shown,
        )

    async def async_close(self) -> None:
        """Wait for a running Next press, then write the state; later changes are ignored."""
        async with self._lock:
            self._closed = True
            await self._store.async_save(self._data())  # also cancels a delayed save

    def async_paths_moved(self, old: str, new: str | None) -> None:
        """A file or folder was moved or renamed to `new`, or deleted (None)."""

        def moved(path: str) -> str | None:
            if path == old:
                return new
            if path.startswith(old + "/"):
                return None if new is None else new + path[len(old) :]
            return path

        for rotation_id, state in self._states.items():
            file = moved(state.file) if state.file else None
            shown = [p for p in (moved(p) for p in state.shown) if p]
            if file == state.file and shown == state.shown:
                continue
            state.file, state.shown = file, shown
            state.updated = dt_util.utcnow().isoformat()
            self._changed(rotation_id)

    def _changed(self, rotation_id: str) -> None:
        if not self._closed:
            self._store.async_delay_save(self._data, 1)
            async_dispatcher_send(self.hass, SIGNAL_ROTATION.format(rotation_id))

    def async_file_changed(self, path: str) -> None:
        """A file was edited in place: rotations showing it now count as updated."""
        now = dt_util.utcnow().isoformat()
        for rotation_id, state in self._states.items():
            if state.file == path:
                state.updated = now
                self._changed(rotation_id)
