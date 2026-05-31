#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve()
ROOT = next(p for p in HERE.parents if (p / "scripts" / "startupgenome_groundtruth_lib.py").exists())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.startupgenome_groundtruth_lib import render_chart

QDIR = Path(__file__).resolve().parent
payload = json.loads((QDIR / "final_chart_data.json").read_text())
render_chart(payload, QDIR / "chart.png")
