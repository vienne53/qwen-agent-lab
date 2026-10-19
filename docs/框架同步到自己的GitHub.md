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

## lab 想用「你 fork 里的框架」而不是 PyPI

默认 lab 仍是 `pip install qwen-agent`（官方发版）。  
若要强制用你 fork 上的代码，在 lab 的 `requirements.txt` 改成例如：

```text
qwen-agent[rag,gui] @ git+https://github.com/vienne53/Qwen-Agent.git@main
```

然后推 lab、让 Render 重建。  
注意：Render 每次构建会拉你 fork；官方发版不会自动进 lab，除非你再改回 PyPI 或合并 upstream 后推 fork。

## 换电脑

```powershell
git clone https://github.com/vienne53/Qwen-Agent.git
cd Qwen-Agent
git remote add upstream https://github.com/QwenLM/Qwen-Agent.git

git clone https://github.com/vienne53/qwen-agent-lab.git
```
