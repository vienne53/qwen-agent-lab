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

> **不要**把官方 `Qwen-Agent` 整仓（含 `.venv`）推上来；本仓通过 `pip` 安装依赖即可。

### GitHub 能不能「部署成公网网页」？

| 方式 | 能不能公网跑本项目 |
|------|-------------------|
| **GitHub Pages** | **不能**。只适合静态 HTML/JS，跑不了 Python + Gradio + 调千问 API。 |
| **GitHub 仓库** | 存代码、换电脑 `clone`；**不是**应用服务器。 |
| **Render / Railway 等**（连 GitHub） | **能**。从本仓自动构建 Docker，给一个 `https://xxx.onrender.com`。 |
| **Hugging Face Space** | 能，但当前免费号创建 Gradio 可能要 PRO。 |

下面「公网部署」用 **Render 连接本 GitHub 仓库**（免费档会休眠，醒来稍慢）。

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

## 公网部署（推荐：Render 连 GitHub）

1. 打开 https://render.com → 用 **GitHub 账号登录**，授权仓库 `vienne53/qwen-agent-lab`。  
2. **New → Blueprint**，选本仓库（会读根目录 `render.yaml`）；或 **New → Web Service** → 选本仓 → Runtime 选 **Docker**。  
3. 在 Environment 里添加密钥（不要写进代码）：  
   - `DASHSCOPE_API_KEY` = 你的千问 Key  
4. Deploy。完成后得到类似：`https://qwen-agent-lab.onrender.com`（名称以控制台为准）。  
5. 免费实例一段时间无访问会休眠，下次打开可能要等 1 分钟冷启动。

仓库已包含 `Dockerfile` + `render.yaml`，推送 `main` 后 Render 可自动重新部署。

### 其它公网方式

| 方式 | 说明 |
|------|------|
| **本机 / 另一台电脑** | `python app.py` → 局域网或自己的服务器反代 |
| **GitHub Codespaces** | 临时演示：跑 `app.py` 后把 7860 端口 Public |
| **Gradio share=True** | 临时链约 72 小时 |
| **Hugging Face Space** | 可能需 [PRO](https://huggingface.co/pro) |

## 安全

- 不要提交 `DASHSCOPE_API_KEY`、`.env` 真值、客户文档。  
- 换电脑只需：clone + setup + 重新设 Key。
