"""Binary sensor platform for BWT Smart Dos DT Plus."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BINARY_STATUS_MESSAGES, DOMAIN
from .entity import BWTEntity


@dataclass(frozen=True)
class BWTBinarySensorEntityDescription(BinarySensorEntityDescription):
    """BWT binary description."""
    status_id: int = 0


BINARY_SENSOR_DESCRIPTIONS = tuple(
    BWTBinarySensorEntityDescription(
        key=f"status_{status_id}",
        translation_key=f"status_{status_id}",
        status_id=status_id,
    )
    for status_id in BINARY_STATUS_MESSAGES
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(BWTBinarySensor(coordinator, entry.entry_id, description) for description in BINARY_SENSOR_DESCRIPTIONS)


class BWTBinarySensor(BWTEntity, BinarySensorEntity):
    """BWT binary sensor."""

    entity_description: BWTBinarySensorEntityDescription
    _attr_device_class = "problem"

    def __init__(self, coordinator, entry_id: str, description: BWTBinarySensorEntityDescription) -> None:
        super().__init__(coordinator, entry_id, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        if not self.coordinator.data:
            return None
        active_states = self.coordinator.data.get("0201", {}).get("activeStates")
        if not isinstance(active_states, list):
            return None
        return self.entity_description.status_id in active_states
