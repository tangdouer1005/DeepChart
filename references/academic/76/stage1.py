import sys
import io
import numpy as np
import pandas as pd
import json
from scipy import stats
from statsmodels.stats.multicomp import MultiComparison

def process_and_save_data(output_filename='bench/ground_truth_code/nature_2_output/76.json'):
    # 1. Data Loading and Processing
    csv_data = """
Unnamed: 0|Unnamed: 1|Unnamed: 2|Unnamed: 3|Unnamed: 4|Unnamed: 5|Unnamed: 6|Unnamed: 7|Unnamed: 8|Unnamed: 9|Unnamed: 10|Unnamed: 11|Unnamed: 12|Unnamed: 13|Unnamed: 14|Unnamed: 15|Unnamed: 16|Unnamed: 17|Unnamed: 18|Unnamed: 19|Unnamed: 20|Unnamed: 21|Unnamed: 22|Unnamed: 23|Unnamed: 24|Unnamed: 25|Unnamed: 26|Unnamed: 27|Unnamed: 28|Unnamed: 29|Unnamed: 30|Unnamed: 31|Unnamed: 32|Unnamed: 33
nan|NT|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|SBI-553|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan
Gq|18.561974|20.5304|21.8859|25.4265|24.8291|20.4485649|20.2525|18.8986|18.5964|19.2369|22.3496|nan|26.1478|21.3146|18.8325|0|nan|nan|0|0|0|0|0|0|0|nan|nan|nan|0|nan|0|5.85292|4.06629
G14|22.4859068|13.1417|20.7836|21.5074|12.7223|14.8950184|21.2973|11.0167|20.0157|20.1997|14.0096|12.3474|nan|nan|nan|8.36146599|5.24927|10.5955|2.92653|0|0.982024|6.3174|5.42314|9.3953|2.71189338|0|0|nan|nan|nan|nan|nan|nan
G15|2.83892413|18.5284|nan|17.208|17.5503|15.649259|14.2055|15.8142|15.7078|5.02659|20.2398|18.5566|16.3465|16.4657|14.7335|12.430777|nan|nan|0|0|0|0|0|0|22.1019669*|0|nan|nan|2.83248|nan|nan|nan|nan
Gi1/2|17.3927901|18.0613|nan|23.4823|22.5571|21.3372179|20.5129|18.8441|18.3129|16.9856|25.0649|25.0652|24.0523|21.7356|17.7672|4.22817524|nan|nan|1.54981|0|2.8971|1.80358|4.40053|5.93329|nan|nan|0.747585|3.7713|nan|6.75973|nan|nan|nan
Gi3|19.0917432|10.0348|16.7753|14.4272|15.9897|12.8235221|19.7727|11.6037|17.7305|15.6435|14.911|12.4173|nan|nan|nan|16.4750053|9.89639|10.8542|5.87834|3.54193606|5.2972|13.3745|10.7178|9.5537|4.91039296|2.51106|5.376|nan|nan|nan|nan|nan|nan
Go|18.9911805|11.7554|15.4463|14.0694|11.8039|8.39655288|18.9416|12.5947|14.3461|14.1207|12.0699|9.89944|nan|nan|nan|11.3366068|9.02009|12.4783|4.81096|2.83418012|4.8773|13.6896|9.43665|13.0261|3.40032889|2.04381|3.77529|nan|nan|nan|nan|nan|nan
Gz|4.98714811|1.37944|19.0384|4.16548|3.21537|0*|3.11607|1.51332|16.5858|3.97033|3.90115|0.0470616|nan|nan|nan|6.15869732|3.51337|15.6124|0|0|1.36561|3.53711|1.42626|13.8869|0|0.445876|0.134207|nan|nan|nan|nan|nan|nan
Gs|17.8064697|19.0933|nan|19.1808|20.7042|19.4019457|19.1168|17.8993|16.2448|18.6427|19.9202|20.6831|21.3034|19.017|16.5337|0|nan|nan|0|0|0|nan|0|1.42575|0|nan|nan|nan|0|nan|1.64149|nan|nan
Golf|17.5269014|9.27352|10.5943|8.13406|7.30447|5.58784443|17.8185|12.4501|10.9083|8.35866|6.68454|6.75767|nan|nan|nan|1.58662873|4.2992|0|0|0|1.34441|3.09422|4.98111|0|0|0|0.0509099|nan|nan|nan|nan|nan|nan
G12|17.1057999|14.0341|20.8579|14.1236|6.59239|9.23437164|18.0802|12.203|20.0663|14.0206|7.11188|9.81983|nan|nan|nan|13.857742|12.189|16.4884|3.8255|0|5.71622|20.258|12.5584|19.2429|6.01763134|0|5.65288|nan|nan|nan|nan|nan|nan
G13|19.6846994|11.214|20.2793|12.9065|10.8931|10.5753117|19.9887|11.964|19.9644|12.8544|11.4575|9.35151|nan|nan|nan|10.8094523|11.4574|15.8762|0.881903|0.48739349*|4.30331|14.9154|11.382|13.9409|2.20009171|4.73532|5.22393|nan|nan|nan|nan|nan|nan
GΔC|1.24566758|0.711698|nan|0.904109|0.748529|0.42162346|0|0.482407|nan|2.32307|0.693716|0.770289|nan|nan|nan|1.43637466|1.17791|nan|0|0|0|0.410506|2.23129|nan|0|0|0|nan|nan|nan|nan|nan|nan
"""

    def clean_value(val):
        if pd.isna(val):
            return np.nan
        s = str(val).replace('*', '').strip()
        try:
            return float(s)
        except ValueError:
            return np.nan

    # Read CSV
    df_raw = pd.read_csv(io.StringIO(csv_data), sep='|', header=None)

    # Extract G-Protein names (Column 0, skipping first two header rows)
    g_proteins = df_raw.iloc[2:, 0].values

    # Extract Data
    # NT: Columns 1 to 15 (indices 1 to 15)
    # SBI: Columns 16 to 33 (indices 16 to 33)
    nt_data_raw = df_raw.iloc[2:, 1:16]
    sbi_data_raw = df_raw.iloc[2:, 16:34]

    # Clean data (remove asterisks, convert to float)
    nt_data = nt_data_raw.applymap(clean_value)
    sbi_data = sbi_data_raw.applymap(clean_value)
    
    # Get GDeltaC data (Control)
    g_ctrl_idx = np.where(g_proteins == 'GΔC')[0][0]
    nt_ctrl = nt_data.iloc[g_ctrl_idx].dropna().values
    sbi_ctrl = sbi_data.iloc[g_ctrl_idx].dropna().values
    
    ctrl_data_combined = np.concatenate([nt_ctrl, sbi_ctrl])
    
    output_data = {}
    
    for i, protein in enumerate(g_proteins):
        nt_vals = nt_data.iloc[i].dropna().values
        sbi_vals = sbi_data.iloc[i].dropna().values
        
        # Calculate Stats
        # NT vs Control
        # SBI vs Control
        # NT vs SBI
        
        # Use statsmodels allpairtest with bonferroni
        data_combined = np.concatenate([ctrl_data_combined, nt_vals, sbi_vals])
        groups = ['Control'] * len(ctrl_data_combined) + ['NT'] * len(nt_vals) + ['SBI'] * len(sbi_vals)
        
        p_nt_vs_ctrl = 1.0
        p_sbi_vs_ctrl = 1.0
        p_nt_vs_sbi = 1.0
        
        try:
            mc = MultiComparison(data_combined, groups)
            res = mc.allpairtest(stats.ttest_ind, method='bonf')[0]
            
            for row in res.data[1:]:
                g1, g2, _, _, p_corr, _ = row
                p_corr = float(p_corr)
                
                if (g1 == 'Control' and g2 == 'NT') or (g2 == 'Control' and g1 == 'NT'):
                    p_nt_vs_ctrl = p_corr
                elif (g1 == 'Control' and g2 == 'SBI') or (g2 == 'Control' and g1 == 'SBI'):
                    p_sbi_vs_ctrl = p_corr
                elif (g1 == 'NT' and g2 == 'SBI') or (g2 == 'NT' and g1 == 'SBI'):
                    p_nt_vs_sbi = p_corr
        except Exception:
            # Fallback if too few samples
            pass
            
        output_data[protein] = {
            'nt_values': nt_vals.tolist(),
            'sbi_values': sbi_vals.tolist(),
            'p_nt_vs_ctrl': p_nt_vs_ctrl,
            'p_sbi_vs_ctrl': p_sbi_vs_ctrl,
            'p_nt_vs_sbi': p_nt_vs_sbi
        }
        
    output = {
        'control_mean': float(np.mean(ctrl_data_combined)),
        'data': output_data,
        'proteins': g_proteins.tolist()
    }

    return df_raw, output

if __name__ == "__main__":
    df_raw, processed_data = process_and_save_data()
    
    final_output = {
        "scr_data": df_raw.to_dict(orient='records'),
        "der_data": processed_data
    }
    
    with open('bench/ground_truth_code/nature_1_output/76.json', 'w') as f:
        json.dump(final_output, f, indent=4)
