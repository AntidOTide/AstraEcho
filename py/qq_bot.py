import requests
from loguru import logger

from send_message import SendMessage


class QQBot(SendMessage):
    @staticmethod
    def qbot_api(url: str, route: str, data: dict[str,]):
        try:
            res = requests.post(url=url + route,
                                params=data).json()
            print(res)
            if res["status"] == "ok":
                logger.info(f"QBot <{route}>api发送成功\n")
                return "消息发送成功"
            else:
                logger.info(res)
                logger.info("私聊消息发送失败，错误信息：" + str(res['wording']))
                return "私聊消息发送失败，错误信息：" + str(res['wording'])
        except Exception as error:
            logger.error("私聊消息发送失败")
            logger.error(error)
            return "私聊消息发送失败"

    @staticmethod
    def send_private_message(url: str, uid: int, message: str):
        try:
            logger.info(f'发送到用户<{uid}>的消息是：{message}')
            res = requests.post(url=url + "/send_private_msg",
                                params={'user_id': uid, 'message': message}).json()
            print(res)
            if res["status"] == "ok":
                logger.info("私聊消息发送成功")
                return "私聊消息发送成功"
            else:
                logger.info(res)
                logger.info("私聊消息发送失败，错误信息：" + str(res['wording']))
                return "私聊消息发送失败，错误信息：" + str(res['wording'])
        except Exception as error:
            logger.error("私聊消息发送失败")
            logger.error(error)
            return "私聊消息发送失败"

    @staticmethod
    def send_group_file(url: str, gid: int, file_path: str, name: str):
        try:
            logger.info(f'发送到用户<{gid}>的消息是')
            res = requests.post(url=url + "/upload_group_file",
                                params={
                                    'group_id': gid,
                                    'file': file_path,
                                    'name': name
                                }).json()
            if res["status"] == "ok":
                logger.info("私聊消息发送成功")
                return "私聊消息发送成功"
            else:
                logger.info(res)
                logger.info("私聊消息发送失败，错误信息：" + str(res['wording']))
                return "私聊消息发送失败，错误信息：" + str(res['wording'])
        except Exception as error:
            logger.error("私聊消息发送失败")
            logger.error(error)
            return "私聊消息发送失败"
