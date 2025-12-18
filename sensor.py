from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


SENSORS = {
    "energie_totale_consommee": {
        "name": "Énergie totale consommée",
        "unit": "kWh",
    },
    "clients_connectes": {
        "name": "Clients connectés",
        "unit": None,
    },
    "temperature_exterieure_moyenne": {
        "name": "Température extérieure moyenne",
        "unit": "°C",
    },
    "temperature_interieure_moyenne": {
        "name": "Température intérieure moyenne",
        "unit": "°C",
    },
}


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]

    entities = [
        HydroEvenementSensor(coordinator, key, meta)
        for key, meta in SENSORS.items()
    ]

    async_add_entities(entities)


class HydroEvenementSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key, meta):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = f"Hydro {meta['name']}"
        self._attr_native_unit_of_measurement = meta["unit"]
        self._attr_unique_id = f"hydro_evenement_{key}"

    @property
    def native_value(self):
        if not self.coordinator.data:
            return None
        return self.coordinator.data[0].get(self._key)

    @property
    def extra_state_attributes(self):
        if not self.coordinator.data:
            return {}

        record = self.coordinator.data[0]

        return {
            "date": record.get("date"),
            "heure_locale": record.get("heure_locale"),
            "poste": record.get("poste"),
            "type_evenement": record.get("type_evenement"),
            "indicateur_evenement": record.get("indicateur_evenement"),
        }
