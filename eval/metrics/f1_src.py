#!/usr/bin/env python3
"""F1_src — faithfulness of the EXTRACTED source data vs `references.d_src`.

A model's stage-1 output is a JSON holding (at least) a source-data blob under
one of the keys below. We compare its numbers against the gold `d_src` file.
"""
from __future__ import annotations

from typing import Any

from .f1 import calculate_f1, extract_values, extract_values_from_file

SRC_KEYS = ["src_data", "scr_data", "raw_data", "source_data"]


def _get(obj: Any, keys: list[str]) -> Any:
    if isinstance(obj, dict):
        # stage-1 output may wrap everything in "data_list"
        root = obj.get("data_list", obj)
        if isinstance(root, dict):
            for k in keys:
                if k in root:
                    return root[k]
    return {}


def score(d_src_path: str, stage1_output: dict) -> dict[str, float]:
    """Returns {f1, precision, recall} for source-data extraction."""
    gt_vals = extract_values_from_file(d_src_path)
    gen_vals = extract_values(_get(stage1_output, SRC_KEYS))
    f1, p, r = calculate_f1(gt_vals, gen_vals)
    return {"f1": f1, "precision": p, "recall": r}
