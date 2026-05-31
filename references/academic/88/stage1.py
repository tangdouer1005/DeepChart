import json
import os

def process_data(output_filename='bench/ground_truth_code/nature_2_output/88.json'):
    # 2. Prepare Data
    # Data transcribed exactly from the provided Source Data table.
    raw_data = {
        "B16-F0": [
            0.94, 1.00, 1.06, 0.98, 1.05, 1.11, 1.01, 0.96, 1.04, 0.99, 
            0.97, 1.04, 0.93, 0.96, 1.12, 0.94, 0.99, 1.07, 1.01, 0.93, 
            1.06, 1.10, 0.89, 1.00, 1.04, 0.93, 1.03, 1.00, 1.00, 1.00
        ],
        "LN1-18IL": [
            0.90, 1.07, 0.97, 0.94, 1.12, 1.01, 0.82, 0.90, 0.89, 1.08, 
            1.12, 1.05, 1.07, 1.24, 1.01, 1.07, 1.11, 1.24, 0.60, 0.66, 
            0.60, 0.53, 0.66, 0.62, 0.56, 0.67, 0.59, 0.66, 1.20, 1.02
        ],
        "LN7-1112AR": [
            0.32, 0.31, 0.39, 0.31, 0.34, 0.41, 0.33, 0.55, 0.32
        ],
        "LN7-1120BL": [
            0.43, 0.42, 0.45, 0.29, 0.42, 0.43, 0.35, 0.68, 0.45
        ],
        "LN7-1134BL": [
            0.34, 0.32, 0.41, 0.45, 0.49, 0.45, 0.33, 0.76, 0.44
        ],
        "LN8-1194BR": [
            0.40, 0.35, 0.43, 0.35, 0.34, 0.35, 0.44, 0.45, 0.36, 0.31, 0.46, 0.27
        ],
        "LN8-1198AR": [
            0.54, 0.51, 0.50, 0.43, 0.46, 0.44, 0.48, 0.48, 0.45, 0.38, 0.57, 0.37
        ],
        "LN8-1205BL": [
            0.45, 0.44, 0.47, 0.33, 0.35, 0.30, 0.39, 0.35, 0.35, 0.25, 0.49, 0.28
        ],
        "LN9-1315BL": [
            0.40, 0.48, 0.46, 0.30, 0.43, 0.34
        ],
        "LN9-1358IR": [
            0.70, 0.42, 0.54, 0.40, 0.69, 0.39
        ]
    }

    # P-values from the "Statistical test" columns in Source Data
    p_values = {
        "LN7-1112AR": r"$P = 4 \times 10^{-15}$",
        "LN7-1120BL": r"$P = 4 \times 10^{-15}$",
        "LN7-1134BL": r"$P = 4 \times 10^{-15}$",
        "LN8-1194BR": r"$P = 4 \times 10^{-15}$",
        "LN8-1198AR": r"$P = 4 \times 10^{-15}$",
        "LN8-1205BL": r"$P = 4 \times 10^{-15}$",
        "LN9-1315BL": r"$P = 4 \times 10^{-15}$",
        "LN9-1358IR": r"$P = 1.8 \times 10^{-12}$"
    }
    
    return raw_data, p_values

if __name__ == "__main__":
    src_data, der_data = process_data()
    
    final_output = {
        "scr_data": src_data,
        "der_data": der_data
    }
    
    output_filename = 'bench/ground_truth_code/nature_1_output/88.json'
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    with open(output_filename, 'w') as f:
        json.dump(final_output, f, indent=4)
        
    print(f"Data saved to {output_filename}")
