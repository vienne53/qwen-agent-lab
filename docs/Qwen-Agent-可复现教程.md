# 说明（本仓库）

本文件来自可复现实验笔记，已脱敏。**请推送本仓库 `qwen-agent-lab`，不要把官方 `Qwen-Agent` 整仓（含 `.venv`）当成自有项目推到 GitHub。**  
运行本仓库 UI 时，用 `pip install -r requirements.txt` 安装依赖即可；官方源码可另克隆作阅读参考。

---
# Qwen-Agent 可复现安装记录（Windows PowerShell）

- 仓库：https://github.com/QwenLM/Qwen-Agent  
- 本机路径：`D:\Qwen-Agent`  
- Python：3.12 + 虚拟环境 `.venv`  
- 用途：Qwen-Agent（RAG + MCP）可复现实验，接 DashScope 千问 API  
- API Key：已写入 **Windows 用户环境变量** `DASHSCOPE_API_KEY`（不要写进仓库、不要贴聊天）  
- 启动脚本：`D:\Qwen-Agent\start_rag_gui.bat`  
- 主入口：`D:\Qwen-Agent\examples\assistant_rag.py`  
- 官方说明：`D:\Qwen-Agent\README_CN.md`

本文同时固化这些问题：

1. **绑死 / 不绑死** PDF：Terminal 启动参数，还是脚本里定义？  
2. **Agent 角色、loop、content**：框架是否已设计好？当前结构是什么？  
3. **RAG** 架构、能力、机制与模型、如何调参？  
4. **可复现路径**：Terminal 做什么、改哪个文件，都写清。  
5. **多 Agent** 怎么实现、什么结构？**MCP** 有啥用、什么结构？

---

## 0. 一句话总览

| 问题 | 答案 |
|------|------|
| 绑死知识库？ | **在 Python 脚本里**给 `Assistant(..., files=[...])`；**不是** Terminal 启动参数。UI 上传 = 当前会话文件，不算绑死。 |
| Agent 角色 / loop？ | **框架已实现**（`Agent` → `FnCallAgent` → `Assistant`）。你主要改：`llm`、`system_message`、`name`、`description`、`files`、`rag_cfg`、`function_list`。 |
| 默认 RAG？ | 解析切片 → 本地 JSON 缓存 → **BM25 关键词 + 首页片段** 注入 System；**默认不做持久向量库**。 |
| 怎么启动？ | Terminal / 双击 bat → 跑 `examples\assistant_rag.py`；改行为 → **编辑该 py 后重启**。 |

---

## 1. 环境准备（一次性）

**在哪里做：** Windows PowerShell。

```powershell
cd D:\
git clone https://github.com/QwenLM/Qwen-Agent.git
cd D:\Qwen-Agent

python -m venv .venv
.\.venv\Scripts\Activate.ps1

pip install -U "qwen-agent[rag,mcp,gui]"
pip install tqdm soundfile

python -c 'import qwen_agent; print("ok")'
```

期望输出：`ok`。

若无法激活虚拟环境：

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
.\.venv\Scripts\Activate.ps1
```

### 配置 API Key（一次性，用户环境变量）

PowerShell（把下面换成你的密钥；**不要提交到 git、不要写进 py**）：

```powershell
[Environment]::SetEnvironmentVariable("DASHSCOPE_API_KEY", "你的密钥", "User")
```

或：系统设置 → 搜索「环境变量」→ 用户变量 → 新建 `DASHSCOPE_API_KEY`。

验证（**新开一个终端**）：

```powershell
if ($env:DASHSCOPE_API_KEY) { "已加载，长度=$($env:DASHSCOPE_API_KEY.Length)" } else { "未加载：请新开终端" }
```

### 入口文件改动（我们已改过）

**改哪个文件：** `D:\Qwen-Agent\examples\assistant_rag.py`（用编辑器打开，不是 Terminal 传参）。

当前要点：

- `if __name__ == '__main__':` 调用 `app_gui()`，`test()` 注释掉。  
- `WebUI(...).run(share=True)`：本地 `http://127.0.0.1:7860` + Gradio 公网临时链（需外网）。  
- `llm={'model': 'qwen-plus-latest'}`：DashScope 云端千问。

CLI 单次问答（不启网页）可改回：

```python
if __name__ == '__main__':
    test()
    # app_gui()
```

---

