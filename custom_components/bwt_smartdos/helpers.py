"""Helper functions for BWT Smart Dos DT Plus."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from .const import (
    EMPTY_DISPLAY_STATE,
    ERROR_STATUS_MESSAGES,
    MINERAL_TYPES,
    MINERAL_TYPES_BY_EAN,
    STATUS_MESSAGES,
    VALUE_NOT_PROVIDED,
)


def parse_float(value: Any) -> float | None:
    """Parse a float safely."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_int(value: Any) -> int | None:
    """Parse an integer safely."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def meaningful_number_text(value: Any) -> str:
    """Return a number as text, treating zero as not supplied."""
    parsed = parse_int(value)
    if parsed is None or parsed == 0:
        return VALUE_NOT_PROVIDED
    return str(parsed)


def text_or_not_provided(value: Any) -> str:
    """Return non-empty text or a clear fallback."""
    if value is None:
        return VALUE_NOT_PROVIDED
    text = str(value).strip()
    if not text or text.lower() in {"none", "null"}:
        return VALUE_NOT_PROVIDED
    return text


def _pouch_score(pouch: dict[str, Any]) -> int:
    """Score a pouch object so the most useful object can be selected."""
    score = 0

    if (parse_int(pouch.get("id")) or 0) > 0:
        score += 10
    if (parse_int(pouch.get("batchNr")) or 0) > 0:
        score += 8
    if (parse_int(pouch.get("orderNr")) or 0) > 0:
        score += 6
    if (parse_int(pouch.get("totCap")) or 0) > 0:
        score += 4
    if pouch.get("expDate"):
        score += 3
    if pouch.get("validDate"):
        score += 2

    return score


def first_pouch(data: dict[str, Any] | None) -> dict[str, Any]:
    """Return the most useful pouch object.

    Some firmware versions may use a key other than "1" or may return more
    than one pouch-like object. Selecting the best populated object is more
    robust than hard-coding one key.
    """
    if not isinstance(data, dict):
        return {}

    candidates = [value for value in data.values() if isinstance(value, dict)]
    if not candidates:
        return {}

    return max(candidates, key=_pouch_score)


def pouch_has_identity(data: dict[str, Any] | None) -> bool:
    """Return whether endpoint 0401 contains useful identity data."""
    pouch = first_pouch(data)
    return any(
        (
            (parse_int(pouch.get("id")) or 0) > 0,
            (parse_int(pouch.get("batchNr")) or 0) > 0,
            (parse_int(pouch.get("orderNr")) or 0) > 0,
        )
    )


def round_or_none(value: Any, digits: int) -> float | None:
    """Round a numeric value safely."""
    parsed = parse_float(value)
    if parsed is None:
        return None
    return round(parsed, digits)


def seconds_to_hhmm(value: Any) -> str | None:
    """Convert seconds to an elapsed HH:MM value.

    Hours are not limited to 23, so an uptime longer than one day is shown
    for example as 27:15.
    """
    seconds = parse_int(value)
    if seconds is None:
        return None

    total_minutes = max(0, seconds) // 60
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours:02d}:{minutes:02d}"


def seconds_to_days(value: Any) -> float | None:
    """Convert seconds to days."""
    seconds = parse_float(value)
    if seconds is None:
        return None
    return round(seconds / 86400, 2)


def status_text(value: Any) -> str | None:
    """Map a status ID to clear text."""
    status_id = parse_int(value)
    if status_id is None:
        return None
    return STATUS_MESSAGES.get(status_id, f"Unbekannter Status {status_id}")


def active_states_text(value: Any) -> str | None:
    """Return all active states as clear text."""
    if not isinstance(value, list):
        return None
    if not value:
        return "Keine aktive Meldung"
    return ", ".join(
        status_text(item) or f"Unbekannter Status {item}"
        for item in value
    )



def active_warning_text(value: Any) -> str | None:
    """Return a warning based on the remaining substance percentage.

    A zero-width space is used when no warning is active, so the value
    appears visually empty in Home Assistant.
    """
    percentage = parse_float(value)
    if percentage is None:
        return None

    if percentage <= 0:
        return "Wirkstoff leer"
    if percentage <= 10:
        return "Wirkstoff kritisch leer"
    if percentage <= 25:
        return "Wirkstoff bald leer"

    return EMPTY_DISPLAY_STATE


def active_error_messages_text(value: Any) -> str | None:
    """Return active warning/error messages.

    A zero-width space is used as the valid no-error state so the Home
    Assistant entity row remains visually empty instead of showing
    "OK", "Aus", "Unbekannt" or "Nicht verfügbar".
    """
    if not isinstance(value, list):
        return None

    errors: list[str] = []
    for item in value:
        status_id = parse_int(item)
        if status_id in ERROR_STATUS_MESSAGES:
            errors.append(ERROR_STATUS_MESSAGES[status_id])

    return ", ".join(errors) if errors else EMPTY_DISPLAY_STATE


def has_error_state(value: Any) -> bool | None:
    """Return whether any warning/error state is active."""
    if not isinstance(value, list):
        return None
    return any(parse_int(item) in ERROR_STATUS_MESSAGES for item in value)


def mineral_type_text(value: Any, ean: Any = None) -> str:
    """Map the mineral ID to clear text and use the EAN as fallback."""
    mineral_id = parse_int(value)
    if mineral_id is not None and mineral_id > 0:
        return MINERAL_TYPES.get(
            mineral_id,
            f"Unbekannter Wirkstofftyp {mineral_id}",
        )

    ean_number = parse_int(ean)
    if ean_number in MINERAL_TYPES_BY_EAN:
        return MINERAL_TYPES_BY_EAN[ean_number]

    return VALUE_NOT_PROVIDED


def iso_date(value: Any) -> str | None:
    """Return an ISO date from an ISO timestamp."""
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(
            value.replace("Z", "+00:00")
        ).date().isoformat()
    except ValueError:
        return value


def total_flow_litres(flow_payload: dict[str, Any] | None) -> float | None:
    """Sum all flow channels and convert millilitres to litres."""
    if not isinstance(flow_payload, dict):
        return None

    flow = flow_payload.get("flow")
    if not isinstance(flow, dict):
        return None

    total_ml = 0.0
    found = False

    for item in flow.values():
        if not isinstance(item, dict):
            continue

        parsed = parse_float(item.get("totFlow"))
        if parsed is not None:
            total_ml += parsed
            found = True

    if not found:
        return None

    return round(total_ml / 1000, 3)
