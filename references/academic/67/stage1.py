import sys
import io
import pandas as pd
import numpy as np
import json

# ---------------------------------------------------------
# 1. Source Data (Embedded)
# ---------------------------------------------------------
# Data for Figure 2C Gi2 extracted from the prompt
csv_data = """Log [NT], M|0 µM|Unnamed: 2|Unnamed: 3|Unnamed: 4|Unnamed: 5|Unnamed: 6|1 µM|Unnamed: 8|Unnamed: 9|Unnamed: 10|Unnamed: 11|Unnamed: 12|3 µM|Unnamed: 14|Unnamed: 15|Unnamed: 16|Unnamed: 17|Unnamed: 18|10 µM|Unnamed: 20|Unnamed: 21|Unnamed: 22|Unnamed: 23|Unnamed: 24|30 µM|Unnamed: 26|Unnamed: 27|Unnamed: 28|Unnamed: 29
nan|10-28-2022|10-28-2022|11-4-22|11-4-22|1-6-23|1-6-23|10-28-2022|10-28-2022|11-4-22|11-4-22|1-6-23|1-6-23|10-28-2022|10-28-2022|11-4-22|11-4-22|1-6-23|1-6-23|10-28-2022|10-28-2022|11-4-22|11-4-22|1-6-23|1-6-23|10-28-2022|11-4-22|11-4-22|1-6-23|1-6-23
1e-05|-0.26864|-0.27211|-0.30694|-0.30421|-0.19562|-0.20463|-0.24832|-0.24615|-0.24732|-0.23169|-0.17771|-0.14636|-0.29424|-0.28908|-0.26322|-0.21903|-0.17156|-0.14337|-0.26232|-0.2705|-0.21355|-0.2285|-0.15007|-0.15281|-0.23803|-0.197|-0.19205|-0.15914|-0.15753
1e-06|-0.26263|-0.25174|-0.29662|-0.27927|-0.16509|-0.16618|-0.26623|-0.24799|-0.21806|-0.19955|-0.17457|-0.13057|-0.28095|-0.27477|-0.23128|-0.2162|-0.13789|-0.14327|-0.2574|-0.25484|-0.21338|-0.22167|-0.13691|-0.15009|-0.22952|-0.2101|-0.20436|-0.15599|-0.17686
1e-07|-0.27149|-0.25565|-0.29406|-0.27765|-0.19344|-0.19083|-0.24423|-0.22719|-0.21275|-0.22237|-0.14065|-0.14791|-0.2613|-0.27208|-0.20171|-0.21859|-0.11377|-0.13206|-0.25356|-0.25089|-0.21105|-0.19502|-0.13093|-0.14627|-0.22919|-0.18564|-0.18006|-0.14961|-0.14546
1e-08|-0.11302|-0.10377|-0.25088|-0.20532|-0.1288|-0.05194|-0.06564|-0.01811|-0.15872|-0.1413|-0.01953|-0.00813|-0.0938|-0.06849|-0.09961|-0.09382|0.026407|-0.06203|-0.06919|-0.05256|-0.11496|-0.12972|-0.02368|-0.00077|-0.11639|-0.12266|-0.12578|-0.05394|-0.05747
1e-09|-0.04118|-0.01842|-0.06084|-0.04651|-0.0059|0.063934|-0.0203|-0.00911|-0.01392|0.003404|0.057539|0.064097|-0.01628|-0.0172|0.005522|-0.0317|0.08131|0.056705|-0.0291|-0.02801|-0.00389|-0.00962|0.048451|0.049231|-0.05937|-0.06193|-0.05412|-0.02407|-0.01507
1e-10|0.002795|-0.01139|-0.03332|-0.01907|-0.00772|0.022652|0.000761|0.014178|-0.03659|0.018991|0.024318|0.041275|-0.0282|-0.02465|0.010756|0.031362|0.062809|0.041553|-0.01543|0.022011|0.007525|-0.02634|0.066248|0.039758|-0.03361|-0.0506|-0.04865|0.008509|-0.00396
1e-11|0.000373|0.01676|-0.04822|-0.01683|0.01759|0.031786|-0.00845|0.015489|-0.01636|0.001256|0.021097|0.025725|-0.02502|-0.01744|0.003446|-0.00972|0.034363|0.063833|-0.00571|-0.01299|0.00393|-0.03111|0.070832|0.041078|-0.03261|-0.06797|-0.06307|-0.00887|-0.02264
1e-12|-0.00677|-0.01494|-0.03355|7.36e-05|-0.0072|-0.00553|-0.02163|-0.01675|-0.07462|-0.04118|-0.02182|-0.00743|-0.01122|-0.01023|-0.01454|-0.00699|0.040261|0.01385|-0.03973|0.012962|-0.0237|-0.04311|0.041749|0.038246|0.005027|-0.08204|-0.06141|0.001129|0.008995
"""

# ---------------------------------------------------------
# 2. Data Processing
# ---------------------------------------------------------

def load_and_process_data(csv_str):
    # Read CSV, handling the separator
    df = pd.read_csv(io.StringIO(csv_str), sep='|')
    
    # Drop the first row (dates)
    df = df.iloc[1:].copy()
    
    # Convert 'Log [NT], M' to numeric
    df['Log [NT], M'] = pd.to_numeric(df['Log [NT], M'], errors='coerce')
    
    # Calculate Log10 of concentration for plotting
    # The values are like 1e-05, so log10 is -5.
    df['LogConc'] = np.log10(df['Log [NT], M'])
    
    # Define column groups based on the table structure
    # 0 µM: Cols 1-6
    # 1 µM: Cols 7-12
    # 3 µM: Cols 13-18
    # 10 µM: Cols 19-24
    # 30 µM: Cols 25-29 (Note: 30uM has fewer columns in the provided text)
    
    groups = {
        '0 µM':  list(range(1, 7)),
        '1 µM':  list(range(7, 13)),
        '3 µM':  list(range(13, 19)),
        '10 µM': list(range(19, 25)),
        '30 µM': list(range(25, 30))
    }
    
    scr_data = []
    der_data = []
    
    for label, col_indices in groups.items():
        # Extract columns
        cols = df.iloc[:, col_indices]
        
        # Clean data: remove asterisks if any, convert to float
        # The prompt mentions asterisks in other tables, checking here just in case
        cleaned_cols = cols.applymap(lambda x: str(x).replace('*', '') if isinstance(x, str) else x)
        cleaned_cols = cleaned_cols.apply(pd.to_numeric, errors='coerce')
        
        # IMPORTANT: The plot shows positive values (0 to 0.3), but data is negative (-0.3 to 0).
        # The Y-axis label is "-Delta Net BRET". We must invert the sign.
        derived_vals = cleaned_cols * -1
        
        # Calculate Mean and SEM
        means = derived_vals.mean(axis=1)
        sems = derived_vals.sem(axis=1)
        
        der_data.append({
            'label': label,
            'x': df['LogConc'].values.tolist(),
            'y': means.values.tolist(),
            'y_err': sems.values.tolist()
        })
        
        # Source Data Extraction
        group_raw = []
        x_vals = df['LogConc'].values.tolist()
        for i, x_val in enumerate(x_vals):
            replicates = cleaned_cols.iloc[i].values.tolist()
            group_raw.append({
                "x_log": x_val,
                "replicates": replicates
            })
            
        scr_data.append({
            "label": label,
            "data": group_raw
        })
        
    return {"scr_data": scr_data, "der_data": der_data}

def main():
    data = load_and_process_data(csv_data)
    output_path = "bench/ground_truth_code/nature_1_output/67.json"
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    main()
