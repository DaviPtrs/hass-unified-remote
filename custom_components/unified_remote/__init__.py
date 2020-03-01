"""HA Unified Remote Integration"""
import logging as log
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.helpers.event import track_time_interval
from requests import ConnectionError

from custom_components.unified_remote.cli.connection import Connection
from custom_components.unified_remote.cli.remotes import Remotes

DOMAIN = "unified_remote"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional("host", default="localhost"): cv.string,
                vol.Optional("port", default="9510"): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

DEFAULT_NAME = ""

_LOGGER = log.getLogger(__name__)

REMOTE_FILE_PATH = "/config/custom_components/unified_remote/cli/remotes.yml"

try:
    REMOTES = Remotes(REMOTE_FILE_PATH)
    _LOGGER.info("Remotes loaded sucessful")
except FileNotFoundError:
    _LOGGER.error(f"Remotes file not found. Path:{REMOTE_FILE_PATH}")
except AssertionError as remote_error:
    _LOGGER.error(str(remote_error))
except Exception as error:
    _LOGGER.error(str(error))

CONNECTION = Connection()


def setup(hass, config):
    """Set up is called when Home Assistant is loading our component."""
    host = config[DOMAIN].get("host")
    port = config[DOMAIN].get("port")
    try:
        CONNECTION.connect(host=host, port=port)
        _LOGGER.info(f"Connection to {CONNECTION.get_url()} established")
    except AssertionError as url_error:
        _LOGGER.error(str(url_error))
        return False
    except:
        return False

    def keep_alive(call):
        """Keep host listening our requests"""
        try:
            response = CONNECTION.exe_remote("", "")
            _LOGGER.debug("Keep alive packet sent")
            if response.status_code != 200:
                _LOGGER.error(
                    f"Keep alive packet was failed. Status code: {response.status_code}"
                )
        except ConnectionError:
            try:
                _LOGGER.debug(f"Trying to reconnect with {host}")
                CONNECTION.reconnect(host=host, port=port)
            except:
                pass

    def handle_call(call):
        """Handle the service call."""
        remote_name = call.data.get("remote", DEFAULT_NAME)
        action = call.data.get("action", DEFAULT_NAME)
        if not (remote_name == "" or action == ""):
            remote = REMOTES.get_remote(remote_name)
            if remote == None:
                _LOGGER.warning(
                    f"Remote {remote_name} not found Please check your remotes.yml"
                )
                return None
            remote_id = remote["id"]
            if action in remote["controls"]:
                try:
                    CONNECTION.exe_remote(remote_id, action)
                    _LOGGER.debug(
                        f'Call -> Remote: "{remote_name}"; Remote ID: "{remote_id}"; Action: "{action}"'
                    )
                except ConnectionError as error:
                    _LOGGER.warning("Unable to call remote. Host is off")
            else:
                _LOGGER.warning(
                    f'Action "{action}" doesn\'t exists for remote {remote_name} Please check your remotes.yml'
                )
                return None

    hass.services.register(DOMAIN, "call", handle_call)
    track_time_interval(hass, keep_alive, timedelta(minutes=1))

    return True
