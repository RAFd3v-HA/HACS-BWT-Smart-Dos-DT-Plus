DOMAIN = "bwt_smart_dos"

SCAN_INTERVAL = 30

UUIDS = [
    "0104",
    "0201",
    "0202",
    "0208",
    "0401",
    "0402",
    "0503",
    "0505",
]

STATUS_CODES = {
    2001: "Standby",
    2002: "Dosierung aktiv",
    7001: "Füllstand Mineralstoffbehälter niedrig!",
    7002: "Mineralstoffbehälter leer!",
    7003: "Mineralstoff läuft bald ab!",
    7004: "Mineralstoff abgelaufen!",
    7005: "AQA Volume Alarm",
    7006: "AQA Watch Alarm",
    7007: "AQA MaxFlow Alarm",
    8001: "Pumpenfehler",
    8002: "Pumpen Stromfehler",
    8003: "Pumpen Steuerungsfehler",
}
