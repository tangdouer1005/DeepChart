from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common import render_chart

if __name__ == "__main__":
    qdir = Path(__file__).resolve().parent
    render_chart(qdir / "final_chart_data.json", qdir / "chart.png")
