from agents.mcp.server import MCPServerSse
import asyncio
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel
from agents.mcp import MCPServer

from AstraConfig import AstraConfig


async def run(mcp_server: MCPServer):
    AstraConfig.load(r"config/config.json")
    external_client = AsyncOpenAI(
        api_key=AstraConfig.get("AstraCore").get("api").get("api_key"),
        base_url=AstraConfig.get("AstraCore").get("api").get("api_base"),
    )
    agent = Agent(
        name="Assistant",
        instructions="",
        mcp_servers=[mcp_server],
        model=OpenAIChatCompletionsModel(
            model="gpt-4o-mini",
            openai_client=external_client,
        ),


    )

    message = "请问荆州市的天气怎么样？"
    print(f"Running: {message}")
    result = await Runner.run(starting_agent=agent, input=message)
    print(result.final_output)




async def main():
    async with MCPServerSse(
            name="SSE Python Server",
            params={
                "url": "http://localhost:8000/sse",
            },
    )as server:
        await run(server)


if __name__ == "__main__":
    asyncio.run(main())
