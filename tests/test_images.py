from __future__ import annotations

from pathlib import Path

from PIL import Image
import pytest

from .conftest import Tree
from .images import ORIENTATION_TAG, colour_at, write_image


@pytest.mark.parametrize(
    ("x", "y", "colour"),
    [(0.25, 0.25, "red"), (0.75, 0.25, "green"), (0.25, 0.75, "blue"), (0.75, 0.75, "white")],
)
def test_quadrants_read_back(tmp_path: Path, x: float, y: float, colour: str) -> None:
    assert colour_at(write_image(tmp_path / "a.jpg"), x, y) == colour


def test_jpeg_keeps_orientation_and_crop(tmp_path: Path) -> None:
    path = write_image(tmp_path / "a.jpg", orientation=6, crop=(0.1, 0.2, 0.9, 0.8))
    with Image.open(path) as im:
        assert im.getexif()[ORIENTATION_TAG] == 6
        assert b"crs:CropLeft" in im.info["xmp"]


def test_tree_lays_out_folders_pictures_and_files(tree: Tree) -> None:
    root = tree("empty/", "a/b.jpg", "a/c.txt")
    assert (root / "empty").is_dir()
    assert colour_at(root / "a/b.jpg", 0.75, 0.75) == "white"
    assert (root / "a/c.txt").read_text() == "a/c.txt"
