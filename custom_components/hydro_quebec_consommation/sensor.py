
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import UnitOfEnergy, STATE_CLASS_MEASUREMENT
from .const import DOMAIN

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        HydroQuebecConsumptionSensor(coordinator),
        HydroQuebecPeakEventSensor(coordinator),
    ]
    async_add_entities(sensors)


class HydroQuebecBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for Hydro-Québec sensors."""

    def __init__(self, coordinator):
        super().__init__(coordinator)

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, "hydro_quebec_device")},
            "name": "Hydro-Québec",
            "manufacturer": "Hydro-Québec",
            "model": "Consommation API",
            "entry_type": "service",
        }


class HydroQuebecConsumptionSensor(HydroQuebecBaseSensor):
    """Sensor for latest energy consumption."""

    _attr_name = "Hydro-Québec – Dernière consommation"
    _attr_unique_id = "hydro_quebec_last_consumption"
    _attr_icon = "mdi:flash"
    _attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
    _attr_state_class = STATE_CLASS_MEASUREMENT

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        return self.coordinator.data[0].get("consommation_kWh")

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        return {
            "timestamp": self.coordinator.data[0].get("horodatage_local"),
            "record_count": len(self.coordinator.data),
        }


class HydroQuebecPeakEventSensor(HydroQuebecBaseSensor):
    """Sensor for peak event status."""

    _attr_name = "Hydro-Québec – Événement de pointe"
    _attr_unique_id = "hydro_quebec_peak_event"
    _attr_icon = "mdi:alert"

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        return "Oui" if self.coordinator.data[0].get("evenement_pointe") else "Non"

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}
        return {
            "timestamp": self.coordinator.data[0].get("horodatage_local"),
            "details": self.coordinator.data[0],
        }
