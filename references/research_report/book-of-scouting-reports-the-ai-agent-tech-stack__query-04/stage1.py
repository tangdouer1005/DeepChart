from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from common import load_json, save_json
from transforms import transform

if __name__ == "__main__":
    qdir = Path(__file__).resolve().parent
    direct = load_json(qdir / "direct_data.json")
    final = transform("032", 4, direct)
    save_json(final, qdir / "final_chart_data.json")
