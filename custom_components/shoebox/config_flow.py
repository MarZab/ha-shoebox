"""Config flow: one Shoebox entry. Options: cache size, clearing the cache, the sidebar panel."""

from __future__ import annotations

from typing import Any, override

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlowWithReload,
)
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
)
import probatio as vol

from .const import (
    CONF_CACHE_SIZE,
    CONF_CLEAR_CACHE,
    CONF_SHOW_IN_SIDEBAR,
    DEFAULT_CACHE_SIZE_MB,
    DOMAIN,
    MIN_CACHE_SIZE_MB,
    TITLE,
)
from .runtime import MB, variant_cache


class ShoeboxConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @override
    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(title=TITLE, data={})
        return self.async_show_form(step_id="user")

    @staticmethod
    @callback
    @override
    def async_get_options_flow(config_entry: ConfigEntry) -> ShoeboxOptionsFlow:
        return ShoeboxOptionsFlow()


class ShoeboxOptionsFlow(OptionsFlowWithReload):
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        cache = variant_cache(self.hass, self.config_entry.options)
        if user_input is not None:
            if user_input.get(CONF_CLEAR_CACHE):
                await self.hass.async_add_executor_job(cache.clear)
            return self.async_create_entry(
                data={
                    CONF_CACHE_SIZE: int(user_input[CONF_CACHE_SIZE]),
                    CONF_SHOW_IN_SIDEBAR: bool(user_input[CONF_SHOW_IN_SIDEBAR]),
                }
            )
        files, size = await self.hass.async_add_executor_job(cache.usage)
        options = self.config_entry.options
        schema = vol.Schema(
            {
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
            description_placeholders={"files": str(files), "size": f"{size / MB:.1f}"},
        )
