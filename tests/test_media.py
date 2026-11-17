from __future__ import annotations

import os
from pathlib import Path

import pytest

from custom_components.shoebox import media
from custom_components.shoebox.media import MediaError

from .conftest import Tree

# ---------------------------------------------------------------- resolve


@pytest.mark.parametrize("path", ["a/b.jpg", " a/b.jpg ", "a/./b.jpg"])
def test_resolve_relative(tree: Tree, path: str) -> None:
    root = tree("a/b.jpg")
    assert media.resolve(root, path) == Path(os.path.realpath(root / "a/b.jpg"))


def test_resolve_absolute_below_root(tree: Tree) -> None:
    root = tree("a/b.jpg")
    assert media.resolve(root, str(root / "a/b.jpg")).name == "b.jpg"


def test_resolve_need_not_exist(media_root: Path) -> None:
    assert media.resolve(media_root, "new/folder").name == "folder"


@pytest.mark.parametrize(
    ("path", "message"),
    [
        ("../x", "'..' is not allowed"),
        ("a/../../x", "'..' is not allowed"),
        ("a\0b", "invalid path"),
        ("/etc/passwd", "outside"),
        ("", "media folder itself"),
        (".", "media folder itself"),
    ],
)
def test_resolve_refuses(media_root: Path, path: str, message: str) -> None:
    with pytest.raises(MediaError, match=message):
        media.resolve(media_root, path)


def test_resolve_allows_root_when_asked(media_root: Path) -> None:
    assert media.resolve(media_root, ".", allow_root=True) == Path(os.path.realpath(media_root))


def test_resolve_refuses_symlink_itself(tree: Tree) -> None:
    root = tree("a.jpg")
    (root / "link.jpg").symlink_to(root / "a.jpg")
    with pytest.raises(MediaError, match="symbolic link"):
        media.resolve(root, "link.jpg")


def test_resolve_refuses_linked_folder_leading_outside(tmp_path: Path, media_root: Path) -> None:
    (tmp_path / "outside").mkdir()
    (media_root / "escape").symlink_to(tmp_path / "outside")
    with pytest.raises(MediaError, match="outside"):
        media.resolve(media_root, "escape/secret.txt")


def test_resolve_follows_linked_folder_inside(tree: Tree) -> None:
    root = tree("real/a.jpg")
    (root / "alias").symlink_to(root / "real")
    assert media.resolve(root, "alias/a.jpg") == Path(os.path.realpath(root / "real/a.jpg"))


# ---------------------------------------------------------------- listing


def test_walk_lists_everything_sorted_without_hidden_or_links(tree: Tree) -> None:
    root = tree("b/2.jpg", "b/1.txt", "a/", ".hidden/x.jpg", "b/.dot.jpg")
    (root / "b/link.jpg").symlink_to(root / "b/2.jpg")
    (root / "linkdir").symlink_to(root / "a")
    entries = media.walk(root)
    assert [(e.path, e.type) for e in entries] == [
        ("a", "folder"),
        ("b", "folder"),
        ("b/1.txt", "file"),
        ("b/2.jpg", "image"),
    ]
    assert entries[3].size > 0
    assert entries[3].as_dict()["path"] == "b/2.jpg"


def test_list_folder_folders_first_then_files_by_name(tree: Tree) -> None:
    root = tree("x/B.jpg", "x/a.txt", "x/z/", "x/.h.jpg")
    rel, entries = media.list_folder(root, "x")
    assert rel == "x"
    assert [e.name for e in entries] == ["z", "a.txt", "B.jpg"]


def test_list_folder_root_and_refusals(tree: Tree) -> None:
    root = tree("a.jpg")
    assert media.list_folder(root) == ("", media.list_folder(root, "")[1])
    with pytest.raises(MediaError, match="not a folder"):
        media.list_folder(root, "a.jpg")


# ---------------------------------------------------------------- patterns


