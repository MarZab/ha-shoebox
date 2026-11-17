"""Download the photos the documentation screenshots show into the dev media folder.

Usage: screenshot_photos.py <media folder>  (writes "<media folder>/Photos/Summer 2025/*.jpg")

The photos come from picsum.photos, which serves Unsplash photos under the Unsplash license
(free to use, no attribution needed). They are not in the repository; this fetches them again.
"""

from __future__ import annotations

from pathlib import Path
import sys
from urllib.request import urlopen

# picsum id -> file name
PHOTOS = {
    49: "santorini.jpg",
    164: "canal.jpg",
    211: "harbour.jpg",
    287: "hills.jpg",
    129: "sunset.jpg",
    237: "rex.jpg",
}
SIZE = (1600, 1067)


def main(media: Path) -> None:
    folder = media / "Photos" / "Summer 2025"
    folder.mkdir(parents=True, exist_ok=True)
    for picsum_id, name in PHOTOS.items():
        target = folder / name
        if target.exists():
            continue
        with urlopen(f"https://picsum.photos/id/{picsum_id}/{SIZE[0]}/{SIZE[1]}.jpg") as response:
            target.write_bytes(response.read())
        print(target)


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "tools/docker/media"))
