"""Config flow for the Tascam BD-MP4K integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_MAC, CONF_PORT

from .const import DEFAULT_NAME, DEFAULT_PORT, DOMAIN
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

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        """Handle a manual setup: address, port and optional MAC address."""
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            port = user_input[CONF_PORT]
            data: dict[str, Any] = {CONF_HOST: host, CONF_PORT: port}

            if raw_mac := user_input.get(CONF_MAC, "").strip():
                if (mac := normalize_mac(raw_mac)) is None:
                    errors[CONF_MAC] = "invalid_mac"
                else:
                    data[CONF_MAC] = mac

            await self.async_set_unique_id(f"{host}:{port}")
            self._abort_if_unique_id_configured()

            if not errors:
                client = TascamClient(host, port)
                try:
                    await client.async_connect()
                except TascamError as err:
                    _LOGGER.debug("Cannot connect to %s:%s: %s", host, port, err)
                    errors["base"] = "cannot_connect"
                except Exception:
                    _LOGGER.exception("Unexpected error while connecting to %s:%s", host, port)
                    errors["base"] = "unknown"
                else:
                    return self.async_create_entry(title=DEFAULT_NAME, data=data)
                finally:
                    await client.async_disconnect()

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(STEP_USER_DATA_SCHEMA, user_input),
            errors=errors,
        )
