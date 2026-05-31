import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import numpy as np

# 1. Source Data Embedding
# Note: Fields containing commas have been quoted to ensure correct parsing.
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

# 2. Configuration and Styling
OUTPUT_FILENAME = sys.argv[1] if len(sys.argv) > 1 else "output.png"

# Color Palette
COLORS = {
    # Gases
    "CH4": "#5D94C3",
    "CO2": "#B4CCE5",
    "N2O": "#F3C57B",
    "F-gases": "#D3D3D3",
    
    # Sectors (Compartments)
    "Land based": "#5FA052",
    "Energy": "#F0AD4E",
    "Industry": "#A9A9A9",
    "Waste": "#F4D06F",
    
    # Stages
    "LULUC": "#869E6E",
    "Production": "#77D362",
    "Transport": "#5D94C3",
    "Processing": "#5D94C3",
    "Packaging": "#5D94C3",
    "Retail": "#5D94C3",
    "Consumption": "#87CEEB",
    "End of life": "#A9A9A9",
    
    # Categories
    "Agriculture": "#A58AC1",
    "Enteric ferment": "#A58AC1",
    "Manure": "#D8BFD8",
    "Indirect N2O": "#D8BFD8",
    "Indirect emi": "#D8BFD8",
    "Waste water": "#ADD8E6",
    "Solid waste": "#ADD8E6",
    "Road transport": "#5F9EA0",
    "Products": "#A9A9A9",
    "Chemicals": "#90EE90",
    "Industrial": "#4682B4",
    "Iron Steel": "#A9A9A9",
    "Non-Ferrous": "#A9A9A9",
    "Non-metallic": "#A9A9A9",
    "Solvents": "#A9A9A9",
    "Waste burning": "#5FA052",
    "Energy for household": "#F0AD4E",
    "Energy for production": "#F0AD4E",
    "Energy for packaging": "#F0AD4E",
    "Energy for agriculture fishing": "#F0AD4E",
    "Other": "#5FA052",
}

DEFAULT_COLOR = "#D3D3D3"

# Labels with trends
LABELS_EXTRA = {
    "CH4": " [↑ +16%]",
    "CO2": " [↓ −11%]",
    "N2O": " [↑ +29%]",
    "Land based": " [↓ −13%]",
    "Energy": " [↑ +78%]",
    "Industry": " [↔ 0%]",
    "Waste": " [↑ +67%]",
    "LULUC": " [↓ −28%]",
    "Production": " [↑ +18%]",
    "Transport": " [↑ +200%]",
    "Processing": " [↑ +200%]",
    "Packaging": " [↑ +150%]",
    "Retail": " [↑ > 100%]",
    "Consumption": " [↑ +50%]",
    "End of life": " [↑ +50%]",
}

# 3. Data Processing
def load_data():
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
    
    return df

def prepare_sankey_data(df):
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

    # Layer 0: GHGs -> Compartment
    add_layer('GHGs', 'FOOD_system_compartment', 0)
    # Layer 1: Compartment -> Stage
    add_layer('FOOD_system_compartment', 'FOOD_system_stage_detailed', 1)
    # Layer 2: Stage -> Sector
    add_layer('FOOD_system_stage_detailed', 'EDGAR_Sector', 2)
    # Layer 3: Sector -> GHG2
    add_layer('EDGAR_Sector', 'GHG2', 3)
    
    return pd.DataFrame(links)

