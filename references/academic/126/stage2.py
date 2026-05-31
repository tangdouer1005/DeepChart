import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path
import numpy as np

# 1. Source Data Embedding
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

# 2. Configuration and Styling
COLORS = {
    'CH4': '#5D94C3',
    'CO2': '#9EB9D9',
    'N2O': '#D8B6D6',
    'F-gases': '#F0A66F', # Not in data, but in palette
    
    'Landbased': '#63B358',
    'Energy': '#F4B95A',
    'Industry': '#A6A6A6',
    'Waste': '#F2D675',
    
    'LULUC': '#7BC96F',
    'Production': '#7BC96F',
    'Transport': '#6D84AB',
    'Processing': '#6D84AB',
    'Packaging': '#87CEEB',
    'Retail': '#6495ED',
    'Consumption': '#87CEEB',
    'End of Life': '#A9A9A9',
    
    # Fallback for detailed sectors
    'Agriculture': '#8FBC8F',
    'Enteric Ferment': '#8FBC8F',
    'Manure': '#8FBC8F',
    'Road Transport': '#F4B95A',
    'Residential': '#F4B95A',
    'Industrial': '#A6A6A6',
    'Solid waste': '#F2D675',
    'Waste water': '#556B2F',
    'Other': '#D3D3D3'
}

# Order of nodes to match the visual as closely as possible
ORDERING = {
    0: ['CH4', 'CO2', 'N2O'], # Gases
    1: ['Landbased', 'Energy', 'Industry', 'Waste'], # Sectors
    2: ['LULUC', 'Production', 'Transport', 'Processing', 'Packaging', 'Retail', 'Consumption', 'End of Life'], # Stages
    # Column 3 (Categories) is sorted dynamically by flux/group
    4: ['CH4', 'CO2', 'N2O'] # Gases (Right)
}

def get_color(name, fallback='#cccccc'):
    # Heuristic matching for colors
    if name in COLORS: return COLORS[name]
    if 'Ener' in name: return COLORS['Energy']
    if 'Waste' in name: return COLORS['Waste']
    if 'Transport' in name: return COLORS['Transport']
    return fallback

# 3. Data Processing
def load_data():
    df = pd.read_csv(io.StringIO(csv_data), sep='|')
    df.columns = df.columns.str.strip()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].str.strip()
    return df

def prepare_sankey_data(df):
    # We need to construct flows between 5 columns:
    # 0: GHGs -> 1: Compartment -> 2: Stage -> 3: Sector -> 4: GHGs
    
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
        
    return pd.DataFrame(flows), total_flux

