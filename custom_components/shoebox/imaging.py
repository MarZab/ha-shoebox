"""Edits stored as standard metadata in the file, and pictures prepared at a requested size.

Edits work on JPEG only. Rotation is the EXIF Orientation tag (IFD0, 0x0112); the crop is the
Adobe XMP crop (crs:HasCrop and crs:CropLeft/Top/Right/Bottom, fractions of the stored image before
orientation, as Lightroom and Camera Raw write them). Only the metadata segments before the image
data are rewritten; the compressed image data is copied byte for byte. Other formats are only read.

Preparing applies the crop, then the orientation, then cover or contain to the requested size,
and writes a baseline JPEG. This module does not import Home Assistant.
"""

from __future__ import annotations

import io
import math
import os
from pathlib import Path
import re
import struct
import tempfile
from typing import Final, Literal, TypedDict

from PIL import Image, ImageOps
import pillow_heif

pillow_heif.register_heif_opener()

ORIENTATION_TAG: Final = 0x0112
EXIF_HEADER: Final = b"Exif\x00\x00"
XMP_HEADER: Final = b"http://ns.adobe.com/xap/1.0/\x00"
CRS_NS: Final = "http://ns.adobe.com/camera-raw-settings/1.0/"
CROP_FIELDS: Final = ("CropLeft", "CropTop", "CropRight", "CropBottom")
JPEG_QUALITY: Final = 85

type Box = tuple[float, float, float, float]
type Fit = Literal["cover", "contain"]
FITS: Final = ("cover", "contain")

# Pillow transpose per EXIF orientation (stored -> shown)
_TRANSPOSE: Final = {
    2: Image.Transpose.FLIP_LEFT_RIGHT,
    3: Image.Transpose.ROTATE_180,
    4: Image.Transpose.FLIP_TOP_BOTTOM,
    5: Image.Transpose.TRANSPOSE,
    6: Image.Transpose.ROTATE_270,
    7: Image.Transpose.TRANSVERSE,
    8: Image.Transpose.ROTATE_90,
}
_INVERSE: Final = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 8, 7: 7, 8: 6}
_NO_LENGTH: Final = frozenset({0x01, *range(0xD0, 0xD8)})  # TEM and RSTn carry no length


class ImageError(Exception):
    """A refused or failed image operation; the message is meant for the user."""


class ImageInfo(TypedDict):
    width: int
    height: int
    format: str | None
    orientation: int
    crop: list[float] | None
    editable: bool


# ---------------------------------------------------------------- orientation arithmetic


def shown_point(orientation: int, x: float, y: float) -> tuple[float, float]:
    """Where a point of the stored image (fractions) appears in the shown, oriented image."""
    return {
        1: (x, y),
        2: (1 - x, y),
        3: (1 - x, 1 - y),
        4: (x, 1 - y),
        5: (y, x),
        6: (1 - y, x),
        7: (1 - y, 1 - x),
        8: (y, 1 - x),
    }[orientation]


def stored_point(orientation: int, x: float, y: float) -> tuple[float, float]:
    return shown_point(_INVERSE[orientation], x, y)


def transpose(im: Image.Image, orientation: int) -> Image.Image:
    method = _TRANSPOSE.get(orientation)
    return im.transpose(method) if method is not None else im


def rotated(orientation: int, degrees: int) -> int:
    """The orientation that shows the picture turned `degrees` clockwise past `orientation`."""
    if degrees % 90:
        raise ImageError("rotate by a multiple of 90 degrees")
    probe = Image.new("L", (2, 3))
    probe.putdata([0, 1, 2, 3, 4, 5])
    want = transpose(probe, orientation).rotate(-(degrees % 360), expand=True)
    for candidate in range(1, 9):
        im = transpose(probe, candidate)
        if im.size == want.size and im.tobytes() == want.tobytes():
            return candidate
    raise AssertionError("every turn of a valid orientation is an orientation")  # pragma: no cover


def _valid_orientation(value: object) -> int:
    return value if isinstance(value, int) and 1 <= value <= 8 else 1


# ---------------------------------------------------------------- JPEG segments


def _jpeg_segments(data: bytes) -> tuple[list[tuple[int, bytes]], int]:
    """The segments before the image data, as (marker, payload), and where the rest starts."""
    if data[:2] != b"\xff\xd8":
        raise ImageError("not a JPEG file")
    segs: list[tuple[int, bytes]] = []
    i = 2
    while i < len(data):
        if data[i] != 0xFF:
            raise ImageError("damaged JPEG file")
        while i < len(data) and data[i] == 0xFF:  # fill bytes
            i += 1
        if i >= len(data):
            break
        marker = data[i]
        i += 1
        if marker in (0xDA, 0xD9):  # start of scan or end of image: the rest stays as it is
            return segs, i - 2
        if marker in _NO_LENGTH:
            segs.append((marker, b""))
            continue
        if i + 2 > len(data):
            break
        (length,) = struct.unpack(">H", data[i : i + 2])
        segs.append((marker, data[i + 2 : i + length]))
        i += length
    raise ImageError("damaged JPEG file")


