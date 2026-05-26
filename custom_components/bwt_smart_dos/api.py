import asyncio
import aiohttp

from .const import UUIDS


class BwtApi:
    def __init__(self, host):
        self.host = host

    async def fetch_uuid(self, session, uuid):
        url = f"http://{self.host}/api/v1/gatt/{uuid}"

        async with session.get(url, timeout=10) as response:
            response.raise_for_status()
            return await response.json()

    async def fetch_all(self):
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.fetch_uuid(session, uuid)
                for uuid in UUIDS
            ]

            results = await asyncio.gather(*tasks)

        return {
            uuid: result
            for uuid, result in zip(UUIDS, results)
        }
