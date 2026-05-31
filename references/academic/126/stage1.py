import sys
import io
import pandas as pd
import json
import os

def compute_data(output_filename):
    csv_data = """
Unnamed: 0|GHGs|EDGAR_Sector|FOOD_system_stage|FOOD_system_stage_detailed|FOOD_system_compartment|flux|freq|GHG2
1|CH4|Agriculture|Production|Production|Landbased|988974|0.0764956|CH4
2|CH4|Chemicals|Distribution|Packaging|Industry|5.12562|3.96459e-07|CH4
3|CH4|Ener for agr. fishing|Production|Production|Energy|24530.7|0.00189741|CH4
4|CH4|Ener for agric. fishing|Consumption|Consumption|Energy|55.0091|4.25486e-06|CH4
5|CH4|Ener for aluminium,paper,glass|Production|Production|Energy|1.1112|8.59497e-08|CH4
6|CH4|Ener for household|Production|Production|Energy|109.451|8.46588e-06|CH4
7|CH4|Ener for households|Consumption|Consumption|Energy|18178.3|0.00140606|CH4
8|CH4|Ener for packaging|Distribution|Packaging|Energy|53635.7|0.00414864|CH4
9|CH4|Ener for production|Processing|Processing|Energy|38328.2|0.00296463|CH4
10|CH4|Ener for retail|Distribution|Retail|Energy|7879.48|0.000609465|CH4
11|CH4|Ener for transport|Distribution|Transport|Energy|40641.9|0.00314359|CH4
12|CH4|Enteric Ferment|Production|Production|Landbased|2.13959e+06|0.165494|CH4
13|CH4|Industrial|Distribution|Packaging|Energy|1464.94|0.000113311|CH4
14|CH4|Industrial|Processing|Processing|Energy|1395.4|0.000107932|CH4
15|CH4|LULUC|Production|LULUC|Landbased|20031.3|0.00154939|CH4
16|CH4|Manure|Production|Production|Landbased|148073|0.0114532|CH4
17|CH4|Residential|Consumption|Consumption|Energy|50505.6|0.00390653|CH4
18|CH4|Residential|Distribution|Retail|Energy|904.397|6.99537e-05|CH4
19|CH4|Residential|Production|Production|Energy|7595.75|0.00058752|CH4
20|CH4|Road Transport|Distribution|Transport|Energy|1264.39|9.77989e-05|CH4
21|CH4|Solid waste|End of Life|End of Life|Waste|358516|0.0277306|CH4
22|CH4|Transport|Distribution|Transport|Energy|24.7084|1.91116e-06|CH4
23|CH4|Waste burning|Production|Production|Landbased|44653|0.00345384|CH4
24|CH4|Waste water|End of Life|End of Life|Waste|754862|0.0583874|CH4
25|CH4|Waste water|Processing|Processing|Waste|74213.7|0.00574031|CH4
26|CO2|Agriculture|Production|Production|Landbased|71232.1|0.00550969|CO2
27|CO2|Chemicals|Distribution|Packaging|Industry|158.323|1.22461e-05|CO2
28|CO2|Chemicals|Production|Production|Industry|146385|0.0113226|CO2
29|CO2|Ener for agr. fishing|Production|Production|Energy|15173.2|0.00117362|CO2
30|CO2|Ener for agric. fishing|Consumption|Consumption|Energy|59469.3|0.00459985|CO2
31|CO2|Ener for aluminium,paper,glass|Production|Production|Energy|1287.49|9.95856e-05|CO2
32|CO2|Ener for household|Production|Production|Energy|140174|0.0108423|CO2
33|CO2|Ener for households|Consumption|Consumption|Energy|11279.4|0.000872446|CO2
34|CO2|Ener for packaging|Distribution|Packaging|Energy|34532|0.00267099|CO2
35|CO2|Ener for production|Processing|Processing|Energy|100855|0.00780097|CO2
36|CO2|Ener for retail|Distribution|Retail|Energy|38193.9|0.00295424|CO2
37|CO2|Ener for transport|Distribution|Transport|Energy|24225.2|0.00187378|CO2
38|CO2|Industrial|Distribution|Packaging|Energy|481018|0.037206|CO2
39|CO2|Industrial|Processing|Processing|Energy|127370|0.0098519|CO2
40|CO2|Iron Steel|Distribution|Packaging|Industry|344.997|2.6685e-05|CO2
41|CO2|LULUC|Production|LULUC|Landbased|4.99379e+06|0.386262|CO2
42|CO2|Non-Ferrous|Distribution|Packaging|Industry|5970.96|0.000461844|CO2
43|CO2|Non-metallic|Distribution|Packaging|Industry|4033.58|0.000311991|CO2
44|CO2|Residential|Consumption|Consumption|Energy|154493|0.0119498|CO2
45|CO2|Residential|Distribution|Retail|Energy|53996.1|0.00417651|CO2
46|CO2|Residential|Production|Production|Energy|236342|0.0182807|CO2
47|CO2|Road Transport|Distribution|Transport|Energy|271497|0.0209999|CO2
48|CO2|Solid waste|End of Life|End of Life|Waste|1180.78|9.13318e-05|CO2
49|CO2|Solvents|Production|Production|Industry|3833.77|0.000296536|CO2
50|CO2|Transport|Distribution|Transport|Energy|12823|0.000991843|CO2
52|N2O|Agriculture|Production|Production|Landbased|833296|0.0644541|N2O
53|N2O|Chemicals|Distribution|Packaging|Industry|1.78121|1.37774e-07|N2O
54|N2O|Chemicals|Production|Production|Industry|7528.54|0.000582321|N2O
55|N2O|Ener for agr. fishing|Production|Production|Energy|43.0308|3.32836e-06|N2O
56|N2O|Ener for agric. fishing|Consumption|Consumption|Energy|260.766|2.01698e-05|N2O
57|N2O|Ener for aluminium,paper,glass|Production|Production|Energy|6.59234|5.09907e-07|N2O
58|N2O|Ener for household|Production|Production|Energy|755.457|5.84334e-05|N2O
59|N2O|Ener for households|Consumption|Consumption|Energy|24.756|1.91484e-06|N2O
60|N2O|Ener for packaging|Distribution|Packaging|Energy|49.1047|3.79817e-06|N2O
61|N2O|Ener for production|Processing|Processing|Energy|523.679|4.05058e-05|N2O
62|N2O|Ener for retail|Distribution|Retail|Energy|166.493|1.28779e-05|N2O
63|N2O|Ener for transport|Distribution|Transport|Energy|78.226|6.05066e-06|N2O
64|N2O|Indirect emi|Consumption|Consumption|Energy|26740.2|0.00206831|N2O
65|N2O|Indirect emi|Processing|Processing|Industry|341.167|2.63887e-05|N2O
66|N2O|Indirect N2O|Production|Production|Landbased|131801|0.0101946|N2O
67|N2O|Industrial|Distribution|Packaging|Energy|2052.09|0.000158726|N2O
68|N2O|Industrial|Processing|Processing|Energy|2766.54|0.000213987|N2O
69|N2O|LULUC|Production|LULUC|Landbased|304.291|2.35364e-05|N2O
70|N2O|Manure|Production|Production|Landbased|53941.3|0.00417227|N2O
71|N2O|Residential|Consumption|Consumption|Energy|4913.5|0.000380052|N2O
72|N2O|Residential|Distribution|Retail|Energy|231.107|1.78758e-05|N2O
73|N2O|Residential|Production|Production|Energy|16849.1|0.00130325|N2O
74|N2O|Road Transport|Distribution|Transport|Energy|1990.73|0.00015398|N2O
75|N2O|Solid waste|End of Life|End of Life|Waste|201.257|1.55669e-05|N2O
76|N2O|Transport|Distribution|Transport|Energy|496.374|3.83937e-05|N2O
77|N2O|Waste burning|Production|Production|Landbased|10956.5|0.00084747|N2O
78|N2O|Waste water|End of Life|End of Life|Waste|53983.4|0.00417553|N2O
79|N2O|Waste water|Processing|Processing|Waste|13108|0.00101388|N2O
"""

    df = pd.read_csv(io.StringIO(csv_data), sep='|')
    df.columns = df.columns.str.strip()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.strip()
            
    flows = []
    
    # Group data to get unique paths and fluxes
    # Path: GHGs -> Compartment -> Stage -> Sector -> GHGs
    grouped = df.groupby(['GHGs', 'FOOD_system_compartment', 'FOOD_system_stage_detailed', 'EDGAR_Sector'])['flux'].sum().reset_index()
    
    total_flux = grouped['flux'].sum()
    
    # Create links for each step
    # Step 1: GHGs -> Compartment
    s1 = grouped.groupby(['GHGs', 'FOOD_system_compartment'])['flux'].sum().reset_index()
    for _, r in s1.iterrows():
        flows.append({'source_col': 0, 'source': r['GHGs'], 'target_col': 1, 'target': r['FOOD_system_compartment'], 'value': r['flux'], 'color_key': r['GHGs']})
        
    # Step 2: Compartment -> Stage
    s2 = grouped.groupby(['FOOD_system_compartment', 'FOOD_system_stage_detailed'])['flux'].sum().reset_index()
    for _, r in s2.iterrows():
        flows.append({'source_col': 1, 'source': r['FOOD_system_compartment'], 'target_col': 2, 'target': r['FOOD_system_stage_detailed'], 'value': r['flux'], 'color_key': r['FOOD_system_compartment']})

    # Step 3: Stage -> Sector
    s3 = grouped.groupby(['FOOD_system_stage_detailed', 'EDGAR_Sector'])['flux'].sum().reset_index()
    for _, r in s3.iterrows():
        flows.append({'source_col': 2, 'source': r['FOOD_system_stage_detailed'], 'target_col': 3, 'target': r['EDGAR_Sector'], 'value': r['flux'], 'color_key': r['FOOD_system_stage_detailed']})

    # Step 4: Sector -> GHGs
    s4 = grouped.groupby(['EDGAR_Sector', 'GHGs'])['flux'].sum().reset_index()
    for _, r in s4.iterrows():
        flows.append({'source_col': 3, 'source': r['EDGAR_Sector'], 'target_col': 4, 'target': r['GHGs'], 'value': r['flux'], 'color_key': r['EDGAR_Sector']})
        
    data_to_save = {
        "scr_data": df.to_dict(orient='records'),
        "der_data": {
            "flows": flows,
            "total_flux": total_flux
        }
    }
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    with open(output_filename, 'w') as f:
        json.dump(data_to_save, f, indent=4)
        
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/126.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compute_data(output_file)
