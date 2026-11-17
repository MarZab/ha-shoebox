"""Prepared pictures on disk: derived data only, safe to clear.

One JPEG per (file path, file size, file mtime, width, height, fit), named by a hash of that key.
Any change to a file changes its size or mtime and so produces a new variant; the old one ages out.
Using a variant touches its mtime, and above the size limit the least recently used variants are
removed. A limit of 0 turns the cache off: pictures are prepared on every request and nothing is
stored. Only files named like the cache's own are ever removed. This module does not import Home
Assistant.
"""

from __future__ import annotations

from collections.abc import Callable
import contextlib
from dataclasses import dataclass
import hashlib
import os
from pathlib import Path
import re
import tempfile
import threading
from typing import Final

VERSION: Final = "1"  # part of every key: bump when render() output changes
_NAME: Final = re.compile(r"\A[0-9a-f]{64}\.jpg\Z")
_TMP: Final = re.compile(r"\A\.[^/]*\.tmp\Z")


def is_variant_name(name: str) -> bool:
    return bool(_NAME.match(name))


@dataclass(frozen=True)
class Variant:
    data: bytes
    key: str  # identifies this prepared picture, e.g. for an ETag
    hit: bool


class VariantCache:
    def __init__(self, directory: Path, limit_bytes: int) -> None:
        self.directory = Path(directory)
        self.limit_bytes = limit_bytes
        self._lock = threading.Lock()

    @staticmethod
    def key(source: Path, width: int, height: int, fit: str, extra: str = "") -> str:
        st = os.stat(source)
        text = f"{VERSION}|{os.path.realpath(source)}|{st.st_size}|{st.st_mtime_ns}"
        text += f"|{width}x{height}|{fit}"
        if extra:
            text += "|" + extra
        return hashlib.sha256(text.encode()).hexdigest()

    @property
    def enabled(self) -> bool:
        return self.limit_bytes > 0

    def get(
        self,
        source: Path,
        width: int,
        height: int,
        fit: str,
        make: Callable[[], bytes],
        extra: str = "",
    ) -> Variant:
        """The prepared picture, from the cache or made now (and stored when the cache is on)."""
        key = self.key(source, width, height, fit, extra)
        if not self.enabled:
            return Variant(make(), key, hit=False)
        target = self.directory / f"{key}.jpg"
        try:
            data = target.read_bytes()
            os.utime(target)  # used now, for least-recently-used order
        except FileNotFoundError:
            pass
        else:
            return Variant(data, key, hit=True)
        data = make()
        self.directory.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".", suffix=".tmp", dir=self.directory)
        try:
            with os.fdopen(fd, "wb") as f:
                f.write(data)
            os.replace(tmp, target)
        except BaseException:
            if os.path.exists(tmp):
                os.unlink(tmp)
            raise
        self.evict(keep=target.name)
        return Variant(data, key, hit=False)

    def _files(self) -> list[tuple[float, int, str]]:
        try:
            names = os.listdir(self.directory)
        except FileNotFoundError:
            return []
        out: list[tuple[float, int, str]] = []
        for n in names:
            if is_variant_name(n):
                try:
                    st = os.stat(self.directory / n)
                except FileNotFoundError:
                    continue
                out.append((st.st_mtime, st.st_size, n))
        return out

    def usage(self) -> tuple[int, int]:
        """(number of variants, bytes)."""
        files = self._files()
        return len(files), sum(f[1] for f in files)

    def evict(self, keep: str | None = None) -> int:
        """Remove least recently used variants until within the limit; returns how many went."""
        with self._lock:
            files = sorted(self._files())
            total = sum(f[1] for f in files)
            removed = 0
            for _, size, name in files:
                if total <= self.limit_bytes:
                    break
                if name == keep:
                    continue
                with contextlib.suppress(FileNotFoundError):
                    os.unlink(self.directory / name)
                total -= size
                removed += 1
            return removed

    def clear(self) -> int:
        """Remove every variant and leftover temporary file; nothing else in the folder."""
        removed = 0
        with self._lock:
            try:
                names = os.listdir(self.directory)
            except FileNotFoundError:
                return 0
            for n in names:
                if is_variant_name(n) or _TMP.match(n):
                    try:
                        os.unlink(self.directory / n)
                    except FileNotFoundError:
                        continue
                    removed += 1
        return removed
