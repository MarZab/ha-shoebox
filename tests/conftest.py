from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import pytest

from .images import write_image

type Tree = Callable[..., Path]


@pytest.fixture
def media_root(tmp_path: Path) -> Path:
    root = tmp_path / "media"
    root.mkdir()
    return root


@pytest.fixture
def tree(media_root: Path) -> Tree:
    """Lay out the media root: "a/" is a folder, a picture suffix a quadrant picture, else text."""

    def make(*paths: str) -> Path:
        for rel in paths:
            target = media_root / rel
            if rel.endswith("/"):
                target.mkdir(parents=True, exist_ok=True)
            elif target.suffix.lower() in (".jpg", ".jpeg", ".png"):
                write_image(target)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(rel)
        return media_root

    return make
