import requests
from mcp.server.fastmcp import FastMCP
import easyquotation
# Create server
mcp = FastMCP("Echo Server")


@mcp.tool()
def get_current_weather(city: str) -> str:
    print(f"[debug-server] get_current_weather({city})")

    endpoint = "https://wttr.in"
    response = requests.get(f"{endpoint}/{city}")
    return response.text
@mcp.tool()
def select_stock_info(stock_code: str) -> dict:
    """Use stock code to select stock info ,you MUST need code ,
    if you don't know code ,you MUST ask for user"""
    quotation = easyquotation.use('sina')  # 新浪 ['sina'] 腾讯 ['tencent', 'qq']
    a = quotation.real(stock_code)  # 支持直接指定前缀，如 'sh000001'
    return a

if __name__ == "__main__":
    mcp.run(transport="sse")