def _jpeg_join(segs: list[tuple[int, bytes]], rest: bytes) -> bytes:
    out = bytearray(b"\xff\xd8")
    for marker, payload in segs:
        out += bytes((0xFF, marker))
        if marker not in _NO_LENGTH:
            if len(payload) + 2 > 0xFFFF:
                raise ImageError("metadata segment too large")
            out += struct.pack(">H", len(payload) + 2) + payload
    return bytes(out) + rest


def _is_exif(seg: tuple[int, bytes]) -> bool:
    return seg[0] == 0xE1 and seg[1].startswith(EXIF_HEADER)


def _is_xmp(seg: tuple[int, bytes]) -> bool:
    return seg[0] == 0xE1 and seg[1].startswith(XMP_HEADER)


def _insert_at(segs: list[tuple[int, bytes]]) -> int:
    """Where a new APP1 goes: after JFIF (APP0) and an existing Exif APP1."""
    i = 0
    while i < len(segs) and (segs[i][0] == 0xE0 or _is_exif(segs[i])):
        i += 1
    return i


def _write_atomic(path: Path, data: bytes) -> None:
    """Replace the file in one step, keeping its permissions; a crash leaves the old file."""
    mode = os.stat(path).st_mode & 0o7777
    fd, tmp = tempfile.mkstemp(prefix=".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(tmp, mode)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def _require_jpeg(path: Path) -> bytes:
    data = path.read_bytes()
    if data[:2] != b"\xff\xd8":
        raise ImageError(f"{path.name}: edits are only possible in JPEG files")
    return data


# ---------------------------------------------------------------- EXIF orientation


def _tiff_with_orientation(tiff: bytes, value: int) -> bytes:
    if tiff[:2] not in (b"II", b"MM"):
        raise ImageError("damaged EXIF data")
    bo = "<" if tiff[:2] == b"II" else ">"
    (ifd0,) = struct.unpack(bo + "I", tiff[4:8])
    (n,) = struct.unpack(bo + "H", tiff[ifd0 : ifd0 + 2])
    entries = [tiff[ifd0 + 2 + 12 * k : ifd0 + 14 + 12 * k] for k in range(n)]
    next_ifd = tiff[ifd0 + 2 + 12 * n : ifd0 + 6 + 12 * n]
    for k, e in enumerate(entries):
        tag, typ, count = struct.unpack(bo + "HHI", e[:8])
        if tag == ORIENTATION_TAG and typ == 3 and count == 1:  # SHORT in place: nothing moves
            at = ifd0 + 2 + 12 * k + 8
            return tiff[:at] + struct.pack(bo + "H", value) + tiff[at + 2 :]
    # Missing or unusual: append a copy of IFD0 with the tag; every offset in the block stays valid
    entries = [e for e in entries if struct.unpack(bo + "H", e[:2])[0] != ORIENTATION_TAG]
    entries.append(struct.pack(bo + "HHIH", ORIENTATION_TAG, 3, 1, value) + b"\x00\x00")
    entries.sort(key=lambda e: struct.unpack(bo + "H", e[:2])[0])
    body = tiff + (b"\x00" if len(tiff) % 2 else b"")
    new_ifd = (
        struct.pack(bo + "H", len(entries)) + b"".join(entries) + (next_ifd or b"\x00\x00\x00\x00")
    )
    return body[:4] + struct.pack(bo + "I", len(body)) + body[8:] + new_ifd


def get_orientation(path: Path) -> int:
    with Image.open(path) as im:
        return _valid_orientation(im.getexif().get(ORIENTATION_TAG, 1))


def set_orientation(path: Path, value: int) -> None:
    if not 1 <= value <= 8:
        raise ImageError("orientation must be 1..8")
    data = _require_jpeg(path)
    segs, start = _jpeg_segments(data)
    for k, seg in enumerate(segs):
        if _is_exif(seg):
            try:
                tiff = _tiff_with_orientation(seg[1][len(EXIF_HEADER) :], value)
            except (struct.error, IndexError) as err:
                raise ImageError(f"{path.name}: damaged EXIF data, not changed") from err
            segs[k] = (seg[0], EXIF_HEADER + tiff)
            break
    else:
        tiff = b"MM\x00\x2a\x00\x00\x00\x08" + struct.pack(
            ">HHHIH", 1, ORIENTATION_TAG, 3, 1, value
        )
        tiff += b"\x00\x00" + b"\x00\x00\x00\x00"
        segs.insert(_insert_at(segs), (0xE1, EXIF_HEADER + tiff))
    _write_atomic(path, _jpeg_join(segs, data[start:]))


def rotate(path: Path, degrees: int) -> int:
    """Turn the picture as shown by `degrees` clockwise; returns the new orientation."""
    value = rotated(get_orientation(path), degrees)
    set_orientation(path, value)
    return value


# ---------------------------------------------------------------- XMP crop


def _xmp_prefix(xmp: str) -> str | None:
    m = re.search(r'xmlns:([\w.-]+)\s*=\s*["\']' + re.escape(CRS_NS) + "[\"']", xmp)
    return m.group(1) if m else None


def parse_crop(xmp: str | bytes | None) -> Box | None:
    """(left, top, right, bottom) in fractions of the stored image, or None without a crop."""
    if not xmp:
        return None
    if isinstance(xmp, bytes):
        xmp = xmp.decode("utf-8", "replace")
    p = _xmp_prefix(xmp)
    if not p:
        return None
    text = xmp

    def field(name: str) -> str | None:
        m = re.search(rf'{p}:{name}\s*=\s*["\']([^"\']*)["\']', text) or re.search(
            rf"<{p}:{name}>\s*([^<]*?)\s*</{p}:{name}>", text
        )
        return m.group(1) if m else None

    if (field("HasCrop") or "").lower() != "true":
        return None
    try:
        left, top, right, bottom = (float(field(n) or "nan") for n in CROP_FIELDS)
    except ValueError:
        return None
    box = (max(0.0, left), max(0.0, top), min(1.0, right), min(1.0, bottom))
    if any(math.isnan(v) for v in box) or box[2] <= box[0] or box[3] <= box[1]:
        return None
    return box


def _xmp_without_crop(xmp: str, p: str) -> str:
    for name in ("HasCrop", *CROP_FIELDS):
        xmp = re.sub(rf'\s+{p}:{name}\s*=\s*(["\'])[^"\']*\1', "", xmp)
        xmp = re.sub(rf"\s*<{p}:{name}>[^<]*</{p}:{name}>", "", xmp)
    return xmp


def _xmp_packet(attrs: str) -> str:
    return (
        '<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>\n'
        '<x:xmpmeta xmlns:x="adobe:ns:meta/">\n'
        ' <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">\n'
        f'  <rdf:Description rdf:about="" xmlns:crs="{CRS_NS}"{attrs}/>\n'
        " </rdf:RDF>\n"
        "</x:xmpmeta>\n"
        '<?xpacket end="w"?>'
    )


def read_xmp(path: Path) -> str | None:
    data = path.read_bytes()
    if data[:2] != b"\xff\xd8":
        with Image.open(path) as im:
            raw = im.info.get("xmp")
        if isinstance(raw, bytes):
            return raw.decode("utf-8", "replace")
        return raw if isinstance(raw, str) else None
    segs, _ = _jpeg_segments(data)
    for seg in segs:
        if _is_xmp(seg):
            return seg[1][len(XMP_HEADER) :].decode("utf-8", "replace")
    return None


def get_crop(path: Path) -> Box | None:
    return parse_crop(read_xmp(path))


def _check_box(box: Box) -> None:
    left, top, right, bottom = box
    if not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
        raise ImageError("crop needs 0 <= left < right <= 1 and 0 <= top < bottom <= 1")


def set_crop(path: Path, box: Box | None) -> None:
    """Write the crop in fractions of the stored image as XMP; None removes it."""
    if box is not None:
        _check_box(box)
    data = _require_jpeg(path)
    segs, start = _jpeg_segments(data)
    k = next((k for k, seg in enumerate(segs) if _is_xmp(seg)), None)
    xmp = segs[k][1][len(XMP_HEADER) :].decode("utf-8") if k is not None else None
    attrs = ""
    if box is not None:
        values = dict(zip(CROP_FIELDS, box, strict=True))
        attrs = ' {p}:HasCrop="True"' + "".join(
            f' {{p}}:{n}="{values[n]:.6f}"' for n in CROP_FIELDS
        )
    if xmp is None:
        if box is None:
            return
        xmp = _xmp_packet(attrs.format(p="crs"))
    else:
        p = _xmp_prefix(xmp)
        if p:
            xmp = _xmp_without_crop(xmp, p)
        if box is not None:
            m = re.search(r"<rdf:Description\b", xmp)
            if not m:
                raise ImageError("XMP without rdf:Description: not changed")
            if not p:
                p = "crs"
                attrs = f' xmlns:crs="{CRS_NS}"' + attrs
            xmp = xmp[: m.end()] + attrs.format(p=p) + xmp[m.end() :]
    segment = (0xE1, XMP_HEADER + xmp.encode("utf-8"))
    if k is None:
        segs.insert(_insert_at(segs), segment)
    else:
        segs[k] = segment
    _write_atomic(path, _jpeg_join(segs, data[start:]))


def _bounds(a: tuple[float, float], b: tuple[float, float]) -> Box:
    return (min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1]))


