# BWT Smart Dos DT Plus

Home Assistant custom integration for the local HTTP API of the BWT Smart Dos DT Plus.

Version: **0.1.4**

## Changes in 0.1.4

- Removed the `WLAN Name` sensor because endpoint `0104.ssid` returns `null`.
- Automatically removes the old `WLAN Name` entity from the entity registry.
- Keeps `WLAN Signal` and `MAC-Adresse`.

## Changes in 0.1.3

- Automatically removes obsolete alarm binary sensors from older test builds.
- Automatically removes the obsolete `Wirkstoff Haltbarkeitsdatum` entity.
- Makes pouch selection from endpoint `0401` robust against different object keys.
- Retries incomplete `0401` data every 120 seconds until the device supplies a valid batch number, order number, or active substance ID.
- Displays `Nicht von API geliefert` instead of `0` or `Unbekannt` for missing metadata.
- Bestellnummer uses `0401.*.orderNr`.
- Chargennummer uses `0401.*.batchNr`.
- Wirkstofftyp uses `0401.*.id`.

## Important API behavior

The provided API example contains:

```json
{
  "ssid": null
}
```

Therefore no real WLAN name can be displayed until the device itself supplies `ssid`.

The provided pouch example contains:

```json
{
  "orderNr": 0,
  "batchNr": 9650,
  "id": 1
}
```

This means:

- Bestellnummer: not supplied by the device
- Chargennummer: `9650`
- Wirkstofftyp: `L1/LE`

## Installation/update

Delete the existing contents of:

```text
/config/custom_components/bwt_smartdos
```

Copy the new `custom_components/bwt_smartdos` folder into place and restart Home Assistant completely.

When using HACS:

1. Replace the repository contents on GitHub.
2. In HACS choose **Redownload** for the integration.
3. Restart Home Assistant.
4. Confirm that `manifest.json` shows version `0.1.3`.

The integration will remove obsolete entities during the first setup after the update.
