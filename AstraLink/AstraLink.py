import asyncio
import time
from threading import Thread

import uvicorn
from typing_extensions import overload
from AstraLink.MCPServer.AstraLinkMCP import AstraLinkMCP
from AstraNex import AstraLogger


class AstraLink:
    def __init__(self):
        self.thread : Thread |None= None
        self.mcp_server_list:list[AstraLinkMCP] = []



    @overload
    def add_mcp_server(self,mcp_server_list:list[AstraLinkMCP]):
        self.mcp_server_list.extend(mcp_server_list)

    def add_mcp_server(self, mcp_server: AstraLinkMCP):
        self.mcp_server_list.append(mcp_server)
    @staticmethod
    async def run_main_server(mcp_server:AstraLinkMCP):


        AstraLogger.info(f"正在启动MCPServer:{mcp_server.name}\n启动于端口:{mcp_server.port}")
        """运行MCP服务器"""
        config = uvicorn.Config(
            app=mcp_server.app,
            host=mcp_server.host,
            port=mcp_server.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
    def start_in_thread(self ,mcp_server:AstraLinkMCP):
        """在新线程中启动服务器"""
        def run():
            asyncio.run(self.run_main_server(mcp_server))
            time.sleep(2)

        self.thread =Thread(
            target=run,
            name=f"MCP-{mcp_server.name}",
            daemon=True  # 设置为守护线程，主线程退出时自动结束
        )
        self.thread.start()
        AstraLogger.info(f"[{mcp_server.name}] 已在后台线程中启动")

    def start_all_mcp_server_in_thread(self):
        for i in self.mcp_server_list:
            self.start_in_thread(i)
