import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.path as mpath
import matplotlib.colors as mcolors
import numpy as np

# ---------------------------------------------------------
# 1. Source Data Embedding
# ---------------------------------------------------------
csv_data = """left|right|NSF|NSFC
p_public health|t_machine learning|4|0
p_environmental conditions|t_machine learning|10|0
p_quality of life|t_machine learning|6|0
p_quality of life|t_internet of things|4|0
p_environmental conditions|t_internet of things|20|1
s_social sciences|p_environmental conditions|1|0
s_social sciences|p_equity|2|0
s_social sciences|p_gas emissions|3|0
p_environmental conditions|t_cloud computing|1|1
p_equity|t_cloud computing|4|0
p_gas emissions|t_cloud computing|3|1
p_environmental conditions|t_reinforcement learning|4|0
p_equity|t_reinforcement learning|4|0
p_gas emissions|t_reinforcement learning|9|0
p_resilience|t_machine learning|11|0
p_emergency response|t_machine learning|7|0
p_resilience|t_big data|6|5
p_emergency response|t_big data|7|8
s_urban systems|p_public safety|2|0
p_public safety|t_deep learning|2|0
p_public safety|t_cloud computing|1|0
p_equity|t_deep learning|2|0
p_environmental conditions|t_deep learning|1|6
p_resilience|t_wireless communication|2|0
p_equity|t_wireless communication|1|0
p_emergency response|t_wireless communication|1|0
p_resilience|t_cloud computing|2|0
p_emergency response|t_cloud computing|1|1
p_climate change|t_internet of things|4|0
p_climate change|t_big data|1|1
s_behavioral sciences|p_equity|2|0
p_equity|t_machine learning|8|0
s_mechanism|p_energy consumption|1|1
s_mechanism|p_quality of life|1|0
p_energy consumption|t_machine learning|7|0
s_control theory|p_quality of life|1|0
s_control theory|p_environmental conditions|1|0
s_control theory|p_digital divide|1|0
s_control theory|p_quality of services|1|0
s_control theory|p_traffic management|1|3
s_control theory|p_equity|1|0
p_digital divide|t_machine learning|1|0
p_quality of services|t_machine learning|3|0
p_traffic management|t_machine learning|10|0
p_quality of life|t_reinforcement learning|1|0
p_digital divide|t_reinforcement learning|1|0
p_quality of services|t_reinforcement learning|1|0
p_traffic management|t_reinforcement learning|6|0
p_gas emissions|t_self-driving|3|0
p_public health|t_deep learning|1|0
p_quality of services|t_self-driving|1|0
p_equity|t_self-driving|3|0
p_resilience|t_deep learning|5|0
p_climate change|t_deep learning|1|2
p_emergency response|t_deep learning|4|0
p_equity|t_big data|6|3
p_equity|t_internet of things|10|0
s_urban systems|p_resilience|4|0
s_human mobility|p_resilience|2|0
s_social sciences|p_information security|1|0
p_information security|t_internet of things|3|0
p_public safety|t_big data|2|2
p_information security|t_big data|2|2
p_public safety|t_unmanned aerial vehicle|1|0
p_information security|t_unmanned aerial vehicle|1|0
p_equity|t_unmanned aerial vehicle|1|0
p_traffic management|t_cloud computing|2|0
p_climate change|t_machine learning|3|0
p_quality of life|t_deep learning|2|0
p_quality of life|t_wireless communication|1|0
p_public health|t_internet of things|10|0
s_urban systems|p_equity|2|0
p_gas emissions|t_deep learning|3|0
p_gas emissions|t_machine learning|3|0
s_urban systems|p_traffic management|5|0
p_traffic management|t_self-driving|4|1
s_complexity sciences|p_energy consumption|2|0
s_complexity sciences|p_demand response|1|0
p_demand response|t_machine learning|3|0
p_resilience|t_virtual reality|1|0
p_climate change|t_virtual reality|1|0
p_equity|t_virtual reality|2|0
p_traffic management|t_deep learning|5|3
p_public health|t_digital twin|2|0
p_equity|t_digital twin|3|0
p_environmental conditions|t_digital twin|2|0
p_public health|t_big data|1|2
p_environmental conditions|t_big data|3|6
p_environmental conditions|t_wireless communication|3|1
p_quality of services|t_big data|1|4
p_resilience|t_internet of things|5|2
p_energy consumption|t_internet of things|1|0
p_digital divide|t_internet of things|5|0
p_energy consumption|t_cloud computing|3|0
p_digital divide|t_cloud computing|3|0
p_resilience|t_digital twin|2|0
p_climate change|t_digital twin|1|0
p_emergency response|t_digital twin|4|0
s_social sciences|p_quality of life|1|0
s_social sciences|p_covid-19 pandemic|1|0
p_quality of life|t_virtual reality|1|0
p_covid-19 pandemic|t_virtual reality|1|0
p_equity|t_explainable artificial intelligence|1|0
s_social sciences|p_traffic management|1|0
p_traffic management|t_internet of things|2|2
s_mechanism|p_covid-19 pandemic|1|0
p_covid-19 pandemic|t_wireless communication|2|0
s_complexity sciences|p_digital divide|1|0
s_urban morphology|p_digital divide|1|0
s_complexity sciences|p_environmental conditions|6|1
s_complexity sciences|p_resilience|1|0
s_complexity sciences|p_information security|1|0
p_information security|t_deep learning|1|0
s_urban systems|p_information security|2|0
s_urban systems|p_public health|2|0
s_human mobility|p_traffic management|0|13
p_traffic management|t_big data|0|29
p_sustainable development|t_big data|0|12
s_mechanism|p_resilience|0|3
s_mechanism|p_environmental conditions|0|3
p_sustainable development|t_deep learning|0|3
s_urban morphology|p_sustainable development|0|2
s_mechanism|p_sustainable development|0|2
p_sustainable development|t_machine learning|0|4
p_policy making|t_big data|0|4
s_human mobility|p_equity|0|1
s_mechanism|p_emergency response|0|5
s_urban morphology|p_traffic management|0|2
s_mechanism|p_gas emissions|0|5
p_gas emissions|t_big data|0|5
s_human mobility|p_public health|0|1
p_sustainable development|t_internet of things|0|1
s_human mobility|p_environmental conditions|0|1
s_human mobility|p_gas emissions|0|2
p_gas emissions|t_internet of things|0|1
s_mechanism|p_traffic management|0|3
s_complexity sciences|p_traffic management|0|8
p_quality of life|t_big data|0|1
s_complexity sciences|p_emergency response|0|6
s_mechanism|p_policy making|0|1
s_mechanism|p_quality of services|0|1
s_behavioral sciences|p_gas emissions|0|1
s_complexity sciences|p_rapid urbanization|0|1
p_rapid urbanization|t_big data|0|2
s_urban morphology|p_emergency response|0|1
s_urban morphology|p_energy consumption|0|1
p_energy consumption|t_deep learning|0|2
p_energy consumption|t_self-driving|0|1
s_mechanism|p_climate change|0|1
s_complexity sciences|p_sustainable development|0|1"""

