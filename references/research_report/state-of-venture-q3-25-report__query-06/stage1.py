
from pathlib import Path
import json
import sys

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
import _shared

query_id = '06'
query_dir = Path(__file__).resolve().parent
direct_path = query_dir / 'direct_data.json'
final_path = query_dir / 'final_chart_data.json'

direct_data = json.loads(direct_path.read_text())
result = _shared.compute_query_result(query_id, direct_data)
final_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
print(final_path)
