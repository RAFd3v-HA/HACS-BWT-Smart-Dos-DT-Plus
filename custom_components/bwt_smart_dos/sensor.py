from homeassistant.components.sensor import (
    SensorEntity,
    SensorDeviceClass,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfVolume,
    UnitOfTime,
    PERCENTAGE,
)
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, STATUS_CODES


SENSORS = [
    {
        "key": "fwRev",
        "name": "Firmware",
    },
    {
        "key": "hwRev",
        "name": "Hardware Revision",
    },
    {
        "key": "dosingRate",
        "name": "Dosierrate",
        "unit": "ml/m³",
    },
    {
        "key": "remCapacity",
        "name": "Restvolumen",
        "unit": UnitOfVolume.MILLILITERS,
        "device_class": SensorDeviceClass.VOLUME,
    },
    {
        "key": "remCapacityPct",
        "name": "Restvolumen Prozent",
        "unit": PERCENTAGE,
    },
    {
        "key": "remCapacityDays",
        "name": "Resttage",
        "unit": UnitOfTime.DAYS,
        "device_class": SensorDeviceClass.DURATION,
    },
    {
        "key": "totCap",
        "name": "Pouchvolumen",
        "unit": UnitOfVolume.MILLILITERS,
        "device_class": SensorDeviceClass.VOLUME,
    },
    {
        "key": "dosedMineral",
        "name": "Dosierte Menge",
        "unit": UnitOfVolume.MILLILITERS,
        "device_class": SensorDeviceClass.VOLUME,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
]


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    entities.append(BwtStatusSensor(coordinator))
    entities.append(BwtActiveStatesSensor(coordinator))
    entities.append(BwtTotalWaterSensor(coordinator))

    for sensor in SENSORS:
        entities.append(BwtSensor(coordinator, sensor))

    async_add_entities(entities)


class BaseEntity(CoordinatorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def device_info(self):
        fw = self.coordinator.data["0201"].get("fwRev", "unknown")

        return DeviceInfo(
            identifiers={(DOMAIN, self.coordinator.host)},
            name="BWT Smart Dos DT Plus",
            manufacturer="BWT",
            model="Smart Dos DT Plus",
            sw_version=fw,
        )


class BwtSensor(BaseEntity, SensorEntity):
    def __init__(self, coordinator, description):
        super().__init__(coordinator)

        self.description = description

        self._attr_name = f"BWT {description['name']}"
        self._attr_unique_id = f"bwt_{description['key']}"

        self._attr_native_unit_of_measurement = (
            description.get("unit")
        )

        self._attr_device_class = (
            description.get("device_class")
        )

        self._attr_state_class = (
            description.get("state_class")
        )

    @property
    def native_value(self):
        key = self.description["key"]

        for section in self.coordinator.data.values():
            if key in section:
                return section[key]

        return None


class BwtStatusSensor(BaseEntity, SensorEntity):
    _attr_name = "BWT Status"
    _attr_unique_id = "bwt_status"

    @property
    def native_value(self):
        code = self.coordinator.data["0201"].get("devState")

        return STATUS_CODES.get(code, f"Unknown ({code})")


class BwtActiveStatesSensor(BaseEntity, SensorEntity):
    _attr_name = "BWT Aktive Statusmeldungen"
    _attr_unique_id = "bwt_active_states"

    @property
    def native_value(self):
        states = self.coordinator.data["0201"].get(
            "activeStates",
            [],
        )

        if not states:
            return "Keine"

        return ", ".join(
            STATUS_CODES.get(code, str(code))
            for code in states
        )


class BwtTotalWaterSensor(BaseEntity, SensorEntity):
    _attr_name = "BWT Aufbereitetes Wasser"
    _attr_unique_id = "bwt_total_water"

    _attr_native_unit_of_measurement = UnitOfVolume.LITERS
    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    @property
    def native_value(self):
        try:
            value_ml = self.coordinator.data["0503"]["flow"]["1"][
                "totFlow"
            ]

            return round(value_ml / 1000, 2)

        except Exception:
            return None
