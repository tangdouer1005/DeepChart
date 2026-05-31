
from pathlib import Path
import sys

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
import _shared

query_dir = Path(__file__).resolve().parent
_shared.render_chart(query_dir / 'final_chart_data.json', query_dir / 'chart.png')
print(query_dir / 'chart.png')
