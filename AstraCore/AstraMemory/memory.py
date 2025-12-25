"""
Astra Echo的多种memory配置方案


"""
from utils import JsonLoader, JsonWriter
from .memory_type import AstraMemoryJson





class AstraMemory:
    def __init__(self):
        pass
    @staticmethod
    def load_json_memory(path:str)->AstraMemoryJson:
        memory = JsonLoader.load_json_file(path)
        return  memory

    @staticmethod
    def write_json_memory(memory:AstraMemoryJson,path:str):
        JsonWriter.write_json(memory,path)









