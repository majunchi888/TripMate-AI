import os
import asyncio
import re
import certifi
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")

# 创建mcp步骤：1. MCP_client 2. MCP_server 3. Tools(async) 4.api

client = MultiServerMCPClient(
    {
            "tavily": {
                    "transport": "streamable_http",
                    "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}",
                }
    }
)

async def get_all_tools():
    tools = await client.get_tools()
    
    return tools

# only returns the tavily_search tool
tavily_search_tool = None

async def get_tavily_search_tool():
    global tavily_search_tool
    if tavily_search_tool is not None:
        return

    tools = await client.get_tools()
    print("\nAVAILABLE MCP TOOLS:\n")

    for tool in tools:
        print(tool.name)

        tavily_search_tool = next(
            tool for tool in tools if tool.name == "tavily_search"
        ) # 只返回第一个tavily_search tool

# 调用 tavily_search tool 的入口函数        
async def tavily_mcp_search(query: str):
    await get_tavily_search_tool()
    result = await tavily_search_tool.ainvoke( # type: ignore
            {
                "query": query
            }
    )
    return result