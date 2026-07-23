# ✈️ TripMate AI — 多代理旅行规划器与 MCP

一个开源的 AI 旅行规划器，它将自然语言旅行需求转换为实用的旅行计划，包括航班建议、酒店推荐、天气信息和逐日行程。该项目使用 LangGraph、LangChain、FastAPI 和 MCP 工具构建多代理工作流。

## 为什么要做这个项目？

规划旅行通常需要在多个网站、工具和表格之间切换。该项目将这些环节整合到一个体验中，通过以下内容实现：

- 航班搜索代理
- 酒店调研代理
- 天气查询代理
- 行程规划代理
- 最终响应代理

所有代理通过 LangGraph 工作流和 MCP 工具集成进行协调。

## 功能

- ✈️ 使用 AviationStack 进行航班调研
- 🏨 使用 Tavily 搜索进行酒店建议
- 🌤 通过自定义 MCP 工具查询天气
- 🧠 使用 LangGraph 和 MCP 实现多代理编排
- 📝 生成结构化旅行行程
- 🌐 基于 FastAPI 的后端和简洁 Web 界面
- 💾 使用 PostgreSQL 持久化会话状态
- ⚡ 使用 Groq 生成 LLM 驱动的响应

## 技术栈

![alt text](image-4.png)

- Python 3.10+
- FastAPI
- Jinja2 + HTML/CSS/JavaScript 前端
- LangGraph
- LangChain
- Groq LLMs
- PostgreSQL
- Tavily API
- AviationStack API
- MCP via `langchain-mcp-adapters` 和 `mcp`

## MCP 集成说明

项目在多个环节中集成了 MCP：

- `Tavily` 搜索使用远程 MCP 端点：`https://mcp.tavily.com/mcp/`
- `AviationStack` 使用本地 stdio MCP 命令：`uvx aviationstack-mcp`
- `Weather` 由本地自定义 MCP 服务器实现，文件位置为 `custom_weather_mcp_server.py`

MCP 客户端定义在 `mcp_client.py`，并提供以下异步辅助函数：

- `tavily_mcp_search`
- `aviation_mcp_call`
- `weather_mcp_search`
- `forecast_mcp_search`
- `extract_destination`

主旅行工作流位于 `backend.py`，其中航班、酒店和天气代理都会调用这些辅助函数。

## 项目结构

```text
.
├── app.py                      # FastAPI 应用入口
├── backend.py                  # LangGraph 旅行工作流
├── mcp_client.py               # MCP 客户端与工具集成
├── custom_weather_mcp_server.py# 本地天气 MCP 服务器
├── requirements.txt            # Python 依赖
├── static/                     # 静态前端资源
├── templates/                  # HTML 模板
└── tools/                      # 航班和网络搜索集成工具
```

## 环境准备

在本地运行项目前，请确认以下条件：

- 已安装 Python 3.10 或更高版本
- PostgreSQL 已启动并可访问
- 已获取以下 API Key：
  - Groq
  - Tavily
  - AviationStack
  - OpenWeather
- 如果使用本地 AviationStack MCP，需安装 `uvx` 或根据需要调整 `mcp_client.py`

## 环境变量

在项目根目录创建 `.env` 文件，并添加如下内容：

```env
DATABASE_URL=postgresql://user:password@localhost:5432/travel_db
GROQ_API_KEY=your_groq_api_key
AVIATIONSTACK_API_KEY=your_aviationstack_api_key
TAVILY_API_KEY=your_tavily_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
DEFAULT_ORIGIN_IATA=DAC
```

> 如果你在 Windows 上运行，建议使用 `.\.venv\Scripts\activate` 激活虚拟环境。

## 安装步骤

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.\.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## 启动应用

运行以下命令启动 FastAPI 服务：

```bash
python app.py
```

在浏览器中打开：

```text
http://127.0.0.1:8000/
```

## 使用 MCP 工具

应用在后台使用 MCP，因此前端无需额外修改。

如果需要自定义天气 MCP 服务器命令，请编辑 `mcp_client.py`，并将天气工具路径替换为你的本地 Python 环境或其他可执行路径。

## API 接口

- GET `/health` - 健康检查
- POST `/api/travel` - 提交旅行请求

示例请求：

```bash
curl -X POST http://127.0.0.1:8000/api/travel \
  -H "Content-Type: application/json" \
  -d '{"message":"Plan a 3-day trip to Tokyo with a budget of $1200"}'
```

## 工作流说明

1. 用户提交旅行请求
2. 航班代理使用 MCP 支持的 AviationStack 数据
3. 酒店代理使用远程 Tavily MCP 搜索
4. 天气代理调用本地自定义天气 MCP 服务器
5. 行程代理生成实用旅行计划
6. 最终结果通过 Web API 返回给用户
