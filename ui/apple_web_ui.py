"""Apple-styled Gradio shell on top of Qwen-Agent WebUI."""

from __future__ import annotations

import os
from typing import List, Optional

from qwen_agent.gui.utils import convert_history_to_chatbot
from qwen_agent.gui.web_ui import WebUI
from qwen_agent.llm.schema import Message


class AppleWebUI(WebUI):
    """Same chat/RAG behavior as WebUI, with clearer KB UX (no fake plugin store)."""

    def _create_agent_plugins_block(self, agent_index: int = 0):
        """Replace empty unclickable「插件」with a knowledge-mode tip."""
        from qwen_agent.gui.gradio_dep import gr

        agent = self.agent_list[agent_index]
        name = agent.name or ""
        tools = list(getattr(agent, "function_map", {}) or {})

        if "灵活" in name:
            body = (
                "<strong>灵活知识库</strong>：在下方输入框旁上传 PDF / Word / TXT 等，"
                "本轮对话即可检索；清空会话后即卸下。<br>"
                "<div class='hint'>右侧不是应用商店，不能点选安装插件。"
                "若以后接入代码解释器 / MCP，工具名称会出现在这里（只读展示）。</div>"
            )
        else:
            body = (
                "<strong>固定知识库</strong>：已绑定仓库 <code>kb/</code> 文档，"
                "无需上传也能问答。<br>"
                "<div class='hint'>右侧不是应用商店，不能点选安装插件。"
                "当前助手未挂载可开关工具。</div>"
            )

        if tools:
            body += (
                "<div class='hint' style='margin-top:10px'>"
                f"已挂载工具（只读）：{', '.join(tools)}"
                "</div>"
            )

        return gr.HTML(f"<div class='kb-tip'>{body}</div>")

    def run(
        self,
        messages: Optional[List[Message]] = None,
        share: bool = False,
        server_name: str = None,
        server_port: int = None,
        concurrency_limit: int = 10,
        enable_mention: bool = False,
        **kwargs,
    ):
        self.run_kwargs = kwargs
        from qwen_agent.gui.gradio_dep import gr, mgr, ms

        css_path = os.path.join(os.path.dirname(__file__), "apple.css")
        theme = gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="slate",
            neutral_hue="slate",
            radius_size="lg",
        )

        with gr.Blocks(css=css_path, theme=theme, title="知识库助手") as demo:
            with gr.Column(elem_classes="apple-shell"):
                gr.HTML(
                    """
                    <div class="apple-hero">
                      <h1>知识库助手</h1>
                      <p>固定知识库随时可问 · 灵活知识库随传随用</p>
                    </div>
                    """
                )
                history = gr.State([])
                with ms.Application():
                    with gr.Row():
                        with gr.Column(scale=4, elem_classes="apple-panel"):
                            chatbot = mgr.Chatbot(
                                value=convert_history_to_chatbot(messages=messages),
                                avatar_images=[self.user_config, self.agent_config_list],
                                height=640,
                                avatar_image_width=56,
                                flushing=False,
                                show_copy_button=True,
                            )
                            input_box = mgr.MultimodalInput(placeholder=self.input_placeholder)
                            # Keep audio component for WebUI.add_text compatibility, but hidden
                            audio_input = gr.Audio(
                                sources=["microphone"],
                                type="filepath",
                                visible=False,
                            )

                        with gr.Column(scale=1, elem_classes="apple-panel"):
                            agent_selector = None
                            if len(self.agent_list) > 1:
                                agent_selector = gr.Dropdown(
                                    [(agent.name, i) for i, agent in enumerate(self.agent_list)],
                                    label="知识库模式",
                                    info="切换固定 / 灵活两种用法",
                                    value=0,
                                    interactive=True,
                                )

                            agent_info_block = self._create_agent_info_block()
                            agent_plugins_block = self._create_agent_plugins_block()

                            if self.prompt_suggestions:
                                gr.Examples(
                                    label="试试这样问",
                                    examples=self.prompt_suggestions,
                                    inputs=[input_box],
                                )

                            if agent_selector is not None:
                                agent_selector.change(
                                    fn=self.change_agent,
                                    inputs=[agent_selector],
                                    outputs=[agent_selector, agent_info_block, agent_plugins_block],
                                    queue=False,
                                )

                            input_promise = input_box.submit(
                                fn=self.add_text,
                                inputs=[input_box, audio_input, chatbot, history],
                                outputs=[input_box, audio_input, chatbot, history],
                                queue=False,
                            )

                            if len(self.agent_list) > 1 and enable_mention:
                                input_promise = (
                                    input_promise.then(
                                        self.add_mention,
                                        [chatbot, agent_selector],
                                        [chatbot, agent_selector],
                                    ).then(
                                        self.agent_run,
                                        [chatbot, history, agent_selector],
                                        [chatbot, history, agent_selector],
                                    )
                                )
                            elif len(self.agent_list) > 1:
                                input_promise = input_promise.then(
                                    self.agent_run,
                                    [chatbot, history, agent_selector],
                                    [chatbot, history, agent_selector],
                                )
                            else:
                                input_promise = input_promise.then(
                                    self.agent_run,
                                    [chatbot, history],
                                    [chatbot, history],
                                )

                            input_promise.then(self.flushed, None, [input_box])

                demo.load(None)

        demo.queue(default_concurrency_limit=concurrency_limit).launch(
            share=share,
            server_name=server_name,
            server_port=server_port,
        )
