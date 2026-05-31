import sys
import json
import numpy as np

def compute_data():
    # 2. Source Data Extraction
    # Data manually extracted from the provided Markdown table to ensure integrity.
    # X-axis: ML210 [log] (mapped to log[RSL3] in chart)
    x_data = [-2.0, -0.3, 0.0, 0.3979, 0.6989, 1.0]

    # LN7 1134BL WT Data (Columns 7, 8, 9)
    # Rows correspond to the x_data points
    wt_replicates = [
        [100.0, 100.0, 100.0],                      # -2
        [102.763158, 100.938338, 99.6083551],       # -0.3
        [100.657895, 99.463807, 94.1253264],        # 0
        [90.7894737, 92.4932976, 88.381201],        # 0.3979
        [83.1578947, 82.30563, 86.8146214],         # 0.6989
        [85.0, 76.1394102, 80.5483029]              # 1
    ]

    # LN7 1134BL FSP1 KO Data (Columns 10, 11, 12)
    ko_replicates = [
        [100.0, 100.0, 100.0],                      # -2
        [86.3945578, 82.860262, 89.088729],         # -0.3
        [80.1587302, 78.0567686, 86.0911271],       # 0
        [68.1405896, 67.3580786, 76.0191847],       # 0.3979
        [65.9863946, 66.7030568, 70.263789],        # 0.6989
        [59.2970522, 54.5851528, 63.0695444]        # 1
    ]

    # Calculate Mean and Standard Deviation
    wt_replicates_arr = np.array(wt_replicates)
    wt_mean = np.mean(wt_replicates_arr, axis=1)
    wt_std = np.std(wt_replicates_arr, axis=1, ddof=1)

    ko_replicates_arr = np.array(ko_replicates)
    ko_mean = np.mean(ko_replicates_arr, axis=1)
    ko_std = np.std(ko_replicates_arr, axis=1, ddof=1)

    output_data = {
        "scr_data": {
            "x_data": x_data,
            "wt_replicates": wt_replicates,
            "ko_replicates": ko_replicates
        },
        "der_data": {
            "wt_mean": wt_mean.tolist(),
            "wt_std": wt_std.tolist(),
            "ko_mean": ko_mean.tolist(),
            "ko_std": ko_std.tolist()
        }
    }
    return output_data

if __name__ == "__main__":
    output_path = "bench/ground_truth_code/nature_1_output/105.json"
    try:
        data = compute_data()
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to {output_path}")
    except Exception as e:
        print(f"Error computing data: {e}")
        sys.exit(1)
