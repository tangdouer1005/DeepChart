import sys
import io
import json
import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def process_data(output_filename):
    csv_data = """sample|C1|C2|C3|K21|K22|K23|K101|K102|K103|K501|K502|K503
label|0|0|0|1|1|1|2|2|2|3|3|3
Pyruvate|0.223058|0.210762|0.149665|0.379206|0.293885|0.464718|0.442063|0.254092|0.40376|0.614279|0.562326|0.429538
Citrate|0.258809|0.309936|0.356968|0.30788|0.325941|0.289485|0.296881|0.274078|0.282906|0.279333|0.314928|0.289988
Glutamate|0.367758|0.344181|0.376461|0.347516|0.379106|0.342397|0.314315|0.281335|0.302929|0.284958|0.332328|0.30411
Succinate|0.382252|0.328351|0.398149|0.360708|0.386626|0.357401|0.335758|0.298984|0.327873|0.297441|0.350486|0.323474
Fumarate|0.097648|0.104257|0.106706|0.0843699|0.0890736|0.0680718|0.0878835|0.0631375|0.0819516|0.0646776|0.0777998|0.0697304
Malate|0.0979276|0.11186|0.113111|0.0915563|0.0970604|0.069992|0.0949667|0.0724992|0.0904031|0.0690075|0.0817405|0.0725173
Aspartic acid|0.140544|0.158885|0.161802|0.132497|0.130524|0.105984|0.137745|0.0969118|0.124096|0.10052|0.12154|0.103243"""
    
    df_raw = pd.read_csv(io.StringIO(csv_data), sep='|')
    df_raw.set_index('sample', inplace=True)
    
    labels = df_raw.loc['label'].astype(int)
    features = df_raw.drop('label').T.astype(float)
    
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    pca = PCA(n_components=2)
    principal_components = pca.fit_transform(features_scaled)
    
    pca_df = pd.DataFrame(data=principal_components, columns=['PC1', 'PC2'])
    pca_df['label'] = labels.values
    
    # Invert signs to match image
    pca_df['PC1'] = pca_df['PC1'] * -1
    pca_df['PC2'] = pca_df['PC2'] * -1
    
    # Prepare output data
    raw_data_dict = {
        "features": features.to_dict(orient="list"),
        "labels": labels.tolist()
    }

    output_data = {
        "scr_data": {
            "raw_data": raw_data_dict
        },
        "der_data": {
            "pc1": pca_df['PC1'].tolist(),
            "pc2": pca_df['PC2'].tolist(),
            "labels": pca_df['label'].tolist()
        }
    }
    
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_2_output/9.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    process_data(output_file)
