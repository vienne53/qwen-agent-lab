"""Hugging Face Spaces 入口：固定绑定 + 可插拔 两个助手（同一页面可切换）。"""

import os
from pathlib import Path

from qwen_agent.agents import Assistant
from qwen_agent.gui import WebUI

ROOT = Path(__file__).resolve().parent
KB_DIR = ROOT / "kb"
KB_FILES = sorted(
    str(p) for p in KB_DIR.glob("*") if p.suffix.lower() in {".md", ".txt", ".pdf", ".docx"}
)


def build_bound() -> Assistant:
    if not KB_FILES:
        raise FileNotFoundError(f"kb/ is empty: {KB_DIR}")
    return Assistant(
        llm={"model": os.getenv("QWEN_MODEL", "qwen-plus-latest")},
        name="固定知识库",
        description="已绑定仓库 kb/ 文档，无需上传也可问答。",
        system_message=(
            "你是文档助手。只根据已绑定的知识库回答；"
            "知识库没有的信息请明确说不知道，不要编造。"
        ),
        files=KB_FILES,
        rag_cfg={
            "max_ref_token": 12000,
            "parser_page_size": 500,
            "rag_keygen_strategy": "GenKeyword",
            "rag_searchers": ["keyword_search", "front_page_search"],
        },
    )


def build_pluggable() -> Assistant:
    return Assistant(
        llm={"model": os.getenv("QWEN_MODEL", "qwen-plus-latest")},
        name="可插拔知识库",
        description="请在输入框旁上传文件；清空会话即卸下该知识。",
        system_message=(
            "你是文档助手。优先依据用户本轮上传的文件回答；"
            "若未上传或文件中没有依据，请明确说明，不要编造。"
        ),
        rag_cfg={
            "max_ref_token": 12000,
            "parser_page_size": 500,
            "rag_keygen_strategy": "GenKeyword",
            "rag_searchers": ["keyword_search", "front_page_search"],
        },
    )


def main() -> None:
    if not os.getenv("DASHSCOPE_API_KEY"):
        raise RuntimeError(
            "Missing DASHSCOPE_API_KEY. "
            "On Render: Service → Environment → Add DASHSCOPE_API_KEY → Save → Manual Deploy. "
            "Do not commit the key to Git."
        )
    # Spaces / Render 等由平台提供公网地址；端口优先读环境变量 PORT
    port = int(os.getenv("PORT", "7860"))
    WebUI(
        [build_bound(), build_pluggable()],
        chatbot_config={
            "prompt.suggestions": [
                {"text": "这份知识库支持哪些文件类型？"},
                {"text": "固定绑定和可插拔有什么区别？"},
                {"text": "请根据我上传的文档做摘要"},
            ]
        },
    ).run(share=False, server_name="0.0.0.0", server_port=port)


if __name__ == "__main__":
    main()
