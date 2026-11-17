"""The media folders Shoebox works on, and paths that start with a folder's name.

A path is "<folder>/<path below it>", such as "local/Family/beach.jpg": the folder names are
Home Assistant's media folder names (media_dirs; "local" is My media). An empty path is the top
level, where the folders themselves are listed. Everything below a folder is done by media.py;
this module adds and removes the prefix, also in error messages. It does not import Home
Assistant.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping, Sequence
from contextlib import contextmanager
import os
from pathlib import Path

from . import media, upload
from .errors import MediaError
from .media import Entry


class Library:
    def __init__(self, folders: Mapping[str, Path]) -> None:
        self.folders = {name: Path(path) for name, path in folders.items()}

    # ---------------------------------------------------------------- paths

    def locate(self, path: str) -> tuple[str, Path, str]:
        """(folder name, folder, path below it) for a prefixed or absolute path."""
        if not isinstance(path, str) or "\0" in path:
            raise MediaError("invalid_path")
        text = path.strip()
        if text.startswith("/"):
            for name, folder in self.folders.items():
                for base in {str(folder), os.path.realpath(folder)}:
                    if text == base or text.startswith(base.rstrip("/") + "/"):
                        return name, folder, text[len(base) :].strip("/")
            raise MediaError("outside_media", path=path)
        name, _, rest = text.partition("/")
        if not name:
            raise MediaError("top_level")
        if name not in self.folders:
            raise MediaError("unknown_folder", path=path, folder=name)
        return name, self.folders[name], rest

    @property
    def titles(self) -> dict[str, str]:
        """How Home Assistant's media browser shows each folder: its directory's name."""
        return {name: folder.name or name for name, folder in self.folders.items()}

    @staticmethod
    def join(name: str, rest: str) -> str:
        return f"{name}/{rest}" if rest else name

    def relative(self, real: Path) -> str:
        """The prefixed path of a real path below one of the folders."""
        for name, folder in self.folders.items():
            root = os.path.realpath(folder)
            if str(real) == root or str(real).startswith(root.rstrip(os.sep) + os.sep):
                return self.join(name, media.relative(folder, real))
        raise MediaError("outside_media", path=str(real))

    @contextmanager
    def _in(self, name: str) -> Iterator[None]:
        """Errors from media.py name paths below the folder; give them the folder's prefix."""
        try:
            yield
        except MediaError as err:
            fixed = {
                k: self.join(name, v) if k == "path" and not v.startswith("/") else v
                for k, v in err.placeholders.items()
            }
            raise type(err)(err.key, **fixed) from err

    def resolve(self, path: str, *, allow_folder: bool = False) -> Path:
        name, folder, rest = self.locate(path)
        with self._in(name):
            return media.resolve(folder, rest or ".", allow_root=allow_folder)

    def resolve_file(self, path: str) -> Path:
        name, folder, rest = self.locate(path)
        with self._in(name):
            return media.resolve_file(folder, rest)

    # ---------------------------------------------------------------- listing

    def walk(self) -> list[Entry]:
        """Everything below every folder, prefixed and sorted by path."""
        out: list[Entry] = []
        for name, folder in self.folders.items():
            if folder.is_dir():
                out += [_prefixed(name, e) for e in media.walk(folder)]
        out.sort(key=lambda e: e.path)
        return out

    def pictures(self, patterns: Sequence[str]) -> list[str]:
        """The pictures these patterns select, sorted by path. Walks every folder: run it once."""
        return media.select_pictures(self.walk(), patterns)

    def selects(self, path: str, patterns: Sequence[str]) -> bool:
        """Whether pictures(patterns) would include this path, without walking the folders."""
        try:
            real = self.resolve_file(path)
        except MediaError:
            return False
        # as walk: no hidden names, no links on the way (the real path is the one given)
        if self.relative(real) != path or any(p.startswith(".") for p in path.split("/")):
            return False
        entry = Entry(path, "image" if media.is_image(path) else "file", 0, 0)
        return bool(media.select_pictures([entry], patterns))

    def list_folder(self, path: str = "") -> tuple[str, list[Entry]]:
        """One folder's folders and files; "" lists the media folders themselves."""
        if not path.strip().strip("/"):
            tops = [
                Entry(name, "folder", 0, folder.stat().st_mtime)
                for name, folder in sorted(self.folders.items())
                if folder.is_dir()
            ]
            return "", tops
        name, folder, rest = self.locate(path)
        with self._in(name):
            rel, entries = media.list_folder(folder, rest)
        return self.join(name, rel), [_prefixed(name, e) for e in entries]

    # ---------------------------------------------------------------- file operations

    def _call(self, path: str, func: Callable[[Path, str], str]) -> str:
        name, folder, rest = self.locate(path)
        if not rest:
            raise MediaError("media_folder_itself", path=path)
        with self._in(name):
            return self.join(name, func(folder, rest))

    def create_folder(self, path: str) -> str:
        return self._call(path, media.create_folder)

    def rename(self, path: str, new_name: str) -> str:
        return self._call(path, lambda folder, rest: media.rename(folder, rest, new_name))

    def delete(self, path: str) -> str:
        return self._call(path, media.delete)

    def move(self, path: str, to: str) -> str:
        """Move a file or folder into the folder `to`, also into another media folder."""
        src = self.resolve(path)
        dest_dir = self.resolve(to, allow_folder=True)
        return self.relative(media.move_resolved(src, dest_dir, path, to, self.relative))

    # ---------------------------------------------------------------- uploads

    def upload_folder(self, path: str) -> Path:
        name, folder, rest = self.locate(path)
        with self._in(name):
            return upload.target_folder(folder, rest)

    def finish_upload(self, folder: Path, tmp: Path, file_name: str) -> str:
        return self.relative(upload.finish(folder, tmp, file_name))


def _prefixed(name: str, entry: Entry) -> Entry:
    return Entry(f"{name}/{entry.path}", entry.type, entry.size, entry.modified)
