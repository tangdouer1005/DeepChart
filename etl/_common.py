"""Shared helpers for the Phase 3 ETL normalizers.

Source data lives in two local places (see docs/PHASE0_INVENTORY.md):
  - MIRROR : local mirror of the remote `bench/` tree (text domains).
             json paths there start with "bench/...".
  - RR_ROOT: the messy working dir holding `new_domain/...` (Research Report).

Materialization uses hardlinks (same APFS volume) so building the repo costs no
extra disk and is instant; falls back to copy across devices.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

# repo root = parent of this file's dir
REPO = Path(__file__).resolve().parent.parent

# Defaults assume the staging layout under the messy working dir. Override via env.
_WORK = Path(os.environ.get(
    "DEEPCHART_WORKDIR",
    "/Users/tangjiahui/Desktop/桌面项目整理_2026-05-30/02_DeepChart与ChartBench/chartbench",
))
MIRROR = Path(os.environ.get("DEEPCHART_MIRROR", _WORK / "tmp" / "remote_bench"))
RR_ROOT = Path(os.environ.get("DEEPCHART_RR_ROOT", _WORK))

sys.path.insert(0, str(REPO))
from schema.instance_model import Instance  # noqa: E402


def loc_bench(p: str) -> Path:
    """Map a json reference like 'bench/foo/bar' to the local mirror."""
    assert p.startswith("bench/"), p
    return MIRROR / p[len("bench/"):]


def materialize(src: Path, rel_dst: str) -> str:
    """Hardlink (or copy) src into REPO/rel_dst. Returns rel_dst (repo-relative)."""
    src = Path(src)
    if not src.exists():
        raise FileNotFoundError(src)
    dst = REPO / rel_dst
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists():
        dst.unlink()
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)
    return rel_dst


def write_jsonl(domain: str, records: list[dict]) -> Path:
    """Validate each record against the schema, then write instances/<domain>.jsonl."""
    out = REPO / "instances" / f"{domain}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w") as f:
        for r in records:
            Instance.model_validate(r)  # raises on schema violation
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"[{domain}] wrote {len(records)} records -> {out.relative_to(REPO)}")
    return out
