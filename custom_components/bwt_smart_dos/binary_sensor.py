from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, STATUS_CODES


ERROR_CODES = {
    7001,
    7002,
    7003,
    7004,
    7005,
    7006,
    7007,
    8001,
    8002,
    8003,
}


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for code in ERROR_CODES:
        entities.append(
            BwtErrorBinarySensor(
                coordinator,
                code,
                STATUS_CODES[code],
            )
        )

    async_add_entities(entities)


class BwtErrorBinarySensor(
    CoordinatorEntity,
    BinarySensorEntity,
):
    def __init__(self, coordinator, code, name):
        super().__init__(coordinator)

        self.code = code

        self._attr_name = f"BWT {name}"
        self._attr_unique_id = f"bwt_error_{code}"

    @property
    def is_on(self):
        states = self.coordinator.data["0201"].get(
            "activeStates",
            [],
        )

        return self.code in states

    @property
    def device_info(self):
        fw = self.coordinator.data["0201"].get(
            "fwRev",
            "unknown",
        )

        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.host)},
            name="BWT Smart Dos DT Plus",
            manufacturer="BWT",
            model="Smart Dos DT Plus",
            sw_version=fw,
        )
