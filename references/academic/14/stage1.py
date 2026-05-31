import sys
import io
import pandas as pd
import numpy as np
import json

def compute_data(output_path):
    # 1. Load Source Data
    csv_data = """Task|CONCH|Virchow2|ProvGigaPath|DinoSSLPath
KIEL_STAD_M_STATUS|0.544224|0.526274|0.534376|0.506792
DACHS_CRC_KRAS|0.534721|0.547883|0.5362|0.533338
IEO_BRCA_N_STATUS|0.575481|0.55847|0.549081|0.573873
CPTAC_LUAD_KRAS|0.581757|0.522889|0.552111|0.540034
CPTAC_CRC_Sidedness|0.613278|0.583832|0.571655|0.60289
CPTAC_CRC_N_STATUS|0.630026|0.615013|0.616402|0.594841
CPTAC_CRC_PIK3CA|0.617665|0.636782|0.619964|0.602783
DACHS_CRC_N_STATUS|0.648021|0.632989|0.622209|0.62096
KIEL_STAD_N_STATUS|0.631522|0.616924|0.657943|0.632616
CPTAC_CRC_KRAS|0.674286|0.613441|0.628008|0.637022
CPTAC_BRCA_PIK3CA|0.675417|0.610655|0.626444|0.633569
CPTAC_BRCA_ERBB2|0.688275|0.66186|0.562938|0.620216
DACHS_CRC_M_STATUS|0.675269|0.697332|0.63174|0.662344
DACHS_CRC_CIMP|0.671484|0.698943|0.692594|0.65021
BERN_STAD_N_STATUS|0.71867|0.598758|0.498635|0.627987
BERN_STAD_LAUREN|0.720555|0.729027|0.644662|0.705261
DACHS_CRC_Sidedness|0.707539|0.723064|0.706909|0.736509
DACHS_CRC_BRAF|0.708614|0.725489|0.741302|0.649243
CPTAC_CRC_BRAF|0.708571|0.724835|0.763956|0.753407
CPTAC_LUAD_STK11|0.727652|0.766667|0.748611|0.737374
CPTAC_LUAD_EGFR|0.711846|0.701634|0.769281|0.718056
CPTAC_LUAD_TP53|0.781961|0.752157|0.732478|0.719857
BERN_STAD_MSI|0.738697|0.795687|0.790903|0.685307
KIEL_STAD_LAUREN|0.795917|0.794557|0.711356|0.806003
CPTAC_BRCA_PGR|0.800114|0.796057|0.779371|0.806571
KIEL_STAD_MSI|0.731109|0.813374|0.778738|0.677917
DACHS_CRC_MSI|0.828881|0.862416|0.816061|0.833579
KIEL_STAD_EBV|0.87855|0.862767|0.877741|0.837932
CPTAC_BRCA_ESR1|0.820932|0.894659|0.817351|0.852485
CPTAC_CRC_MSI|0.916667|0.92284|0.888272|0.850309
NSCLC_Subtyping|0.99268|0.983386|0.986583|0.97072"""

    df = pd.read_csv(io.StringIO(csv_data), sep='|')
    models = ['CONCH', 'Virchow2', 'ProvGigaPath', 'DinoSSLPath']

    # 2. Logic to determine Scale per Axis
    FIXED_STEP = 0.06
    
    df['data_max'] = df[models].max(axis=1)
    
    axis_tops = []
    axis_bottoms = []
    
    for idx, row in df.iterrows():
        dmax = row['data_max']
        top = dmax
        bottom = top - (4 * FIXED_STEP)
        axis_tops.append(top)
        axis_bottoms.append(bottom)
        
    df['axis_top'] = axis_tops
    df['axis_bottom'] = axis_bottoms 

    def get_category(task_name):
        task_upper = task_name.upper()
        if 'N_STATUS' in task_upper or 'M_STATUS' in task_upper:
            return 'Prognosis'
        if 'SUBTYPING' in task_upper or 'SIDEDNESS' in task_upper or 'LAUREN' in task_upper:
            return 'Morphology'
        return 'Biomarkers'

    df['category'] = df['Task'].apply(get_category)
    
    # Keep a copy of raw data for scr_data
    # Re-read or just drop columns? The original df read had only Task + models.
    # So we can reconstruct raw columns.
    raw_cols = ['Task'] + models
    df_raw = df[raw_cols]

    # Convert to JSON
    # scr_data: raw input
    # der_data: all processed info including calculated limits and categories
    output_data = {
        "scr_data": {
            "data": df_raw.to_dict(orient='records')
        },
        "der_data": {
            "models": models,
            "processed_data": df.to_dict(orient='records')
        }
    }

    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_2_output/14.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compute_data(output_file)
