"""Draw the Shoebox brand icon: a photo standing in an open box.

Usage: brand_icon.py <brand folder>  (writes icon.png at 256 px and icon@2x.png at 512 px)
"""

from __future__ import annotations

from pathlib import Path
import sys

from PIL import Image, ImageDraw

BOX = (3, 169, 244)
BOX_DARK = (2, 136, 209)
PHOTO = (236, 239, 241)
SKY = (179, 229, 252)
HILL = (76, 175, 80)
SUN = (255, 193, 7)
SCALE = 4  # draw large, then downsample for smooth edges


def draw(size: int) -> Image.Image:
    s = size * SCALE
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    u = s / 16

    # the photo, tilted slightly, standing out of the box
    photo = Image.new("RGBA", (int(8 * u), int(7 * u)), (0, 0, 0, 0))
    p = ImageDraw.Draw(photo)
    pw, ph = photo.size
    m = 0.5 * u
    p.rounded_rectangle((0, 0, pw - 1, ph - 1), radius=0.4 * u, fill=PHOTO)
    p.rectangle((m, m, pw - m, ph - m), fill=SKY)
    p.polygon([(m, ph - m), (pw * 0.4, ph * 0.45), (pw * 0.7, ph - m)], fill=HILL)
    p.polygon([(pw * 0.45, ph - m), (pw * 0.72, ph * 0.55), (pw - m, ph - m)], fill=HILL)
    p.ellipse((pw * 0.62, ph * 0.18, pw * 0.82, ph * 0.18 + pw * 0.2), fill=SUN)
    photo = photo.rotate(-8, resample=Image.Resampling.BICUBIC, expand=True)
    im.alpha_composite(photo, (int(4.2 * u), int(0.8 * u)))

    # the box: body and a front lip, wider at the top
    d.polygon(
        [(1.5 * u, 6.5 * u), (14.5 * u, 6.5 * u), (13.5 * u, 15 * u), (2.5 * u, 15 * u)], fill=BOX
    )
    d.rounded_rectangle((1 * u, 6 * u, 15 * u, 8.2 * u), radius=0.5 * u, fill=BOX_DARK)
    return im.resize((size, size), Image.Resampling.LANCZOS)


def main(folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)
    draw(256).save(folder / "icon.png", optimize=True)
    draw(512).save(folder / "icon@2x.png", optimize=True)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
