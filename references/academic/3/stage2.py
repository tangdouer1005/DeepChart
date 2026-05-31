import sys
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

def generate_chart(output_filename='output.png'):
    # ---------------------------------------------------------
    # 1. Load Source Data
    # ---------------------------------------------------------
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
    # Clean the markdown table string: remove the separator line (contains '---')
    lines = [line for line in csv_data.strip().split('\n') if '---' not in line]
    cleaned_csv = '\n'.join(lines)
    
    # Read data using regex separator to handle pipes and whitespace
    df = pd.read_csv(io.StringIO(cleaned_csv), sep=r'\s*\|\s*', engine='python')
    
    # Drop the first and last columns if they are empty (due to leading/trailing pipes)
    if df.columns[0] == '' or df.columns[0].startswith('Unnamed'):
        df = df.iloc[:, 1:]
    if df.columns[-1] == '' or df.columns[-1].startswith('Unnamed'):
        df = df.iloc[:, :-1]
        
    # Ensure all data is numeric (coercing errors to NaN)
    df = df.apply(pd.to_numeric, errors='coerce')
    
    # ---------------------------------------------------------
    # 2. Data Processing
    # ---------------------------------------------------------
    means = df.mean()
    sems = df.sem()
    x_pos = np.arange(len(means))
    
    # ---------------------------------------------------------
    # 3. Plotting Setup
    # ---------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Define Colors (WT: Teal/Black/Red, A1: Lighter Teal/Grey/Red, A2a: Light Teal/Grey/Light Red)
    colors = [
        '#468FA3', '#1A1A1A', '#9E2A2B',  # WT
        '#5DAcc0', '#444444', '#E85A55',  # A1
        '#66C2D9', '#808080', '#F08080'   # A2a
    ]
    
    # Draw Bars
    ax.bar(x_pos, means, yerr=sems, color=colors, 
           capsize=4, width=0.7, edgecolor='none', 
           error_kw={'elinewidth': 1.5, 'ecolor': 'gray'})
           
    # Draw Swarm/Strip Plot (Individual Data Points)
    np.random.seed(42)
    for i, col in enumerate(df.columns):
        vals = df[col].dropna()
        # Jitter x coordinates
        jitter = np.random.uniform(-0.15, 0.15, size=len(vals))
        ax.scatter(x_pos[i] + jitter, vals, color='#555555', s=15, alpha=0.7, zorder=10, edgecolors='none')
        
    # ---------------------------------------------------------
    # 4. Significance Annotations
    # ---------------------------------------------------------
    def draw_bracket(ax, x1, x2, text, y_start):
        line_h = 2
        # Draw bracket lines
        ax.plot([x1, x1, x2, x2], [y_start, y_start + line_h, y_start + line_h, y_start], 
                lw=1.0, c='k')
        # Add text
        ax.text((x1 + x2) * 0.5, y_start + line_h + 1, text, 
                ha='center', va='bottom', color='k', fontsize=10)
        # Return new height for potential stacking
        return y_start + line_h + 10 

    # Calculate base heights for brackets (max data point + padding)
    # We use the max of (mean+sem) or max individual data point to ensure clearance
    def get_group_max(start_idx, end_idx):
        max_val = max((means + sems)[start_idx:end_idx])
        max_data = df.iloc[:, start_idx:end_idx].max().max()
        return max(max_val, max_data) + 5

    # Define groups and their comparisons
    # structure: (start_col_idx, end_col_idx, list_of_pairs)
    groups = [
        (0, 3, [(0, 1), (1, 2)]), # WT
        (3, 6, [(3, 4), (4, 5)]), # A1
        (6, 9, [(6, 7), (7, 8)])  # A2a
    ]

    for start, end, pairs in groups:
        current_h = get_group_max(start, end)
        for col1, col2 in pairs:
            # Calculate P-value
            d1 = df.iloc[:, col1].dropna()
            d2 = df.iloc[:, col2].dropna()
            t_stat, p_val = stats.ttest_ind(d1, d2)
            
            # Format P-text
            if p_val < 0.001:
                sig_text = "***"
            elif p_val < 0.01:
                sig_text = "**"
            elif p_val < 0.05:
                sig_text = "*"
            else:
                sig_text = f"P = {p_val:.2f}"
            
            current_h = draw_bracket(ax, col1, col2, sig_text, current_h)
    
    # ---------------------------------------------------------
    # 5. Custom X-Axis Table and Layout
    # ---------------------------------------------------------
    ax.set_xticks([])
    
    # Set Y limit to accommodate data and annotations
    # Data max is ~100, annotations go up to ~130-140
    ax.set_ylim(0, 145)
    
    # Define positions for table text
    y_row1 = -8
    y_row2 = -18
    y_line = -25
    y_group = -32
    
    # Row Headers
    ax.text(-1.0, y_row1, "CRS", ha='right', va='center', fontsize=12)
    ax.text(-1.0, y_row2, "Ketamine", ha='right', va='center', fontsize=12)
    
    # Column Labels
    labels_crs = ['-', '+', '+'] * 3
    labels_ket = ['-', '-', '+'] * 3
    
    for i in range(9):
        ax.text(i, y_row1, labels_crs[i], ha='center', va='center', fontsize=12)
        ax.text(i, y_row2, labels_ket[i], ha='center', va='center', fontsize=12)
        
    # Grouping Lines and Labels
    # WT
    ax.plot([0, 2], [y_line, y_line], color='k', lw=1, clip_on=False)
    ax.text(1, y_group, "WT", ha='center', va='center', fontsize=12)
    
    # Adora1-/-
    ax.plot([3, 5], [y_line, y_line], color='k', lw=1, clip_on=False)
    ax.text(4, y_group, r"$Adora1^{-/-}$", ha='center', va='center', fontsize=12)
    
    # Adora2a-/-
    ax.plot([6, 8], [y_line, y_line], color='k', lw=1, clip_on=False)
    ax.text(7, y_group, r"$Adora2a^{-/-}$", ha='center', va='center', fontsize=12)
    
    # ---------------------------------------------------------
    # 6. Final Styling
    # ---------------------------------------------------------
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylabel("Immobility time (s)", fontsize=12)
    
    # Add 'b' label
    ax.text(-0.1, 1.0, 'b', transform=ax.transAxes, fontsize=16, fontweight='bold', va='top')
    
    # Adjust layout to prevent clipping of the bottom table
    plt.subplots_adjust(bottom=0.25, left=0.15)
    
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)