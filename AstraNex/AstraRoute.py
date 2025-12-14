import time

from agents import RunResult
from agents.mcp import MCPServerSse
from flask import Flask, request, jsonify
from sqlite3 import Connection

from AstraCore import AstraCore
from AstraLink import AstraLink
from utils import JsonLoader, JsonWriter

temp_memory = []
class AstraRoute:
    def __init__(self, app: Flask,
                 db_connection: Connection,
                 astra_core:AstraCore,
                 astra_link:AstraLink):
        self.app = app
        self.db_connection = db_connection
        self.core_ins = astra_core
        self.astra_link = astra_link
        self.register_routes()

    @staticmethod
    async def create_and_start_server(config):
        """创建并启动单个服务器"""
        server = MCPServerSse(
            name=config["name"],
            params={
                "url": config["url"],
                "headers": config.get("headers", {})
            },
            cache_tools_list=config.get("cache_tools_list", True),
        )
        # 进入上下文管理器
        await server.__aenter__()
        return server

    async def run_with_multiple_servers(self,server_configs):
        """运行带有多个MCP服务器的agent"""

        # 创建并启动所有服务器
        servers = []
        for config in server_configs:
            server = await self.create_and_start_server(config)
            servers.append(server)
        return servers
    def register_routes(self):
        @self.app.route("/", methods=["GET"])
        def index():
            return "该接口正常工作"

        @self.app.route("/send", methods=["GET"])
        async def send():

            message = request.args.get('message')
            path = "memory_test/agent_memory.json"
            memory = JsonLoader.load_json_file(path)
            print(memory)
            human_message = {
                "role":"user",
                "content":message
            }
            memory_list:list = memory["agent_memory"]['memory']
            memory_list.append(human_message)
            configs = []
            servers = []
            for server in self.astra_link.mcp_server_list:
                configs.append(
                    {
                        "name": server.name,
                        "url" : f"http://{server.host}:{server.port}/sse"
                    }
                )
                servers = await self.run_with_multiple_servers(configs)
            ans:RunResult = await self.core_ins.run_agent(servers,memory_list)
            print(ans)
            ai_message = {
                "role":"assistant",
                "content":ans.final_output
            }
            memory_list.append(ai_message)
            print(memory)
            JsonWriter.write_json(memory,path)
            return ans.final_output

        @self.app.route("/chat",methods = ["POST"])
        def chat():
            d = {
                "device":"",
                "chat_messages":""
            }
        @self.app.route("/add_chat_message", methods=["POST"])
        def add_chat_message():
            """添加回话数据"""
            data = request.get_json()
            if not data:
                return jsonify({'error': "Data error"})
            if not data.get('role'):
                return jsonify({'error': 'Name and email are required'}), 400
            elif not data.get('content'):
                return jsonify({'error': 'Content is required'}), 400

            try:
                self.db_connection.execute(
                    """
                    INSERT INTO ASTRA_CHAT (role, content) 
                    VALUES (?,?)
                    """
                    , (data['role'], data['content']))
                self.db_connection.commit()
            except Exception as e:
                self.db_connection.rollback()
                return jsonify({'error': str(e)}), 500
