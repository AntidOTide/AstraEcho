import time
from flask import Flask
from AstraChart import AstraChart
from AstraCore import AstraCore
from AstraCore.AstraMemory.memory import AstraMemory
from AstraLink import AstraLink
from AstraNex import AstraNex, AstraRoute
from AstraNex import AstraLogger
from AstraLink.mcp_server import mcp


class AstraEcho:
    def __init__(self):
        self.client = None
        self.port = None
        self._init_astra_echo()

    def _init_astra_echo(self):
        AstraLogger.info("正在配置AstraEcho")
        self.astra_core = AstraCore()
        self.astra_chart = AstraChart()
        self.astra_link = AstraLink()
        self.astra_memory = AstraMemory()
        # 添加mcp服务器到astra_link
        self.astra_link.add_mcp_server(mcp)
        self.astra_link.start_all_mcp_server_in_thread()

        self.astra_nex = AstraNex(self.astra_chart.conn,
                                  self.astra_core,
                                  self.astra_link,
                                  self.astra_memory
                                  )
        self.init_routes()
        AstraRoute(self.client,self.astra_chart.conn,self.astra_nex)
        self.run()
        time.sleep(2)

    def init_routes(self):
        self.client = Flask(__name__)

    def run(self):
        AstraLogger.info("AstraEcho配置完毕")
        self.client.run(port=self.port)

if __name__ == '__main__':
    pass
