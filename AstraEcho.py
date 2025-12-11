import time

from AstraChart import AstraChart
from AstraConfig import AstraConfig
from AstraCore import AstraCore
from AstraNex import AstraNex
from AstraNex import AstraLogger

class AstraEcho:
    def __init__(self):
        self._init_astra_echo()

    def _init_astra_echo(self):
        AstraLogger.info("正在配置AstraEcho")
        self.astra_core =AstraCore()
        self.astra_chart =AstraChart()
        self.astra_nex =AstraNex(self.astra_chart.conn,self.astra_core)
        self.astra_nex.run()
        time.sleep(2)
        AstraLogger.info("AstraEcho配置完毕")

if __name__ == '__main__':
    AstraConfig.load(r"config/config.json")
    astra_echo = AstraEcho()