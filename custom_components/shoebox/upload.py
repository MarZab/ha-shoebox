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

from .errors import MediaError
from .media import resolve

# In bytes, as file systems count: 255 for a name, less room for "-9999" from free_name
MAX_NAME: Final = 255 - len("-9999")
MEDIA_TYPES: Final = ("image/", "video/", "audio/")


def safe_name(filename: str) -> str:
    """The file name to store.

    The last part of what the browser sent (also after "\\"), without control characters, leading
    dots or surrounding spaces, shortened to MAX_NAME bytes keeping the suffix.
    """
    name = unicodedata.normalize("NFC", str(filename or ""))
    name = name.replace("\\", "/").rsplit("/", 1)[-1]
    name = "".join(c for c in name if unicodedata.category(c)[0] != "C").strip().lstrip(".").strip()
    if not name:
        raise MediaError("invalid_file_name", name=filename)
    if len(name.encode()) > MAX_NAME:
        stem, suffix = os.path.splitext(name)
        if len(suffix.encode()) > 16:  # not a real suffix
            stem, suffix = name, ""
        while stem and len((stem + suffix).encode()) > MAX_NAME:
            stem = stem[:-1]
        name = stem.rstrip() + suffix
    return name


def check_type(name: str, content_type: str | None) -> None:
    """Only pictures, videos and audio, by the type the browser declared."""
    if not (content_type or "").lower().startswith(MEDIA_TYPES):
        raise MediaError("upload_type", name=name)


def target_folder(root: Path, folder: str) -> Path:
    """The folder to upload into ("" is the media folder); it must exist."""
    real = resolve(root, folder or ".", allow_root=True)
    if not real.is_dir():
        raise MediaError("not_a_folder", path=folder)
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
    raise MediaError("no_free_name", name=name)


def finish(folder: Path, tmp: Path, name: str) -> Path:
    """Move the complete upload to a free name in the folder; returns where it went."""
    target = free_name(folder, name)
    try:
        os.chmod(tmp, 0o644)
        os.replace(tmp, target)  # replaces only the empty placeholder claimed just now
    except BaseException:
        target.unlink(missing_ok=True)
        raise
    return target
