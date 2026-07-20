from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights
from backend import run_travel_agent

# res = search_flights("Plan a 7 days Japan trip from China")
# print(res)

user_input = input("请输入你的问题:")
res = run_travel_agent(user_query=user_input, thread_id="test")
print("\n\n FINAL ANSWER:\n", res["answer"])
