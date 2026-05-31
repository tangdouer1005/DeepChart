#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import sys

HERE = Path(__file__).resolve()
ROOT = next(p for p in HERE.parents if (p / "scripts" / "build_startupblink_ibei_2026_groundtruth.py").exists())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.build_startupblink_ibei_2026_groundtruth import rebuild_final_from_direct

QDIR = Path(__file__).resolve().parent
rebuild_final_from_direct(QDIR / "direct_data.json", QDIR / "final_chart_data.json")