# ---------------------------------------------------------
# 2. Data Processing
# ---------------------------------------------------------

# Load data
df = pd.read_csv(io.StringIO(csv_data), sep="|")

# Clean whitespace
df.columns = df.columns.str.strip()
df['left'] = df['left'].str.strip()
df['right'] = df['right'].str.strip()

# Calculate metrics
df['Total'] = df['NSF'] + df['NSFC']
df['Ratio'] = df['NSF'] / df['Total']

# Label Mapping to match the chart image exactly
label_map = {
    's_human mobility': 'Human mobility',
    's_complexity sciences': 'Complexity sciences',
    's_urban morphology': 'Urban morphology',
    's_mechanism': 'Mechanism',
    's_control theory': 'Control theory',
    's_urban systems': 'Urban systems',
    's_social sciences': 'Social sciences',
    's_behavioral sciences': 'Behavioral sciences',
    
    'p_traffic management': 'Traffic management',
    'p_rapid urbanization': 'Rapid urbanization',
    'p_policy making': 'Policy-making',
    'p_sustainable development': 'Sustainable development',
    'p_emergency response': 'Emergency response',
    'p_environmental conditions': 'Environmental conditions',
    'p_gas emissions': 'Gas emissions',
    'p_quality of services': 'Quality of services',
    'p_resilience': 'Resilience',
    'p_demand response': 'Demand response',
    'p_energy consumption': 'Energy consumption',
    'p_public safety': 'Public safety',
    'p_information security': 'Information security',
    'p_equity': 'Equity',
    'p_climate change': 'Climate change',
    'p_public health': 'Public health',
    'p_digital divide': 'Digital divide',
    'p_quality of life': 'Quality of life',
    'p_covid-19 pandemic': 'COVID-19 pandemic',
    
    't_big data': 'Big data',
    't_self-driving': 'Self-driving',
    't_reinforcement learning': 'Reinforcement learning',
    't_deep learning': 'Deep learning',
    't_machine learning': 'Machine learning',
    't_cloud computing': 'Cloud computing',
    't_digital twin': 'Digital twin',
    't_internet of things': 'Internet of Things',
    't_wireless communication': 'Wireless communication',
    't_unmanned aerial vehicle': 'Unmanned aerial vehicle',
    't_explainable artificial intelligence': 'Explainable AI',
    't_virtual reality': 'Virtual reality'
}

