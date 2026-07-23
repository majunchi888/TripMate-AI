import os
import asyncio
from re import search
import certifi
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

load_dotenv()


TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATION_STACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(model = "llama-3.3-70b-versatile", api_key = GROQ_API_KEY) # type: ignore

client = MultiServerMCPClient(
    {
            "tavily": {
                    "transport": "streamable_http", # remote mcp server
                    "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}",
                },

            "aviationstack": {
                    "transport": "stdio", # local mcp server
                    "command": "uvx",
                    "args": [
                        "aviationstack-mcp"
                    ],
                    "env": {
                        "AVIATION_STACK_API_KEY": AVIATION_STACK_API_KEY
                    }
            },
            "weather": {
                    "transport": "stdio", # local mcp server
                    "command": r"D:\agent-project\TripMate-AI\.venv\Scripts\python.exe",
                    # "command": r"C:\Users\MI\AppData\Roaming\uv\python\cpython-3.13.13-windows-x86_64-none\python.exe",
                    "args": [
                        r"D:\agent-project\TripMate-AI\custom_weather_mcp_server.py"
                    ],
                    "env": {
                        "OPENWEATHER_API_KEY": OPENWEATHER_API_KEY
                    }
            }

    } # type: ignore
)

async def get_all_tools():
    tools = await client.get_tools()

    print("\nAVAILABLE MCP TOOLS:\n")
    for tool in tools:
            print(tool.name)

# ===================================================
# Tavily and Aviationstack tools
# ===================================================

search_tool = None
aviation_tools = {}

async def initialize_mcp():
    
    global search_tool
    global aviation_tools

    if search_tool is not None and aviation_tools:
        return

    tools = await client.get_tools()

    print("\nAVAILABLE MCP TOOLS:\n")

    for tool in tools:
        print(tool.name)

    search_tool = next(tool for tool in tools if tool.name == "tavily_search") # 只返回第一个tavily_search tool

    aviation_tools = {tool.name: tool for tool in tools if tool.name != "tavily_search"}
    # print(aviation_tools)

# 调用 tavily_search tool      
async def tavily_mcp_search(query: str):
    await initialize_mcp()
    result = await search_tool.ainvoke( # type: ignore
            {
                "query": query
            }
    )
    return result    

# 调用 Aviationstack tools
async def aviation_mcp_call(tool_name: str, tool_args: dict = None): # type: ignore
    tools = await client.get_tools()

    tool = next(tool for tool in tools if tool.name == tool_name)
    
    result = await tool.ainvoke( # type: ignore
            tool_args or {}
    )
    return result
    
# ===================================================
# Weather tools
# ===================================================
weather_tool = None
forecast_tool = None

async def initialize_weather_tools():
    global weather_tool
    global forecast_tool

    if weather_tool is not None:
        return

    tools = await client.get_tools()

    weather_tool = next(tool for tool in tools if tool.name == "get_current_weather")
    forecast_tool = next(tool for tool in tools if tool.name == "get_forecast")



async def weather_mcp_search(city: str):   
    await initialize_weather_tools()

    result = await weather_tool.ainvoke( # type: ignore
            {
                "city": city
            }
    )
    return result


async def forecast_mcp_search(city: str):   
    await initialize_weather_tools()

    result = await forecast_tool.ainvoke( # type: ignore
            {
                "city": city
            }
    )
    return result

# ===================================================
# Destination extractor
# ===================================================

def extract_destination(query: str):

    prompt = f"""Extract only the destination city or country.
    
    Query:
    {query}

    Return only destination name like "Japan"，""Tokyo".
    """

    response = llm.invoke(prompt)

    return response.content.strip() # type: ignore