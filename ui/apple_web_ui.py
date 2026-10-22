"""Apple-styled Gradio shell with live RAG settings."""

from __future__ import annotations

import os
import time
from typing import Any, Dict, List, Optional

from qwen_agent.gui.utils import convert_history_to_chatbot, get_avatar_image
from qwen_agent.gui.web_ui import WebUI
from qwen_agent.llm.schema import Message

from agents_factory import DEFAULT_CFG, build_agents, cfg_summary

# 页面上可点选的 DashScope 模型（可在下面「自定义」里手填其它名）
MODEL_CHOICES = [
    # 通用文本：均衡 / 轻量 / 旗舰
    "qwen-plus-latest",
    "qwen-plus",
    "qwen-turbo",
    "qwen-turbo-latest",
    "qwen-max",
    "qwen-max-latest",
    # Qwen3 系列与长文本
    "qwen3-max",
    "qwen3-plus",
    "qwen3-flash",
    "qwen-long",
    # 多模态：视觉（-vl 自动路由 / 音频见 omni）
    "qwen-vl-max-latest",
    "qwen-vl-plus-latest",
    # 全模态（需要 qwenomni_oai model_type，见 agents_factory.llm_cfg_for_model）
    "qwen-omni-turbo-latest",
]


class AppleWebUI(WebUI):
    """WebUI + 知识库说明 + 高级设置（可热更新 Agent）。"""

    def __init__(self, agent, chatbot_config: Optional[dict] = None, agent_cfg: Optional[Dict[str, Any]] = None):
        super().__init__(agent, chatbot_config=chatbot_config)
        self.agent_cfg: Dict[str, Any] = {**DEFAULT_CFG, **(agent_cfg or {})}
        self._last_e2e_ms: Optional[float] = None

    def _model_choices(self) -> List[str]:
        cur = str(self.agent_cfg.get("model") or DEFAULT_CFG["model"])
        choices = list(MODEL_CHOICES)
        if cur and cur not in choices:
            choices = [cur] + choices
        return choices

    def _refresh_agent_meta(self) -> None:
        self.agent_config_list = [
            {
                "name": agent.name,
                "avatar": get_avatar_image(agent.name),
                "description": agent.description or "I'm a helpful assistant.",
            }
            for agent in self.agent_list
        ]

    def _create_agent_plugins_block(self, agent_index: int = 0):
        from qwen_agent.gui.gradio_dep import gr

        agent = self.agent_list[agent_index]
        name = agent.name or ""
        tools = list(getattr(agent, "function_map", {}) or {})

        if "灵活" in name:
            body = (
                "<strong>灵活知识库</strong>：在输入框旁上传 PDF / Word / TXT，"
                "本轮即可检索；清空会话后卸下。<br>"
                "<div class='hint'>不是插件商店。MCP/代码工具需在配置里启用后才会出现。</div>"
            )
        else:
            body = (
                "<strong>固定知识库</strong>：已绑定 <code>kb/</code>，无需上传。<br>"
                "<div class='hint'>不是插件商店。下面「高级设置」可改 RAG 参数。</div>"
            )
        if tools:
            body += f"<div class='hint' style='margin-top:10px'>工具（只读）：{', '.join(tools)}</div>"
        return gr.HTML(f"<div class='kb-tip'>{body}</div>")

    def _status_text(self) -> str:
        parts = [cfg_summary(self.agent_cfg)]
        if self._last_e2e_ms is not None:
            parts.append(f"上次端到端 ≈ {self._last_e2e_ms:.0f} ms（并发=1）")
        return " · ".join(parts)

    def apply_settings(
        self,
        model: str,
        max_ref_token: int,
        parser_page_size: int,
        rag_keygen_strategy: str,
        rag_searchers: List[str],
        agent_index: int = 0,
    ):
        from qwen_agent.gui.gradio_dep import gr

        searchers = rag_searchers or ["keyword_search", "front_page_search"]
        self.agent_cfg = {
            "model": (model or DEFAULT_CFG["model"]).strip(),
            "max_ref_token": int(max_ref_token),
            "parser_page_size": int(parser_page_size),
            "rag_keygen_strategy": rag_keygen_strategy,
            "rag_searchers": list(searchers),
        }
        self.agent_list = build_agents(self.agent_cfg)
        self._refresh_agent_meta()
        idx = int(agent_index or 0)
        idx = max(0, min(idx, len(self.agent_list) - 1))
        return (
            gr.update(choices=[(a.name, i) for i, a in enumerate(self.agent_list)], value=idx),
            self._create_agent_info_block(idx),
            self._create_agent_plugins_block(idx),
            self._status_text(),
            "✅ 设置已应用（新消息生效；建议清空对话后再问）",
        )

    def agent_run(self, _chatbot, _history, _agent_selector=None):
        t0 = time.perf_counter()
        if _agent_selector is None:
            gen = super().agent_run(_chatbot, _history)
        else:
            gen = super().agent_run(_chatbot, _history, _agent_selector)
        for item in gen:
            yield item
        self._last_e2e_ms = (time.perf_counter() - t0) * 1000

    def clear_chat(self):
        return [], [], self._status_text()

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
                      <p>固定知识库随时可问 · 灵活知识库随传随用 · 右侧可调 RAG</p>
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
                                height=620,
                                avatar_image_width=56,
                                flushing=False,
                                show_copy_button=True,
                            )
                            input_box = mgr.MultimodalInput(placeholder=self.input_placeholder)
                            audio_input = gr.Audio(
                                sources=["microphone"],
                                type="filepath",
                                visible=False,
                            )
                            with gr.Row():
                                clear_btn = gr.Button("清空对话", variant="secondary")

                        with gr.Column(scale=1, elem_classes="apple-panel"):
                            agent_selector = gr.Dropdown(
                                [(agent.name, i) for i, agent in enumerate(self.agent_list)],
                                label="知识库模式",
                                info="切换固定 / 灵活",
                                value=0,
                                interactive=True,
                            )
                            model_dd = gr.Dropdown(
                                choices=self._model_choices(),
                                value=str(self.agent_cfg.get("model") or DEFAULT_CFG["model"]),
                                label="模型",
                                info="点选后点下方「应用设置」生效；不在列表可改自定义名",
                                interactive=True,
                                allow_custom_value=True,
                            )
                            agent_info_block = self._create_agent_info_block()
                            agent_plugins_block = self._create_agent_plugins_block()
                            status_md = gr.Markdown(self._status_text())
                            apply_msg = gr.Markdown("")

                            with gr.Accordion("高级设置（RAG）", open=True):
                                max_ref = gr.Slider(
                                    2000,
                                    30000,
                                    value=int(self.agent_cfg.get("max_ref_token", 12000)),
                                    step=500,
                                    label="max_ref_token（注入参考上限）",
                                )
                                page_size = gr.Slider(
                                    200,
                                    2000,
                                    value=int(self.agent_cfg.get("parser_page_size", 500)),
                                    step=50,
                                    label="parser_page_size（单块 token）",
                                )
                                keygen = gr.Dropdown(
                                    choices=[
                                        "None",
                                        "GenKeyword",
                                        "SplitQueryThenGenKeyword",
                                        "GenKeywordWithKnowledge",
                                    ],
                                    value=str(self.agent_cfg.get("rag_keygen_strategy", "GenKeyword")),
                                    label="rag_keygen_strategy",
                                )
                                searchers = gr.CheckboxGroup(
                                    choices=["keyword_search", "front_page_search", "vector_search"],
                                    value=list(
                                        self.agent_cfg.get(
                                            "rag_searchers",
                                            ["keyword_search", "front_page_search"],
                                        )
                                    ),
                                    label="rag_searchers",
                                    info="vector_search 需额外依赖，且每次临时建索引",
                                )
                                gr.Markdown(
                                    "MCP：云端演示默认关闭。本机可用官方 "
                                    "`examples/assistant_mcp_sqlite_bot.py` 或后续在此扩展。"
                                )
                                apply_btn = gr.Button("应用设置", variant="primary")

                            if self.prompt_suggestions:
                                gr.Examples(
                                    label="试试这样问 / 冒烟评测题",
                                    examples=self.prompt_suggestions,
                                    inputs=[input_box],
                                )

                            agent_selector.change(
                                fn=self.change_agent,
                                inputs=[agent_selector],
                                outputs=[agent_selector, agent_info_block, agent_plugins_block],
                                queue=False,
                            )
                            apply_btn.click(
                                fn=self.apply_settings,
                                inputs=[model_dd, max_ref, page_size, keygen, searchers, agent_selector],
                                outputs=[
                                    agent_selector,
                                    agent_info_block,
                                    agent_plugins_block,
                                    status_md,
                                    apply_msg,
                                ],
                                queue=False,
                            )
                            # 只改模型时也能一键应用
                            model_dd.change(
                                fn=lambda m, a: self.apply_settings(
                                    m,
                                    int(self.agent_cfg.get("max_ref_token", 12000)),
                                    int(self.agent_cfg.get("parser_page_size", 500)),
                                    str(self.agent_cfg.get("rag_keygen_strategy", "GenKeyword")),
                                    list(
                                        self.agent_cfg.get(
                                            "rag_searchers",
                                            ["keyword_search", "front_page_search"],
                                        )
                                    ),
                                    a,
                                ),
                                inputs=[model_dd, agent_selector],
                                outputs=[
                                    agent_selector,
                                    agent_info_block,
                                    agent_plugins_block,
                                    status_md,
                                    apply_msg,
                                ],
                                queue=False,
                            )
                            clear_btn.click(
                                fn=self.clear_chat,
                                inputs=None,
                                outputs=[chatbot, history, status_md],
                                queue=False,
                            )

                            input_promise = input_box.submit(
                                fn=self.add_text,
                                inputs=[input_box, audio_input, chatbot, history],
                                outputs=[input_box, audio_input, chatbot, history],
                                queue=False,
                            ).then(
                                self.agent_run,
                                [chatbot, history, agent_selector],
                                [chatbot, history, agent_selector],
                            ).then(
                                lambda: self._status_text(),
                                None,
                                [status_md],
                            )
                            input_promise.then(self.flushed, None, [input_box])

                demo.load(None)

        demo.queue(default_concurrency_limit=concurrency_limit).launch(
            share=share,
            server_name=server_name,
            server_port=server_port,
        )
