"""Draw the Shoebox brand icon: a shoebox, its lid off behind it, with two photos inside.

Usage: brand_icon.py <brand folder>  (writes icon.png at 256 px and icon@2x.png at 512 px)
"""

from __future__ import annotations

from pathlib import Path
import sys

from PIL import Image, ImageDraw

BOX = (3, 169, 244)
BOX_DARK = (2, 119, 189)
INSIDE = (1, 87, 155)
PHOTO = (250, 250, 250)
SKY = (179, 229, 252)
HILL = (76, 175, 80)
HILL_DARK = (56, 142, 60)
SUN = (255, 193, 7)
SCALE = 4  # draw large, then downsample for smooth edges


def _photo(u: float, width: float, height: float, angle: float, *, sun: bool) -> Image.Image:
    """A photo with a white border: sky, two hills and maybe a sun, turned by `angle` degrees."""
    photo = Image.new("RGBA", (int(width * u), int(height * u)), (0, 0, 0, 0))
    p = ImageDraw.Draw(photo)
    w, h = photo.size
    b = 0.7 * u
    p.rounded_rectangle((0, 0, w - 1, h - 1), radius=0.5 * u, fill=PHOTO)
    p.rectangle((b, b, w - b, h - b), fill=SKY)
    p.polygon([(b, h - b), (w * 0.42, h * 0.38), (w * 0.7, h - b)], fill=HILL)
    p.polygon([(w * 0.48, h - b), (w * 0.72, h * 0.55), (w - b, h - b)], fill=HILL_DARK)
    if sun:
        p.ellipse((w * 0.66, h * 0.16, w * 0.84, h * 0.16 + w * 0.18), fill=SUN)
    return photo.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)


def draw(size: int) -> Image.Image:
    s = size * SCALE
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    u = s / 32

    def place(photo: Image.Image, cx: float, cy: float) -> None:
        im.alpha_composite(photo, (int(cx * u - photo.width / 2), int(cy * u - photo.height / 2)))

    # the lid, leaning against the back, and the dark inside of the box
    d.rounded_rectangle((5 * u, 5.5 * u, 27 * u, 9.5 * u), radius=1 * u, fill=BOX_DARK)
    d.rectangle((4 * u, 12.5 * u, 28 * u, 15.5 * u), fill=INSIDE)
    # two photos standing in it
    place(_photo(u, 11, 9, 8, sun=False), 11.5, 13)
    place(_photo(u, 11, 9, -6, sun=True), 20.5, 12)
    # the front: low and wide, with its rim
    d.rounded_rectangle((3 * u, 14.5 * u, 29 * u, 26.5 * u), radius=1.2 * u, fill=BOX)
    d.rectangle((3 * u, 14.5 * u, 29 * u, 16.7 * u), fill=BOX_DARK)
    return im.resize((size, size), Image.Resampling.LANCZOS)


def main(folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    draw(256).save(folder / "icon.png", optimize=True)
    draw(512).save(folder / "icon@2x.png", optimize=True)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