# Apply mapping
df['left_label'] = df['left'].map(label_map)
df['right_label'] = df['right'].map(label_map)

# Split into two stages
# Stage 1: Science (s_) to Problems (p_)
df_stage1 = df[df['left'].str.startswith('s_')].copy()
# Stage 2: Problems (p_) to Technology (t_)
df_stage2 = df[df['right'].str.startswith('t_')].copy()

# ---------------------------------------------------------
# 3. Layout Configuration
# ---------------------------------------------------------

# Define explicit order based on the chart image
order_left = [
    'Human mobility', 'Complexity sciences', 'Urban morphology', 'Mechanism',
    'Control theory', 'Urban systems', 'Social sciences', 'Behavioral sciences'
]

order_mid = [
    'Traffic management', 'Rapid urbanization', 'Policy-making', 'Sustainable development',
    'Emergency response', 'Environmental conditions', 'Gas emissions', 'Quality of services',
    'Resilience', 'Demand response', 'Energy consumption', 'Public safety',
    'Information security', 'Equity', 'Climate change', 'Public health',
    'Digital divide', 'Quality of life', 'COVID-19 pandemic'
]

order_right = [
    'Big data', 'Self-driving', 'Reinforcement learning', 'Deep learning',
    'Machine learning', 'Cloud computing', 'Digital twin', 'Internet of Things',
    'Wireless communication', 'Unmanned aerial vehicle', 'Explainable AI', 'Virtual reality'
]

# Calculate node sizes (heights)
# For middle nodes, height is max(input_sum, output_sum)
node_sizes = {}

# Left nodes (only outputs)
left_sums = df_stage1.groupby('left_label')['Total'].sum()
for node in order_left:
    node_sizes[node] = left_sums.get(node, 0)

# Right nodes (only inputs)
right_sums = df_stage2.groupby('right_label')['Total'].sum()
for node in order_right:
    node_sizes[node] = right_sums.get(node, 0)

# Middle nodes (inputs from left, outputs to right)
mid_inputs = df_stage1.groupby('right_label')['Total'].sum()
mid_outputs = df_stage2.groupby('left_label')['Total'].sum()

for node in order_mid:
    inp = mid_inputs.get(node, 0)
    out = mid_outputs.get(node, 0)
    node_sizes[node] = max(inp, out)

# ---------------------------------------------------------
# 4. Plotting Logic
# ---------------------------------------------------------

def get_node_positions(order_list, sizes, gap, y_start_offset=0):
    positions = {}
    current_y = y_start_offset
    # We draw from top to bottom, but matplotlib coordinates are bottom-up.
    # However, it's easier to calculate "distance from top" and then invert or subtract.
    # Let's calculate cumulative height and place nodes.
    
    # Calculate total height needed
    total_content_height = sum([sizes[n] for n in order_list]) + gap * (len(order_list) - 1)
    
    current_y = total_content_height # Start at top
    
    pos_map = {}
    for node in order_list:
        h = sizes[node]
        # Position is the bottom of the bar
        pos_map[node] = current_y - h
        current_y -= (h + gap)
    
    return pos_map, total_content_height

# Parameters
GAP = 2.0  # Gap between nodes
WIDTH_NODE = 0.5 # Width of the grey bars
X_LEFT, X_MID, X_RIGHT = 0, 10, 20

# Calculate positions
# We align the columns roughly by center or top. The chart looks fairly centered.
# Let's calculate heights first.
_, h_left = get_node_positions(order_left, node_sizes, GAP)
_, h_mid = get_node_positions(order_mid, node_sizes, GAP)
_, h_right = get_node_positions(order_right, node_sizes, GAP)

