"""Files below the media folder.

Path confinement, listing, patterns, rotation order and file operations. Every function takes
the media root and works only below it; anything else raises MediaError. This module does not
import Home Assistant.
"""

from __future__ import annotations

import bisect
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
import errno
import logging
import os
from pathlib import Path
import random
import re
import shutil
from typing import Final, Literal

from .errors import MediaError

IMAGE_SUFFIXES: Final = frozenset(
    {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif", ".avif", ".gif", ".bmp", ".tif", ".tiff"}
)
type EntryType = Literal["image", "file", "folder"]
TYPES: Final = ("all", "image", "file", "folder")


def is_image(name: str) -> bool:
    return Path(name).suffix.lower() in IMAGE_SUFFIXES


# ---------------------------------------------------------------- paths


def _inside(root_real: str, real: str) -> bool:
    return real == root_real or real.startswith(root_real.rstrip(os.sep) + os.sep)


def resolve(root: Path, path: str, *, allow_root: bool = False) -> Path:
    """The real path for `path`, relative to the root or absolute below it.

    ".." is refused outright, and so is a path that is itself a symbolic link: deleting or moving it
    would act on its target. Links in the folders on the way are followed, and the result must still
    be below the root. The path need not exist.
    """
    if not isinstance(path, str) or "\0" in path:
        raise MediaError("invalid_path")
    p = Path(path.strip())
    if ".." in p.parts:
        raise MediaError("parent_not_allowed", path=path)
    root_real = os.path.realpath(root)
    candidate = p if p.is_absolute() else Path(root_real, p)
    if p.is_absolute() and not (_inside(str(root), str(p)) or _inside(root_real, str(p))):
        raise MediaError("outside_media", path=path)
    if os.path.islink(candidate):
        raise MediaError("symbolic_link", path=path)
    real = os.path.realpath(candidate)
    if not _inside(root_real, real):
        raise MediaError("outside_media", path=path)
    if real == root_real and not allow_root:
        raise MediaError("media_folder_itself", path=path)
    return Path(real)


def relative(root: Path, real: Path) -> str:
    """The path below the root as actions show it: "folder/photo.jpg"."""
    return Path(real).relative_to(os.path.realpath(root)).as_posix()


def _check_name(name: str) -> str:
    if not name or name in (".", "..") or "/" in name or "\0" in name or name != name.strip():
        raise MediaError("invalid_name", name=name)
    return name


# ---------------------------------------------------------------- listing and patterns


@dataclass(frozen=True)
class Entry:
    path: str  # below the root, "/"-separated
    type: EntryType
    size: int
    modified: float

    @property
    def name(self) -> str:
        return self.path.rsplit("/", 1)[-1]

    def as_dict(self) -> dict[str, str | int | float]:
        return {"path": self.path, "type": self.type, "size": self.size, "modified": self.modified}


_LOGGER = logging.getLogger(__name__)
_reported: set[str] = set()


def _shown_name(dirpath: str, name: str) -> bool:
    """Whether a name is listed: not hidden, and valid UTF-8 (JSON and URLs need that)."""
    if name.startswith("."):
        return False
    try:
        name.encode("utf-8")
    except UnicodeEncodeError:
        full = os.path.join(dirpath, name)
        if full not in _reported:
            _reported.add(full)
            _LOGGER.warning("Skipping %r: the name is not valid UTF-8; rename it", full)
        return False
    return True


def _entry(rel: str, full: str, is_dir: bool) -> Entry | None:
    try:
        st = os.stat(full)
    except OSError:
        return None
    if is_dir:
        return Entry(rel, "folder", 0, st.st_mtime)
    return Entry(rel, "image" if is_image(rel) else "file", st.st_size, st.st_mtime)


def walk(root: Path) -> list[Entry]:
    """Everything below the root, sorted by path. Hidden names and symbolic links are skipped."""
    root_real = os.path.realpath(root)
    out: list[Entry] = []
    for dirpath, dirnames, filenames in os.walk(root_real, followlinks=False):
        dirnames[:] = sorted(
            d
            for d in dirnames
            if _shown_name(dirpath, d) and not os.path.islink(os.path.join(dirpath, d))
        )
        rel_dir = os.path.relpath(dirpath, root_real).replace(os.sep, "/")
        for name, is_dir in [(d, True) for d in dirnames] + [(f, False) for f in filenames]:
            full = os.path.join(dirpath, name)
            if not _shown_name(dirpath, name) or (not is_dir and os.path.islink(full)):
                continue
            rel = name if rel_dir == "." else f"{rel_dir}/{name}"
            if entry := _entry(rel, full, is_dir):
                out.append(entry)
    out.sort(key=lambda e: e.path)
    return out


# Each "**" multiplies the work of matching a path that almost matches: 4 take a millisecond on a
# long path, 5 take seconds, and every walk matches every path.
MAX_GLOBSTARS = 3


def _glob_to_regex(pattern: str) -> str:
    out: list[str] = []
    i, n = 0, len(pattern)
    while i < n:
        c = pattern[i]
        if c == "*":
            if pattern.startswith("**", i):
                i += 2
                if i < n and pattern[i] == "/":  # "**/": any number of folders, also none
                    out.append("(?:.*/)?")
                    i += 1
                else:
                    out.append(".*")
                continue
            out.append("[^/]*")
        elif c == "?":
            out.append("[^/]")
        elif c == "[":
            j = pattern.find("]", i + 2 if pattern.startswith(("[!", "[^"), i) else i + 1)
            if j < 0:
                out.append(re.escape(c))
            else:
                body = pattern[i + 1 : j]
                if body.startswith("!"):
                    body = "^" + body[1:]
                out.append("[" + body.replace("\\", "\\\\") + "]")
                i = j
        else:
            out.append(re.escape(c))
        i += 1
    return "".join(out)


def compile_pattern(pattern: str) -> re.Pattern[str]:
    """A pattern over paths below the root.

    A glob ("*" within a folder, "**" at any depth, "?", "[...]") matches the whole path;
    "re:<regular expression>" is searched in the path.
    """
    if not isinstance(pattern, str) or not pattern.strip():
        raise MediaError("empty_pattern")
    if not pattern.startswith("re:") and len(re.findall(r"\*\*+", pattern)) > MAX_GLOBSTARS:
        raise MediaError("too_many_globstars", pattern=pattern, limit=MAX_GLOBSTARS)
    try:
        if pattern.startswith("re:"):
            return re.compile(pattern[3:])
        return re.compile(r"\A(?:" + _glob_to_regex(pattern.strip().lstrip("/")) + r")\Z")
    except re.error as err:
        raise MediaError("invalid_pattern", pattern=pattern, error=err) from err


def _finder(pattern: str) -> Callable[[str], re.Match[str] | None]:
    rx = compile_pattern(pattern)
    return rx.search if pattern.startswith("re:") else rx.match


def matches(pattern: str, path: str) -> bool:
    return bool(_finder(pattern)(path))


def select(entries: Iterable[Entry], pattern: str, type_: str = "all") -> list[Entry]:
    if type_ not in TYPES:
        raise MediaError("invalid_type", types=", ".join(TYPES))
    rx = compile_pattern(pattern)
    find = rx.search if pattern.startswith("re:") else rx.match
    return [e for e in entries if (type_ in ("all", e.type)) and find(e.path)]


def select_pictures(entries: Sequence[Entry], patterns: Sequence[str]) -> list[str]:
    """The pictures any pattern selects, minus those a pattern starting with "!" selects.

    Sorted by path, without duplicates. Only "!" patterns select nothing.
    """
    include = [_finder(p) for p in patterns if not p.startswith("!")]
    exclude = [_finder(p[1:]) for p in patterns if p.startswith("!")]
    return [
        e.path
        for e in entries
        if e.type == "image"
        and any(find(e.path) for find in include)
        and not any(find(e.path) for find in exclude)
    ]


def check_pattern(pattern: str) -> None:
    """Refuse a pattern that is not valid, also after a leading "!"."""
    compile_pattern(pattern.removeprefix("!"))


def advance(files: Sequence[str], current: str | None) -> int:
    """The index of the picture after `current` in the sorted list, wrapping around.

    When `current` is gone, the rotation continues with the picture sorted after it, so adding or
    removing files does not restart it. -1 for an empty list.
    """
    if not files:
        return -1
    if current is None:
        return 0
    if current in files:
        return (files.index(current) + 1) % len(files)
    return bisect.bisect_right(list(files), current) % len(files)


def shuffle_next(
    files: Sequence[str],
    shown: Sequence[str],
    current: str | None,
    choose: Callable[[Sequence[str]], str] = random.choice,
) -> tuple[str | None, list[str]]:
    """The next picture of a shuffled rotation, and the pictures shown in this round with it.

    Every picture once per round, in random order; a new round never starts with `current`.
    Pictures that are gone drop out of the round, new ones join it.
    """
    if not files:
        return None, []
    present = set(files)
    seen = [f for f in shown if f in present]
    seen_set = set(seen)
    left = [f for f in files if f not in seen_set]
    if not left:
        seen = []
        left = [f for f in files if f != current] or list(files)
    pick = choose(left)
    return pick, [*seen, pick]


# ---------------------------------------------------------------- file operations


def resolve_file(root: Path, path: str) -> Path:
    """The real path of an existing file below the root."""
    real = resolve(root, path)
    if not real.is_file():
        raise MediaError("not_a_file", path=path)
    return real


def create_folder(root: Path, path: str) -> str:
    target = resolve(root, path)
    if target.exists() and not target.is_dir():
        raise MediaError("exists_not_folder", path=path)
    target.mkdir(parents=True, exist_ok=True)
    return relative(root, target)


def move(root: Path, path: str, to: str) -> str:
    """Move a file or folder into the folder `to` ("" or "/" is the media folder itself)."""
    src = resolve(root, path)
    dest_dir = resolve(root, to or ".", allow_root=True)
    return relative(root, move_resolved(src, dest_dir, path, to, lambda p: relative(root, p)))


def move_resolved(
    src: Path, dest_dir: Path, path: str, to: str, show: Callable[[Path], str]
) -> Path:
    """Move `src` into `dest_dir`, both already resolved; `show` names a path in errors."""
    if not src.exists():
        raise MediaError("not_found", path=path)
    if not dest_dir.is_dir():
        raise MediaError("not_a_folder", path=to)
    if src.is_dir() and (dest_dir == src or src in dest_dir.parents):
        raise MediaError("move_into_itself", path=path)
    target = dest_dir / src.name
    _move_to_free(src, target, show)
    return target


def _move_to_free(src: Path, target: Path, show: Callable[[Path], str]) -> None:
    """Move src to target only if nothing is there, also when something arrives meanwhile.

    The name is claimed first with an empty file or folder (creating one fails if the name is
    taken), then the move replaces that placeholder and nothing else.
    """
    is_dir = src.is_dir()
    try:
        if is_dir:
            os.mkdir(target)
        else:
            os.close(os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600))
    except FileExistsError as err:
        raise MediaError("already_exists", path=show(target)) from err
    try:
        os.rename(src, target)
    except OSError as err:
        if err.errno != errno.EXDEV:  # not another file system: give the name back
            (os.rmdir if is_dir else os.unlink)(target)
            raise
        if is_dir:  # another file system: copy into the placeholder, then remove the original
            shutil.copytree(src, target, symlinks=True, dirs_exist_ok=True)
            shutil.rmtree(src)
        else:
            shutil.copy2(src, target)
            src.unlink()


