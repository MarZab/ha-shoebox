from __future__ import annotations

import os
from pathlib import Path

import pytest

from custom_components.shoebox import upload
from custom_components.shoebox.errors import MediaError

from .conftest import Tree


@pytest.mark.parametrize(
    ("sent", "stored"),
    [
        ("photo.jpg", "photo.jpg"),
        ("C:\\Users\\me\\photo.jpg", "photo.jpg"),
        ("../../etc/photo.jpg", "photo.jpg"),
        ("  .hidden.jpg ", "hidden.jpg"),
        ("pho\x00to\x1f.jpg", "photo.jpg"),
        ("Cafe\u0301.jpg", "Café.jpg"),
    ],
)
def test_safe_name(sent: str, stored: str) -> None:
    assert upload.safe_name(sent) == stored


def test_safe_name_shortens_keeping_the_suffix() -> None:
    name = upload.safe_name("x" * 300 + ".jpeg")
    assert len(name) == upload.MAX_NAME
    assert name.endswith("x.jpeg")


@pytest.mark.parametrize("sent", ["", "..", "a/", "...", "\x00"])
def test_safe_name_refuses(sent: str) -> None:
    with pytest.raises(MediaError, match="not a valid file name"):
        upload.safe_name(sent)


@pytest.mark.parametrize("content_type", ["image/jpeg", "VIDEO/mp4", "audio/mpeg"])
def test_check_type_accepts_media(content_type: str) -> None:
    upload.check_type("a", content_type)


@pytest.mark.parametrize("content_type", [None, "", "text/html", "application/x-image/"])
def test_check_type_refuses_other(content_type: str | None) -> None:
    with pytest.raises(MediaError, match="only pictures"):
        upload.check_type("a", content_type)


def test_target_folder(tree: Tree) -> None:
    root = tree("x/", "a.jpg")
    assert upload.target_folder(root, "") == Path(os.path.realpath(root))
    assert upload.target_folder(root, "x").name == "x"
    with pytest.raises(MediaError, match="not a folder"):
        upload.target_folder(root, "a.jpg")


def test_free_name_numbers_taken_names(tree: Tree) -> None:
    root = tree("a.jpg", "a-1.jpg")
    assert upload.free_name(root, "a.jpg").name == "a-2.jpg"
    assert upload.free_name(root, "a.jpg").name == "a-3.jpg"
    assert upload.free_name(root, "b").name == "b"


def test_finish_never_replaces_an_existing_file(tree: Tree) -> None:
    root = tree("x/a.jpg")
    folder = upload.target_folder(root, "x")
    before = (folder / "a.jpg").read_bytes()
    fd, tmp = upload.temp_file(folder)
    assert tmp.name.startswith(".upload-")
    os.write(fd, b"new")
    os.close(fd)
    assert upload.finish(folder, tmp, "a.jpg") == folder / "a-1.jpg"
    assert (folder / "a.jpg").read_bytes() == before
    assert (folder / "a-1.jpg").read_bytes() == b"new"
    assert not tmp.exists()


def test_finish_failure_releases_the_name(tree: Tree) -> None:
    root = tree("x/")
    folder = upload.target_folder(root, "x")
    with pytest.raises(FileNotFoundError):
        upload.finish(folder, folder / ".gone.tmp", "a.jpg")
    assert not (folder / "a.jpg").exists()