@pytest.mark.parametrize(
    ("pattern", "path", "expected"),
    [
        ("*.jpg", "a.jpg", True),
        ("*.jpg", "x/a.jpg", False),
        ("x/*", "x/a.jpg", True),
        ("**", "x/y/a.jpg", True),
        ("x/**", "x/y/a.jpg", True),
        ("**/a.jpg", "a.jpg", True),
        ("**/a.jpg", "x/y/a.jpg", True),
        ("?.jpg", "a.jpg", True),
        ("?.jpg", "ab.jpg", False),
        ("[ab].jpg", "b.jpg", True),
        ("[!ab].jpg", "b.jpg", False),
        ("[!ab].jpg", "c.jpg", True),
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
    ("pattern", "message"), [("", "empty"), ("  ", "empty"), ("re:(", "invalid")]
)
def test_compile_pattern_refuses(pattern: str, message: str) -> None:
    with pytest.raises(MediaError, match=message):
        media.compile_pattern(pattern)


def test_select_by_type(tree: Tree) -> None:
    entries = media.walk(tree("x/a.jpg", "x/b.txt"))
    assert [e.path for e in media.select(entries, "**", "image")] == ["x/a.jpg"]
    assert [e.path for e in media.select(entries, "**", "folder")] == ["x"]
    assert len(media.select(entries, "**")) == 3
    with pytest.raises(MediaError, match="type must be"):
        media.select(entries, "**", "video")


def test_first_match_falls_through(tree: Tree) -> None:
    entries = media.walk(tree("evening/a.jpg", "evening/b.jpg", "morning/c.txt"))
    assert media.first_match(entries, ["morning/*", "evening/*"]) == (
        "evening/*",
        ["evening/a.jpg", "evening/b.jpg"],
    )
    assert media.first_match(entries, ["night/*"]) == (None, [])


@pytest.mark.parametrize(
    ("current", "expected"),
    [(None, 0), ("a", 1), ("c", 0), ("a5", 1), ("b0", 2), ("z", 0)],
)
def test_advance(current: str | None, expected: int) -> None:
    assert media.advance(["a", "b", "c"], current) == expected


def test_advance_empty() -> None:
    assert media.advance([], "a") == -1


# ---------------------------------------------------------------- file operations


def test_create_folder(tree: Tree) -> None:
    root = tree("a.jpg")
    assert media.create_folder(root, "x/y") == "x/y"
    assert media.create_folder(root, "x/y") == "x/y"
    with pytest.raises(MediaError, match="not a folder"):
        media.create_folder(root, "a.jpg")


def test_move(tree: Tree) -> None:
    root = tree("a.jpg", "dest/", "dest/b.jpg", "b.jpg")
    assert media.move(root, "a.jpg", "dest") == "dest/a.jpg"
    assert media.move(root, "dest/a.jpg", "") == "a.jpg"


@pytest.mark.parametrize(
    ("path", "to", "message"),
    [
        ("missing.jpg", "dest", "does not exist"),
        ("a.jpg", "b.jpg", "not a folder"),
        ("b.jpg", "dest", "already exists"),
        ("dest", "dest/sub", "into itself"),
        ("dest", "dest", "into itself"),
    ],
)
def test_move_refuses(tree: Tree, path: str, to: str, message: str) -> None:
    root = tree("a.jpg", "b.jpg", "dest/b.jpg", "dest/sub/")
    with pytest.raises(MediaError, match=message):
        media.move(root, path, to)


def test_rename(tree: Tree) -> None:
    root = tree("x/a.jpg", "x/b.jpg")
    assert media.rename(root, "x/a.jpg", "c.jpg") == "x/c.jpg"
    assert media.rename(root, "x", "y") == "y"


@pytest.mark.parametrize(
    ("path", "name", "message"),
    [
        ("x/a.jpg", "b.jpg", "already exists"),
        ("x/a.jpg", "s/b.jpg", "not a valid name"),
        ("x/a.jpg", "..", "not a valid name"),
        ("x/a.jpg", " a.jpg", "not a valid name"),
        ("x/gone.jpg", "c.jpg", "does not exist"),
    ],
)
def test_rename_refuses(tree: Tree, path: str, name: str, message: str) -> None:
    root = tree("x/a.jpg", "x/b.jpg")
    with pytest.raises(MediaError, match=message):
        media.rename(root, path, name)


def test_delete_file_and_folder(tree: Tree) -> None:
    root = tree("x/a.jpg", "x/y/b.jpg", "c.jpg")
    assert media.delete(root, "c.jpg") == "c.jpg"
    assert media.delete(root, "x") == "x"
    assert list(root.iterdir()) == []
    with pytest.raises(MediaError, match="does not exist"):
        media.delete(root, "x")
