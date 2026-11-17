from __future__ import annotations

import os
from pathlib import Path

import pytest

from custom_components.shoebox import media
from custom_components.shoebox.errors import MediaError

from .conftest import Tree

# ---------------------------------------------------------------- paths stay below the root


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("a/b.jpg", "a/b.jpg"),
        (" a/./b.jpg ", "a/b.jpg"),
        ("new/folder", "new/folder"),  # need not exist
        ("ROOT/a/b.jpg", "a/b.jpg"),  # absolute below the root
    ],
)
def test_resolve(tree: Tree, path: str, expected: str) -> None:
    root = tree("a/b.jpg")
    path = path.replace("ROOT", str(root))
    assert media.resolve(root, path) == Path(os.path.realpath(root / expected))


@pytest.mark.parametrize(
    ("path", "message"),
    [
        ("../x", '".." is not allowed'),
        ("a/../../x", '".." is not allowed'),
        ("a\0b", "Invalid path"),
        ("/etc/passwd", "outside"),
        ("", "media folder itself"),
        ("link.jpg", "symbolic link"),
        ("escape/secret.txt", "outside"),
    ],
)
def test_resolve_refuses(tree: Tree, tmp_path: Path, path: str, message: str) -> None:
    root = tree("a.jpg", "inner/b.jpg")
    (tmp_path / "outside").mkdir()
    (root / "link.jpg").symlink_to(root / "a.jpg")
    (root / "escape").symlink_to(tmp_path / "outside")
    with pytest.raises(MediaError, match=message):
        media.resolve(root, path)


def test_resolve_follows_links_that_stay_inside(tree: Tree) -> None:
    root = tree("real/a.jpg")
    (root / "alias").symlink_to(root / "real")
    assert media.resolve(root, "alias/a.jpg") == Path(os.path.realpath(root / "real/a.jpg"))
    assert media.resolve(root, ".", allow_root=True) == Path(os.path.realpath(root))


# ---------------------------------------------------------------- listing


def test_walk_lists_everything_sorted_without_hidden_or_links(tree: Tree) -> None:
    root = tree("b/2.jpg", "b/1.txt", "a/", ".hidden/x.jpg", "b/.dot.jpg")
    (root / "b/link.jpg").symlink_to(root / "b/2.jpg")
    (root / "linkdir").symlink_to(root / "a")
    assert [(e.path, e.type) for e in media.walk(root)] == [
        ("a", "folder"),
        ("b", "folder"),
        ("b/1.txt", "file"),
        ("b/2.jpg", "image"),
    ]


def test_list_folder_shows_folders_first_then_files_by_name(tree: Tree) -> None:
    root = tree("x/B.jpg", "x/a.txt", "x/z/", "x/.h.jpg")
    rel, entries = media.list_folder(root, "x")
    assert (rel, [e.name for e in entries]) == ("x", ["z", "a.txt", "B.jpg"])
    with pytest.raises(MediaError, match="not a folder"):
        media.list_folder(root, "x/a.txt")


# ---------------------------------------------------------------- patterns and order


@pytest.mark.parametrize(
    ("pattern", "path", "expected"),
    [
        ("*.jpg", "a.jpg", True),
        ("*.jpg", "x/a.jpg", False),
        ("x/*", "x/a.jpg", True),
        ("x/**", "x/y/a.jpg", True),
        ("**/a.jpg", "a.jpg", True),
        ("**/a.jpg", "x/y/a.jpg", True),
        ("?.jpg", "ab.jpg", False),
        ("[ab].jpg", "b.jpg", True),
        ("[!ab].jpg", "b.jpg", False),
        ("[ab.jpg", "[ab.jpg", True),
        ("/x/*", "x/a.jpg", True),
        ("a(1).jpg", "a(1).jpg", True),
        ("re:summer", "2024 summer/a.jpg", True),
        ("re:^summer", "2024 summer/a.jpg", False),
    ],
)
def test_matches(pattern: str, path: str, expected: bool) -> None:
    assert media.matches(pattern, path) is expected


@pytest.mark.parametrize(
    ("pattern", "message"),
    [(" ", "empty"), ("re:(", "Invalid pattern"), ("!", "empty"), ("!re:(", "Invalid pattern")],
)
def test_bad_patterns(pattern: str, message: str) -> None:
    with pytest.raises(MediaError, match=message):
        media.check_pattern(pattern)


@pytest.mark.parametrize(
    ("patterns", "expected"),
    [
        (["evening/*"], ["evening/a.jpg"]),
        (["evening/**", "night/*"], ["evening/a.jpg", "evening/private/b.jpg", "night/c.jpg"]),
        (["evening/**", "**/a.jpg"], ["evening/a.jpg", "evening/private/b.jpg"]),  # once each
        (["evening/**", "night/*", "!**/private/**"], ["evening/a.jpg", "night/c.jpg"]),
        (["**", "!re:^night/"], ["evening/a.jpg", "evening/private/b.jpg"]),
        (["!night/*"], []),
    ],
)
def test_select_pictures_combines_patterns_and_exclusions(
    tree: Tree, patterns: list[str], expected: list[str]
) -> None:
    entries = media.walk(
        tree("evening/a.jpg", "evening/private/b.jpg", "night/c.jpg", "night/d.txt")
    )
    assert media.select_pictures(entries, patterns) == expected


@pytest.mark.parametrize(
    ("files", "current", "expected"),
    [
        (["a", "b", "c"], None, 0),
        (["a", "b", "c"], "a", 1),
        (["a", "b", "c"], "c", 0),  # wraps
        (["a", "b", "c"], "b0", 2),  # current file gone: the one sorted after it
        (["a", "b", "c"], "z", 0),
        ([], "a", -1),
    ],
)
def test_advance(files: list[str], current: str | None, expected: int) -> None:
    assert media.advance(files, current) == expected


# ---------------------------------------------------------------- file operations


def test_file_operations(tree: Tree) -> None:
    root = tree("a.jpg", "dest/")
    assert media.create_folder(root, "x/y") == "x/y"
    assert media.move(root, "a.jpg", "dest") == "dest/a.jpg"
    assert media.rename(root, "dest/a.jpg", "b.jpg") == "dest/b.jpg"
    assert media.move(root, "dest/b.jpg", "") == "b.jpg"
    assert media.delete(root, "x") == "x"
    assert sorted(p.name for p in root.iterdir()) == ["b.jpg", "dest"]


@pytest.mark.parametrize(
    ("call", "message"),
    [
        (lambda r: media.create_folder(r, "a.jpg"), "not a folder"),
        (lambda r: media.move(r, "missing.jpg", "dest"), "does not exist"),
        (lambda r: media.move(r, "a.jpg", "b.jpg"), "not a folder"),
        (lambda r: media.move(r, "b.jpg", "dest"), "already exists"),
        (lambda r: media.move(r, "dest", "dest/sub"), "into itself"),
        (lambda r: media.rename(r, "a.jpg", "b.jpg"), "already exists"),
        (lambda r: media.rename(r, "a.jpg", "s/b.jpg"), "not a valid name"),
        (lambda r: media.rename(r, "a.jpg", " a.jpg"), "not a valid name"),
        (lambda r: media.delete(r, "missing.jpg"), "does not exist"),
    ],
)
def test_file_operations_refuse(tree: Tree, call: object, message: str) -> None:
    root = tree("a.jpg", "b.jpg", "dest/b.jpg", "dest/sub/")
    with pytest.raises(MediaError, match=message):
        call(root)  # type: ignore[operator]
