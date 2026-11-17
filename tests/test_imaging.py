from __future__ import annotations

from collections.abc import Callable
import io
from pathlib import Path

from PIL import Image, ImageOps
import pytest

from custom_components.shoebox import imaging
from custom_components.shoebox.errors import ImageError

from .images import colour_at, write_image

POINTS = [(0.2, 0.2), (0.8, 0.2), (0.2, 0.8), (0.8, 0.8)]
ORIENTATIONS = range(1, 9)


def shown(path: Path) -> Image.Image:
    """The picture as viewers show it, by Pillow's own reading of the EXIF orientation."""
    with Image.open(path) as im:
        return ImageOps.exif_transpose(im)


def colours(image: Image.Image | bytes | Path) -> list[str]:
    return [colour_at(image, x, y) for x, y in POINTS]


# ---------------------------------------------------------------- turning


@pytest.mark.parametrize("orientation", ORIENTATIONS)
@pytest.mark.parametrize("degrees", [90, 180, 270, -90])
def test_rotate_turns_the_shown_picture(tmp_path: Path, orientation: int, degrees: int) -> None:
    path = write_image(tmp_path / "a.jpg", orientation=orientation)
    expected = colours(shown(path).rotate(-degrees, expand=True))
    imaging.rotate(path, degrees)
    assert colours(shown(path)) == expected


@pytest.mark.parametrize("exif", [True, False])
def test_turning_keeps_the_image_data(tmp_path: Path, exif: bool) -> None:
    path = write_image(tmp_path / "a.jpg", orientation=3 if exif else 1)
    data = path.read_bytes()
    before = data[data.index(b"\xff\xda") :]
    imaging.set_orientation(path, 6)
    data = path.read_bytes()
    assert imaging.get_orientation(path) == 6
    assert data[data.index(b"\xff\xda") :] == before


# ---------------------------------------------------------------- cropping


@pytest.mark.parametrize("orientation", ORIENTATIONS)
def test_crop_is_kept_as_shown_whatever_the_orientation(tmp_path: Path, orientation: int) -> None:
    path = write_image(tmp_path / "a.jpg", orientation=orientation)
    imaging.crop_shown(path, (0.1, 0.2, 0.5, 0.9))
    assert imaging.crop_as_shown(path) == pytest.approx((0.1, 0.2, 0.5, 0.9))
    imaging.crop_shown(path, None)
    assert imaging.crop_as_shown(path) is None


def test_crop_keeps_other_xmp_fields(tmp_path: Path) -> None:
    path = tmp_path / "a.jpg"
    xmp = (
        '<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF '
        'xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:Description rdf:about="" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" dc:format="image/jpeg"/></rdf:RDF></x:xmpmeta>'
    )
    Image.new("RGB", (20, 10)).save(path, "JPEG", xmp=xmp.encode())
    imaging.set_crop(path, (0.0, 0.0, 0.5, 0.5))
    imaging.set_crop(path, (0.5, 0.5, 1.0, 1.0))
    text = imaging.read_xmp(path) or ""
    assert text.count("CropLeft") == 1
    assert imaging.get_crop(path) == pytest.approx((0.5, 0.5, 1.0, 1.0))
    imaging.set_crop(path, None)
    assert 'dc:format="image/jpeg"' in (imaging.read_xmp(path) or "")
    assert imaging.get_crop(path) is None


@pytest.mark.parametrize(
    ("xmp", "expected"),
    [
        (  # as Lightroom writes it: elements instead of attributes
            "<c:HasCrop>True</c:HasCrop><c:CropLeft>0.1</c:CropLeft><c:CropTop>0.2</c:CropTop>"
            "<c:CropRight>0.7</c:CropRight><c:CropBottom>0.8</c:CropBottom>",
            (0.1, 0.2, 0.7, 0.8),
        ),
        ("<c:HasCrop>False</c:HasCrop><c:CropLeft>0.1</c:CropLeft>", None),
        ("<c:HasCrop>True</c:HasCrop><c:CropLeft>x</c:CropLeft>", None),
        (  # right of left is not a crop
            "<c:HasCrop>True</c:HasCrop><c:CropLeft>0.5</c:CropLeft><c:CropTop>0</c:CropTop>"
            "<c:CropRight>0.2</c:CropRight><c:CropBottom>1</c:CropBottom>",
            None,
        ),
    ],
)
def test_reads_crops_written_by_other_apps(xmp: str, expected: tuple[float, ...] | None) -> None:
    crop = imaging.parse_crop(f'<d xmlns:c="{imaging.CRS_NS}">{xmp}</d>')
    assert crop == (pytest.approx(expected) if expected else None)


# ---------------------------------------------------------------- the editor


