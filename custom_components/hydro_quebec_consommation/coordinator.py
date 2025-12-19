from datetime import timedelta
import aiohttp
import async_timeout

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.core import HomeAssistant

from .const import API_URL, DEFAULT_LIMIT, DEFAULT_SCAN_INTERVAL, DOMAIN


class HydroEvenementsCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant):
        super().__init__(
            hass,
            logger=hass.logger,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self):
        params = {
            "limit": DEFAULT_LIMIT,
            "order_by": "horodatage_local desc",
        }

        try:
            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession() as session:
                    async with session.get(API_URL, params=params) as resp:
                        if resp.status != 200:
                            raise UpdateFailed(f"HTTP {resp.status}")
                        data = await resp.json()
                        return data["results"]

        except Exception as err:
            raise UpdateFailed(err) from err
