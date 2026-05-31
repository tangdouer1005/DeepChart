import sys
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from scipy import stats

def generate_chart(output_filename):
    # 1. Load Source Data
    csv_data = """WT saline,WT K,A1ko saline,A1ko K,A2a ko saline,A2a ko K
48.1752,87.156,50.9091,63.3663,60,80.16
66.2921,81.6514,88.9831,39.6226,83.47,72.88
82.0513,62.5514,80.0781,61.9048,51.06,58.86
55.6391,60.9043,58.0524,60.7595,68.25,52.89
56.6901,83.5249,63.986,60.0746,57.25,66.97
88.3803,91.8182,71.1679,82.7206,43.1,60.5
62.0155,75.6477,64.2857,60.794,72,67.53
72.9167,73.4615,65.4762,63.7288,62.55,66.52
55.3719,67.2199,46.9055,40.0862,nan,nan
51.5038,74.4361,37.5,53.0351,nan,nan
62.5,66.6667,nan,nan,nan,nan
45.0237,79.3774,nan,nan,nan,nan
65.26,82.88,nan,nan,nan,nan
62.61,81.76,nan,nan,nan,nan
56.64,66.67,nan,nan,nan,nan
69.52,78.55,nan,nan,nan,nan
61.04,63.23,nan,nan,nan,nan
50.8,87.82,nan,nan,nan,nan
67.17,64.86,nan,nan,nan,nan"""

    df = pd.read_csv(io.StringIO(csv_data))

    # 2. Configuration
    # Column mapping order matches the chart left-to-right
    columns = ['WT saline', 'WT K', 'A1ko saline', 'A1ko K', 'A2a ko saline', 'A2a ko K']
    
    # Visual settings
    # Colors approximated from the image
    bar_colors = [
        '#000000', # WT Saline (Black)
        '#991f17', # WT K (Dark Red)
        '#454545', # A1ko Saline (Dark Grey)
        '#e8554e', # A1ko K (Salmon/Red)
        '#6b6b6b', # A2a Saline (Medium Grey)
        '#f08582'  # A2a K (Light Salmon)
    ]
    
    # X-axis positions with gaps between genotypes
    # Pairs: (0,1), (3,4), (6,7)
    x_positions = [0, 1, 3, 4, 6, 7]
    bar_width = 0.8
    
    # Initialize Plot
    fig, ax = plt.subplots(figsize=(7, 6))
    
    # 3. Plotting Logic
    max_y_val = 0 # To help position significance bars
    
    for i, col in enumerate(columns):
        # Extract valid data (remove NaNs)
        data = df[col].dropna().values
        
        # Calculate Statistics
        mean_val = np.mean(data)
        sem_val = np.std(data, ddof=1) / np.sqrt(len(data))
        
        # Update max for scaling
        max_data_point = np.max(data)
        if max_data_point > max_y_val:
            max_y_val = max_data_point
            
        # Draw Bar
        ax.bar(x_positions[i], mean_val, width=bar_width, color=bar_colors[i], 
               edgecolor=None, zorder=1)
        
        # Draw Error Bar (SEM)
        ax.errorbar(x_positions[i], mean_val, yerr=sem_val, fmt='none', 
                    ecolor='gray', capsize=5, elinewidth=1.5, markeredgewidth=1.5, zorder=2)
        
        # Draw Scatter Points (Jittered)
        # Create deterministic jitter for reproducibility
        np.random.seed(42 + i) 
        jitter = np.random.uniform(-0.15, 0.15, size=len(data))
        ax.scatter(np.full(len(data), x_positions[i]) + jitter, data, 
                   color='gray', s=20, alpha=0.9, zorder=3, edgecolors='none')

    # 4. Significance Annotations
    def draw_sig_line(x1, x2, y, text):
        line_y = y
        ax.plot([x1, x2], [line_y, line_y], color='black', linewidth=0.8)
        ax.text((x1 + x2) / 2, line_y + 1, text, ha='center', va='bottom', fontsize=12)

    # Determine height for significance lines (slightly above max data)
    sig_height = 105
    
    # Dynamic Calculation
    # Pairs: (col1_idx, col2_idx, x1_idx, x2_idx in x_positions)
    comparisons = [
        (0, 1, 0, 1),
        (2, 3, 2, 3),
        (4, 5, 4, 5)
    ]

    for c1, c2, x1, x2 in comparisons:
        d1 = df.iloc[:, c1].dropna()
        d2 = df.iloc[:, c2].dropna()
        t, p_val = stats.ttest_ind(d1, d2)
        
        if p_val < 0.001:
            sig_text = "***"
        elif p_val < 0.01:
            sig_text = "**"
        elif p_val < 0.05:
            sig_text = "*"
        else:
            sig_text = f"P = {p_val:.2f}"
            
        draw_sig_line(x_positions[x1], x_positions[x2], sig_height, sig_text)

    # 5. Axis Formatting
    
    # Y-Axis
    ax.set_ylabel("Sucrose preference (%)", fontsize=14, labelpad=10)
    ax.set_ylim(0, 115) # Extend slightly for annotations
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.tick_params(axis='y', labelsize=12, length=5)
    
    # Remove standard X-axis ticks/labels
    ax.set_xticks([])
    ax.set_xticklabels([])
    
    # Remove spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False) # We will draw custom lines
    
    # Add bottom axis line manually (only covering the data width if desired, or full)
    # The image has a standard bottom spine, let's keep it but hide ticks
    ax.spines['bottom'].set_visible(True)
    
    # 6. Custom X-Axis Table/Labels
    
    # Y-coordinates for labels (in data coordinates, negative values)
    y_crs = -8
    y_ket = -16
    y_geno_line = -22
    y_geno_text = -28
    
    # Row Labels
    ax.text(-1.5, y_crs, "CRS", ha='right', va='center', fontsize=12)
    ax.text(-1.5, y_ket, "Ketamine", ha='right', va='center', fontsize=12)
    
    # Column Labels (+ / -)
    labels_crs = ['+', '+', '+', '+', '+', '+']
    labels_ket = ['-', '+', '-', '+', '-', '+']
    
    for i, pos in enumerate(x_positions):
        ax.text(pos, y_crs, labels_crs[i], ha='center', va='center', fontsize=12)
        ax.text(pos, y_ket, labels_ket[i], ha='center', va='center', fontsize=12, fontweight='bold')

    # Genotype Grouping Lines and Labels
    # WT
    ax.plot([x_positions[0]-0.4, x_positions[1]+0.4], [y_geno_line, y_geno_line], color='black', linewidth=1, clip_on=False)
    ax.text((x_positions[0] + x_positions[1])/2, y_geno_text, "WT", ha='center', va='center', fontsize=12)
    
    # Adora1-/-
    ax.plot([x_positions[2]-0.4, x_positions[3]+0.4], [y_geno_line, y_geno_line], color='black', linewidth=1, clip_on=False)
    # Using LaTeX formatting for superscript
    ax.text((x_positions[2] + x_positions[3])/2, y_geno_text, r"$Adora1^{-/-}$", ha='center', va='center', fontsize=12)
    
    # Adora2a-/-
    ax.plot([x_positions[4]-0.4, x_positions[5]+0.4], [y_geno_line, y_geno_line], color='black', linewidth=1, clip_on=False)
    ax.text((x_positions[4] + x_positions[5])/2, y_geno_text, r"$Adora2a^{-/-}$", ha='center', va='center', fontsize=12)

    # 7. Figure Label "e"
    # Placed in figure coordinates relative to top-left
    ax.text(-0.15, 1.05, "e", transform=ax.transAxes, fontsize=18, fontweight='bold', va='top', ha='left')

    # Adjust layout to prevent clipping of bottom labels
    plt.subplots_adjust(bottom=0.2, left=0.15, right=0.95, top=0.9)

    # 8. Save Output
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    generate_chart(output_file)