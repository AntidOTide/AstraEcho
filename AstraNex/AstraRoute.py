from agents import RunResult
from agents.mcp import MCPServerSse, MCPServer
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
            server_list :list[MCPServer]= []
            for server in self.astra_link.mcp_server_list:
                async with MCPServerSse(
                        name=server.name,
                        params={
                            "url": f"http://{server.host}:{server.port}/sse",
                        },
                ) as sse_server:
                    server_list.append(sse_server)
            ans:RunResult = await self.core_ins.run_agent(server_list,memory_list)
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
