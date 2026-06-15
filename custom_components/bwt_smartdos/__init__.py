"""BWT Smart Dos DT Plus integration."""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError

from .const import CONF_IP, CONF_PORT, DEFAULT_PORT, DOMAIN
from .coordinator import BWTDataCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor", "binary_sensor"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up services."""
    hass.data.setdefault(DOMAIN, {})

    async def async_reload_service(call: ServiceCall) -> None:
        entry_id = call.data.get("entry_id")
        entries = hass.config_entries.async_entries(DOMAIN)

        if entry_id:
            entries = [entry for entry in entries if entry.entry_id == entry_id]
            if not entries:
                raise HomeAssistantError(f"No BWT Smart Dos config entry found for entry_id {entry_id}")

        for entry in entries:
            await hass.config_entries.async_reload(entry.entry_id)

    hass.services.async_register(
        DOMAIN,
        "reload",
        async_reload_service,
        schema=vol.Schema({vol.Optional("entry_id"): str}),
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = BWTDataCoordinator(
        hass,
        entry.data[CONF_IP],
        entry.data.get(CONF_PORT, DEFAULT_PORT),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
