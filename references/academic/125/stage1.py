import sys
import io
import pandas as pd
import json
import os

def compute_data(output_filename):
    csv_data = """Unnamed: 0,GHGs,EDGAR_Sector,FOOD_system_stage,FOOD_system_stage_detailed,FOOD_system_compartment,flux,freq,GHG2
1,CH4,Agriculture,Production,Production,Landbased,42177.5,0.0088166,CH4
2,CH4,Chemicals,Distribution,Packaging,Industry,1.36274,2.84862e-07,CH4
3,CH4,Ener for agr. fishing,Production,Production,Energy,19618.7,0.00410101,CH4
4,CH4,Ener for agric. fishing,Consumption,Consumption,Energy,93.927,1.96341e-05,CH4
5,CH4,"Ener for aluminium,paper,glass",Production,Production,Energy,1.13454,2.3716e-07,CH4
6,CH4,Ener for household,Production,Production,Energy,46.3744,9.69392e-06,CH4
7,CH4,Ener for households,Consumption,Consumption,Energy,2479.58,0.000518322,CH4
8,CH4,Ener for packaging,Distribution,Packaging,Energy,14900.5,0.00311474,CH4
9,CH4,Ener for production,Processing,Processing,Energy,15353.9,0.00320952,CH4
10,CH4,Ener for retail,Distribution,Retail,Energy,8150.33,0.00170371,CH4
11,CH4,Ener for transport,Distribution,Transport,Energy,32191.3,0.00672914,CH4
12,CH4,Enteric Ferment,Production,Production,Landbased,819792,0.171366,CH4
13,CH4,Industrial,Distribution,Packaging,Energy,1028.36,0.000214964,CH4
14,CH4,Industrial,Processing,Processing,Energy,311.032,6.5017e-05,CH4
15,CH4,LULUC,Production,LULUC,Landbased,4180.63,0.000873903,CH4
16,CH4,Manure,Production,Production,Landbased,190894,0.0399037,CH4
17,CH4,Residential,Consumption,Consumption,Energy,162.718,3.40139e-05,CH4
18,CH4,Residential,Distribution,Retail,Energy,173.192,3.62034e-05,CH4
19,CH4,Residential,Production,Production,Energy,1809.76,0.000378304,CH4
20,CH4,Road Transport,Distribution,Transport,Energy,921.986,0.000192728,CH4
21,CH4,Solid waste,End of Life,End of Life,Waste,241386,0.0504583,CH4
22,CH4,Transport,Distribution,Transport,Energy,27.9537,5.84333e-06,CH4
23,CH4,Waste burning,Production,Production,Landbased,8217.86,0.00171783,CH4
24,CH4,Waste water,End of Life,End of Life,Waste,90833.4,0.0189875,CH4
25,CH4,Waste water,Processing,Processing,Waste,30124.5,0.0062971,CH4
26,CO2,Agriculture,Production,Production,Landbased,38462.2,0.00803998,CO2
27,CO2,Chemicals,Distribution,Packaging,Industry,108.402,2.26599e-05,CO2
28,CO2,Chemicals,Production,Production,Industry,78676.1,0.0164461,CO2
29,CO2,Ener for agr. fishing,Production,Production,Energy,12709.5,0.00265674,CO2
30,CO2,Ener for agric. fishing,Consumption,Consumption,Energy,87351.5,0.0182596,CO2
31,CO2,"Ener for aluminium,paper,glass",Production,Production,Energy,1544.68,0.000322895,CO2
32,CO2,Ener for household,Production,Production,Energy,50876.3,0.010635,CO2
33,CO2,Ener for households,Consumption,Consumption,Energy,1629.85,0.000340698,CO2
34,CO2,Ener for packaging,Distribution,Packaging,Energy,21964.5,0.00459138,CO2
35,CO2,Ener for production,Processing,Processing,Energy,75347.5,0.0157503,CO2
36,CO2,Ener for retail,Distribution,Retail,Energy,136332,0.0284983,CO2
37,CO2,Ener for transport,Distribution,Transport,Energy,24678.3,0.00515866,CO2
38,CO2,Industrial,Distribution,Packaging,Energy,178748,0.0373647,CO2
39,CO2,Industrial,Processing,Processing,Energy,133339,0.0278725,CO2
40,CO2,Iron Steel,Distribution,Packaging,Industry,560.61,0.000117188,CO2
41,CO2,LULUC,Production,LULUC,Landbased,677014,0.14152,CO2
42,CO2,Non-Ferrous,Distribution,Packaging,Industry,4169.58,0.000871593,CO2
43,CO2,Non-metallic,Distribution,Packaging,Industry,5559.02,0.00116203,CO2
44,CO2,Residential,Consumption,Consumption,Energy,20635,0.00431346,CO2
45,CO2,Residential,Distribution,Retail,Energy,66260.3,0.0138508,CO2
46,CO2,Residential,Production,Production,Energy,186441,0.0389729,CO2
47,CO2,Road Transport,Distribution,Transport,Energy,400796,0.0837808,CO2
48,CO2,Solid waste,End of Life,End of Life,Waste,2254.99,0.000471374,CO2
49,CO2,Solvents,Production,Production,Industry,2504.88,0.00052361,CO2
50,CO2,Transport,Distribution,Transport,Energy,15605.9,0.00326219,CO2
51,F-gases,Non-Ferrous,Distribution,Packaging,Industry,2.15024,4.49477e-07,F-gases
52,F-gases,Products,Distribution,Retail,Industry,385620,0.0806085,F-gases
53,N2O,Agriculture,Production,Production,Landbased,403577,0.0843622,N2O
54,N2O,Chemicals,Distribution,Packaging,Industry,66.2957,1.38582e-05,N2O
55,N2O,Chemicals,Production,Production,Industry,47449.3,0.0099186,N2O
56,N2O,Ener for agr. fishing,Production,Production,Energy,90.0027,1.88138e-05,N2O
57,N2O,Ener for agric. fishing,Consumption,Consumption,Energy,437.88,9.15327e-05,N2O
58,N2O,"Ener for aluminium,paper,glass",Production,Production,Energy,9.48851,1.98344e-06,N2O
59,N2O,Ener for household,Production,Production,Energy,180.47,3.77247e-05,N2O
60,N2O,Ener for households,Consumption,Consumption,Energy,1.78579,3.73294e-07,N2O
61,N2O,Ener for packaging,Distribution,Packaging,Energy,15.1069,3.15788e-06,N2O
62,N2O,Ener for production,Processing,Processing,Energy,330.889,6.91677e-05,N2O
63,N2O,Ener for retail,Distribution,Retail,Energy,706.782,0.000147743,N2O
64,N2O,Ener for transport,Distribution,Transport,Energy,217.662,4.54992e-05,N2O
65,N2O,Indirect emi,Consumption,Consumption,Energy,14050.4,0.00293705,N2O
66,N2O,Indirect emi,Processing,Processing,Industry,235.675,4.92646e-05,N2O
67,N2O,Indirect N2O,Production,Production,Landbased,83877.8,0.0175335,N2O
68,N2O,Industrial,Distribution,Packaging,Energy,1365.91,0.000285524,N2O
69,N2O,Industrial,Processing,Processing,Energy,496.762,0.000103841,N2O
70,N2O,LULUC,Production,LULUC,Landbased,104.356,2.18141e-05,N2O
71,N2O,Manure,Production,Production,Landbased,32650.9,0.00682522,N2O
72,N2O,Residential,Consumption,Consumption,Energy,28.1415,5.88258e-06,N2O
73,N2O,Residential,Distribution,Retail,Energy,33.3353,6.96828e-06,N2O
74,N2O,Residential,Production,Production,Energy,13219.3,0.00276331,N2O
75,N2O,Road Transport,Distribution,Transport,Energy,5907.09,0.00123479,N2O
76,N2O,Solid waste,End of Life,End of Life,Waste,6543.85,0.0013679,N2O
77,N2O,Transport,Distribution,Transport,Energy,1043.14,0.000218053,N2O
78,N2O,Waste burning,Production,Production,Landbased,2016.42,0.000421504,N2O
79,N2O,Waste water,End of Life,End of Life,Waste,28113.3,0.00587668,N2O
80,N2O,Waste water,Processing,Processing,Waste,7028.01,0.00146911,N2O
"""

    df = pd.read_csv(io.StringIO(csv_data))
    
    # Rename values to match image labels
    df['FOOD_system_compartment'] = df['FOOD_system_compartment'].replace({
        'Landbased': 'Land based'
    })
    
    df['FOOD_system_stage_detailed'] = df['FOOD_system_stage_detailed'].replace({
        'End of Life': 'End of life'
    })
    
    df['EDGAR_Sector'] = df['EDGAR_Sector'].replace({
        'Enteric Ferment': 'Enteric ferment',
        'Road Transport': 'Road transport',
        'Ener for agr. fishing': 'Energy for agriculture fishing',
        'Ener for agric. fishing': 'Energy for agriculture fishing',
        'Ener for household': 'Energy for household',
        'Ener for households': 'Energy for household',
        'Ener for production': 'Energy for production',
        'Ener for packaging': 'Energy for packaging',
        'Ener for retail': 'Energy for retail',
        'Ener for transport': 'Energy for transport',
        'Ener for aluminium,paper,glass': 'Energy for aluminium,paper,glass'
    })
    
    links = []
    
    def add_layer(source_col, target_col, layer_idx):
        grouped = df.groupby([source_col, target_col])['flux'].sum().reset_index()
        for _, row in grouped.iterrows():
            links.append({
                'source': row[source_col],
                'target': row[target_col],
                'value': row['flux'],
                'layer': layer_idx
            })

    add_layer('GHGs', 'FOOD_system_compartment', 0)
    add_layer('FOOD_system_compartment', 'FOOD_system_stage_detailed', 1)
    add_layer('FOOD_system_stage_detailed', 'EDGAR_Sector', 2)
    add_layer('EDGAR_Sector', 'GHG2', 3)
    
    links_df = pd.DataFrame(links)
    total_flux = links_df[links_df['layer'] == 0]['value'].sum()
    
    # Populate Layer 3 order
    top_nodes = ['LULUC', 'Agriculture', 'Enteric ferment', 'Manure', 'Indirect N2O']
    layer3_nodes = links_df[links_df['layer'] == 2]['target'].unique()
    node_sums = links_df[links_df['layer'] == 2].groupby('target')['value'].sum()
    sorted_all = node_sums.sort_values(ascending=False).index.tolist()
    
    final_order = [n for n in top_nodes if n in layer3_nodes]
    remaining = [n for n in sorted_all if n not in final_order]
    final_order.extend(remaining)
    
    data_to_save = {
        "scr_data": df.to_dict(orient='records'),
        "der_data": {
            "links": links,
            "layer3_order": final_order,
            "total_flux": total_flux
        }
    }
    
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    with open(output_filename, 'w') as f:
        json.dump(data_to_save, f, indent=4)
        
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/125.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compute_data(output_file)
