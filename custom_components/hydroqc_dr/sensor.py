
from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any, Dict, Optional

import async_timeout
from aiohttp.client_exceptions import ClientError

from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorEntityDescription
from homeassistant.const import (
    UnitOfTemperature,
    UnitOfEnergy,
    UnitOfSpeed,
    PERCENTAGE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, BASE_URL
from homeassistant.const import CONF_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

CONF_POSTE = "poste"

SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key="energie_totale_consommee",
        name="HydroQC DR Energy Total",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        state_class="measurement",
        icon="mdi:lightning-bolt",
    ),
    SensorEntityDescription(
        key="temperature_interieure_moyenne",
        name="HydroQC DR Inside Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SensorEntityDescription(
        key="temperature_exterieure_moyenne",
        name="HydroQC DR Outside Temperature",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    SensorEntityDescription(
        key="humidite_relative_moyenne",
        name="HydroQC DR Relative Humidity",
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
    ),
    SensorEntityDescription(
        key="irradiance_solaire_moyenne",
        name="HydroQC DR Solar Irradiance",
        native_unit_of_measurement="W/m²",
        icon="mdi:white-balance-sunny",
    ),
    SensorEntityDescription(
        key="vitesse_vent_moyenne",
        name="HydroQC DR Wind Speed",
        device_class=SensorDeviceClass.WIND_SPEED,
        native_unit_of_measurement=UnitOfSpeed.METERS_PER_SECOND,
    ),
    SensorEntityDescription(
        key="indicateur_evenement",
        name="HydroQC DR Event Indicator",
        icon="mdi:alert",
    ),
)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    poste = entry.data.get(CONF_POSTE, "B")
    scan_interval = int(entry.data.get(CONF_SCAN_INTERVAL, 900))

    coordinator = HydroQcDrCoordinator(hass, poste, scan_interval)
    await coordinator.async_config_entry_first_refresh()

    entities = [
        HydroQcDrSensor(coordinator, desc, poste)
        for desc in SENSOR_DESCRIPTIONS
    ]
    async_add_entities(entities, update_before_add=True)

class HydroQcDrCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, poste: str, scan_interval: int) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"Hydro-Québec DR (poste {poste})",
            update_interval=timedelta(seconds=scan_interval),
        )
        self._poste = poste

    async def _async_update_data(self) -> Dict[str, Any]:
        session = async_get_clientsession(self.hass)
        params = {
            "limit": "1",
            "order_by": "horodatage_local desc",  # latest record first
            "where": f'poste="{self._poste}"',
        }
        try:
            async with async_timeout.timeout(20):
                async with session.get(BASE_URL, params=params) as resp:
                    data = await resp.json()
        except (ClientError, asyncio.TimeoutError) as err:
            raise UpdateFailed(f"API request failed: {err}") from err

        results = data.get("results")
        if not results:
            raise UpdateFailed("No results returned for the selected poste.")

        # Return the first record (latest hour)
        return results[0]

class HydroQcDrSensor(SensorEntity):
    def __init__(self, coordinator: HydroQcDrCoordinator, description: SensorEntityDescription, poste: str) -> None:
        self.coordinator = coordinator
        self.entity_description = description
        self._attr_has_entity_name = True
        self._attr_unique_id = f"hydroqc_dr_{poste}_{description.key}"

    @property
    def name(self) -> Optional[str]:
        base = self.entity_description.name
        return f"{base} (poste {self.coordinator._poste})"

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

    @property
    def native_value(self) -> Any:
        record = self.coordinator.data or {}
        return record.get(self.entity_description.key)

    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        record = self.coordinator.data or {}
        return {
            "date": record.get("date"),
            "horodatage_local": record.get("horodatage_local"),
            "heure_locale": record.get("heure_locale"),
            "type_evenement": record.get("type_evenement"),
            "clients_connectes": record.get("clients_connectes"),
            "tstats_intelligents_connectes": record.get("tstats_intelligents_connectes"),
            "poste": record.get("poste"),
            "jour_semaine": record.get("jour_semaine"),
        }

    async def async_update(self) -> None:
        await self.coordinator.async_request_refresh()

    @property
    def should_poll(self) -> bool:
        return False

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
