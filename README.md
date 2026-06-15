# BWT Smart Dos DT Plus

Home Assistant custom integration for the local HTTP API of the BWT Smart Dos DT Plus.

Version: **0.1.6**

## Changes in 0.1.6

- `Gesamtbetriebszeit` is displayed in days instead of hours.
- `Betriebszeit seit Reboot` is displayed as elapsed `HH:MM`.
- The hours in `HH:MM` may exceed 23, for example `27:15`.

## Changes in 0.1.5

The device page is now deliberately grouped.

### Main sensor section

Only these entities are shown as primary entities:

- Aktive Meldung
- Fehler
- Gesamtwasser
- Restvolumen in ml
- Restvolumen in %
- Restvolumen in Tagen

`Fehler` is a Home Assistant problem binary sensor:

- Off: OK, shown with a check mark
- On: Problem, shown as a warning
- The exact active warning/error text is available in the
  `aktive_fehler` attribute

### Diagnostics section

All technical and metadata values are shown under Diagnostics:

- Bestellnummer
- Chargennummer
- Firmware
- Hardware
- Produktcode
- MAC-Adresse
- Inbetriebnahmedatum
- Pouchvolumen
- Wirkstofftyp
- Wirkstoff Ablaufdatum
- WLAN Signal
- Betriebszeit seit Reboot
- Gesamtbetriebszeit
- Dosierte Wirkstoffmenge

The duplicate `Status` and text-based `Fehler` entities from earlier
test versions are automatically removed from the entity registry.

## API limitations

When `orderNr` or `batchNr` is `0`, the device has not supplied a useful
number. In that case the integration displays `Nicht von API geliefert`.

## Update

Replace the repository contents, redownload the integration in HACS and
restart Home Assistant completely. Confirm that `manifest.json` contains
version `0.1.5`.
