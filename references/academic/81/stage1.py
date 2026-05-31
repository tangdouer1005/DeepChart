import pandas as pd
import io
import json
import os

def process_data(output_filename='bench/ground_truth_code/nature_2_output/81.json'):
    # 1. Load Data
    csv_data = """Station,PM_size,Site_type,N_samples,OP_AA_m_mean,OP_AA_m_SD,PM_mass_mean,PM_mass_SD
nan,nan,nan,nan,nmol min-1 µg-1,nmol min-1 µg-1,µg m-3,µg m-3
BERN,PM10,Traffic,738,0.2,0.04,19.42,10.22
BERN,PM2.5,Traffic,644,0.11,0.03,12.61,7.52
ZURICH,PM10,Urban,204,0.12,0.05,18.38,12.57
ZURICH,PM2.5,Urban,90,0.08,0.04,10.8,6.97
BCN,PM1,Urban,94,0.05,0.03,14.71,4.91
BCN,PM10,Urban,270,0.07,0.03,23.31,8.94
BCN,PM2.5,Urban,197,0.05,0.03,17.48,6.32
MRS-lcp,PM1,Urban,262,0.08,0.07,13.65,13.48
MRS-lcp,PM10,Urban,271,0.06,0.04,18.69,8.2
PARIS-lcpp,PM10,Urban,184,0.08,0.04,19.4,9.26
PARIS-lcpp,PM2.5,Urban,69,0.06,0.04,12.51,7.26
PARIS-lh,PM10,Urban,386,0.07,0.04,20.74,13.22
PARIS-lh,PM2.5,Urban,807,0.07,0.04,10.32,6.06
ATH,PM10,Urban,147,0.06,0.05,31.99,14.89
ATH,PM2.5,Urban,152,0.08,0.05,24.7,16.61
KRAK,PM1,Urban,63,0.04,0.02,19.73,17.28
KRAK,PM10,Urban,63,0.05,0.01,28.69,18.9
BASEL,PM10,Suburban,90,0.09,0.05,13.97,9.26
BASEL,PM2.5,Suburban,90,0.06,0.05,10.6,7.76
MGD,PM10,Rural,240,0.1,0.06,16.7,10.6
MGD,PM2.5,Rural,153,0.09,0.07,10.61,7.2
PAYRN,PM10,Rural,103,0.06,0.03,13.49,8.31
PAYRN,PM2.5,Rural,102,0.04,0.03,9.68,6.73
MSY,PM1,Rural,93,0.04,0.04,9.35,4.39
MSY,PM10,Rural,106,0.04,0.03,12.82,6.24
MSY,PM2.5,Rural,107,0.05,0.06,9.62,4.68
OPE,PM10,Rural,200,0.05,0.06,9.54,6.54
OPE,PM2.5,Rural,102,0.03,0.02,9,7.23"""

    # Read CSV, skipping the unit row (row index 1 in 0-based, or just filter after)
    df = pd.read_csv(io.StringIO(csv_data))
    
    df_raw = df.copy()
    
    # Remove the unit row (where Station is NaN)
    df = df.dropna(subset=['Station'])
    
    # Convert numeric columns
    numeric_cols = ['N_samples', 'OP_AA_m_mean', 'OP_AA_m_SD', 'PM_mass_mean', 'PM_mass_SD']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col])
        
    return df_raw, df

if __name__ == "__main__":
    raw_df, processed_df = process_data()
    
    final_output = {
        "scr_data": raw_df.to_dict(orient='records'),
        "der_data": processed_df.to_dict(orient='records')
    }
    
    output_filename = 'bench/ground_truth_code/nature_1_output/81.json'
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    with open(output_filename, 'w') as f:
        json.dump(final_output, f, indent=4)
    print(f"Data saved to {output_filename}")