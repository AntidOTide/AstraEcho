from sqlite3 import Connection
from AstraConfig import AstraConfig
from flask import Flask
from AstraCore import AstraCore
from .AstraRoute import AstraRoute


class AstraNex:
    def __init__(self,db_connection:Connection,astra_core:AstraCore):
        self.client = None
        self.port = None
        self.db_connection =db_connection
        self.astra_core = astra_core
        self._get_astra_nex_config()
        self.init_routes()

    def _get_astra_nex_config(self):
        self.port = AstraConfig.get("AstraNex").get("port")

    def init_routes(self):
        self.client = Flask(__name__)
        AstraRoute(self.client,self.db_connection,self.astra_core)

    def run(self):
        self.client.run(port=self.port)


