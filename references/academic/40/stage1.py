import sys
import io
import pandas as pd
import numpy as np
import json

def generate_data(output_filename):
    # 1. Source Data Loading
    csv_data = """
| Unnamed: 0               | Replicat 1   | Unnamed: 2          | Unnamed: 3          |   Unnamed: 4 | Replicat 2   | Unnamed: 6          | Unnamed: 7          |   Unnamed: 8 | Replicat 3   | Unnamed: 10         | Unnamed: 11         |
|:-------------------------|:-------------|:--------------------|:--------------------|-------------:|:-------------|:--------------------|:--------------------|-------------:|:-------------|:--------------------|:--------------------|
| Current Density (mA/cm2) | Voltage      | H2 FE               | C2H4 FE             |          nan | Voltage      | H2 FE               | C2H4 FE             |          nan | Voltage      | H2 FE               | C2H4 FE             |
| 50                       | -2.19        | 0.14772951293614345 | 0.2841110201559966  |          nan | -2.21        | 0.16659888570878167 | 0.28937132854531883 |          nan | -2.18        | 0.1888294403408317  | 0.25330493150718664 |
| 100                      | -2.29        | 0.13622886439877685 | 0.35598251602440345 |          nan | -2.32        | 0.14907543682901048 | 0.33550637114835125 |          nan | -2.3         | 0.15912463821740822 | 0.29676788789945335 |
| 200                      | -2.42        | 0.12530608096033213 | 0.36550238628465515 |          nan | -2.45        | 0.1377245152430452  | 0.37442304425052125 |          nan | -2.43        | 0.15254533565244513 | 0.3435177886402429  |
| 300                      | -2.51        | 0.11464390335081295 | 0.37335524493525885 |          nan | -2.55        | 0.11102635632320186 | 0.38879786512901043 |          nan | -2.53        | 0.13583593231820743 | 0.3632693180940613  |
| 400                      | -2.6         | 0.10910135072793622 | 0.388883534833731   |          nan | -2.64        | 0.09560740292701592 | 0.41619116019255026 |          nan | -2.62        | 0.12006939120524997 | 0.38904904838695203 |
| 500                      | -2.69        | 0.10381782093740254 | 0.4165935997695558  |          nan | -2.73        | 0.09430612734127848 | 0.42967953252503405 |          nan | -2.7         | 0.11820621568028583 | 0.4104312502649696  |
| 600                      | -2.76        | 0.09963402785714663 | 0.4330863305582307  |          nan | -2.8         | 0.09568653789232114 | 0.44928148891806313 |          nan | -2.77        | 0.11560445294969272 | 0.43694898384427705 |
| 700                      | -2.83        | 0.09538907521023639 | 0.4513225621393819  |          nan | -2.86        | 0.1038688813362222  | 0.45312933890831797 |          nan | -2.83        | 0.1152933475744668  | 0.4448906002539135  |
| 800                      | -2.89        | 0.09551489238377986 | 0.457784267885434   |          nan | -2.92        | 0.10198024060175066 | 0.4568219553633485  |          nan | -2.89        | 0.11540281057686111 | 0.4581472241460321  |
"""

    # 2. Data Parsing
    lines = [line.strip() for line in csv_data.strip().split('\n')]
    data_rows = []
    
    for line in lines:
        if not line.startswith('|'): continue
        parts = [p.strip() for p in line.split('|')]
        parts = [p for p in parts if p != '']
        
        if parts[0].replace('.', '', 1).isdigit():
            data_rows.append(parts)

    current_density = []
    
    h2_reps = [[], [], []]
    c2h4_reps = [[], [], []]
    volt_reps = [[], [], []]

    for row in data_rows:
        current_density.append(float(row[0]))
        
        volt_reps[0].append(float(row[1]))
        h2_reps[0].append(float(row[2]))
        c2h4_reps[0].append(float(row[3]))
        
        volt_reps[1].append(float(row[5]))
        h2_reps[1].append(float(row[6]))
        c2h4_reps[1].append(float(row[7]))
        
        volt_reps[2].append(float(row[9]))
        h2_reps[2].append(float(row[10]))
        c2h4_reps[2].append(float(row[11]))

    h2_arr = np.array(h2_reps) * 100 
    c2h4_arr = np.array(c2h4_reps) * 100
    volt_arr = np.array(volt_reps)

    # Calculate Mean and Std Dev
    h2_mean = np.mean(h2_arr, axis=0)
    h2_std = np.std(h2_arr, axis=0)
    
    c2h4_mean = np.mean(c2h4_arr, axis=0)
    c2h4_std = np.std(c2h4_arr, axis=0)
    
    volt_mean = np.mean(volt_arr, axis=0)
    volt_std = np.std(volt_arr, axis=0)

    # Prepare data for JSON
    scr_data = {
        "current_density": current_density,
        "h2_reps": h2_reps,
        "c2h4_reps": c2h4_reps,
        "volt_reps": volt_reps
    }

    der_data = {
        "h2_mean": h2_mean.tolist(),
        "h2_std": h2_std.tolist(),
        "c2h4_mean": c2h4_mean.tolist(),
        "c2h4_std": c2h4_std.tolist(),
        "volt_mean": volt_mean.tolist(),
        "volt_std": volt_std.tolist()
    }
    
    output_json = {
        "scr_data": scr_data,
        "der_data": der_data
    }
    
    with open(output_filename, 'w') as f:
        json.dump(output_json, f, indent=4)
        
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/40.json"
    generate_data(output_file)
