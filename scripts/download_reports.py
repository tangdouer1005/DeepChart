#!/usr/bin/env python3
"""Help populate the Research Report source PDFs that are NOT redistributed here.

The RR domain uses third-party reports (CB Insights / StartupBlink / Startup
Genome) as multimodal input. They are copyrighted and excluded from this repo
(see data/research_report/SOURCES.md). This script reports which expected PDFs
are present vs missing so you can drop them in (obtain from the publishers).

Usage:
    python scripts/download_reports.py            # status report
    python scripts/download_reports.py --list     # list every missing path
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INSTANCES = REPO / "instances" / "research_report.jsonl"


def expected_pdfs() -> dict[str, Path]:
    """report doc_id -> expected PDF path (one representative per report)."""
    out: dict[str, Path] = {}
    for line in INSTANCES.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        rep = d["source"]["doc_id"]
        for p in d["context"]["variants"]["normal"]:
            if p.endswith(".pdf"):
                out.setdefault(rep, REPO / p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true", help="list every missing PDF path")
    args = ap.parse_args()

    pdfs = expected_pdfs()
    present = {r: p for r, p in pdfs.items() if p.exists()}
    missing = {r: p for r, p in pdfs.items() if not p.exists()}

    print(f"Research Report source PDFs: {len(present)}/{len(pdfs)} present, "
          f"{len(missing)} missing.")
    if missing:
        print("\nMissing reports (obtain from publishers — see "
              "data/research_report/SOURCES.md):")
        for r in sorted(missing):
            print(f"  - {r}")
        if args.list:
            print("\nExpected paths:")
            for r in sorted(missing):
                print(f"  {missing[r].relative_to(REPO)}")
        print("\nNote: queries + ground-truth scoring work without the raw PDFs "
              "(the OCR'd `summary` text is included).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
