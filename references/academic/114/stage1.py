import json

def save_data(output_filename):
    # 1. Data Preparation
    # Extracted directly from the provided Markdown table
    data_dict = {
        "0": [18.3852, 18.9828, 29.2471],
        "1": [23.8849, 22.2176, 30.8746, 16.6495],
        "2": [28.1565, 50.9344, 25.8434],
        "3": [18.4267, 44.67, 24.6989],
        "4": [18.4647, 15.9874, 43.8441],
        "5": [38.9606, 25.1849, 22.7408],
        "6": [42.5473, 21.3322, 17.5755, 26.8835, 22.4924],
        "7": [29.1812, 48.6689, 26.2712],
        "8": [17.2065, 20.452, 23.9359],
        "9": [18.4808, 26.2369]
    }

    # Flatten data for DataFrame
    rows = []
    for gen, values in data_dict.items():
        gen_int = int(gen)
        for val in values:
            rows.append({'Generation': gen_int, 'TPM': val})
            
    with open(output_filename, 'w') as f:
        json.dump({"scr_data": rows, "der_data": {}}, f, indent=4)

if __name__ == "__main__":
    output_file = 'bench/ground_truth_code/nature_1_output/114.json'
    save_data(output_file)
