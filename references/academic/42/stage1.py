import pandas as pd
import numpy as np
import io
import json
import os

def compute_data(output_json_path):
    # 2. Load Source Data
    # We embed the data exactly as provided in the prompt.
    # The data is cleaned of Markdown formatting for CSV parsing.
    csv_data = """Current Density (mA/cm2),Rep1_H2,Rep1_C2H4,nan1,Rep2_H2,Rep2_C2H4,nan2,Rep3_H2,Rep3_C2H4,nan3,Avg_H2,Avg_C2H4
50,0.09562508428860417,0.27377173745173744,nan,0.08166149696561024,0.2903888803088803,nan,0.09324558327714091,0.2774304864864865,nan,0.0901774,0.28053
100,0.07264598786244099,0.3495242213642214,nan,0.06387997302764666,0.3397964478764479,nan,0.08520040458530005,0.33606292921492914,nan,0.0739088,0.341795
200,0.051187457855697914,0.41262543114543115,nan,0.04671746459878625,0.4046474131274131,nan,0.061038705327039776,0.402314054054054,nan,0.0529812,0.406529
300,0.05160035963137784,0.4295400429000429,nan,0.04587592717464599,0.42223042471042466,nan,0.062447156664418954,0.4415946014586014,nan,0.0533078,0.431122
400,0.05305664194200944,0.45169425997425994,nan,0.0496608226567768,0.43887150579150574,nan,0.06659838165879972,0.4492887696267696,nan,0.0564386,0.446618
500,0.05537828725556304,0.47332697039897037,nan,0.057444639244774096,0.45714143629343634,nan,0.06460213081591368,0.45415355057915047,nan,0.0591417,0.461541
600,0.057465048325466395,0.4859334706134706,nan,0.05663385030343897,0.46232803088803087,nan,0.0663062261182288,0.5100811788931789,nan,0.060135,0.486114
700,0.06027588864271265,0.5073731494760066,nan,0.05893998651382333,0.4818689023717595,nan,0.06692542144302088,0.5251823614635042,nan,0.0620471,0.504808
800,0.06099511126095751,0.5276463577863578,nan,0.05805394470667566,0.49906922779922785,nan,0.06894325691166553,0.542612507078507,nan,0.0626641,0.523109"""

    df = pd.read_csv(io.StringIO(csv_data))

    # 3. Process Data
    # Extract replicates for H2 and C2H4
    # The source data is in fractions (e.g., 0.09), but the chart is in % (e.g., 9).
    # We multiply by 100.
    
    h2_reps = df[['Rep1_H2', 'Rep2_H2', 'Rep3_H2']].values * 100
    c2h4_reps = df[['Rep1_C2H4', 'Rep2_C2H4', 'Rep3_C2H4']].values * 100
    
    # Calculate Mean and Standard Deviation
    h2_mean = np.mean(h2_reps, axis=1)
    h2_std = np.std(h2_reps, axis=1)
    
    c2h4_mean = np.mean(c2h4_reps, axis=1)
    c2h4_std = np.std(c2h4_reps, axis=1)
    
    current_density = df['Current Density (mA/cm2)'].tolist()

    output_data = []
    for i in range(len(current_density)):
        output_data.append({
            "Current_Density": current_density[i],
            "H2_mean": h2_mean[i],
            "H2_std": h2_std[i],
            "C2H4_mean": c2h4_mean[i],
            "C2H4_std": c2h4_std[i]
        })

    # Prepare scr_data with raw values
    scr_data = []
    for i in range(len(current_density)):
        scr_data.append({
             "Current_Density": current_density[i],
             "Rep1_H2": df.iloc[i]['Rep1_H2'] * 100,
             "Rep2_H2": df.iloc[i]['Rep2_H2'] * 100,
             "Rep3_H2": df.iloc[i]['Rep3_H2'] * 100,
             "Rep1_C2H4": df.iloc[i]['Rep1_C2H4'] * 100,
             "Rep2_C2H4": df.iloc[i]['Rep2_C2H4'] * 100,
             "Rep3_C2H4": df.iloc[i]['Rep3_C2H4'] * 100
        })

    output_json = {
        "scr_data": scr_data,
        "der_data": output_data
    }

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

    with open(output_json_path, 'w') as f:
        json.dump(output_json, f, indent=4)
    print(f"Data saved to {output_json_path}")

if __name__ == "__main__":
    output_json = "bench/ground_truth_code/nature_1_output/42.json"
    compute_data(output_json)
