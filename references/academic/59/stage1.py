import sys
import io
import pandas as pd
import numpy as np
import json
import os
from scipy.optimize import curve_fit
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

csv_data = """
Unnamed: 0,G11,Unnamed: 2,Unnamed: 3,Unnamed: 4,Unnamed: 5,Unnamed: 6,Unnamed: 7,Unnamed: 8,Unnamed: 9,Unnamed: 10,Unnamed: 11,Unnamed: 12,Unnamed: 13,Unnamed: 14,Unnamed: 15,Unnamed: 16,Unnamed: 17,Unnamed: 18,Unnamed: 19,Unnamed: 20
Log [NT] M,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,Log [SR142948A] M,nan,nan,nan,nan,nan,nan,nan,nan,nan
nan,10-27-2022,10-27-2022,10-27-2022,10-28-22,10-28-22,10-28-22,1-26-23,1-26-23,1-26-23,nan,nan,10-27-2022,10-27-2022,10-27-2022,10-28-22,10-28-22,10-28-22,1-26-23,1-26-23,1-26-23
1e-05,-0.30303,-0.30282,-0.28583,-0.30089,-0.28729,-0.30189,-0.25323,-0.25536,-0.25034,nan,0.0001,0.00041,0.015236,0.000381,-0.02693,-0.03254,-0.03043,-0.00501,-0.01106,-0.01598
1e-06,-0.31003,-0.29578,-0.29356,-0.30663,-0.28465,-0.30822,-0.24806,-0.25629,-0.25088,nan,1e-05,0.020088,0.002293,0.012814,-0.00333,-0.02885,-0.02846,-0.01216,-0.00682,-0.00417
1e-07,-0.33322,-0.31046,-0.33121,-0.32247,-0.31273,-0.30752,-0.26004,-0.26857,-0.26028,nan,1e-06,0.026049,-0.00424,0.034537,-0.02108,-0.03401,-0.01226,0.011219,0.000242,-0.00854
1e-08,-0.26646,-0.21203,-0.22524,-0.29949,-0.28921,-0.25745,-0.27731,-0.29487,-0.28025,nan,1e-07,-0.0117,-0.01407,0.004829,-0.01594,-0.00954,-0.01617,-0.00368,0.004866,-0.01149
1e-09,-0.07168,-0.06128,-0.05854,-0.06981,-0.06586,-0.0414,-0.18718,-0.22246,-0.22065,nan,1e-08,0.031768,-0.0068,0.031635,-0.00072,-0.00809,-0.00801,-0.01716,-0.02464,-0.00803
1e-10,-0.0109,0.013042,0.00957,-0.00538,0.003219,0.021555,-0.00899,-0.02872,-0.02977,nan,1e-09,-0.00107,0.003729,0.011285,-0.01865,-0.01439,0.005616,-0.00749,-0.00187,-0.0012
1e-11,-0.0248,-0.00236,0.000497,-0.00841,0.019556,0.027191,0.011828,-0.01373,-0.00675,nan,1e-10,0.002425,-0.02784,0.006075,0.011147,-0.01826,0.007284,-0.00457,-0.01237,-0.00729
1e-12,0,0,0,0,0,0,0,0,0,nan,1e-12,0,0,0,0,0,0,0,0,0
nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan
nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan
Log [SBI-553] M,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,Log [PD149163] M,nan,nan,nan,nan,nan,nan,nan,nan,nan
nan,10-27-2022,10-27-2022,10-27-2022,10-28-22,10-28-22,10-28-22,1-26-23,1-26-23,1-26-23,nan,nan,1-26-23,1-26-23,3-2-23,3-2-23,3-2-23,5-26-23,5-26-23,5-26-23,nan
3e-05,0.005378,0.042057,0.007707,0.020865,0.0239,0.006675,0.004195,0.001597,-0.00743,nan,3e-05,-0.27204,-0.29712,-0.29818,-0.29176,-0.2658,nan,nan,nan,nan
1e-05,0.023098,0.043557,0.015936,0.031693,-0.0037,0.006687,0.019648,0.003516,0.010053,nan,1e-05,-0.26599,-0.28802,-0.29799,-0.28387,-0.26445,nan,nan,nan,nan
3e-06,-0.00561,0.052117,0.020797,0.015179,0.012205,-0.08769,0.011891,-0.00562,-0.0053,nan,3e-06,-0.26244,-0.27857,-0.29463,-0.2905,-0.23894,-0.25836,-0.25825,-0.27552,nan
1e-06,0.021415,0.015621,0.006367,0.002298,-0.0067,-0.00221,0.004357,-0.00415,-0.00662,nan,1e-06,-0.26427,-0.27816,-0.25785,-0.25866,-0.21631,-0.21645,-0.25024,-0.21577,nan
3e-07,-0.01279,0.015919,-0.00114,0.000707,-0.00339,-0.0035,0.011367,-0.00365,0.003233,nan,3e-07,-0.20815,-0.23486,-0.21603,-0.21307,-0.19013,-0.16447,-0.15812,-0.17147,nan
1e-07,-0.00507,0.013791,-0.00432,-0.00635,-0.02843,0.004074,0.004932,-0.02226,-0.00432,nan,1e-07,-0.12406,-0.17286,-0.13609,-0.13711,-0.16775,-0.08329,-0.09085,-0.11236,nan
1e-12,0,0,0,0,0,0,0,0,0,nan,3e-08,nan,nan,nan,nan,nan,-0.02941,-0.00624,-0.02679,nan
nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,1e-08,nan,nan,nan,nan,nan,-0.0031,-0.02306,0.012733,nan
nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,3e-09,nan,nan,nan,nan,nan,0.000368,0.018503,0.009733,nan
nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,1e-12,0,0,0,0,0,0,0,0,nan
"""

