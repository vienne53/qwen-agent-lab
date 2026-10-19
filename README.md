# qwen-agent-lab

基于 [Qwen-Agent](https://github.com/QwenLM/Qwen-Agent) 的可复现实验仓库：两套 Gradio UI + 中文教程。

> **不要**把本机克隆的官方 `D:\Qwen-Agent` 整仓（含 `.venv`、workspace 缓存）推到 GitHub。  
> 本仓库只放演示代码与文档；框架通过 `pip install` 安装。

## 两套 UI

| 入口 | 模式 | 说明 |
|------|------|------|
| `apps/app_bound_kb.py` | **固定绑定** | 启动时 `files=` 绑定 `kb/`，不上传也能问 |
| `apps/app_pluggable_kb.py` | **可插拔** | 不传 `files=`，网页上传/清空会话即装卸知识 |

公网演示：两个入口都使用 `WebUI(...).run(share=True)`，终端会打印 Gradio 临时公网链接（通常约 72 小时）。

## 快速开始（Windows PowerShell）

```powershell
cd D:\qwen-agent-lab
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 用户环境变量已配置 DASHSCOPE_API_KEY 时可跳过；否则：
# [Environment]::SetEnvironmentVariable("DASHSCOPE_API_KEY", "你的密钥", "User")
# 然后新开终端再启动
```

固定知识库 UI：

```powershell
python apps\app_bound_kb.py
```

可插拔知识库 UI（另开一个终端）：

```powershell
python apps\app_pluggable_kb.py
```

或双击：

- `scripts\start_bound.bat`
- `scripts\start_pluggable.bat`

浏览器打开终端中的本地地址或 `*.gradio.live` 公网链接。

## 目录

```text
apps/           # 两个 Gradio 入口
kb/             # 固定绑定用的示例知识（可替换）
docs/           # 可复现教程（安装、绑死/可插拔、RAG、多 Agent、MCP）
scripts/        # Windows 启动脚本
requirements.txt
```

## 教程

见 [`docs/Qwen-Agent-可复现教程.md`](docs/Qwen-Agent-可复现教程.md)。

## 安全

- 不要提交 `DASHSCOPE_API_KEY` 或 `.env` 真值。
- Gradio share 链接适合临时演示，不要当生产站、不要在链接里传机密。
