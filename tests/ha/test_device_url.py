from __future__ import annotations

import io

from aiohttp.test_utils import TestClient
from homeassistant.core import HomeAssistant
from PIL import Image
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from ..conftest import Tree

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


async def test_without_a_token(
    hass_client_no_auth: ClientSessionGenerator, with_rotation: MockConfigEntry
) -> None:
    client = await hass_client_no_auth()
    assert (await client.get(URL)).status == 401


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
    ],
)
async def test_refusals(device: TestClient, url: str, params: dict[str, str], status: int) -> None:
    assert (await device.get(url, params=params)).status == status
