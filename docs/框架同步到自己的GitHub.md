# 官方更新 + 本地改动，怎么都进「你自己的」GitHub

**不要**往 `QwenLM/Qwen-Agent` 推。  
你有两个仓：

| 仓 | 地址 | 装什么 |
|----|------|--------|
| 演示 lab | https://github.com/vienne53/qwen-agent-lab | UI / 教程 / Render |
| 框架 fork | https://github.com/vienne53/Qwen-Agent | 官方源码的你的副本 + 你的改动 |

本机 `D:\Qwen-Agent` 已按下面双远程配置：

```text
origin   → https://github.com/vienne53/Qwen-Agent.git   （你的 fork，可 push）
upstream → https://github.com/QwenLM/Qwen-Agent.git     （官方，只 pull）
```

## 日常：把「你自己的改动」推上去

```powershell
cd D:\Qwen-Agent
git add <你改的文件>    # 不要 add .venv
git commit -m "说明改了什么"
git push origin main
```

## 日常：把「官方更新」同步进你的 fork

```powershell
cd D:\Qwen-Agent
git fetch upstream
git merge upstream/main
# 若有冲突，解决后再：
git push origin main
```

（也可用 `git rebase upstream/main`，习惯 merge 即可。）

## lab 现在怎么用框架

lab 的 `requirements.txt` **已经指向你的 fork**：

```text
qwen-agent[rag,gui] @ git+https://github.com/vienne53/Qwen-Agent.git@main
```

含义：

1. `pip install` / Render 构建时，从 **https://github.com/vienne53/Qwen-Agent** 拉代码并安装。  
2. **不是**每次去读官方 `QwenLM/Qwen-Agent`。  
3. **也不是**自动读本机 `D:\Qwen-Agent`；本机改完必须 `git push origin main` 到 fork，lab/Render 重建后才会用到。  
4. 「官方包 / PyPI」是以前的默认（从 pip 网站下发布版）；现已改成跟你的 fork。

流程：`官方 upstream → merge 进你本地 → push 到 vienne53/Qwen-Agent → lab/Render 装这份`。

## 换电脑

```powershell
git clone https://github.com/vienne53/Qwen-Agent.git
cd Qwen-Agent
git remote add upstream https://github.com/QwenLM/Qwen-Agent.git

git clone https://github.com/vienne53/qwen-agent-lab.git
```