def crop_shown(path: Path, box: Box | None) -> Box | None:
    """Crop to a box in fractions of the picture as shown (after orientation).

    It is stored as Adobe does, relative to the stored image, so a later rotation keeps the same
    part of the picture. None removes the crop.
    """
    if box is None:
        set_crop(path, None)
        return None
    o = get_orientation(path)
    stored = _bounds(stored_point(o, box[0], box[1]), stored_point(o, box[2], box[3]))
    set_crop(path, stored)
    return stored


def crop_as_shown(path: Path) -> Box | None:
    """The crop in fractions of the picture as shown; the inverse of crop_shown()."""
    try:
        box = get_crop(path)
    except ImageError, OSError, struct.error:
        return None
    if box is None:
        return None
    o = get_orientation(path)
    return _bounds(shown_point(o, box[0], box[1]), shown_point(o, box[2], box[3]))


def info(path: Path) -> ImageInfo:
    """What an editor needs: size and crop as shown, orientation, whether edits are possible."""
    try:
        with Image.open(path) as im:
            w, h = im.size
            fmt = im.format
            o = _valid_orientation(im.getexif().get(ORIENTATION_TAG, 1))
    except Exception as err:  # Pillow raises several kinds for unreadable files
        raise ImageError(f"{path.name}: cannot read the image ({err})") from err
    if o >= 5:
        w, h = h, w
    crop = crop_as_shown(path)
    return {
        "width": w,
        "height": h,
        "format": fmt,
        "orientation": o,
        "crop": list(crop) if crop else None,
        "editable": fmt == "JPEG",
    }


