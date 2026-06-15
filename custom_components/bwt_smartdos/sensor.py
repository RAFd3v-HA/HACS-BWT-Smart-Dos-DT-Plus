"""Sensor platform for BWT Smart Dos DT Plus."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .entity import BWTEntity
from .helpers import (
    active_states_text,
    first_pouch,
    iso_date,
    meaningful_number_text,
    mineral_type_text,
    parse_float,
    parse_int,
    round_or_none,
    seconds_to_days,
    seconds_to_hhmm,
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
    # ------------------------------------------------------------------
    # Primary entities: shown in the main "Sensors" section.
    # ------------------------------------------------------------------
    BWTSensorEntityDescription(
        key="active_messages",
        translation_key="active_messages",
        value_fn=lambda d: active_states_text(
            d.get("0201", {}).get("activeStates")
        ),
    ),
    BWTSensorEntityDescription(
        key="total_water",
        translation_key="total_water",
        native_unit_of_measurement="l",
        state_class=SensorStateClass.TOTAL_INCREASING,
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

    # ------------------------------------------------------------------
    # Diagnostic entities: shown in the "Diagnostics" section.
    # ------------------------------------------------------------------
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
        value_fn=lambda d: seconds_to_hhmm(
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


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up BWT sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        BWTSensor(coordinator, entry.entry_id, description)
        for description in SENSOR_DESCRIPTIONS
    )


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
