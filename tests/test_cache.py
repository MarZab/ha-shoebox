from __future__ import annotations

import os
from pathlib import Path

import pytest

from custom_components.shoebox.cache import VariantCache


@pytest.fixture
def source(tmp_path: Path) -> Path:
    path = tmp_path / "a.jpg"
    path.write_bytes(b"picture")
    return path


@pytest.fixture
def cache(tmp_path: Path) -> VariantCache:
    return VariantCache(tmp_path / "cache", limit_bytes=25)


def test_key_changes_with_every_part(source: Path) -> None:
    base = VariantCache.key(source, 10, 10, "cover")
    assert VariantCache.key(source, 10, 10, "cover") == base
    variants = {
        VariantCache.key(source, 11, 10, "cover"),
        VariantCache.key(source, 10, 11, "cover"),
        VariantCache.key(source, 10, 10, "contain"),
        VariantCache.key(source, 10, 10, "cover", "nocrop"),
    }
    os.utime(source, ns=(1, 1))
    variants.add(VariantCache.key(source, 10, 10, "cover"))
    source.write_bytes(b"longer picture")
    os.utime(source, ns=(1, 1))
    variants.add(VariantCache.key(source, 10, 10, "cover"))
    assert base not in variants
    assert len(variants) == 6


def test_get_makes_once_then_reads_the_cache(cache: VariantCache, source: Path) -> None:
    made: list[int] = []

    def make() -> bytes:
        made.append(1)
        return b"jpeg"

    first = cache.get(source, 10, 10, "cover", make)
    assert (first.data, first.hit, made) == (b"jpeg", False, [1])
    stored = cache.directory / f"{first.key}.jpg"
    os.utime(stored, (0, 0))
    second = cache.get(source, 10, 10, "cover", make)
    assert (second.data, second.key, second.hit, made) == (b"jpeg", first.key, True, [1])
    assert stored.stat().st_mtime > 0
    assert cache.usage() == (1, 4)


@pytest.mark.parametrize(
    ("limit", "store"),
    [(0, True), (1 << 20, False)],  # the cache off, or a one-off picture such as a display trial
)
def test_nothing_is_stored(tmp_path: Path, source: Path, limit: int, store: bool) -> None:
    cache = VariantCache(tmp_path / "cache", limit_bytes=limit)
    for _ in range(2):
        variant = cache.get(source, 10, 10, "cover", lambda: b"jpeg", store=store)
        assert (variant.data, variant.hit) == (b"jpeg", False)
    assert not cache.directory.exists()


def test_make_failure_leaves_nothing(cache: VariantCache, source: Path) -> None:
    def fail() -> bytes:
        raise ValueError("broken")

    with pytest.raises(ValueError, match="broken"):
        cache.get(source, 10, 10, "cover", fail)
    assert cache.usage() == (0, 0)


def test_evict_removes_least_recently_used_but_not_the_new_one(
    cache: VariantCache, tmp_path: Path
) -> None:
    names = []
    for i, size in enumerate((10, 10, 10)):
        src = tmp_path / f"{i}.jpg"
        src.write_bytes(b"x")
        name = cache.get(src, 1, 1, "cover", lambda size=size: b"v" * size).key + ".jpg"
        os.utime(cache.directory / name, (i, i))
        names.append(name)
    assert not (cache.directory / names[0]).exists()
    assert cache.usage() == (2, 20)
    cache.limit_bytes = 0
    assert cache.evict(keep=names[2]) == 1
    assert [p.name for p in cache.directory.iterdir()] == [names[2]]


def test_clear_removes_only_its_own_files(cache: VariantCache, source: Path) -> None:
    cache.get(source, 1, 1, "cover", lambda: b"v")
    (cache.directory / ".leftover.tmp").write_bytes(b"")
    (cache.directory / "notes.txt").write_text("keep")
    assert cache.clear() == 2
    assert [p.name for p in cache.directory.iterdir()] == ["notes.txt"]
