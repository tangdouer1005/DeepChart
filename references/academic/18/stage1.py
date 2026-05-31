import sys
import io
import pandas as pd
import json

def compute_data(output_path):
    # 1. Source Data
    csv_data = """
| Task               |    CONCH |   Virchow2 |   BiomedCLIP |   DinoSSLPath |   Phikon |   Virchow |   ProvGigaPath |   Panakeia* |   H-optimus-0 |   CTransPath |   Hibou-L |      UNI |   Hibou-B |     PLIP |    Kaiko |
|:-------------------|---------:|-----------:|-------------:|--------------:|---------:|----------:|---------------:|------------:|--------------:|-------------:|----------:|---------:|----------:|---------:|---------:|
| BERN STAD N STATUS | 0.71867  |   0.598758 |     0.622676 |      0.627987 | 0.574063 |  0.60613  |       0.498635 |    0.564809 |      0.570485 |     0.56206  |  0.583819 | 0.573323 |  0.560453 | 0.587603 | 0.583129 |
| KIEL STAD N STATUS | 0.631522 |   0.616924 |     0.631596 |      0.632616 | 0.614332 |  0.598649 |       0.657943 |    0.608062 |      0.577523 |     0.630989 |  0.5934   | 0.629206 |  0.632883 | 0.625878 | 0.608752 |
| KIEL STAD M STATUS | 0.544224 |   0.526274 |     0.492196 |      0.506792 | 0.591025 |  0.51302  |       0.534376 |    0.525071 |      0.537186 |     0.510906 |  0.53073  | 0.504209 |  0.465878 | 0.479537 | 0.515843 |
| IEO BRCA N STATUS  | 0.575481 |   0.55847  |     0.592211 |      0.573873 | 0.564433 |  0.573822 |       0.549081 |    0.562549 |      0.54941  |     0.568043 |  0.558692 | 0.557326 |  0.565293 | 0.595723 | 0.558933 |
| CPTAC CRC N STATUS | 0.630026 |   0.615013 |     0.640146 |      0.594841 | 0.559854 |  0.568056 |       0.616402 |    0.574471 |      0.588294 |     0.572024 |  0.573611 | 0.526455 |  0.541865 | 0.54914  | 0.51918  |
| DACHS CRC N STATUS | 0.648021 |   0.632989 |     0.625073 |      0.62096  | 0.609028 |  0.594649 |       0.622209 |    0.6141   |      0.597321 |     0.594246 |  0.573889 | 0.585531 |  0.595719 | 0.571071 | 0.531017 |
| DACHS CRC M STATUS | 0.675269 |   0.697332 |     0.632462 |      0.662344 | 0.615553 |  0.65678  |       0.63174  |    0.657834 |      0.680039 |     0.600907 |  0.613861 | 0.629181 |  0.628469 | 0.563312 | 0.563876 |
| Average            | 0.631888 |   0.606537 |     0.605194 |      0.602773 | 0.589755 |  0.587301 |       0.587198 |    0.586699 |      0.585751 |     0.577025 |  0.575429 | 0.572176 |  0.57008  | 0.567466 | 0.55439  |
"""

    # 2. Data Processing
    # Read markdown table
    df = pd.read_csv(io.StringIO(csv_data), sep="|", skipinitialspace=True)
    
    # Clean column names
    df.columns = [c.strip() for c in df.columns]
    df = df.drop(columns=[c for c in df.columns if c == '' or 'Unnamed' in c])

    # Filter markdown separator row
    df = df[~df['Task'].str.contains('---', na=False)]
    
    # Set index
    df['Task'] = df['Task'].str.strip()
    
    # Copy raw data for scr_data
    df_raw = df.copy()

    df = df.set_index('Task')

    # Convert to float
    df = df.astype(float)
    
    # Rename rows
    rename_map = {
        'BERN STAD N STATUS': 'Bern STAD N-status',
        'KIEL STAD N STATUS': 'Kiel STAD N-status',
        'KIEL STAD M STATUS': 'Kiel STAD M-status',
        'IEO BRCA N STATUS': 'IEO BRCA N-status',
        'CPTAC CRC N STATUS': 'CPTAC CRC N-status',
        'DACHS CRC N STATUS': 'DACHS CRC N-status',
        'DACHS CRC M STATUS': 'DACHS CRC M-status',
        'Average': 'Average'
    }
    df = df.rename(index=rename_map)

    # Reorder rows
    desired_order = [
        'DACHS CRC M-status',
        'Kiel STAD N-status',
        'DACHS CRC N-status',
        'Bern STAD N-status',
        'CPTAC CRC N-status',
        'IEO BRCA N-status',
        'Kiel STAD M-status',
        'Average'
    ]
    df = df.reindex(desired_order)

    # Convert to JSON
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
    output_file = "bench/ground_truth_code/nature_2_output/18.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compute_data(output_file)
