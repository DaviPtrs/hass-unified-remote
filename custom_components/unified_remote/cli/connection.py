"Handle with connection and requests"
import re
from json import dumps
from uuid import uuid4

from requests import Session, get, post


class Connection:
    def __init__(self):
        self.__url = ""
        self.__source_guid = ""
        self.__session = Session()  # Creating a persistent http session

    def connect(self, host, port):
        self.__url = f"http://{host}:{port}/client/"
        assert self.__validate_url(), AssertionError("Malformed URL")
        self.__headers = (
            self.__set_headers()
        )  # Fetching connection id and setting it on headers
        self.__gen_guid()
        self.__autenticate()

    def __gen_guid(self):
        self.__source_guid = f"web-{uuid4()}"

    def __validate_url(self):
        regex = re.compile(
            r"^(?:http|ftp)s?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        return re.match(regex, self.__url) is not None

    def __set_headers(self):
        response = self.__session.get(self.__url + "connect")
        conn_id = response.json()["id"]
        headers = {"UR-Connection-ID": conn_id}
        return headers

    def __autenticate(self):
        password = str(uuid4())
        payload = {
            "Action": 0,
            "Request": 0,
            "Version": 10,
            "Password": password,
            "Platform": "web",
            "Source": self.__source_guid,
        }
        response = self.__session.post(
            self.__url + "request", headers=self.__headers, data=dumps(payload)
        )

        payload = {
            "Capabilities": {
                "Actions": True,
                "Sync": True,
                "Grid": True,
                "Fast": False,
                "Loading": True,
                "Encryption2": True,
            },
            "Action": 1,
            "Request": 1,
            "Source": self.__source_guid,
        }
        response = self.__session.post(
            self.__url + "request", headers=self.__headers, data=dumps(payload)
        )

    # Executing given remote id and action using post method
    def exe_remote(self, remoteID, action):
        payload = {
            "ID": remoteID,
            "Action": 7,
            "Request": 7,
            "Run": {"Name": action},
            "Source": self.__source_guid,
        }
        return self.__session.post(
            self.__url + "request", headers=self.__headers, data=dumps(payload)
        )

    def get_headers(self):
        return self.__headers

    def get_url(self):
        return self.__url
