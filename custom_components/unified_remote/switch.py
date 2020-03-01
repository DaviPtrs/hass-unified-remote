"""Platform for light integration."""
import logging

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
# Import the device class from the component that you want to support
from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchDevice

# from homeassistant.components.switch import

_LOGGER = logging.getLogger(__name__)

EMPTY_REMOTE = {"action": "", "remote": ""}

REMOTE_CONFIG = vol.Schema(
    {
        vol.Required("remote", default=""): cv.string,
        vol.Required("action", default=""): cv.string,
    }
)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required("name"): cv.string,
        vol.Required("turn_on", default=EMPTY_REMOTE): REMOTE_CONFIG,
        vol.Optional("turn_off", default=EMPTY_REMOTE): REMOTE_CONFIG,
        vol.Optional("toggle", default=EMPTY_REMOTE): REMOTE_CONFIG,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Awesome Light platform."""
    # Assign configuration variables.
    # The configuration check takes care they are present.
    name = config["name"]
    remotes = {
        "turn_on": config.get("turn_on"),
        "turn_off": config.get("turn_off"),
        "toggle": config.get("toggle"),
    }

    # Add devices
    add_entities([UnifiedSwitch(hass, name, remotes)])


class UnifiedSwitch(SwitchDevice):
    def __init__(self, hass, name, remotes):
        self._switch_name = name
        self._remotes = remotes
        self.hass = hass
        self.call = self.hass.services.call
        self._state = False

    def turn_on(self) -> None:
        """Turn the entity on."""
        remote = self._remotes.get("turn_on")
        if remote != EMPTY_REMOTE:
            self.call(domain="unified_remote", service="call", service_data=remote)
            self._state = True

    def turn_off(self):
        """Turn the entity off."""
        remote = self._remotes.get("turn_off")
        if remote != EMPTY_REMOTE:
            self.call(domain="unified_remote", service="call", service_data=remote)
            self._state = False

    def toggle(self):
        """Toggle the entity."""
        remote = self._remotes.get("toggle")
        if remote != EMPTY_REMOTE:
            self.call(domain="unified_remote", service="call", service_data=remote)
            self._state = not self._state

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._switch_name

    @property
    def is_on(self):
        return self._state
