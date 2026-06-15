"""Local API client for BWT Smart Dos DT Plus."""
from __future__ import annotations

import asyncio
from typing import Any

import aiohttp


class BWTApiError(Exception):
    """Base API error."""


class BWTApiConnectionError(BWTApiError):
    """Connection error."""


class BWTApiResponseError(BWTApiError):
    """Invalid response error."""


class BWTApi:
    """Small async client for the local BWT Smart Dos API."""

    def __init__(self, session: aiohttp.ClientSession, ip: str, port: int = 80) -> None:
        self._session = session
        self._ip = ip
        self._port = port
        self._base_url = f"http://{ip}:{port}/api/v1/gatt"

    @property
    def ip(self) -> str:
        return self._ip

    @property
    def port(self) -> int:
        return self._port

    async def async_get(self, uuid: str) -> dict[str, Any]:
        url = f"{self._base_url}/{uuid}"
        try:
            async with self._session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status != 200:
                    raise BWTApiResponseError(f"HTTP {response.status} for {uuid}")
                data = await response.json(content_type=None)
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            raise BWTApiConnectionError(str(err)) from err

        if not isinstance(data, dict):
            raise BWTApiResponseError(f"Unexpected JSON response for {uuid}: {type(data)!r}")
        return data

    async def async_validate(self) -> dict[str, Any]:
        device = await self.async_get("0201")
        wifi = await self.async_get("0104")
        return {"0201": device, "0104": wifi}
