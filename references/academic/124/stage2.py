import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches

# ---------------------------------------------------------
# 1. Source Data Embedding
# ---------------------------------------------------------
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

# ---------------------------------------------------------
# 2. Data Processing
# ---------------------------------------------------------

def load_data():
    df = pd.read_csv(io.StringIO(csv_data), sep='|')
    df.columns = [c.strip() for c in df.columns]
    
    # Clean string columns
    str_cols = ['GHGs', 'EDGAR_Sector', 'FOOD_system_stage', 'FOOD_system_compartment', 'GHG2']
    for c in str_cols:
        df[c] = df[c].str.strip()
        
    # Fix specific naming to match chart visual
    df['FOOD_system_compartment'] = df['FOOD_system_compartment'].replace({'Landbased': 'Land based'})
    df['FOOD_system_stage'] = df['FOOD_system_stage'].replace({'End of Life': 'End of life'})
    
    return df

# ---------------------------------------------------------
# 3. Sankey Logic (Manual Implementation)
# ---------------------------------------------------------

class SankeyChart:
    def __init__(self, df):
        self.df = df
        self.total_flux = df['flux'].sum()
        self.node_width = 0.3
        self.gap = 0.05  # Vertical gap between nodes relative to total height
        self.curvature = 0.5
        
        # Define Colors
        self.colors = {
            'CH4': '#5D94B4',
            'CO2': '#A8C6E3',
            'F-gases': '#F09C6F',
            'N2O': '#F6D99A',
            
            'Land based': '#6FB05C',
            'Energy': '#F5B041',
            'Industry': '#99A3A4',
            'Waste': '#F7DC6F',
            
            'LULUC': '#8D9E74',
            'Production': '#76D75D',
            'Transport': '#34495E',
            'Processing': '#5D6D7E',
            'Packaging': '#5499C7',
            'Retail': '#5DADE2',
            'Consumption': '#85C1E9',
            'End of life': '#95A5A6',
            
            # Fallback for categories
            'Agriculture': '#A569BD',
            'Enteric Ferment': '#8E44AD',
            'Manure': '#D2B4DE',
            'Indirect N2O': '#E8DAEF',
            'Waste water': '#52BE80',
            'Solid waste': '#F4D03F',
            'Road Transport': '#E67E22',
            'Other': '#BDC3C7'
        }
        
        # Define Order of Nodes (Top to Bottom)
        self.order = {
            0: ['CH4', 'CO2', 'F-gases', 'N2O'],
            1: ['Land based', 'Energy', 'Industry', 'Waste'],
            2: ['LULUC', 'Production', 'Transport', 'Processing', 'Packaging', 'Retail', 'Consumption', 'End of life'],
            3: [], # Will be sorted by flux
            4: ['CH4', 'CO2', 'F-gases', 'N2O']
        }

    def _get_color(self, name):
        # Heuristic for coloring categories based on parent or name
        if name in self.colors:
            return self.colors[name]
        if 'Energy' in name or 'Ener' in name: return '#D6DBDF'
        if 'Industrial' in name: return '#85929E'
        if 'Chemicals' in name: return '#AED6F1'
        if 'Residential' in name: return '#5DADE2'
        return '#D7DBDD'

    def prepare_data(self):
        # Define the columns of the Sankey
        # Col 0: GHGs
        # Col 1: Compartment
        # Col 2: Stage
        # Col 3: Category (EDGAR)
        # Col 4: GHGs (Right)
        
        self.layers = []
        
        # Layer 1: GHGs -> Compartment
        l1 = self.df.groupby(['GHGs', 'FOOD_system_compartment'])['flux'].sum().reset_index()
        l1.columns = ['source', 'target', 'value']
        self.layers.append(l1)
        
        # Layer 2: Compartment -> Stage
        l2 = self.df.groupby(['FOOD_system_compartment', 'FOOD_system_stage'])['flux'].sum().reset_index()
        l2.columns = ['source', 'target', 'value']
        self.layers.append(l2)
        
        # Layer 3: Stage -> Category
        l3 = self.df.groupby(['FOOD_system_stage', 'EDGAR_Sector'])['flux'].sum().reset_index()
        l3.columns = ['source', 'target', 'value']
        self.layers.append(l3)
        
        # Layer 4: Category -> GHGs (Right)
        l4 = self.df.groupby(['EDGAR_Sector', 'GHG2'])['flux'].sum().reset_index()
        l4.columns = ['source', 'target', 'value']
        self.layers.append(l4)
        
        # Populate order for column 3 (Categories) based on flux
        cats = self.df.groupby('EDGAR_Sector')['flux'].sum().sort_values(ascending=False).index.tolist()
        # Move LULUC to top to match image style if present
        if 'LULUC' in cats:
            cats.remove('LULUC')
            cats.insert(0, 'LULUC')
        self.order[3] = cats

    def calculate_layout(self):
        self.node_pos = {} # {col_idx: {node_name: {'y': start_y, 'h': height}}}
        
        for col_idx in range(5):
            nodes = self.order[col_idx]
            
            # Calculate heights
            node_fluxes = {}
            
            # Sum incoming or outgoing to determine node size
            if col_idx == 0:
                # Only outgoing
                data = self.layers[0]
                for n in nodes:
                    node_fluxes[n] = data[data['source'] == n]['value'].sum()
            elif col_idx == 4:
                # Only incoming
                data = self.layers[3]
                for n in nodes:
                    node_fluxes[n] = data[data['target'] == n]['value'].sum()
            else:
                # Max of incoming or outgoing
                data_in = self.layers[col_idx-1]
                data_out = self.layers[col_idx]
                for n in nodes:
                    val_in = data_in[data_in['target'] == n]['value'].sum()
                    val_out = data_out[data_out['source'] == n]['value'].sum()
                    node_fluxes[n] = max(val_in, val_out)
            
            # Normalize to plot height (let's say 100 units)
            total_flux_in_col = sum(node_fluxes.values())
            scale_factor = (100 - (len(nodes) - 1) * 2) / total_flux_in_col # 2 is gap size
            
            current_y = 100
            self.node_pos[col_idx] = {}
            
            for n in nodes:
                h = node_fluxes[n] * scale_factor
                self.node_pos[col_idx][n] = {'y': current_y, 'h': h, 'flux': node_fluxes[n]}
                current_y -= (h + 2) # 2 unit gap

    def draw_bezier(self, ax, x1, y1, x2, y2, width, color, alpha=0.6):
        # Control points for Bezier curve
        mid_x = (x1 + x2) / 2
        verts = [
            (x1, y1), # Start top
            (mid_x, y1), # Control 1
            (mid_x, y2), # Control 2
            (x2, y2), # End top
            (x2, y2 - width), # End bottom
            (mid_x, y2 - width), # Control 3
            (mid_x, y1 - width), # Control 4
            (x1, y1 - width), # Start bottom
            (x1, y1), # Close
        ]
        codes = [
            Path.MOVETO,
            Path.CURVE4,
            Path.CURVE4,
            Path.CURVE4,
            Path.LINETO,
            Path.CURVE4,
            Path.CURVE4,
            Path.CURVE4,
            Path.CLOSEPOLY,
        ]
        path = Path(verts, codes)
        patch = patches.PathPatch(path, facecolor=color, lw=0, alpha=alpha)
        ax.add_patch(patch)

    def draw(self, output_path):
        fig, ax = plt.subplots(figsize=(20, 10))
        ax.set_xlim(-0.5, 4.5)
        ax.set_ylim(0, 105)
        ax.axis('off')
        
        # Draw Links
        for i, layer in enumerate(self.layers):
            source_col = i
            target_col = i + 1
            
            # Track current Y position for stacking flows
            source_y_offsets = {n: 0.0 for n in self.order[source_col]}
            target_y_offsets = {n: 0.0 for n in self.order[target_col]}
            
            # Sort flows to minimize crossing? 
            # Simple approach: iterate through source nodes in order, then target nodes in order
            
            # We need to normalize values to height units
            # Re-calculate scale factor for this column to ensure links match node heights
            # (Using the pre-calculated heights in node_pos)
            
            for src in self.order[source_col]:
                if src not in self.node_pos[source_col]: continue
                
                # Get flows from this source
                flows = layer[layer['source'] == src]
                
                # Sort targets by their vertical position to untangle
                flows['target_y'] = flows['target'].apply(lambda x: self.node_pos[target_col][x]['y'] if x in self.node_pos[target_col] else 0)
                flows = flows.sort_values('target_y', ascending=False)
                
                src_node = self.node_pos[source_col][src]
                
                for _, row in flows.iterrows():
                    tgt = row['target']
                    val = row['value']
                    
                    if tgt not in self.node_pos[target_col]: continue
                    tgt_node = self.node_pos[target_col][tgt]
                    
                    # Calculate link height
                    # Scale based on source node's scaling
                    # h = (val / src_node['flux']) * src_node['h'] 
                    # Better: global scale approximation or ratio
                    link_h = (val / self.total_flux) * (100 - (len(self.order[0])-1)*2) * 1.1 # Approximation
                    # Precise calculation:
                    link_h = (val / src_node['flux']) * src_node['h']
                    
                    # Coordinates
                    x1 = source_col + self.node_width
                    y1 = src_node['y'] - source_y_offsets[src]
                    x2 = target_col
                    y2 = tgt_node['y'] - target_y_offsets[tgt]
                    
                    # Color logic
                    color = self._get_color(src)
                    if i == 3: # Last layer color by target (Gas)
                        color = self._get_color(tgt)
                    elif i == 2: # Categories layer
                         # Try to inherit or use specific category color
                         color = self._get_color(tgt)

                    self.draw_bezier(ax, x1, y1, x2, y2, link_h, color)
                    
                    source_y_offsets[src] += link_h
                    target_y_offsets[tgt] += link_h

        # Draw Nodes and Labels
        col_labels = ["Gases", "Sectors", "Stages", "Categories", ""]
        
        for col_idx in range(5):
            # Column Title
            if col_idx < 4:
                ax.text(col_idx, 102, col_labels[col_idx], fontsize=14, fontweight='bold')
            
            for name in self.order[col_idx]:
                if name not in self.node_pos[col_idx]: continue
                node = self.node_pos[col_idx][name]
                
                # Draw Rectangle
                rect = patches.Rectangle(
                    (col_idx, node['y'] - node['h']),
                    self.node_width,
                    node['h'],
                    facecolor=self._get_color(name),
                    edgecolor='black',
                    linewidth=0.5,
                    alpha=0.9
                )
                ax.add_patch(rect)
                
                # Add Label
                pct = (node['flux'] / self.total_flux) * 100
                label_text = f"{name} ({pct:.0f}%)"
                
                # Adjust label position
                text_x = col_idx + self.node_width/2
                text_y = node['y'] - node['h']/2
                
                # Special handling for small nodes or specific columns
                if col_idx == 4:
                    text_x = col_idx + self.node_width + 0.1
                    ha = 'left'
                elif col_idx == 0:
                    text_x = col_idx + self.node_width/2
                    ha = 'center'
                elif col_idx == 3:
                    # Categories: put label to the right of the bar if it fits, or inside
                    if node['h'] < 2:
                        text_x = col_idx + self.node_width + 0.05
                        ha = 'left'
                    else:
                        text_x = col_idx + 0.05
                        ha = 'left'
                else:
                    ha = 'left'
                    text_x = col_idx + 0.05
                
                # Filter very small labels
                if pct >= 1.0:
                    ax.text(text_x, text_y, label_text, ha=ha, va='center', fontsize=9)

        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()

# ---------------------------------------------------------
# 4. Main Execution
# ---------------------------------------------------------

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
        
    df = load_data()
    chart = SankeyChart(df)
    chart.prepare_data()
    chart.calculate_layout()
    chart.draw(output_file)
    print(f"Chart saved to {output_file}")