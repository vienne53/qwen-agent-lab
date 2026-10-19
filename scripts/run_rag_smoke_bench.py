#!/usr/bin/env python
"""Mini RAG task smoke-bench + end-to-end latency (concurrency=1).

对齐「私有化方案」文档口径：
- 测速类：只报「同时 1 路」的端到端时延（本 Demo 走 DashScope，不是自建 vLLM，
  故不做 TTFT/GPU 显存；那些要有推理服务基准环境）。
- 任务类：用 kb/product_faq.md 做小标注集，检查回答是否包含期望关键词（支撑率代理）。

用法（仓库根目录）:
  .\\.venv\\Scripts\\Activate.ps1
  python scripts\\run_rag_smoke_bench.py
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Load user-level key on Windows if shell didn't inherit it
if not os.getenv("DASHSCOPE_API_KEY"):
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as k:
            os.environ["DASHSCOPE_API_KEY"] = winreg.QueryValueEx(k, "DASHSCOPE_API_KEY")[0]
    except Exception:
        pass

from agents_factory import DEFAULT_CFG, build_agents  # noqa: E402

# 小标注集：问法 + 回答里应出现的关键词（全部小写匹配）
CASES = [
    {
        "id": "file_types",
        "query": "这份知识库支持哪些文件类型？",
        "expect_any": ["pdf", "word", "markdown", "txt", "html"],
    },
    {
        "id": "api_key",
        "query": "API Key 写在哪里？",
        "expect_any": ["dashscope_api_key", "环境变量"],
    },
    {
        "id": "binding",
        "query": "固定绑定和灵活知识库（可插拔）有什么区别？",
        "expect_any": ["固定", "上传", "files"],
    },
    {
        "id": "vector",
        "query": "默认有没有持久向量库比如 Milvus？",
        "expect_any": ["不", "milvus", "持久", "bm25"],
    },
]


def _answer_text(messages) -> str:
    if not messages:
        return ""
    last = messages[-1]
    content = last.get("content") if isinstance(last, dict) else getattr(last, "content", "")
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                parts.append(item["text"])
            else:
                parts.append(str(item))
        return "\n".join(parts)
    return str(content or "")


def main() -> int:
    if not os.getenv("DASHSCOPE_API_KEY"):
        print("ERROR: DASHSCOPE_API_KEY missing")
        return 2

    agents = build_agents(DEFAULT_CFG)
    bot = agents[0]  # 固定知识库
    results = []
    latencies = []

    print("=== RAG smoke bench (concurrency=1, bound kb/) ===")
    print(f"model={DEFAULT_CFG['model']}")
    print()

    for case in CASES:
        t0 = time.perf_counter()
        last = None
        for last in bot.run([{"role": "user", "content": case["query"]}]):
            pass
        ms = (time.perf_counter() - t0) * 1000
        latencies.append(ms)
        text = _answer_text(last)
        low = text.lower()
        hit = any(k.lower() in low for k in case["expect_any"])
        results.append(
            {
                "id": case["id"],
                "query": case["query"],
                "e2e_ms": round(ms, 1),
                "keyword_hit": hit,
                "answer_preview": text[:240].replace("\n", " "),
            }
        )
        flag = "PASS" if hit else "FAIL"
        print(f"[{flag}] {case['id']}  e2e={ms:.0f}ms  hit={hit}")
        print(f"  Q: {case['query']}")
        print(f"  A: {text[:180].replace(chr(10), ' ')}...")
        print()

    hit_rate = sum(1 for r in results if r["keyword_hit"]) / len(results)
    latencies_sorted = sorted(latencies)
    p50 = latencies_sorted[len(latencies_sorted) // 2]
    report = {
        "conditions": {
            "concurrency": 1,
            "kb": "kb/product_faq.md",
            "model": DEFAULT_CFG["model"],
            "note": "DashScope API; not a self-hosted vLLM serving bench",
        },
        "task_proxy": {
            "metric": "keyword_hit_rate",
            "value": round(hit_rate, 3),
            "n": len(results),
            "disclaimer": "无完整标注集时的冒烟代理指标，勿写成合同召回率%",
        },
        "latency_ms": {
            "e2e_p50": round(p50, 1),
            "e2e_mean": round(sum(latencies) / len(latencies), 1),
            "per_case": [r["e2e_ms"] for r in results],
        },
        "cases": results,
    }

    out = ROOT / "workspace" / "bench_last.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("=== summary ===")
    print(f"keyword_hit_rate={hit_rate:.0%}  e2e_p50={p50:.0f}ms  e2e_mean={report['latency_ms']['e2e_mean']}ms")
    print(f"wrote {out}")
    return 0 if hit_rate >= 0.75 else 1


if __name__ == "__main__":
    raise SystemExit(main())