## 2. 每次启动（不必再写 Key）

**网页 RAG（推荐）：** 双击或运行：

```text
D:\Qwen-Agent\start_rag_gui.bat
```

bat 等价于：进入 `D:\Qwen-Agent` → 激活 `.venv` → `python examples\assistant_rag.py`。

或 PowerShell：

```powershell
cd D:\Qwen-Agent
.\.venv\Scripts\Activate.ps1
python examples\assistant_rag.py
```

浏览器打开终端提示的地址（多为 `http://127.0.0.1:7860`）。**只有在网页里发问才会耗 token。**

MCP 示例：

```powershell
python examples\assistant_mcp_sqlite_bot.py
```

### 上传 PDF 后产物在哪

| 产物 | 路径 |
|------|------|
| 切片 / 整篇缓存 JSON | `D:\Qwen-Agent\workspace\tools\doc_parser\` |
| 原始解析缓存 | `D:\Qwen-Agent\workspace\tools\simple_doc_parser\` |

查看切片：

```powershell
cd D:\Qwen-Agent
.\.venv\Scripts\Activate.ps1
python -c "import json,glob; p=glob.glob(r'workspace/tools/doc_parser/*')[0]; d=json.load(open(p,encoding='utf-8')); print('file',p); print('title',d['title']); print('n_chunks',len(d['raw'])); print('chunk0_token',d['raw'][0]['token'])"
```

---

## 3. 绑死 / 不绑死怎么实现？

### 3.1 结论

| 模式 | 是否「绑死」 | 在哪里配置 | Terminal 能否设？ |
|------|--------------|------------|-------------------|
| UI 上传 PDF | 否（会话级） | 网页上传 → 当前聊天 history 的 `file` | 否 |
| `Assistant(files=[...])` | 是（进程级，启动即带） | **编辑** `examples\assistant_rag.py` | 否（官方入口无 `--kb`） |
| 消息里带 `file` | 否（该次对话） | `test()` 的 `messages` 或 UI | 不是 bat 开关 |

**不是** `python assistant_rag.py --pdf xxx`；要改行为 → **改 `Assistant(...)` 参数，保存后重启进程**。

### 3.2 框架如何拼文件

源码：`D:\Qwen-Agent\qwen_agent\memory\memory.py` → `get_rag_files()`：

```text
rag_files = system_files（构造时 files=） + session_files（messages 里上传）
```

再经 `DocParser` → `Retrieval`。

### 3.3 完整命令：不绑死启动 vs 绑死启动

把下面的 `D:\docs\产品手册.pdf` 换成你的真实 PDF 路径。

**A. 不绑死（当前默认，只靠 UI 上传）**

```powershell
cd D:\Qwen-Agent
.\.venv\Scripts\Activate.ps1
python examples\assistant_rag.py
```

或直接：

```text
D:\Qwen-Agent\start_rag_gui.bat
```

**B. 绑死一份 PDF 再启动（推荐：命令行一次写好并启动）**

```powershell
cd D:\Qwen-Agent
.\.venv\Scripts\Activate.ps1

@'
from qwen_agent.agents import Assistant
from qwen_agent.gui import WebUI

bot = Assistant(
    llm={"model": "qwen-plus-latest"},
    name="手册助手",
    description="只基于产品手册回答。",
    system_message="你是售后助手，只根据知识库回答，不知道就说不知道。",
    files=[r"D:\docs\产品手册.pdf"],
    rag_cfg={
        "max_ref_token": 20000,
        "parser_page_size": 500,
        "rag_keygen_strategy": "GenKeyword",
        "rag_searchers": ["keyword_search", "front_page_search"],
    },
)
WebUI(bot).run(share=True)
'@ | Set-Content -Encoding utf8 examples\_run_bound_rag.py

python examples\_run_bound_rag.py
```

浏览器打开终端里的地址（多为 `http://127.0.0.1:7860`）。验收：不上传也能问该 PDF。

**C. 绑死实现长什么样（核心就这一行）**

```python
Assistant(files=[r"D:\docs\产品手册.pdf"], ...)
```

等价地，也可以手改 `D:\Qwen-Agent\examples\assistant_rag.py` 的 `app_gui()`，在 `Assistant(...)` 里加上同样的 `files=[...]`，保存后：

