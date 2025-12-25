from sqlite3 import Connection
from AstraConfig import AstraConfig
from AstraCore import AstraCore
from AstraCore.AstraMemory.memory import AstraMemory
from AstraLink import AstraLink


class AstraNex:
    def __init__(self,db_connection:Connection,
                 astra_core:AstraCore,
                 astra_link:AstraLink,
                 astra_memory:AstraMemory):
        self.db_connection =db_connection
        self.astra_core = astra_core
        self.astra_link = astra_link
        self.astra_memory = astra_memory




