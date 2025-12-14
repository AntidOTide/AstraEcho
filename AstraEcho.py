import time

from AstraChart import AstraChart
from AstraConfig import AstraConfig
from AstraCore import AstraCore
from AstraLink import AstraLink
from AstraNex import AstraNex
from AstraNex import AstraLogger
from AstraLink.mcp_server import mcp

class AstraEcho:
    def __init__(self):
        self._init_astra_echo()

    def _init_astra_echo(self):
        AstraLogger.info("正在配置AstraEcho")
        self.astra_core =AstraCore()
        self.astra_chart =AstraChart()
        self.astra_link = AstraLink()
        self.astra_link.add_mcp_server(mcp)
        self.astra_link.start_all_mcp_server_in_thread()


        self.astra_nex =AstraNex(self.astra_chart.conn,self.astra_core,self.astra_link)
        self.astra_nex.run()
        time.sleep(2)


if __name__ == '__main__':
    pass
