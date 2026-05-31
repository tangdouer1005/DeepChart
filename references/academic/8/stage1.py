import sys
import io
import json
import pandas as pd
from scipy import stats

def process_data(output_filename):
    csv_data = """vehicle_K,dipy_K
1.236048,0.989125
1.619549,0.56055
1.148544,0.32109
1.240917,0.850561
0.132969,-0.17079
1.456884,1.161851
0.517272,-0.22695
0.647817,0.167474"""

    df = pd.read_csv(io.StringIO(csv_data))

    v = df['vehicle_K']
    d = df['dipy_K']
    t_stat, p_val = stats.ttest_rel(v, d)
    
    output_data = {
        "scr_data": {
            "raw_data": {
                "vehicle_K": v.tolist(),
                "dipy_K": d.tolist()
            }
        },
        "der_data": {
            "comparison": {
                "t_stat": t_stat,
                "p_val": p_val
            }
        }
    }
    
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_2_output/8.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    process_data(output_file)
