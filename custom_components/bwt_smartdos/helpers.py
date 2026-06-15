"""Helper functions for BWT Smart Dos DT Plus."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from .const import MINERAL_TYPES, STATUS_MESSAGES


def first_pouch(data: dict[str, Any] | None) -> dict[str, Any]:
    """Return first pouch object from endpoint 0401/0402."""
    if not isinstance(data, dict):
        return {}
    value = data.get("1")
    return value if isinstance(value, dict) else {}


def parse_float(value: Any) -> float | None:
    """Parse float safely."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_int(value: Any) -> int | None:
    """Parse int safely."""
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def seconds_to_hours(value: Any) -> float | None:
    """Convert seconds to hours."""
    seconds = parse_float(value)
    if seconds is None:
        return None
    return round(seconds / 3600, 2)


def ml_to_l(value: Any) -> float | None:
    """Convert millilitres to litres."""
    millilitres = parse_float(value)
    if millilitres is None:
        return None
    return round(millilitres / 1000, 3)


def status_text(value: Any) -> str | None:
    """Return status text for one status ID."""
    status_id = parse_int(value)
    if status_id is None:
        return None
    return STATUS_MESSAGES.get(status_id, f"Unbekannter Status {status_id}")


def active_states_text(value: Any) -> str | None:
    """Return text for active state list."""
    if not isinstance(value, list):
        return None
    if not value:
        return "Keine aktive Meldung"
    return ", ".join(status_text(item) or f"Unbekannter Status {item}" for item in value)


def mineral_type_text(value: Any) -> str | None:
    """Return mineral type text."""
    mineral_id = parse_int(value)
    if mineral_id is None:
        return None
    return MINERAL_TYPES.get(mineral_id, f"Unbekannter Wirkstofftyp {mineral_id}")


def iso_date(value: Any) -> str | None:
    """Return YYYY-MM-DD from an ISO timestamp when possible."""
    if not isinstance(value, str) or not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return value


def total_flow_litres(flow_payload: dict[str, Any] | None) -> float | None:
    """Return total treated water in litres from endpoint 0503.

    Endpoint values are given in millilitres. All flow channels are summed.
    """
    if not isinstance(flow_payload, dict):
        return None
    flow = flow_payload.get("flow")
    if not isinstance(flow, dict):
        return None

    total_ml = 0.0
    found = False
    for item in flow.values():
        if isinstance(item, dict) and "totFlow" in item:
            parsed = parse_float(item.get("totFlow"))
            if parsed is not None:
                total_ml += parsed
                found = True

    if not found:
        return None
    return round(total_ml / 1000, 3)
