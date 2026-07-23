# TripMate AI

TripMate AI 是一个基于 FastAPI + LangGraph 的智能旅行规划应用。它可以根据用户的旅行需求，自动收集航班信息、酒店建议和行程安排，并生成可直接阅读的旅行方案。
![alt text](image.png)

## 功能特点

- 支持中文和英文自然语言输入
- 通过 LangGraph 多 Agent 协作完成以下步骤：
  - 语言预处理
  - 航班信息检索
  - 酒店信息检索
  - 行程规划
  - 最终结果整合与翻译
- 前端使用 FastAPI + Jinja2 渲染，提供简洁的 Web 界面
- 支持线程式对话状态管理，便于持续追踪同一次旅行规划会话
- 使用 PostgreSQL Checkpointer 记录状态，适合后续扩展为多轮对话系统

## 项目架构

- 入口：app.py
- 业务逻辑与 Agent 流程：backend.py
- 航班查询工具：tools/flight_tool.py
- 网络搜索工具：tools/tavily_tool.py
- 模板页面：templates/index.html
- 静态资源：static/

## 技术栈

- Python 3.13+
- FastAPI
- Jinja2
- LangGraph
- LangChain
- Groq LLM
- Tavily Search
- AviationStack Flight API
- PostgreSQL

## 环境要求

请确保本地已安装：

- Python 3.13+
- PostgreSQL（用于 LangGraph checkpointer）
- 可用的 API 密钥：
  - GROQ_API_KEY
  - AVIATIONSTACK_API_KEY
  - TAVILY_API_KEY

## 环境变量配置

在项目根目录创建 .env 文件，并填入以下内容：

```env
GROQ_API_KEY=your_groq_api_key
AVIATIONSTACK_API_KEY=your_aviationstack_api_key
TAVILY_API_KEY=your_tavily_api_key
DATABASE_URL=postgresql://your_user:your_password@your_host:5432/your_db
DEFAULT_ORIGIN_IATA=JFK
```

说明：

- DATABASE_URL 用于 PostgreSQL Checkpointer。
- DEFAULT_ORIGIN_IATA 可选，默认值为 JFK。
- 航班接口返回更多是实时航班状态信息，不一定提供票价。

## 安装依赖

推荐使用 uv：

```bash
uv sync
```

如果你使用 pip，也可以执行：

```bash
pip install -r requirements.txt
```

## 运行项目

启动应用：

```bash
python app.py
```

启动后访问：

- 前端页面：http://127.0.0.1:8000/
- 健康检查接口：http://127.0.0.1:8000/health

## API 说明

### 发送旅行请求

接口：POST /api/travel

请求示例：

```bash
curl -X POST http://127.0.0.1:8000/api/travel \
  -H "Content-Type: application/json" \
  -d '{"message":"帮我规划一趟 5 天日本旅行，预算控制在 8000 元以内。","thread_id":"demo-thread"}'
```

返回内容包含：

- answer：最终回答
- flight_results：航班检索结果
- hotel_results：酒店检索结果
- itinerary：行程规划结果
- llm_calls：本次调用次数

## 项目结构

```text
TripMate-AI/
├── app.py                # FastAPI 应用入口
├── backend.py            # LangGraph 多 Agent 流程
├── requirements.txt      # 依赖列表
├── pyproject.toml        # 项目配置
├── static/               # 前端静态资源
├── templates/            # HTML 模板
└── tools/                # 搜索与航班工具
```

## 注意事项

- 如果没有配置有效的 API Key，部分功能会返回提示信息而不是实际结果。
- 当前航班工具依赖 AviationStack，适合获取实时航班状态，但不保证提供实时票价。
- 若你想扩展为更完整的在线预订系统，还可以接入价格查询、酒店预订和支付流程相关 API。

## 许可证

本项目当前未指定许可证，若需公开发布建议补充许可证文件。
