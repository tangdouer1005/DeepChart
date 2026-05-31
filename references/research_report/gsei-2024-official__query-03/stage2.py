#!/usr/bin/env python3
from __future__ import annotations
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = next(parent for parent in HERE.parents if (parent / "scripts" / "startupblink_groundtruth_lib.py").exists())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.startupblink_groundtruth_lib import render_chart_from_file

QDIR = Path(__file__).resolve().parent
render_chart_from_file(QDIR / "final_chart_data.json", QDIR / "chart.png")
