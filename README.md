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

**仓库地址：** https://github.com/vienne53/qwen-agent-lab  

> GitHub **不能**像 Hugging Face Space 那样直接托管 Gradio 网页。演示方式是：克隆本仓 → 本机（或 Codespaces）启动 → 浏览器打开本地地址。  
> **不要**把官方 `Qwen-Agent` 整仓（含 `.venv`）推上来；本仓通过 `pip` 安装依赖即可。

## 换电脑：克隆即可跑通

### 1. 克隆

```bash
git clone https://github.com/vienne53/qwen-agent-lab.git
cd qwen-agent-lab
```

### 2. 安装依赖

**Windows（PowerShell）：**

```powershell
.\scripts\setup.ps1
```

**macOS / Linux：**

```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

或手动：

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
# Unix:    source .venv/bin/activate
pip install -r requirements.txt
```

### 3. 配置 API Key（每台电脑一次）

DashScope 密钥**不要**提交到 Git。在新电脑上设置环境变量：

```powershell
# Windows 用户环境变量（推荐）
[Environment]::SetEnvironmentVariable("DASHSCOPE_API_KEY", "你的密钥", "User")
# 然后新开一个终端
```

```bash
# macOS / Linux（可写入 ~/.bashrc 或 ~/.zshrc）
export DASHSCOPE_API_KEY="你的密钥"
```

### 4. 启动演示

推荐（两个助手同页：固定知识库 + 可插拔）：

```bash
python app.py
```

Windows 也可双击：`scripts\start_app.bat`

浏览器打开终端提示的地址（多为 `http://127.0.0.1:7860`）。

单独启动：

| 脚本 / 命令 | 模式 |
|-------------|------|
| `python apps/app_bound_kb.py` 或 `scripts/start_bound.bat` | 固定绑定 `kb/` |
| `python apps/app_pluggable_kb.py` 或 `scripts/start_pluggable.bat` | 可插拔（网页上传） |

### 5. 验收

- 固定知识库：不问上传，直接问「支持哪些文件类型？」应能答到 `kb/product_faq.md` 内容。  
- 可插拔：上传任意 PDF/MD 后再问摘要。

## 目录

```text
app.py                 # 推荐入口（双助手）
apps/                  # 单独入口
kb/                    # 固定绑定示例知识（可替换后重启）
docs/                  # 完整中文教程（RAG / 多 Agent / MCP / 调参）
scripts/               # setup + 启动脚本（相对路径，换盘符也可用）
requirements.txt
.env.example
LICENSE
```

## 教程

见 [`docs/Qwen-Agent-可复现教程.md`](docs/Qwen-Agent-可复现教程.md)。

## 关于「GitHub 演示」与公网

| 方式 | 说明 |
|------|------|
| **本仓 + 本机/另一台电脑** | 上面步骤，最稳 |
| **GitHub Codespaces** | 网页打开本仓 → Code → Codespaces → 跑 `setup` + `python app.py` → Ports 里公开 7860 |
| **Gradio share=True** | `apps/*.py` 可开临时公网链（约 72h，需能下载 frpc） |
| **Hugging Face Space** | 当前免费账号创建 Gradio Space 可能需 [PRO](https://huggingface.co/pro)；代码已兼容 `app.py` |

## 安全

- 不要提交 `DASHSCOPE_API_KEY`、`.env` 真值、客户文档。  
- 换电脑只需：clone + setup + 重新设 Key。
