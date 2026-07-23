from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights
from backend import run_travel_agent

# res = search_flights("Plan a 7-day trip to Japan from Beijing, including flights, accommodation, and sightseeing, with a budget of under 20,000.")
# print(res)

# res2 = search_flights("Plan a complete 7 days Japan trip from China under 20000 yuan.")

# print(res2)

# user_input = input("请输入你的问题:")
# res = run_travel_agent(user_query="规划一个7天的北京到日本旅行", thread_id="test")
# print("\n\n FINAL ANSWER:\n", res["answer"])

import asyncio
from mcp_client import get_all_tools, extract_destination, weather_mcp_search, forecast_mcp_search


if __name__ == "__main__":
    # asyncio.run(get_all_tools())

    # weather_data = asyncio.run(weather_mcp_search("Japan"))

    # forecast_data = asyncio.run(forecast_mcp_search("Japan"))
    # print(f"/n{weather_data} /n/n{forecast_data}")

    city = extract_destination("Plan a complete 7 days Japan trip from China including flights, hotels and sightseeing under 20000 yuan.")

    print(city)