"""Sensor platform for BWT Smart Dos DT Plus."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Self

from homeassistant.components.sensor import (
    RestoreSensor,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorExtraStoredData,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfVolume
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import DOMAIN
from .entity import BWTEntity
from .helpers import (
    active_error_messages_text,
    active_warning_text,
    first_pouch,
    iso_date,
    meaningful_number_text,
    mineral_type_text,
    parse_float,
    parse_int,
    round_or_none,
    seconds_to_days,
    seconds_to_uptime_display,
    status_text,
    text_or_not_provided,
    total_flow_litres,
)


@dataclass(frozen=True)
class BWTSensorEntityDescriptionMixin:
    """Mixin containing the value callback."""

    value_fn: Callable[[dict[str, Any]], Any]


@dataclass(frozen=True)
class BWTSensorEntityDescription(
    SensorEntityDescription,
    BWTSensorEntityDescriptionMixin,
):
    """BWT sensor entity description."""


@dataclass
class BWTPeriodSensorExtraStoredData(SensorExtraStoredData):
    """Stored data for a period water-consumption sensor."""

    baseline_total: Decimal | None
    period_id: str | None

    def as_dict(self) -> dict[str, Any]:
        """Return stored data as a dictionary."""
        data = super().as_dict()
        data["baseline_total"] = (
            str(self.baseline_total)
            if self.baseline_total is not None
            else None
        )
        data["period_id"] = self.period_id
        return data

    @classmethod
    def from_dict(
        cls,
        restored: dict[str, Any],
    ) -> Self | None:
        """Restore stored period sensor data."""
        extra = SensorExtraStoredData.from_dict(restored)
        if extra is None:
            return None

        try:
            baseline_total = (
                Decimal(str(restored["baseline_total"]))
                if restored.get("baseline_total") is not None
                else None
            )
        except (InvalidOperation, TypeError, ValueError):
            return None

        return cls(
            extra.native_value,
            extra.native_unit_of_measurement,
            baseline_total,
            restored.get("period_id"),
        )


@dataclass
class BWTDosageSensorExtraStoredData(SensorExtraStoredData):
    """Stored data for the calculated active-substance dosage sensor."""

    baseline_water_l: Decimal | None
    baseline_remaining_ml: Decimal | None

    def as_dict(self) -> dict[str, Any]:
        """Return stored data as a dictionary."""
        data = super().as_dict()
        data["baseline_water_l"] = (
            str(self.baseline_water_l)
            if self.baseline_water_l is not None
            else None
        )
        data["baseline_remaining_ml"] = (
            str(self.baseline_remaining_ml)
            if self.baseline_remaining_ml is not None
            else None
        )
        return data

    @classmethod
    def from_dict(
        cls,
        restored: dict[str, Any],
    ) -> Self | None:
        """Restore stored dosing-calculation data."""
        extra = SensorExtraStoredData.from_dict(restored)
        if extra is None:
            return None

        try:
            baseline_water_l = (
                Decimal(str(restored["baseline_water_l"]))
                if restored.get("baseline_water_l") is not None
                else None
            )
            baseline_remaining_ml = (
                Decimal(str(restored["baseline_remaining_ml"]))
                if restored.get("baseline_remaining_ml") is not None
                else None
            )
        except (InvalidOperation, TypeError, ValueError):
            return None

        return cls(
            extra.native_value,
            extra.native_unit_of_measurement,
            baseline_water_l,
            baseline_remaining_ml,
        )


def _static(
    data: dict[str, Any],
    endpoint: str,
) -> dict[str, Any]:
    """Return one static endpoint."""
    return data.get("static", {}).get(endpoint, {})


def _pouch_static(data: dict[str, Any]) -> dict[str, Any]:
    """Return the best populated pouch object."""
    return first_pouch(_static(data, "0401"))


SENSOR_DESCRIPTIONS = (
    # --------------------------------------------------------------
    # Primary entities.
    # --------------------------------------------------------------
    BWTSensorEntityDescription(
        key="active_messages",
        translation_key="active_messages",
        value_fn=lambda d: status_text(
            d.get("0201", {}).get("devState")
        ),
    ),
    BWTSensorEntityDescription(
        key="active_errors",
        translation_key="active_errors",
        value_fn=lambda d: active_error_messages_text(
            d.get("0201", {}).get("activeStates")
        ),
    ),
    BWTSensorEntityDescription(
        key="active_warning",
        translation_key="active_warning",
        value_fn=lambda d: active_warning_text(
            first_pouch(d.get("0402")).get("remCapacityPct")
        ),
    ),
    BWTSensorEntityDescription(
        key="total_water",
        translation_key="total_water",
        native_unit_of_measurement=UnitOfVolume.LITERS,
        device_class=SensorDeviceClass.WATER,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=1,
        value_fn=lambda d: total_flow_litres(d.get("0503")),
    ),
    BWTSensorEntityDescription(
        key="remaining_volume_ml",
        translation_key="remaining_volume_ml",
        native_unit_of_measurement="ml",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: round_or_none(
            first_pouch(d.get("0402")).get("remCapacity"),
            1,
        ),
    ),
    BWTSensorEntityDescription(
        key="remaining_volume_percent",
        translation_key="remaining_volume_percent",
        native_unit_of_measurement="%",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: parse_int(
            first_pouch(d.get("0402")).get("remCapacityPct")
        ),
    ),
    BWTSensorEntityDescription(
        key="remaining_volume_days",
        translation_key="remaining_volume_days",
        native_unit_of_measurement="d",
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=lambda d: parse_int(
            first_pouch(d.get("0402")).get("remCapacityDays")
        ),
    ),

    # --------------------------------------------------------------
    # Diagnostic entities.
    # --------------------------------------------------------------
    BWTSensorEntityDescription(
        key="wifi_signal",
        translation_key="wifi_signal",
        native_unit_of_measurement="dBm",
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: parse_float(
            d.get("0104", {}).get("rssiAvg")
            if d.get("0104", {}).get("rssiAvg") is not None
            else d.get("0104", {}).get("rssi")
        ),
    ),
    BWTSensorEntityDescription(
        key="uptime_reboot",
        translation_key="uptime_reboot",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: seconds_to_uptime_display(
            d.get("0201", {}).get("uptime")
        ),
    ),
    BWTSensorEntityDescription(
        key="operating_time",
        translation_key="operating_time",
        native_unit_of_measurement="d",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: seconds_to_days(
            d.get("0201", {}).get("operatingTime")
        ),
    ),
    BWTSensorEntityDescription(
        key="dosed_mineral",
        translation_key="dosed_mineral",
        native_unit_of_measurement="ml",
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: round_or_none(
            d.get("0505", {}).get("dosedMineral"),
            3,
        ),
    ),
    BWTSensorEntityDescription(
        key="firmware",
        translation_key="firmware",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: text_or_not_provided(
            d.get("0201", {}).get("fwRev")
        ),
    ),
    BWTSensorEntityDescription(
        key="hardware",
        translation_key="hardware",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: text_or_not_provided(
            d.get("0201", {}).get("hwRev")
        ),
    ),
    BWTSensorEntityDescription(
        key="product_code",
        translation_key="product_code",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: text_or_not_provided(
            d.get("0201", {}).get("productCode")
        ),
    ),
    BWTSensorEntityDescription(
        key="mac_address",
        translation_key="mac_address",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: text_or_not_provided(
            d.get("0104", {}).get("mac")
        ),
    ),
    BWTSensorEntityDescription(
        key="commissioning_date",
        translation_key="commissioning_date",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: iso_date(
            d.get("0201", {}).get("commDate")
        ),
    ),
    BWTSensorEntityDescription(
        key="pouch_volume",
        translation_key="pouch_volume",
        native_unit_of_measurement="ml",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: parse_int(
            _pouch_static(d).get("totCap")
        ),
    ),
    BWTSensorEntityDescription(
        key="order_number",
        translation_key="order_number",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: meaningful_number_text(
            _pouch_static(d).get("orderNr")
        ),
    ),
    BWTSensorEntityDescription(
        key="batch_number",
        translation_key="batch_number",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: meaningful_number_text(
            _pouch_static(d).get("batchNr")
        ),
    ),
    BWTSensorEntityDescription(
        key="mineral_type",
        translation_key="mineral_type",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: mineral_type_text(
            _pouch_static(d).get("id"),
            _pouch_static(d).get("ean"),
        ),
    ),
    BWTSensorEntityDescription(
        key="mineral_expiration_date",
        translation_key="mineral_expiration_date",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda d: text_or_not_provided(
            _pouch_static(d).get("expDate")
        ),
    ),
)


PERIOD_SENSOR_KEYS = (
    ("daily_water", "daily"),
    ("monthly_water", "monthly"),
    ("yearly_water", "yearly"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up BWT sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [
        BWTSensor(coordinator, entry.entry_id, description)
        for description in SENSOR_DESCRIPTIONS
    ]
    entities.extend(
        BWTPeriodWaterSensor(
            coordinator,
            entry.entry_id,
            key,
            period,
        )
        for key, period in PERIOD_SENSOR_KEYS
    )
    entities.append(
        BWTDosageSensor(
            coordinator,
            entry.entry_id,
        )
    )

    async_add_entities(entities)


class BWTSensor(BWTEntity, SensorEntity):
    """BWT sensor."""

    entity_description: BWTSensorEntityDescription

    def __init__(
        self,
        coordinator,
        entry_id: str,
        description: BWTSensorEntityDescription,
    ) -> None:
        """Initialize sensor."""
        super().__init__(
            coordinator,
            entry_id,
            description.key,
        )
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        """Return the sensor value."""
        if not self.coordinator.data:
            return None
        return self.entity_description.value_fn(
            self.coordinator.data
        )


class BWTPeriodWaterSensor(BWTEntity, RestoreSensor):
    """Water consumption within the current calendar period."""

    _attr_device_class = SensorDeviceClass.WATER
    _attr_native_unit_of_measurement = UnitOfVolume.LITERS
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_suggested_display_precision = 1

    def __init__(
        self,
        coordinator,
        entry_id: str,
        key: str,
        period: str,
    ) -> None:
        """Initialize the period water sensor."""
        super().__init__(coordinator, entry_id, key)
        self._attr_translation_key = key
        self._period = period
        self._period_id: str | None = None
        self._baseline_total: Decimal | None = None
        self._attr_native_value: Decimal | None = None

    def _current_period_id(self) -> str:
        """Return the current local calendar period identifier."""
        now = dt_util.now()

        if self._period == "daily":
            return now.date().isoformat()
        if self._period == "monthly":
            return now.strftime("%Y-%m")
        return now.strftime("%Y")

    def _current_total(self) -> Decimal | None:
        """Return the lifetime total-water value as Decimal."""
        if not self.coordinator.data:
            return None

        total = total_flow_litres(
            self.coordinator.data.get("0503")
        )
        if total is None:
            return None

        return Decimal(str(total))

    def _update_from_total(self, total: Decimal | None) -> None:
        """Update current-period consumption from the lifetime counter."""
        if total is None:
            return

        current_period = self._current_period_id()

        if self._period_id != current_period:
            self._period_id = current_period
            self._baseline_total = total
            self._attr_native_value = Decimal("0")
            return

        if self._baseline_total is None:
            self._baseline_total = total
            self._attr_native_value = Decimal("0")
            return

        if total < self._baseline_total:
            # The lifetime counter was reset or replaced.
            self._baseline_total = total
            self._attr_native_value = Decimal("0")
            return

        self._attr_native_value = (
            total - self._baseline_total
        ).quantize(Decimal("0.001"))

    async def async_added_to_hass(self) -> None:
        """Restore period baseline and current value."""
        await super().async_added_to_hass()

        restored = await self.async_get_last_sensor_data()
        current_period = self._current_period_id()
        current_total = self._current_total()

        if (
            restored is not None
            and restored.period_id == current_period
            and restored.baseline_total is not None
        ):
            self._period_id = restored.period_id
            self._baseline_total = restored.baseline_total

            if current_total is not None:
                self._update_from_total(current_total)
            else:
                try:
                    self._attr_native_value = Decimal(
                        str(restored.native_value)
                    )
                except (InvalidOperation, TypeError, ValueError):
                    self._attr_native_value = None
            return

        self._period_id = current_period
        self._baseline_total = current_total
        self._attr_native_value = (
            Decimal("0")
            if current_total is not None
            else None
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Update the period sensor after coordinator refresh."""
        self._update_from_total(self._current_total())
        super()._handle_coordinator_update()

    @property
    def extra_restore_state_data(
        self,
    ) -> BWTPeriodSensorExtraStoredData:
        """Return data needed to restore this period sensor."""
        return BWTPeriodSensorExtraStoredData(
            self.native_value,
            self.native_unit_of_measurement,
            self._baseline_total,
            self._period_id,
        )

    async def async_get_last_sensor_data(
        self,
    ) -> BWTPeriodSensorExtraStoredData | None:
        """Restore period sensor data."""
        restored = await self.async_get_last_extra_data()
        if restored is None:
            return None

        return BWTPeriodSensorExtraStoredData.from_dict(
            restored.as_dict()
        )

