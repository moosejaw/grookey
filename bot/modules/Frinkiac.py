import requests

class Frinkiac:
    def __init__(self, dns, port):
        self.dns = dns
        self.port = port

    def getNodeResponse(self):
        r = requests.get(f'http://{self.dns}:{self.port}/api/')
        if not r.json():
            return None
        return r