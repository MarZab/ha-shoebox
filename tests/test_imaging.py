from __future__ import annotations

import io
from pathlib import Path

from PIL import Image, ImageOps
import pytest

from custom_components.shoebox import imaging
from custom_components.shoebox.errors import ImageError

from .images import ORIENTATION_TAG, colour_at, write_image

POINTS = [(0.2, 0.2), (0.8, 0.2), (0.2, 0.8), (0.8, 0.8)]
ORIENTATIONS = range(1, 9)


def shown(path: Path) -> Image.Image:
    """The picture as viewers show it, by Pillow's own reading of the EXIF orientation."""
    with Image.open(path) as im:
        return ImageOps.exif_transpose(im)


def colours(image: Image.Image | bytes | Path) -> list[str]:
    return [colour_at(image, x, y) for x, y in POINTS]


def image_data(path: Path) -> bytes:
    data = path.read_bytes()
    return data[data.index(b"\xff\xda") :]


# ---------------------------------------------------------------- orientation


@pytest.mark.parametrize("orientation", ORIENTATIONS)
@pytest.mark.parametrize("degrees", [90, 180, 270, -90])
def test_rotate_turns_the_shown_picture(tmp_path: Path, orientation: int, degrees: int) -> None:
    path = write_image(tmp_path / "a.jpg", orientation=orientation)
    expected = colours(shown(path).rotate(-degrees, expand=True))
    imaging.rotate(path, degrees)
    assert colours(shown(path)) == expected


@pytest.mark.parametrize("degrees", [45, 1, -100])
def test_rotate_refuses_other_angles(degrees: int) -> None:
    with pytest.raises(ImageError, match="multiple of 90"):
        imaging.rotated(1, degrees)


@pytest.mark.parametrize("exif", [True, False])
def test_set_orientation_keeps_image_data(tmp_path: Path, exif: bool) -> None:
    path = write_image(tmp_path / "a.jpg", orientation=3 if exif else 1)
    before = image_data(path)
    imaging.set_orientation(path, 6)
    assert imaging.get_orientation(path) == 6
    assert image_data(path) == before


def test_set_orientation_refuses_out_of_range(tmp_path: Path) -> None:
    with pytest.raises(ImageError, match=r"1\.\.8"):
        imaging.set_orientation(write_image(tmp_path / "a.jpg"), 9)


# ---------------------------------------------------------------- crop


def test_crop_round_trip_and_clear(tmp_path: Path) -> None:
    path = write_image(tmp_path / "a.jpg")
    imaging.set_crop(path, (0.1, 0.2, 0.6, 0.9))
    assert imaging.get_crop(path) == pytest.approx((0.1, 0.2, 0.6, 0.9))
    imaging.set_crop(path, None)
    assert imaging.get_crop(path) is None


def test_set_crop_keeps_other_xmp_fields(tmp_path: Path) -> None:
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
    assert 'dc:format="image/jpeg"' in text
    assert text.count("CropLeft") == 1
    imaging.set_crop(path, None)
    assert "CropLeft" not in (imaging.read_xmp(path) or "")
    assert 'dc:format="image/jpeg"' in (imaging.read_xmp(path) or "")


@pytest.mark.parametrize(
    "box", [(0.5, 0, 0.4, 1), (0, 0, 1.1, 1), (-0.1, 0, 1, 1), (0, 0.5, 1, 0.5)]
)
def test_set_crop_refuses_bad_boxes(tmp_path: Path, box: imaging.Box) -> None:
    with pytest.raises(ImageError, match="crop needs"):
        imaging.set_crop(write_image(tmp_path / "a.jpg"), box)


@pytest.mark.parametrize(
    "xmp",
    [
        None,
        b"",
        b"<x/>",
        f'<d xmlns:crs="{imaging.CRS_NS}" crs:HasCrop="False"/>'.encode(),
        f'<d xmlns:crs="{imaging.CRS_NS}" crs:HasCrop="True" crs:CropLeft="x"/>'.encode(),
        f'<d xmlns:crs="{imaging.CRS_NS}" crs:HasCrop="True" crs:CropLeft="0.5" crs:CropTop="0" '
        'crs:CropRight="0.2" crs:CropBottom="1"/>'.encode(),
    ],
)
def test_parse_crop_without_a_usable_crop(xmp: bytes | None) -> None:
    assert imaging.parse_crop(xmp) is None


def test_parse_crop_element_form() -> None:
    xmp = (
        f'<d xmlns:c="{imaging.CRS_NS}"><c:HasCrop>True</c:HasCrop><c:CropLeft>0.1</c:CropLeft>'
        "<c:CropTop>0.2</c:CropTop><c:CropRight>0.7</c:CropRight><c:CropBottom>0.8</c:CropBottom></d>"
    )
    assert imaging.parse_crop(xmp) == pytest.approx((0.1, 0.2, 0.7, 0.8))


