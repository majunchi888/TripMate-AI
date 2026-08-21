# Multi-Agent-System-using-LangGraph-MCP-Supervisor-Guardrails-HITL

一个基于 **LangGraph + MCP** 构建的多智能体旅行规划系统 Demo，通过 **Supervisor、Input Guardrails 和 Human-in-the-Loop（HITL）** 实现安全、可控、可审核的旅行规划工作流。

项目包含 FastAPI Web 前端、示例 MCP Server 以及 MCP Client，完整演示了多智能体、Supervisor、Guardrails 和人工审核机制如何组合成一个可实际运行的 Agent 工作流。

## 核心理念

- **Multi-Agent Coordination**：使用 LangGraph 和 MCP 实现多智能体协作
- **Supervisor Agent**：由 Supervisor 负责管理和协调复杂的旅行规划流程
- **Input Guardrails**：对用户输入进行校验，过滤不符合要求的请求
- **Human-in-the-Loop（HITL）**：生成旅行方案后暂停工作流，由用户审核并决定是否批准或要求修改
- **MCP Tool Integration**：通过 MCP Server 提供天气、检查点等外部能力
- **可审核工作流**：将 Agent 的自动决策与人工确认结合，提高系统的可控性

## 项目结构

```text
.
├── app.py                         # FastAPI Web 前端及 API 接口
├── backend.py                     # 核心 Agent 编排与旅行规划逻辑
├── mcp_client.py                  # MCP Client，与 MCP Server 进行交互
├── custom_weather_mcp_server.py   # 示例天气 MCP Server
├── templates/                     # HTML 模板
├── static/                        # CSS、JavaScript 等静态资源
├── requirements.txt               # Python 依赖
├── .env                           # 环境变量（自行配置，不提交）
└── LICENSE                        # 项目许可证
```

## 功能特性

### 1. 多智能体协作

基于 LangGraph 构建 Agent 工作流，通过 Supervisor 对不同 Agent 或工具进行统一协调，实现复杂旅行规划任务的拆分与执行。

### 2. Supervisor Agent

Supervisor 作为工作流的核心控制节点，根据用户需求管理任务执行流程，并协调不同的 Agent 和 MCP 工具。

典型流程：

```text
用户请求
   ↓
Input Guardrails
   ↓
Supervisor
   ↓
┌──────────────┬──────────────┐
↓              ↓              ↓
Travel Agent   MCP Tools      Other Agents
└──────────────┴──────────────┘
   ↓
生成旅行方案
   ↓
Human Review
   ↓
批准 / 要求修改
   ↓
最终方案
```

### 3. Input Guardrails

在进入 Agent 工作流之前对用户请求进行检查。

主要用于：

- 验证用户输入是否符合旅行规划场景
- 拦截不符合要求的请求
- 降低无效请求进入 Agent 工作流造成的额外调用
- 提高系统整体的安全性和可控性

### 4. Human-in-the-Loop（HITL）

旅行方案生成后不会直接作为最终结果返回，而是进入人工审核阶段。

用户可以：

- **批准方案**：继续执行工作流
- **拒绝方案**：要求 Agent 根据反馈重新生成
- **提供修改意见**：将用户反馈重新交给 Agent

示例流程：

```text
生成 Draft
    ↓
等待人工审核
    ↓
┌───────────────┬────────────────┐
│               │                │
批准            拒绝             修改
│               │                │
↓               ↓                ↓
完成          重新规划        根据反馈修改
```

### 5. MCP 集成

项目提供一个示例 MCP Server：

```text
custom_weather_mcp_server.py
```

用于演示如何通过 MCP 向 Agent 提供外部工具能力，例如：

- 天气查询
- 行程检查点
- 其他可扩展的旅行相关工具

项目中的 MCP Client 负责连接和调用 MCP Server。

### 6. Web UI

项目提供基于 FastAPI 的简单 Web 前端，可以直接在浏览器中：

- 输入旅行规划需求
- 创建或恢复旅行规划线程
- 查看生成的旅行方案
- 对方案进行批准或要求修改

---

## 技术栈

| 技术                    | 用途                             |
| ----------------------- | -------------------------------- |
| Python                  | 后端开发                         |
| FastAPI                 | Web API 与前端服务               |
| LangGraph               | Agent 工作流编排                 |
| MCP                     | Agent 与外部工具之间的标准化通信 |
| Supervisor              | 多 Agent 协调与任务调度          |
| Guardrails              | 用户输入校验                     |
| HITL                    | 人工审核与工作流暂停/恢复        |
| HTML / CSS / JavaScript | Web 前端                         |

---

## 环境要求