# 4. Sankey Drawing Logic
class SankeyDiagram:
    def __init__(self, links_df, width=20, height=12):
        self.links_df = links_df
        self.fig, self.ax = plt.subplots(figsize=(width, height))
        self.ax.axis('off')
        
        self.x_pos = [0, 1, 2, 3, 4]
        self.col_width = 0.05
        self.gap = 0.02
        
        self.layers = [
            ['GHGs'], 
            ['FOOD_system_compartment'], 
            ['FOOD_system_stage_detailed'], 
            ['EDGAR_Sector'], 
            ['GHG2']
        ]
        
        # Define explicit order for nodes to match image
        self.node_order = {
            0: ['CH4', 'CO2', 'F-gases', 'N2O'],
            1: ['Land based', 'Energy', 'Industry', 'Waste'],
            2: ['LULUC', 'Production', 'Transport', 'Processing', 'Packaging', 'Retail', 'Consumption', 'End of life'],
            3: [], # To be populated
            4: ['CH4', 'CO2', 'F-gases', 'N2O']
        }
        
        self.total_flux = links_df[links_df['layer'] == 0]['value'].sum()
        
        # Populate Layer 3 order
        # Prioritize specific nodes at top
        top_nodes = ['LULUC', 'Agriculture', 'Enteric ferment', 'Manure', 'Indirect N2O']
        
        # Get all target nodes for layer 2
        layer3_nodes = links_df[links_df['layer'] == 2]['target'].unique()
        
        # Calculate sums to sort the rest
        node_sums = links_df[links_df['layer'] == 2].groupby('target')['value'].sum()
        
        # Sort descending
        sorted_all = node_sums.sort_values(ascending=False).index.tolist()
        
        # Construct final order: Top nodes first, then the rest sorted by size
        final_order = [n for n in top_nodes if n in layer3_nodes]
        remaining = [n for n in sorted_all if n not in final_order]
        final_order.extend(remaining)
        
        self.node_order[3] = final_order

        self.node_geoms = {}
        self.node_input_y = {}
        self.node_output_y = {}

    def layout(self):
        for layer_idx in range(5):
            # Determine nodes for this layer
            if layer_idx in self.node_order and self.node_order[layer_idx]:
                nodes = self.node_order[layer_idx]
                # Filter to only those present in data
                if layer_idx == 0:
                    present = self.links_df[self.links_df['layer']==0]['source'].unique()
                else:
                    present = self.links_df[self.links_df['layer']==layer_idx-1]['target'].unique()
                nodes = [n for n in nodes if n in present]
            else:
                # Fallback if not defined (shouldn't happen with current setup)
                nodes = []

            # Calculate flux per node
            node_fluxes = {}
            for node in nodes:
                if layer_idx == 0:
                    flux = self.links_df[(self.links_df['layer'] == 0) & (self.links_df['source'] == node)]['value'].sum()
                else:
                    flux = self.links_df[(self.links_df['layer'] == layer_idx - 1) & (self.links_df['target'] == node)]['value'].sum()
                node_fluxes[node] = flux
            
            # Calculate geometry
            current_y = 1.0
            total_gap = (len(nodes) - 1) * self.gap
            available_height = 1.0 - total_gap
            
            # Scale based on the layer's total flux to fill height
            layer_total = sum(node_fluxes.values())
            scale = available_height / layer_total if layer_total > 0 else 0
            
            for node in nodes:
                h = node_fluxes[node] * scale
                
                # Color lookup
                color = COLORS.get(node, DEFAULT_COLOR)
                if node.startswith("Energy for"):
                    color = COLORS.get("Energy", DEFAULT_COLOR)
                
                self.node_geoms[f"{layer_idx}_{node}"] = {
                    'x': self.x_pos[layer_idx],
                    'y': current_y - h,
                    'h': h,
                    'w': self.col_width,
                    'color': color,
                    'value': node_fluxes[node],
                    'name': node
                }
                
                self.node_input_y[f"{layer_idx}_{node}"] = current_y
                self.node_output_y[f"{layer_idx}_{node}"] = current_y
                
                current_y -= (h + self.gap)

    def draw_ribbon(self, x_s, y_s, x_t, y_t, h, color, alpha=0.5):
        path_data = [
            (Path.MOVETO, (x_s, y_s)),
            (Path.CURVE4, (x_s + 0.4, y_s)),
            (Path.CURVE4, (x_t - 0.4, y_t)),
            (Path.CURVE4, (x_t, y_t)),
            (Path.LINETO, (x_t, y_t - h)),
            (Path.CURVE4, (x_t - 0.4, y_t - h)),
            (Path.CURVE4, (x_s + 0.4, y_s - h)),
            (Path.CURVE4, (x_s, y_s - h)),
            (Path.CLOSEPOLY, (x_s, y_s))
        ]
        codes, verts = zip(*path_data)
        path = Path(verts, codes)
        patch = patches.PathPatch(path, facecolor=color, edgecolor='none', alpha=alpha)
        self.ax.add_patch(patch)

    def draw(self):
        self.layout()
        
        for layer_idx in range(4):
            layer_links = self.links_df[self.links_df['layer'] == layer_idx].copy()
            
            # Sort links to minimize crossing
            def get_order(node_name, l_idx):
                nodes = self.node_order.get(l_idx, [])
                # Filter to present nodes to match layout order
                if l_idx == 0:
                    present = self.links_df[self.links_df['layer']==0]['source'].unique()
                else:
                    present = self.links_df[self.links_df['layer']==l_idx-1]['target'].unique()
                
                nodes = [n for n in nodes if n in present]
                
                try:
                    return nodes.index(node_name)
                except ValueError:
                    return 999
            
            layer_links['src_order'] = layer_links['source'].apply(lambda x: get_order(x, layer_idx))
            layer_links['tgt_order'] = layer_links['target'].apply(lambda x: get_order(x, layer_idx+1))
            
            layer_links = layer_links.sort_values(['src_order', 'tgt_order'])
            
            # Calculate scale for this layer
            src_nodes = [n for n in self.node_order[layer_idx] if f"{layer_idx}_{n}" in self.node_geoms]
            layer_total = sum([self.node_geoms[f"{layer_idx}_{n}"]['value'] for n in src_nodes])
            total_gap = (len(src_nodes) - 1) * self.gap
            available_height = 1.0 - total_gap
            scale = available_height / layer_total if layer_total > 0 else 0

            for _, row in layer_links.iterrows():
                src = row['source']
                tgt = row['target']
                val = row['value']
                h = val * scale
                
                src_key = f"{layer_idx}_{src}"
                tgt_key = f"{layer_idx+1}_{tgt}"
                
                if src_key not in self.node_geoms or tgt_key not in self.node_geoms:
                    continue
                
                x_s = self.node_geoms[src_key]['x'] + self.col_width
                y_s = self.node_output_y[src_key]
                
                x_t = self.node_geoms[tgt_key]['x']
                y_t = self.node_input_y[tgt_key]
                
                color = self.node_geoms[src_key]['color']
                
                self.draw_ribbon(x_s, y_s, x_t, y_t, h, color)
                
                self.node_output_y[src_key] -= h
                self.node_input_y[tgt_key] -= h

        # Draw Nodes and Labels
        for key, geom in self.node_geoms.items():
            rect = patches.Rectangle(
                (geom['x'], geom['y']), 
                geom['w'], 
                geom['h'], 
                facecolor=geom['color'], 
                edgecolor='black',
                linewidth=0.5
            )
            self.ax.add_patch(rect)
            
            pct = (geom['value'] / self.total_flux) * 100
            extra = LABELS_EXTRA.get(geom['name'], "")
            label_text = f"{geom['name']} ({pct:.0f}%){extra}"
            
            layer_idx = int(key.split('_')[0])
            
            # Label positioning
            if layer_idx == 4:
                text_x = geom['x'] + geom['w'] + 0.05
                ha = 'left'
            elif layer_idx == 0:
                text_x = geom['x'] + 0.1
                ha = 'left'
            else:
                text_x = geom['x'] + geom['w'] + 0.02
                ha = 'left'
            
            # Only label if height is significant or it's a main category
            if geom['h'] > 0.005 or layer_idx in [0, 1, 4]:
                self.ax.text(
                    text_x, 
                    geom['y'] + geom['h']/2, 
                    label_text, 
                    va='center', 
                    ha=ha, 
                    fontsize=8,
                    color='black'
                )

        titles = ["Gases", "Sectors", "Stages", "Categories", ""]
        for i, title in enumerate(titles):
            self.ax.text(i, 1.02, title, fontsize=12, fontweight='bold')

        self.ax.set_xlim(-0.1, 4.8)
        self.ax.set_ylim(0, 1.05)

def main():
    df = load_data()
    links_df = prepare_sankey_data(df)
    
    sankey = SankeyDiagram(links_df)
    sankey.draw()
    
    plt.tight_layout()
    plt.savefig(OUTPUT_FILENAME, dpi=300, bbox_inches='tight')

if __name__ == "__main__":
    main()