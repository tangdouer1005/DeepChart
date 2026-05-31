import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

def generate_chart(output_filename):
    # ---------------------------------------------------------
    # 1. Source Data Preparation
    # ---------------------------------------------------------
    # Raw data extracted from Columns 0-9 of the provided table.
    # 'nan' values are represented as np.nan
    raw_data = {
        'B16-F0': [0.999999823, 1.00032767, 1.000005438, 0.861667086, 1.003190644, 1.136074996, 0.999999998],
        'LN1-18IL': [0.800686, 1.500677, 1.341806, 1.640613, 1.483361, 1.106523, 0.813898],
        'LN7-1112AR': [0.587407, 0.932256, 0.847907, 0.563434468, np.nan, np.nan, np.nan],
        'LN7-1120BL': [1.054753, 1.447167, 1.117306, np.nan, np.nan, np.nan, np.nan],
        'LN7-1134BL': [0.270697051, 0.731263444, 0.744321601, 0.463934401, np.nan, np.nan, np.nan],
        'LN8-1194BR': [0.179749188, 0.782426964, 0.479145444, np.nan, np.nan, np.nan, np.nan],
        'LN8-1198AR': [0.70873371, 1.548417104, 1.414139626, np.nan, np.nan, np.nan, np.nan],
        'LN8-1205BL': [0.485153079, 1.03000271, 0.782000195, np.nan, np.nan, np.nan, np.nan],
        'LN9-1315BL': [0.492599693, 0.953486003, 0.618357257, 0.371824586, 0.625783402, 0.705343274, 0.451463534],
        'LN9-1358IR': [0.33207914, 0.455197984, 0.453811153, 0.537530998, 0.160409973, 0.327652464, 0.318659655]
    }

    # P-values extracted from the "Adjusted P Value" column in the table.
    # Note: The chart does not show a P-value for LN1-18IL.
    p_values = {
        'LN7-1112AR': 0.4237,
        'LN7-1120BL': 0.7995,
        'LN7-1134BL': 0.0342,
        'LN8-1194BR': 0.0225,
        'LN8-1198AR': 0.7291,
        'LN8-1205BL': 0.6822,
        'LN9-1315BL': 0.0249,
        'LN9-1358IR': 0.0001
    }

    groups = list(raw_data.keys())
    
    # Calculate Mean and Std Dev for plotting
    means = []
    stds = []
    clean_data_points = []

    for g in groups:
        # Filter out NaNs
        data = [x for x in raw_data[g] if not np.isnan(x)]
        clean_data_points.append(data)
        means.append(np.mean(data))
        stds.append(np.std(data, ddof=1)) # Sample standard deviation

    # ---------------------------------------------------------
    # 2. Plotting Setup
    # ---------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 6))
    
    # Styling constants
    bar_width = 0.65
    color_control = '#D9D9D9'  # Light Grey
    color_ln1 = '#E6A5E9'      # Light Pink/Orchid
    color_others = '#8CC685'   # Muted Green
    edge_color = 'black'
    scatter_color = '#222222'  # Dark grey/black for points
    
    # Assign colors based on group index
    colors = []
    for i, group in enumerate(groups):
        if i == 0:
            colors.append(color_control)
        elif i == 1:
            colors.append(color_ln1)
        else:
            colors.append(color_others)

    x_pos = np.arange(len(groups))

    # ---------------------------------------------------------
    # 3. Draw Bars and Error Bars
    # ---------------------------------------------------------
    ax.bar(x_pos, means, width=bar_width, color=colors, edgecolor=edge_color, 
           linewidth=1.0, zorder=1)

    # Draw Error Bars (Standard Deviation)
    # capsize creates the horizontal lines at the end of error bars
    ax.errorbar(x_pos, means, yerr=stds, fmt='none', ecolor='black', 
                elinewidth=1.2, capsize=4, capthick=1.2, zorder=2)

    # ---------------------------------------------------------
    # 4. Draw Scatter Points (Jittered)
    # ---------------------------------------------------------
    np.random.seed(42) # For reproducibility
    jitter_strength = 0.15
    
    for i, points in enumerate(clean_data_points):
        # Create random x-offsets for the swarm effect
        x_jitter = np.random.uniform(-jitter_strength, jitter_strength, size=len(points))
        ax.scatter(x_pos[i] + x_jitter, points, color=scatter_color, s=30, zorder=3, edgecolors='none')

    # ---------------------------------------------------------
    # 5. Annotations (P-values and Significance Line)
    # ---------------------------------------------------------
    
    # Add vertical P-value text above the green bars
    # We position them slightly above the max of the error bar or a fixed height
    # Looking at the chart, they are aligned at varying heights but generally high up.
    # To match the chart exactly, we place them vertically.
    
    text_y_start = 1.8 # Base height for text
    
    for i, group in enumerate(groups):
        if group in p_values:
            p_val = p_values[group]
            p_text = f"P = {p_val:.4f}"
            
            # Determine height: slightly above the error bar, but ensure a minimum height for alignment
            # The chart shows them aligned nicely. Let's put them at a fixed height relative to the bar
            # or just above the bar. The chart has them "floating" quite high.
            
            # Let's use a fixed Y position for the text to look uniform, 
            # or dynamic based on the bar height if they vary wildly.
            # In the image, they seem to start around y=1.8 to 2.0
            
            ax.text(i, 1.85, p_text, rotation=90, ha='center', va='bottom', fontsize=10, color='#333333')

    # Add the top significance line and overall ANOVA P-value
    # The line spans from the second bar (LN1-18IL) to the last bar.
    line_start_idx = 1
    line_end_idx = len(groups) - 1
    line_y = 2.7
    
    ax.plot([line_start_idx, line_end_idx], [line_y, line_y], color='black', linewidth=1.0)
    
    # Add the overall P-value text centered above the line
    # Chart header: P = 2 x 10^-7
    ax.text((line_start_idx + line_end_idx) / 2, line_y + 0.05, 
            r'$P = 2 \times 10^{-7}$', ha='center', va='bottom', fontsize=12)

    # Add Figure label "i"
    ax.text(-0.15, 1.05, 'i', transform=ax.transAxes, fontsize=20, fontweight='bold', va='top', ha='right')

    # ---------------------------------------------------------
    # 6. Formatting Axes and Layout
    # ---------------------------------------------------------
    
    # Y-Axis
    ax.set_ylabel('Relative GPX4 levels', fontsize=14, labelpad=10)
    ax.set_ylim(0, 3.0) # Set limit to accommodate annotations
    ax.set_yticks(np.arange(0, 2.6, 0.5))
    ax.tick_params(axis='y', labelsize=12, length=5)
    
    # X-Axis
    ax.set_xticks(x_pos)
    ax.set_xticklabels(groups, rotation=45, ha='right', fontsize=12)
    ax.tick_params(axis='x', length=0) # Hide x ticks marks, keep labels

    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Adjust layout to prevent clipping of rotated labels
    plt.tight_layout()
    
    # Save output
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)