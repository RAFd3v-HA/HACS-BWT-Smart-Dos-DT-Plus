"""Diagnostics support for BWT Smart Dos DT Plus."""
from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


TO_REDACT = {
    "ssid",
    "ip",
    "sn",
    "sg",
    "pDns",
    "sDns",
    "mac",
    "iotDevId",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    def redact(value: Any) -> Any:
        if isinstance(value, dict):
            return {key: ("**REDACTED**" if key in TO_REDACT else redact(item)) for key, item in value.items()}
        if isinstance(value, list):
            return [redact(item) for item in value]
        return value

    return {
        "entry": {
            "title": entry.title,
            "data": redact(dict(entry.data)),
        },
        "last_data": redact(coordinator.data or {}),
    }
