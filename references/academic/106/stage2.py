import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

def generate_chart(output_filename):
    # ---------------------------------------------------------
    # 1. Data Preparation
    # ---------------------------------------------------------
    # Raw data extracted directly from the provided Markdown table
    data_dict = {
        'B16-F0 21%O2': [1, 1, 1, 1],
        'B16-F0 1%O2': [1.48403264, 1.68837926, 1.21210873, 1.34768451],
        'B16-F0 1%O2 + Liprox': [1.34308934, 1.43866036, 1.32754921, np.nan],
        
        'B16-F0 FSP1 KO 21%O2': [1, 1, 1, 1],
        'B16-F0 FSP1 KO 1%O2': [2.13260939, 2.40660031, 1.73214387, 1.75709602],
        'B16-F0 FSP1 KO 1%O2 + Liprox': [1.19117817, 1.18719077, 1.18639812, np.nan],
        
        'LN71134BL 21%O2': [1, 1, 1, 1],
        'LN71134BL 1%O2': [2.25799359, 1.9494307, 1.90228148, 2.19323958],
        'LN71134BL 1%O2 + Liprox': [1.15397846, 1.40481629, 1.449258435, np.nan],
        
        'LN71134BL FSP1 KO 21%O2': [1, 1, 1, 1],
        'LN71134BL FSP1 KO 1%O2': [2.78758832, 2.77704055, 2.66783802, 2.87541627],
        'LN71134BL FSP1 KO 1%O2 + Liprox': [1.23286389, 1.24515659, 1.036090783, np.nan]
    }

    # Convert to list of arrays, filtering nans
    data_values = []
    for key in data_dict:
        clean_vals = [x for x in data_dict[key] if not np.isnan(x)]
        data_values.append(clean_vals)

    # Calculate stats
    means = [np.mean(d) for d in data_values]
    stds = [np.std(d, ddof=1) if len(d) > 1 else 0 for d in data_values] # Sample SD

    # ---------------------------------------------------------
    # 2. Plot Configuration
    # ---------------------------------------------------------
    
    # Define Colors (Approximated from image)
    # Groups: B16 WT, B16 KO, LN7 WT, LN7 KO
    # Within group: 21% (Dark), 1% (Light/Color), Liprox (Pale/Greyish)
    colors = [
        # B16-F0 WT
        '#000000', # Black
        '#FFFFFF', # White
        '#A9A9A9', # Grey
        
        # B16-F0 FSP1 KO
        '#654321', # Dark Brown
        '#C2B280', # Tan/Sand
        '#E6DCC3', # Beige
        
        # LN7-1134BL WT
        '#2E8B57', # SeaGreen
        '#5F9EA0', # CadetBlue/Teal
        '#B0E0E6', # PowderBlue/LightTeal
        
        # LN7-1134BL FSP1 KO
        '#1E90FF', # DodgerBlue
        '#87CEFA', # LightSkyBlue
        '#E0FFFF'  # LightCyan
    ]

    edge_colors = ['black'] * 12
    
    # Scatter point colors (match bar edge or specific style)
    # In the image, points are open circles. 
    # For colored bars, points often match the color family or are black.
    # We will use black edges for points on light bars, and white/colored for dark bars?
    # Actually, looking closely:
    # Bar 1 (Black): Points are grey/white? Hard to see, usually 1.0.
    # Bar 2 (White): Black open circles.
    # Bar 4 (Brown): Brown open circles.
    # Let's use the bar color for the marker edge, unless it's white/black.
    marker_colors = []
    for c in colors:
        if c == '#FFFFFF': marker_colors.append('black')
        elif c == '#000000': marker_colors.append('gray') 
        else: marker_colors.append('black') # Use black outlines for visibility as per standard scientific plots

    # Bar Positions with spacing between groups
    # Groups of 3, gap of 1
    indices = [0, 1, 2,  4, 5, 6,  8, 9, 10,  12, 13, 14]
    
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # ---------------------------------------------------------
    # 3. Drawing the Chart
    # ---------------------------------------------------------
    
    # Bars
    bars = ax.bar(indices, means, width=0.8, color=colors, edgecolor='black', linewidth=1.2, capsize=5)

    # Error Bars
    ax.errorbar(indices, means, yerr=stds, fmt='none', ecolor='black', capsize=5, elinewidth=1.2, capthick=1.2)

    # Scatter Points (Jittered)
    np.random.seed(42) # For reproducible jitter
    for i, (x_pos, vals) in enumerate(zip(indices, data_values)):
        # Create jitter
        jitter = np.random.uniform(-0.1, 0.1, size=len(vals))
        
        # Determine marker style
        # The image uses open circles.
        # For the black bar, points are barely visible, likely grey.
        # For the white bar, points are black.
        # For colored bars, points seem to have black edges.
        m_edge = 'black'
        if i == 0: m_edge = 'gray' # Visibility on black
        
        ax.scatter(np.array([x_pos]*len(vals)) + jitter, vals, 
                   zorder=10, color='none', edgecolor=m_edge, s=60, linewidth=1.2)

    # ---------------------------------------------------------
    # 4. Statistical Annotations
    # ---------------------------------------------------------
    # Helper to draw significance lines
    def draw_sig_line(idx1, idx2, p_text, y_offset_scale=0.1):
        x1, x2 = indices[idx1], indices[idx2]
        # Find max y in this range to place the line above
        y_max = max(means[idx1] + stds[idx1], means[idx2] + stds[idx2])
        
        # Specific adjustments based on visual height in original chart
        if idx1 == 0: y_h = 2.0
        elif idx1 == 3: y_h = 2.9
        elif idx1 == 6: y_h = 2.9
        elif idx1 == 9: y_h = 3.4
        else: y_h = y_max + 0.2

        line_h = 0.05
        
        # Draw line
        ax.plot([x1, x2], [y_h, y_h], color='black', linewidth=1.2)
        
        # Add text
        ax.text((x1+x2)/2, y_h + 0.05, p_text, ha='center', va='bottom', fontsize=12, color='black')

    # P-values from source data
    draw_sig_line(0, 1, r'$P = 0.1667$')
    draw_sig_line(3, 4, r'$P = 0.0115$')
    draw_sig_line(6, 7, r'$P = 0.0078$')
    draw_sig_line(9, 10, r'$P = 0.0007$')

    # ---------------------------------------------------------
    # 5. Axis Formatting & Labels
    # ---------------------------------------------------------
    
    # Y Axis
    ax.set_ylabel('BODIPY$_{ox}$/BODIPY$_{red}$\n(relative to 21% O$_2$)', fontsize=14, labelpad=10)
    ax.set_ylim(0, 4)
    ax.set_yticks([0, 1, 2, 3, 4])
    ax.tick_params(axis='y', labelsize=12, length=6)
    
    # Remove default X ticks
    ax.set_xticks([])
    ax.set_xticklabels([])
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.2)
    ax.spines['bottom'].set_linewidth(1.2)

    # ---------------------------------------------------------
    # 6. Custom X-Axis Table/Labels
    # ---------------------------------------------------------
    
    # Define the table content
    # Rows: 21% O2, 1% O2, Liproxstatin-1
    # Columns correspond to the 12 bars
    row_labels = ['21% O$_2$', '1% O$_2$', 'Liproxstatin-1']
    
    # Pattern logic:
    # Bar 1: +, -, -
    # Bar 2: -, +, -
    # Bar 3: -, +, +
    # Repeated for each group
    
    table_data = []
    for _ in range(4): # 4 groups
        table_data.extend([
            ['+', '-', '-'],
            ['-', '+', '-'],
            ['-', '+', '+']
        ])
    
    # Transpose to iterate by row
    table_rows = list(zip(*table_data)) # 3 rows, 12 cols
    
    # Y-positions for the table text (relative to axes coordinates, negative)
    y_start = -0.08
    y_step = 0.05
    
    # Add row labels (right side)
    for i, label in enumerate(row_labels):
        y_pos = y_start - (i * y_step)
        ax.text(15.5, y_pos, label, ha='left', va='center', fontsize=12)

    # Add +/- signs
    for r_idx, row in enumerate(table_rows):
        y_pos = y_start - (r_idx * y_step)
        for c_idx, val in enumerate(row):
            x_pos = indices[c_idx]
            # Bold font for visibility
            fw = 'bold' if val == '+' else 'normal'
            ax.text(x_pos, y_pos, val, ha='center', va='center', fontsize=12, fontweight=fw)

    # Add Group Labels (Bottom)
    group_labels = [
        "B16-F0\nWT", 
        "B16-F0\nFsp1 KO", 
        "LN7-1134BL\nWT", 
        "LN7-1134BL\nFsp1 KO"
    ]
    
    # Calculate center of each group
    group_centers = [1, 5, 9, 13]
    
    # Draw lines separating groups and table
    # Line above group names
    line_y = y_start - (3 * y_step) - 0.02
    
    # Draw horizontal lines for groups
    for i, center in enumerate(group_centers):
        # Line width covers the 3 bars (approx width 2.4 units)
        ax.plot([center - 1.2, center + 1.2], [line_y, line_y], color='black', linewidth=1, clip_on=False)
        
        # Text
        ax.text(center, line_y - 0.02, group_labels[i], ha='center', va='top', fontsize=12, rotation=45)

    # Add 'c' label in top left corner
    fig.text(0.02, 0.95, 'c', fontsize=24, fontweight='bold')

    # Adjust layout to make room for the bottom table
    plt.subplots_adjust(bottom=0.3, right=0.85, left=0.1)

    # ---------------------------------------------------------
    # 7. Save Output
    # ---------------------------------------------------------
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    generate_chart(output_file)