- Python 3.10+
- Git
- pip
- virtualenv / venv 等虚拟环境工具

推荐使用 **Python 3.10 或 3.11**。

---

## 快速开始

### 1. 克隆项目

```powershell
git clone <your-repository-url>
cd <project-directory>
```

### 2. 创建虚拟环境

Windows PowerShell：

```powershell
python -m venv .venv
```

激活虚拟环境：

```powershell
.venv\Scripts\Activate.ps1
```

如果 PowerShell 因执行策略无法激活，可以使用：

```powershell
.\.venv\Scripts\activate
```

### 3. 安装依赖

```powershell
pip install -r requirements.txt
```

### 4. 配置环境变量

项目不会在代码仓库中提交 API Key 等敏感信息。

可以创建 `.env` 文件：

```env
# 根据实际使用的模型和 MCP 服务进行配置
OPENAI_API_KEY=your_api_key
```

具体环境变量根据项目中实际使用的 LangChain、LangGraph、MCP Server 或其他 Adapter 进行配置。

**注意：不要将真实 API Key 提交到 Git 仓库。**

---

## 启动 FastAPI

### 方式一：直接运行

```powershell
python app.py
```

### 方式二：使用 Uvicorn

```powershell
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

启动成功后访问：

```text
http://127.0.0.1:8000
```

即可打开 TripMate Web UI。

---

## 启动 MCP Server

项目提供了一个示例 MCP Server：

```text
custom_weather_mcp_server.py
```

如果需要测试自定义 MCP Adapter，可以在另一个终端中运行：

```powershell
python custom_weather_mcp_server.py
```

然后由 MCP Client 与该 Server 建立连接并调用对应工具。

该 Server 主要用于演示 MCP 的基本集成方式，实际项目中可以替换为更加丰富的旅行相关 MCP 服务。

---

## API 接口

### `POST /api/travel`

创建或恢复一个旅行规划线程。

请求：

```json
{
  "message": "帮我规划一个东京三日旅行",
  "thread_id": "optional-thread-id"
}
```

参数说明：

| 参数        | 类型   | 必填 | 说明                  |
| ----------- | ------ | ---- | --------------------- |
| `message`   | string | 是   | 用户的旅行规划需求    |
| `thread_id` | string | 否   | 已存在的工作流线程 ID |

---

### `POST /api/travel/approve`

对生成的旅行方案进行人工审核。

请求：

```json
{
  "thread_id": "thread-id",
  "approved": true,
  "feedback": "方案不错，可以继续"
}
```

参数说明：

| 参数        | 类型    | 必填 | 说明                 |
| ----------- | ------- | ---- | -------------------- |
| `thread_id` | string  | 是   | 当前旅行规划线程 ID  |
| `approved`  | boolean | 是   | 是否批准当前方案     |
| `feedback`  | string  | 否   | 用户的修改意见或反馈 |

例如拒绝当前方案并要求修改：

```json
{
  "thread_id": "thread-id",
  "approved": false,
  "feedback": "减少购物行程，多安排一些历史文化景点"
}
```

---

### `GET /health`

检查服务是否正常运行。

```text
GET /health
```

用于返回基本健康状态以及当前支持的功能列表。

---

## 工作流示意

整个旅行规划流程可以概括为：

```text
                    User
                     │
                     ▼
              Input Guardrails
                     │
              ┌──────┴──────┐
              │             │
           Reject          Pass
              │             │
              ▼             ▼
            Error        Supervisor
                            │
             ┌──────────────┼──────────────┐
             ▼              ▼              ▼
        Travel Agent    MCP Tools      Other Agents
             │              │              │
             └──────────────┼──────────────┘
                            ▼
                     Draft Travel Plan
                            │
                            ▼
                    Human-in-the-Loop
                            │
                   ┌────────┴────────┐
                   │                 │
                Approved          Rejected
                   │                 │
                   ▼                 ▼
              Final Plan        Revise Plan
                                     │
                                     └──────► Supervisor
```

---

## 项目中的核心设计

### LangGraph：工作流编排

LangGraph 用于构建有状态的 Agent 工作流，将不同 Agent、工具调用、条件判断以及人工审核节点组织成一个完整的执行图。

相比简单的：

```text
User → LLM → Answer
```

本项目采用：

```text
User
 ↓
Guardrails
 ↓
Supervisor
 ↓
Agents / MCP Tools
 ↓
Draft
 ↓
Human Approval
 ↓
Final Result / Revision
```

从而实现更加复杂和可控的 Agent 工作流。

### MCP：工具标准化

MCP 将 Agent 与外部工具进行解耦。

可以将：

```text
Agent
  ↓
MCP Client
  ↓
MCP Server
  ↓
