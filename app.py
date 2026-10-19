"""公网入口：固定知识库 + 灵活知识库（苹果风 + 可调 RAG）。"""

import os

from agents_factory import DEFAULT_CFG, build_agents
from ui import AppleWebUI


def main() -> None:
    if not os.getenv("DASHSCOPE_API_KEY"):
        raise RuntimeError(
            "Missing DASHSCOPE_API_KEY. "
            "On Render: Service → Environment → Add DASHSCOPE_API_KEY → Save → Manual Deploy. "
            "Do not commit the key to Git."
        )
    port = int(os.getenv("PORT", "7860"))
    agents = build_agents(DEFAULT_CFG)
    AppleWebUI(
        agents,
        agent_cfg=DEFAULT_CFG,
        chatbot_config={
            "user.name": "你",
            "input.placeholder": "有问题尽管问；灵活模式下可先上传文件…",
            "prompt.suggestions": [
                {"text": "这份知识库支持哪些文件类型？"},
                {"text": "API Key 写在哪里？"},
                {"text": "固定知识库和灵活知识库有什么区别？"},
                {"text": "默认有没有持久向量库比如 Milvus？"},
                {"text": "请根据我上传的文档做摘要"},
            ],
        },
    ).run(share=False, server_name="0.0.0.0", server_port=port)


if __name__ == "__main__":
    main()