```powershell
cd D:\Qwen-Agent
.\.venv\Scripts\Activate.ps1
python examples\assistant_rag.py
```

**D. CLI 绑死问一句（不开网页，省事试通）**

```powershell
cd D:\Qwen-Agent
.\.venv\Scripts\Activate.ps1

python -c "from qwen_agent.agents import Assistant; bot=Assistant(llm={'model':'qwen-plus-latest'}, files=[r'D:\docs\产品手册.pdf']); msgs=[{'role':'user','content':'这份文档讲了什么？'}];
[print(r) for r in bot.run(msgs)]"
```

### 3.4 「不绑死」（当前默认）

不传 `files=`。只靠 UI / 消息里的 `file`。清空会话后该次上传不再参与检索；`workspace\tools\doc_parser\` 缓存可能仍在（加速解析 ≠ 仍绑定 Agent）。

### 3.5 解绑 / 删缓存

- 会话：清空对话，或去掉 `files=` 后重启。  
- 缓存：删 `D:\Qwen-Agent\workspace\tools\doc_parser\` 下对应文件。

---

## 4. Agent 角色、Loop、Content —— 框架结构

### 4.1 结论

**Loop、工具调用、检索注入 prompt，框架已写好。** 不用自己写 while-loop；在示例脚本里配置即可。

### 4.2 类继承与职责（本机路径）

```text
qwen_agent/agent.py          Agent（抽象基类）
  ├─ run() / run_nonstream()   统一入口
  ├─ system_message / name / description / llm / function_map
  └─ _call_llm / _call_tool

qwen_agent/agents/fncall_agent.py   FnCallAgent
  ├─ 内置 Memory(files=..., rag_cfg=...)
  └─ _run：while（最多 MAX_LLM_CALL_PER_RUN）
        → 调 LLM → 若 function call → 执行工具 → 追加 messages → 直到不再调工具

qwen_agent/agents/assistant.py     Assistant（我们用的）
  └─ 先 mem.run 做 RAG → 知识写入 SYSTEM → 再 super()._run

qwen_agent/memory/memory.py        Memory（文件列表 + retrieval + 关键词策略）
qwen_agent/gui/web_ui.py           WebUI（上传 → history 的 file → agent.run）
```

### 4.3 脚本里可设的角色参数

| 参数 | 作用 | 在哪改 |
|------|------|--------|
| `system_message` | 人设 / 规则 | `Assistant(system_message='...')` |
| `name` | UI / 多 Agent 显示名 | 同上 |
| `description` | UI 简介 | 同上 |
| `llm` | 模型 | `llm={'model': 'qwen-plus-latest'}` |
| `function_list` | 工具 / MCP | 示例或 MCP 脚本 |
| `files` | 绑死知识 | 第 3 节 |
| `rag_cfg` | RAG 超参 | 第 5 节 |

**只改人设：** 编辑 `examples\assistant_rag.py`：

```python
bot = Assistant(
    llm={'model': 'qwen-plus-latest'},
    name='标书助手',
    description='根据上传材料做技术应答。',
    system_message='你是投标技术写手。只依据用户上传文档作答，条理分点，不编造条款。',
)
```

保存 → 重启 bat。

### 4.4 一次提问的 Loop（可对外说明）

1. **RAG（Memory）**：收集文件 →（默认）关键词生成 → 切片/读缓存 → 检索  
2. **注入（Assistant）**：片段写成「# 知识库」写入 **SYSTEM** `content`  
3. **工具循环（FnCallAgent）**：调主模型；有 function call 则执行并写回，直到结束或达调用上限  
4. **GUI**：流式渲染气泡  

`content` 可为字符串或多模态列表：`[{'text': '...'}, {'file': '...'}]`。

### 4.5 改代码认路

| 想改什么 | 打开哪个文件 |
|----------|--------------|
| Demo 入口、模型、人设、files、GUI | `D:\Qwen-Agent\examples\assistant_rag.py` |
| RAG 默认常量 | `qwen_agent\settings.py` 或示例 `rag_cfg` |
| 切片 | `qwen_agent\tools\doc_parser.py` |
| 检索 | `qwen_agent\tools\retrieval.py` |
| BM25 | `qwen_agent\tools\search_tools\keyword_search.py` |
| 可选向量 | `...\search_tools\vector_search.py` |
| Agent 循环 | `qwen_agent\agents\fncall_agent.py` |
| RAG 拼进 System | `qwen_agent\agents\assistant.py` |
| 上传进消息 | `qwen_agent\gui\web_ui.py`（`add_text`） |
| 缓存 CRUD | `qwen_agent\tools\storage.py` |

日常 Demo **只改 `examples\*.py`**。

---

## 5. RAG 架构、能力、机制、模型、调参

### 5.1 架构（默认）

```text
文件（files= 和/或 UI/消息）
  → SimpleDocParser → DocParser（按 parser_page_size 切；≤max_ref_token 可整篇一块）
  → Storage 缓存 workspace/tools/doc_parser/
  →（可选）Keygen 生成关键词
  → HybridSearch：默认 keyword_search(BM25) + front_page_search
  → 截断到 max_ref_token，注入 SYSTEM
  → 主模型回答（可再 function call）
