import sys
import io
import pandas as pd
import numpy as np
import json
import os
from scipy.optimize import curve_fit

# 1. Source Data
csv_data = """
| Unnamed: 0       | Gq              | Unnamed: 2      | Unnamed: 3      | Unnamed: 4     | Unnamed: 5     | Unnamed: 6      | Unnamed: 7   | Unnamed: 8   | Unnamed: 9   |   Unnamed: 10 | Unnamed: 11        | Unnamed: 12     | Unnamed: 13     | Unnamed: 14    | Unnamed: 15     | Unnamed: 16     | Unnamed: 17     | Unnamed: 18   | Unnamed: 19   | Unnamed: 20   |
|:-----------------|:----------------|:----------------|:----------------|:---------------|:---------------|:----------------|:-------------|:-------------|:-------------|--------------:|:-------------------|:----------------|:----------------|:---------------|:----------------|:----------------|:----------------|:--------------|:--------------|:--------------|
| Log [NT], M      | nan             | nan             | nan             | nan            | nan            | nan             | nan          | nan          | nan          |           nan | Log [SR142948A], M | nan             | nan             | nan            | nan             | nan             | nan             | nan           | nan           | nan           |
| nan              | 9-29-2022       | 9-29-2022       | 9-29-2022       | 9-30-2022      | 9-30-2022      | 9-30-2022       | 10-20-22     | 10-20-22     | 10-20-22     |           nan | nan                | 9-29-2022       | 9-29-2022       | 9-29-2022      | 9-30-2022       | 9-30-2022       | 9-30-2022       | 10-20-22      | 10-20-22      | 10-20-22      |
| 1e-05            | -0.2846707733   | -0.2922985717   | -0.3193177434   | -0.3065884008  | -0.3204788423  | -0.325865056    | -0.2960383   | -0.31831     | -0.31534     |           nan | 0.0001             | 0.01551835518   | -0.009531307549 | 0.02556414581  | 0.03727658243   | 0.04267700414   | 0.03471723089   | 0.003298      | -0.01579      | 0.008178      |
| 1e-06            | -0.2837755147   | -0.2790089656   | -0.3184799264   | -0.3001126777  | -0.3363730402  | -0.329891852    | -0.29029718  | -0.31151     | -0.31947     |           nan | 1e-05              | -0.006806356965 | 0.00325625729   | 0.0282819784   | 0.04511932267   | 0.03243180303   | 0.01454354078   | -0.02388      | -0.0164       | 0.011033      |
| 1e-07            | -0.2845085962   | -0.2884077651   | -0.3221942222   | -0.302998495   | -0.3220711242  | -0.2961996195   | -0.30170406  | -0.31268     | -0.31973     |           nan | 1e-06              | 0.01871456628   | 0.0009482251578 | 0.02596617074  | 0.02877222398   | 0.02188480918   | 0.0318877293    | -0.00356      | -0.0346       | -0.00949      |
| 1e-08            | -0.2861371087   | -0.2937983124   | -0.3064097402   | -0.1745302564  | -0.196284247   | -0.1691147899   | -0.25900445  | -0.31037     | -0.27897     |           nan | 1e-07              | 0.01906760018   | 0.00254628934   | 0.02176789121  | 0.009862852531  | 0.02745551133   | -0.003120962184 | -0.01416      | -0.03401      | -0.00575      |
| 1e-09            | -0.1364206378   | -0.1539867212   | -0.08216952403  | 0.005149619583 | 0.01530646611  | 0.02295521923   | -0.06382135  | -0.09468     | -0.07666     |           nan | 1e-08              | 0.01653917056   | -0.01479382846  | 0.005373306705 | 0.01719663542   | -0.006388936239 | 0.0006392670214 | -0.00387      | -0.03053      | -0.00429      |
| 1e-10            | -0.01474690403  | -0.002808660416 | -0.01810853665  | 0.006762902844 | 0.02158308969  | 0.005950253723  | -0.02435792  | -0.00096     | 0.011162     |           nan | 1e-09              | 0.01125208223   | -0.01402880121  | 0.001006920087 | 0.02193310818   | 0.002682548168  | -0.01002280404  | -0.00749      | -0.02674      | -0.00044      |
| 1e-11            | -0.01579522443  | 0.004394906898  | -0.01337023148  | 0.01556749636  | 0.002418979757 | -0.01260954458  | -0.00932098  | 0.001582     | 0.007514     |           nan | 1e-10              | 0.01279465807   | -0.02011770642  | 0.01028645084  | 0.0272334621    | -0.01156297641  | -0.02599588148  | -0.00415      | -0.02971      | -0.00589      |
| 1e-12            | 0               | 0               | 0               | 0              | 0              | 0               | 0            | 0            | 0            |           nan | 1e-12              | 0               | 0               | 0              | 0               | 0               | 0               | 0             | 0             | 0             |
| nan              | nan             | nan             | nan             | nan            | nan            | nan             | nan          | nan          | nan          |           nan | nan                | nan             | nan             | nan            | nan             | nan             | nan             | nan           | nan           | nan           |
| nan              | nan             | nan             | nan             | nan            | nan            | nan             | nan          | nan          | nan          |           nan | nan                | nan             | nan             | nan            | nan             | nan             | nan             | nan           | nan           | nan           |
| Log [SBI-553], M | nan             | nan             | nan             | nan            | nan            | nan             | nan          | nan          | nan          |           nan | Log [PD149163], M  | nan             | nan             | nan            | nan             | nan             | nan             | nan           | nan           | nan           |
| nan              | 9-29-2022       | 9-29-2022       | 9-29-2022       | 9-30-2022      | 9-30-2022      | 9-30-2022       | 10-20-22     | 10-20-22     | 10-20-22     |           nan | nan                | 9-29-2022       | 9-29-2022       | 9-29-2022      | 9-30-2022       | 9-30-2022       | 9-30-2022       | 10-20-22      | 10-20-22      | 10-20-22      |
| 3e-05            | -0.01784590087  | -0.01786160807  | 0.01066236004   | 0.02248613077  | 0.01276301501  | 6.222282921e-05 | -0.01537     | 0.00931      | 0.00336      |           nan | 3e-05              | -0.338614818    | -0.3405346276   | -0.3328287892  | -0.3257737864   | -0.3081186091   | -0.3407366527   | -0.33512      | -0.34039006   | -0.34201      |
| 1e-05            | -0.01078614784  | -0.01783481942  | 0.01053609922   | 0.03255674649  | 0.004401341327 | 0.02165624513   | -0.01002     | -0.00154     | 0.00063      |           nan | 1e-05              | -0.3418162111   | -0.3367490733   | -0.3211403983  | -0.259265497    | -0.2453636257   | -0.2986696077   | -0.30747      | -0.289431762  | -0.30654      |
| 3e-06            | -0.002834037491 | -0.005377666716 | 0.00834612671   | 0.03628485793  | 0.006906849447 | 0.01410939454   | -0.01118     | -0.01431     | -0.01113     |           nan | 3e-06              | -0.3046899353   | -0.3092269811   | -0.3031103094  | -0.191687865    | -0.1868550215   | -0.233524305    | -0.27924      | -0.269188268  | -0.26957      |
| 1e-06            | 0.003823173438  | -0.01830586944  | -0.001833846773 | 0.03465847306  | 0.002538107204 | 0.03278517843   | -0.01912     | -0.01871     | -0.00198     |           nan | 1e-06              | -0.2334956111   | -0.2564710655   | -0.2683567328  | -0.08709610759  | -0.07243301327  | -0.1110112919   | -0.20001      | -0.183127389  | -0.19983      |
| 3e-07            | -0.003435117025 | 0.0005049550199 | -0.005930616238 | 0.01571439573  | 0.01389873352  | 0.01591047888   | -0.01264     | -0.00377     | 0.00266      |           nan | 3e-07              | -0.08323249529  | -0.1507142521   | -0.1939446581  | -0.006178763395 | -0.02816936576  | -0.04315777776  | -0.08875      | -0.072633535  | -0.10661      |
| 1e-07            | -0.01297468774  | -0.00693527962  | 0.003296560107  | 0.03097132517  | -0.01082877846 | -0.003031684702 | -0.01612     | 0.001852     | -0.01071     |           nan | 1e-07              | -0.02705875732  | -0.05281870506  | -0.113820769   | -0.005425441483 | -0.04175331565  | 0.0008431300221 | -0.01583      | -0.030061404  | -0.03099      |
| 1e-12            | 0               | 0               | 0               | 0              | 0              | 0               | 0            | 0            | 0            |           nan | 1e-12              | 0               | 0               | 0              | 0               | 0               | 0               | 0             | 0             | 0             |
"""

