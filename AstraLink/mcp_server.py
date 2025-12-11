import requests
from mcp.server.fastmcp import FastMCP
import easyquotation

from AstraConfig import AstraConfig

# Create server
AstraConfig.load("config/config.json")
mcp_port =AstraConfig.get("AstraLink").get("mcp_server").get("mcp_port")
mcp = FastMCP(
            name = "Echo Server",
            port = mcp_port ,
)


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
    answer = quotation.real(stock_code)  # 支持直接指定前缀，如 'sh000001'
    return answer

@mcp.tool()
def get_device_info()->list[str]:
    """Get user computer device info"""
    import platform
    machine = f"处理器架构: {platform.machine()}"
    type = f"处理器类型: {platform.processor()}"
    sys = f"系统架构: {platform.architecture()[0]}"
    platform = f"平台信息: {platform.platform()}"
    print("=== 使用 platform 模块 ===")
    print(machine)
    print(type)
    print(sys)
    print(platform)
    return [machine,type,sys,platform]



if __name__ == "__main__":
    try:
        mcp.run(transport="sse")
        # get_device_info()


    except KeyboardInterrupt:
        print("MCP Server Exit")