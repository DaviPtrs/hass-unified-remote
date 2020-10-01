from custom_components.unified_remote.cli.connection import Connection
from custom_components.unified_remote.cli.remotes import Remotes
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
        self.connection = Connection()
        try:
            self.connect()
        except AssertionError as url_error:
            _LOGGER.error(str(url_error))
            raise
        except ConnectionError:
            _LOGGER.warning(
                f"At the first moment {name} seems down, but the connection will be retried."
            )
        except Exception as e:
            _LOGGER.error(str(e))
            raise

    def call_remote(self, id, action):
        try:
            self.connection.exe_remote(id, action)
            _LOGGER.debug(f'Call -> Remote ID: "{id}"; Action: "{action}"')
        # Log if request fails.
        except ConnectionError:
            _LOGGER.warning(f"Unable to call remote. {self.name} is off")
    
    