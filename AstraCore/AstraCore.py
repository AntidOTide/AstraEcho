import asyncio

from openai import AsyncOpenAI

from AstraConfig import AstraConfig

class AstraCore:
    def __init__(self):
        self.client = None
        self.init_openai()

    def init_openai(self):
        self.client = AsyncOpenAI(
            base_url=AstraConfig.get("AstraCore").get("api").get("api_base"),
            api_key=AstraConfig.get("AstraCore").get("api").get("api_key"),
        )
    async def _run_chat_openai_async(self, message: list):
        """星核初燃，异步回响"""
        api_config:dict = AstraConfig.get("AstraCore").get("api")
        model =api_config.get("model")
        temperature = api_config.get("temperature")
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=message,
                # tools=self.tools.tool_list,
                timeout=10,
                top_p=float(temperature),
            )
            print(f"Response\n{response}")
            return response
        except Exception as e:
            # 捕获异常并返回错误信息
            raise Exception(f"Error occurred: {str(e)}")


async def main():
    AstraConfig.load(r"../config/config.json")
    a = AstraCore()
    message:list =[
        {
            "role":"system",
            "content":"You are a helpful AI"
         },
        {
            "role":"user",
            "content":"Hello, World!"
        }
    ]

    print(await a._run_chat_openai_async(message))
if __name__ == "__main__":
    asyncio.run(main())