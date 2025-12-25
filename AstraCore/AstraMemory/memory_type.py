from typing import TypeAlias, List, TypedDict

from openai.types.responses import EasyInputMessageParam


# class AstraMemoryJson(List[EasyInputMessageParam]):
#     pass

class AstraMemoryJson(TypedDict):
    id:int
    device:str
    memory:List[EasyInputMessageParam]

AstraMemoryType:TypeAlias = [
    AstraMemoryJson
]