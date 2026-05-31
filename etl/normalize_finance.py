#!/usr/bin/env python3
"""Finance (10-K) -> canonical. SOURCE: bench/json2/ (290), source.type=annual_report.

code_type = python (report_py_2 + python-rendered image/report_py both complete
290/290; html report/ + image/report kept as secondary stage2). A Finance query
spans several fiscal years; each variant therefore holds one file per year:
  normal     = md_3table_context (context.md + 3 statement md per year)
  long       = pdfs_good_md       (one full md per year)
  ultra_long = pdfs_good          (one full 10-K PDF per year)
Finance G_GT images DO exist at ground_truth_code/image/report/<id>.png.
stage1 (report_py_1) + d_der (report_py_1_output) are absent for 6 ids
(268,278,284,285,286,288) -> set null.
"""
from __future__ import annotations

import glob
import json
from pathlib import Path

from _common import MIRROR, loc_bench, materialize, write_jsonl


def _report(p: str) -> str:
    """Parent-dir name = per-year report id, e.g. nyse-abbv-2017-10K-17620484."""
    return Path(p).parent.name


def _ext(p: str) -> str:
    return Path(p).suffix or ".txt"


def build() -> list[dict]:
    records = []
    for f in sorted(glob.glob(str(MIRROR / "json2" / "*.json")),
                    key=lambda x: int(Path(x).stem)):
        d = json.load(open(f))
        i = d["id"]
        info = d["info"]

        # ---- context variants: 3 OCR-TEXT granularities (no raw PDF; the model
        # is fed text only). Sizes grow normal < long < ultra_long.
        #   normal     = the 3 financial-statement tables          (data.table)
        #   long       = tables + surrounding 10-K context.md      (data.table_context)
        #   ultra_long = the full 10-K as OCR'd markdown           (data.complete_report)
        # The raw 10-K PDFs (pdfs_good) are source provenance, NOT input -> not shipped.
        normal = []
        for grp in d["data"]["table"]:          # list of lists (3 statements/year)
            for p in grp:
                normal.append(materialize(loc_bench(p),
                              f"data/finance/{i}/normal/{_report(p)}/{Path(p).name}"))
        long = []
        for p in d["data"]["table_context"]:    # context.md (tables + context)
            long.append(materialize(loc_bench(p),
                        f"data/finance/{i}/long/{_report(p)}/{Path(p).name}"))
        ultra_long = []
        for p in d["data"]["complete_report"]:  # full-10K OCR md
            ultra_long.append(materialize(loc_bench(p),
                              f"data/finance/{i}/ultra_long/{_report(p)}/{Path(p).name}"))

        variants = {"normal": normal, "long": long, "ultra_long": ultra_long}

        # ---- references ----
        d_src = materialize(loc_bench(d["ground_truth_table"]),
                           f"references/finance/{i}/d_src{_ext(d['ground_truth_table'])}")
        d_der = None
        der = MIRROR / "ground_truth_code" / "report_py_1_output" / f"{i}.json"
        if der.exists():
            d_der = materialize(der, f"references/finance/{i}/d_der.json")
        stage1 = None
        s1 = MIRROR / "ground_truth_code" / "report_py_1" / f"{i}.py"
        if s1.exists():
            stage1 = materialize(s1, f"references/finance/{i}/stage1.py")
        stage2_py = None
        s2p = MIRROR / "ground_truth_code" / "report_py_2" / f"{i}.py"
        if s2p.exists():
            stage2_py = materialize(s2p, f"references/finance/{i}/stage2.py")
        stage2_html = materialize(loc_bench(d["ground_truth_code"]["html"]),
                                 f"references/finance/{i}/stage2.html")
        # G_GT from the PYTHON rendering (image/report_py), not the html one
        img_py = MIRROR / "ground_truth_code" / "image" / "report_py" / f"{i}.png"
        chart_img = materialize(img_py, f"references/finance/{i}/chart.png")

        records.append({
            "uid": f"finance/{i}", "domain": "finance", "orig_id": str(i),
            "source": {"type": "annual_report", "doc_id": info["company"],
                       "url": info["source"].get("url", "")},
            "info": {"level": info["level"], "chart_type": info["chart_type"],
                     "chart_type_subclass": info.get("chart_type_subclass", ""),
                     "topic_domain": info.get("domain", []), "chart_description": None},
            "query": {"template": d["query"], "code_types": ["python"],
                      "metadata": {k: info[k] for k in
                                   ("company", "indicator", "indicator_full",
                                    "start_year", "end_year") if k in info}},
            "context": {"modality": "text", "variants": variants},
            "references": {"d_src": d_src, "d_der": d_der,
                           "program": {"stage1_extract": stage1,
                                       "stage2_python": stage2_py,
                                       "stage2_html": stage2_html},
                           "chart_image": chart_img},
        })
    return records


if __name__ == "__main__":
    write_jsonl("finance", build())
