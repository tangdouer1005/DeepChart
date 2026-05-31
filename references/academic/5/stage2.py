import sys
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

def generate_chart(output_filename='output.png'):
    # 1. Load Source Data
    csv_data = """
|   WT saline |     WT K |   A1ko saline |   A1ko K |   A2a ko saline |   A2a ko K |
|------------:|---------:|--------------:|---------:|----------------:|-----------:|
|     163.926 | 146.915  |       93.4671 |  168.582 |           89.33 |     144.37 |
|     164.714 | 130.208  |      141.638  |  167.291 |          143.23 |     153.87 |
|     141.336 | 133.681  |      164.543  |   82.285 |          183.09 |     154.22 |
|     130.72  | 118.735  |      157.607  |  112.291 |           54.72 |     139.03 |
|     178.996 |  87.1218 |      201.418  |  121.264 |          167.68 |      74.62 |
|     160.724 | 144.446  |      148.003  |  152.277 |          201.62 |     123.2  |
|     151.167 | 101.561  |      165.569  |  150.877 |          181.81 |     147.89 |
|     102.942 | 137.995  |      167.359  |  146.772 |          198.38 |     190.94 |
|     178.892 | 151.035  |      141.59   |  120.345 |          nan    |     nan    |
|     165.005 | 130.827  |       99.848  |  147.588 |          nan    |     nan    |
|     146.067 | 110.871  |      nan      |  nan     |          nan    |     nan    |
|     198.72  |  62.9039 |      nan      |  nan     |          nan    |     nan    |
|     178.15  | 138.84   |      nan      |  nan     |          nan    |     nan    |
|      93.44  | 124.06   |      nan      |  nan     |          nan    |     nan    |
|     158.86  | 100.39   |      nan      |  nan     |          nan    |     nan    |
|     171.53  | 118.43   |      nan      |  nan     |          nan    |     nan    |
|     175.43  | 104.59   |      nan      |  nan     |          nan    |     nan    |
|     128     |  97      |      nan      |  nan     |          nan    |     nan    |
|     nan     | 108      |      nan      |  nan     |          nan    |     nan    |
|     nan     | 112      |      nan      |  nan     |          nan    |     nan    |
"""
    # Read CSV, handling the markdown pipe separators
    # The input string contains a markdown table. 
    # pd.read_csv with sep='|' will read the header, then the separator line (e.g. "---:"), then data.
    df = pd.read_csv(io.StringIO(csv_data), sep='|', skipinitialspace=True)
    
    # Drop empty columns created by leading/trailing pipes
    df = df.dropna(axis=1, how='all') 
    
    # Clean column names
    df.columns = [c.strip() for c in df.columns]
    
    # Remove the separator row (index 0) which contains '---' strings
    df = df.iloc[1:].reset_index(drop=True)
    
    # Convert all columns to numeric, coercing errors (like empty strings or remaining formatting chars) to NaN
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 2. Setup Plotting Parameters
    cols = ['WT saline', 'WT K', 'A1ko saline', 'A1ko K', 'A2a ko saline', 'A2a ko K']
    
    # Colors extracted from image
    # WT: Black, Dark Red
    # Adora1: Dark Grey, Red
    # Adora2a: Grey, Light Red
    colors = [
        '#000000', '#9F2B2B',  # WT (Black, Dark Red)
        '#4D4D4D', '#EE5C5C',  # Adora1 (Dark Grey, Red)
        '#808080', '#F28C8C'   # Adora2a (Grey, Light Red)
    ]

    # X positions: Grouped pairs with gaps
    # Pair 1: 0, 1
    # Pair 2: 3, 4
    # Pair 3: 6, 7
    x_positions = [0, 1, 3, 4, 6, 7]
    
    # Initialize Figure
    fig, ax = plt.subplots(figsize=(7, 6))
    
    # 3. Plot Data
    np.random.seed(42) 
    bar_width = 0.8
    
    for i, col in enumerate(cols):
        # Extract valid data
        data = df[col].dropna().values
        
        if len(data) == 0:
            continue
            
        mean_val = np.mean(data)
        sem_val = np.std(data, ddof=1) / np.sqrt(len(data))
        
        # Bar
        ax.bar(x_positions[i], mean_val, width=bar_width, color=colors[i], 
               edgecolor='none', zorder=1)
        
        # Error Bar
        ax.errorbar(x_positions[i], mean_val, yerr=sem_val, fmt='none', 
                    ecolor='#555555', capsize=6, elinewidth=1.5, markeredgewidth=1.5, zorder=3)
        
        # Jittered Points
        jitter = np.random.uniform(-0.15, 0.15, size=len(data))
        ax.scatter(x_positions[i] + jitter, data, color='#555555', s=20, alpha=0.8, zorder=2, edgecolors='none')

    # 4. Statistical Annotations
    # Y-level for significance lines
    sig_y = 165
    text_offset = 5
    
    # Function to draw bracket
    def draw_bracket(x1, x2, y, text):
        # Horizontal line
        ax.plot([x1, x2], [y, y], lw=1, c='k')
        # Text
        ax.text((x1 + x2) / 2, y + text_offset, text, ha='center', va='bottom', fontsize=12)

    # Dynamic Calculation
    # Pairs: (col1_idx, col2_idx, x1, x2)
    comparisons = [
        (0, 1, 0, 1),
        (2, 3, 3, 4),
        (4, 5, 6, 7)
    ]

    for c1, c2, x1, x2 in comparisons:
        d1 = df.iloc[:, c1].dropna()
        d2 = df.iloc[:, c2].dropna()
        t, p_val = stats.ttest_ind(d1, d2)
        
        if p_val < 0.001:
            sig_text = '***'
        elif p_val < 0.01:
            sig_text = '**'
        elif p_val < 0.05:
            sig_text = '*'
        else:
            sig_text = f'$P = {p_val:.2f}$'
            
        draw_bracket(x1, x2, sig_y, sig_text)

    # 5. Axis Formatting
    ax.set_ylabel('Immobility time (s)', fontsize=14, labelpad=10)
    ax.set_ylim(0, 210)
    ax.set_yticks([0, 50, 100, 150, 200])
    ax.tick_params(axis='y', labelsize=12, length=5)
    
    # Hide X ticks
    ax.set_xticks([])
    
    # Spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # 6. Custom Table Labels
    # We need to place text below the axis.
    # Coordinates: x is data coords, y is data coords (negative)
    
    # Define Y positions for rows
    y_crs = -15
    y_ket = -35
    y_geno_line = -50
    y_geno_text = -65
    
    # Row 1: CRS
    ax.text(-1.5, y_crs, "CRS", ha='right', va='center', fontsize=12)
    for x in x_positions:
        ax.text(x, y_crs, "+", ha='center', va='center', fontsize=12)
        
    # Row 2: Ketamine
    ax.text(-1.5, y_ket, "Ketamine", ha='right', va='center', fontsize=12)
    signs = ['-', '+', '-', '+', '-', '+']
    for i, x in enumerate(x_positions):
        # En-dash or minus sign
        s = u'\u2212' if signs[i] == '-' else '+'
        ax.text(x, y_ket, s, ha='center', va='center', fontsize=14)
        
    # Row 3: Genotypes
    # Lines
    # WT: 0 to 1
    ax.plot([0 - 0.4, 1 + 0.4], [y_geno_line, y_geno_line], color='black', lw=1, clip_on=False)
    ax.text(0.5, y_geno_text, "WT", ha='center', va='center', fontsize=12)
    
    # Adora1
    ax.plot([3 - 0.4, 4 + 0.4], [y_geno_line, y_geno_line], color='black', lw=1, clip_on=False)
    ax.text(3.5, y_geno_text, r"$Adora1^{-/-}$", ha='center', va='center', fontsize=12)
    
    # Adora2a
    ax.plot([6 - 0.4, 7 + 0.4], [y_geno_line, y_geno_line], color='black', lw=1, clip_on=False)
    ax.text(6.5, y_geno_text, r"$Adora2a^{-/-}$", ha='center', va='center', fontsize=12)

    # Figure Label 'd'
    # Position relative to axes: top left, outside
    ax.text(-0.15, 1.0, 'd', transform=ax.transAxes, fontsize=20, fontweight='bold', va='bottom', ha='right')

    # Adjust margins to fit the table below
    plt.subplots_adjust(bottom=0.3, left=0.15, right=0.95, top=0.9)
    
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)