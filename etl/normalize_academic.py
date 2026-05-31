#!/usr/bin/env python3
"""Academic (Nature) -> canonical. SOURCE: bench/json/ (178), source.type=nature.

code_type = python (json ground_truth_code has only py+image). Normal/Long
context are runtime crops of the single full-paper md, so we store the one md as
context; the variant split is an eval-time construction (see eval/README.md).
"""
from __future__ import annotations

import glob
import json
from pathlib import Path

from _common import MIRROR, loc_bench, materialize, write_jsonl


def _ext(p: str) -> str:
    return Path(p).suffix or ".txt"


def build() -> list[dict]:
    records = []
    for f in sorted(glob.glob(str(MIRROR / "json" / "*.json")),
                    key=lambda x: int(Path(x).stem)):
        d = json.load(open(f))
        i = d["id"]
        info = d["info"]
        doi = d["data"]["paper"].split("/data/nature/")[-1].split("/")[0]

        # context: single full-paper md
        paper = materialize(loc_bench(d["data"]["paper"]),
                            f"data/academic/{i}/normal/{Path(d['data']['paper']).name}")

        # references
        d_src = materialize(loc_bench(d["ground_truth_table"]),
                           f"references/academic/{i}/d_src{_ext(d['ground_truth_table'])}")
        d_der = None
        der_src = MIRROR / "ground_truth_code" / "nature_2_output" / f"{i}.json"
        if der_src.exists():
            d_der = materialize(der_src, f"references/academic/{i}/d_der.json")

        stage1 = None
        s1 = MIRROR / "ground_truth_code" / "nature_1" / f"{i}.py"
        if s1.exists():
            stage1 = materialize(s1, f"references/academic/{i}/stage1.py")

        stage2_py = materialize(loc_bench(d["ground_truth_code"]["py"]),
                               f"references/academic/{i}/stage2.py")
        stage2_html = None
        s2h = MIRROR / "ground_truth_code" / "nature_2_html" / f"{i}.html"
        if s2h.exists():
            stage2_html = materialize(s2h, f"references/academic/{i}/stage2.html")

        chart_img = materialize(loc_bench(d["ground_truth_image"]),
                               f"references/academic/{i}/chart.png")

        records.append({
            "uid": f"academic/{i}", "domain": "academic", "orig_id": str(i),
            "source": {"type": "nature", "doc_id": doi,
                       "url": info["source"].get("url", ""),
                       "fig": info["source"].get("fig", ""),
                       "notes": info["source"].get("notes", "")},
            "info": {"level": info["level"], "chart_type": info["chart_type"],
                     "chart_type_subclass": info.get("chart_type_subclass", ""),
                     "topic_domain": info.get("domain", []),
                     "chart_description": info["source"].get("description")},
            "query": {"template": d["query"], "code_types": ["python"], "metadata": None},
            "context": {"modality": "text", "variants": {"normal": [paper]}},
            "references": {"d_src": d_src, "d_der": d_der,
                           "program": {"stage1_extract": stage1,
                                       "stage2_python": stage2_py,
                                       "stage2_html": stage2_html},
                           "chart_image": chart_img},
        })
    return records


if __name__ == "__main__":
    write_jsonl("academic", build())
