import sys
import io
import pandas as pd
import json
import numpy as np

def compile_data(output_filename):
    # 1. Source Data
    csv_data = """feature_1,feature_2,feature_3,feature_4,feature_5,feature_6,feature_7,feature_8,feature_9,feature_10,feature_11,feature_12,feature_13,feature_14,feature_15,feature_16,feature_17,feature_18,feature_19,feature_20,feature_21,feature_22,feature_23,feature_24,source
86,87,91,7,95,105,8,23,103,14,1,88,9,101,21,17,111,11,11,87,92,87,25,20,NSF
98,8,28,87,56,60,72,112,82,86,70,5,81,3,80,83,12,98,109,3,25,14,143,88,NSFC
"""
    
    # Load data
    df = pd.read_csv(io.StringIO(csv_data))
    
    # 2. Data Preparation
    # Define the labels corresponding to feature_1 to feature_24 based on visual mapping
    labels_ordered = [
        "Frameworks and models",                  # feature_1
        "Exploring social and behavioral impacts",# feature_2
        "Enhancing urban efficiency",             # feature_3
        "Deploying smart city infrastructure",    # feature_4
        "Data-driven hypothesis testing",         # feature_5
        "Commercial products or services",        # feature_6
        "Collaboration with industry and government", # feature_7
        "Building practical solutions",           # feature_8
        "Understanding urban dynamics",           # feature_9
        "Theoretical framework development",      # feature_10
        "Technological innovation",               # feature_11
        "System integration",                     # feature_12
        "Supporting scalability and commercialization", # feature_13
        "Modeling and simulation",                # feature_14
        "Quantitative and qualitative analysis",  # feature_15
        "Prototyping and testing",                # feature_16
        "New theoretical insights",               # feature_17
        "Multidisciplinary collaboration",        # feature_18
        "Iterative design and development",       # feature_19
        "Investigating long-term trends",         # feature_20
        "Improved city services",                 # feature_21
        "Identification of knowledge gaps",       # feature_22
        "Guidance for policymakers",              # feature_23
        "Functioning prototypes or systems"       # feature_24
    ]
    
    # Extract values
    nsf_row = df[df['source'] == 'NSF'].iloc[0, :-1].astype(int).values
    nsfc_row = df[df['source'] == 'NSFC'].iloc[0, :-1].astype(int).values
    
    # Shift data to align with 12:00 start for plotting convenience
    labels_shifted = labels_ordered[1:] + labels_ordered[:1]
    nsf_shifted = np.concatenate([nsf_row[1:], nsf_row[:1]])
    nsfc_shifted = np.concatenate([nsfc_row[1:], nsfc_row[:1]])
    
    # Create a list of dictionaries for JSON output
    data_records = []
    for i in range(len(labels_shifted)):
        data_records.append({
            "label": labels_shifted[i],
            "nsf_value": int(nsf_shifted[i]),
            "nsfc_value": int(nsfc_shifted[i])
        })

    output_data = {
        'scr_data': data_records,
        'der_data': []
    }
    
    # Save to JSON
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_2_output/176.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compile_data(output_file)
