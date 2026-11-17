from __future__ import annotations

import os
from pathlib import Path

import pytest

from custom_components.shoebox.cache import VariantCache, is_variant_name


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


def test_get_or_make_makes_once(cache: VariantCache, source: Path) -> None:
    made: list[int] = []

    def make() -> bytes:
        made.append(1)
        return b"jpeg"

    name, hit = cache.get_or_make(source, 10, 10, "cover", make)
    assert (hit, made) == (False, [1])
    os.utime(cache.directory / name, (0, 0))
    assert cache.get_or_make(source, 10, 10, "cover", make) == (name, True)
    assert made == [1]
    assert (cache.directory / name).stat().st_mtime > 0
    assert cache.path(name) == cache.directory / name
    assert cache.usage() == (1, 4)


def test_make_failure_leaves_nothing(cache: VariantCache, source: Path) -> None:
    def fail() -> bytes:
        raise ValueError("broken")

    with pytest.raises(ValueError, match="broken"):
        cache.get_or_make(source, 10, 10, "cover", fail)
    assert cache.usage() == (0, 0)


def test_evict_removes_least_recently_used_but_not_the_new_one(
    cache: VariantCache, tmp_path: Path
) -> None:
    names = []
    for i, size in enumerate((10, 10, 10)):
        src = tmp_path / f"{i}.jpg"
        src.write_bytes(b"x")
        name, _ = cache.get_or_make(src, 1, 1, "cover", lambda size=size: b"v" * size)
        os.utime(cache.directory / name, (i, i))
        names.append(name)
    assert not (cache.directory / names[0]).exists()
    assert cache.usage() == (2, 20)
    cache.limit_bytes = 0
    assert cache.evict(keep=names[2]) == 1
    assert [p.name for p in cache.directory.iterdir()] == [names[2]]


def test_clear_removes_only_its_own_files(cache: VariantCache, source: Path) -> None:
    cache.get_or_make(source, 1, 1, "cover", lambda: b"v")
    (cache.directory / ".leftover.tmp").write_bytes(b"")
    (cache.directory / "notes.txt").write_text("keep")
    assert cache.clear() == 2
    assert [p.name for p in cache.directory.iterdir()] == ["notes.txt"]


def test_empty_or_missing_cache(cache: VariantCache) -> None:
    assert cache.usage() == (0, 0)
    assert cache.evict() == 0
    assert cache.clear() == 0


@pytest.mark.parametrize(
    "name", ["../secret.jpg", "a.jpg", "0" * 63 + ".jpg", "0" * 64 + ".png", "G" * 64 + ".jpg"]
)
def test_path_refuses_foreign_names(cache: VariantCache, name: str) -> None:
    assert not is_variant_name(name)
    assert cache.path(name) is None


def test_path_of_missing_variant(cache: VariantCache) -> None:
    assert cache.path("0" * 64 + ".jpg") is None


def test_failed_write_leaves_no_temp_file(
    cache: VariantCache, source: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail(*_: object) -> None:
        raise OSError("disk full")

    monkeypatch.setattr("custom_components.shoebox.cache.os.replace", fail)
    with pytest.raises(OSError, match="disk full"):
        cache.get_or_make(source, 1, 1, "cover", lambda: b"v")
    assert list(cache.directory.iterdir()) == []


def test_variants_vanishing_meanwhile_are_skipped(
    cache: VariantCache, monkeypatch: pytest.MonkeyPatch
) -> None:
    cache.directory.mkdir()
    ghost = "0" * 64 + ".jpg"
    monkeypatch.setattr("custom_components.shoebox.cache.os.listdir", lambda _: [ghost])
    assert cache.usage() == (0, 0)
    assert cache.clear() == 0
