import json
import numpy as np

def save_data(output_filename):
    # 1. Data Preparation
    # Extracting raw data points from the provided table (LN0 to LN9)
    # Columns Unnamed: 1 to Unnamed: 6 contain the TPM values.
    raw_data = {
        "0": [109.65, 195.875, 109.068],
        "1": [100.79, 114.565, 133.259, 133.781],
        "2": [91.3753, 141.924, 77.3639],
        "3": [99.6594, 151.292, 122.839],
        "4": [140.845, 180.585, 125.153],
        "5": [197.032, 183.955, 146.76],
        "6": [151.958, 96.4668, 134.488, 81.04, 59.3186],
        "7": [130.808, 121.361, 131.118],
        "8": [136.999, 123.907, 98.043],
        "9": [165.937, 131.635]
    }

    # Flatten data for plotting and regression
    plot_data = []

    for gen, tpms in raw_data.items():
        gen_int = int(gen)
        for tpm in tpms:
            if not np.isnan(tpm):
                plot_data.append({'Gen': gen_int, 'TPM': tpm})
    
    with open(output_filename, 'w') as f:
        json.dump({"scr_data": plot_data, "der_data": {}}, f, indent=4)

if __name__ == "__main__":
    output_file = 'bench/ground_truth_code/nature_1_output/115.json'
    save_data(output_file)
