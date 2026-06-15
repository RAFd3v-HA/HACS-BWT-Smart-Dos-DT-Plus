# BWT Smart Dos DT Plus

Home Assistant custom integration for the local HTTP API of the BWT Smart Dos DT Plus.

Version: **0.1.7**

## Polling intervals

- Endpoint `0201` for Status and Fehlerstatus: every **10 seconds**
- Endpoints `0104`, `0402`, `0503`, `0505`: every **120 seconds**
- Endpoints `0202`, `0208`, `0401`: every **600 seconds**

Firmware, hardware, uptime and operating time are part of the same `0201`
response as the status. They therefore arrive with the 10-second response
without any additional API request.

## Changes in 0.1.7

- Renamed `Aktive Meldung` to `Status`.
- Renamed `Fehler` to `Fehlerstatus`.
- Changed the former static endpoint refresh interval to 600 seconds.
- Added EAN fallback for Wirkstofftyp:
  `9022000010354` is displayed as `L1/LE`.
- Existing entity IDs and unique IDs remain unchanged.

## Main sensor section

- Status
- Fehlerstatus
- Gesamtwasser
- Restvolumen in ml
- Restvolumen in %
- Restvolumen in Tagen

## Diagnostics

Technical and metadata values remain under Diagnostics.

## Update

Replace the repository contents, redownload the integration in HACS and
restart Home Assistant completely. Confirm that `manifest.json` contains
version `0.1.7`.
