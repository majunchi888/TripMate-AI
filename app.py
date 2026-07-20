from email import message
from pathlib import Path
import traceback
import uvicorn

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from backend import run_travel_agent

BASE_DIR = Path(__file__).resolve().parent # app.py 的父目录

app = FastAPI(
        title = "TripMate AI",
        description = "Langgraph Multi-Agent Travel Planner with FastAPI Frontend",
        version = "1.0.0"
    )

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static") # 告诉 FastAPI：静态资源在这里

templates = Jinja2Templates(directory=str(BASE_DIR / "templates")) # 把 HTML 模板和 Python 数据结合起来，生成最终发送给浏览器的网页。

class TravelRequest(BaseModel):
    message: str
    thread_id: str | None = None

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
            name = "index.html",
            request = request,
            context={},
        )    


@app.post("/api/travel")
async def travel_planner(request_data: TravelRequest):
    try:
        user_message = request_data.message.strip()

        if not user_message:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Message cannot be empty."
                }
            )

        result = run_travel_agent(
            user_query=user_message,
            thread_id=request_data.thread_id
        )

        return JSONResponse(
            content={
                "success": True,
                "thread_id": result["thread_id"],
                "answer": result["answer"],
                "flight_results": result["flight_results"],
                "hotel_results": result["hotel_results"],
                "itinerary": result["itinerary"],
                "llm_calls": result["llm_calls"],
            }
        )

    except Exception as e:
        print("ERROR:", e)
        traceback.print_exc()

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": str(e)
            }
        )


@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "message": "AI Travel Planner API is running"
    }


@app.get("/favicon.ico")
async def favicon():
    return JSONResponse(content={})


if __name__ == "__main__": # 如果直接运行 app.py 时
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)