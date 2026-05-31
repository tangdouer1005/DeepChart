import sys
import pandas as pd
import json

def compute_data(output_path):
    # 1. Data Preparation
    data = {
        'Task Type': ['Morphology', 'Biomarker', 'Prognosis'],
        'CONCH':        [0.765994, 0.726168, 0.631888],
        'Virchow2':     [0.762773, 0.732160, 0.606537],
        'ProvGigaPath': [0.724233, 0.722228, 0.587198],
        'DinoSSLPath':  [0.764277, 0.702064, 0.602773],
        'H-optimus-0':  [0.746789, 0.704686, 0.585751],
        'UNI':          [0.735135, 0.712024, 0.572176],
        'Panakeia*':    [0.730634, 0.706015, 0.586699],
        'Virchow':      [0.730047, 0.685068, 0.587301],
        'CTransPath':   [0.724566, 0.686569, 0.577025],
        'Hibou-L':      [0.729732, 0.685489, 0.575429],
        'Hibou-B':      [0.727391, 0.684032, 0.570080],
        'BiomedCLIP':   [0.733166, 0.667362, 0.605194],
        'Kaiko':        [0.707349, 0.680724, 0.554390],
        'Phikon':       [0.698691, 0.665523, 0.589755],
        'PLIP':         [0.698386, 0.651622, 0.567466]
    }

    # Create DataFrame
    df = pd.DataFrame(data)

    # Transform data for plotting (Melt to Long Format)
    df_melted = df.melt(id_vars='Task Type', var_name='Model', value_name='AUROC')

    # Save to JSON
    # We save the melted data records and the original model order to preserve sorting
    model_order = [k for k in data.keys() if k != 'Task Type']
    
    output_data = {
        "scr_data": {
            "records": df_melted.to_dict(orient='records')
        },
        "der_data": {
            "model_order": model_order
        }
    }

    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_2_output/13.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compute_data(output_file)
