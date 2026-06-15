"""Config flow for BWT Smart Dos DT Plus."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import BWTApi, BWTApiConnectionError, BWTApiResponseError
from .const import CONF_IP, CONF_PORT, DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BWT Smart Dos DT Plus."""

    VERSION = 4

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            ip = str(user_input[CONF_IP]).strip()
            api = BWTApi(async_get_clientsession(self.hass), ip, DEFAULT_PORT)

            try:
                validation = await api.async_validate()
            except BWTApiConnectionError:
                errors["base"] = "cannot_connect"
            except BWTApiResponseError:
                errors["base"] = "invalid_response"
            except Exception:
                _LOGGER.exception("Unexpected error during BWT Smart Dos config flow")
                errors["base"] = "unknown"
            else:
                device = validation.get("0201", {})
                wifi = validation.get("0104", {})
                unique_id = device.get("iotDevId") or wifi.get("mac") or ip

                await self.async_set_unique_id(str(unique_id))
                self._abort_if_unique_id_configured(updates={CONF_IP: ip, CONF_PORT: DEFAULT_PORT})

                title = f"BWT Smart Dos {ip}"
                if device.get("productCode"):
                    title = f"BWT Smart Dos {device['productCode']}"

                return self.async_create_entry(
                    title=title,
                    data={CONF_IP: ip, CONF_PORT: DEFAULT_PORT},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_IP): str}),
            errors=errors,
        )
