"""Base entity for BWT Smart Dos DT Plus."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL


class BWTEntity(CoordinatorEntity):
    """Base BWT entity."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry_id: str, key: str) -> None:
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._key = key
        self._attr_unique_id = f"{entry_id}_{key}"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        data = self.coordinator.data or {}
        device_data = data.get("0201", {})
        wifi_data = data.get("0104", {})

        identifier = device_data.get("iotDevId") or wifi_data.get("mac") or self.coordinator.api.ip

        return DeviceInfo(
            identifiers={(DOMAIN, str(identifier))},
            manufacturer=MANUFACTURER,
            model=MODEL,
            name="BWT Smart Dos DT Plus",
            sw_version=device_data.get("fwRev"),
            hw_version=device_data.get("hwRev"),
        )
