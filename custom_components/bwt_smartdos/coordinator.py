"""Data coordinator for BWT Smart Dos DT Plus."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import BWTApi, BWTApiError
from .const import (
    DOMAIN,
    DYNAMIC_ENDPOINTS,
    ENDPOINT_POUCH,
    SCAN_INTERVAL,
    STATIC_ENDPOINTS,
)
from .helpers import pouch_has_identity

_LOGGER = logging.getLogger(__name__)


class BWTDataCoordinator(DataUpdateCoordinator):
    """Fetch dynamic values and cache static values."""

    def __init__(self, hass: HomeAssistant, ip: str, port: int) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
            always_update=True,
        )
        self.api = BWTApi(async_get_clientsession(hass), ip, port)
        self.static_data: dict[str, Any] = {}
        self._pouch_identity_complete = False

    async def async_load_static_data(self) -> None:
        """Load static data once.

        Endpoint 0401 is retried during later coordinator updates only when
        the device initially returns incomplete zero values. Once useful
        pouch identity data is available, it is cached.
        """
        for endpoint in STATIC_ENDPOINTS:
            if endpoint in self.static_data:
                continue

            try:
                payload = await self.api.async_get(endpoint)
            except BWTApiError as err:
                _LOGGER.warning(
                    "Could not load static endpoint %s: %s",
                    endpoint,
                    err,
                )
                continue

            self.static_data[endpoint] = payload

            if endpoint == ENDPOINT_POUCH:
                self._pouch_identity_complete = pouch_has_identity(payload)

    async def async_refresh_incomplete_pouch_data(self) -> None:
        """Retry 0401 until the device supplies useful pouch identity data."""
        if self._pouch_identity_complete:
            return

        try:
            payload = await self.api.async_get(ENDPOINT_POUCH)
        except BWTApiError as err:
            _LOGGER.debug(
                "Could not refresh incomplete pouch data: %s",
                err,
            )
            return

        self.static_data[ENDPOINT_POUCH] = payload
        self._pouch_identity_complete = pouch_has_identity(payload)

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch dynamic data every 120 seconds."""
        try:
            await self.async_load_static_data()
            await self.async_refresh_incomplete_pouch_data()

            data: dict[str, Any] = {}
            for endpoint in DYNAMIC_ENDPOINTS:
                data[endpoint] = await self.api.async_get(endpoint)

            data["static"] = self.static_data
            return data

        except BWTApiError as err:
            raise UpdateFailed(
                f"Error communicating with BWT Smart Dos: {err}"
            ) from err
