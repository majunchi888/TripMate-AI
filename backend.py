import asyncio
import json
import os
import certifi
from dotenv import load_dotenv
import time

load_dotenv(override=True)

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

from typing import Any, TypedDict, Annotated
import operator
import uuid

import psycopg
from psycopg.rows import dict_row

from langgraph.graph import StateGraph, START, END 
from langgraph.types import Command, interrupt
from langgraph.checkpoint.postgres import PostgresSaver

from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, AIMessage
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq

from mcp_client import tavily_mcp_search, aviation_mcp_call, forecast_mcp_search, weather_mcp_search

def get_database_url():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL is missing. Please add your Render PostgresSQL External Database URL in your .env file")
    # if sslmode is not set, add it
    if "sslmode=" not in database_url:
        separator = "&" if "?" in database_url else "?"
        database_url = f"{database_url}{separator}sslmode=require"

    return database_url

# ===========================================================================
# LLM
llm = ChatGroq(model = "openai/gpt-oss-120b", api_key = os.getenv("GROQ_API_KEY"))

llm_qwen = ChatOpenAI(
    api_key=os.getenv("ALIYUN_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model_name="qwen3.7-plus",
    temperature=0.2,
)
# ===========================================================================
# State
class TravelState(TypedDict):
    """TripMate Agent 的共享状态，在各个 LangGraph 节点之间传递数据。"""
    # 对话历史，使用 operator.add 自动追加消息，而不是覆盖
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str           # 原始输入

    # Original specialist results    
    flight_results: str
    hotel_results: str
    weather_results: str
    itinerary: str

    # Supervisor + guardrail state
    guardrail_allowed: bool        # 是否开启防护
    guardrail_reason: str          # 拒绝原因
    selected_agents: list[str]     # 选择的agents
    trip_constraints: dict[str, Any]  # 提取旅行约束条件 例如旅行时间，预算等
    supervisor_reasoning: str        # 管理员的理由

    # New budget + HITL state
    budget_results: str
    approval_request: str   # hitl 管理员的审批请求
    approved: bool
    human_feedback: str
    final_response: str

    llm_calls: int

# ===========================================================================

# Shared helpers
# =========================
KNOWN_AGENTS = {
    "flight_agent",
    "hotel_agent",
    "weather_agent",
    "budget_agent",
    "itinerary_agent",
}

AGENT_ORDER = [
    "flight_agent",
    "hotel_agent",
    "weather_agent",
    "budget_agent",
    "itinerary_agent",
]


def _llm_text(system_prompt: str, user_prompt: str) -> str:
    response = llm.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
    )
    return str(response.content)

