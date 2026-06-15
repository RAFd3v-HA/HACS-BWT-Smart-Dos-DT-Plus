"""Binary sensor platform for BWT Smart Dos DT Plus."""
from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BINARY_STATUS_MESSAGES, DOMAIN
from .coordinator import BWTDataCoordinator
from .entity import BWTEntity


@dataclass(frozen=True, kw_only=True)
class BWTBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describe a BWT binary sensor."""

    status_id: int


BINARY_SENSOR_DESCRIPTIONS: tuple[BWTBinarySensorEntityDescription, ...] = tuple(
    BWTBinarySensorEntityDescription(
        key=f"status_{status_id}",
        translation_key=f"status_{status_id}",
        status_id=status_id,
        device_class=BinarySensorDeviceClass.PROBLEM,
    )
    for status_id in BINARY_STATUS_MESSAGES
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up BWT binary sensors."""
    coordinator: BWTDataCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        BWTBinarySensor(coordinator, entry.entry_id, description)
        for description in BINARY_SENSOR_DESCRIPTIONS
    )


class BWTBinarySensor(BWTEntity, BinarySensorEntity):
    """BWT binary sensor."""

    entity_description: BWTBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: BWTDataCoordinator,
        entry_id: str,
        description: BWTBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, entry_id, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return true if the status ID is active."""
        if not self.coordinator.data:
            return None

        active_states = self.coordinator.data.get("0201", {}).get("activeStates")
        if not isinstance(active_states, list):
            return None

        return self.entity_description.status_id in active_states
