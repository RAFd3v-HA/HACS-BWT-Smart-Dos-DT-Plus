"""Constants for BWT Smart Dos DT Plus."""
from __future__ import annotations

from datetime import timedelta

DOMAIN = "bwt_smartdos"
DEFAULT_PORT = 80

STATUS_SCAN_INTERVAL = timedelta(seconds=10)
DATA_SCAN_INTERVAL_SECONDS = 120
STATIC_SCAN_INTERVAL_SECONDS = 600

CONF_IP = "ip"
CONF_PORT = "port"

MANUFACTURER = "BWT"
MODEL = "Smart Dos DT Plus"
VALUE_NOT_PROVIDED = "Nicht von API geliefert"
EMPTY_DISPLAY_STATE = "\u200b"

ENDPOINT_WIFI = "0104"
ENDPOINT_DEVICE = "0201"
ENDPOINT_CONFIG = "0202"
ENDPOINT_TIME = "0208"
ENDPOINT_POUCH = "0401"
ENDPOINT_REMAINING = "0402"
ENDPOINT_FLOW = "0503"
ENDPOINT_DOSED = "0505"

FAST_ENDPOINTS = (
    ENDPOINT_DEVICE,
)

DATA_ENDPOINTS = (
    ENDPOINT_WIFI,
    ENDPOINT_REMAINING,
    ENDPOINT_FLOW,
    ENDPOINT_DOSED,
)

STATIC_ENDPOINTS = (
    ENDPOINT_CONFIG,
    ENDPOINT_TIME,
    ENDPOINT_POUCH,
)

STATUS_MESSAGES: dict[int, str] = {
    2001: "Standby",
    2002: "Dosierung aktiv",
    7001: "Mineralstoffbehälter niedrig",
    7002: "Mineralstoffbehälter leer",
    7003: "Wirkstoff läuft bald ab",
    7004: "Wirkstoff abgelaufen",
    7005: "AQA Volume Alarm",
    7006: "AQA Watch Alarm",
    7007: "AQA MaxFlow Alarm",
    8001: "Pumpenfehler",
    8002: "Pumpen Stromfehler",
    8003: "Pumpen Steuerungsfehler",
}

ERROR_STATUS_MESSAGES: dict[int, str] = {
    status_id: text
    for status_id, text in STATUS_MESSAGES.items()
    if status_id >= 7000
}

MINERAL_TYPES: dict[int, str] = {
    1: "L1/LE",
    2: "L2/L3",
    3: "L4",
    4: "CU2",
    5: "Spüllösung",
}

MINERAL_TYPES_BY_EAN: dict[int, str] = {
    9022000010354: "L1/LE",
}

DEPRECATED_SENSOR_KEYS = {
    "mineral_valid_date",
    "wifi_name",
    "status",
    "errors",
}

DEPRECATED_BINARY_SENSOR_KEYS = {
    "error_active",
    "status_7001",
    "status_7002",
    "status_7003",
    "status_7004",
    "status_7005",
    "status_7006",
    "status_7007",
    "status_8001",
    "status_8002",
    "status_8003",
}