class BWTDosageSensor(BWTEntity, RestoreSensor):
    """Calculate active-substance dosage from counter differences."""

    _attr_translation_key = "calculated_dosage"
    _attr_native_unit_of_measurement = "ml/m³"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 2

    def __init__(
        self,
        coordinator,
        entry_id: str,
    ) -> None:
        """Initialize the calculated dosage sensor."""
        super().__init__(
            coordinator,
            entry_id,
            "calculated_dosage",
        )
        self._baseline_water_l: Decimal | None = None
        self._baseline_remaining_ml: Decimal | None = None
        self._attr_native_value: Decimal | None = None
        self._last_water_delta_l: Decimal | None = None
        self._last_mineral_delta_ml: Decimal | None = None

    def _current_values(
        self,
    ) -> tuple[Decimal | None, Decimal | None]:
        """Return current total water and remaining mineral."""
        if not self.coordinator.data:
            return None, None

        total_water = total_flow_litres(
            self.coordinator.data.get("0503")
        )
        remaining = parse_float(
            first_pouch(
                self.coordinator.data.get("0402")
            ).get("remCapacity")
        )

        if total_water is None or remaining is None:
            return None, None

        return (
            Decimal(str(total_water)),
            Decimal(str(remaining)),
        )

    def _reset_baseline(
        self,
        total_water_l: Decimal,
        remaining_ml: Decimal,
    ) -> None:
        """Set a new calculation baseline."""
        self._baseline_water_l = total_water_l
        self._baseline_remaining_ml = remaining_ml

    def _update_calculation(
        self,
        total_water_l: Decimal | None,
        remaining_ml: Decimal | None,
    ) -> None:
        """Update dosage after a measurable mineral decrease."""
        if total_water_l is None or remaining_ml is None:
            return

        if (
            self._baseline_water_l is None
            or self._baseline_remaining_ml is None
        ):
            self._reset_baseline(total_water_l, remaining_ml)
            return

        # Counter reset or pouch replacement: start a fresh period.
        if (
            total_water_l < self._baseline_water_l
            or remaining_ml > self._baseline_remaining_ml
        ):
            self._reset_baseline(total_water_l, remaining_ml)
            return

        water_delta_l = total_water_l - self._baseline_water_l
        mineral_delta_ml = (
            self._baseline_remaining_ml - remaining_ml
        )

        # Accumulate until both a meaningful water amount and a measurable
        # mineral decrease are available. This avoids misleading zero values
        # and unstable division by very small water quantities.
        if water_delta_l < Decimal("1"):
            return
        if mineral_delta_ml <= Decimal("0"):
            return

        dosage = (
            mineral_delta_ml
            * Decimal("1000")
            / water_delta_l
        ).quantize(Decimal("0.01"))

        self._attr_native_value = dosage
        self._last_water_delta_l = water_delta_l.quantize(
            Decimal("0.001")
        )
        self._last_mineral_delta_ml = mineral_delta_ml.quantize(
            Decimal("0.001")
        )
        self._reset_baseline(total_water_l, remaining_ml)

    async def async_added_to_hass(self) -> None:
        """Restore the previous value and calculation baseline."""
        await super().async_added_to_hass()

        restored = await self.async_get_last_sensor_data()
        current_water, current_remaining = self._current_values()

        if restored is not None:
            self._baseline_water_l = restored.baseline_water_l
            self._baseline_remaining_ml = (
                restored.baseline_remaining_ml
            )

            try:
                self._attr_native_value = (
                    Decimal(str(restored.native_value))
                    if restored.native_value is not None
                    else None
                )
            except (InvalidOperation, TypeError, ValueError):
                self._attr_native_value = None

        if (
            self._baseline_water_l is None
            or self._baseline_remaining_ml is None
        ):
            if (
                current_water is not None
                and current_remaining is not None
            ):
                self._reset_baseline(
                    current_water,
                    current_remaining,
                )
            return

        self._update_calculation(
            current_water,
            current_remaining,
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Recalculate after coordinator updates."""
        total_water, remaining = self._current_values()
        self._update_calculation(total_water, remaining)
        super()._handle_coordinator_update()

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Expose differences used for the latest calculation."""
        attributes: dict[str, Any] = {}

        if self._last_water_delta_l is not None:
            attributes["berechnungsbasis_wasser_l"] = float(
                self._last_water_delta_l
            )
        if self._last_mineral_delta_ml is not None:
            attributes["verbrauchter_wirkstoff_ml"] = float(
                self._last_mineral_delta_ml
            )

        return attributes

    @property
    def extra_restore_state_data(
        self,
    ) -> BWTDosageSensorExtraStoredData:
        """Return data required to restore the calculation."""
        return BWTDosageSensorExtraStoredData(
            self.native_value,
            self.native_unit_of_measurement,
            self._baseline_water_l,
            self._baseline_remaining_ml,
        )

    async def async_get_last_sensor_data(
        self,
    ) -> BWTDosageSensorExtraStoredData | None:
        """Restore dosing sensor data."""
        restored = await self.async_get_last_extra_data()
        if restored is None:
            return None

        return BWTDosageSensorExtraStoredData.from_dict(
            restored.as_dict()
        )