# 4. Sankey Logic
class SankeyPlotter:
    def __init__(self, flows_df, total_flux):
        self.flows = flows_df
        self.total_flux = total_flux
        self.columns = sorted(flows_df['source_col'].unique().tolist() + [4])
        self.nodes = {} # {col_idx: {node_name: {'value': v, 'y_top': y, 'y_bot': y}}}
        self.node_order = ORDERING
        
        # Layout params
        self.gap = 0.02 * total_flux # Gap between nodes
        self.width = 0.3 # Width of node bars
        self.x_spacing = 4 # Horizontal distance between columns
        
    def calculate_layout(self):
        # Calculate total value for each node
        for col in self.columns:
            self.nodes[col] = {}
            
            # Get nodes in this column
            if col < 4:
                col_nodes = self.flows[self.flows['source_col'] == col]['source'].unique()
            else:
                col_nodes = self.flows[self.flows['target_col'] == col]['target'].unique()
            
            # Calculate values
            node_data = []
            for node in col_nodes:
                if col < 4:
                    val = self.flows[(self.flows['source_col'] == col) & (self.flows['source'] == node)]['value'].sum()
                else:
                    val = self.flows[(self.flows['target_col'] == col) & (self.flows['target'] == node)]['value'].sum()
                node_data.append({'name': node, 'value': val})
            
            # Sort nodes
            if col in self.node_order:
                # Sort based on predefined order, putting unknown ones at the end
                order_map = {name: i for i, name in enumerate(self.node_order[col])}
                node_data.sort(key=lambda x: order_map.get(x['name'], 999))
            else:
                # Sort by value descending for the detailed sector column
                node_data.sort(key=lambda x: x['value'], reverse=True)
                
            # Assign Y coordinates (Top down)
            current_y = 0
            for n in node_data:
                self.nodes[col][n['name']] = {
                    'value': n['value'],
                    'y_top': current_y,
                    'y_bot': current_y + n['value'],
                    'input_y': current_y, # Tracker for incoming ribbons
                    'output_y': current_y # Tracker for outgoing ribbons
                }
                current_y += n['value'] + self.gap

    def draw_ribbon(self, ax, x1, x2, y1_top, y1_bot, y2_top, y2_bot, color, alpha=0.6):
        verts = [
            (x1, y1_top),
            (x1 + (x2-x1)/2, y1_top), # Control 1
            (x1 + (x2-x1)/2, y2_top), # Control 2
            (x2, y2_top),
            (x2, y2_bot),
            (x1 + (x2-x1)/2, y2_bot), # Control 3
            (x1 + (x2-x1)/2, y1_bot), # Control 4
            (x1, y1_bot),
            (x1, y1_top),
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

    def draw(self, ax):
        # Draw Ribbons
        # We iterate column by column
        for col_idx in range(len(self.columns) - 1):
            # Get flows for this step
            step_flows = self.flows[self.flows['source_col'] == col_idx].copy()
            
            # Sort flows to minimize crossing (simple heuristic: sort by target order)
            # This is complex, simplified here by iterating source nodes in order
            
            source_nodes = list(self.nodes[col_idx].keys())
            target_nodes = list(self.nodes[col_idx+1].keys())
            
            for s_node in source_nodes:
                # Get flows from this source
                s_flows = step_flows[step_flows['source'] == s_node]
                
                # Sort these flows by the order of target nodes
                s_flows['target_idx'] = s_flows['target'].apply(lambda x: target_nodes.index(x) if x in target_nodes else 999)
                s_flows = s_flows.sort_values('target_idx')
                
                for _, row in s_flows.iterrows():
                    t_node = row['target']
                    val = row['value']
                    
                    # Calculate coordinates
                    s_props = self.nodes[col_idx][s_node]
                    t_props = self.nodes[col_idx+1][t_node]
                    
                    y1_top = s_props['output_y']
                    y1_bot = y1_top + val
                    
                    y2_top = t_props['input_y']
                    y2_bot = y2_top + val
                    
                    # Update trackers
                    self.nodes[col_idx][s_node]['output_y'] += val
                    self.nodes[col_idx+1][t_node]['input_y'] += val
                    
                    # Color logic
                    color = get_color(row['color_key'])
                    if col_idx == 3: # Last step colors by source (Sector) or target (Gas)? Image uses Sector colors mostly
                         color = get_color(s_node)
                         # Special case: make the ribbons to right-side gases semi-transparent versions of the gas color?
                         # The image shows ribbons colored by the Category (Sector), flowing into the Gas.
                         pass

                    self.draw_ribbon(ax, 
                                     col_idx * self.x_spacing + self.width, 
                                     (col_idx + 1) * self.x_spacing, 
                                     y1_top, y1_bot, y2_top, y2_bot, 
                                     color)

        # Draw Nodes (Bars) and Labels
        for col_idx, col_nodes in self.nodes.items():
            for name, props in col_nodes.items():
                x = col_idx * self.x_spacing
                y = props['y_top']
                h = props['value']
                
                # Determine color
                color = get_color(name)
                if col_idx == 0 or col_idx == 4:
                    color = COLORS.get(name, '#333')
                
                # Draw Bar
                rect = patches.Rectangle((x, y), self.width, h, facecolor=color, edgecolor='black', linewidth=0.5, alpha=0.9)
                ax.add_patch(rect)
                
                # Add Label
                pct = (props['value'] / self.total_flux) * 100
                label_text = f"{name} ({pct:.0f}%)"
                
                # Clean up long names
                if "Ener for" in name: label_text = name.replace("Ener for", "Energy for") + f" ({pct:.0f}%)"
                if "Enteric" in name: label_text = f"Enteric ferment ({pct:.0f}%)"
                
                # Positioning logic
                text_x = x + self.width + 0.1
                ha = 'left'
                
                if col_idx == 4: # Rightmost labels inside or left
                    text_x = x + self.width + 0.1
                
                # Only label if significant enough to avoid clutter
                if h > self.total_flux * 0.005: 
                    ax.text(text_x, y + h/2, label_text, va='center', ha=ha, fontsize=8, fontweight='normal')

# 5. Main Execution
def main():
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]

    df = load_data()
    flows_df, total_flux = prepare_sankey_data(df)
    
    # Setup Plot
    fig, ax = plt.subplots(figsize=(20, 10))
    
    plotter = SankeyPlotter(flows_df, total_flux)
    plotter.calculate_layout()
    plotter.draw(ax)
    
    # Headers
    headers = ["Gases", "Sectors", "Stages", "Categories", ""]
    for i, h in enumerate(headers):
        ax.text(i * plotter.x_spacing, -plotter.total_flux * 0.05, h, fontsize=14, fontweight='bold')

    # Adjustments
    ax.set_xlim(-0.5, 4 * plotter.x_spacing + 2)
    # Invert Y axis so 0 is top
    ax.set_ylim(plotter.total_flux * 1.1, -plotter.total_flux * 0.1)
    ax.axis('off')
    
    # Add 'b' label
    ax.text(-0.5, -plotter.total_flux * 0.08, 'b', fontsize=20, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_file}")

if __name__ == "__main__":
    main()