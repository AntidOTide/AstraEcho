import requests
from mcp.server.fastmcp import FastMCP
import easyquotation

from AstraConfig import AstraConfig


class AstraLink:
    def __init__(self):
        self.mcp:FastMCP|None = None
        self.mcp_port :int = AstraConfig.get("AstraLink").get("mcp_server").get("mcp_port")


    def _init_mcp(self):
        # Create server
        self.mcp = FastMCP(
            "Echo Server",
            port=self.mcp_port,
        )

        @self.mcp.tool()
        def get_current_weather(city: str) -> str:
            print(f"[debug-server] get_current_weather({city})")

            endpoint = "https://wttr.in"
            response = requests.get(f"{endpoint}/{city}")
            return response.text

        @self.mcp.tool()
        def select_stock_info(stock_code: str) -> dict:
            """Use stock code to select stock info ,you MUST need code ,
            if you don't know code ,you MUST ask for user"""
            quotation = easyquotation.use('sina')  # 新浪 ['sina'] 腾讯 ['tencent', 'qq']
            answer = quotation.real(stock_code)  # 支持直接指定前缀，如 'sh000001'
            return answer
    def mcp_run(self):
        self.mcp.run(transport="sse")

if __name__ == "__main__":
    AstraLink().mcp_run()
