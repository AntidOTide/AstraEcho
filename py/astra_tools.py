import json

import requests

from qq_bot import QQBot
from tool import Tool, astratool


class AstraTools(Tool):
    """
    这里是 Astra Echo 的工具类，用于编写自定义工具
    编写函数的规范:
    1.所有函数必须添加 @astratool 装饰器
    2.函数输入的变量必须给予类型限定，例如： a:int ,x:str , c:None
    3.必须添加注释


    下方编写了两个示例函数


    """

    @astratool
    def sum(self, x: int, y: int):
        """
        Get the result of adding two numbers, the user should supply two numbers to start with.
        :param x: First number.
        :param y: Second number
        :return: the plus
        """
        return x + y

    @astratool
    def multiply(self, a: int, b: int):
        """
        Multiply two numbers.
        :param a: First number.
        :param b: Second number.
        :return: The product.
        """
        return a * b

    @astratool
    def turn_light(self, state: str):
        """
        Change the light ,for example turn_on and turn_off
        :param state:The state you should change you MUST input 'turn_on' or 'turn_off' command and Do not omit '_'
        :return:
        """
        # 防止LLM卖傻不加下划线
        if state == "turn off":
            state = "turn_off"
        elif state == "turn on":
            state = "turn_on"
        api = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhZjUwNWQ2ZDVkOTM0M2Q1OGY2NjlmYjJiNWM1OTVjYiIsImlhdCI6MTczOTYzMzM5MywiZXhwIjoyMDU0OTkzMzkzfQ.3Hm6AheiI78wmI5y_jE8xM8-BOeSVwSK4Agwe7uxmdc"
        post_url = "http://192.168.31.190:8123/api/services/light/" + state
        headers = {
            "Authorization": "Bearer " + api,
            "content-type": "application/json",

        }
        data = {
            "entity_id": "light.yeelink_lamp22_0a61_light"
        }
        post_response = requests.request("POST", post_url, headers=headers, data=json.dumps(data))
        print(post_response)
        print(post_response.json())
        return "success"

    @astratool
    def get_cloud_music_id(self, name: str, singer: str):
        """
        When user need the music or song to listen.
        :param name:The name of song user mention.
        :param singer:The name of singer user mention,if user do not mention ,use 'default' instead it.
        :return:
        """
        url = "https://music-api.yunxge.cn/search?keywords="
        resp = requests.get(url=f"{url}{name}")
        songs = resp.json()['result']['songs']
        current_list: list[dict] = []
        current_singer_list = []
        song_id: int = 0
        for i in songs:
            if i['name'] == name:
                print(f"找到了歌曲{name},作者是:{i['artists'][0]['name']}")
                current_list.append(i)
                current_singer_list.append(i['artists'][0]['name'])
        if singer != 'default':
            for i, x in enumerate(current_singer_list):
                if x == singer:
                    song_id = current_list[i]['id']

            if song_id == 0:
                song_id = current_list[0]['id']
        QQBot.send_private_message(url=self.chat_session['url'], uid=self.chat_session['uid'],
                                   message=f"[CQ:music,type=163,id={song_id}]")
        return f"成功向用户发送歌曲{name}"
