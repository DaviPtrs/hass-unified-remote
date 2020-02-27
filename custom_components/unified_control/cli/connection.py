#!/usr/bin/python3
from requests import get, post, Session
from json import dumps
from uuid import uuid4
import re

class Connection():
    def __init__(self, host="localhost", port="9510"):
        self.__url = f"http://{host}:{port}/client"
        assert self.__validate_url(), AssertionError("Malformed URL!")
        self.__source_guid = ""
        self.__session = Session() # Creating a persistent http session
        self.__headers = self.__set_headers() # Fetching connection id and setting it on headers

    def __validate_url(self):
        regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

        return (re.match(regex, self.__url) is not None)

    def __set_headers(self):
        response = self.__session.get(self.__url + '/connect')
        conn_id = response.json()['id']
        headers = {
            'UR-Connection-ID': conn_id
        }
        self.__source_guid = f"web-{conn_id}"
        return headers    

    # Executing given remote id and action using post method
    def exe_remote(self, remoteID, action):
        payload = {"ID":remoteID,"Action":7,"Request":7,"Run":{"Name":action},"Source":self.__source_guid}
        response = self.__session.post(self.__url+'/request', headers=self.__headers, data=dumps(payload))

    def get_headers(self):
        return self.__headers
    
    def get_url(self):
        return self.__url
