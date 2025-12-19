
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.const import CONF_SCAN_INTERVAL
from .const import DOMAIN, DEFAULT_UPDATE_INTERVAL, CONF_POSTE

class HydroQcDrConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors = {}
        if user_input is not None:
            poste = user_input.get(CONF_POSTE, "").strip()
            if not poste:
                errors["base"] = "invalid_poste"
            else:
                return self.async_create_entry(
                    title=f"Hydro-Québec DR (poste {poste})",
                    data={
                        CONF_POSTE: poste,
                        CONF_SCAN_INTERVAL: int(user_input.get(CONF_SCAN_INTERVAL, DEFAULT_UPDATE_INTERVAL)),
                    },
                )

        schema = vol.Schema({
            vol.Required(CONF_POSTE, default="B"): str,
            vol.Optional(CONF_SCAN_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): int,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @callback
    def async_get_options_flow(self, config_entry):
        return OptionsFlowHandler(config_entry)

class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, entry):
        self.config_entry = entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema({
            vol.Optional(CONF_SCAN_INTERVAL, default=self.config_entry.data.get(CONF_SCAN_INTERVAL, DEFAULT_UPDATE_INTERVAL)): int,
        })
        return self.async_show_form(step_id="init", data_schema=schema)
