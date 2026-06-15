"""Data coordinator for BWT Smart Dos DT Plus."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import BWTApi, BWTApiError
from .const import DOMAIN, DYNAMIC_ENDPOINTS, SCAN_INTERVAL, STATIC_ENDPOINTS

_LOGGER = logging.getLogger(__name__)


class BWTDataCoordinator(DataUpdateCoordinator):
    """Fetch dynamic values every 120 seconds and static values once."""

    def __init__(self, hass: HomeAssistant, ip: str, port: int) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
            always_update=True,
        )
        self.api = BWTApi(async_get_clientsession(hass), ip, port)
        self.static_data: dict[str, Any] = {}

    async def async_load_static_data(self) -> None:
        """Load static data once per integration setup/reload."""
        if self.static_data:
            return

        data: dict[str, Any] = {}
        for endpoint in STATIC_ENDPOINTS:
            try:
                data[endpoint] = await self.api.async_get(endpoint)
            except BWTApiError as err:
                _LOGGER.warning("Could not load static endpoint %s: %s", endpoint, err)
                data[endpoint] = {}
        self.static_data = data

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch dynamic data."""
        try:
            await self.async_load_static_data()
            data: dict[str, Any] = {}
            for endpoint in DYNAMIC_ENDPOINTS:
                data[endpoint] = await self.api.async_get(endpoint)
            data["static"] = self.static_data
            return data
        except BWTApiError as err:
            raise UpdateFailed(f"Error communicating with BWT Smart Dos: {err}") from err
