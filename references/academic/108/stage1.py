import sys
import json
import numpy as np

def get_source_data():
    raw_data = [
        [
            100.859599, 120.057307, 67.6217765, 26.0744986, 103.724928, 
            100.865801, 91.3419913, 93.5064935, 15.8008658, 87.012987, 
            105.707763, 111.415525, 60.2739726, 24.4292237, 108.219178, 
            100.149158, 94.8220754, 58.3848285, 33.0279139, 93.5435755
        ],
        [
            99.1404011, 122.922636, 65.6160458, 27.2206304, 112.320917, 
            100.649351, 88.7445887, 89.3939394, 18.1818182, 82.4675325, 
            99.3150685, 107.990868, 60.9589041, 25.5707763, 109.13242, 
            104.197741, 101.214575, 54.9754954, 33.2409972, 91.4127424
        ],
        [
            100.0, 121.776504, 63.8968481, 29.7994269, 105.157593, 
            98.9177489, 85.2813853, 92.6406926, 16.6666667, 78.1385281, 
            94.9771689, 102.283105, 52.9680365, 22.8310502, 97.716895, 
            95.6744087, 94.6089921, 50.0745792, 29.1924142, 98.0183252
        ]
    ]
    return raw_data

def compute_data():
    raw_data = get_source_data()
    data_means = np.mean(raw_data, axis=0).tolist() # Convert to list for JSON

    # P-values and group labels are static, can be included directly
    annotations = [
        # iFSP1 Group (Indices 0-4)
        (0, 0, 3, r"$P = 3 \times 10^{-11}$",),
        (0, 3, 4, r"$P = 1.2 \times 10^{-11}$",),
        
        # FSEN1 Group (Indices 5-9)
        (1, 0, 3, r"$P = 1.6 \times 10^{-11}$",),
        (1, 3, 4, r"$P = 1.7 \times 10^{-10}$",),
        
        # icFSP1 Group (Indices 10-14)
        (2, 0, 3, r"$P = 1.1 \times 10^{-8}$",),
        (2, 3, 4, r"$P = 5.6 \times 10^{-9}$",),
        
        # viFSP1 Group (Indices 15-19)
        (3, 0, 3, r"$P = 2.2 \times 10^{-9}$",),
        (3, 3, 4, r"$P = 5.3 \times 10^{-9}$",),
    ]

    group_labels = ["iFSP1 (10 µM)", "FSEN1 (10 µM)", "icFSP1 (15 µM)", "viFSP1 (15 µM)"]

    output_data = {
        "scr_data": {
            "raw_data": raw_data,
            "group_labels": group_labels
        },
        "der_data": {
            "data_means": data_means,
            "annotations": annotations
        }
    }
    return output_data

if __name__ == "__main__":
    output_path = "bench/ground_truth_code/nature_1_output/108.json"
    try:
        data = compute_data()
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"Data saved to {output_path}")
    except Exception as e:
        print(f"Error computing data: {e}")
        sys.exit(1)
