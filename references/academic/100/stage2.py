import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def generate_chart(output_filename):
    # 1. Data Preparation
    # Extracted directly from the provided Markdown table under "Glutathione disulfide"
    # and mapped to the groups shown in Fig 2h.
    
    data = {
        'B16-F0':     [21863.71235, 24875.51896, 22016.88534, 25814.18798, 27246.77866],
        'LN1-18IL':   [18036.00176, 18830.57124, 19307.19433, 16733.69258, 16079.18642, 17297.56782],
        'LN7-1112AR': [5248.194658, 4320.354879, 15541.98794],
        'LN7-1120BL': [13139.91358, 14483.39718, 13964.36330],
        'LN7-1134BL': [10780.69564, 8743.865759, 13898.34151],
        'LN8-1194BR': [10198.56842, 12314.92301, 11617.38643],
        'LN8-1198AR': [17421.54825, 15474.15213, 16688.72750],
        'LN8-1205BL': [14176.33743, 13151.32158, 15637.46513],
        'LN9-1315BL': [14238.32810, 13632.08987, 13037.78140],
        'LN9-1358IR': [14076.18123, 13737.78268, 14613.45740]
    }

    # P-values extracted from the image and the "Table Analyzed: Fig 2h" section
    p_values = [
        None, # B16-F0
        None, # LN1-18IL
        r"$P = 6.7 \times 10^{-9}$", # LN7-1112AR
        r"$P = 1.2 \times 10^{-5}$", # LN7-1120BL
        r"$P = 2.5 \times 10^{-7}$", # LN7-1134BL
        r"$P = 3.4 \times 10^{-7}$", # LN8-1194BR
        r"$P = 0.0007$",             # LN8-1198AR
        r"$P = 2.4 \times 10^{-5}$", # LN8-1205BL
        r"$P = 8.6 \times 10^{-6}$", # LN9-1315BL
        r"$P = 1.8 \times 10^{-5}$"  # LN9-1358IR
    ]

    groups = list(data.keys())
    means = [np.mean(data[g]) for g in groups]
    stds = [np.std(data[g], ddof=1) for g in groups] # Using Sample SD

    # 2. Plot Setup
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Colors
    bar_colors = ['#d9d9d9', '#f0b0f0'] + ['#90cf90'] * 8  # Gray, Pink, Greens
    edge_colors = ['black'] * 10
    scatter_colors = ['black', 'black'] + ['#1e7145'] * 8 # Black for first two, Dark Green for rest

    x_pos = np.arange(len(groups))

    # 3. Draw Bars
    bars = ax.bar(x_pos, means, yerr=stds, align='center', 
                  color=bar_colors, edgecolor=edge_colors, 
                  capsize=5, width=0.7, linewidth=1, 
                  error_kw={'elinewidth': 1, 'ecolor': 'black', 'capthick': 1})

    # 4. Draw Scatter Points (Individual Data)
    np.random.seed(42) # For reproducible jitter
    for i, group in enumerate(groups):
        y_vals = data[group]
        # Add slight jitter to x
        x_vals = np.random.normal(i, 0.04, size=len(y_vals))
        ax.scatter(x_vals, y_vals, color=scatter_colors[i], s=30, zorder=10, edgecolors='none')

    # 5. Annotations (P-values)
    
    # Global P-value line
    line_y = 31000
    ax.plot([0, 9], [line_y, line_y], color='black', linewidth=0.8)
    ax.text(4.5, line_y + 500, r"$P = 4.5 \times 10^{-8}$", ha='center', va='bottom', fontsize=12)

    # Individual vertical P-values
    # Based on the image, these start from the 3rd bar and are positioned vertically
    for i, p_val in enumerate(p_values):
        if p_val:
            # Position text vertically rotated
            # The height in the image is roughly consistent, slightly staggered or high up
            text_y_start = 20000 
            ax.text(i, text_y_start, p_val, rotation=90, ha='center', va='bottom', fontsize=10)

    # 6. Formatting
    
    # Axes Labels
    ax.set_ylabel('GSSG peak intensity', fontsize=12)
    
    # X-Axis Ticks
    ax.set_xticks(x_pos)
    ax.set_xticklabels(groups, rotation=45, ha='right', fontsize=11)
    
    # Y-Axis Ticks (Custom formatting to match 1 x 10^4 style)
    ax.set_ylim(0, 33000)
    yticks = [0, 10000, 20000, 30000]
    ytick_labels = ['0', r'$1 \times 10^4$', r'$2 \times 10^4$', r'$3 \times 10^4$']
    ax.set_yticks(yticks)
    ax.set_yticklabels(ytick_labels, fontsize=11)

    # Spines (Remove top and right)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add 'h' label in top left corner
    fig.text(0.02, 0.95, 'h', fontsize=24, fontweight='bold')

    # Adjust layout to prevent clipping of x-labels
    plt.tight_layout()
    
    # Save
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)