def sigmoid(x, Top, Bottom, LogEC50, HillSlope):
    return Bottom + (Top - Bottom) / (1 + 10**((LogEC50 - x) * HillSlope))

def compute_data():
    df = pd.read_csv(io.StringIO(csv_data), header=None)

    datasets = []

    def process_data_block(row_start, row_end, x_col_idx, y_col_start, y_col_end, name, color):
        subset = df.iloc[row_start:row_end, [x_col_idx] + list(range(y_col_start, y_col_end))]
        subset = subset.apply(pd.to_numeric, errors='coerce')
        subset = subset.dropna(subset=[subset.columns[0]])
        
        x_vals = subset.iloc[:, 0].values
        y_data = subset.iloc[:, 1:].values
        
        x_log = np.log10(x_vals)
        y_mean = np.nanmean(y_data, axis=1) * -1
        y_sem = np.nanstd(y_data, axis=1, ddof=1) / np.sqrt(np.sum(~np.isnan(y_data), axis=1))
        
        x_data = x_log.tolist()
        y_vals = y_mean.tolist()
        sem_vals = y_sem.tolist()
        
        # Curve Fitting
        x_smooth = []
        y_smooth = []
        
        # Check range
        y_range = np.max(y_mean) - np.min(y_mean)
        
        if y_range < 0.05:
             # Just connect points
             x_smooth = x_data
             y_smooth = y_vals
        else:
            try:
                p0 = [max(y_mean), min(y_mean), np.median(x_log), 1.0]
                # Relaxed bounds
                popt, _ = curve_fit(sigmoid, x_log, y_mean, p0=p0, maxfev=5000)
                
                x_lin = np.linspace(min(x_log), max(x_log), 100)
                y_lin = sigmoid(x_lin, *popt)
                
                x_smooth = x_lin.tolist()
                y_smooth = y_lin.tolist()
            except:
                x_smooth = x_data
                y_smooth = y_vals
        
        return {
            'scr': {
                'name': name,
                'color': color,
                'x': x_data,
                'y': y_vals,
                'y_err': sem_vals,
            },
            'der': {
                'name': name,
                'color': color,
                'x_smooth': x_smooth,
                'y_smooth': y_smooth
            }
        }

    # Block 1: NT (Top Left)
    datasets.append(process_data_block(2, 10, 0, 1, 10, "NT", '#0000AA'))

    # Block 2: SR142948A (Top Right)
    datasets.append(process_data_block(2, 10, 11, 12, 21, "SR142948A", '#AA00AA'))

    # Block 3: SBI-553 (Bottom Left)
    datasets.append(process_data_block(14, 21, 0, 1, 10, "SBI-553", '#FF9900'))

    # Block 4: PD149163 (Bottom Right)
    datasets.append(process_data_block(14, 25, 11, 12, 21, "PD149163", '#44AA77'))

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
        
    output_path = os.path.join(output_dir, "59.json")
    
    with open(output_path, "w") as f:
        json.dump(output_json, f, indent=4)
        
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    compute_data()
