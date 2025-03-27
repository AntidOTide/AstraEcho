import asyncio
import copy
import json
import os
import random
import re

import aiosqlite
import jmcomic
from flask import Flask, render_template, request, redirect, url_for
from jmcomic import JmOption
from loguru import logger
from openai import NOT_GIVEN, AsyncOpenAI

from astra_tools import AstraTools
from qq_bot import QQBot
from utils import load_json_file, write_json_file, get_parent_path, load_json_file_async, transform_timestamp


class AstraEcho:
    def __init__(self):
        self.nickname: str | None = None
        self.sender: str | None = None
        self.uid: int | None = None
        self.raw_message: str | None = None
        self.llm_bot_server: Flask = Flask(__name__)
        self.tools: AstraTools | NOT_GIVEN
        self.config_data_path = "../config/config.json"
        self.config_data = load_json_file(self.config_data_path)
        self.port = self.config_data['AstraEcho']['port']
        self.temp = self.config_data['AstraEcho']['model_temp']
        self.request_method = self.config_data['AstraEcho']['request_method']
        self.is_write_memory = self.config_data['AstraEcho']['is_write_memory']
        self.debug_mode = self.config_data['AstraEcho']['debug_mode']
        self.is_use_tools = self.config_data['AstraEcho']['is_use_tools']
        self.output_method = self.config_data['AstraEcho']['output_method']
        self.qq_no = self.config_data['qq_bot']['qq_no']
        self.memory_json: dict | None = None
        self.db: aiosqlite.Connection | None = None

        if self.is_use_tools:
            self.tools = AstraTools()
        else:
            self.tools = NOT_GIVEN

        if self.output_method == "qq_bot":
            self.send_message = QQBot()
            self.qq_bot_url = self.config_data['qq_bot']['cqhttp_url']
        if self.request_method == "api":
            self.api_key = self.config_data['openai']['OPENAI_API_KEY']
            self.api_base = self.config_data['openai']['OPENAI_API_BASE']
            self.model = self.config_data['openai']['OPENAI_MODEL']

        elif self.request_method == "local":
            self.api_key = self.config_data['local']['LOCAL_API_KEY']
            self.api_base = self.config_data['local']['LOCAL_API_BASE']
            self.model = self.config_data['local']['LOCAL_MODEL']


        else:
            raise ValueError("Invalid configuration provided. Please check your config.")

        # self.client = OpenAI(
        #     base_url=self.api_base,
        #     api_key=self.api_key,
        # )
        self.client = AsyncOpenAI(
            base_url=self.api_base,
            api_key=self.api_key,
        )
        self.session_data = {}

        self._begin()

    async def connect_database(self):
        self.db = await aiosqlite.connect(self.config_data['AstraEcho']['db_path'])

    async def disconnect_database(self):
        if self.db:
            await self.db.close()

    def _reset_instance(self):
        """重新实例化自身，并替换当前实例"""
        # 创建一个新的实例
        new_instance = AstraEcho()
        # 将当前实例的属性复制到新实例
        new_instance.__dict__.update(self.__dict__)
        # 替换当前实例
        self.__dict__.update(new_instance.__dict__)

    def _begin(self):
        """初始化flask服务的路由"""

        @self.llm_bot_server.route("/", methods=["GET"])
        def index():
            return "该接口正常工作"

        @self.llm_bot_server.route("/", methods=["POST"])
        async def get_message_data():
            await self.connect_database()
            logger.info("收到上报消息:")
            logger.info(request.get_json())
            self.session_data = request.get_json()
            await self._process_message_async(self.session_data)
            return "ok"

        @self.llm_bot_server.route('/setting')
        def setting():
            config = self._read_config()
            return render_template('index.html', config=config)

        # 编辑配置文件的页面
        @self.llm_bot_server.route('/edit', methods=['GET', 'POST'])
        def edit():
            config = self._read_config()
            if request.method == 'POST':
                # 更新配置文件
                for key in request.form:
                    keys = key.split('.')  # 支持嵌套键（如 "database.host"）
                    current = config
                    for k in keys[:-1]:
                        if k not in current:
                            current[k] = {}
                        current = current[k]
                    current[keys[-1]] = request.form[key]
                self._save_config(config)
                self._reset_instance()
                redirect(url_for('setting'))
                return redirect(url_for('setting'))
            return render_template('edit.html', config=config)

    # <-----------------------Async-------------------------->
    async def _load_private_memory_async(self):
        await self._check_memory_folder_async(is_private=True)
        memory_json = await load_json_file_async(f"../memory/private/{self.uid}/{self.uid}.json")
        return memory_json

    async def _check_memory_folder_async(self, is_private: bool = False, is_group_bool: bool = False):
        """
        检查记忆文件夹是否存在，如果不存在则初始化。
        :param is_private: 是否为私有文件夹
        :param is_group_bool: 是否为群组文件夹
        """
        if is_private:
            memory_path = f"../memory/private/{self.uid}/{self.uid}.json"
            await self._initialize_memory_folder(memory_path)

        elif is_group_bool:
            memory_path = f"../memory/group/{self.gid}/{self.gid}.json"
            await self._initialize_memory_folder(memory_path)

        else:
            raise ValueError("ERROR: 必须指定 is_private 或 is_group_bool")

    async def _initialize_memory_folder(self, memory_path: str):
        """
        异步初始化记忆文件夹。
        :param memory_path: 文件夹路径
        """
        # 检查文件夹是否存在
        if not await self._async_path_exists(memory_path):
            # 创建文件夹
            await asyncio.to_thread(os.makedirs, memory_path)

            # 创建 JSON 文件
            data = {
                "config": {
                    "AI_Name": "AstraEcho"
                },
                "memory": [
                    {
                        "role": "system",
                        "content": "You' are a helpful assistant"
                    }
                ]
            }

            # 异步写入 JSON 数据
            async with aiofiles.open(memory_path, mode='w', encoding='utf-8') as f:
                await f.write(json.dumps(data, indent=4, ensure_ascii=False))

    async def _async_path_exists(self, path: str) -> bool:
        """
        异步检查路径是否存在。
        :param path: 路径
        :return: 布尔值，表示路径是否存在
        """
        return await asyncio.to_thread(os.path.exists, path)

    async def _run_chat_openai_async(self, message: list):
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=message,
                tools=self.tools.tool_list,
                timeout=10,
                top_p=float(self.temp)
            )
            print(f"Response\n{response}")
            return response
        except Exception as e:
            # 捕获异常并返回错误信息
            raise Exception(f"Error occurred: {str(e)}")

    async def _load_private_memory(self):
        self._check_user_memory_folder(is_private=True)
        memory_json = load_json_file(f"../memory/private/{self.uid}/{self.uid}.json")
        return memory_json

    async def _process_message_command_private_async(self) -> bool:
        command_dict = {
            "/获取会话": "获取当前会话信息",
            "/更改人格 + 你需要设定的人格 ": "更改当前会话中的人格"

        }
        resp = ""
        if self.raw_message.strip().startswith("/获取会话"):
            resp = "当前会话信息为：\n"
            resp += f"窗口类型:\n"
            resp += f"QQ:{self.uid}+\n"
            resp += f"昵称:{self.nickname}+\n"
            resp += f"模型:{self.model}+\n"
            role_dict = memory_json['memory'][0]
            if role_dict['role'] == "system":
                resp += f"人格:{role_dict['content']}\n"
            else:
                resp += f"人格:未找到配置，人格文件出错！\n"
            resp += f"AstraEchoAI名称:{memory_json['config']['AI_Name']}"
        elif self.raw_message.strip().startswith("/jm"):
            print(message)
            id = self._jm_download(message)
        elif self.raw_message.strip().startswith("/"):
            resp = "test"

        else:
            return False
        print("resp" + resp)
        await self.send_message.send_private_message_async(url=self.qq_bot_url, uid=self.uid, message=resp)
        return True

    async def _get_private_message_info_async(self):
        self.sender = self.session_data.get('sender')  # 获取发送者信息
        self.uid = int(self.sender.get('user_id'))  # 获取信息发送者的 QQ号码
        self.nickname = self.sender.get('nickname')  # 获取信息发送者的 QQ昵称
        self.raw_message = self.session_data.get('raw_message')
        self.memory_json = await self._load_private_memory_async()

    async def _process_message_async(self, data: dict):
        if data['post_type'] == "message":
            if data.get('message_type') == 'private':
                await self._get_private_message_info_async()
                if await self._process_message_command_private_async():  # 如果是私聊信息
                    return "ok"
                await self._process_private_message_async()
            elif data.get('message_type') == 'group':
                message = data.get('raw_message')
                self.gid = request.get_json().get('group_id')  # 群号
                self.uid = request.get_json().get('sender').get('user_id')  # 发言者的qq号
                if str("[CQ:at,qq=2265917047,") in message:
                    print("msg" + message)
                    pattern = r'\[CQ:at,qq=2265917047,name=[^\]]+\]'
                    # 使用 re.sub 替换匹配到的内容为空字符串
                    result = re.sub(pattern, '', message)
                    # 返回处理后的字
                    message = result.strip()
                    print("replaced msg" + message)
                    self._process_message_command_group(message)

    async def check_user_is_existed(self):
        result = await self.db.execute("""
            SELECT user_id FROM private_chat_user WHERE qq_no = ? OR nickname = ?
        """, (self.uid, self.nickname))
        existing_user = await result.fetchone()
        if existing_user is None:
            await self.db.execute("""
            INSERT INTO private_chat_user (qq_no,nickname)VALUES(?,?)"""
                                  , (self.uid, self.nickname))

    async def load_private_memory_from_database(self):
        self.memory: list[dict] = []

        role_result = await self.db.execute("""
        SELECT * FROM private_chat_user WHERE qq_no = ? OR nickname = ?
        """, (self.uid, self.nickname))

        user_info = await role_result.fetchone()
        role = user_info[4]
        self.memory.append(
            {
                "role": "system",
                "content": role
            }
        )
        memory_result = await self.db.execute("""
        SELECT * FROM private_messages WHERE qq_no = ? ORDER BY timestamp
        """, (self.uid,))
        memory = await memory_result.fetchall()
        for i in memory:
            print(i)
            print(type(i))
            if i[2] == 'user':
                self.memory.append({
                    "role": i[2],
                    "content": i[3]
                })
            if i[2] == 'assistant':
                self.memory.append({
                    "role": i[2],
                    "content": i[3]
                })
            else:
                pass

    async def _process_private_message_async(self):
        """处理私人信息"""
        logger.info(f"收到私聊消息:{self.nickname}<{self.uid}>:{self.raw_message}")
        await self.check_user_is_existed()
        await self.load_private_memory_from_database()
        # self.memory_json['memory'].append({'role': 'user', 'content': self.raw_message})
        self.memory.append({'role': 'user', 'content': self.raw_message})
        chat_message = copy.deepcopy(self.memory)
        answer = ''
        print(chat_message)
        answer = await self._run_chat_openai_async(chat_message)
        if self.is_use_tools:
            try:
                is_tools_call = answer.choices[0].message.tool_calls[0]
                if is_tools_call:
                    self.tools._get_chat_session(url=self.qq_bot_url, uid=self.uid)
                    tools_return = self.tools.tool_parser(is_tools_call)
                    print(tools_return)
                    chat_message.append(answer.choices[0].message)
                    chat_message.append(
                        {"role": "tool", "tool_call_id": is_tools_call.id, "content": str(tools_return)})
                    answer = await self._run_chat_openai_async(chat_message)
            except TypeError as t:
                print("本次对话无工具调用")
        resp = answer.choices[0].message.content
        logger.info(f"{self.model}模型返回消息:{resp}")
        if '<think>' in resp:
            pattern = r'<think>.*?</think>'
            resp = re.sub(pattern, '', resp, flags=re.DOTALL).strip()
        # self.memory.append({'role': 'assistant', 'content': resp})
        if self.is_write_memory:
            await self._write_private_memory_from_database(transform_timestamp(), resp)
            min_time = self.config_data['qq_bot']['reply_waiting_time']['min_time']
            max_time = self.config_data['qq_bot']['reply_waiting_time']['max_time']
            waiting_time = float('%.2f' % random.randrange(min_time, max_time)) * 60
            print(resp)
        await self.send_message.send_private_message_async(url=self.qq_bot_url, uid=self.uid, message=resp,
                                                           waiting_time=waiting_time)

    async def _write_private_memory_from_database(self, user_time, resp):
        logger.info("Writing private memory to database")
        await self.db.execute("""
        INSERT INTO private_messages (qq_no,role,content,timestamp)VALUES(?,?,?,?);

        """, (self.uid, "user", self.raw_message, user_time))

        await self.db.execute("""
        INSERT INTO private_messages (qq_no,role,content,timestamp)VALUES(?,?,?,?)
        """, (self.uid, "assistant", resp, transform_timestamp()))
        await self.db.commit()
        logger.info("Write private memory to database finished")
    def _jm_download(self, command: str):

        command_list = command.split()
        print(command_list)
        option: JmOption
        option = jmcomic.create_option('option.yml')
        if command_list[0] != "/jm" or len(command_list) == 1:
            return "Error"

        if len(command_list) > 2:
            for command in command_list:
                if command == "-pdf":
                    option.call_all_plugin("save_pdf")
        jmcomic.download_album(command_list[1], option=option)
        # pdf =open(f"../pdf/{command_list[1]}/{command_list[1].pdf}", 'rb')
        return command_list[1]

    def _process_message_command_group(self, message: str) -> bool:
        command_dict = {
            "/jm": "获取当前会话信息",
        }
        if message.strip().startswith("/获取会话"):
            resp = "当前会话信息为：\n"
            resp += f"窗口类型:\n"
            resp += f"QQ:{self.uid}\n"
            resp += f"昵称:{self.nickname}\n"
            resp += f"模型:{self.model}\n"
            role_dict = memory_json['memory'][0]
            if role_dict['role'] == "system":
                resp += f"人格:\n{role_dict['content']}\n"
            else:
                resp += f"人格:未找到配置，人格文件出错！\n"
            resp += f"AstraEchoAI名称:{memory_json['config']['AI_Name']}"
        elif message.strip().startswith("/jm"):
            id = self._jm_download(message)
            print(id)
            file_path = get_parent_path()
            self.send_message.send_group_file(url=self.qq_bot_url, gid=self.gid,
                                              file_path=file_path + f"\pdf\{id}.pdf",
                                              name=f"{id}.pdf")
        elif message.strip().startswith("/"):
            resp = "test"

        else:
            return False

        return True

    def _run_chat_openai(self, message: list):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=message,
            tools=self.tools.tool_list,
            timeout=10,
            top_p=float(self.temp)
        )
        print(f"Response\n{response}")
        return response

    def _run_chat_local(self, message: list):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=message,
            tools=self.tools.tool_list,
            timeout=10,
            top_p=float(self.temp)
        )
        print(f"Response\n{response}")
        return response

    def _check_user_memory_folder(self, is_private: bool = False, is_group_bool: bool = False):
        if is_private:
            memory_path = f"../memory/private/{self.uid}"
            if not os.path.exists(memory_path):
                os.makedirs(memory_path)
                with open(memory_path + f"/{self.uid}.json", "w") as f:
                    data = {
                        "config": {
                            "AI_Name": "AstraEcho"
                        },
                        "memory": [{
                            "role": "system",
                            "content": "You' are a helpful assistant"
                        }
                        ]
                    }
                    f.write(json.dumps(data, indent=4, ensure_ascii=False))
                    f.close()
        if is_group_bool:
            memory_path = f"../memory/group/{self.uid}"
            if not os.path.exists(memory_path):
                os.makedirs(memory_path)
                with open(memory_path + f"/{self.uid}.json", "w") as f:
                    data = {
                        "config": {
                            "AI_Name": "AstraEcho"
                        },
                        "memory": [{
                            "role": "system",
                            "content": "You' are a helpful assistant"
                        }]
                    }
                    f.write(json.dumps(data, indent=4, ensure_ascii=False))
                    f.close()
        else:
            raise ValueError("ERROR")

    def _load_private_memory(self):
        self._check_user_memory_folder(is_private=True)
        memory_json = load_json_file(f"../memory/private/{self.uid}/{self.uid}.json")
        return memory_json

    def _write_private_memory(self, data):
        write_json_file(f"../memory/private/{self.uid}/{self.uid}.json", data)

    def _read_config(self):
        return self.config_data

    # 保存配置文件
    def _save_config(self, config):
        with open(self.config_data_path, 'w') as f:
            json.dump(config, f, indent=4)  # 使用 indent 格式化 JSON

    def run(self):
        self.llm_bot_server.run(port=self.port, debug=self.debug_mode)
