---
title: Qwen Agent Lab
emoji: 📚
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 5.49.1
app_file: app.py
pinned: false
short_description: Bound vs pluggable KB agents on Qwen-Agent
python_version: "3.12"
---

# qwen-agent-lab

基于 [Qwen-Agent](https://github.com/QwenLM/Qwen-Agent)（Apache-2.0）的可复现实验：固定绑定 / 可插拔知识库 Agent + 中文教程。

> **不要**把本机克隆的官方 `Qwen-Agent` 整仓（含 `.venv`）推到 GitHub/HF。本仓是薄封装 + 文档，框架用 `pip install`。

## 两套 UI

| 入口 | 模式 | 说明 |
|------|------|------|
| `app.py`（Spaces / 推荐） | **两个助手同页** | 「固定知识库」+「可插拔知识库」可切换 |
| `apps/app_bound_kb.py` | **固定绑定** | `files=` → `kb/` |
| `apps/app_pluggable_kb.py` | **可插拔** | 网页上传，清空会话即卸下 |

### Hugging Face Space

1. 在 Space **Settings → Secrets** 添加 `DASHSCOPE_API_KEY`（不要写进代码）。  
2. 本页即 Gradio 应用入口（`app.py`）。  
3. 硬件用免费 **CPU basic** 即可（调用云端千问 API，不占本地 GPU）。

### 本机临时公网

`apps/*.py` 可用 `share=True`（需 Gradio frpc）；链接约 72 小时。

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