max_h = max(h_left, h_mid, h_right)

# Center vertically
offset_left = (max_h - h_left) / 2
offset_mid = (max_h - h_mid) / 2
offset_right = (max_h - h_right) / 2

# Recalculate with offsets (centering logic)
# Actually, looking at the chart, "Human Mobility" (top left) aligns roughly with "Traffic" (top mid).
# "Behavioral" (bottom left) is much higher than "Covid" (bottom mid).
# It seems top-aligned or loosely aligned. Let's try centering the whole block first.
pos_left, _ = get_node_positions(order_left, node_sizes, GAP)
pos_mid, _ = get_node_positions(order_mid, node_sizes, GAP)
pos_right, _ = get_node_positions(order_right, node_sizes, GAP)

# Adjust offsets to center relative to the tallest column (Middle)
# Shift left and right to align centers with middle
mid_center = h_mid / 2
left_center = h_left / 2
right_center = h_right / 2

# Apply shifts
for k in pos_left: pos_left[k] += (mid_center - left_center)
for k in pos_right: pos_right[k] += (mid_center - right_center)
# Middle stays as is (or shift all up/down to fit in view)

# Create Color Map
# Orange (0) -> Grey (0.5) -> Blue (1.0)
colors = ["#e69f00", "#f0f0f0", "#56b4e9"] # Orange, Light Grey, Blue
cmap = mcolors.LinearSegmentedColormap.from_list("custom_diverging", colors)

# Initialize Figure
fig, ax = plt.subplots(figsize=(16, 18))
ax.axis('off')

# Track current y-position for links within each node
# Since we draw top-down in logic but coords are bottom-up, 
# and we calculated pos as the *bottom* of the node:
# The "top" of a node is pos[node] + node_sizes[node].
# We fill from Top to Bottom.
cursor_left_out = {n: pos_left[n] + node_sizes[n] for n in order_left}
cursor_mid_in = {n: pos_mid[n] + node_sizes[n] for n in order_mid}
cursor_mid_out = {n: pos_mid[n] + node_sizes[n] for n in order_mid}
cursor_right_in = {n: pos_right[n] + node_sizes[n] for n in order_right}

# Helper to draw sigmoid link
def draw_link(ax, x1, x2, y1_top, y2_top, width, color, alpha=0.6):
    if width <= 0: return
    
    y1_bot = y1_top - width
    y2_bot = y2_top - width
    
    mid_x = (x1 + x2) / 2
    
    # Bezier control points
    # P0: (x1, y1_top)
    # P1: (mid_x, y1_top)
    # P2: (mid_x, y2_top)
    # P3: (x2, y2_top)
    
    verts = [
        (x1, y1_top),
        (mid_x, y1_top),
        (mid_x, y2_top),
        (x2, y2_top),
        (x2, y2_bot),
        (mid_x, y2_bot),
        (mid_x, y1_bot),
        (x1, y1_bot),
        (x1, y1_top)
    ]
    
    codes = [
        mpath.Path.MOVETO,
        mpath.Path.CURVE4,
        mpath.Path.CURVE4,
        mpath.Path.CURVE4,
        mpath.Path.LINETO,
        mpath.Path.CURVE4,
        mpath.Path.CURVE4,
        mpath.Path.CURVE4,
        mpath.Path.CLOSEPOLY
    ]
    
    path = mpath.Path(verts, codes)
    patch = patches.PathPatch(path, facecolor=color, edgecolor='none', alpha=alpha)
    ax.add_patch(patch)

# ---------------------------------------------------------
# 5. Draw Links
# ---------------------------------------------------------

# Draw Stage 1: Left -> Mid
# Sort links to minimize crossing? Or just iterate.
# Usually, sorting by target index helps.
df_stage1['target_rank'] = df_stage1['right_label'].apply(lambda x: order_mid.index(x) if x in order_mid else 999)
df_stage1_sorted = df_stage1.sort_values(by=['left_label', 'target_rank'])

for _, row in df_stage1_sorted.iterrows():
    src = row['left_label']
    dst = row['right_label']
    w = row['Total']
    ratio = row['Ratio']
    
    if src in pos_left and dst in pos_mid:
        y_src = cursor_left_out[src]
        y_dst = cursor_mid_in[dst]
        
        col = cmap(ratio)
        
        draw_link(ax, X_LEFT + WIDTH_NODE, X_MID, y_src, y_dst, w, col)
        
        cursor_left_out[src] -= w
        cursor_mid_in[dst] -= w

# Draw Stage 2: Mid -> Right
df_stage2['target_rank'] = df_stage2['right_label'].apply(lambda x: order_right.index(x) if x in order_right else 999)
# For the source side (mid), we want to maintain the flow logic if possible, 
# but standard Sankey just stacks.
df_stage2_sorted = df_stage2.sort_values(by=['left_label', 'target_rank'])

for _, row in df_stage2_sorted.iterrows():
    src = row['left_label']
    dst = row['right_label']
    w = row['Total']
    ratio = row['Ratio']
    
    if src in pos_mid and dst in pos_right:
        y_src = cursor_mid_out[src]
        y_dst = cursor_right_in[dst]
        
        col = cmap(ratio)
        
        draw_link(ax, X_MID + WIDTH_NODE, X_RIGHT, y_src, y_dst, w, col)
        
        cursor_mid_out[src] -= w
        cursor_right_in[dst] -= w

# ---------------------------------------------------------
# 6. Draw Nodes and Labels
# ---------------------------------------------------------

def draw_nodes(pos_map, sizes, x_pos, align='left'):
    for node, y_bot in pos_map.items():
        h = sizes[node]
        # Draw bar
        rect = patches.Rectangle((x_pos, y_bot), WIDTH_NODE, h, 
                                 linewidth=0, facecolor='#a0a0a0', alpha=0.8)
        ax.add_patch(rect)
        
        # Draw Label
        if align == 'left':
            # Text to the right of the bar (for Left column, actually text is inside/left? 
            # Image: Left col text is inside/left. Right col text is inside/right.
            # Actually, looking at image:
            # Left Col: Text is on the right of the bar? No, text is on the bar or just right of it.
            # Wait, the image has text *inside* the flow area for the left column?
            # No, "Human mobility" is to the right of the grey bar.
            # "Traffic management" is to the right of the grey bar.
            # "Big data" is to the left of the grey bar.
            
            # Let's stick to:
            # Left Col: Text starts at x + width + padding
            # Mid Col: Text starts at x + width + padding
            # Right Col: Text ends at x - padding
            
            ax.text(x_pos + WIDTH_NODE + 0.2, y_bot + h/2, node, 
                    va='center', ha='left', fontsize=11, color='black')
        elif align == 'mid':
             ax.text(x_pos + WIDTH_NODE + 0.2, y_bot + h/2, node, 
                    va='center', ha='left', fontsize=11, color='black')
        else: # right
             ax.text(x_pos - 0.2, y_bot + h/2, node, 
                    va='center', ha='right', fontsize=11, color='black')

draw_nodes(pos_left, node_sizes, X_LEFT, align='left')
draw_nodes(pos_mid, node_sizes, X_MID, align='mid')
draw_nodes(pos_right, node_sizes, X_RIGHT, align='right')

# Column Titles
y_max = max_h + 5 # slightly above
ax.text(X_LEFT, y_max, "Urban science", fontsize=14, ha='left')
ax.text(X_MID + WIDTH_NODE/2, y_max, "Real-world problems", fontsize=14, ha='center')
ax.text(X_RIGHT + WIDTH_NODE, y_max, "Urban technology", fontsize=14, ha='right')

# ---------------------------------------------------------
# 7. Colorbar
# ---------------------------------------------------------
# Create an inset axes for the colorbar at the bottom
cbar_ax = fig.add_axes([0.3, 0.05, 0.4, 0.02]) # [left, bottom, width, height]
norm = mcolors.Normalize(vmin=0, vmax=1)
cb = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cbar_ax, orientation='horizontal')
cb.set_label('Proportion of NSF-funded proposals', fontsize=12)
cb.outline.set_visible(False)

# Adjust plot limits
ax.set_xlim(X_LEFT, X_RIGHT + WIDTH_NODE)
ax.set_ylim(min(pos_right.values()) - 5, y_max + 2)
# Invert Y axis so 0 is at bottom? No, we calculated manually.
# Just ensure aspect ratio is okay.

# ---------------------------------------------------------
# 8. Save Output
# ---------------------------------------------------------
output_file = "output.png"
if len(sys.argv) > 1:
    output_file = sys.argv[1]

plt.savefig(output_file, bbox_inches='tight', dpi=300)