def edit(
    path: Path, rotate_by: int, box: Box | None, *, orientation: int | None = None
) -> ImageInfo:
    """One editor save: turn by `rotate_by` degrees clockwise (or set `orientation`), then set the
    crop in fractions of the picture as shown after that turn, or remove it (None)."""
    _require_jpeg(path)
    if box is not None:
        _check_box(box)
    if orientation is not None:
        if orientation != get_orientation(path):
            set_orientation(path, orientation)
    elif rotate_by % 360:
        rotate(path, rotate_by)
    crop_shown(path, box)
    return info(path)


# ---------------------------------------------------------------- preparing


def render(path: Path, width: int, height: int, fit: Fit = "cover", use_crop: bool = True) -> bytes:
    """The picture as a baseline JPEG: crop, orientation, then cover or contain.

    cover is exactly width x height, scaled to cover with the overhang cut evenly; contain is scaled
    to fit inside, aspect kept. use_crop=False ignores the crop, e.g. to draw a new crop on.
    """
    if fit not in FITS:
        raise ImageError("fit must be cover or contain")
    crop: Box | None = None
    if use_crop:
        try:
            crop = get_crop(path)
        except ImageError, OSError, struct.error:
            crop = None
    try:
        im = Image.open(path)
    except Exception as err:  # Pillow raises several kinds for unreadable files
        raise ImageError(f"{path.name}: cannot read the image ({err})") from err
    with im:
        orientation = _valid_orientation(im.getexif().get(ORIENTATION_TAG, 1))
        sw, sh = im.size
        left, top, right, bottom = crop or (0.0, 0.0, 1.0, 1.0)
        cw, ch = (right - left) * sw, (bottom - top) * sh
        dw, dh = (ch, cw) if orientation >= 5 else (cw, ch)
        scale = (max if fit == "cover" else min)(width / dw, height / dh)
        if im.format == "JPEG" and scale < 1:  # decode at a reduced size where that is enough
            im.draft("RGB", (math.ceil(sw * scale), math.ceil(sh * scale)))
        out_im = im if im.mode in ("RGB", "L") else im.convert("RGB")
        if crop:
            w, h = out_im.size
            box = (round(left * w), round(top * h), round(right * w), round(bottom * h))
            out_im = out_im.crop(box)
        out_im = transpose(out_im, orientation)
        if fit == "cover":
            out_im = ImageOps.fit(out_im, (width, height), method=Image.Resampling.LANCZOS)
        else:
            out_im = ImageOps.contain(out_im, (width, height), method=Image.Resampling.LANCZOS)
        if out_im.mode != "RGB":
            out_im = out_im.convert("RGB")
        out = io.BytesIO()
        # baseline, not progressive: small displays such as ESPHome decode only baseline JPEG
        out_im.save(out, "JPEG", quality=JPEG_QUALITY, progressive=False)
        return out.getvalue()
