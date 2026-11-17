"""Uploads into a folder below the media root: safe names, never overwriting.

The upload streams into a hidden temporary file in the target folder (hidden names are skipped by
every listing); finish() then moves it to a free name: "photo.jpg", else "photo-1.jpg",
"photo-2.jpg", ... A name is claimed with O_CREAT | O_EXCL, so two uploads at the same time never
get the same name and an existing file is never replaced. This module does not import Home
Assistant.
"""

from __future__ import annotations

import os
from pathlib import Path
import tempfile
from typing import Final
import unicodedata

from .media import MediaError, relative, resolve

MAX_NAME: Final = 200
MEDIA_TYPES: Final = ("image/", "video/", "audio/")


def safe_name(filename: str) -> str:
    """The file name to store.

    The last part of what the browser sent (also after "\\"), without control characters, leading
    dots or surrounding spaces, shortened to MAX_NAME keeping the suffix.
    """
    name = unicodedata.normalize("NFC", str(filename or ""))
    name = name.replace("\\", "/").rsplit("/", 1)[-1]
    name = "".join(c for c in name if unicodedata.category(c)[0] != "C").strip().lstrip(".").strip()
    if not name:
        raise MediaError(f"'{filename}' is not a valid file name")
    if len(name) > MAX_NAME:
        stem, suffix = os.path.splitext(name)
        name = stem[: MAX_NAME - len(suffix)].rstrip() + suffix
    return name


def check_type(name: str, content_type: str | None) -> None:
    """Only pictures, videos and audio, by the type the browser declared."""
    if not (content_type or "").lower().startswith(MEDIA_TYPES):
        raise MediaError(f"'{name}': only pictures, videos and audio can be uploaded")


def target_folder(root: Path, folder: str) -> Path:
    """The folder to upload into ("" is the media folder); it must exist."""
    real = resolve(root, folder or ".", allow_root=True)
    if not real.is_dir():
        raise MediaError(f"'{folder}' is not a folder")
    return real


def temp_file(folder: Path) -> tuple[int, Path]:
    """A new hidden temporary file in the folder, on the same file system so finish() renames."""
    fd, tmp = tempfile.mkstemp(prefix=".upload-", suffix=".tmp", dir=folder)
    return fd, Path(tmp)


def free_name(folder: Path, name: str) -> Path:
    """Claim the first free name ("a.jpg", "a-1.jpg", ...) by creating it empty, exclusively."""
    stem, suffix = os.path.splitext(name)
    for n in range(10000):
        candidate = folder / (name if n == 0 else f"{stem}-{n}{suffix}")
        try:
            fd = os.open(candidate, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o644)
        except FileExistsError:
            continue
        os.close(fd)
        return candidate
    raise MediaError(f"no free name for '{name}'")


def finish(root: Path, folder: Path, tmp: Path, name: str) -> str:
    """Move the complete upload to a free name in the folder; returns its path below the root."""
    target = free_name(folder, name)
    try:
        os.chmod(tmp, 0o644)
        os.replace(tmp, target)  # replaces only the empty placeholder claimed just now
    except BaseException:
        target.unlink(missing_ok=True)
        raise
    return relative(root, target)
