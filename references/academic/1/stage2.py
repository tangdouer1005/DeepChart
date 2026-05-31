import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import stats

def generate_chart(output_filename):
    # 1. Load Source Data
    # Using the exact markdown table provided in the prompt
    csv_data = """
|   saline |        K5 |     K10 |     K20 |     K30 |      K50 |
|---------:|----------:|--------:|--------:|--------:|---------:|
|  2.61617 |  10.9128  | 17.0236 | 27.166  | 29.3987 |  24.7485 |
|  2.36168 |   8.18393 | 10.8045 | 24.2927 | 25.5928 |  32.7675 |
|  7.15327 |   7.4796  | 19.7571 | 40.8666 | 43.1267 |  30.3007 |
|  5.95655 |   6.79138 | 11.4857 | 33.6696 | 38.4147 |  35.1756 |
|  8.7249  |   6.06007 | 20.58   | 28.6541 | 34.1275 |  45.9113 |
| 10.075   |  10.8698  | 22.387  | 32.8038 | 38.4792 |  50.5032 |
|  4.65983 |  11.254   | 17.5725 | 36.9777 | 41.937  |  50.1651 |
|  5.17181 |   6.60699 | 19.0825 | 35.9643 | 39.0227 |  33.9109 |
|  4.41222 |  11.6103  | 20.2917 | 30.9105 | 37.767  |  23.291  |
|  3.4727  | nan       | 20.6828 | 27.4061 | 35.177  |  25.8906 |
|  3.31779 | nan       | 13.9655 | 21.5009 | 20.7624 |  33.9761 |
|  7.68342 | nan       | 14.848  | 22.4181 | 21.3724 | nan      |
"""
    
    # Parse the markdown table
    # We skip the first row (header separator) and handle the pipes
    df = pd.read_csv(io.StringIO(csv_data), sep="|", skipinitialspace=True)
    
    # Clean up dataframe: remove empty columns caused by leading/trailing pipes
    df = df.dropna(axis=1, how='all')
    
    # Clean column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Ensure numeric types
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 2. Prepare Data for Plotting
    # Define the order and labels
    columns = ['saline', 'K5', 'K10', 'K20', 'K30', 'K50']
    x_labels = ['0', '5', '10', '20', '30', '50']
    x_pos = np.arange(len(columns))
    
    # Calculate Mean and SEM (Standard Error of the Mean)
    means = df[columns].mean()
    sems = df[columns].sem()
    
    # 3. Setup Plot
    # Set font style to match scientific publication (sans-serif)
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
    plt.rcParams['font.size'] = 14
    
    fig, ax = plt.subplots(figsize=(5, 6))
    
    # 4. Define Colors
    # Matching the gradient from black to light red to dark red
    colors = [
        '#000000',  # Saline (Black)
        '#F08080',  # K5 (Light Salmon/Red)
        '#A52A2A',  # K10 (Brown/Red)
        '#800000',  # K20 (Maroon)
        '#500000',  # K30 (Very Dark Red)
        '#400000'   # K50 (Almost Black Red)
    ]
    
    # 5. Plot Bars
    bars = ax.bar(x_pos, means, yerr=sems, 
                  align='center', 
                  alpha=1.0, 
                  color=colors, 
                  capsize=5, 
                  width=0.65,
                  error_kw={'elinewidth': 1.5, 'ecolor': 'gray'})
    
    # 6. Plot Individual Data Points (Scatter/Swarm)
    np.random.seed(42) # For reproducible jitter
    jitter_strength = 0.15
    
    for i, col in enumerate(columns):
        data = df[col].dropna()
        # Create jittered x coordinates
        x_jitter = np.random.uniform(-jitter_strength, jitter_strength, size=len(data)) + x_pos[i]
        ax.scatter(x_jitter, data, color='#555555', s=20, zorder=10, alpha=0.8, edgecolors='none')

    # 7. Add Statistical Annotations
    # Helper function to draw significance lines
    def draw_significance(x1, x2, y, text):
        line_height = 1
        # Draw the horizontal line
        ax.plot([x1, x2], [y, y], color='black', linewidth=0.8)
        # Add text
        ax.text((x1 + x2) * 0.5, y + 0.5, text, ha='center', va='bottom', color='black', fontsize=14)

    # Dynamically calculate p-values and add annotations
    comparisons = [
        ('saline', 'K5', 0, 1, 14),
        ('K5', 'K10', 1, 2, 26),
        ('K10', 'K20', 2, 3, 44),
        ('K20', 'K30', 3, 4, 51),
        ('K30', 'K50', 4, 5, 59)
    ]

    for col1, col2, x1, x2, y_pos in comparisons:
        d1 = df[col1].dropna()
        d2 = df[col2].dropna()
        t_stat, p_val = stats.ttest_ind(d1, d2)
        
        if p_val < 0.001:
            sig_text = "***"
        elif p_val < 0.01:
            sig_text = "**"
        elif p_val < 0.05:
            sig_text = "*"
        else:
            sig_text = f"P = {p_val:.2f}"
            
        draw_significance(x1, x2, y_pos, sig_text)

    # 8. Formatting
    
    # Axis Labels
    ax.set_ylabel(r'Ado peak ($\Delta F/F$ %)', fontsize=16, labelpad=10)
    ax.set_xlabel(r'Ketamine (mg kg$^{-1}$)', fontsize=16, labelpad=10)
    
    # X-Axis Ticks
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x_labels, fontsize=16)
    
    # Y-Axis Ticks
    ax.set_ylim(0, 65) # Set limit to accommodate top annotation
    ax.set_yticks([0, 20, 40, 60])
    ax.tick_params(axis='y', labelsize=16)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Adjust spine thickness
    ax.spines['left'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1)
    
    # Add Figure Label "f"
    # Positioned in figure coordinates or axes coordinates relative to top-left
    ax.text(-0.25, 1.0, 'f', transform=ax.transAxes, fontsize=24, fontweight='bold', va='top', ha='left')

    # Layout adjustment
    plt.tight_layout()
    
    # 9. Save Output
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    generate_chart(output_file)