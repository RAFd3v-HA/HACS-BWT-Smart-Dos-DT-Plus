"""BWT Smart Dos DT Plus integration."""
from __future__ import annotations

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import entity_registry as er

from .const import (
    CONF_IP,
    CONF_PORT,
    DEFAULT_PORT,
    DEPRECATED_BINARY_SENSOR_KEYS,
    DEPRECATED_SENSOR_KEYS,
    DOMAIN,
)
from .coordinator import BWTDataCoordinator

PLATFORMS = ["sensor", "binary_sensor"]


def _remove_deprecated_entities(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> None:
    """Remove obsolete entities from older test versions."""
    registry = er.async_get(hass)

    deprecated = {
        "sensor": DEPRECATED_SENSOR_KEYS,
        "binary_sensor": DEPRECATED_BINARY_SENSOR_KEYS,
    }

    for entity_domain, keys in deprecated.items():
        for key in keys:
            unique_id = f"{entry.entry_id}_{key}"
            entity_id = registry.async_get_entity_id(
                entity_domain,
                DOMAIN,
                unique_id,
            )
            if entity_id is not None:
                registry.async_remove(entity_id)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up integration services."""
    hass.data.setdefault(DOMAIN, {})

    async def async_reload_service(call: ServiceCall) -> None:
        """Reload one or all config entries."""
        entry_id = call.data.get("entry_id")
        entries = hass.config_entries.async_entries(DOMAIN)

        if entry_id:
            entries = [
                entry
                for entry in entries
                if entry.entry_id == entry_id
            ]
            if not entries:
                raise HomeAssistantError(
                    "No BWT Smart Dos config entry found for "
                    f"entry_id {entry_id}"
                )

        for entry in entries:
            await hass.config_entries.async_reload(entry.entry_id)

    if not hass.services.has_service(DOMAIN, "reload"):
        hass.services.async_register(
            DOMAIN,
            "reload",
            async_reload_service,
            schema=vol.Schema({vol.Optional("entry_id"): str}),
        )

    return True


async def async_migrate_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Migrate old test entries and remove obsolete entities."""
    if entry.version < 4:
        _remove_deprecated_entities(hass, entry)
        hass.config_entries.async_update_entry(entry, version=4)

    return True


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Set up from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Also run cleanup here so users upgrading directly from a test build
    # do not need to delete obsolete entities manually.
    _remove_deprecated_entities(hass, entry)

    coordinator = BWTDataCoordinator(
        hass,
        entry.data[CONF_IP],
        entry.data.get(CONF_PORT, DEFAULT_PORT),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(
        entry,
        PLATFORMS,
    )
    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(
        entry,
        PLATFORMS,
    )

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok
