import json

def save_data(output_filename):
    # ---------------------------------------------------------
    # 1. Data Preparation
    # ---------------------------------------------------------
    # Raw data extracted from the provided Markdown table
    raw_data = {
        "0": [4.10245, 11.6237, 29.64],
        "1": [79.815, 127.6, 43.9972, 7.03619],
        "2": [26.9305, 94.9128, 74.5187],
        "3": [54.9296, 5.20333, 86.6899],
        "4": [17.0596, 51.9138, 95.6225],
        "5": [49.2182, 11.0186, 3.77802],
        "6": [68.2353, 39.2656, 2.02585, 1.70821, 2.8439],
        "7": [22.2469, 3.55125, 2.04192],
        "8": [1.71285, 6.08144, 30.3082],
        "9": [33.2841, 20.0993]
    }

    # Flatten data for plotting
    plot_data = []
    
    for gen, values in raw_data.items():
        gen_int = int(gen)
        for val in values:
            plot_data.append({'Generation': gen_int, 'TPM': val})
    
    with open(output_filename, 'w') as f:
        json.dump({"scr_data": plot_data, "der_data": {}}, f, indent=4)

if __name__ == "__main__":
    output_file = 'bench/ground_truth_code/nature_1_output/116.json'
    save_data(output_file)
