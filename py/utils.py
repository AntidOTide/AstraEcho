import asyncio
import json
import os

import aiofiles
import requests
from openai import OpenAI, AsyncOpenAI


# import tiktoken


def get_path():
    path = os.path.abspath(os.getcwd())
    return path


def get_parent_path():
    path = os.path.abspath(os.getcwd())
    parent_dir = os.path.dirname(path)
    return parent_dir


def load_json_file(file_path: str) -> dict:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            file = f.read()
            config_data = json.loads(file)
            return config_data
    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in file: {file_path}")


async def load_json_file_async(file_path):
    """
    异步读取 JSON 文件并解析为 Python 字典。
    :param file_path: JSON 文件路径
    :return: 解析后的 Python 字典
    """
    try:
        # 使用 aiofiles 异步打开文件
        async with aiofiles.open(file_path, mode='r', encoding='utf-8') as f:
            content = await f.read()  # 异步读取文件内容
            data = json.loads(content)  # 将文件内容解析为 JSON
        return data
    except FileNotFoundError:
        raise ValueError(f"File not found: {file_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON format in file: {file_path}")


def write_json_file(path: str, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json_file = json.dumps(data, indent=4, ensure_ascii=False)
        f.write(json_file)
        f.close()


# def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
#     # Returns the number of tokens in a text string.
#     encoding = tiktoken.get_encoding(encoding_name)
#     num_tokens = len(encoding.encode(string))
#     return num_tokens

def send_post_request(
        url: str,
        data: dict
):
    resp = requests.request("POST", url=url, data=data)
    return resp


def send_openai_request(
        api_key: str,
        api_base: str,
        model: str,
        text: str,
        tools: list[dict] | None
):
    client = OpenAI(
        api_key=api_key,
        base_url=api_base
    )
    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": text}],
        tools=tools,
        timeout=10,
        top_p=1
    )
    return resp


def search_serper_online(question, api_key):
    url = "https://cn2us02.opapi.win/api/v1/openapi/search/serper/v1"
    payload = {
        'q': question,
        'cache': '3',
        'gl': 'us',
        'hl': 'en',
        'page': '1',
        'num=': '10'
    }
    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Authorization': api_key
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json()


def summary_answer(search_json):
    text = ""
    print("找到以下信息")
    for i in search_json["organic"]:
        try:
            text += (str(i['position']) + ". " + i["snippet"] + "\n")

        except:
            continue
    print(text)
    question = search_json["searchParameters"]["q"]
    url = "https://cn2us02.opapi.win/v1/chat/completions"

    payload = json.dumps({
        "model": "gpt-4o",
        "messages": [
            {
                "role": "system",
                "content": f"请为我总结以下的几段文字，告诉我{question}是什么，尽可能的详细，包括时间地点人物"
            },
            {
                "role": "user",
                "content": text
            }
        ]
    })
    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json',
        'Authorization': 'sk-iFZyeJYF0FD999fcf3a4T3BLbkFJbeFd232421384aE99462'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.json()['choices'][0]['message']['content'])
    return response.json()['choices'][0]['message']['content']


def chat_with_gpt(user):
    url = "https://cn2us02.opapi.win/v1/chat/completions"

    payload = json.dumps({
        "model": "deepseek-reasoner",
        "messages": [
            {
                "role": "user",
                "content": user
            },
            # {
            #     "role": "user",
            #     "content": system
            # }
        ]
    })
    headers = {
        'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
        'Content-Type': 'application/json',
        'Authorization': 'sk-pHWCo00H54775580D97CT3BlbKFJ3e794eD16949431A84d1'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    resp_json = response.json()
    print(resp_json)
    resp = resp_json['choices'][0]['message']['content']
    return resp


async def chat_deepseek_in_openai():
    client = AsyncOpenAI(
        api_key="sk-pHWCo00H54775580D97CT3BlbKFJ3e794eD16949431A84d1",
        base_url="https://cn2us02.opapi.win/v1/")

    # Round 1
    messages = [{"role": "user", "content": "9.11 and 9.8, which is greater?"}]
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    # reasoning_content = response.choices[0].message.content
    content = response.choices[0].message.content
    print(content)


asyncio.run(chat_deepseek_in_openai())
#
# tools =AstraTools()
# ans =send_openai_request(
#     api_key="sk-pHWCo00H54775580D97CT3BlbKFJ3e794eD16949431A84d1",
#     api_base="https://cn2us02.opapi.win/v1/",
#     model="gpt-4o-mini",
#     text="turn on the light",
#     tools=tools.tool_list
# )
# print(ans)
# tool=ans.choices[0].message.tool_calls
# if tool:
#     tools.tool_parser(tool)
from datetime import datetime


def transform_timestamp():
    # 当前时间
    current_datetime = datetime.now()

    # 格式化为 SQLite 兼容的时间戳格式
    sqlite_timestamp = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    return sqlite_timestamp
