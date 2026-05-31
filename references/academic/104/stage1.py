import sys
import json
import numpy as np

def get_source_data():
    """
    Reconstructs the dataframe exactly from the provided Markdown table source data.
    """
    # X-axis values (Concentration log[RSL3])
    x_vals = [-2.0, -0.3, 0.0, 0.3979, 0.6989, 1.0]
    
    # Data organized by group. 
    # Structure: Key = Group Name, Value = List of lists (rows=concentrations, cols=replicates n1,n2,n3)
    # Note: Values are transcribed exactly from the provided source table.
    
    data = {
        "B16-F0 WT": [
            [100, 100, 100],                                # -2
            [106.5217, 104.9917, 129.6482],                 # -0.3
            [109.9638, 116.4725, 116.9179],                 # 0
            [86.23188, 89.35108, 92.62982],                 # 0.3979
            [61.23188, 55.24126, 53.76884],                 # 0.6989
            [36.41304, 31.78037, 30.48576]                  # 1
        ],
        "B16-F0 Fsp1 KO": [
            [100, 100, 100],                                # -2
            [110.9756, 105.0715, 107.0423],                 # -0.3
            [100.813, 89.20676, 99.37402],                  # 0
            [61.11111, 56.69701, 62.28482],                 # 0.3979
            [36.99187, 38.23147, 40.37559],                 # 0.6989
            [30.4878, 27.56827, 30.51643]                   # 1
        ],
        "LN7-1134BL WT": [
            [100, 100, 100],                                # -2
            [83.71336, 88.78101, 83.44444],                 # -0.3
            [70.03257, 76.05178, 74],                       # 0
            [44.84256, 48.00431, 51],                       # 0.3979
            [28.77307, 30.52859, 31.44444],                 # 0.6989
            [23.88708, 24.59547, 26.88889]                  # 1
        ],
        "LN7-1134BL Fsp1 KO": [
            [100, 100, 100],                                # -2
            [66.82879, 68.39482, 56.55022],                 # -0.3
            [58.85214, 55.2343, 43.34061],                  # 0
            [33.07393, 32.00399, 31.33188],                 # 0.3979
            [21.49805, 25.92223, 21.61572],                 # 0.6989
            [17.89883, 17.54736, 16.48472]                  # 1
        ]
    }
    
    return x_vals, data

def compute_stats(raw_data):
    stats = {}
    for group_name, replicates in raw_data.items():
        replicates_arr = np.array(replicates)
        y_mean = np.mean(replicates_arr, axis=1)
        y_std = np.std(replicates_arr, axis=1, ddof=1) # Sample standard deviation
        stats[group_name] = {
            "mean": y_mean.tolist(),
            "std": y_std.tolist()
        }
    return stats

if __name__ == "__main__":
    output_path = "bench/ground_truth_code/nature_1_output/104.json"
    try:
        x_vals, raw_data = get_source_data()
        stats = compute_stats(raw_data)
        
        output_data = {
            "scr_data": {
                "x_vals": x_vals,
                "raw_data": raw_data
            },
            "der_data": {
                "stats": stats
            }
        }
        
        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=4)
        print(f"Data saved to {output_path}")
    except Exception as e:
        print(f"Error computing data: {e}")
        sys.exit(1)
