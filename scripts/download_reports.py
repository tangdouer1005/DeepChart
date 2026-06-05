#!/usr/bin/env python3
"""Fetch the Research Report source PDFs that are not stored in this repo.

The RR domain uses third-party reports (CB Insights / StartupBlink / Startup
Genome) as multimodal input. They are copyrighted and excluded from the git repo
(see data/research_report/SOURCES.md). They are distributed as a single archive;
this script downloads it, extracts the 26 unique report PDFs, and places each one
into every instance directory that references it.

Usage:
    python scripts/download_reports.py            # status: how many PDFs present
    python scripts/download_reports.py --fetch    # download + extract + distribute
    python scripts/download_reports.py --list     # list missing reports
"""
from __future__ import annotations

import argparse
import json
import shutil
import tarfile
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INSTANCES = REPO / "instances" / "research_report.jsonl"

# Direct download URL for research_report_pdfs.tar.gz (Zenodo; no uploader
# identity in the URL). ~940 MB, 26 unique report PDFs.
BUNDLE_URL = "https://zenodo.org/records/20543123/files/research_report_pdfs.tar.gz?download=1"


def _instances() -> list[dict]:
    return [json.loads(l) for l in INSTANCES.read_text(encoding="utf-8").splitlines() if l.strip()]


def _instance_pdf_paths() -> list[tuple[str, Path]]:
    """(report_doc_id, absolute expected PDF path) for every instance."""
    out = []
    for d in _instances():
        rep = d["source"]["doc_id"]
        for p in d["context"]["variants"]["normal"]:
            if p.endswith(".pdf"):
                out.append((rep, REPO / p))
    return out


def status() -> tuple[int, int, list[str]]:
    pairs = _instance_pdf_paths()
    present = sum(1 for _, p in pairs if p.exists())
    missing_reports = sorted({rep for rep, p in pairs if not p.exists()})
    return present, len(pairs), missing_reports


def fetch() -> int:
    if not BUNDLE_URL:
        print("BUNDLE_URL is not set yet. Put the archive's direct URL at the top "
              "of this script (see data/research_report/SOURCES.md), then re-run "
              "with --fetch.")
        return 1
    cache = REPO / ".cache"
    cache.mkdir(exist_ok=True)
    archive = cache / "research_report_pdfs.tar.gz"
    if not archive.exists():
        print(f"Downloading {BUNDLE_URL} ...")
        urllib.request.urlretrieve(BUNDLE_URL, archive)
    extract_dir = cache / "rr_pdfs"
    if not extract_dir.exists():
        print("Extracting ...")
        with tarfile.open(archive) as t:
            t.extractall(cache)
        # archive root is research_report_pdfs/
        (cache / "research_report_pdfs").rename(extract_dir)

    # index extracted PDFs by report name
    by_report = {p.stem: p for p in extract_dir.rglob("*.pdf")}
    placed = 0
    for rep, dst in _instance_pdf_paths():
        if dst.exists():
            continue
        src = by_report.get(rep)
        if src is None:
            print(f"  [warn] no PDF for report {rep} in archive")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        placed += 1
    present, total, _ = status()
    print(f"Placed {placed} PDFs. Now {present}/{total} instance PDFs present.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true", help="download + extract + distribute")
    ap.add_argument("--list", action="store_true", help="list missing reports")
    args = ap.parse_args()

    if args.fetch:
        return fetch()

    present, total, missing = status()
    print(f"Research Report source PDFs: {present}/{total} instance copies present, "
          f"{len(missing)} reports missing.")
    if missing:
        print("Run `python scripts/download_reports.py --fetch` to download them "
              "(see data/research_report/SOURCES.md).")
        if args.list:
            for r in missing:
                print(f"  - {r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
