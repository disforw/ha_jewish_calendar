"""Config flow for Jewish calendar integration."""
from __future__ import annotations

import logging
from typing import Any
import zoneinfo

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import (
    CONF_ELEVATION,
    CONF_LANGUAGE,
    CONF_LOCATION,
    CONF_NAME,
    CONF_TIME_ZONE,
)
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    BooleanSelector,
    LocationSelector,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
)
from homeassistant.helpers.typing import ConfigType

DOMAIN = "jewish_calendar"
CONF_DIASPORA = "diaspora"
CONF_CANDLE_LIGHT_MINUTES = "candle_lighting_minutes_before_sunset"
CONF_HAVDALAH_OFFSET_MINUTES = "havdalah_minutes_after_sunset"
DEFAULT_NAME = "Jewish Calendar"
DEFAULT_CANDLE_LIGHT = 18
DEFAULT_DIASPORA = False
DEFAULT_HAVDALAH_OFFSET_MINUTES = 0
DEFAULT_LANGUAGE = "english"

LANGUAGE = [
    SelectOptionDict(value="hebrew", label="Hebrew"),
    SelectOptionDict(value="english", label="English"),
]

_LOGGER = logging.getLogger(__name__)


class JewishCalendarConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Jewish calendar."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Get the options flow for this handler."""
        return JewishCalendarOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            for entry in self.hass.config_entries.async_entries(DOMAIN):
                if all(
                    _value == entry.as_dict().get(_key)
                    for _key, _value in user_input.items()
                    if _key != CONF_NAME
                ):
                    return self.async_abort(reason="already_configured")

                if entry.data[CONF_NAME] == user_input[CONF_NAME]:
                    errors[CONF_NAME] = "name_exists"
                    break

            try:
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                    vol.Required(
                        CONF_DIASPORA, default=DEFAULT_DIASPORA
                    ): BooleanSelector(),
                    vol.Required(
                        CONF_LANGUAGE, default=DEFAULT_LANGUAGE
                    ): SelectSelector(SelectSelectorConfig(options=LANGUAGE)),
                    vol.Required(
                        CONF_LOCATION,
                        default={
                            "latitude": self.hass.config.latitude,
                            "longitude": self.hass.config.longitude,
                        },
                    ): LocationSelector(),
                    vol.Optional(
                        CONF_ELEVATION, default=self.hass.config.elevation
                    ): int,
                    vol.Optional(
                        CONF_TIME_ZONE, default=self.hass.config.time_zone
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=sorted(zoneinfo.available_timezones()),
                        )
                    ),
                }
            ),
            errors=errors,
        )

    async def async_step_import(self, import_config: ConfigType | None) -> FlowResult:
        """Import a config entry from configuration.yaml."""
        return await self.async_step_user(import_config)


class JewishCalendarOptionsFlowHandler(OptionsFlow):
    """Handle Jewish Calendar options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize Jewish Calendar options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        """Manage the Jewish Calendar options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        options = {
            vol.Optional(
                CONF_CANDLE_LIGHT_MINUTES,
                default=self.config_entry.options.get(
                    CONF_CANDLE_LIGHT_MINUTES, DEFAULT_CANDLE_LIGHT
                ),
            ): int,
            vol.Optional(
                CONF_HAVDALAH_OFFSET_MINUTES,
                default=self.config_entry.options.get(
                    CONF_HAVDALAH_OFFSET_MINUTES, DEFAULT_HAVDALAH_OFFSET_MINUTES
                ),
            ): int,
        }

        return self.async_show_form(step_id="init", data_schema=vol.Schema(options))
