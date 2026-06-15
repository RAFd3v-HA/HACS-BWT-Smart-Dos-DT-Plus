"""Config flow for BWT Smart Dos DT Plus."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_IP, CONF_PORT
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import BWTApi, BWTApiConnectionError, BWTApiError, BWTApiResponseError
from .const import DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)


class BWTConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BWT Smart Dos DT Plus."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            ip = user_input[CONF_IP].strip()
            port = DEFAULT_PORT

            session = async_get_clientsession(self.hass)
            api = BWTApi(session, ip, port)

            try:
                validation = await api.async_validate()
            except BWTApiConnectionError:
                errors["base"] = "cannot_connect"
            except BWTApiResponseError:
                errors["base"] = "invalid_response"
            except BWTApiError:
                errors["base"] = "unknown"
            except Exception:
                _LOGGER.exception("Unexpected error while validating BWT Smart Dos connection")
                errors["base"] = "unknown"
            else:
                device = validation.get("0201", {})
                wifi = validation.get("0104", {})
                unique_id = device.get("iotDevId") or wifi.get("mac") or ip
                await self.async_set_unique_id(str(unique_id))
                self._abort_if_unique_id_configured(updates={CONF_IP: ip, CONF_PORT: port})

                title = device.get("productCode") or f"BWT Smart Dos {ip}"
                return self.async_create_entry(
                    title=str(title),
                    data={CONF_IP: ip, CONF_PORT: port},
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_IP): str}),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """No options flow yet."""
        return None
