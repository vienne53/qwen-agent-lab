"""可插拔知识库的 Agent UI：不传 files=，由网页上传决定本轮知识。"""

import sys
from pathlib import Path

from qwen_agent.agents import Assistant

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ui import AppleWebUI


def build_bot() -> Assistant:
    return Assistant(
        llm={"model": "qwen-plus-latest"},
        name="灵活知识库助手",
        description="请在输入框旁上传 PDF/Word/TXT 等；清空会话即卸下该知识。",
        system_message=(
            "你是文档助手。优先依据用户本轮上传的文件回答；"
            "若未上传或文件中没有依据，请明确说明，不要编造。"
        ),
        # 故意不传 files= → 可插拔
        rag_cfg={
            "max_ref_token": 12000,
            "parser_page_size": 500,
            "rag_keygen_strategy": "GenKeyword",
            "rag_searchers": ["keyword_search", "front_page_search"],
        },
    )


def main() -> None:
    bot = build_bot()
    AppleWebUI(
        bot,
        chatbot_config={
            "user.name": "你",
            "input.placeholder": "上传文件后提问…",
            "prompt.suggestions": [
                {"text": "请根据我上传的文档做摘要"},
                {"text": "文档里提到的关键定义是什么？"},
                {"text": "列出文档中的三条要点"},
            ],
        },
    ).run(share=False, server_name="0.0.0.0", server_port=7863)


if __name__ == "__main__":
    main()
