"""HA Unified Remote Integration"""
import logging as log
from datetime import timedelta

from requests import ConnectionError

import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from custom_components.unified_remote.cli.connection import Connection
from custom_components.unified_remote.cli.remotes import Remotes
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.event import track_time_interval

DOMAIN = "unified_remote"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Optional(CONF_HOST, default="localhost"): cv.string,
                vol.Optional(CONF_PORT, default="9510"): cv.string,
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
# Handle with Remote parsing error.
except AssertionError as remote_error:
    _LOGGER.error(str(remote_error))
except Exception as error:
    _LOGGER.error(str(error))

CONNECTION = Connection()


def setup(hass, config):
    """Setting up Unified Remote Integration"""
    # Fetching configuration entries.
    host = config[DOMAIN].get(CONF_HOST)
    port = config[DOMAIN].get(CONF_PORT)

    try:
        # Establishing connection with host client.
        CONNECTION.connect(host=host, port=port)
        _LOGGER.info(f"Connection to {CONNECTION.get_url()} established")
    # Handling with malformed url error.
    except AssertionError as url_error:
        _LOGGER.error(str(url_error))
        return False
    except ConnectionError:
        _LOGGER.warning("At the first moment host seems down, but the connection will be retried.")
    except Exception as e:
        _LOGGER.error(str(e))
        return False

    def keep_alive(call):
        """Keep host listening our requests"""
        try:
            response = CONNECTION.exe_remote("", "")
            _LOGGER.debug("Keep alive packet sent")
            _LOGGER.debug(f"Keep alive packet response: {str(response.content)}")

            if "Not a valid connection" in str(response.content):
                raise ConnectionError()

            if response.status_code != 200:
                _LOGGER.error(
                    f"Keep alive packet was failed. Status code: {response.status_code}"
                )
        # If there's an connection error, try to reconnect.
        except ConnectionError:
            try:
                _LOGGER.debug(f"Trying to reconnect with {host}")
                CONNECTION.connect(host=host, port=port)
            except Exception:
                pass

    def handle_call(call):
        """Handle the service call."""
        # Fetch service data.
        remote_name = call.data.get("remote", DEFAULT_NAME)
        action = call.data.get("action", DEFAULT_NAME)

        # Check if none or empty service data was parsed.
        if not (remote_name == "" or action == ""):
            remote = REMOTES.get_remote(remote_name)
            # Check if remote was declared on remotes.yml.
            if remote is None:
                _LOGGER.warning(
                    f"Remote {remote_name} not found Please check your remotes.yml"
                )
                return None
            # Fetch remote id.
            remote_id = remote["id"]
            # Check if given action exists in remote control list.
            if action in remote["controls"]:
                try:
                    CONNECTION.exe_remote(remote_id, action)
                    _LOGGER.debug(
                        f'Call -> Remote: "{remote_name}"; Remote ID: "{remote_id}"; Action: "{action}"'
                    )
                # Log if request fails.
                except ConnectionError:
                    _LOGGER.warning("Unable to call remote. Host is off")
            else:
                # Log if called remote doens't exists on remotes.yml.
                _LOGGER.warning(
                    f'Action "{action}" doesn\'t exists for remote {remote_name} Please check your remotes.yml'
                )
                return None

    # Register remote call service.
    hass.services.register(DOMAIN, "call", handle_call)
    # Set "keep_alive()" function to be called every 2 minutes.
    # 2 minutes are the max interval to keep connection alive.
    track_time_interval(hass, keep_alive, timedelta(minutes=2))

    return True