def _llm_qwen_text(system_prompt: str, user_prompt: str) -> str:
    response = llm_qwen.invoke(
        [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
    )
    return str(response.content)

# json 格式在agent之间传递比较方便
def _json_from_llm(text: str) -> dict[str, Any]:
    """Extract the first complete JSON object returned by the model."""
    start = text.find("{")
    end = text.rfind("}")  # 从右往左找最后一个 } 的位置

    if start == -1 or end == -1 or end < start:
        raise ValueError("The model did not return a JSON object.")

    return json.loads(text[start : end + 1]) # 用 json.loads 解析成 Python 字典并返回


def _empty_constraints() -> dict[str, Any]:
    return {
        "destination": "",
        "origin": "",
        "duration": "",
        "budget": "",
        "travel_style": "",
        "special_preferences": [],
    }

async def get_airport_iata(city_or_country: str, limit: int = 5):
    """把城市/国家转换成机场 IATA 代码列表"""
    result = await aviation_mcp_call(
        "list_airports",
        {
            "search": city_or_country,
            "limit": limit
        }
    )
    return result

# =========================
# Supervisor Agent + Input Guardrail
# =========================
def supervisor_agent(state: TravelState):
    query = state["user_query"]
    llm_calls = state.get("llm_calls", 0)

    guardrail_prompt = f"""
Determine whether the following request belongs to travel planning or travel
information. Valid requests can include destinations, flights, hotels, weather,
budgets, visas, transportation, sightseeing, food, packing, or itineraries.

Block clearly unrelated requests and requests asking for harmful or illegal
instructions. Do not block a valid travel request merely because some details
are missing.

Return strict JSON only:
{{
  "allowed": true,
  "reason": ""
}}

User request:
{query}
"""
    # Guardrail 在检查用户请求时发生了任何异常（比如模型调用失败、网络超时、解析错误、代码 bug 等），不要把请求拦住，而是放行（allowed = True），并记录原因是“兜底放行”。不会因为 Guardrail 服务临时出问题，导致整个系统不可用
    try:
        guardrail_raw = _llm_text(
            "You are the input guardrail for a travel-planning application."
            "Return strict JSON only.",
            guardrail_prompt,
        )
        guardrail_result = _json_from_llm(guardrail_raw)
        allowed = bool(guardrail_result.get("allowed", True))
        guardrail_reason = str(guardrail_result.get("reason", "")).strip()
        llm_calls += 1
    except Exception as exc:
        print(f"Guardrail fallback used: {exc}")
        allowed = True
        guardrail_reason = "Guardrail validation fallback allowed the request."

    if not allowed:
        reason = guardrail_reason or (
            "TripMate AI can only help with travel-planning requests. "
            "Please ask about a destination, flight, hotel, weather, budget, "
            "or itinerary."
        )
        return {
            "guardrail_allowed": False,
            "guardrail_reason": reason,
            "selected_agents": [],
            "trip_constraints": _empty_constraints(),
            "supervisor_reasoning": reason,
            "final_response": reason,
            "messages": [AIMessage(content=f"Guardrail blocked request: {reason}")],
            "llm_calls": llm_calls,
        }

    supervisor_prompt = f"""
You are the supervisor of a multi-agent travel-planning system.
Choose only the specialist agents needed for the user_request, and do not include the unnecessary agents.

Available agents:
- flight_agent: flights, airports, airlines, routes, airfare, or booking advice
- hotel_agent: hotels, accommodation, neighborhoods, or places to stay
- weather_agent: weather, climate, season, forecast, or packing advice
- budget_agent: cost, affordability, price limits, or budget feasibility
- itinerary_agent: creates the integrated travel plan and must always be included

Return strict JSON only using this schema:
{{
  "selected_agents": ["flight_agent", "hotel_agent", "weather_agent", "budget_agent", "itinerary_agent"],
  "trip_constraints": {{
    "destination": "",
    "origin": "",
    "duration": "",
    "budget": "",
    "travel_style": "",
    "special_preferences": []
  }},
  "reasoning": ""
}}

User request:
{query}
"""

    try:
        supervisor_raw = _llm_text(
            "You route work to travel specialist agents. Return strict JSON only.",
            supervisor_prompt,
        )
        parsed = _json_from_llm(supervisor_raw)
        requested_agents = parsed.get("selected_agents", [])
        selected_agents = [
            name for name in AGENT_ORDER
            if name in requested_agents and name in KNOWN_AGENTS
        ]

        # The itinerary agent integrates whichever specialist results were selected.
        if "itinerary_agent" not in selected_agents:
            selected_agents.append("itinerary_agent")

        constraints = _empty_constraints()
        parsed_constraints = parsed.get("trip_constraints", {})
        if isinstance(parsed_constraints, dict):
            constraints.update(parsed_constraints)

        reasoning = str(parsed.get("reasoning", "")).strip()
        llm_calls += 1
    except Exception as exc:
        print(f"Supervisor fallback used: {exc}")
        # Original workflow behavior is preserved as the fallback.
        selected_agents = AGENT_ORDER.copy()
        constraints = _empty_constraints()
        reasoning = (
            "Supervisor parsing failed, so the original full travel workflow "
            "was selected as a safe fallback."
        )

    return {
        "guardrail_allowed": True,
        "guardrail_reason": guardrail_reason,
        "selected_agents": selected_agents,
        "trip_constraints": constraints,
        "supervisor_reasoning": reasoning,
        "messages": [AIMessage(content="Supervisor created the agent plan.")],
        "llm_calls": llm_calls,
    }


# =========================
# Guardrail blocked response
# =========================
def guardrail_blocked_agent(state: TravelState):
    reason = state.get("final_response") or state.get("guardrail_reason") or (
        "This request was blocked by the travel input guardrail."
    )
    return {
        "final_response": reason,
        "messages": [AIMessage(content=reason)],
    }


# =========================
# Flight Agent - original behavior kept
# =========================
def flight_agent(state: TravelState):

    print("\nINSIDE FLIGHT AGENT\n")

    query = state["user_query"]

    constraints = state.get(
        "trip_constraints",
        {}
    )

    origin = (
        constraints.get("origin", "")
        or "北京"
    )

    destination = (
        constraints.get("destination", "")
        or "东京"
    )

    print(f"origin: {origin}")
    print(f"destination: {destination}")

    try:

        # ==========================================
        # 1. Flight Search
        # ==========================================

        flight_query = (
            f"{origin} {destination} "
            f"direct flights airlines "
            f"flight duration airfare"
        )

        print("\nFLIGHT SEARCH QUERY:")
        print(flight_query)

        search_result = asyncio.run(
            tavily_mcp_search(
                flight_query,
                max_results=5
            )
        )

        # ==========================================
        # 2. 清洗
        # ==========================================

        flight_results = clean_tavily_results(
            search_result
        )

        print("\nFLIGHT SEARCH RESULT:")
        print(flight_results)

    except Exception as exc:

        print(
            f"FLIGHT AGENT MCP ERROR: "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

        flight_results = []

    return {
        "flight_results": flight_results,

        "messages": [
            AIMessage(
                content="Flight information fetched."
            )
        ],

        # 没调用 LLM
        "llm_calls": state.get(
            "llm_calls",
            0
        ),
    }

def clean_tavily_results(result, max_results=5):
    """
    解析 Tavily MCP 返回结果，并提取有效搜索结果。
    """

    if not result:
        return []

    # ==========================================
    # 1. MCP 返回通常是：
    #
    # [
    #     {
    #         "type": "text",
    #         "text": "JSON字符串"
    #     }
    # ]
    # ==========================================

    if isinstance(result, list):

        # 找到 text
        text = None

        for item in result:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    text = item.get("text")
                    break

        if text is None:
            return []

        # JSON 字符串 → dict
        if isinstance(text, str):

            try:
                result = json.loads(text)

            except json.JSONDecodeError:
                return []

    # ==========================================
    # 2. 提取 Tavily results
    # ==========================================

    if isinstance(result, dict):

        results = result.get("results", [])

    else:
        return []

    if not isinstance(results, list):
        return []

    # ==========================================
    # 3. 清洗
    # ==========================================

    cleaned = []

    for item in results:

        if not isinstance(item, dict):
            continue

        title = item.get("title", "")
        content = item.get("content", "")
        score = item.get("score", 0)

        # 没有正文直接跳过
        if not content:
            continue

        cleaned.append({
            "title": title,
            "content": content[:800],
            "score": score,
        })

    # ==========================================
    # 4. 按 Tavily score 排序
    # ==========================================

    cleaned.sort(
        key=lambda x: x.get("score", 0),
        reverse=True
    )

    return cleaned[:max_results]

# =========================
# Hotel Agent - original behavior kept
# =========================

def hotel_agent(state: TravelState):
    print("\nINSIDE HOTEL AGENT\n")

    query = (
        f"{state['user_query']} "
        "Japan hotels best areas hotel prices"
    )

    print("\nHOTEL SEARCH QUERY:")
    print(query)

    try:
        raw_result = asyncio.run(
            tavily_mcp_search(query)
        )

        print("\nHOTEL RAW RESULT:")
        print(raw_result)

        # 1. MCP 返回 list
        if not isinstance(raw_result, list):
            hotel_results = []
        else:
            hotel_results = []

            # 2. 找到 MCP 的 text 内容
            for item in raw_result:
                if not isinstance(item, dict):
                    continue

                text = item.get("text")

                if not text:
                    continue

                # 3. text 本身是 JSON 字符串
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    continue

                # 4. 获取 Tavily results
                results = data.get("results", [])

                if not isinstance(results, list):
                    continue

                # 5. 提取真正需要的数据
                for result in results:
                    if not isinstance(result, dict):
                        continue

                    title = result.get("title", "")
                    url = result.get("url", "")
                    content = result.get("content", "")

                    if not content:
                        continue

                    hotel_results.append({
                        "title": title,
                        "url": url,
                        "content": content,
                    })

        print("\nHOTEL SEARCH RESULT:")
        print(hotel_results)

    except Exception as exc:
        print(
            f"HOTEL AGENT MCP ERROR: "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

        hotel_results = []

    return {
        "hotel_results": hotel_results,
        "messages": [
            AIMessage(
                content="Hotel information processed."
            )
        ],
        # 酒店 Agent 没有调用 LLM
        "llm_calls": state.get("llm_calls", 0),
    }


# =========================
# Weather Agent - original behavior kept
# =========================
def weather_agent(state: TravelState):
    constraint = state["trip_constraints"]
    city = constraint["destination"]
    print(f"\n\nCity: {city}\n\n")

    try:
        weather_data = asyncio.run(
            weather_mcp_search(city)
        )

        forecast_data = asyncio.run(
            forecast_mcp_search(city)
        )

        weather_results = f"""
Current Weather:
{weather_data}

Forecast:
{forecast_data}
"""

        print("\nWEATHER AGENT RESULT:")
        print(weather_results[:200])

    except Exception as exc:
        print(
            f"WEATHER AGENT MCP ERROR: "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

        weather_results = (
            f"Live weather information for {city} "
            "is temporarily unavailable. Give general "
            "seasonal guidance and advise the traveler "
            "to verify the forecast before departure."
        )

    return {
        "weather_results": weather_results,
        "messages": [
            AIMessage(
                content="Weather information processed."
            )
        ],
    }


# =========================
# Budget Agent - new specialist
# =========================
def budget_agent(state: TravelState):
 
    t0 = time.perf_counter()

    prompt = f"""
Analyze whether this trip is realistic for the user's budget.

User Query:
{state['user_query']}

Trip Constraints:
{state.get('trip_constraints', {})}

Flight Results:
{state.get('flight_results', '')}

Hotel Results:
{state.get('hotel_results', '')}

Weather Results:
{state.get('weather_results', '')}

Return:
1. Estimated cost categories
2. Budget risk areas
3. Money-saving suggestions
4. Overall feasibility

If exact live prices are unavailable, clearly label estimates as approximate.
"""
    t1 = time.perf_counter()

    response = llm_qwen.invoke(
        [
            SystemMessage(content="You are a practical travel budget analyst."),
            HumanMessage(content=prompt),
        ]
    )

    t2 = time.perf_counter()

    print(
        f"[BUDGET] prompt_build={t1-t0:.2f}s "
        f"llm={t2-t1:.2f}s "
        f"total={t2-t0:.2f}s"
    )

    return {
        "budget_results": response.content,
        "messages": [AIMessage(content="Budget assessment generated.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# =========================
# Itinerary Agent - original behavior extended with selected results
# =========================
def itinerary_agent(state: TravelState):

    t0 = time.perf_counter()
    print("[ITINERARY] BEFORE LLM", flush=True)

    prompt = f"""
Create a complete travel itinerary.

User Query:
{state['user_query']}

Trip Constraints:
{state.get('trip_constraints', {})}

Flight Results:
{state.get('flight_results', '')}

Hotel Results:
{state.get('hotel_results', '')}

Weather Results:
{state.get('weather_results', '')}

Budget Results:
{state.get('budget_results', '')}

Make the itinerary practical, budget-aware, and easy to follow.
Create a clear draft that is ready for human review.
"""

    t1 = time.perf_counter()

    response = llm.invoke(
        [
            SystemMessage(content="You are an expert travel planner."),
            HumanMessage(content=prompt),
        ]
    )
    print("[ITINERARY] AFTER LLM", flush=True)

    t2 = time.perf_counter()

    print(
        f"[ITINERARY] prompt_build={t1-t0:.2f}s "
        f"llm={t2-t1:.2f}s "
        f"total={t2-t0:.2f}s"
    )

    approval_request = (
        "Please review the generated draft itinerary. Approve it to create the "
        "final polished plan, or provide feedback for revision."
    )

    print("\n\nITINERARY AGENT RESULT:\n\n")
    print(response.content[:200])

    return {
        "itinerary": response.content,
        "approval_request": approval_request,
        "messages": [AIMessage(content="Draft itinerary created for human review.")],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# =========================
# Human-in-the-Loop approval
# =========================
def human_approval_agent(state: TravelState):
    # Do not wrap interrupt() in try/except. LangGraph uses it to pause execution.
    review = interrupt(
        {
            "question": "Do you approve this itinerary?",
            "draft_itinerary": state.get("itinerary", ""),
            "approval_request": state.get("approval_request", ""),
            "selected_agents": state.get("selected_agents", []),
            "supervisor_reasoning": state.get("supervisor_reasoning", ""),
            "expected_response": {
                "approved": True,
                "feedback": "Optional revision feedback",
            },
        }
    )

    approved = bool(review.get("approved", False))
    human_feedback = str(review.get("feedback", "")).strip()

    return {
        "approved": approved,
        "human_feedback": human_feedback,
        "messages": [AIMessage(content="Human approval step completed.")],
    }


# =========================
# Final Response Agent - original format kept, HITL feedback added
# =========================
def final_agent(state: TravelState):
    if state.get("approved", False):
        review_instruction = (
            "The user approved the draft. Preserve its decisions while polishing it."
        )
    else:
        review_instruction = f"""
The user requested a revision. Apply this feedback carefully:
{state.get('human_feedback', '') or 'Improve the draft before finalizing it.'}
"""

    final_prompt = f"""
重要：请使用与用户请求相同的语言来回答。
如果用户用中文提问，就全部用中文回复；如果用英文提问，就用英文回复。    
Generate the final travel response for the user.

Human Review:
{review_instruction}

User Request:
{state['user_query']}

Supervisor Constraints:
{state.get('trip_constraints', {})}

Flights:
{state.get('flight_results', '')}

Hotels:
{state.get('hotel_results', '')}

Weather:
{state.get('weather_results', '')}

Budget Analysis:
{state.get('budget_results', '')}

Draft Itinerary:
{state.get('itinerary', '')}

Format the final answer beautifully using these sections:
1. Trip Summary
2. Flight Information
3. Hotel Suggestions
4. Weather Information
5. Day-by-Day Itinerary
6. Estimated Budget
7. Final Recommendations

Important:
- Be clear and practical.
- Mention that live flight APIs may not provide ticket prices when pricing is unavailable.
- Include weather-based travel advice.
- Keep the response useful for real travel planning.
- Incorporate the human feedback when revision was requested.
"""

    response = llm_qwen.invoke(
        [
            SystemMessage(
                content="You are a professional AI travel booking assistant."
            ),
            HumanMessage(content=final_prompt),
        ]
    )

    return {
        "final_response": response.content,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }


# =========================
# Dynamic Supervisor Routing
# =========================
ROUTE_MAP = {
    "guardrail_blocked": "guardrail_blocked",
    "flight_agent": "flight_agent",
    "hotel_agent": "hotel_agent",
    "weather_agent": "weather_agent",
    "budget_agent": "budget_agent",
    "itinerary_agent": "itinerary_agent",
}

def _selected_agents(state: TravelState) -> list[str]:
    selected = state.get("selected_agents", [])
    return [agent for agent in AGENT_ORDER if agent in selected]


def route_from_supervisor(state: TravelState) -> str:
    if not state.get("guardrail_allowed", True):
        return "guardrail_blocked"

    selected = _selected_agents(state)
    return selected[0] if selected else "itinerary_agent"


def route_after_agent(current_agent: str):
    def route(state: TravelState) -> str:
        selected = _selected_agents(state)
        current_index = AGENT_ORDER.index(current_agent)
        print(f"Current Agent: {current_agent}, Selected Agents: {selected}")

        for next_agent in AGENT_ORDER[current_index + 1 :]:
            if next_agent in selected:
                return next_agent

        return "itinerary_agent"

    return route


# ===========================================================================
# Postprocess
# def postprocess_agent(state: TravelState):

#     answer = state["messages"][-1].content

#     prompt = f"""
#               Translate the following answer into same language as .
              
#               Requirements:
#               1. Keep all formatting.
#               2. If the answer contains prices in USD ($), convert them to Chinese Yuan (CNY, ¥).
#               3. Use an approximate exchange rate of 1 USD ≈ 7.2 CNY unless another rate is provided.
#               4. Show only the converted CNY prices, not the original USD prices.
              
#               {answer}
#               """

#     translated = llm.invoke([
#             SystemMessage(content="You are a professional travel translator. Translate English travel content into fluent and accurate Chinese."),
#               HumanMessage(content=prompt)])

#     return {
#         "messages": [translated],
#         "llm_calls": 1 
#     }        

# =========================
# Build Graph
# =========================
graph = StateGraph(TravelState)

graph.add_node("supervisor", supervisor_agent)
graph.add_node("guardrail_blocked", guardrail_blocked_agent)
graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("weather_agent", weather_agent)
graph.add_node("budget_agent", budget_agent)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("human_approval", human_approval_agent)
graph.add_node("final_agent", final_agent)

graph.add_edge(START, "supervisor")
graph.add_conditional_edges("supervisor", route_from_supervisor, ROUTE_MAP)

graph.add_conditional_edges(
    "flight_agent", route_after_agent("flight_agent"), ROUTE_MAP
)
graph.add_conditional_edges(
    "hotel_agent", route_after_agent("hotel_agent"), ROUTE_MAP
)
graph.add_conditional_edges(
    "weather_agent", route_after_agent("weather_agent"), ROUTE_MAP
)
graph.add_conditional_edges(
    "budget_agent", route_after_agent("budget_agent"), ROUTE_MAP
)

graph.add_edge("itinerary_agent", "human_approval")
graph.add_edge("human_approval", "final_agent")
graph.add_edge("final_agent", END)
graph.add_edge("guardrail_blocked", END)


# ===========================================================================
# PostgreSQL Checkpointer
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver


DATABASE_URL = get_database_url()

_conn = psycopg.connect(
    DATABASE_URL,
    autocommit=True,
    row_factory=dict_row,
    prepare_threshold=0,
)

checkpointer = PostgresSaver(_conn)
checkpointer.setup()

print("连接数据库成功")

travel_graph = graph.compile(
    checkpointer=checkpointer
)

# ===========================================================================
# Function for FastAPI


# =========================
# FastAPI-facing helpers
# =========================
def _interrupt_payload(result: dict[str, Any]) -> dict[str, Any] | None:
    interrupts = result.get("__interrupt__", [])
    if not interrupts:
        return None

    first_interrupt = interrupts[0]
    payload = getattr(first_interrupt, "value", first_interrupt)
    return payload if isinstance(payload, dict) else {"value": payload}


def _serialize_result(
    result: dict[str, Any],
    thread_id: str,
) -> dict[str, Any]:
    messages = result.get("messages", [])
    last_message = messages[-1].content if messages else ""
    answer = result.get("final_response") or last_message
    interrupt_payload = _interrupt_payload(result)

    if interrupt_payload:
        answer = interrupt_payload.get("draft_itinerary") or result.get(
            "itinerary", ""
        )

    return {
        "thread_id": thread_id,
        "answer": answer,
        "requires_approval": interrupt_payload is not None,
        "approval_request": (
            interrupt_payload.get("approval_request", "")
            if interrupt_payload
            else result.get("approval_request", "")
        ),
        "flight_results": result.get("flight_results", ""),
        "hotel_results": result.get("hotel_results", ""),
        "weather_results": result.get("weather_results", ""),
        "budget_results": result.get("budget_results", ""),
        "itinerary": (
            interrupt_payload.get("draft_itinerary", "")
            if interrupt_payload
            else result.get("itinerary", "")
        ),
        "selected_agents": result.get("selected_agents", []),
        "trip_constraints": result.get("trip_constraints", {}),
        "supervisor_reasoning": result.get("supervisor_reasoning", ""),
        "guardrail_allowed": result.get("guardrail_allowed", True),
        "guardrail_reason": result.get("guardrail_reason", ""),
        "approved": result.get("approved"),
        "human_feedback": result.get("human_feedback", ""),
        "llm_calls": result.get("llm_calls", 0),
    }


def run_travel_agent(user_input: str, thread_id: str | None = None):
    """Start a new travel-planning run and pause at human approval."""
    if not thread_id:
        thread_id = f"user_{uuid.uuid4().hex}"

    config = {"configurable": {"thread_id": thread_id}}

    result = travel_graph.invoke(
        {
            "messages": [HumanMessage(content=user_input)],
            "user_query": user_input,
            "guardrail_allowed": True,
            "guardrail_reason": "",
            "selected_agents": [],
            "trip_constraints": _empty_constraints(),
            "supervisor_reasoning": "",
            "flight_results": "",
            "hotel_results": "",
            "weather_results": "",
            "budget_results": "",
            "itinerary": "",
            "approval_request": "",
            "approved": False,
            "human_feedback": "",
            "final_response": "",
            "llm_calls": 0,
        },
        config=config,
    )

    return _serialize_result(result, thread_id)


def resume_travel_agent(
    thread_id: str,
    approved: bool,
    feedback: str = "",
):
    """Resume the paused LangGraph thread after human review."""
    if not thread_id:
        raise ValueError("thread_id is required to resume a travel plan.")

    config = {"configurable": {"thread_id": thread_id}}
    result = travel_graph.invoke(
        Command(
            resume={
                "approved": approved,
                "feedback": feedback.strip(),
            }
        ),
        config=config,
    )

    return _serialize_result(result, thread_id)