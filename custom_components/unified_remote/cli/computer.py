from custom_components.unified_remote.cli.connection import Connection
from custom_components.unified_remote.cli.remotes import Remotes
import requests
import logging as log

_LOGGER = log.getLogger(__name__)

class Computer:
    def connect(self):
        """Handle with connect function and logs if was successful"""
        self.connection.connect(self.host, self.port)
        _LOGGER.info(f"Connection to {self.name} established")

    def __init__(self, name: str, host: str, port: int):
        self.name = name
        self.host = host
        self.port = port
        self.is_available = False
        self.connection = Connection()
        try:
            self.connect()
            self.is_available = True
        except AssertionError as url_error:
            _LOGGER.error(str(url_error))
            raise
        except requests.ConnectionError:
            _LOGGER.warning(
                f"At the first moment {name} seems down, but the connection will be retried."
            )
        except Exception as e:
            _LOGGER.error(str(e))
            raise

    def call_remote(self, id, action):
        if not self.is_available:
            _LOGGER.error(f"Unable to call remote. {self.name} is unavailable.")
            return None
        try:
            self.connection.exe_remote(id, action)
            _LOGGER.debug(f'Call -> Remote ID: "{id}"; Action: "{action}"')
        # Log if request fails.
        except requests.ConnectionError:
            _LOGGER.error(f"Unable to call remote. {self.name} is unavailable.")
    
    