"""Rotations in the media browser: each rotation is a folder of the pictures it selects."""

from __future__ import annotations

from typing import override
from urllib.parse import quote

from homeassistant.components.media_player import BrowseError, MediaClass
from homeassistant.components.media_source import (
    BrowseMediaSource,
    MediaSource,
    MediaSourceItem,
    PlayMedia,
    Unresolvable,
)
from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant

from . import media
from .const import CONF_PATTERNS, DOMAIN, SUBENTRY_ROTATION, TITLE
from .runtime import Shoebox

MIME: str = "image/jpeg"


async def async_get_media_source(hass: HomeAssistant) -> ShoeboxMediaSource:
    return ShoeboxMediaSource(hass)


def media_url(rotation_id: str, path: str, *, thumb: bool = False) -> str:
    url = f"/api/shoebox/media/{rotation_id}/{quote(path)}"
    return url + "?thumb=1" if thumb else url


class ShoeboxMediaSource(MediaSource):
    name = TITLE

    def __init__(self, hass: HomeAssistant) -> None:
        super().__init__(DOMAIN)
        self.hass = hass

    def _loaded(self) -> tuple[Shoebox, dict[str, ConfigSubentry]]:
        entries = self.hass.config_entries.async_loaded_entries(DOMAIN)
        if not entries:
            raise BrowseError("Shoebox is not set up")
        rotations = {
            sub.subentry_id: sub
            for sub in entries[0].subentries.values()
            if sub.subentry_type == SUBENTRY_ROTATION
        }
        return entries[0].runtime_data, rotations

    async def _pictures(self, shoebox: Shoebox, rotation: ConfigSubentry) -> list[str]:
        entries = await self.hass.async_add_executor_job(shoebox.library.walk)
        return media.select_pictures(entries, rotation.data.get(CONF_PATTERNS, []))

    @override
    async def async_resolve_media(self, item: MediaSourceItem) -> PlayMedia:
        rotation_id, _, path = (item.identifier or "").partition("/")
        if not path:
            raise Unresolvable("Choose a picture in a rotation")
        return PlayMedia(media_url(rotation_id, path), MIME)

    @override
    async def async_browse_media(self, item: MediaSourceItem) -> BrowseMediaSource:
        shoebox, rotations = self._loaded()
        if not item.identifier:
            return self._folder(
                None,
                TITLE,
                [self._rotation(shoebox, sub) for sub in rotations.values()],
            )
        if (rotation := rotations.get(item.identifier)) is None:
            raise BrowseError(f"Unknown rotation: {item.identifier}")
        pictures = [
            BrowseMediaSource(
                domain=DOMAIN,
                identifier=f"{rotation.subentry_id}/{path}",
                media_class=MediaClass.IMAGE,
                media_content_type=MIME,
                title=path.rsplit("/", 1)[-1],
                can_play=True,
                can_expand=False,
                thumbnail=media_url(rotation.subentry_id, path, thumb=True),
            )
            for path in await self._pictures(shoebox, rotation)
        ]
        return self._folder(rotation.subentry_id, rotation.title, pictures)

    def _rotation(self, shoebox: Shoebox, rotation: ConfigSubentry) -> BrowseMediaSource:
        current = shoebox.rotations.state(rotation.subentry_id).file
        return BrowseMediaSource(
            domain=DOMAIN,
            identifier=rotation.subentry_id,
            media_class=MediaClass.DIRECTORY,
            media_content_type="",
            title=rotation.title,
            can_play=False,
            can_expand=True,
            children_media_class=MediaClass.IMAGE,
            thumbnail=media_url(rotation.subentry_id, current, thumb=True) if current else None,
        )

    @staticmethod
    def _folder(
        identifier: str | None, title: str, children: list[BrowseMediaSource]
    ) -> BrowseMediaSource:
        return BrowseMediaSource(
            domain=DOMAIN,
            identifier=identifier,
            media_class=MediaClass.DIRECTORY,
            media_content_type="",
            title=title,
            can_play=False,
            can_expand=True,
            children=children,
            children_media_class=MediaClass.IMAGE if identifier else MediaClass.DIRECTORY,
        )
