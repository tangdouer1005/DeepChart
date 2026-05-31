import sys
import io
import pandas as pd
import numpy as np
import json
from scipy import stats

def process_data(output_filename):
    # 1. Source Data
    csv_data = """service_type|state|fairnes_index|number_HighAging_CBG
Health Care Services|AZ|0.0413625|274
Health Care Services|CA|-0.075969|215
Health Care Services|FL|0.146886|851
Health Care Services|IL|0.423423|37
Health Care Services|MD|0.311111|40
Health Care Services|MA|-0.105105|37
Health Care Services|MI|0.00740741|30
Health Care Services|NV|0.255556|40
Health Care Services|NJ|-0.266055|109
Health Care Services|NY|0.0896921|83
Health Care Services|OH|0.160494|36
Health Care Services|PA|0.106667|50
Health Care Services|SC|-0.045045|37
Health Care Services|TX|-0.100529|63
Health Care Services|VA|0.117845|33
Health Care Services|WA|0.247312|31
Grocery and Food Supply|AZ|-0.0841503|272
Grocery and Food Supply|CA|-0.167186|214
Grocery and Food Supply|FL|0.12178|854
Grocery and Food Supply|IL|0.141141|37
Grocery and Food Supply|MD|0.19883|38
Grocery and Food Supply|MA|-0.117284|36
Grocery and Food Supply|MI|-0.103704|30
Grocery and Food Supply|NV|-0.015873|42
Grocery and Food Supply|NJ|-0.323232|110
Grocery and Food Supply|NY|-0.259259|84
Grocery and Food Supply|NC|-0.25448|31
Grocery and Food Supply|OH|0.123457|36
Grocery and Food Supply|PA|-0.12854|51
Grocery and Food Supply|SC|0.00900901|37
Grocery and Food Supply|TX|-0.107584|63
Grocery and Food Supply|VA|0.0505051|33
Grocery and Food Supply|WA|0.139785|31
Housing and Real Estate|AZ|0.0178427|274
Housing and Real Estate|CA|-0.00253678|219
Housing and Real Estate|FL|0.142783|856
Housing and Real Estate|IL|0.171171|37
Housing and Real Estate|MD|0.138889|40
Housing and Real Estate|MA|-0.135135|37
Housing and Real Estate|NV|0.0757576|44
Housing and Real Estate|NJ|-0.232143|112
Housing and Real Estate|NY|0.0534979|81
Housing and Real Estate|OH|0.117284|36
Housing and Real Estate|PA|-0.0283224|51
Housing and Real Estate|SC|-0.0643275|38
Housing and Real Estate|TX|0.00529101|63
Housing and Real Estate|VA|0.030303|33
Housing and Real Estate|WA|0.194444|32"""

    # Load data
    df = pd.read_csv(io.StringIO(csv_data), sep='|')

    # 2. Data Preprocessing
    # Map full names to abbreviations used in the chart
    name_map = {
        'Health Care Services': 'HCS',
        'Grocery and Food Supply': 'GFS',
        'Housing and Real Estate': 'HRE'
    }
    df['service_type_abbr'] = df['service_type'].map(name_map)
    
    # Calculate P-values (Derived Data)
    g_hcs = df[df['service_type_abbr'] == 'HCS']['fairnes_index']
    g_gfs = df[df['service_type_abbr'] == 'GFS']['fairnes_index']
    g_hre = df[df['service_type_abbr'] == 'HRE']['fairnes_index']
    
    _, p1 = stats.ttest_ind(g_hcs, g_gfs, equal_var=False)
    _, p2 = stats.ttest_ind(g_gfs, g_hre, equal_var=False)
    _, p3 = stats.ttest_ind(g_hcs, g_hre, equal_var=False)

    p_values = {
        'p_hcs_gfs': p1,
        'p_gfs_hre': p2,
        'p_hcs_hre': p3
    }

    # Prepare final output structure
    output_data = {
        'scr_data': df.to_dict(orient='records'),
        'der_data': {
            'p_values': p_values
        }
    }

    # Save to JSON
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "bench/ground_truth_code/nature_1_output/144.json"
    process_data(output_file)
