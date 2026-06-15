# BWT Smart Dos DT Plus for Home Assistant

Version: **0.1.0**

Custom Home Assistant integration for the local HTTP API of a **BWT Smart Dos DT Plus**.

## Features

- Local polling via `http://<IP>:80/api/v1/gatt/<UUID>`
- Config Flow: only the IP address is requested
- Port is fixed to the API default: **80**
- Connection is validated during setup
- Dynamic values are refreshed every **120 seconds**
- Static values are read once when Home Assistant starts or the integration is reloaded
- Clear text status sensors, no raw status values
- Status ID binary sensors for documented warning/error states
- Reload service: `bwt_smartdos.reload`

## Dynamic sensors, refreshed every 120 seconds

| Sensor | Unit |
|---|---|
| WLAN Signal | dBm |
| Betriebszeit seit Reboot | h |
| Status | Text |
| Aktive Meldungen | Text |
| Restvolumen | ml |
| Restvolumen | % |
| Restvolumen | Tage |
| Gesamtwasser | l |
| Dosierte Wirkstoffmenge | ml |

## Static sensors, read on integration start/reload

| Sensor | Source |
|---|---|
| WLAN Name | `0104.ssid` |
| Firmware | `0201.fwRev` |
| Hardware | `0201.hwRev` |
| Produktcode | `0201.productCode` |
| MAC-Adresse | `0104.mac` |
| Inbetriebnahmedatum | `0201.commDate` |
| Pouchvolumen | `0401.1.totCap` |
| Bestellnummer | `0401.1.orderNr` |
| Chargennummer | `0401.1.batchNr` |
| Wirkstofftyp | `0401.1.id` |
| Wirkstoff Haltbarkeitsdatum | `0401.1.validDate` |
| Wirkstoff Ablaufdatum | `0401.1.expDate` |

Important: `commDate` is used as commissioning date. `validDate` is used as best-before date. `expDate` is used as active substance expiration date.

## Binary sensors

| Binary Sensor | Status ID |
|---|---:|
| Mineralstoffbehälter niedrig | 7001 |
| Mineralstoffbehälter leer | 7002 |
| Wirkstoff läuft bald ab | 7003 |
| Wirkstoff abgelaufen | 7004 |
| AQA Volume Alarm | 7005 |
| AQA Watch Alarm | 7006 |
| AQA MaxFlow Alarm | 7007 |
| Pumpenfehler | 8001 |
| Pumpen Stromfehler | 8002 |
| Pumpen Steuerungsfehler | 8003 |

## Installation for testing

### Manual

Copy this folder into your Home Assistant config directory:

```text
custom_components/bwt_smartdos
```

Restart Home Assistant, then add the integration via:

```text
Settings → Devices & services → Add integration → BWT Smart Dos DT Plus
```

### HACS custom repository

1. Upload this repository to GitHub.
2. In HACS, add it as a custom repository.
3. Category: Integration.
4. Install and restart Home Assistant.

## API endpoints used

- `0104` Wi-Fi information
- `0201` device information, uptime, status, active states, total flow/dosed lifetime values
- `0202` configuration/static settings
- `0208` device time/timezone
- `0401` pouch/static active substance data
- `0402` remaining capacity
- `0503` treated water
- `0505` dosed active substance

## Notes

- Total water is calculated from `0503.flow.*.totFlow`.
- The API value is in millilitres and is converted to litres.
- Dosed active substance is read from `0505.dosedMineral` and kept in ml.