```

属 **Naive RAG + 轻量 Agent 编排**，不是知识库中台。

### 5.2 能做什么

| 能力 | 情况 |
|------|------|
| PDF/Word/PPT/TXT/HTML 问答 | 支持 |
| 多文件检索 | 支持 |
| UI 临时上传 | 支持 |
| 启动绑死 `files=` | 支持 |
| 切片落盘复用 | 支持 |
| 默认持久向量库 / Milvus | **不支持** |
| 可选 `vector_search` | 临时 FAISS + DashScope embedding |
| 知识库管理台 CRUD | **无**（只有缓存文件 + 改 `files=`） |
| MCP | 另见 `examples\assistant_mcp_sqlite_bot.py` |

### 5.3 机制与模型

| 环节 | 机制 | 模型 / 库 |
|------|------|-----------|
| 主问答 | Chat | DashScope：`qwen-plus-latest`（可改） |
| 关键词 | `rag_keygen_strategy`（默认 `GenKeyword`） | Memory 侧 LLM（部分场景降级 `qwen-turbo`） |
| 切片 | 按 token | 本地 Qwen tokenizer |
| 默认检索 | BM25 + 文档前部 | `rank_bm25`、`jieba` |
| 可选向量 | 嵌入相似度 | `text-embedding-v1` + FAISS |
| 缓存 | 一 key 一文件 | `Storage` |

### 5.4 调参

**推荐：改示例 `rag_cfg`（重启生效）** — 编辑 `examples\assistant_rag.py`：

```python
bot = Assistant(
    llm={'model': 'qwen-plus-latest'},
    rag_cfg={
        'max_ref_token': 20000,       # 注入参考总 token 上限
        'parser_page_size': 500,      # 单块最大 token
        'rag_keygen_strategy': 'GenKeyword',
        'rag_searchers': ['keyword_search', 'front_page_search'],
        # 试向量需：pip install langchain langchain_community faiss-cpu
        # 'rag_searchers': ['keyword_search', 'vector_search'],
    },
)
```

**环境变量（管「未传 rag_cfg 时的默认」）** — 启动前同一 Terminal：

```powershell
$env:QWEN_AGENT_DEFAULT_MAX_REF_TOKEN = "12000"
$env:QWEN_AGENT_DEFAULT_PARSER_PAGE_SIZE = "800"
$env:QWEN_AGENT_DEFAULT_RAG_KEYGEN_STRATEGY = "GenKeyword"
$env:QWEN_AGENT_DEFAULT_RAG_SEARCHERS = "['keyword_search', 'front_page_search']"
$env:QWEN_AGENT_MAX_LLM_CALL_PER_RUN = "10"
python examples\assistant_rag.py
```

定义见：`D:\Qwen-Agent\qwen_agent\settings.py`。脚本显式传了 `rag_cfg` 则以脚本为准。

| 现象 | 可试 |
|------|------|
| 答非所问 | 换 keygen；或加 `vector_search` |
| 太贵 / 太长 | 降 `max_ref_token` |
| 切太碎 | 增 `parser_page_size` |
| 短文整篇一块 | 正常（`*_without_chunking`） |
| 工具死循环 | 降 `QWEN_AGENT_MAX_LLM_CALL_PER_RUN` |

换主模型：仍改 `assistant_rag.py` 的 `llm={'model': 'qwen-turbo', ...}`（本地 vLLM 等见官方 README_CN）。

---

## 6. 操作对照表（Terminal vs 改文件）

| 目标 | 做法 |
|------|------|
| 安装依赖 | Terminal：`pip install ...`（`D:\Qwen-Agent` + venv） |
| 配 API Key | 用户环境变量（**不要**写进 py） |
| 启动网页 | `start_rag_gui.bat` 或 `python examples\assistant_rag.py` |
| 换模型 / 人设 / 绑死 PDF / rag_cfg | **编辑** `examples\assistant_rag.py` → 重启 |
| 改框架默认常量 | `settings.py` 或环境变量（优先示例 `rag_cfg`） |
| 看切片 | 读 `workspace\tools\doc_parser\` |
| 清缓存 | 删该目录文件 |
| CLI 试一条 | 同文件 `main` 调 `test()` |
| MCP | `python examples\assistant_mcp_sqlite_bot.py` |

---

## 7. 验收清单

- [ ] `import qwen_agent` → `ok`  
- [ ] 新终端能读到 `DASHSCOPE_API_KEY`  
- [ ] `start_rag_gui.bat` 能开网页  
- [ ] UI 上传 PDF 能问答；`workspace\tools\doc_parser\` 有缓存  
- [ ] （可选）`files=[本地pdf]` 不上传也能答  
- [ ] （可选）改 `system_message` 后人设生效  

---

## 8. 快速复述（30 秒）

「官方 Qwen-Agent 的 `Assistant` 内置 Memory。知识要么构造时 `files=` 绑死，要么 UI/消息上传。解析后按 token 切片缓存在 workspace，默认 BM25，片段写进 System，再进 function-call 循环。角色用 `system_message`/`name` 配，loop 框架已有。要持久向量库或知识库 CRUD，得自己接，不是开箱功能。」

---

## 9. 多 Agent 怎么实现？结构是什么？

### 9.1 两种官方模式

| 模式 | 类 | 示例文件 | 干什么 |
|------|-----|----------|--------|
| **路由分发** | `Router` | `D:\Qwen-Agent\examples\multi_agent_router.py` | 一个总控按 `name`/`description` 选子 Agent |
| **群聊协作** | `GroupChat` | `D:\Qwen-Agent\examples\group_chat_demo.py` | 多个角色轮流发言（可含真人 `is_human`） |

相关源码：

- `D:\Qwen-Agent\qwen_agent\agents\router.py`
- `D:\Qwen-Agent\qwen_agent\agents\group_chat.py`
- `D:\Qwen-Agent\qwen_agent\agents\fncall_agent.py`（单 Agent 工具循环）

### 9.2 结构（路由型，最常用面试口径）

```text
用户
  ↓
