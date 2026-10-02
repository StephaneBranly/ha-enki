"""Config flow for Enki."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import (
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    LOGGER,
)

DOCUMENTATION_URL = "https://github.com/StephaneBranly/ha-enki"

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


async def validate_input(
    hass: HomeAssistant,
    data: dict[str, Any],
) -> dict[str, Any]:
    """Validate user input."""

    from .api import API, APIAuthError, APIConnectionError

    api = API(
        data[CONF_USERNAME],
        data[CONF_PASSWORD],
    )

    try:
        await api.connect()

    except APIAuthError as err:
        LOGGER.warning(
            "Enki authentication failed for user %s: %s",
            data[CONF_USERNAME],
            err,
        )
        raise InvalidAuth from err

    except APIConnectionError as err:
        LOGGER.warning(
            "Enki connection failed for user %s: %s",
            data[CONF_USERNAME],
            err,
        )
        raise CannotConnect from err

    return {
        "title": f"Enki - {data[CONF_USERNAME]}"
    }


class EnkiConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Enki."""

    VERSION = 1

    _input_data: dict[str, Any]

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ):
        """Handle the initial step."""

        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(
                    self.hass,
                    user_input,
                )

            except CannotConnect:
                errors["base"] = "cannot_connect"

            except InvalidAuth:
                errors["base"] = "invalid_auth"

            except Exception:
                LOGGER.exception(
                    "Unexpected exception during Enki login"
                )
                errors["base"] = "unknown"

            if not errors:
                await self.async_set_unique_id(
                    info["title"]
                )
                self._abort_if_unique_id_configured()

                self._input_data = {
                    **user_input,
                    "_title": info["title"],
                }

                return await self.async_step_polling()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
            description_placeholders={
                "documentation_url": DOCUMENTATION_URL,
            },
        )

    async def async_step_polling(
        self,
        user_input: dict[str, Any] | None = None,
    ):
        """Handle polling configuration."""

        if user_input is not None:
            title = self._input_data.pop("_title")

            return self.async_create_entry(
                title=title,
                data={
                    **self._input_data,
                    CONF_SCAN_INTERVAL: user_input[
                        CONF_SCAN_INTERVAL
                    ],
                },
            )

        return self.async_show_form(
            step_id="polling",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=DEFAULT_SCAN_INTERVAL,
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(
                            min=10,
                            max=3600,
                        ),
                    ),
                }
            ),
            description_placeholders={
                "documentation_url": DOCUMENTATION_URL,
            },
        )

    async def async_step_reconfigure(
        self,
        user_input: dict[str, Any] | None = None,
    ):
        """Reconfigure an existing entry."""

        errors: dict[str, str] = {}

        config_entry = (
            self.hass.config_entries.async_get_entry(
                self.context["entry_id"]
            )
        )

        if user_input is not None:
            try:
                await validate_input(
                    self.hass,
                    user_input,
                )

            except CannotConnect:
                errors["base"] = "cannot_connect"

            except InvalidAuth:
                errors["base"] = "invalid_auth"

            except Exception:
                LOGGER.exception(
                    "Unexpected exception during Enki reconfiguration"
                )
                errors["base"] = "unknown"

            else:
                return self.async_update_reload_and_abort(
                    config_entry,
                    unique_id=config_entry.unique_id,
                    data={
                        **config_entry.data,
                        **user_input,
                    },
                    reason="reconfigure_successful",
                )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME,
                        default=config_entry.data[
                            CONF_USERNAME
                        ],
                    ): str,
                    vol.Required(
                        CONF_PASSWORD
                    ): str,
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=config_entry.data.get(
                            CONF_SCAN_INTERVAL,
                            DEFAULT_SCAN_INTERVAL,
                        ),
                    ): vol.All(
                        vol.Coerce(int),
                        vol.Range(
                            min=10,
                            max=3600,
                        ),
                    ),
                }
            ),
            errors=errors,
            description_placeholders={
                "documentation_url": DOCUMENTATION_URL,
            },
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate invalid authentication."""