Weather / Checkpoint / Other Tools
```

作为独立的工具调用链路。

因此后续可以比较方便地增加新的 MCP Server，而不需要大幅修改 Agent 的核心逻辑。

### HITL：人工控制关键决策

对于需要用户最终确认的操作，Agent 不直接完成整个流程，而是在关键节点暂停：

```text
Agent
 ↓
Draft
 ↓
Interrupt
 ↓
Human Review
 ↓
Resume
```

用户批准后继续执行，用户拒绝或提供反馈后重新进入规划流程。

---

## 异步与同步说明

项目的 FastAPI 服务采用异步 Web Server，而 `backend.py` 中保留了一些同步调用封装。

为了让同步封装能够调用异步 MCP Helper，`app.py` 中使用了：

```python
nest_asyncio
```

从而允许相关同步辅助函数在当前异步运行环境中调用异步 MCP 操作。

这种方式主要用于 Demo 和实验场景。

在生产环境中，可以进一步统一异步调用链路，减少同步与异步之间的转换。

---

## 项目运行效果

启动 FastAPI 后，可以通过浏览器访问：

```text
http://127.0.0.1:8000
```

输入旅行规划需求，例如：

```text
帮我规划一个东京三日旅行，预算 50000 日元，
希望包含历史文化景点、美食和一些轻松的购物行程。
```

系统将依次执行：

```text
Input Guardrails
      ↓
Supervisor
      ↓
Agent / MCP Tools
      ↓
生成旅行方案
      ↓
等待用户审核
```

用户可以批准当前方案，也可以提供反馈让 Agent 重新规划。

---

## 扩展方向

该项目目前主要用于演示 LangGraph + MCP + Supervisor + Guardrails + HITL 的组合方式。

后续可以进一步扩展：

- 增加天气 MCP Server
- 增加地图 / POI MCP Server
- 增加航班 / 酒店查询工具
- 增加多个专业旅行 Agent
- 增加长期记忆和用户偏好
- 增加数据库持久化
- 增加 LangSmith Tracing 与 Evaluation
- 增加更多 Guardrails
- 增加真正的生产级 MCP 服务
- 使用 Docker 进行容器化部署

---

## 测试

当前项目暂未提供完整的自动化测试。

可以通过以下方式进行功能验证：

1. 启动 FastAPI 服务
2. 打开 Web UI
3. 输入旅行规划需求
4. 检查 Guardrails 是否正常工作
5. 检查 Supervisor 是否正确调度 Agent
6. 检查 MCP Tool 是否能够正常调用
7. 检查生成的 Draft 是否进入 HITL 审核阶段
8. 分别测试批准和拒绝 / 修改流程

也可以直接调用 API 进行测试。

---

## 注意事项

### API Key

项目不会提供任何真实 API Key。

请通过环境变量或 `.env` 文件配置相关密钥。

不要将 `.env` 提交到 Git：

```gitignore
.env
.venv/
__pycache__/
```

### MCP Server

示例 MCP Server 主要用于学习和演示。

实际生产环境中，应根据具体业务需求部署和管理 MCP Server，并对工具调用增加必要的权限控制、异常处理和安全校验。

### HITL

HITL 机制适合用于需要用户确认的重要步骤。

例如：

```text
生成旅行计划 → 用户确认
```

也可以进一步扩展到：

```text
预订酒店 → 用户确认
购买机票 → 用户确认
提交订单 → 用户确认
```

从而避免 Agent 在未经用户确认的情况下执行具有实际影响的操作。

---

## 项目定位

本项目是一个用于学习和演示 **Agent Workflow Engineering** 的 Demo，重点展示以下技术如何组合：

```text
LangGraph
    +
Multi-Agent
    +
Supervisor
    +
MCP
    +
Guardrails
    +
Human-in-the-Loop
    ↓
可控、可审核的 Agent 工作流
```

它不仅展示单个 Agent 如何调用工具，也重点体现了复杂 Agent 系统中的**工作流编排、工具标准化、输入安全控制以及人工介入机制**。

---

## Contributing

欢迎提交 Issue 或 Pull Request。

如果发现 Bug、文档问题，或者希望增加新的 MCP Adapter，欢迎参与贡献。

---

## License

本项目遵循仓库中的 `LICENSE` 文件所规定的许可证。

---

## Acknowledgements

本项目用于演示：

- LangGraph Multi-Agent Workflow
- MCP Tool Integration
- Supervisor Agent
- Input Guardrails
- Human-in-the-Loop（HITL）

感谢相关开源项目和社区提供的技术支持。

---

## Contact

如有问题或建议，可以提交 GitHub Issue，或联系项目作者。
