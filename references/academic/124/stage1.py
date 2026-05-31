import sys
import io
import pandas as pd
import json
import os

def compute_data(output_filename):
    csv_data = """
Unnamed: 0|GHGs|EDGAR_Sector|FOOD_system_stage|FOOD_system_stage_detailed|FOOD_system_compartment|flux|freq|GHG2
2|CH4|Agriculture|Production|Production|Landbased|1.03115e+06|0.0580785|CH4
3|CH4|Chemicals|Distribution|Packaging|Industry|6.48836|3.6545e-07|CH4
4|CH4|Ener for agr. fishing|Production|Production|Energy|44621.3|0.00251325|CH4
5|CH4|Ener for agric. fishing|Consumption|Consumption|Energy|148.936|8.38867e-06|CH4
6|CH4|Ener for aluminium,paper,glass|Production|Production|Energy|2.24574|1.26489e-07|CH4
7|CH4|Ener for household|Production|Production|Energy|155.826|8.77671e-06|CH4
8|CH4|Ener for households|Consumption|Consumption|Energy|20727.6|0.00116746|CH4
9|CH4|Ener for packaging|Distribution|Packaging|Energy|68698|0.00386934|CH4
10|CH4|Ener for production|Processing|Processing|Energy|53788.4|0.00302957|CH4
11|CH4|Ener for retail|Distribution|Retail|Energy|16050.5|0.000904026|CH4
12|CH4|Ener for transport|Distribution|Transport|Energy|73187.5|0.00412221|CH4
13|CH4|Enteric Ferment|Production|Production|Landbased|2.95938e+06|0.166684|CH4
14|CH4|Industrial|Distribution|Packaging|Energy|2493.29|0.000140432|CH4
15|CH4|Industrial|Processing|Processing|Energy|1706.43|9.61129e-05|CH4
16|CH4|LULUC|Production|LULUC|Landbased|24212|0.00136371|CH4
17|CH4|Manure|Production|Production|Landbased|338967|0.019092|CH4
18|CH4|Residential|Consumption|Consumption|Energy|50668.3|0.00285384|CH4
19|CH4|Residential|Distribution|Retail|Energy|1077.59|6.0694e-05|CH4
20|CH4|Residential|Production|Production|Energy|9405.51|0.000529755|CH4
21|CH4|Road Transport|Distribution|Transport|Energy|2186.38|0.000123145|CH4
22|CH4|Solid waste|End of Life|End of Life|Waste|599901|0.0337888|CH4
23|CH4|Transport|Distribution|Transport|Energy|101.576|5.72116e-06|CH4
24|CH4|Waste burning|Production|Production|Landbased|52870.9|0.0029779|CH4
25|CH4|Waste water|End of Life|End of Life|Waste|845695|0.0476329|CH4
26|CH4|Waste water|Processing|Processing|Waste|104338|0.00587674|CH4
27|CO2|Agriculture|Production|Production|Landbased|109694|0.00617842|CO2
28|CO2|Chemicals|Distribution|Packaging|Industry|266.725|1.5023e-05|CO2
29|CO2|Chemicals|Production|Production|Industry|225061|0.0126763|CO2
30|CO2|Ener for agr. fishing|Production|Production|Energy|27882.7|0.00157046|CO2
31|CO2|Ener for agric. fishing|Consumption|Consumption|Energy|146821|0.00826952|CO2
32|CO2|Ener for aluminium,paper,glass|Production|Production|Energy|2832.18|0.000159519|CO2
33|CO2|Ener for household|Production|Production|Energy|191051|0.0107607|CO2
34|CO2|Ener for households|Consumption|Consumption|Energy|12909.3|0.000727101|CO2
35|CO2|Ener for packaging|Distribution|Packaging|Energy|56496.5|0.0031821|CO2
36|CO2|Ener for production|Processing|Processing|Energy|176202|0.00992441|CO2
37|CO2|Ener for retail|Distribution|Retail|Energy|174526|0.00982999|CO2
38|CO2|Ener for transport|Distribution|Transport|Energy|48903.5|0.00275444|CO2
39|CO2|Industrial|Distribution|Packaging|Energy|659765|0.0371606|CO2
40|CO2|Industrial|Processing|Processing|Energy|260709|0.0146842|CO2
41|CO2|Iron Steel|Distribution|Packaging|Industry|905.607|5.10074e-05|CO2
42|CO2|LULUC|Production|LULUC|Landbased|5.67081e+06|0.319402|CO2
43|CO2|Non-Ferrous|Distribution|Packaging|Industry|10140.5|0.000571155|CO2
44|CO2|Non-metallic|Distribution|Packaging|Industry|9592.6|0.000540293|CO2
45|CO2|Residential|Consumption|Consumption|Energy|175128|0.00986389|CO2
46|CO2|Residential|Distribution|Retail|Energy|120256|0.00677332|CO2
47|CO2|Residential|Production|Production|Energy|422783|0.0238128|CO2
48|CO2|Road Transport|Distribution|Transport|Energy|672293|0.0378662|CO2
49|CO2|Solid waste|End of Life|End of Life|Waste|3435.78|0.000193516|CO2
50|CO2|Solvents|Production|Production|Industry|6338.65|0.000357018|CO2
51|CO2|Transport|Distribution|Transport|Energy|50017.2|0.00281716|CO2
52|F-gases|Non-Ferrous|Distribution|Packaging|Industry|2.15024|1.2111e-07|F-gases
53|F-gases|Products|Distribution|Retail|Industry|402981|0.0226975|F-gases
54|N2O|Agriculture|Production|Production|Landbased|1.23687e+06|0.0696656|N2O
55|N2O|Chemicals|Distribution|Packaging|Industry|68.077|3.83436e-06|N2O
56|N2O|Chemicals|Production|Production|Industry|54977.8|0.00309657|N2O
57|N2O|Ener for agr. fishing|Production|Production|Energy|133.033|7.49297e-06|N2O
58|N2O|Ener for agric. fishing|Consumption|Consumption|Energy|698.646|3.93505e-05|N2O
59|N2O|Ener for aluminium,paper,glass|Production|Production|Energy|16.0808|9.05736e-07|N2O
60|N2O|Ener for household|Production|Production|Energy|935.927|5.27151e-05|N2O
61|N2O|Ener for households|Consumption|Consumption|Energy|26.5418|1.49494e-06|N2O
62|N2O|Ener for packaging|Distribution|Packaging|Energy|64.2116|3.61665e-06|N2O
63|N2O|Ener for production|Processing|Processing|Energy|854.568|4.81326e-05|N2O
64|N2O|Ener for retail|Distribution|Retail|Energy|873.275|4.91863e-05|N2O
65|N2O|Ener for transport|Distribution|Transport|Energy|295.888|1.66656e-05|N2O
66|N2O|Indirect emi|Consumption|Consumption|Energy|42525.1|0.00239518|N2O
67|N2O|Indirect emi|Processing|Processing|Industry|576.842|3.249e-05|N2O
68|N2O|Indirect N2O|Production|Production|Landbased|215679|0.0121479|N2O
69|N2O|Industrial|Distribution|Packaging|Energy|3418|0.000192515|N2O
70|N2O|Industrial|Processing|Processing|Energy|3263.3|0.000183802|N2O
71|N2O|LULUC|Production|LULUC|Landbased|408.646|2.30166e-05|N2O
72|N2O|Manure|Production|Production|Landbased|86592.2|0.00487721|N2O
73|N2O|Residential|Consumption|Consumption|Energy|4941.64|0.000278333|N2O
74|N2O|Residential|Distribution|Retail|Energy|264.443|1.48945e-05|N2O
75|N2O|Residential|Production|Production|Energy|30068.3|0.00169357|N2O
76|N2O|Road Transport|Distribution|Transport|Energy|7897.82|0.000444836|N2O
77|N2O|Solid waste|End of Life|End of Life|Waste|6745.11|0.000379911|N2O
78|N2O|Transport|Distribution|Transport|Energy|1690.01|9.51879e-05|N2O
79|N2O|Waste burning|Production|Production|Landbased|12972.9|0.000730687|N2O
80|N2O|Waste water|End of Life|End of Life|Waste|82096.6|0.004624|N2O
81|N2O|Waste water|Processing|Processing|Waste|20136|0.00113414|N2O
"""

    df = pd.read_csv(io.StringIO(csv_data), sep='|')
    df.columns = [c.strip() for c in df.columns]
    
    # Clean string columns
    str_cols = ['GHGs', 'EDGAR_Sector', 'FOOD_system_stage', 'FOOD_system_compartment', 'GHG2']
    for c in str_cols:
        df[c] = df[c].str.strip()
        
    # Fix specific naming to match chart visual
    df['FOOD_system_compartment'] = df['FOOD_system_compartment'].replace({'Landbased': 'Land based'})
    df['FOOD_system_stage'] = df['FOOD_system_stage'].replace({'End of Life': 'End of life'})
    
    total_flux = df['flux'].sum()
    
    layers = []
    
    # Layer 1: GHGs -> Compartment
    l1 = df.groupby(['GHGs', 'FOOD_system_compartment'])['flux'].sum().reset_index()
    l1.columns = ['source', 'target', 'value']
    layers.append(l1.to_dict(orient='records'))
    
    # Layer 2: Compartment -> Stage
    l2 = df.groupby(['FOOD_system_compartment', 'FOOD_system_stage'])['flux'].sum().reset_index()
    l2.columns = ['source', 'target', 'value']
    layers.append(l2.to_dict(orient='records'))
    
    # Layer 3: Stage -> Category
    l3 = df.groupby(['FOOD_system_stage', 'EDGAR_Sector'])['flux'].sum().reset_index()
    l3.columns = ['source', 'target', 'value']
    layers.append(l3.to_dict(orient='records'))
    
    # Layer 4: Category -> GHGs (Right)
    l4 = df.groupby(['EDGAR_Sector', 'GHG2'])['flux'].sum().reset_index()
    l4.columns = ['source', 'target', 'value']
    layers.append(l4.to_dict(orient='records'))
    
    # Populate order for column 3 (Categories) based on flux
    cats = df.groupby('EDGAR_Sector')['flux'].sum().sort_values(ascending=False).index.tolist()
    if 'LULUC' in cats:
        cats.remove('LULUC')
        cats.insert(0, 'LULUC')
        
    data_to_save = {
        "scr_data": df.to_dict(orient='records'),
        "der_data": {
            "layers": layers,
            "sorted_categories": cats,
            "total_flux": total_flux
        }
    }
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    with open(output_filename, 'w') as f:
        json.dump(data_to_save, f, indent=4)
        
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/124.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compute_data(output_file)
