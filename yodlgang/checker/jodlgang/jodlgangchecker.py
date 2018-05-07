from ctf_gameserver.checker import BaseChecker, OK, NOTFOUND, NOTWORKING, TIMEOUT
import requests


class JodlGangChecker(BaseChecker):
    def __init__(self, tick, team, service, ip):
        BaseChecker.__init__(self, tick, team, service, ip)
        self._base_url = "http://{}:8000".format(ip)

    def place_flag(self):
        return OK

    def check_flag(self, tick):
        return OK

    def check_service(self):
        return OK
