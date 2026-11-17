"""Generate a small media folder for the dev Home Assistant.

Each picture shows its own name and an arrow pointing to its top, so rotation and crop are easy
to check by eye. Usage: sample_media.py <target folder>
"""

from __future__ import annotations

from pathlib import Path
import sys

from PIL import Image, ImageDraw
import pillow_heif

ORIENTATION_TAG = 0x0112

# path below the media folder, size, background colour, EXIF orientation
PICTURES: list[tuple[str, tuple[int, int], tuple[int, int, int], int]] = [
    ("Family/2024 Summer/beach.jpg", (1600, 1200), (52, 120, 190), 1),
    ("Family/2024 Summer/sideways.jpg", (1600, 1200), (210, 140, 40), 6),
    ("Family/2024 Summer/upside-down.jpg", (1200, 1600), (120, 60, 160), 3),
    ("Family/Kids art/drawing.png", (900, 1200), (240, 200, 60), 1),
    ("Phone/IMG_0001.heic", (1512, 2016), (40, 150, 90), 1),
    ("Wallpapers/forest.jpg", (1920, 1080), (30, 90, 50), 1),
    ("Wallpapers/city.jpg", (1920, 1080), (70, 70, 80), 1),
]


def picture(name: str, size: tuple[int, int], colour: tuple[int, int, int]) -> Image.Image:
    im = Image.new("RGB", size, colour)
    draw = ImageDraw.Draw(im)
    w, h = size
    draw.polygon([(w // 2, h // 10), (w // 2 - w // 8, h // 3), (w // 2 + w // 8, h // 3)], "white")
    draw.text((w // 20, h - h // 8), name, fill="white", font_size=max(24, h // 20))
    return im


def save(im: Image.Image, path: Path, orientation: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.suffix == ".heic":
        pillow_heif.from_pillow(im).save(path, quality=80)
        return
    if path.suffix == ".png":
        im.save(path)
        return
    exif = Image.Exif()
    if orientation != 1:
        exif[ORIENTATION_TAG] = orientation
    im.save(path, quality=85, exif=exif.tobytes())


def main(target: Path) -> None:
    for rel, size, colour, orientation in PICTURES:
        save(picture(rel, size, colour), target / rel, orientation)
    (target / "Documents").mkdir(parents=True, exist_ok=True)
    (target / "Documents/readme.txt").write_text("Not a picture.\n")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
