"""Binary sensor platform for BWT Smart Dos DT Plus."""
from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BWTEntity
from .helpers import has_error_state


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([BWTErrorActiveBinarySensor(coordinator, entry.entry_id)])


class BWTErrorActiveBinarySensor(BWTEntity, BinarySensorEntity):
    """Single problem binary sensor."""

    _attr_device_class = "problem"
    _attr_translation_key = "error_active"

    def __init__(self, coordinator, entry_id: str) -> None:
        super().__init__(coordinator, entry_id, "error_active")

    @property
    def is_on(self) -> bool | None:
        if not self.coordinator.data:
            return None
        return has_error_state(self.coordinator.data.get("0201", {}).get("activeStates"))
