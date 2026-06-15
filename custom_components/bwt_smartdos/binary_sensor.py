"""Binary sensor platform for BWT Smart Dos DT Plus."""
from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BWTEntity
from .helpers import error_states_text, has_error_state


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the single problem binary sensor."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [BWTErrorBinarySensor(coordinator, entry.entry_id)]
    )


class BWTErrorBinarySensor(BWTEntity, BinarySensorEntity):
    """Show whether the BWT device reports a warning or error."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_translation_key = "error_active"

    def __init__(self, coordinator, entry_id: str) -> None:
        """Initialize the error binary sensor."""
        super().__init__(coordinator, entry_id, "error_active")

    @property
    def is_on(self) -> bool | None:
        """Return true when at least one warning/error status is active."""
        if not self.coordinator.data:
            return None
        return has_error_state(
            self.coordinator.data
            .get("0201", {})
            .get("activeStates")
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose the exact clear-text warning/error messages."""
        if not self.coordinator.data:
            return {}

        error_text = error_states_text(
            self.coordinator.data
            .get("0201", {})
            .get("activeStates")
        )

        return {
            "aktive_fehler": (
                "Keine"
                if error_text in (None, "OK")
                else error_text
            )
        }
