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


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        BwtStatusSensor(coordinator),
        BwtActiveStatesSensor(coordinator),
        BwtTotalWaterSensor(coordinator),
        BwtRemainingCapacitySensor(coordinator),
        BwtRemainingCapacityPercentSensor(coordinator),
        BwtRemainingDaysSensor(coordinator),
        BwtPouchVolumeSensor(coordinator),
        BwtExpirationDateSensor(coordinator),
        BwtProductionDateSensor(coordinator),
        BwtBatchNumberSensor(coordinator),
    ]

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
            value_ml = self.coordinator.data["0503"]["flow"]["1"]["totFlow"]
            return round(value_ml / 1000, 2)
        except Exception:
            return None


class BwtRemainingCapacitySensor(BaseEntity, SensorEntity):
    _attr_name = "BWT Restvolumen"
    _attr_unique_id = "bwt_rem_capacity"

    _attr_native_unit_of_measurement = UnitOfVolume.MILLILITERS
    _attr_device_class = SensorDeviceClass.VOLUME

    @property
    def native_value(self):
        try:
            return round(
                self.coordinator.data["0402"]["1"]["remCapacity"],
                2,
            )
        except Exception:
            return None


class BwtRemainingCapacityPercentSensor(BaseEntity, SensorEntity):
    _attr_name = "BWT Restvolumen Prozent"
    _attr_unique_id = "bwt_rem_capacity_pct"

    _attr_native_unit_of_measurement = PERCENTAGE

    @property
    def native_value(self):
        try:
            return self.coordinator.data["0402"]["1"]["remCapacityPct"]
        except Exception:
            return None


class BwtRemainingDaysSensor(BaseEntity, SensorEntity):
    _attr_name = "BWT Resttage"
    _attr_unique_id = "bwt_rem_days"

    _attr_native_unit_of_measurement = UnitOfTime.DAYS
    _attr_device_class = SensorDeviceClass.DURATION

    @property
    def native_value(self):
        try:
            return self.coordinator.data["0402"]["1"]["remCapacityDays"]
        except Exception:
            return None


class BwtPouchVolumeSensor(BaseEntity, SensorEntity):
    _attr_name = "BWT Pouchvolumen"
    _attr_unique_id = "bwt_tot_cap"

    _attr_native_unit_of_measurement = UnitOfVolume.MILLILITERS
    _attr_device_class = SensorDeviceClass.VOLUME

    @property
    def native_value(self):
        try:
            return self.coordinator.data["0401"]["1"]["totCap"]
        except Exception:
            return None


class BwtExpirationDateSensor(BaseEntity, SensorEntity):
    _attr_name = "BWT Ablaufdatum"
    _attr_unique_id = "bwt_exp_date"

    @property
    def native_value(self):
        try:
            return self.coordinator.data["0401"]["1"]["expDate"]
        except Exception:
            return None


class BwtProductionDateSensor(BaseEntity, SensorEntity):
    _attr_name = "BWT Produktionsdatum"
    _attr_unique_id = "bwt_valid_date"

    @property
    def native_value(self):
        try:
            return self.coordinator.data["0401"]["1"]["validDate"]
        except Exception:
            return None


class BwtBatchNumberSensor(BaseEntity, SensorEntity):
    _attr_name = "BWT Batchnummer"
    _attr_unique_id = "bwt_batch_nr"

    @property
    def native_value(self):
        try:
            return self.coordinator.data["0401"]["1"]["batchNr"]
        except Exception:
            return None
