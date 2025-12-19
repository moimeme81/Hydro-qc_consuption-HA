
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN

class HydroQuebecConsommationConfigFlow(config_entries.ConfigFlow):
    """Handle a config flow for Hydro-Québec Consommation."""

    domain = DOMAIN  # ✅ Correct placement
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="Hydro-Québec – Consommation d’énergie",  # ✅ Use static or translated title
                data={},
            )

        return self.async_show_form(step_id="user")

    @callback
    def async_get_options_flow(config_entry):
        return HydroQuebecOptionsFlowHandler(config_entry)


class HydroQuebecOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for Hydro-Québec integration."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(step_id="init")
