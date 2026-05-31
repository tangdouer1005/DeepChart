import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

def generate_chart(output_filename):
    # 1. Source Data
    # The data is provided as a markdown table string.
    csv_data = """
|   WT naive |   WT saline |     WT K |   A1 ko naive |   A1ko saline |   A1ko K |   A2a ko naive |   A2a ko saline |   A2a ko K |
|-----------:|------------:|---------:|--------------:|--------------:|---------:|---------------:|----------------:|-----------:|
|    55.5556 |     65.5914 |  82.2878 |       97.2881 |       40.5512 |  49.7382 |        80.2198 |         80      |    54.5455 |
|    95.9821 |     57.2072 |  88.8393 |       96.4169 |       76.4463 |  57.5758 |        79.5322 |         55.9322 |    83.3333 |
|    74.0458 |     58.1673 |  48.1081 |       82.3708 |       68.75   |  61.6541 |        96.6258 |         81.1225 |    79.2627 |
|    71.9512 |     44.9735 |  86.1925 |       92.9578 |       53.7234 |  75.3927 |        71.5596 |         74.8603 |    47.9245 |
|    80.2691 |     72.1774 |  63.8743 |       77.6786 |       83.3333 |  66.8293 |        70.5882 |         81.8182 |    66.3158 |
|    79.0941 |     54.1936 |  86.9565 |       80.8725 |       73.0337 |  85.1282 |        61.6601 |         58.9226 |    57.7092 |
|    76.0563 |     63.587  |  84.188  |       86.0656 |       25.1724 |  78.7879 |        77.1784 |         88.835  |    78.2101 |
|    74.6114 |     48.731  |  78.0172 |       84.9582 |       76.1468 |  47.541  |        86.2069 |         80.1136 |    88.0597 |
|    89      |     35.3591 |  95.0226 |       70.7395 |       85.4406 |  75.6493 |        87.5598 |         60.9091 |   nan      |
|    92.4603 |     59.6154 |  73.5178 |       86.6667 |      nan      |  84.5902 |        95.6522 |         46.25   |   nan      |
|    91.4062 |     69.0196 |  93.609  |       70.1492 |      nan      |  77.8912 |        83.7963 |         43.949  |   nan      |
|    75.8755 |     61.6601 |  52.7094 |       71.0191 |      nan      | nan      |        82.5911 |         70.4918 |   nan      |
|    92.7185 |     81.0127 |  44.6237 |       56.3319 |      nan      | nan      |        84.5745 |        nan      |   nan      |
|    76.7933 |     54.0909 |  88.421  |       74.6988 |      nan      | nan      |        75.5245 |        nan      |   nan      |
|    69.9531 |     60.4938 |  79.9257 |       65.942  |      nan      | nan      |        56.5217 |        nan      |   nan      |
|    71.5026 |     62.3037 | nan      |       70.3971 |      nan      | nan      |        96.8641 |        nan      |   nan      |
|    88.6598 |     53.8117 | nan      |       83.5766 |      nan      | nan      |       nan      |        nan      |   nan      |
|    62.234  |    nan      | nan      |      nan      |      nan      | nan      |       nan      |        nan      |   nan      |
"""
    # Data Cleaning: Remove the markdown separator line and parse
    lines = csv_data.strip().split('\n')
    # Keep header (index 0) and data (index 2 onwards), skipping the separator line (index 1)
    clean_csv_str = "\n".join([lines[0]] + lines[2:])
    
    # Read CSV with pipe separator
    df = pd.read_csv(io.StringIO(clean_csv_str), sep="|")
    
    # Drop empty columns resulting from leading/trailing pipes
    df = df.dropna(axis=1, how='all')
    
    # Clean column names (remove whitespace)
    df.columns = df.columns.str.strip()
    
    # Ensure all data is numeric
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 2. Configuration
    # Define column order explicitly to match the chart groups
    cols = [
        'WT naive', 'WT saline', 'WT K',
        'A1 ko naive', 'A1ko saline', 'A1ko K',
        'A2a ko naive', 'A2a ko saline', 'A2a ko K'
    ]
    
    # X-axis positions for the bars (grouped)
    # Groups: WT (0,1,2), A1 (4,5,6), A2a (8,9,10)
    positions = [0, 1, 2, 4, 5, 6, 8, 9, 10]
    
    # Colors based on the image
    colors = [
        '#3E7D91', '#1A1A1A', '#9E2A2B',  # WT: Teal, Black, Dark Red
        '#3E7D91', '#4D4D4D', '#E6554D',  # A1: Teal, Dark Grey, Red/Salmon
        '#6ECCE5', '#808080', '#F08080'   # A2a: Light Blue, Grey, Light Red
    ]

    # 3. Plotting
    fig, ax = plt.subplots(figsize=(9, 7))
    
    bar_width = 0.8
    
    for i, col in enumerate(cols):
        data = df[col].dropna()
        mean_val = data.mean()
        sem_val = data.sem()
        pos = positions[i]
        
        # Bar
        ax.bar(pos, mean_val, width=bar_width, color=colors[i], edgecolor='none', zorder=1)
        
        # Error Bar
        ax.errorbar(pos, mean_val, yerr=sem_val, fmt='none', ecolor='gray', capsize=5, elinewidth=1.5, zorder=2)
        
        # Scatter (Jittered)
        np.random.seed(42 + i) 
        jitter = np.random.normal(0, 0.08, size=len(data))
        jitter = np.clip(jitter, -0.25, 0.25)
        
        ax.scatter(np.full(len(data), pos) + jitter, data, 
                   color='#555555', s=15, alpha=0.8, zorder=3, edgecolors='none')

    # 4. Significance Annotations
    def add_sig(x1, x2, y_start, text, rotation=0):
        line_h = 2
        # Draw bracket
        ax.plot([x1, x1, x2, x2], [y_start, y_start + line_h, y_start + line_h, y_start], lw=1, c='k')
        # Add text
        text_y = y_start + line_h + 2
        if rotation != 0:
            # Adjust position for rotated text
            ax.text((x1 + x2) * 0.5, text_y, text, ha='left', va='bottom', fontsize=12, rotation=rotation)
        else:
            ax.text((x1 + x2) * 0.5, text_y, text, ha='center', va='bottom', fontsize=14)

    # Dynamic calculation
    # Define groups: (col1_idx, col2_idx, x1, x2, y_h, rot)
    comparisons = [
        (0, 1, 0, 1, 105, 0),
        (1, 2, 1, 2, 105, 0),
        (3, 4, 4, 5, 105, 0),
        (4, 5, 5, 6, 105, 45),
        (6, 7, 8, 9, 105, 0),
        (7, 8, 9, 10, 105, 45)
    ]

    for c1, c2, x1, x2, y_h, rot in comparisons:
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
            
        add_sig(x1, x2, y_h, sig_text, rotation=rot)

    # 5. Axis Formatting
    ax.set_ylim(0, 135) # Space for annotations
    ax.set_ylabel('Sucrose preference (%)', fontsize=14, color='black')
    
    # Remove standard x-ticks
    ax.set_xticks([])
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('black')
    ax.spines['bottom'].set_color('black')
    
    # Y-ticks
    ax.tick_params(axis='y', labelsize=12, colors='black')
    ax.set_yticks([0, 20, 40, 60, 80, 100])

    # 6. Custom X-Axis Table
    # Y-positions for the table rows (negative data coordinates)
    y_crs = -10
    y_ket = -22
    y_geno_line = -32
    y_geno_text = -42
    
    # Row Labels
    ax.text(-1.5, y_crs, 'CRS', ha='right', va='center', fontsize=12)
    ax.text(-1.5, y_ket, 'Ketamine', ha='right', va='center', fontsize=12)
    
    # Row Values
    row_crs = ['–', '+', '+', '–', '+', '+', '–', '+', '+']
    row_ket = ['–', '–', '+', '–', '–', '+', '–', '–', '+']
    
    for i, pos in enumerate(positions):
        ax.text(pos, y_crs, row_crs[i], ha='center', va='center', fontsize=12)
        ax.text(pos, y_ket, row_ket[i], ha='center', va='center', fontsize=12)

    # Genotype Grouping Lines and Labels
    # WT
    ax.plot([0, 2], [y_geno_line, y_geno_line], color='black', lw=1, clip_on=False)
    ax.text(1, y_geno_text, 'WT', ha='center', va='center', fontsize=12)
    
    # Adora1-/-
    ax.plot([4, 6], [y_geno_line, y_geno_line], color='black', lw=1, clip_on=False)
    ax.text(5, y_geno_text, r'$Adora1^{-/-}$', ha='center', va='center', fontsize=12)
    
    # Adora2a-/-
    ax.plot([8, 10], [y_geno_line, y_geno_line], color='black', lw=1, clip_on=False)
    ax.text(9, y_geno_text, r'$Adora2a^{-/-}$', ha='center', va='center', fontsize=12)

    # Figure Label 'c'
    ax.text(-0.15, 1.0, 'c', transform=ax.transAxes, fontsize=20, fontweight='bold', va='top', ha='right')

    # Adjust layout to accommodate the bottom table
    plt.subplots_adjust(bottom=0.25, left=0.15, right=0.95, top=0.85)

    # Save
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    generate_chart(output_file)