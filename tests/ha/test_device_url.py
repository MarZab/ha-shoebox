from __future__ import annotations

import io

from aiohttp.test_utils import TestClient
from homeassistant.components.image import ImageEntity
from homeassistant.components.image.const import DATA_COMPONENT as IMAGE_COMPONENT
from homeassistant.core import HomeAssistant
from PIL import Image
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from custom_components.shoebox.const import DOMAIN, TITLE

from ..conftest import Tree
from .conftest import rotation

URL = "/api/shoebox/image/image.evening"


@pytest.fixture
async def device(
    hass_client: ClientSessionGenerator,
    hass_read_only_access_token: str,
    with_rotation: MockConfigEntry,
) -> TestClient:
    """A device: a user without admin rights, with a long-lived token."""
    return await hass_client(hass_read_only_access_token)


async def press(hass: HomeAssistant) -> None:
    await hass.services.async_call(
        "button", "press", {"entity_id": "button.evening_next"}, blocking=True
    )


async def test_device_gets_the_picture_at_its_size(
    hass: HomeAssistant, device: TestClient, tree: Tree
) -> None:
    tree("evening/a.jpg")
    assert (await device.get(URL)).status == 404  # nothing shown yet
    await press(hass)
    response = await device.get(URL, params={"width": "200", "height": "120", "fit": "cover"})
    assert response.status == 200
    assert response.headers["Content-Type"] == "image/jpeg"
    assert response.headers["Last-Modified"].endswith("GMT")
    with Image.open(io.BytesIO(await response.read())) as im:
        assert im.size == (200, 120)
        assert "progressive" not in im.info


async def test_a_display_gets_its_palette_and_format(
    hass: HomeAssistant, device: TestClient, tree: Tree
) -> None:
    tree("evening/a.jpg")
    await press(hass)
    plain = await device.get(URL, params={"width": "64", "height": "40"})
    epaper = await device.get(URL, params={"width": "64", "height": "40", "colors": "bw"})
    assert (epaper.status, epaper.headers["Content-Type"]) == (200, "image/png")
    assert epaper.headers["ETag"] != plain.headers["ETag"]  # each look is its own picture
    with Image.open(io.BytesIO(await epaper.read())) as im:
        assert {c for _, c in im.convert("RGB").getcolors()} <= {(0, 0, 0), (255, 255, 255)}
    etag = epaper.headers["ETag"]
    again = await device.get(
        URL, params={"width": "64", "height": "40", "colors": "bw"}, headers={"If-None-Match": etag}
    )
    assert again.status == 304


async def test_unchanged_picture_is_not_sent_again(
    hass: HomeAssistant, device: TestClient, tree: Tree
) -> None:
    tree("evening/a.jpg", "evening/b.jpg")
    await press(hass)
    first = await device.get(URL)
    etag = first.headers["ETag"]
    assert (await device.get(URL, headers={"If-None-Match": etag})).status == 304
    await press(hass)
    second = await device.get(URL, headers={"If-None-Match": etag})
    assert second.status == 200
    assert second.headers["ETag"] != etag


async def test_url_stays_the_same_across_a_reload(
    hass: HomeAssistant, device: TestClient, with_rotation: MockConfigEntry, tree: Tree
) -> None:
    tree("evening/a.jpg")
    await press(hass)
    assert await hass.config_entries.async_reload(with_rotation.entry_id)
    assert (await device.get(URL)).status == 200


# ---------------------------------------------------------------- the image entity's token


@pytest.fixture
async def two_rotations(hass: HomeAssistant, tree: Tree) -> None:
    tree("evening/a.jpg", "morning/b.jpg")
    entry = MockConfigEntry(
        domain=DOMAIN,
        title=TITLE,
        data={},
        subentries_data=[rotation(), rotation("Morning", "local/morning/*")],
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    for name in ("evening", "morning"):
        await hass.services.async_call(
            "button", "press", {"entity_id": f"button.{name}_next"}, blocking=True
        )


def image(hass: HomeAssistant, entity_id: str) -> ImageEntity:
    entity = hass.data[IMAGE_COMPONENT].get_entity(entity_id)
    assert entity is not None
    return entity


@pytest.mark.usefixtures("two_rotations")
async def test_a_device_can_use_the_entitys_token(
    hass: HomeAssistant,
    hass_client_no_auth: ClientSessionGenerator,
    caplog: pytest.LogCaptureFixture,
) -> None:
    client = await hass_client_no_auth()
    token = image(hass, "image.evening").access_tokens[-1]
    params = {"token": token, "width": "64", "height": "80", "fit": "cover"}
    response = await client.get(URL, params=params)
    assert response.status == 200
    with Image.open(io.BytesIO(await response.read())) as im:
        assert im.size == (64, 80)
    image(hass, "image.evening").async_update_token()  # every 5 minutes: the last two work
    assert (await client.get(URL, params={"token": token})).status == 200
    image(hass, "image.evening").async_update_token()
    assert (await client.get(URL, params={"token": token})).status == 403
    shoebox_logs = [
        r.getMessage() for r in caplog.records if r.name.startswith("custom_components")
    ]
    assert not any(token in line for line in shoebox_logs)


@pytest.mark.usefixtures("two_rotations")
@pytest.mark.parametrize(
    ("url", "token", "headers", "status"),
    [
        (URL, "made-up", {}, 403),  # not a login attempt: no ban counting
        (URL, None, {}, 403),
        (URL, "morning", {}, 403),  # another rotation's token opens only that rotation
        (URL, None, {"Authorization": "Bearer wrong"}, 401),  # a wrong login: counted
        ("/api/shoebox/image/image.missing", "evening", {}, 401),  # does not tell what exists
        ("/api/shoebox/image/sun.sun", None, {}, 401),
    ],
)
async def test_token_refusals(
    hass: HomeAssistant,
    hass_client_no_auth: ClientSessionGenerator,
    url: str,
    token: str | None,
    headers: dict[str, str],
    status: int,
) -> None:
    client = await hass_client_no_auth()
    params = {}
    if token in ("evening", "morning"):
        params["token"] = image(hass, f"image.{token}").access_tokens[-1]
    elif token:
        params["token"] = token
    assert (await client.get(url, params=params, headers=headers)).status == status


@pytest.mark.parametrize(
    ("url", "params", "status"),
    [
        ("/api/shoebox/image/image.missing", {}, 404),
        ("/api/shoebox/image/button.evening_next", {}, 404),
        ("/api/shoebox/image/sun.sun", {}, 404),
        (URL, {"width": "0"}, 400),
        (URL, {"height": "5000"}, 400),
        (URL, {"width": "abc"}, 400),
        (URL, {"fit": "stretch"}, 400),
        (URL, {"colors": "rainbow"}, 400),
    ],
)
async def test_refusals(device: TestClient, url: str, params: dict[str, str], status: int) -> None:
    assert (await device.get(url, params=params)).status == status
