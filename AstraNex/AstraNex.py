from AstraChart import AstraChart
from AstraConfig import AstraConfig
from flask import Flask
from .AstraRoute import AstraRoute


class AstraNex:
    def __init__(self,db_connection):
        self.client = None
        self.port = None
        self._get_astra_nex_config()
        self.init_routes()

    def _get_astra_nex_config(self):
        self.port = AstraConfig.get("AstraNex").get("port")

    def init_routes(self):
        self.client = Flask(__name__)
        AstraRoute(self.client,self.db_connection)

    def run(self):
        self.client.run(port=self.port)


if __name__ == '__main__':
    ins = AstraNex()
    ins.run()