def sigmoid(x, Top, Bottom, LogEC50, HillSlope):
    return Bottom + (Top - Bottom) / (1 + 10**((LogEC50 - x) * HillSlope))

def compute_data():
    # Read the markdown table
    df = pd.read_csv(io.StringIO(csv_data), sep='|', skipinitialspace=True)
    df.columns = [c.strip() for c in df.columns]
    
    if 'Unnamed: 0' in df.columns and df.iloc[:, 0].astype(str).str.contains('Log').any():
        pass 
    else:
        df = df.iloc[:, 1:-1]

    datasets = []

    def extract_block(row_start, row_end, x_col_idx, y_col_start, y_col_end, name, color):
        subset = df.iloc[row_start:row_end+1, :].copy()
        
        x_raw = subset.iloc[:, x_col_idx]
        x_vals = pd.to_numeric(x_raw, errors='coerce')
        
        y_raw = subset.iloc[:, y_col_start:y_col_end+1]
        y_vals = y_raw.apply(pd.to_numeric, errors='coerce')
        
        # Invert signal
        y_mean = y_vals.mean(axis=1) * -1
        y_sem = y_vals.sem(axis=1)
        
        x_log = np.log10(x_vals)
        
        # Curve Fitting
        x_data = x_log.values
        y_data = y_mean.values
        
        # Determine if fit is needed
        y_range = np.max(y_data) - np.min(y_data)
        
        x_smooth = []
        y_smooth = []
        
        if y_range < 0.05:
            # Flat line / connect points
            # For visualization, just use the raw points, but let's provide a smooth line that just connects them 
            # or is a straight line if it's really noise.
            # Original code plots x_data, y_data as line.
            x_smooth = x_data.tolist()
            y_smooth = y_data.tolist()
        else:
            try:
                p0 = [0.3, 0, -7, 1.0]
                popt, _ = curve_fit(sigmoid, x_data, y_data, p0=p0, maxfev=5000)
                
                # Generate smooth points
                x_min, x_max = min(x_data), max(x_data)
                x_lin = np.linspace(x_min, x_max, 100)
                y_lin = sigmoid(x_lin, *popt)
                
                x_smooth = x_lin.tolist()
                y_smooth = y_lin.tolist()
            except:
                x_smooth = x_data.tolist()
                y_smooth = y_data.tolist()
        
        return {
            'scr': {
                'name': name,
                'x': x_data.tolist(),
                'y': y_data.tolist(),
                'y_err': y_sem.values.tolist(),
                'color': color
            },
            'der': {
                'name': name,
                'x_smooth': x_smooth,
                'y_smooth': y_smooth,
                'color': color
            }
        }

    # 1. NT (Neurotensin) - Top Left
    nt_data = extract_block(2, 9, 0, 1, 9, 'NT', '#0000B2') 
    datasets.append(nt_data)

    # 2. PD (PD149163) - Bottom Right
    pd_data = extract_block(15, 21, 11, 12, 20, 'PD', '#4C9F70') 
    datasets.append(pd_data)

    # 3. SR (SR142948A) - Top Right
    sr_data = extract_block(2, 9, 11, 12, 20, 'SR', '#B200B2')
    datasets.append(sr_data)

    # 4. SBI (SBI-553) - Bottom Left
    sbi_data = extract_block(15, 21, 0, 1, 9, 'SBI', '#F59B00') 
    datasets.append(sbi_data)

    # Output Data
    scr_data = [d['scr'] for d in datasets]
    der_data = [d['der'] for d in datasets]

    output_json = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Ensure output directory exists
    output_dir = "bench/ground_truth_code/nature_1_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_path = os.path.join(output_dir, "58.json")
    
    with open(output_path, "w") as f:
        json.dump(output_json, f, indent=4)
        
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    compute_data()