Router（总控 Assistant + 路由 prompt）
  ├─ 能自己答 → 直接回复
  └─ 不能 → 输出 Call: 某帮手名字
        ↓
    子 Agent A（如多模态 Assistant）
    子 Agent B（如 ReActChat + 工具）
    …
```

每个子 Agent 仍是独立的 `Assistant` / `ReActChat`：自己的 `llm`、`system_message`/`instructions`、`function_list`、可选 `files`。

### 9.3 启动命令（多 Agent 路由 GUI）

```powershell
cd D:\Qwen-Agent
.\.venv\Scripts\Activate.ps1
python examples\multi_agent_router.py
```

核心写法（见该文件 `init_agent_service()`）：

```python
bot_vl = Assistant(llm=llm_cfg_vl, name='多模态助手', description='可以理解图像内容。')
bot_tool = ReActChat(llm=llm_cfg, name='工具助手', description='...', function_list=['image_gen', 'code_interpreter'])
bot = Router(llm=llm_cfg, agents=[bot_vl, bot_tool])
```

群聊：

```powershell
python examples\group_chat_demo.py
```

用配置里的 `background` + 多个 `agents[{name, description, instructions, selected_tools, knowledge_files, is_human}]` 交给 `GroupChat(agents=cfgs, llm=...)`。

### 9.4 和「单 Agent + RAG」的关系

- 单 Agent：一个 `Assistant`，自己 RAG + 工具 loop。  
- 多 Agent：外面多一层 **Router / GroupChat**；RAG/工具仍在各个子 Agent 内部配置。  
- WebUI 可直接吃 `Router`（`MultiAgentHub`），界面里能切换/展示多个助手气泡。

---

## 10. MCP 有啥用？啥结构？

### 10.1 一句话

**MCP（Model Context Protocol）= 把外部能力（数据库、文件系统、浏览器等）做成标准「工具服务器」；Agent 通过 `function_list` 挂上这些工具，像调本地 tool 一样调。**

在 Qwen-Agent 里：**不是多 Agent**，而是 **给某个 Agent 扩工具**。多 Agent 管「谁来答」；MCP 管「能调用什么外部系统」。

### 10.2 结构

```text
Assistant / ReActChat
  └─ function_list = [
        { "mcpServers": {
            "sqlite": { "command": "uvx", "args": ["mcp-server-sqlite", "--db-path", "test.db"] },
            "某服务": { "command": "...", "args": [...] }
        }}
     ]
        ↓
  MCPManager（qwen_agent/tools/mcp_manager.py）
        ↓ 子进程拉起 MCP Server
  工具列表注册进 Agent 的 function_map
        ↓
  FnCallAgent 循环里：模型 function call → 调 MCP 工具 → 结果回写
