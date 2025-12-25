from agents import RunResult
from agents.mcp import MCPServerSse
from flask import Flask, request, jsonify
from sqlite3 import Connection

from openai.types.responses import EasyInputMessageParam

from AstraCore.AstraMemory import AstraMemoryJson
from AstraNex import AstraNex
temp_memory = []
class AstraRoute:
    def __init__(self, app: Flask,
                 db_connection: Connection,
                 astra_nex:AstraNex,
                 ):
        self.app = app
        self.db_connection = db_connection
        self.core_ins = astra_nex.astra_core
        self.astra_link = astra_nex.astra_link
        self.astra_memory = astra_nex.astra_memory
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
            message:str = request.args.get('message')
            path = "memory_test/agent_memory.json"
            memory = self.astra_memory.load_json_memory(path)
            human_message :EasyInputMessageParam = {
                "role":"user",
                "content":message
            }
            memory_list = memory['memory']
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
            ai_message = {
                "role":"assistant",
                "content":ans.final_output
            }
            memory_list.append(ai_message)
            self.astra_memory.write_json_memory(memory, path)
            return ans.final_output

        @self.app.route("/send", methods=["POST"])
        async def send():
            req = request.json
            message: str = req['message']
            id :int =req['id']
            device:str =req['device']

            # path = "memory_test/agent_memory.json"
            # memory = self.astra_memory.load_json_memory(path)
            human_message: EasyInputMessageParam = {
                "role": "user",
                "content": message
            }
            memory_list = memory['memory']
            memory_list.append(human_message)
            configs = []
            servers = []
            for server in self.astra_link.mcp_server_list:
                configs.append(
                    {
                        "name": server.name,
                        "url": f"http://{server.host}:{server.port}/sse"
                    }
                )
                servers = await self.run_with_multiple_servers(configs)
            ans: RunResult = await self.core_ins.run_agent(servers, memory_list)
            ai_message = {
                "role": "assistant",
                "content": ans.final_output
            }
            memory_list.append(ai_message)
            self.astra_memory.write_json_memory(memory, path)
            return ans.final_output


        @self.app.route("/chat",methods = ["POST"])
        def chat():
            pass
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
