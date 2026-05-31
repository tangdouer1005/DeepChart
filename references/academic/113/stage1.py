import json

def save_data(output_filename):
    # 1. Data Preparation
    # Parsing the provided "Source Data" table manually into a structure
    # Keys are Generation (LN#), Values are the non-nan TPM values
    raw_data = {
        "0": [521.144, 502.542, 418.634],
        "1": [406.000, 546.786, 438.859, 507.417],
        "2": [431.356, 439.983, 451.431],
        "3": [596.385, 427.692, 397.725],
        "4": [556.008, 535.857, 556.679],
        "5": [490.246, 469.509, 611.647],
        "6": [491.132, 475.304, 531.666, 427.445, 628.977],
        "7": [662.653, 640.417, 525.559],
        "8": [508.716, 410.376, 512.663],
        "9": [501.776, 518.009]
    }

    # Flatten into a DataFrame for plotting
    rows = []
    for gen, values in raw_data.items():
        gen_int = int(gen)
        for val in values:
            rows.append({'Generation': gen_int, 'TPM': val})
    
    with open(output_filename, 'w') as f:
        json.dump({"scr_data": rows, "der_data": {}}, f, indent=4)

if __name__ == "__main__":
    output_file = 'bench/ground_truth_code/nature_1_output/113.json'
    save_data(output_file)
