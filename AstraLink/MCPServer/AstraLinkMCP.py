from mcp.server import FastMCP

class AstraLinkMCP:
    """代理基类，强制子类实现特定方法"""

    def __init__(self,
                 name:str,
                 mcp_server: FastMCP,
                 port:int=8000,
                 host:str="127.0.0.1",
                 ):
        self.name = name
        self.port = port
        self.mcp_server:FastMCP=mcp_server
        self.app = self.mcp_server.sse_app()
        self.host:str = host


# class AstraLinkMCPBase(ABC):
#     """代理基类，强制子类实现特定方法"""
#
#     def __init__(self,
#                  name:str,
#                  port:int=8000,
#                  host:str="127.0.0.1"
#                  ):
#         self.name = name
#         self.port = port
#         self.mcp_server:FastMCP|None=None
#         self.host:str = host
#     @abstractmethod
#     def initialize(self):
#         """初始化代理 - 必须实现"""
#         pass
#
#     @abstractmethod
#     def process(self, input_data):
#         """处理输入数据 - 必须实现"""
#         pass
#
#     @abstractmethod
#     def cleanup(self):
#         """清理资源 - 必须实现"""
#         pass
#
#
# class AstraLinkMCP(AstraLinkMCPBase):
#     def __init__(self, name: str):
#         super().__init__(name)
#
#
#     def cleanup(self):
#         pass
#
#     def process(self, input_data):
#         pass
#
#     def initialize(self):
#         self.mcp_server = FastMCP(
#             name=self.name,
#             port=self.port,
#             host=self.host
#         )
#         pass