```

对比：

| | 内置 tool（如 `code_interpreter`） | MCP |
|--|-----------------------------------|-----|
| 配置 | `function_list=['code_interpreter']` | `function_list=[{'mcpServers': {...}}]` |
| 实现位置 | 框架内 Python 类 | 外部进程（官方/第三方 MCP Server） |
| 典型用途 | 画图、跑代码 | SQLite、Git、浏览器、公司内部 API 封装成 MCP |

### 10.3 官方示例：SQLite MCP

文件：`D:\Qwen-Agent\examples\assistant_mcp_sqlite_bot.py`

启动（需已装 `uvx` / 能拉起 `mcp-server-sqlite`；首次可能下包）：

```powershell
cd D:\Qwen-Agent
.\.venv\Scripts\Activate.ps1
python examples\assistant_mcp_sqlite_bot.py
```

核心配置：

```python
tools = [{
    "mcpServers": {
        "sqlite": {
            "command": "uvx",
            "args": ["mcp-server-sqlite", "--db-path", "test.db"]
        }
    }
}]
bot = Assistant(
    llm={'model': 'qwen-max'},
    name='数据库助手',
    system_message='你扮演一个数据库助手，你具有查询数据库的能力',
    function_list=tools,
)
```

说明口径：用户问「有几张表」→ Agent function call → MCP SQLite 工具查库 → 结果进对话 → 模型组织回答。

### 10.4 多 Agent + MCP 怎么叠

```text
Router
  ├─ RAG助手（files= / UI 上传，无 MCP）
  └─ 数据库助手（function_list 挂 mcpServers.sqlite）
