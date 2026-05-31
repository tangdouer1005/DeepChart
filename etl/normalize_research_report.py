#!/usr/bin/env python3
"""Research Report (multimodal) -> canonical.
SOURCE: new_domain_eval/new_domain/query-level.jsonl (256), paths under RR_ROOT.

query_id ("query-01") repeats across reports, so the unique id is
"<report>__<query_id>". Context is multimodal: the summary md + the source PDF.
No pre-declared level/chart_type (the model chooses the chart).
"""
from __future__ import annotations

import json
from pathlib import Path

from _common import RR_ROOT, materialize, write_jsonl

JSONL = RR_ROOT / "new_domain_eval" / "new_domain" / "query-level.jsonl"


def build() -> list[dict]:
    records = []
    for line in JSONL.read_text().splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        lid = f"{d['report']}__{d['query_id']}"          # filesystem-safe unique id
        g = d["ground_truth"]

        summary = materialize(RR_ROOT / d["summary"],
                             f"data/research_report/{lid}/normal/{Path(d['summary']).name}")
        pdf = materialize(RR_ROOT / d["src_pdf"],
                         f"data/research_report/{lid}/normal/{Path(d['src_pdf']).name}")

        d_src = materialize(RR_ROOT / g["direct_data"],
                           f"references/research_report/{lid}/d_src.json")
        d_der = materialize(RR_ROOT / g["final_chart_data"],
                           f"references/research_report/{lid}/d_der.json")
        stage1 = materialize(RR_ROOT / g["reasoning"],
                            f"references/research_report/{lid}/stage1.py")
        stage2 = materialize(RR_ROOT / g["chart_code"],
                            f"references/research_report/{lid}/stage2.py")
        chart = materialize(RR_ROOT / g["chart_image"],
                           f"references/research_report/{lid}/chart.png")

        records.append({
            "uid": f"research_report/{lid}", "domain": "research_report",
            "orig_id": d["query_id"],
            "source": {"type": d["source"], "doc_id": d["report"]},
            "info": {"level": None, "chart_type": "", "topic_domain": [],
                     "chart_description": None},
            "query": {"template": d["query"], "code_types": ["python"], "metadata": None},
            "context": {"modality": "multimodal",
                        "variants": {"normal": [summary, pdf]}},
            "references": {"d_src": d_src, "d_der": d_der,
                           "program": {"stage1_extract": stage1,
                                       "stage2_python": stage2, "stage2_html": None},
                           "chart_image": chart},
        })
    return records


if __name__ == "__main__":
    write_jsonl("research_report", build())
