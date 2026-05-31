import sys
import io
import pandas as pd
import json

def compute_data(output_path):
    # 1. Source Data
    csv_data = """Task,CONCH,DinoSSLPath,Virchow2,H-optimus-0,UNI,BiomedCLIP,Panakeia*,Virchow,Hibou-L,Hibou-B,CTransPath,ProvGigaPath,Kaiko,Phikon,PLIP
NSCLC Subtyping,0.99268,0.97072,0.983386,0.983421,0.976415,0.978721,0.951695,0.982075,0.970615,0.969672,0.982058,0.986583,0.972414,0.952446,0.974092
BERN STAD LAUREN,0.720555,0.705261,0.729027,0.6772,0.674646,0.680686,0.656958,0.680314,0.718225,0.679581,0.655981,0.644662,0.681257,0.646098,0.656523
KIEL STAD LAUREN,0.795917,0.806003,0.794557,0.754781,0.741579,0.772257,0.787877,0.804057,0.708738,0.744629,0.767198,0.711356,0.696902,0.705138,0.701759
CPTAC CRC Sidedness,0.613278,0.60289,0.583832,0.620846,0.622291,0.557757,0.538493,0.547781,0.59257,0.573856,0.568627,0.571655,0.525628,0.553285,0.545304
DACHS CRC Sidedness,0.707539,0.736509,0.723064,0.697698,0.660742,0.676409,0.718146,0.636007,0.658513,0.66922,0.648967,0.706909,0.660542,0.636486,0.614253
Average,0.765994,0.764277,0.762773,0.746789,0.735135,0.733166,0.730634,0.730047,0.729732,0.727391,0.724566,0.724233,0.707349,0.698691,0.698386"""

    # Load data
    df = pd.read_csv(io.StringIO(csv_data))
    
    # Set Task as index
    df = df.set_index('Task')

    # Rename rows
    rename_map = {
        "NSCLC Subtyping": "NSCLC subtyping",
        "KIEL STAD LAUREN": "Kiel STAD Lauren",
        "BERN STAD LAUREN": "Bern STAD Lauren",
        "DACHS CRC Sidedness": "DACHS CRC sidedness",
        "CPTAC CRC Sidedness": "CPTAC CRC sidedness",
        "Average": "Average"
    }
    df = df.rename(index=rename_map)

    # Reorder rows
    desired_order = [
        "NSCLC subtyping",
        "Kiel STAD Lauren",
        "Bern STAD Lauren",
        "DACHS CRC sidedness",
        "CPTAC CRC sidedness",
        "Average"
    ]
    df = df.reindex(desired_order)

    # Convert to JSON
    # scr_data: raw input
    # der_data: processed split format
    df_raw = pd.read_csv(io.StringIO(csv_data))
    
    output_data = {
        "scr_data": {
            "data": df_raw.to_dict(orient='records')
        },
        "der_data": {
            "processed_data": df.to_dict(orient='split')
        }
    }

    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_2_output/16.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compute_data(output_file)
