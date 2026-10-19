"""Apple-styled Gradio shell wrapping qwen_agent.gui.WebUI."""

from __future__ import annotations

import os
from typing import List, Optional

from qwen_agent.gui.utils import convert_history_to_chatbot
from qwen_agent.gui.web_ui import WebUI
from qwen_agent.llm.schema import Message

_CSS = os.path.join(os.path.dirname(__file__), "apple.css")


class AppleWebUI(WebUI):
    """Same behavior as WebUI, with Soft theme + Apple CSS + hero header."""

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

        theme = gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="slate",
            neutral_hue="slate",
            font=[
                gr.themes.GoogleFont("Source Sans 3"),
                "-apple-system",
                "BlinkMacSystemFont",
                "Helvetica Neue",
                "sans-serif",
            ],
            radius_size=gr.themes.sizes.radius_lg,
            spacing_size=gr.themes.sizes.spacing_md,
        ).set(
            body_background_fill="#f5f5f7",
            body_background_fill_dark="#f5f5f7",
            block_background_fill="#ffffff",
            block_border_width="1px",
            block_shadow="0 8px 30px rgba(0,0,0,0.06)",
            button_primary_background_fill="#0071e3",
            button_primary_background_fill_hover="#0077ed",
            button_primary_text_color="#ffffff",
            border_color_primary="rgba(0,0,0,0.08)",
        )

        with gr.Blocks(css=_CSS, theme=theme, title="Qwen Agent Lab") as demo:
            history = gr.State([])

            gr.HTML(
                """
                <div class="apple-hero">
                  <h1>Qwen Agent Lab</h1>
                  <p>固定知识库 · 可插拔上传 · 简洁对话</p>
                </div>
                """
            )

            with ms.Application():
                with gr.Row(elem_classes="container"):
                    with gr.Column(scale=4):
                        chatbot = mgr.Chatbot(
                            value=convert_history_to_chatbot(messages=messages),
                            avatar_images=[
                                self.user_config,
                                self.agent_config_list,
                            ],
                            height=720,
                            avatar_image_width=56,
                            flushing=False,
                            show_copy_button=True,
                            latex_delimiters=[
                                {"left": "\\(", "right": "\\)", "display": True},
                                {"left": "\\[", "right": "\\]", "display": True},
                            ],
                        )
                        input_box = mgr.MultimodalInput(placeholder=self.input_placeholder)
                        with gr.Accordion("语音输入（可选）", open=False):
                            audio_input = gr.Audio(sources=["microphone"], type="filepath")

                    with gr.Column(scale=1):
                        if len(self.agent_list) > 1:
                            agent_selector = gr.Dropdown(
                                [(agent.name, i) for i, agent in enumerate(self.agent_list)],
                                label="助手",
                                info="切换固定 / 可插拔知识库",
                                value=0,
                                interactive=True,
                            )

                        agent_info_block = self._create_agent_info_block()
                        agent_plugins_block = self._create_agent_plugins_block()

                        if self.prompt_suggestions:
                            gr.Examples(
                                label="试试这些",
                                examples=self.prompt_suggestions,
                                inputs=[input_box],
                            )

                    if len(self.agent_list) > 1:
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
