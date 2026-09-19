"""Config flow for the Tascam BD-MP4K integration."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
import voluptuous as vol

from .const import (
    CONF_HOST,
    CONF_MAC,
    CONF_PORT,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DOMAIN,
)
from .protocol import TascamClient, TascamError
from .wol import normalize_mac

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_MAC): str,
    }
)


class TascamConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tascam BD-MP4K."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]

            if CONF_MAC in user_input:
                mac = normalize_mac(user_input[CONF_MAC])
                if mac is None:
                    errors[CONF_MAC] = "invalid_mac"
                else:
                    user_input[CONF_MAC] = mac

            await self.async_set_unique_id(f"{host}:{port}")
            self._abort_if_unique_id_configured()

            if not errors:
                client = TascamClient(host, port)
                try:
                    await client.async_connect()
                except TascamError as err:
                    _LOGGER.debug("Connection test failed: %s", err)
                    errors["base"] = "cannot_connect"
                finally:
                    await client.async_disconnect()

                if not errors:
                    return self.async_create_entry(
                        title=DEFAULT_NAME, data=user_input
                    )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
