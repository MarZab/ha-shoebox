from __future__ import annotations

import os
from pathlib import Path
import re

import pytest

from custom_components.shoebox.errors import MediaError
from custom_components.shoebox.library import Library

from .images import write_image


@pytest.fixture
def library(tmp_path: Path) -> Library:
    for name in ("local", "nas"):
        (tmp_path / name).mkdir()
    (tmp_path / "other").mkdir()
    write_image(tmp_path / "local/Family/a.jpg")
    write_image(tmp_path / "nas/Family/b.jpg")
    (tmp_path / "other/secret.txt").write_text("x")
    return Library({"local": tmp_path / "local", "nas": tmp_path / "nas"})


def test_paths_start_with_the_folder(library: Library, tmp_path: Path) -> None:
    real = library.resolve("local/Family/a.jpg")
    assert real == Path(os.path.realpath(tmp_path / "local/Family/a.jpg"))
    assert library.relative(real) == "local/Family/a.jpg"
    assert library.resolve_file("nas/Family/b.jpg").name == "b.jpg"


def test_absolute_paths_below_a_folder(library: Library, tmp_path: Path) -> None:
    assert library.locate(str(tmp_path / "nas/Family/b.jpg")) == (
        "nas",
        tmp_path / "nas",
        "Family/b.jpg",
    )


@pytest.mark.parametrize(
    ("path", "key"),
    [
        ("", "top_level"),
        ("/", "outside_media"),
        ("other/secret.txt", "unknown_folder"),
        ("local/../other/secret.txt", "parent_not_allowed"),
        ("a\0b", "invalid_path"),
    ],
)
def test_refusals(library: Library, path: str, key: str) -> None:
    with pytest.raises(MediaError) as err:
        library.resolve(path)
    assert err.value.key == key


def test_errors_name_prefixed_paths(library: Library) -> None:
    with pytest.raises(MediaError, match=re.escape('"local/Family/missing.jpg" does not exist')):
        library.delete("local/Family/missing.jpg")


def test_walk_covers_every_folder(library: Library) -> None:
    assert [e.path for e in library.walk() if e.type == "image"] == [
        "local/Family/a.jpg",
        "nas/Family/b.jpg",
    ]


def test_top_level_lists_the_folders(library: Library) -> None:
    rel, entries = library.list_folder("")
    assert (rel, [(e.path, e.type) for e in entries]) == (
        "",
        [("local", "folder"), ("nas", "folder")],
    )
    rel, entries = library.list_folder("nas/Family")
    assert (rel, [e.path for e in entries]) == ("nas/Family", ["nas/Family/b.jpg"])
    assert library.list_folder("nas")[0] == "nas"


def test_file_operations_keep_prefixes(library: Library) -> None:
    assert library.create_folder("nas/Album") == "nas/Album"
    assert library.rename("nas/Family/b.jpg", "c.jpg") == "nas/Family/c.jpg"
    assert library.move("local/Family/a.jpg", "nas/Album") == "nas/Album/a.jpg"
    assert library.move("nas/Album/a.jpg", "local") == "local/a.jpg"
    assert library.delete("nas/Album") == "nas/Album"


@pytest.mark.parametrize("call", ["create_folder", "delete"])
def test_a_media_folder_itself_cannot_change(library: Library, call: str) -> None:
    with pytest.raises(MediaError, match="media folder itself"):
        getattr(library, call)("nas")


def test_move_refuses_an_existing_target_in_another_folder(library: Library) -> None:
    library.create_folder("nas/Family/sub")
    write_image(library.folders["nas"] / "Family/a.jpg")
    with pytest.raises(MediaError, match=re.escape('"nas/Family/a.jpg" already exists')):
        library.move("local/Family/a.jpg", "nas/Family")


def test_uploads_land_in_a_chosen_folder(library: Library, tmp_path: Path) -> None:
    folder = library.upload_folder("nas/Family")
    tmp = folder / ".upload-x.tmp"
    tmp.write_bytes(b"jpeg")
    assert library.finish_upload(folder, tmp, "b.jpg") == "nas/Family/b-1.jpg"
    with pytest.raises(MediaError):
        library.upload_folder("")


def test_a_missing_folder_is_skipped_when_listing(tmp_path: Path) -> None:
    library = Library({"local": tmp_path / "missing"})
    assert library.walk() == []
    assert library.list_folder("") == ("", [])
