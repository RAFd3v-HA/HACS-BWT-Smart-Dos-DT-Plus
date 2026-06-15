"""Data coordinator for BWT Smart Dos DT Plus."""
from __future__ import annotations

import logging
from time import monotonic
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .api import BWTApi, BWTApiError
from .const import (
    DATA_ENDPOINTS,
    DATA_SCAN_INTERVAL_SECONDS,
    DOMAIN,
    FAST_ENDPOINTS,
    STATIC_ENDPOINTS,
    STATIC_SCAN_INTERVAL_SECONDS,
    STATUS_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


class BWTDataCoordinator(DataUpdateCoordinator):
    """Coordinate fast status, regular measurements and metadata polling."""

    def __init__(self, hass: HomeAssistant, ip: str, port: int) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=STATUS_SCAN_INTERVAL,
            always_update=True,
        )
        self.api = BWTApi(async_get_clientsession(hass), ip, port)
        self.data_cache: dict[str, Any] = {}
        self.static_data: dict[str, Any] = {}
        self._last_data_refresh: float | None = None
        self._last_static_refresh: float | None = None

    @staticmethod
    def _refresh_due(last_refresh: float | None, interval: int) -> bool:
        """Return whether an endpoint group is due for refresh."""
        if last_refresh is None:
            return True
        return monotonic() - last_refresh >= interval

    async def _async_refresh_group(
        self,
        endpoints: tuple[str, ...],
        target: dict[str, Any],
        group_name: str,
    ) -> None:
        """Refresh an endpoint group and retain old values on failures."""
        for endpoint in endpoints:
            try:
                target[endpoint] = await self.api.async_get(endpoint)
            except BWTApiError as err:
                _LOGGER.warning(
                    "Could not refresh %s endpoint %s: %s",
                    group_name,
                    endpoint,
                    err,
                )

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch status every 10 s, data every 120 s and metadata every 600 s."""
        try:
            now = monotonic()

            if self._refresh_due(
                self._last_static_refresh,
                STATIC_SCAN_INTERVAL_SECONDS,
            ):
                await self._async_refresh_group(
                    STATIC_ENDPOINTS,
                    self.static_data,
                    "static",
                )
                self._last_static_refresh = now

            if self._refresh_due(
                self._last_data_refresh,
                DATA_SCAN_INTERVAL_SECONDS,
            ):
                await self._async_refresh_group(
                    DATA_ENDPOINTS,
                    self.data_cache,
                    "data",
                )
                self._last_data_refresh = now

            fast_data: dict[str, Any] = {}
            for endpoint in FAST_ENDPOINTS:
                fast_data[endpoint] = await self.api.async_get(endpoint)

            return {
                **self.data_cache,
                **fast_data,
                "static": self.static_data,
            }

        except BWTApiError as err:
            raise UpdateFailed(
                f"Error communicating with BWT Smart Dos: {err}"
            ) from err
