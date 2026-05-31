import sys
import io
import pandas as pd
import numpy as np
from scipy import stats
import json
import os

def process_data(output_filename):
    # ---------------------------------------------------------
    # 1. Source Data Embedding
    # ---------------------------------------------------------
    csv_content = """Model,Task Category,AUROC,k_WSIs,k_Patients,k_Sites
bioptimus,Morphology,0.7467894276890517,500,333,nan
ctranspath,Morphology,0.7245662906836026,32,13,25
hibou,Morphology,0.7273914889097874,nan,nan,nan
phikon,Morphology,0.6986905923455256,6,5.6,13
prov-gigapath,Morphology,0.7242330131938731,171,30,31
uni,Morphology,0.7351347723197759,100,nan,20
virchow-class,Morphology,0.7300469326931298,1488,120,17
hibou-l,Morphology,0.7297320720088225,1139,306,nan
virchow2-class,Morphology,0.762773096016989,3135,225,175
panakeia,Morphology,0.7306335682076608,6,nan,2
kaiko,Morphology,0.7073485188270819,29,11,25
dinosslpath,Morphology,0.764276572755652,37,nan,nan
bioptimus,Biomarker,0.7046859564606631,500,333,nan
ctranspath,Biomarker,0.6865689130621666,32,13,25
hibou,Biomarker,0.6840318931145523,nan,nan,nan
phikon,Biomarker,0.6655231079066909,6,5.6,13
prov-gigapath,Biomarker,0.7222276213474471,171,30,31
uni,Biomarker,0.7120236484959361,100,nan,20
virchow-class,Biomarker,0.6850684143619094,1488,120,17
hibou-l,Biomarker,0.6854885628643554,1139,306,nan
virchow2-class,Biomarker,0.732159659734404,3135,225,175
panakeia,Biomarker,0.706014841052465,6,nan,2
kaiko,Biomarker,0.6807236915312719,29,11,25
dinosslpath,Biomarker,0.7020635797745987,37,nan,nan
bioptimus,Prognosis,0.5857513036006027,500,333,nan
ctranspath,Prognosis,0.5770248615268212,32,13,25
hibou,Prognosis,0.5700799404528647,nan,nan,nan
phikon,Prognosis,0.5897553541124554,6,5.6,13
prov-gigapath,Prognosis,0.5871979448905298,171,30,31
uni,Prognosis,0.5721758498408054,100,nan,20
virchow-class,Prognosis,0.5873006733060928,1488,120,17
hibou-l,Prognosis,0.5754285617170372,1139,306,nan
virchow2-class,Prognosis,0.6065370877164761,3135,225,175
panakeia,Prognosis,0.5866993918324305,6,nan,2
kaiko,Prognosis,0.5543899668068984,29,11,25
dinosslpath,Prognosis,0.602773354053987,37,nan,nan
"""
    
    # ---------------------------------------------------------
    # 2. Data Processing
    # ---------------------------------------------------------
    df = pd.read_csv(io.StringIO(csv_content))
    
    # Filter for the categories present in the chart
    target_categories = ['Morphology', 'Biomarker', 'Prognosis']
    df = df[df['Task Category'].isin(target_categories)]
    
    # The X-axis is "Pretraining Dataset (k Anatomic Tissue Sites)"
    # We must drop rows where this value is NaN to plot them
    df_plot = df.dropna(subset=['k_Sites']).copy()
    
    # Ensure numeric types
    df_plot['k_Sites'] = pd.to_numeric(df_plot['k_Sites'])
    df_plot['AUROC'] = pd.to_numeric(df_plot['AUROC'])

    # Calculate stats
    stats_list = []
    for category in target_categories:
        subset = df_plot[df_plot['Task Category'] == category]
        corr_df = subset[['k_Sites', 'AUROC']].dropna()
        if len(corr_df) > 1:
            r_val, p_val = stats.pearsonr(corr_df['k_Sites'], corr_df['AUROC'])
        else:
            r_val, p_val = None, None
            
        stats_list.append({
            "category": category,
            "r": r_val,
            "p": p_val
        })
        
    # Prepare output
    output_data = {
        "scr_data": {
            "plot_data": df_plot.to_dict(orient='records')
        },
        "der_data": {
            "stats_data": stats_list
        }
    }
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
        
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_2_output/22.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
        
    process_data(output_file)
