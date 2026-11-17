"""Errors of the file and picture modules, each with a key into the integration's translations.

MESSAGES holds the English text; translations/en.json repeats it under "exceptions", so Home
Assistant shows the error in the user's language. This module does not import Home Assistant.
"""

from __future__ import annotations

from typing import Final

MESSAGES: Final = {
    "invalid_path": "Invalid path.",
    "top_level": "Choose a media folder first.",
    "unknown_folder": '"{path}": "{folder}" is not a media folder Shoebox uses.',
    "parent_not_allowed": '"{path}": ".." is not allowed.',
    "outside_media": '"{path}" is outside the media folder.',
    "symbolic_link": '"{path}" is a symbolic link.',
    "media_folder_itself": '"{path}" is the media folder itself.',
    "invalid_name": '"{name}" is not a valid name.',
    "empty_pattern": "The pattern is empty.",
    "invalid_pattern": 'Invalid pattern "{pattern}": {error}.',
    "invalid_type": "The type must be one of {types}.",
    "exists_not_folder": '"{path}" exists and is not a folder.',
    "not_found": '"{path}" does not exist.',
    "not_a_folder": '"{path}" is not a folder.',
    "not_a_file": '"{path}" is not a file.',
    "move_into_itself": 'Cannot move "{path}" into itself.',
    "already_exists": '"{path}" already exists.',
    "invalid_file_name": '"{name}" is not a valid file name.',
    "upload_type": '"{name}": only pictures, videos and audio can be uploaded.',
    "no_free_name": 'No free name for "{name}".',
    "rotate_by_90": "Rotate by a multiple of 90 degrees.",
    "not_jpeg": "Not a JPEG file.",
    "jpeg_only": "{name}: edits are only possible in JPEG files.",
    "damaged_jpeg": "Damaged JPEG file.",
    "metadata_too_large": "The metadata segment is too large.",
    "damaged_exif": "{name}: damaged EXIF data, not changed.",
    "orientation_range": "The orientation must be 1..8.",
    "crop_range": "The crop needs 0 <= left < right <= 1 and 0 <= top < bottom <= 1.",
    "xmp_unsupported": "{name}: the XMP data has no rdf:Description, not changed.",
    "unreadable": "{name}: cannot read the image ({error}).",
    "invalid_fit": "The fit must be cover or contain.",
}


class ShoeboxError(Exception):
    """A refused or failed operation; the message is meant for the user."""

    def __init__(self, key: str, **placeholders: object) -> None:
        self.key = key
        self.placeholders = {name: str(value) for name, value in placeholders.items()}
        super().__init__(MESSAGES[key].format(**self.placeholders))


class MediaError(ShoeboxError):
    """A refused or failed file operation."""


class ImageError(ShoeboxError):
    """A refused or failed picture operation."""
