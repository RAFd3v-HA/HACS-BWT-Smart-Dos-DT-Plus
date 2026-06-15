# BWT Smart Dos DT Plus

Home Assistant custom integration for the local HTTP API of the BWT Smart Dos DT Plus.

Version: **0.1.1**

## Changes in 0.1.1

- Fixed config flow handler loading.
- Removed fragile imports from `homeassistant.const`.
- Renamed config flow class to `ConfigFlow`.

## Installation

Copy this repository to:

```text
/config/custom_components/bwt_smartdos
```

Restart Home Assistant and add the integration via:

```text
Settings → Devices & services → Add integration → BWT Smart Dos DT Plus
```

## API

The integration reads:

- `0104`
- `0201`
- `0202`
- `0208`
- `0401`
- `0402`
- `0503`
- `0505`

The API port is fixed to **80**.

## Notes

- Dynamic values are refreshed every 120 seconds.
- Static values are read once on integration setup/reload.
- `commDate` is used as commissioning date.
- `validDate` is used as best-before date.
- `expDate` is used as active substance expiration date.
- Total water is converted from ml to l.
