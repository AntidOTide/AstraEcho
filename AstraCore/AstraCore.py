from openai import AsyncOpenAI
from AstraNex import AstraLogger
from agents import Agent, Runner, OpenAIChatCompletionsModel, TResponseInputItem
from agents.mcp import MCPServer

from config_accessor import OPENAI_API_KEY, OPENAI_API_BASE, OPENAI_MODEL, OPENAI_TEMPERATURE, OPENAI_PROMPT


class AstraCore:
    def __init__(self):
        self.client = None
        self.init_openai()

    def init_openai(self):
        AstraLogger.info("正在配置  |星核|  AstraCore")
        self.client = AsyncOpenAI(
                base_url=OPENAI_API_BASE.config_key,
                api_key=OPENAI_API_KEY.config_key,
        )
    async def _run_chat_openai_async(self, message: list):
        """星核初燃，异步回响"""
        try:
            response = await self.client.chat.completions.create(
                model=OPENAI_MODEL.config_key,
                messages=message,
                timeout=10,
                top_p=float(OPENAI_TEMPERATURE.config_key),
            )
            AstraLogger.info(f"Response\n{response}")
            return response
        except Exception as e:
            # 捕获异常并返回错误信息
            raise Exception(f"Error occurred: {str(e)}")

    async def run_agent(self,mcp_server_list: list[MCPServer],message: str | list[TResponseInputItem]):
        agent = Agent(
            name="Assistant",
            instructions=OPENAI_PROMPT.config_key,
            mcp_servers=mcp_server_list,
            model=OpenAIChatCompletionsModel(
                model=OPENAI_MODEL.config_key,
                openai_client=self.client,
            ),
        )

        AstraLogger.info(f"Running: {message}")
        result = await Runner.run(starting_agent=agent, input=message)
        return result

# async def main():
#     AstraConfig.load(r"../config/config.json")
#     a = AstraCore()
#     message:list =[
#         {
#             "role":"system",
#             "content":"You are a helpful AI"
#          },
#         {
#             "role":"user",
#             "content":"Hello, World!"
#         }
#     ]
#
#     print(await a._run_chat_openai_async(message))
if __name__ == "__main__":
    # asyncio.run(main())
    pass