from agents.mcp import MCPServerSse
from flask import Flask, request, jsonify
from sqlite3 import Connection

from AstraCore import AstraCore


class AstraRoute:
    def __init__(self, app: Flask, db_connection: Connection,astra_core:AstraCore):
        self.app = app
        self.db_connection = db_connection
        self.core_ins = astra_core
        self.register_routes()

    def register_routes(self):
        @self.app.route("/", methods=["GET"])
        def index():
            return "该接口正常工作"

        @self.app.route("/send", methods=["GET"])
        async def send():
            message = request.args.get('message')
            async with MCPServerSse(
                    name="SSE Python Server",
                    params={
                        "url": "http://localhost:8000/sse",
                    },
            ) as server:
                ans = await self.core_ins.run_agent(server,message)
            print(ans)
            return ans





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
