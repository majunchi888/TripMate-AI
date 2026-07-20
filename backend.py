import json
import os
import certifi
from dotenv import load_dotenv
from pycountry import DATABASE_DIR

load_dotenv()

os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

from typing import TypedDict, Annotated
import operator
import uuid

import psycopg
from psycopg.rows import dict_row

from langgraph.graph import StateGraph, START, END 
from langgraph.checkpoint.postgres import PostgresSaver

from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, AIMessage
from langchain_groq import ChatGroq

from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights

def get_database_url():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL is missing. Please add your Render PostgresSQL External Database URL in your .env file")
    # if sslmode is not set, add it
    if "sslmode=" not in database_url:
        separator = "&" if "?" in database_url else "?"
        database_url = f"{database_url}{separator}sslmode=require"

    return database_url

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing. Please add your Groq API key in your .env file")

# ===========================================================================
# LLM
llm = ChatGroq(model = "llama-3.3-70b-versatile", api_key = GROQ_API_KEY) # type: ignore

# ===========================================================================
# State
class TravelState(TypedDict):
    """TripMate Agent 的共享状态，在各个 LangGraph 节点之间传递数据。"""
    # 对话历史，使用 operator.add 自动追加消息，而不是覆盖
    messages: Annotated[list[AnyMessage], operator.add]
    user_query: str           # 原始输入
    english_query: str        # 翻译后的英文
    user_language: str        # zh/en/ja...
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int

# ===========================================================================
# preprocess
def preprocess_agent(state: TravelState):

    query = state["user_query"]

    # 简单判断语言
    if any('\u4e00' <= char <= '\u9fff' for char in query):
        user_language = "zh"
    else:
        user_language = "en"


    # 如果本身英文，不需要翻译
    if user_language == "en":
        english_query = query

    else:
        prompt = f"""
                  Translate the following travel request into English.
                  
                  Only output the translated sentence.
                  Do not explain.
                  
                  User request:
                  {query}
                  """
                  
        response = llm.invoke([
            SystemMessage(
                content="You are a professional travel query translator."
            ),
            HumanMessage(
                content=prompt
            )
        ])

        english_query = response.content.strip() # type: ignore


    return {
        "english_query": english_query,
        "user_language": user_language,
        "llm_calls": state.get("llm_calls", 0) + 1
    }
# ===========================================================================
# Flight Agent

def flight_agent(state: TravelState):
    query = state["english_query"]
    flight_results = search_flights(query)

    return{
            "flight_results": flight_results,
            "messages": [
                    AIMessage(content="Flighr results fetched.")
                ],
            # "llm_calls": state.get("llm_calls", 0) + 1 
        }

# ===========================================================================
# Hotel Agent

def hotel_agent(state: TravelState):
    query = f"Best hotels for {state['english_query']}."
    hotel_results = tavily_search(query)

    return{
            "hotel_results": hotel_results,
            "messages": [
                    AIMessage(content="Hotel information searched.")
                ],
            # "llm_calls": state.get("llm_calls", 0) + 1 
        }

# ===========================================================================
# Itinerary Agent 负责生成行程

def itinerary_agent(state: TravelState):
    prompt = f"""
                   Create a complete travel itinerary,

                   User Query: 
                   {state["english_query"]}

                   Flight Results: 
                   {state["flight_results"]}

                   Hotel Results: 
                   {state["hotel_results"]}
                   
                   Make the itinerary practical, budget-aware, and easy to follow.
             """        
    response = llm.invoke([
            SystemMessage(content="You are an expert travel planner."),
            HumanMessage(content=prompt)
        ])

    return{
            "itinerary": response.content,
            "messages": [response],
            "llm_calls": state.get("llm_calls", 0) + 1 
        }

# ===========================================================================
# Final Response Agent 整合与格式化

def final_agent(state: TravelState):
    final_prompt = f"""english_query
                        Generate the final travel response for the user.

                        User Request:
                        {state['english_query']}
                        
                        Flights:
                        {state['flight_results']}
                        
                        Hotels:
                        {state['hotel_results']}
                        
                        Itinerary:
                        {state['itinerary']}
                        
                        Format the final answer beautifully using these sections:
                        
                        1. Trip Summary
                        2. Flight Information
                        3. Hotel Suggestions
                        4. Day-by-Day Itinerary
                        5. Estimated Budget
                        6. Final Recommendations
                        
                        Important:
                        - Be clear and practical.
                        - Always be budget-aware.
                        - Mention that live flight API may not provide ticket prices if pricing is unavailable.
                        - Keep the response useful for real travel planning.
                   """
    response = llm.invoke([
            SystemMessage(content="You are a professional AI travel booking assistant."),
            HumanMessage(content=final_prompt)
        ])

    return{
            "messages": [response],
            "llm_calls": state.get("llm_calls", 0) + 1 
        }

# ===========================================================================
# Postprocess
def postprocess_agent(state: TravelState):

    answer = state["messages"][-1].content

    if state.get("user_language") in ["en", "English"]:
        return {}

    prompt = f"""
              Translate the following answer into {state["user_language"]}.
              
              Requirements:
              1. Keep all formatting.
              2. If the answer contains prices in USD ($), convert them to Chinese Yuan (CNY, ¥).
              3. Use an approximate exchange rate of 1 USD ≈ 7.2 CNY unless another rate is provided.
              4. Show only the converted CNY prices, not the original USD prices.
              
              {answer}
              """

    translated = llm.invoke([HumanMessage(content=prompt)])

    return {
        "messages": [translated],
        "llm_calls": state.get("llm_calls", 0) + 1 
    }        

# ===========================================================================
# Build Graph

graph = StateGraph(TravelState)

graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("itinerary_agent", itinerary_agent)
graph.add_node("final_agent", final_agent)

graph.add_node("preprocess_agent", preprocess_agent)
graph.add_node("postprocess_agent", postprocess_agent)

graph.add_edge(START, "preprocess_agent")
graph.add_edge("preprocess_agent", "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "itinerary_agent")
graph.add_edge("itinerary_agent", "final_agent")
graph.add_edge("final_agent", "postprocess_agent")
graph.add_edge("postprocess_agent", END)

# ===========================================================================
# PostgreSQL Checkpointer
DATABASE_URL = get_database_url()

_conn = psycopg.connect(
    DATABASE_URL, 
    autocommit=True,
    row_factory=dict_row, # type: ignore
    )

checkpointer = PostgresSaver(_conn) # type: ignore
checkpointer.setup()

travel_graph = graph.compile(checkpointer)

# ===========================================================================
# Function for FastAPI

def run_travel_agent(user_query: str, thread_id: str | None = None):
    if not thread_id:
        thread_id = f"user_{uuid.uuid4().hex}"

    config = {
        "configurable": {
            "thread_id": thread_id
            }
    }    

    result = travel_graph.invoke({
            "messages": [HumanMessage(content = user_query)],
            "user_query": user_query,
            "english_query": "",
            "user_language": "",
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0,
        },
        config=config # type: ignore
    )

    final_answer = result["messages"][-1].content

    return {
            "thread_id": thread_id,
            "answer": final_answer,
            "flight_results": result.get("flight_results", ""),
            "hotel_results": result.get("hotel_results", ""),
            "itinerary": result.get("itinerary", ""),
            "llm_calls": result.get("llm_calls", 0)
        }