"""Test pictures: four coloured quadrants, so orientation and crop can be read back by colour.

red   | green
------+------
blue  | white
"""

from __future__ import annotations

import io
from pathlib import Path

from PIL import Image

ORIENTATION_TAG = 0x0112
QUADRANTS = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "white": (255, 255, 255),
}
CRS = "http://ns.adobe.com/camera-raw-settings/1.0/"


def quadrants(width: int = 80, height: int = 40) -> Image.Image:
    im = Image.new("RGB", (width, height))
    w, h = width // 2, height // 2
    for name, box in (
        ("red", (0, 0, w, h)),
        ("green", (w, 0, width, h)),
        ("blue", (0, h, w, height)),
        ("white", (w, h, width, height)),
    ):
        im.paste(QUADRANTS[name], box)
    return im


def xmp_crop(left: float, top: float, right: float, bottom: float) -> bytes:
    return (
        '<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF '
        'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
        f'<rdf:Description rdf:about="" xmlns:crs="{CRS}" crs:HasCrop="True" '
        f'crs:CropLeft="{left}" crs:CropTop="{top}" crs:CropRight="{right}" '
        f'crs:CropBottom="{bottom}"/></rdf:RDF></x:xmpmeta>'
    ).encode()


def write_image(
    path: Path,
    size: tuple[int, int] = (80, 40),
    *,
    orientation: int = 1,
    crop: tuple[float, float, float, float] | None = None,
) -> Path:
    """A quadrant picture at `path`; the format follows the suffix (JPEG keeps EXIF and XMP)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    im = quadrants(*size)
    if path.suffix.lower() in (".jpg", ".jpeg"):
        exif = Image.Exif()
        if orientation != 1:
            exif[ORIENTATION_TAG] = orientation
        extra: dict[str, bytes] = {"xmp": xmp_crop(*crop)} if crop else {}
        im.save(path, "JPEG", quality=95, exif=exif.tobytes(), **extra)
    else:
        im.save(path)
    return path


def colour_at(image: Image.Image | bytes | Path, x: float, y: float) -> str:
    """The quadrant colour nearest to the pixel at fractions (x, y) of the image."""
    if isinstance(image, bytes):
        image = Image.open(io.BytesIO(image))
    elif isinstance(image, Path):
        image = Image.open(image)
    rgb = image.convert("RGB")
    px = rgb.getpixel(
        (min(int(x * rgb.width), rgb.width - 1), min(int(y * rgb.height), rgb.height - 1))
    )
    assert isinstance(px, tuple)
    return min(
        QUADRANTS,
        key=lambda name: sum((a - b) ** 2 for a, b in zip(px, QUADRANTS[name], strict=False)),
    )
