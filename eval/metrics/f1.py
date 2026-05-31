"""Core numeric-F1 logic, ported verbatim (behaviour-preserving) from the
original `code/eval/simple_f1.py`.

The benchmark scores extraction/reasoning as a *bag of numbers*: pull every
numeric value out of the predicted and gold JSON, then greedily match them with
a relative tolerance. This is robust to key renaming and row/column ordering.

`F1_src` compares predicted source data vs `references.d_src`;
`F1_der` compares predicted derived data vs `references.d_der`.
Both reuse `score_values` below — see f1_src.py / f1_der.py.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def extract_values(data: Any) -> list[float]:
    """Recursively collect every numeric value from a nested JSON structure.

    Strings that parse as numbers (after stripping thousands separators) count;
    booleans do not.
    """
    values: list[float] = []
    if isinstance(data, dict):
        for value in data.values():
            values.extend(extract_values(value))
    elif isinstance(data, list):
        for item in data:
            values.extend(extract_values(item))
    elif isinstance(data, (int, float)) and not isinstance(data, bool):
        values.append(float(data))
    elif isinstance(data, str):
        try:
            clean = data.replace(",", "").strip()
            if clean:
                values.append(float(clean))
        except ValueError:
            pass
    return values


def calculate_f1(
    gt_values: list[float], gen_values: list[float], rel_tol: float = 1e-4
) -> tuple[float, float, float]:
    """Greedy one-to-one match within `rel_tol`; returns (f1, precision, recall).

    Empty-vs-empty scores a perfect 1.0 (nothing to extract, nothing wrong)."""
    if not gt_values and not gen_values:
        return 1.0, 1.0, 1.0

    tp = 0
    matched: set[int] = set()
    for gt_val in gt_values:
        best_idx, best_diff = -1, float("inf")
        for i, gen_val in enumerate(gen_values):
            if i in matched:
                continue
            diff = abs(gen_val - gt_val)
            is_match = diff == 0 if gt_val == 0 else (diff / abs(gt_val)) <= rel_tol
            if is_match and diff < best_diff:
                best_idx, best_diff = i, diff
        if best_idx != -1:
            matched.add(best_idx)
            tp += 1

    precision = tp / len(gen_values) if gen_values else 0.0
    recall = tp / len(gt_values) if gt_values else 0.0
    if precision + recall == 0:
        return 0.0, precision, recall
    f1 = 2 * precision * recall / (precision + recall)
    return f1, precision, recall


def _maybe_unwrap(obj: Any, keys: list[str]) -> Any:
    """Unwrap a common container key if present (e.g. {'records': [...]})"""
    if isinstance(obj, dict):
        for k in keys:
            if k in obj:
                return obj[k]
    return obj


def score_values(gt_json: Any, gen_values_obj: Any, *, gt_unwrap: list[str]) -> dict[str, float]:
    """Compute F1/precision/recall between a gold JSON blob and a predicted blob."""
    gt = _maybe_unwrap(gt_json, gt_unwrap)
    f1, p, r = calculate_f1(extract_values(gt), extract_values(gen_values_obj))
    return {"f1": f1, "precision": p, "recall": r}


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


import re  # noqa: E402

_NUM_RE = re.compile(r"-?\d[\d,]*\.?\d+|-?\d+")


def extract_values_from_file(path: str | Path) -> list[float]:
    """Pull numeric values out of a gold data file, format-aware.

    `references.d_der` is JSON for all three domains, but `references.d_src`
    is JSON (research_report), CSV (finance) or a markdown table (academic).
    JSON keeps structure (so `extract_values` walks it); for text/csv/md we
    regex every numeric token — consistent with the bag-of-numbers metric.
    """
    p = Path(path)
    if p.suffix.lower() == ".json":
        return extract_values(load_json(p))
    text = p.read_text(encoding="utf-8", errors="ignore")
    out: list[float] = []
    for tok in _NUM_RE.findall(text):
        try:
            out.append(float(tok.replace(",", "")))
        except ValueError:
            pass
    return out
