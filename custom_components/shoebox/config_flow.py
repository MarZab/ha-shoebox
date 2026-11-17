"""Config flow: one Shoebox entry, rotations as its subentries, and the options.

Options: cache size, clearing the cache, the sidebar panel.
"""

from __future__ import annotations

from typing import Any, override

from homeassistant.config_entries import (
    SOURCE_RECONFIGURE,
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    OptionsFlow,
    SubentryFlowResult,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
)
import probatio as vol

from . import media
from .const import (
    CONF_CACHE_SIZE,
    CONF_CLEAR_CACHE,
    CONF_FOLDERS,
    CONF_ORDER,
    CONF_PATTERNS,
    CONF_SHOW_IN_SIDEBAR,
    DEFAULT_CACHE_SIZE_MB,
    DEFAULT_FOLDERS,
    DOMAIN,
    MIN_CACHE_SIZE_MB,
    ORDER_PATH,
    ORDER_SHUFFLE,
    SUBENTRY_ROTATION,
    TITLE,
)
from .errors import MediaError
from .library import Library
from .runtime import MB, chosen_folders, media_folders, variant_cache

PREVIEW_COUNT = 5


def folder_selector(hass: HomeAssistant) -> SelectSelector:
    """The media folders Home Assistant knows, by name and location."""
    return SelectSelector(
        SelectSelectorConfig(
            options=[
                SelectOptionDict(value=name, label=f"{name} ({path})")
                for name, path in hass.config.media_dirs.items()
            ],
            multiple=True,
        )
    )


def folders_error(folders: list[str]) -> dict[str, str]:
    return {} if folders else {CONF_FOLDERS: "no_folder"}


class ShoeboxConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @override
    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            folders = list(user_input[CONF_FOLDERS])
            if not (errors := folders_error(folders)):
                return self.async_create_entry(
                    title=TITLE, data={}, options={CONF_FOLDERS: folders}
                )
        known = [f for f in DEFAULT_FOLDERS if f in self.hass.config.media_dirs]
        schema = vol.Schema({vol.Required(CONF_FOLDERS, default=known): folder_selector(self.hass)})
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    @override
    def async_get_options_flow(config_entry: ConfigEntry) -> ShoeboxOptionsFlow:
        return ShoeboxOptionsFlow()

    @classmethod
    @callback
    @override
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        return {SUBENTRY_ROTATION: RotationSubentryFlow}


class ShoeboxOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        cache = variant_cache(self.hass, self.config_entry.options)
        errors: dict[str, str] = {}
        if user_input is not None:
            folders = list(user_input[CONF_FOLDERS])
            if not (errors := folders_error(folders)):
                if user_input.get(CONF_CLEAR_CACHE):
                    await self.hass.async_add_executor_job(cache.clear)
                return self.async_create_entry(
                    data={
                        CONF_FOLDERS: folders,
                        CONF_CACHE_SIZE: int(user_input[CONF_CACHE_SIZE]),
                        CONF_SHOW_IN_SIDEBAR: bool(user_input[CONF_SHOW_IN_SIDEBAR]),
                    }
                )
        files, size = await self.hass.async_add_executor_job(cache.usage)
        options = self.config_entry.options
        schema = vol.Schema(
            {
                vol.Required(CONF_FOLDERS, default=chosen_folders(options)): folder_selector(
                    self.hass
                ),
                vol.Required(
                    CONF_CACHE_SIZE, default=options.get(CONF_CACHE_SIZE, DEFAULT_CACHE_SIZE_MB)
                ): NumberSelector(
                    NumberSelectorConfig(
                        min=MIN_CACHE_SIZE_MB,
                        max=100_000,
                        step=1,
                        mode=NumberSelectorMode.BOX,
                        unit_of_measurement="MB",
                    )
                ),
                vol.Required(CONF_CLEAR_CACHE, default=False): BooleanSelector(),
                vol.Required(
                    CONF_SHOW_IN_SIDEBAR, default=options.get(CONF_SHOW_IN_SIDEBAR, True)
                ): BooleanSelector(),
            }
        )
        return self.async_show_form(
            step_id="init",
            data_schema=schema,
            errors=errors,
            description_placeholders={"files": str(files), "size": f"{size / MB:.1f}"},
        )


class RotationSubentryFlow(ConfigSubentryFlow):
    """Add or change a rotation: a name and the patterns that select its pictures."""

    def __init__(self) -> None:
        self._name = ""
        self._patterns: list[str] = []
        self._order: str = ORDER_PATH

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> SubentryFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            self._name = str(user_input["name"]).strip()
            self._patterns = [p.strip() for p in user_input[CONF_PATTERNS] if p.strip()]
            self._order = user_input[CONF_ORDER]
            if not self._patterns:
                errors[CONF_PATTERNS] = "no_pattern"
            else:
                try:
                    for pattern in self._patterns:
                        media.check_pattern(pattern)
                except MediaError:
                    errors[CONF_PATTERNS] = "invalid_pattern"
            if not errors:
                return await self.async_step_preview()
        schema = vol.Schema(
            {
                vol.Required("name", default=self._name): TextSelector(),
                vol.Required(CONF_PATTERNS, default=self._patterns): TextSelector(
                    TextSelectorConfig(multiple=True)
                ),
                vol.Required(CONF_ORDER, default=self._order): SelectSelector(
                    SelectSelectorConfig(
                        options=[ORDER_PATH, ORDER_SHUFFLE],
                        translation_key=CONF_ORDER,
                        mode=SelectSelectorMode.LIST,
                    )
                ),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        subentry = self._get_reconfigure_subentry()
        self._name = subentry.title
        self._patterns = list(subentry.data.get(CONF_PATTERNS, []))
        self._order = subentry.data.get(CONF_ORDER, ORDER_PATH)
        return await self.async_step_user()

    async def async_step_preview(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        data = {CONF_PATTERNS: self._patterns, CONF_ORDER: self._order}
        if user_input is not None:
            if self.source == SOURCE_RECONFIGURE:
                return self.async_update_and_abort(
                    self._get_entry(), self._get_reconfigure_subentry(), title=self._name, data=data
                )
            return self.async_create_entry(title=self._name, data=data)
        library = Library(media_folders(self.hass, self._get_entry().options))
        files = await self.hass.async_add_executor_job(library.pictures, self._patterns)
        return self.async_show_form(
            step_id="preview",
            data_schema=vol.Schema({}),
            description_placeholders={
                "count": str(len(files)),
                "examples": "\n".join(f"- {f}" for f in files[:PREVIEW_COUNT]) or "-",
            },
        )
