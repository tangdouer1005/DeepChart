import sys
import io
import pandas as pd
import numpy as np
import json

def main():
    # 1. Data Ingestion
    # We will parse the provided markdown-style data. 
    # Since the data is in three distinct blocks separated by 'nan' rows/headers, 
    # we will process them as three separate CSV-like strings.

    # Block 1: Main properties
    data_main_str = """Electrolyte|SSL ratio (%)|Li+ binding energy (eV)|Ionic conductivity (mS cm-1)|Initial interfacial resistance (Ohm)|SEI thickness (nm)|F ratio (%)|C ratio (%)|O ratio (%)|15th Rinterface (ohm)|15th overpotential (V)|Thickness of deposited Li (μm)|Cycle life
LiAsF6 electrolyte|90|-1.10496|0.346|88|9.8513|3.18|32.24|32.24|21.22|0.22|11.7|279
LiPF6 electrolyte|80|-1.11207|0.336|71|8.90335|7.99|38.74|22.7|9.5|0.17|12.3|115
LiFSI electrolyte|78.33333|-1.19801|0.344|47|10.2788|4.44|38.34|25.79|6.4|0.14|14.2|71
LiTFSI electrolyte|76.66667|-1.2481|0.322|52|9.10781|14.17|29.5|22.27|8|0.155|15.8|53
LiClO4 electrolyte|71.66667|-1.22465|0.28|35|8.86617|7.89|26.13|32.59|4.3|0.25|15.8|56
LiBF4 electrolyte|75|-1.20247|0.3|24|9.83271|9.65|27.63|23.13|30.1|0.22|16.1|38
LiDFOB electrolyte|70.4918|-1.36423|0.279|50|11.7379|7.07|32.83|29.61|6.6|0.16|14.9|45
LiNO3 electrolyte|68.33333|-1.40999|0.277|52|17.0074|7.47|33.73|24.44|4.54|0.18|17|30"""

    # Block 2: CCD measurements
    data_ccd_str = """Electrolyte|m1|m2
LiAsF6 electrolyte|36|36
LiPF6 electrolyte|32|28
LiFSI electrolyte|29|22
LiTFSI electrolyte|20|18
LiClO4 electrolyte|26|23
LiBF4 electrolyte|21|17
LiDFOB electrolyte|20|16
LiNO3 electrolyte|15|15"""

    # Block 3: Crystallite size measurements
    data_cryst_str = """Electrolyte|m1|m2|m3|m4
LiAsF6 electrolyte|2.9|2.6|2.6|2.7
LiPF6 electrolyte|3|3.3|2.8|3.3
LiFSI electrolyte|3.2|3.1|3.3|3
LiTFSI electrolyte|3.9|3.4|3|3.7
LiClO4 electrolyte|4.1|4.8|4.2|3.8
LiBF4 electrolyte|3.9|4.1|5.4|4.4
LiDFOB electrolyte|4.7|4.5|4.9|5.4
LiNO3 electrolyte|5.2|5.2|6.2|5.3"""

    # Parse DataFrames
    df_main = pd.read_csv(io.StringIO(data_main_str), sep='|')
    df_ccd_raw = pd.read_csv(io.StringIO(data_ccd_str), sep='|')
    df_cryst_raw = pd.read_csv(io.StringIO(data_cryst_str), sep='|')

    # 2. Data Processing
    # Calculate means for CCD and Crystallite size
    # Note: We assume the order of electrolytes is identical across tables (which it is in the source).
    
    # CCD Mean
    df_ccd_raw['J_crit'] = df_ccd_raw[['m1', 'm2']].mean(axis=1)
    
    # Crystallite Mean
    df_cryst_raw['Crystallite size'] = df_cryst_raw[['m1', 'm2', 'm3', 'm4']].mean(axis=1)

    # Merge into a single dataframe
    # We can just assign columns because the rows are aligned by Electrolyte
    df_final = df_main.copy()
    df_final['J_crit'] = df_ccd_raw['J_crit']
    df_final['Crystallite size'] = df_cryst_raw['Crystallite size']

    # 3. Prepare for Correlation
    # Map columns to the specific order and names required for the plot
    col_mapping = {
        'SSL ratio (%)': 'SSL ratio',
        'Li+ binding energy (eV)': 'Eb',
        'Ionic conductivity (mS cm-1)': 'sigma_ion',
        'Initial interfacial resistance (Ohm)': 'Initial R_interface',
        'SEI thickness (nm)': 'SEI thickness',
        'F ratio (%)': 'F%',
        'C ratio (%)': 'C%',
        'O ratio (%)': 'O%',
        '15th Rinterface (ohm)': 'R_interface',
        '15th overpotential (V)': 'eta_15th',
        'J_crit': 'J_crit',
        'Crystallite size': 'Crystallite size',
        'Thickness of deposited Li (μm)': 'Thickness',
        'Cycle life': 'Cycle performance'
    }

    # Select and rename columns
    df_corr_input = df_final[list(col_mapping.keys())].rename(columns=col_mapping)

    # Calculate Spearman Correlation
    corr_matrix = df_corr_input.corr(method='spearman')

    # Save to JSON
    # We save the correlation matrix as JSON. Pandas to_json handles indices.
    output_path = "bench/ground_truth_code/nature_1_output/34.json"
    
    # Convert correlation matrix to dictionary/json structure
    # Using 'split' orientation to preserve index and columns clearly, or just default
    # 'split' gives: {"index": [...], "columns": [...], "data": [[...]]}
    # This is easy to reconstruct into a DataFrame.

    scr_data = {
        "main_properties": df_main.to_dict(orient='records'),
        "ccd_measurements": df_ccd_raw.to_dict(orient='records'),
        "crystallite_size_measurements": df_cryst_raw.to_dict(orient='records')
    }

    der_data = {
        "calculated_means": {
            "J_crit": df_final[['Electrolyte', 'J_crit']].to_dict(orient='records'),
            "Crystallite size": df_final[['Electrolyte', 'Crystallite size']].to_dict(orient='records')
        },
        "spearman_correlation": corr_matrix.to_dict(orient='split')
    }
    
    output_json = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    with open(output_path, 'w') as f:
        json.dump(output_json, f, indent=4)
        
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    main()