```

各子 Agent 各自挂自己的 MCP；Router 只负责选人。

---

## 11. 没有默认向量库怎么办？是不是不如 Dify？MCP 啥场景用？

### 11.1 先认清：缺的是「产品化知识库」，不是「不能做向量」

笔记里写「默认持久向量库 / Milvus → **不支持**」指的是：

- 开箱**没有**「上传 → 永久入库 → 管理台 CRUD → Milvus」这条产品链路；  
- 默认检索是 **BM25 + 首页**；可选的 `vector_search` 是 **每次问答临时建 FAISS**，进程结束就没了。

所以：**不是物理上做不了向量检索**，而是官方 Demo 定位是 **Agent 编排框架**，不是 Dify 那种 **RAG 知识库平台**。

### 11.2 向量检索三条路（由易到难）

| 路径 | 做法 | 持久？ | 适合 |
|------|------|--------|------|
| A. 开可选向量 | `rag_cfg` 里 `'rag_searchers': ['keyword_search', 'vector_search']`，并 `pip install langchain langchain_community faiss-cpu` | 否（临时 FAISS） | 面试演示「也能语义检索」 |
| B. 继续用默认 BM25 | 不改，短文档 / 关键词明确场景往往够用 | 切片缓存在 `workspace` | 当前 Demo、标书材料问答 |
| C. 自己接持久库 | 写自定义 Tool：查询时调 Milvus/Qdrant/ES；入库脚本另做 | 是 | 对标客户「企业知识库」 |

A 的改法（编辑 `examples\assistant_rag.py` 或绑死启动脚本）：

```python
bot = Assistant(
    llm={"model": "qwen-plus-latest"},
    rag_cfg={
        "rag_searchers": ["keyword_search", "vector_search"],  # 需 DASHSCOPE_API_KEY（embedding）
    },
)
```

C 的说明口径：入库流水线（切块→embedding→写 Milvus）与问答 Agent 分离；Agent 的 `function_list` 里挂一个 `search_kb` 工具即可——和挂 MCP 同构。

### 11.3 和 Dify 怎么选（不是谁碾压谁）

| 维度 | Qwen-Agent | Dify |
|------|------------|------|
| 定位 | **代码级 Agent 框架**（路由、工具 loop、MCP、多 Agent） | **低代码应用平台**（知识库、工作流、发布、权限） |
| 知识库 | 弱（文件 + 缓存；持久向量要自己接） | **强**（分段、向量库、引用、管理台开箱） |
| Agent / 多角色 | **强**（Router、GroupChat、源码可控） | 有，但是产品抽象，深度定制不如写代码 |
| MCP | 官方示例直接挂 `mcpServers` | 也在接生态，看版本与插件 |
| 方案选型 | 适合讲「我们能二次开发 / 嵌进现有系统」 | 适合讲「两周搭出带知识库的助手门户」 |
| 学习/面试 Demo | 看源码、讲清 RAG+Agent loop | UI 点点就能出效果 |

**结论（可背）：**

- 要 **知识库产品体验 / 持久向量 / 运营上传 CRUD** → 优先 **Dify（或同类）**，或自建入库 + 向量库。  
- 要 **Agent 编排、多专家路由、MCP 接内部系统、和现有 Python 服务集成** → **Qwen-Agent 更合适**。  
- 私有化方案常是：**Dify/自建 KB 管知识 + Agent 框架管编排与工具**；不是二选一互斥。  
- 「没有默认 Milvus」≠「不如 Dify」；是 **品类不同**。拿 Agent 框架去比知识库平台的向量开箱能力，会误判。

### 11.4 MCP 你能用在什么场景（结合私有化/面试）

MCP = 把外部系统做成标准工具，给 Agent 调。典型场景：

| 场景 | 做什么 | 示例 |
|------|--------|------|
| **业务库查询** | 问「订单状态 / 有几张表」→ 查 SQLite/MySQL | 官方 `assistant_mcp_sqlite_bot.py` |
| **运维/配置** | 读配置文件、查日志目录（只读 MCP） | filesystem MCP（注意权限） |
| **研发助手** | 查 Git 提交、提 Issue | git / GitHub MCP |
| **浏览器/页面** | 打开内网文档页抓内容 | browser / playwright 类 MCP |
| **办公协同** | 查日历、发消息（需企业授权） | 日历 / IM 的 MCP |
| **接公司已有 API** | 把内部 HTTP API 包成一个 MCP Server | 私有化最常见：工单、CMDB、权限系统 |
| **和 RAG 分工** | RAG 管「文档知识」；MCP 管「实时/结构化数据」 | 「手册怎么说」走 PDF；「库存多少」走 MCP 查库 |

**一句话分工：**  
- 文档/制度/标书 → **RAG（文件）**  
- 库表/API/实时状态 → **MCP（工具）**  
- 多个专家角色 → **多 Agent（Router）**

你现在最容易上手的 MCP Demo：SQLite 助手（笔记 §10）。私有化故事可升级为：「客户 ERP/工单 API 做成 MCP Server，Agent 只写编排，不把 SQL 写死进 prompt。」

### 11.5 建议怎么练

1. Demo 主路径继续 Qwen-Agent RAG GUI（已跑通）。  
2. 对外说明时说清：默认 BM25；要语义可开 `vector_search`；要企业级持久库用 Dify 或自建 Milvus 工具。  
3. 再跑一个 MCP：`python examples\assistant_mcp_sqlite_bot.py`，讲「非文档类能力靠工具协议扩展」。  
4. 若需求是「知识库管理台」→ 方案里写 Dify/同类，Agent 框架作进阶定制，而不是硬说 Qwen-Agent 开箱等于 Dify。

---

## 12. 版本快照

| 项 | 值 |
|---|---|
| qwen-agent | 0.0.34 |
| 额外补装 | tqdm、soundfile、gui(gradio) |
| 验收 | `import qwen_agent` → `ok`；网页入口 `app_gui()` |
| 多 Agent | `python examples\multi_agent_router.py` |
| MCP | `python examples\assistant_mcp_sqlite_bot.py` |

