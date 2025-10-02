from AstraChart import AstraChart
from AstraConfig import AstraConfig
from AstraCore import AstraCore
from AstraNex import AstraNex
from loguru import logger

class AstraEcho:
    def __init__(self):
        self.astra_nex =AstraNex()
        self.astra_core =AstraCore()
        self.astra_chart =AstraChart()
        self.astra_chart.init_database(AstraConfig.get("AstraChart").get("db_path"))
        self.astra_nex.run()


if __name__ == '__main__':
    AstraConfig.load(r"config/config.json")
    astra_echo = AstraEcho()    # def init_astra(self):