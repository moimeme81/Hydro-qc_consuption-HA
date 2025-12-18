from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([HydroQuebecConsommationSensor(coordinator)])


class HydroQuebecConsommationSensor(CoordinatorEntity, SensorEntity):
    _attr_name = "Hydro-Québec – Consommation d’énergie"
    _attr_unique_id = "hydro_quebec_consommation"
    _attr_icon = "mdi:transmission-tower"

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        return self.coordinator.data[0].get("horodatage_local")

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}

        return {
            "latest": self.coordinator.data[0],
            "records": self.coordinator.data,
            "record_count": len(self.coordinator.data),
        }
