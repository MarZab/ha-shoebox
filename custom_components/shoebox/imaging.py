"""Edits stored as standard metadata in the file, and pictures prepared at a requested size.

Edits work on JPEG only. Rotation is the EXIF Orientation tag (IFD0, 0x0112); the crop is the
Adobe XMP crop (crs:HasCrop and crs:CropLeft/Top/Right/Bottom, fractions of the stored image before
orientation, as Lightroom and Camera Raw write them). Only the metadata segments before the image
data are rewritten; the compressed image data is copied byte for byte. Other formats are only read.

Preparing applies the crop, then the orientation, then cover or contain to the requested size,
and writes a baseline JPEG. This module does not import Home Assistant.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
import io
import math
import os
from pathlib import Path
import re
import struct
import tempfile
from typing import Final, Literal, TypedDict

from PIL import Image, ImageEnhance, ImageOps
import pillow_heif

from .errors import ImageError

pillow_heif.register_heif_opener()

ORIENTATION_TAG: Final = 0x0112
EXIF_HEADER: Final = b"Exif\x00\x00"
XMP_HEADER: Final = b"http://ns.adobe.com/xap/1.0/\x00"
MPF_HEADER: Final = b"MPF\x00"
MPF_ENTRIES: Final = 0xB002
# MPO is JPEG with further images appended (iPhone gain maps, depth maps): edited as JPEG
JPEG_FORMATS: Final = ("JPEG", "MPO")
CRS_NS: Final = "http://ns.adobe.com/camera-raw-settings/1.0/"
CROP_FIELDS: Final = ("CropLeft", "CropTop", "CropRight", "CropBottom")
JPEG_QUALITY: Final = 85
# Decoding is refused above this many pixels (after JPEG's reduced decoding): a small file can
# claim a huge picture, and decoding one at full size takes gigabytes of memory.
MAX_PIXELS: Final = 50_000_000
# The metadata of a JPEG is read from the start of the file only, and XMP larger than this is
# ignored: neither ever needs more, and both bound the work a crafted file can cause.
HEAD_BYTES: Final = 1 << 20
MAX_XMP: Final = 256 * 1024

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


# ---------------------------------------------------------------- looks for displays

type Format = Literal["jpeg", "png", "bmp"]
type RGB = tuple[int, int, int]

# Named palettes for e-paper and similar displays. Real panels show duller colours than these;
# a list of measured hex colours in place of a name calibrates for one.
PALETTES: Final[dict[str, tuple[str, ...]]] = {
    "bw": ("000000", "ffffff"),
    "gray4": ("000000", "555555", "aaaaaa", "ffffff"),
    "gray16": tuple(f"{v:02x}" * 3 for v in range(0, 256, 17)),
    "spectra6": ("000000", "ffffff", "ff0000", "ffff00", "0000ff", "00ff00"),
    "acep7": ("000000", "ffffff", "ff0000", "ffff00", "0000ff", "00ff00", "ff8000"),
}
MIME: Final[dict[str, str]] = {"jpeg": "image/jpeg", "png": "image/png", "bmp": "image/bmp"}
MAX_ENHANCE: Final = 3.0


@dataclass(frozen=True)
class Look:
    """How a display wants the picture: colours, dithering, file format and adjustments."""

    colors: tuple[RGB, ...] | None = None
    dither: bool = True
    format: Format = "jpeg"
    contrast: float = 1.0
    saturation: float = 1.0
    brightness: float = 1.0

    @property
    def key(self) -> str:
        """Part of the cache key; empty for the plain look, so plain pictures keep their keys."""
        if self == Look():
            return ""
        colors = ".".join(f"{r:02x}{g:02x}{b:02x}" for r, g, b in self.colors or ())
        return (
            f"look:{colors}:{int(self.dither)}:{self.format}"
            f":{self.contrast:g}:{self.saturation:g}:{self.brightness:g}"
        )

    @property
    def mime(self) -> str:
        return MIME[self.format]


def _rgb(text: str) -> RGB:
    value = text.strip().lstrip("#").lower()
    if len(value) != 6 or any(c not in "0123456789abcdef" for c in value):
        raise ValueError(text)
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def parse_look(query: Mapping[str, str]) -> Look:
    """A look from URL parameters; ValueError when one is not valid.

    colors: a palette name or 2 to 256 hex colours separated by commas. dither: floyd or none.
    format: jpeg, png or bmp (png by default with colors). contrast, saturation, brightness:
    0 to 3, 1 leaves the picture as it is.
    """
    colors: tuple[RGB, ...] | None = None
    if spec := query.get("colors", "").strip():
        names = PALETTES.get(spec.lower()) or tuple(spec.split(","))
        colors = tuple(_rgb(c) for c in names)
        if not 2 <= len(colors) <= 256:
            raise ValueError(spec)
    dither = query.get("dither", "floyd")
    if dither not in ("floyd", "none"):
        raise ValueError(dither)
    fmt = query.get("format", "png" if colors else "jpeg")
    if fmt not in MIME:
        raise ValueError(fmt)
    enhance = []
    for name in ("contrast", "saturation", "brightness"):
        value = float(query.get(name, "1"))
        if not 0 <= value <= MAX_ENHANCE:  # also refuses nan
            raise ValueError(name)
        enhance.append(value)
    return Look(colors, dither == "floyd", fmt, *enhance)  # type: ignore[arg-type]  # checked above


def _apply_look(im: Image.Image, look: Look) -> bytes:
    """Adjust, reduce to the palette and encode the prepared picture."""
    if look.brightness != 1:
        im = ImageEnhance.Brightness(im).enhance(look.brightness)
    if look.contrast != 1:
        im = ImageEnhance.Contrast(im).enhance(look.contrast)
    if look.saturation != 1:
        im = ImageEnhance.Color(im).enhance(look.saturation)
    out = io.BytesIO()
    if look.colors:
        flat = [v for rgb in look.colors for v in rgb]
        palette = Image.new("P", (1, 1))
        palette.putpalette(flat + flat[:3] * (256 - len(look.colors)))  # padding is never chosen
        dither = Image.Dither.FLOYDSTEINBERG if look.dither else Image.Dither.NONE
        im = im.quantize(palette=palette, dither=dither)
        if look.format == "png":  # as few bits per pixel as the palette needs
            bits = next(b for b in (1, 2, 4, 8) if len(look.colors) <= 1 << b)
            im.save(out, "PNG", optimize=True, bits=bits)
            return out.getvalue()
        im = im.convert("RGB")
    if look.format == "png":
        im.save(out, "PNG", optimize=True)
    elif look.format == "bmp":
        im.save(out, "BMP")  # 24 bits: every BMP reader takes it
    else:
        # baseline, not progressive: small displays such as ESPHome decode only baseline JPEG
        im.save(out, "JPEG", quality=JPEG_QUALITY, progressive=False)
    return out.getvalue()


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
        raise ImageError("rotate_by_90")
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
        raise ImageError("not_jpeg")
    segs: list[tuple[int, bytes]] = []
    i = 2
    while i < len(data):
        if data[i] != 0xFF:
            raise ImageError("damaged_jpeg")
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
    raise ImageError("damaged_jpeg")


def _seg_bytes(seg: tuple[int, bytes]) -> int:
    return 2 if seg[0] in _NO_LENGTH else 4 + len(seg[1])


def _mpf_index(segs: list[tuple[int, bytes]]) -> int | None:
    return next(
        (i for i, s in enumerate(segs) if s[0] == 0xE2 and s[1].startswith(MPF_HEADER)), None
    )


def _mpf_moved(payload: bytes, delta: int) -> bytes:
    """The MPF segment with the offsets of the further images moved by `delta` bytes.

    MPO files (iPhone photos with an HDR gain map or depth map, stereo cameras) append further
    images after the first, at offsets counted from the MPF header. An edit that changes the
    length of segments after that header moves the further images: their offsets move with them.
    """
    tiff = len(MPF_HEADER)
    order = payload[tiff : tiff + 2]
    if order not in (b"II", b"MM"):
        raise ImageError("damaged_jpeg")
    bo = "<" if order == b"II" else ">"
    out = bytearray(payload)
    try:
        (ifd,) = struct.unpack_from(bo + "I", payload, tiff + 4)
        (count,) = struct.unpack_from(bo + "H", payload, tiff + ifd)
        for k in range(count):
            at = tiff + ifd + 2 + 12 * k
            tag, _type, size, value = struct.unpack_from(bo + "HHII", payload, at)
            if tag != MPF_ENTRIES:
                continue
            for e in range(size // 16):
                where = tiff + value + 16 * e + 8  # attribute, size, then the offset
                (offset,) = struct.unpack_from(bo + "I", payload, where)
                if offset:  # 0 is the first image, which starts the file
                    struct.pack_into(bo + "I", out, where, offset + delta)
    except struct.error as err:
        raise ImageError("damaged_jpeg") from err
    return bytes(out)


def _jpeg_join(
    segs: list[tuple[int, bytes]], rest: bytes, before: list[tuple[int, bytes]] | None = None
) -> bytes:
    """The file from its segments and the rest; `before` are the segments as they were, so
    MPF offsets follow a change in length after the MPF segment."""
    if before is not None and (i := _mpf_index(segs)) is not None:
        j = _mpf_index(before)
        assert j is not None  # edits never add or remove the MPF segment
        delta = sum(map(_seg_bytes, segs[i + 1 :])) - sum(map(_seg_bytes, before[j + 1 :]))
        if delta:
            segs = [*segs[:i], (0xE2, _mpf_moved(segs[i][1], delta)), *segs[i + 1 :]]
    out = bytearray(b"\xff\xd8")
    for marker, payload in segs:
        out += bytes((0xFF, marker))
        if marker not in _NO_LENGTH:
            if len(payload) + 2 > 0xFFFF:
                raise ImageError("metadata_too_large")
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
        raise ImageError("jpeg_only", name=path.name)
    return data


# ---------------------------------------------------------------- EXIF orientation


def _tiff_with_orientation(tiff: bytes, value: int) -> bytes:
    if tiff[:2] not in (b"II", b"MM"):
        raise ValueError("unknown byte order")
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
        raise ImageError("orientation_range")
    data = _require_jpeg(path)
    segs, start = _jpeg_segments(data)
    before = list(segs)
    for k, seg in enumerate(segs):
        if _is_exif(seg):
            try:
                tiff = _tiff_with_orientation(seg[1][len(EXIF_HEADER) :], value)
            except (struct.error, IndexError, ValueError) as err:
                raise ImageError("damaged_exif", name=path.name) from err
            segs[k] = (seg[0], EXIF_HEADER + tiff)
            break
    else:
        tiff = b"MM\x00\x2a\x00\x00\x00\x08" + struct.pack(
            ">HHHIH", 1, ORIENTATION_TAG, 3, 1, value
        )
        tiff += b"\x00\x00" + b"\x00\x00\x00\x00"
        segs.insert(_insert_at(segs), (0xE1, EXIF_HEADER + tiff))
    _write_atomic(path, _jpeg_join(segs, data[start:], before))


def rotate(path: Path, degrees: int) -> int:
    """Turn the picture as shown by `degrees` clockwise; returns the new orientation."""
    value = rotated(get_orientation(path), degrees)
    set_orientation(path, value)
    return value


# ---------------------------------------------------------------- XMP crop


def _xmp_prefix(xmp: str) -> str | None:
    m = re.search(r'xmlns:([\w.-]+)\s*=\s*["\']' + re.escape(CRS_NS) + "[\"']", xmp)
    return re.escape(m.group(1)) if m else None


def parse_crop(xmp: str | bytes | None) -> Box | None:
    """(left, top, right, bottom) in fractions of the stored image, or None without a crop."""
    if not xmp:
        return None
    if len(xmp) > MAX_XMP:
        return None
    if isinstance(xmp, bytes):
        xmp = xmp.decode("utf-8", "replace")
    p = _xmp_prefix(xmp)
    if not p:
        return None
    text = xmp

    def field(name: str) -> str | None:
        # The value is stripped here, not in the pattern: lazy and greedy whitespace around it
        # backtracks for hours on a long run of spaces.
        m = re.search(rf'{p}:{name}\s*=\s*["\']([^"\']*)["\']', text) or re.search(
            rf"<{p}:{name}>([^<]*)</{p}:{name}>", text
        )
        return m.group(1).strip() if m else None

    if (field("HasCrop") or "").lower() != "true":
        return None
    try:
        left, top, right, bottom = (float(field(n) or "nan") for n in CROP_FIELDS)
    except ValueError:
        return None
    if any(math.isnan(v) for v in (left, top, right, bottom)):  # before clamping: max(0, nan) is 0
        return None
    box = (max(0.0, left), max(0.0, top), min(1.0, right), min(1.0, bottom))
    if box[2] <= box[0] or box[3] <= box[1]:
        return None
    return box


def _xmp_without_crop(xmp: str, p: str) -> str:
    for name in ("HasCrop", *CROP_FIELDS):
        # (?<!\s): try each run of whitespace once from its start, not from every space in it
        xmp = re.sub(rf'(?<!\s)\s+{p}:{name}\s*=\s*(["\'])[^"\']*\1', "", xmp)
        xmp = re.sub(rf"(?<!\s)\s*<{p}:{name}>[^<]*</{p}:{name}>", "", xmp)
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
    with path.open("rb") as f:
        data = f.read(HEAD_BYTES)
    if data[:2] != b"\xff\xd8":
        with Image.open(path) as im:
            raw = im.info.get("xmp")
        if isinstance(raw, bytes):
            return raw.decode("utf-8", "replace")
        return raw if isinstance(raw, str) else None
    try:
        segs, _ = _jpeg_segments(data)
    except ImageError:  # metadata longer than the head: no crop is read
        return None
    for seg in segs:
        if _is_xmp(seg):
            return seg[1][len(XMP_HEADER) :].decode("utf-8", "replace")
    return None


def get_crop(path: Path) -> Box | None:
    return parse_crop(read_xmp(path))


def _check_box(box: Box) -> None:
    left, top, right, bottom = box
    if not (0 <= left < right <= 1 and 0 <= top < bottom <= 1):
        raise ImageError("crop_range")


def set_crop(path: Path, box: Box | None) -> None:
    """Write the crop in fractions of the stored image as XMP; None removes it."""
    if box is not None:
        _check_box(box)
    data = _require_jpeg(path)
    segs, start = _jpeg_segments(data)
    before = list(segs)
    k = next((k for k, seg in enumerate(segs) if _is_xmp(seg)), None)
    xmp = segs[k][1][len(XMP_HEADER) :].decode("utf-8", "replace") if k is not None else None
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
                raise ImageError("xmp_unsupported", name=path.name)
            if not p:
                p = "crs"
                attrs = f' xmlns:crs="{CRS_NS}"' + attrs
            xmp = xmp[: m.end()] + attrs.format(p=p) + xmp[m.end() :]
    segment = (0xE1, XMP_HEADER + xmp.encode("utf-8"))
    if k is None:
        segs.insert(_insert_at(segs), segment)
    else:
        segs[k] = segment
    _write_atomic(path, _jpeg_join(segs, data[start:], before))


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
    _check_box(box)
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
            # Reading a PNG's EXIF decodes the whole picture: not for huge ones
            huge = fmt not in JPEG_FORMATS and w * h > MAX_PIXELS
            o = 1 if huge else _valid_orientation(im.getexif().get(ORIENTATION_TAG, 1))
    except Exception as err:  # Pillow raises several kinds for unreadable files
        raise _unreadable(path, err) from err
    if o >= 5:
        w, h = h, w
    crop = crop_as_shown(path)
    return {
        "width": w,
        "height": h,
        "format": fmt,
        "orientation": o,
        "crop": list(crop) if crop else None,
        "editable": fmt in JPEG_FORMATS,
    }


def edit(
    path: Path, rotate_by: int, box: Box | None, *, orientation: int | None = None
) -> ImageInfo:
    """One editor save: turn by `rotate_by` degrees clockwise (or set `orientation`), then set the
    crop in fractions of the picture as shown after that turn, or remove it (None)."""
    original = _require_jpeg(path)
    if box is not None:
        _check_box(box)
    try:
        if orientation is not None:
            if orientation != get_orientation(path):
                set_orientation(path, orientation)
        elif rotate_by % 360:
            rotate(path, rotate_by)
        crop_shown(path, box)
    except Exception:
        if path.read_bytes() != original:  # the turn was written: a failed crop takes it back
            _write_atomic(path, original)
        raise
    return info(path)


# ---------------------------------------------------------------- preparing


def _unreadable(path: Path, err: Exception) -> ImageError:
    """Pillow's messages name the full path; users see only the file's name."""
    return ImageError("unreadable", name=path.name, error=str(err).replace(str(path), path.name))


def _check_pixels(im: Image.Image, path: Path) -> None:
    if im.width * im.height > MAX_PIXELS:
        raise ImageError(
            "too_large",
            name=path.name,
            megapixels=round(im.width * im.height / 1e6),
            limit=MAX_PIXELS // 10**6,
        )


def render(
    path: Path,
    width: int,
    height: int,
    fit: Fit = "cover",
    use_crop: bool = True,
    look: Look = Look(),  # frozen, so one shared default is safe
) -> bytes:
    """The picture as a baseline JPEG: crop, orientation, then cover or contain; then the look.

    cover is exactly width x height, scaled to cover with the overhang cut evenly; contain is scaled
    to fit inside, aspect kept. use_crop=False ignores the crop, e.g. to draw a new crop on. A look
    adjusts it, reduces it to a display's colours and picks the file format.
    """
    if fit not in FITS:
        raise ImageError("invalid_fit")
    crop: Box | None = None
    if use_crop:
        try:
            crop = get_crop(path)
        except ImageError, OSError, struct.error:
            crop = None
    try:
        im = Image.open(path)
    except Exception as err:  # Pillow raises several kinds for unreadable files
        raise _unreadable(path, err) from err
    try:
        return _render(im, path, crop, width, height, fit, look)
    except ImageError:
        raise
    except Exception as err:  # decoding happens here, and Pillow raises several kinds
        raise _unreadable(path, err) from err


def _render(
    im: Image.Image, path: Path, crop: Box | None, width: int, height: int, fit: Fit, look: Look
) -> bytes:
    with im:
        if (
            im.format not in JPEG_FORMATS
        ):  # JPEG is checked after reduced decoding; PNG's EXIF decodes it all
            _check_pixels(im, path)
        orientation = _valid_orientation(im.getexif().get(ORIENTATION_TAG, 1))
        sw, sh = im.size
        left, top, right, bottom = crop or (0.0, 0.0, 1.0, 1.0)
        cw, ch = (right - left) * sw, (bottom - top) * sh
        dw, dh = (ch, cw) if orientation >= 5 else (cw, ch)
        scale = (max if fit == "cover" else min)(width / dw, height / dh)
        if im.format in JPEG_FORMATS and scale < 1:  # decode at a reduced size where that is enough
            im.draft("RGB", (math.ceil(sw * scale), math.ceil(sh * scale)))
        _check_pixels(im, path)
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
        return _apply_look(out_im, look)