@pytest.mark.parametrize("orientation", ORIENTATIONS)
def test_crop_shown_and_crop_as_shown_are_inverse(tmp_path: Path, orientation: int) -> None:
    path = write_image(tmp_path / "a.jpg", orientation=orientation)
    imaging.crop_shown(path, (0.1, 0.2, 0.5, 0.9))
    assert imaging.crop_as_shown(path) == pytest.approx((0.1, 0.2, 0.5, 0.9))
    imaging.crop_shown(path, None)
    assert imaging.crop_as_shown(path) is None


# ---------------------------------------------------------------- info and edit


def test_info_reports_shown_size_and_crop(tmp_path: Path) -> None:
    path = write_image(tmp_path / "a.jpg", (80, 40), orientation=6, crop=(0.0, 0.0, 0.5, 0.5))
    info = imaging.info(path)
    assert (info["width"], info["height"], info["orientation"], info["editable"]) == (
        40,
        80,
        6,
        True,
    )
    assert info["crop"] == pytest.approx([0.5, 0.0, 1.0, 0.5])


def test_info_png_is_not_editable(tmp_path: Path) -> None:
    assert imaging.info(write_image(tmp_path / "a.png"))["editable"] is False


def test_edit_turns_then_crops_as_shown(tmp_path: Path) -> None:
    path = write_image(tmp_path / "a.jpg")
    info = imaging.edit(path, 90, (0.0, 0.0, 0.5, 0.5))
    assert info["orientation"] == 6
    assert colours(imaging.render(path, 20, 20, "cover")) == ["blue"] * 4


def test_edit_sets_orientation_and_removes_crop(tmp_path: Path) -> None:
    path = write_image(tmp_path / "a.jpg", crop=(0.0, 0.0, 0.5, 0.5))
    info = imaging.edit(path, 0, None, orientation=3)
    assert (info["orientation"], info["crop"]) == (3, None)


# ---------------------------------------------------------------- refusals


@pytest.mark.parametrize(
    "call",
    [
        lambda p: imaging.set_orientation(p, 6),
        lambda p: imaging.set_crop(p, None),
        lambda p: imaging.edit(p, 90, None),
    ],
)
def test_edits_refuse_png(tmp_path: Path, call: object) -> None:
    path = write_image(tmp_path / "a.png")
    with pytest.raises(ImageError, match="only possible in JPEG"):
        call(path)  # type: ignore[operator]


@pytest.mark.parametrize(
    "data",
    [b"\xff\xd8\x00\x00", b"\xff\xd8\xff\xe0\x00\x10JFIF", b"\xff\xd8\xff"],
)
def test_damaged_jpeg(tmp_path: Path, data: bytes) -> None:
    path = tmp_path / "a.jpg"
    path.write_bytes(data)
    with pytest.raises(ImageError, match="Damaged JPEG"):
        imaging.set_orientation(path, 6)


def test_damaged_exif(tmp_path: Path) -> None:
    path = tmp_path / "a.jpg"
    Image.new("RGB", (8, 8)).save(path, "JPEG", exif=b"Exif\x00\x00II*\x00\xff\xff\x00\x00")
    with pytest.raises(ImageError, match="damaged EXIF"):
        imaging.set_orientation(path, 6)


def test_unreadable_picture(tmp_path: Path) -> None:
    path = tmp_path / "a.jpg"
    path.write_bytes(b"not a picture")
    with pytest.raises(ImageError, match="cannot read"):
        imaging.render(path, 10, 10)
    with pytest.raises(ImageError, match="cannot read"):
        imaging.info(path)


# ---------------------------------------------------------------- render


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
        assert im.size == expected
        assert im.format == "JPEG"
        assert "progressive" not in im.info
        assert "progression" not in im.info


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


def test_render_large_jpeg_and_png(tmp_path: Path) -> None:
    big = write_image(tmp_path / "big.jpg", (1600, 800))
    assert colours(imaging.render(big, 40, 20, "cover")) == ["red", "green", "blue", "white"]
    png = tmp_path / "a.png"
    Image.new("RGBA", (20, 20), (255, 0, 0, 255)).save(png)
    assert colours(imaging.render(png, 10, 10)) == ["red"] * 4


def test_render_refuses_unknown_fit(tmp_path: Path) -> None:
    with pytest.raises(ImageError, match="fit must be"):
        imaging.render(write_image(tmp_path / "a.jpg"), 10, 10, "stretch")  # type: ignore[arg-type]


def test_get_orientation_of_unusual_values(tmp_path: Path) -> None:
    path = tmp_path / "a.jpg"
    exif = Image.Exif()
    exif[ORIENTATION_TAG] = 42
    Image.new("RGB", (8, 8)).save(path, "JPEG", exif=exif.tobytes())
    assert imaging.get_orientation(path) == 1


def test_crop_shown_refuses_an_inverted_box(tmp_path: Path) -> None:
    with pytest.raises(ImageError, match="crop needs"):
        imaging.crop_shown(write_image(tmp_path / "a.jpg"), (0.5, 0.0, 0.2, 1.0))
