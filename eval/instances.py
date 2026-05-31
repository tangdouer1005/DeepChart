"""Load canonical instances and resolve their files for the eval harness."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from schema.instance_model import Instance  # noqa: E402

DOMAINS = ("academic", "finance", "research_report")


def load_instances(domain: str, repo_root: Path | None = None) -> list[Instance]:
    root = repo_root or REPO
    path = root / "instances" / f"{domain}.jsonl"
    out: list[Instance] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            out.append(Instance.model_validate_json(line))
    return out


def load_all(repo_root: Path | None = None) -> dict[str, list[Instance]]:
    return {d: load_instances(d, repo_root) for d in DOMAINS}


def uid_safe(uid: str) -> str:
    """Filesystem-safe form of a uid for output paths ('academic/1' -> 'academic__1')."""
    return uid.replace("/", "__")


def resolve(rel_path: str, repo_root: Path | None = None) -> Path:
    return (repo_root or REPO) / rel_path


def read_context(inst: Instance, variant: str = "normal", repo_root: Path | None = None) -> str:
    """Concatenate the context files of a given variant into one text blob.

    (For multimodal research_report the PDF is left to the caller; this returns
    the text/markdown parts.)"""
    root = repo_root or REPO
    paths = getattr(inst.context.variants, variant, None) or []
    chunks = []
    for rel in paths:
        p = root / rel
        if p.suffix.lower() in {".md", ".txt", ".csv", ".json"} and p.exists():
            chunks.append(f"\n--- {p.name} ---\n{p.read_text(encoding='utf-8', errors='ignore')}")
    return "\n".join(chunks)
