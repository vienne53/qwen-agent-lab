"""固定绑定知识库的 Agent UI：启动时 files= 指向 kb/。"""

import sys
from pathlib import Path

from qwen_agent.agents import Assistant

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ui import AppleWebUI
KB_DIR = ROOT / "kb"
KB_FILES = sorted(str(p) for p in KB_DIR.glob("*") if p.suffix.lower() in {".md", ".txt", ".pdf", ".docx"})


def build_bot() -> Assistant:
    if not KB_FILES:
        raise FileNotFoundError(f"知识库目录为空，请在 {KB_DIR} 放入 md/txt/pdf 等文件")
    return Assistant(
        llm={"model": "qwen-plus-latest"},
        name="固定知识库助手",
        description="已绑定仓库 kb/ 内文档；无需上传也可问答。",
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


def main() -> None:
    bot = build_bot()
    AppleWebUI(
        bot,
        chatbot_config={
            "user.name": "你",
            "input.placeholder": "有问题尽管问…",
            "prompt.suggestions": [
                {"text": "这份知识库支持哪些文件类型？"},
                {"text": "固定绑定和可插拔有什么区别？"},
                {"text": "API Key 应该放在哪里？"},
            ],
        },
    ).run(share=False, server_name="0.0.0.0", server_port=7862)


if __name__ == "__main__":
    main()
