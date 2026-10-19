"""Build bound / flexible Assistants from a shared config dict."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, List

from qwen_agent.agents import Assistant

ROOT = Path(__file__).resolve().parent
KB_DIR = ROOT / "kb"

DEFAULT_CFG: Dict[str, Any] = {
    "model": os.getenv("QWEN_MODEL", "qwen-plus-latest"),
    "max_ref_token": 12000,
    "parser_page_size": 500,
    "rag_keygen_strategy": "GenKeyword",
    "rag_searchers": ["keyword_search", "front_page_search"],
}


def list_kb_files() -> List[str]:
    return sorted(
        str(p) for p in KB_DIR.glob("*") if p.suffix.lower() in {".md", ".txt", ".pdf", ".docx"}
    )


def _rag_cfg(cfg: Dict[str, Any]) -> Dict[str, Any]:
    searchers = cfg.get("rag_searchers") or DEFAULT_CFG["rag_searchers"]
    if isinstance(searchers, str):
        searchers = [s.strip() for s in searchers.split(",") if s.strip()]
    return {
        "max_ref_token": int(cfg.get("max_ref_token", DEFAULT_CFG["max_ref_token"])),
        "parser_page_size": int(cfg.get("parser_page_size", DEFAULT_CFG["parser_page_size"])),
        "rag_keygen_strategy": cfg.get("rag_keygen_strategy", DEFAULT_CFG["rag_keygen_strategy"]),
        "rag_searchers": list(searchers),
    }


def build_agents(cfg: Dict[str, Any] | None = None) -> List[Assistant]:
    cfg = {**DEFAULT_CFG, **(cfg or {})}
    model = cfg.get("model") or DEFAULT_CFG["model"]
    rag = _rag_cfg(cfg)
    kb_files = list_kb_files()
    if not kb_files:
        raise FileNotFoundError(f"kb/ is empty: {KB_DIR}")

    bound = Assistant(
        llm={"model": model},
        name="固定知识库",
        description="已绑定仓库 kb/ 文档，无需上传也可问答。",
        system_message=(
            "你是文档助手。只根据已绑定的知识库回答；"
            "知识库没有的信息请明确说不知道，不要编造。"
        ),
        files=kb_files,
        rag_cfg=rag,
    )
    flexible = Assistant(
        llm={"model": model},
        name="灵活知识库",
        description="在输入框旁上传文件作为临时知识；清空会话即卸下。",
        system_message=(
            "你是文档助手。优先依据用户本轮上传的文件回答；"
            "若未上传或文件中没有依据，请明确说明，不要编造。"
        ),
        rag_cfg=rag,
    )
    return [bound, flexible]


def cfg_summary(cfg: Dict[str, Any]) -> str:
    rag = _rag_cfg(cfg)
    return (
        f"模型={cfg.get('model')} · "
        f"max_ref_token={rag['max_ref_token']} · "
        f"chunk={rag['parser_page_size']} · "
        f"keygen={rag['rag_keygen_strategy']} · "
        f"searchers={','.join(rag['rag_searchers'])}"
    )
