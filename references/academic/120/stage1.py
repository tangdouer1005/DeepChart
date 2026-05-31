import json

def save_data(output_filename):
    # ---------------------------------------------------------
    # 1. Source Data
    # ---------------------------------------------------------
    # Data extracted faithfully from the provided Markdown table.
    
    # Group: Primary Tumors (Gray)
    # Columns: GCLC (x), GPX4 (y)
    pt_gclc = [
        0.0558, 0.0758, 0.0426, 0.038, 0.1027, 0.0, 0.03, 0.0593, 0.0, 0.049, 
        0.0086, 0.0157, 0.0194, 0.0259, 0.0072, 0.0889, 0.0764, 0.0438, 0.0, 
        0.0, 0.0264, 0.0668, 0.0443, 0.0272, 0.0806
    ]
    pt_gpx4 = [
        0.06784, 0.0908, 0.0579, 0.0372, 0.1016, 0.0, 0.0271, 0.0918, 0.0, 0.0, 
        0.0462, 0.0296, 0.0508, 0.0577, 0.0206, 0.1052, 0.0421, 0.0481, 0.0458, 
        0.0268, 0.0837, 0.0445, 0.0547, 0.0391, 0.0763
    ]

    # Group: LN Metastasis (Green)
    # Columns: GCLC (x), GPX4 (y)
    ln_gclc = [
        0.0562, 0.0135, 0.0133, 0.0095, 0.0095, 0.0, 0.0221, 0.0398, 0.0461, 0.0, 
        0.0123, 0.0, 0.0882, 0.0279, 0.0408, 0.0944, 0.0039, 0.001, 0.082, 0.0, 
        0.0146, 0.0
    ]
    ln_gpx4 = [
        0.0897, 0.0488, 0.0082, 0.0635, 0.0197, 0.0041, 0.0757, 0.0758, 0.0702, 
        0.0735, 0.0378, 0.0, 0.0794, 0.1062, 0.0652, 0.086, 0.0657, 0.0837, 
        0.1191, 0.0317, 0.0584, 0.0662
    ]

    data = {
        "scr_data": {
            "pt_gclc": pt_gclc,
            "pt_gpx4": pt_gpx4,
            "ln_gclc": ln_gclc,
            "ln_gpx4": ln_gpx4
        },
        "der_data": {}
    }
    
    with open(output_filename, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    output_file = 'bench/ground_truth_code/nature_1_output/120.json'
    save_data(output_file)
