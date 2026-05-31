#!/usr/bin/env python3
"""Validate canonical instances against the schema, counts, and path existence.

Usage:
    python etl/validate.py [--repo-root .] [--check-paths]

Phase 1: runs and reports "0 instances" cleanly (jsonl not produced yet).
Phase 3: must pass with the expected counts and (with --check-paths) all
referenced files present.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

EXPECTED = {"academic": 178, "finance": 290, "research_report": 256}

# Finance instances known to lack a stage1 program (Phase 0 finding).
FINANCE_NO_STAGE1 = {"268", "278", "284", "285", "286", "288"}


def _load_model():
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from schema.instance_model import Instance  # noqa: E402
    return Instance


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--check-paths", action="store_true",
                    help="also assert every referenced data/reference file exists")
    args = ap.parse_args()
    root = Path(args.repo_root).resolve()
    Instance = _load_model()

    total_ok = total_err = 0
    for domain, expected in EXPECTED.items():
        jsonl = root / "instances" / f"{domain}.jsonl"
        if not jsonl.exists():
            print(f"[{domain}] MISSING {jsonl.relative_to(root)} (ok in Phase 1)")
            continue
        n_ok = n_err = 0
        for ln, line in enumerate(jsonl.read_text().splitlines(), 1):
            if not line.strip():
                continue
            try:
                inst = Instance.model_validate_json(line)
            except Exception as e:  # noqa: BLE001
                n_err += 1
                print(f"[{domain}:{ln}] schema error: {e}")
                continue
            if args.check_paths:
                _check_paths(root, inst, domain)
            n_ok += 1
        flag = "OK" if n_ok == expected else f"!! expected {expected}"
        print(f"[{domain}] {n_ok} valid, {n_err} invalid  {flag}")
        total_ok += n_ok
        total_err += n_err

    print(f"\nTOTAL valid={total_ok} (target 724), invalid={total_err}")
    return 1 if total_err else 0


def _check_paths(root: Path, inst, domain: str) -> None:
    paths = []
    for v in inst.context.variants.model_dump().values():
        if v:
            paths.extend(v)
    refs = inst.references
    paths.append(refs.d_src)
    if refs.d_der:
        paths.append(refs.d_der)
    for p in (refs.program.stage1_extract, refs.program.stage2_python, refs.program.stage2_html):
        if p:
            paths.append(p)
    if refs.chart_image:  # "" is allowed (render on the fly)
        paths.append(refs.chart_image)
    for p in paths:
        if not (root / p).exists():
            print(f"[{inst.uid}] MISSING path: {p}")


if __name__ == "__main__":
    raise SystemExit(main())