def rename(root: Path, path: str, name: str) -> str:
    src = resolve(root, path)
    if not src.exists():
        raise MediaError("not_found", path=path)
    target = src.parent / _check_name(name)
    resolve(root, str(target))
    _move_to_free(src, target, lambda p: relative(root, p))
    return relative(root, target)


def delete(root: Path, path: str) -> str:
    """Delete a file, or a folder with everything in it."""
    target = resolve(root, path)
    if not target.exists():
        raise MediaError("not_found", path=path)
    rel = relative(root, target)
    if target.is_dir():
        shutil.rmtree(target)
    else:
        target.unlink()
    return rel


def list_folder(root: Path, path: str = "") -> tuple[str, list[Entry]]:
    """One folder ("" is the media folder): its folders, then its files, each sorted by name.

    Hidden names and symbolic links are skipped, as in walk().
    """
    folder = resolve(root, path or ".", allow_root=True)
    if not folder.is_dir():
        raise MediaError("not_a_folder", path=path)
    rel_dir = "" if folder == Path(os.path.realpath(root)) else relative(root, folder)
    found: list[Entry] = []
    with os.scandir(folder) as it:
        for d in it:
            if not _shown_name(str(folder), d.name) or d.is_symlink():
                continue
            rel = f"{rel_dir}/{d.name}" if rel_dir else d.name
            if entry := _entry(rel, d.path, d.is_dir()):
                found.append(entry)
    found.sort(key=lambda e: (e.type != "folder", e.name.casefold()))
    return rel_dir, found