def test_info_reports_the_picture_as_shown(tmp_path: Path) -> None:
    path = write_image(tmp_path / "a.jpg", (80, 40), orientation=6, crop=(0.0, 0.0, 0.5, 0.5))
    info = imaging.info(path)
    assert (info["width"], info["height"], info["orientation"], info["editable"]) == (
        40,
        80,
        6,
        True,
    )
    assert info["crop"] == pytest.approx([0.5, 0.0, 1.0, 0.5])
    assert imaging.info(write_image(tmp_path / "a.png"))["editable"] is False


def test_edit_turns_then_crops_as_shown(tmp_path: Path) -> None:
    path = write_image(tmp_path / "a.jpg")
    assert imaging.edit(path, 90, (0.0, 0.0, 0.5, 0.5))["orientation"] == 6
    assert colours(imaging.render(path, 20, 20, "cover")) == ["blue"] * 4
    info = imaging.edit(path, 0, None, orientation=3)
    assert (info["orientation"], info["crop"]) == (3, None)


# ---------------------------------------------------------------- refusals


def _png(tmp_path: Path) -> Path:
    return write_image(tmp_path / "a.png")


def _damaged_exif(tmp_path: Path) -> Path:
    path = tmp_path / "a.jpg"
    Image.new("RGB", (8, 8)).save(path, "JPEG", exif=b"Exif\x00\x00II*\x00\xff\xff\x00\x00")
    return path


def _bytes(data: bytes) -> Callable[[Path], Path]:
    def make(tmp_path: Path) -> Path:
        path = tmp_path / "a.jpg"
        path.write_bytes(data)
        return path

    return make


def _jpeg(tmp_path: Path) -> Path:
    return write_image(tmp_path / "a.jpg")


@pytest.mark.parametrize(
    ("make", "call", "message"),
    [
        (_jpeg, lambda p: imaging.rotate(p, 45), "multiple of 90"),
        (_jpeg, lambda p: imaging.set_orientation(p, 9), r"1\.\.8"),
        (_jpeg, lambda p: imaging.set_crop(p, (0.5, 0, 0.4, 1)), "crop needs"),
        (_jpeg, lambda p: imaging.crop_shown(p, (0.5, 0.0, 0.2, 1.0)), "crop needs"),
        (_jpeg, lambda p: imaging.render(p, 10, 10, "stretch"), "fit must be"),
        (_png, lambda p: imaging.set_orientation(p, 6), "only possible in JPEG"),
        (_png, lambda p: imaging.edit(p, 90, None), "only possible in JPEG"),
        (_damaged_exif, lambda p: imaging.set_orientation(p, 6), "damaged EXIF"),
        (_bytes(b"\xff\xd8\x00\x00"), lambda p: imaging.set_orientation(p, 6), "Damaged JPEG"),
        (_bytes(b"\xff\xd8\xff"), lambda p: imaging.set_orientation(p, 6), "Damaged JPEG"),
        (_bytes(b"not a picture"), lambda p: imaging.render(p, 10, 10), "cannot read"),
    ],
)
def test_refusals(
    tmp_path: Path, make: Callable[[Path], Path], call: Callable[[Path], object], message: str
) -> None:
    with pytest.raises(ImageError, match=message):
        call(make(tmp_path))


# ---------------------------------------------------------------- preparing


@pytest.mark.parametrize(
    ("fit", "size", "expected"),
    [
        ("cover", (30, 30), (30, 30)),
        ("contain", (30, 30), (30, 15)),
        ("contain", (10, 50), (10, 5)),
    ],
)
def test_render_size(
    tmp_path: Path, fit: imaging.Fit, size: tuple[int, int], expected: tuple[int, int]
) -> None:
    data = imaging.render(write_image(tmp_path / "a.jpg", (80, 40)), *size, fit)
    with Image.open(io.BytesIO(data)) as im:
        assert (im.size, im.format) == (expected, "JPEG")
        assert "progressive" not in im.info  # baseline: small displays decode only that


@pytest.mark.parametrize("orientation", ORIENTATIONS)
def test_render_applies_orientation(tmp_path: Path, orientation: int) -> None:
    path = write_image(tmp_path / "a.jpg", orientation=orientation)
    assert colours(imaging.render(path, 40, 40, "contain")) == colours(shown(path).resize((40, 40)))


def test_render_applies_crop_unless_told_not_to(tmp_path: Path) -> None:
    path = write_image(tmp_path / "a.jpg", crop=(0.5, 0.5, 1.0, 1.0))
    assert colours(imaging.render(path, 20, 20)) == ["white"] * 4
    assert colours(imaging.render(path, 20, 20, use_crop=False)) == [
        "red",
        "green",
        "blue",
        "white",
    ]


def test_render_png_with_transparency(tmp_path: Path) -> None:
    path = tmp_path / "a.png"
    Image.new("RGBA", (20, 20), (255, 0, 0, 255)).save(path)
    assert colours(imaging.render(path, 10, 10)) == ["red"] * 4
