#!/usr/bin/env python3
"""F1_der — faithfulness of the DERIVED (reasoned) data vs `references.d_der`.

`d_der` is JSON for all three domains. The stage-1 output holds the derived blob
under one of the keys below. `d_der` may be null (derived == source); callers
should skip F1_der in that case.
"""
from __future__ import annotations

from typing import Any

from .f1 import calculate_f1, extract_values, extract_values_from_file

DER_KEYS = ["der_data", "derived_data", "final_chart_data", "chart_data"]


def _get(obj: Any, keys: list[str]) -> Any:
    if isinstance(obj, dict):
        root = obj.get("data_list", obj)
        if isinstance(root, dict):
            for k in keys:
                if k in root:
                    return root[k]
    return {}


def score(d_der_path: str, stage1_output: dict) -> dict[str, float]:
    """Returns {f1, precision, recall} for derived-data reasoning."""
    gt_vals = extract_values_from_file(d_der_path)
    gen_vals = extract_values(_get(stage1_output, DER_KEYS))
    f1, p, r = calculate_f1(gt_vals, gen_vals)
    return {"f1": f1, "precision": p, "recall": r}
