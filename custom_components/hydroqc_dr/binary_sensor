
import logging
from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType

from .sensor import HydroQcDrCoordinator
from .const import DOMAIN, CONF_POSTE
from homeassistant.const import CONF_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    poste = entry.data.get(CONF_POSTE, "B")
    scan_interval = int(entry.data.get(CONF_SCAN_INTERVAL, 900))

    coordinator = HydroQcDrCoordinator(hass, poste, scan_interval)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([HydroQcDrEventBinarySensor(coordinator, poste)], update_before_add=True)

class HydroQcDrEventBinarySensor(BinarySensorEntity):
    def __init__(self, coordinator: HydroQcDrCoordinator, poste: str) -> None:
        self.coordinator = coordinator
        self._poste = poste
        self._attr_has_entity_name = True
        self._attr_name = f"Event Active (poste {poste})"
        self._attr_unique_id = f"hydroqc_dr_event_active_{poste}"
        self._attr_device_class = BinarySensorDeviceClass.PROBLEM

    @property
    def is_on(self) -> bool:
        record = self.coordinator.data or {}
        return (record.get("indicateur_evenement") or 0) == 1

    @property
    def device_info(self):
        return {
            "identifiers": {("hydroqc_dr", f"poste_{self._poste}")},
            "name": f"Hydro-Québec DR (poste {self._poste})",
            "manufacturer": "Hydro-Québec",
            "model": "Open Data – Opendatasoft",
            "entry_type": DeviceEntryType.SERVICE,
            "configuration_url": "https://donnees.hydroquebec.com/explore/dataset/consommation-clients-evenements-pointe/",
        }

    @property
    def extra_state_attributes(self):
        record = self.coordinator.data or {}
        return {
            "type_evenement": record.get("type_evenement"),
            "horodatage_local": record.get("horodatage_local"),
        }

    async def async_update(self) -> None:
        await self.coordinator.async_request_refresh()

    @property
    def should_poll(self) -> bool:
        return False

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(self.coordinator.async_add_listener(self.async_write_ha_state))
