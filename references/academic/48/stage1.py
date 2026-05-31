import sys
import io
import pandas as pd
import json
import os

def compute_data(output_json_path):
    # 1. Source Data Loading
    # Using the exact data provided in the prompt
    csv_data = """
GO term|piggybac_abs_log10_q_value|human_abs_log10_q_value|sum_abs_log10_q_value|piggybac_marker_size_binned_q|human_marker_size_binned_q|total_marker_size_binned_q
synaptic membrane|10.9683220431953|27.1999010137671|38.1682230569625|40|80|80
postsynapse|13.5690029560099|11.9859107281264|25.5549136841363|40|40|80
neuron differentiation|15.4613873832848|8.00296758756651|23.4643549708513|40|20|80
biological adhesion|8.67189690613437|14.2766853763774|22.9485822825118|20|40|80
neuron to neuron synapse|13.985186921544|7.62842695455214|21.6136138760962|40|20|80
glutamatergic synapse|10.2438761964056|10.0243580040108|20.2682342004164|40|40|80
gated channel activity|1.38980943250208|16.9962913940332|18.3861008265352|10|40|40
regulation of membrane potential|5.61355344651853|12.4308863597106|18.0444398062292|20|40|40
ion channel complex|3.46667759619904|14.3980727256377|17.8647503218367|20|40|40
synapse organization|10.342692521706|6.89491987055633|17.2376123922624|40|20|40
trans-synaptic signaling|3.53762865997199|13.6838452055278|17.2214738654998|20|40|40
modulation of chemical synaptic transmission|6.7627162380012|9.66651296264769|16.4292292006489|20|20|40
cell morphogenesis|11.4391738590977|4.6716762136979|16.1108500727957|40|20|40
regulation of ion transmembrane transport|5.40342991222435|8.93170096109507|14.3351308733194|20|20|40
cell part morphogenesis|10.5347125889337|3.60180433795327|14.136516926887|40|20|40
regulation of nervous system development|8.83646274468904|5.17551645632876|14.0119792010178|20|20|40
central nervous system development|8.83646274468904|4.61984120461526|13.4563039493043|20|20|40
somatodendritic compartment|8.83646274468904|4.32490960269357|13.1613723473826|20|20|40
glutamate receptor activity|3.76126695799075|8.72002068201322|12.481287640004|20|20|40
regulation of synapse structure or activity|6.42566939091866|5.79263196486851|12.2183013557872|20|20|40
"""
    
    # Parse data
    df = pd.read_csv(io.StringIO(csv_data), sep="|")
    
    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Clean string data (remove whitespace)
    df['GO term'] = df['GO term'].str.strip()

    # 2. Data Preparation & Formatting
    # Map raw data labels to the specific formatting seen in the image
    # (Capitalization, abbreviations like "Reg.", spelling adjustments)
    def format_label(label):
        label = label.capitalize() # Start with sentence case
        
        # Specific replacements based on visual inspection of the target chart
        replacements = {
            "Regulation of": "Reg. of",
            "Modulation of": "Mod. of",
            "Neuron to neuron": "Neuron-to-neuron",
            "Trans-synaptic signaling": "Transsynaptic signalling" # Note spelling change in chart
        }
        
        for old, new in replacements.items():
            if label.startswith(old) or old in label:
                label = label.replace(old, new)
        
        return label

    df['display_label'] = df['GO term'].apply(format_label)
    
    # Reverse dataframe to plot top-to-bottom (matplotlib plots index 0 at bottom by default)
    df = df.iloc[::-1].reset_index(drop=True)

    # Save to JSON
    scr_data = df.drop(columns=['display_label']).to_dict(orient='records')
    der_data = df[['GO term', 'display_label']].to_dict(orient='records')

    output_json = {
        "scr_data": scr_data,
        "der_data": der_data
    }

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

    with open(output_json_path, 'w') as f:
        json.dump(output_json, f, indent=4)
    print(f"Data saved to {output_json_path}")

if __name__ == "__main__":
    output_json = "bench/ground_truth_code/nature_1_output/48.json"
    compute_data(output_json)
