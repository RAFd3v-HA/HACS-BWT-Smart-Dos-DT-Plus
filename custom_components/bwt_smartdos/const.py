"""Constants for BWT Smart Dos DT Plus."""
from __future__ import annotations

from datetime import timedelta

DOMAIN = "bwt_smartdos"
DEFAULT_PORT = 80
SCAN_INTERVAL = timedelta(seconds=120)

CONF_IP = "ip"
CONF_PORT = "port"

MANUFACTURER = "BWT"
MODEL = "Smart Dos DT Plus"

ENDPOINT_WIFI = "0104"
ENDPOINT_DEVICE = "0201"
ENDPOINT_CONFIG = "0202"
ENDPOINT_TIME = "0208"
ENDPOINT_POUCH = "0401"
ENDPOINT_REMAINING = "0402"
ENDPOINT_FLOW = "0503"
ENDPOINT_DOSED = "0505"

DYNAMIC_ENDPOINTS = (
    ENDPOINT_WIFI,
    ENDPOINT_DEVICE,
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

BINARY_STATUS_MESSAGES: dict[int, str] = {
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

MINERAL_TYPES: dict[int, str] = {
    1: "L1/LE",
    2: "L2/L3",
    3: "L4",
    4: "CU2",
    5: "Spüllösung",
}
