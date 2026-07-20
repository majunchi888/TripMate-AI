from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights
from backend import run_travel_agent

# res = search_flights("Plan a 7-day trip to Japan from Beijing, including flights, accommodation, and sightseeing, with a budget of under 20,000.")
# print(res)

res2 = search_flights("Plan a complete 7 days Japan trip from China under 20000 yuan.")

print(res2)

# user_input = input("请输入你的问题:")
# res = run_travel_agent(user_query=user_input, thread_id="test")
# print("\n\n FINAL ANSWER:\n", res["answer"])
