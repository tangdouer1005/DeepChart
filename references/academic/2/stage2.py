import sys
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

def generate_chart(output_filename):
    # 1. Load Source Data
    # The data is provided as a markdown table string.
    csv_data = """saline|K5|K10|K20|K30|K50
-0.15442|2.02859|5.40501|5.92692|8.08702|6.62419
-0.58043|0.878401|2.23115|4.92276|5.83228|13.2996
1.58696|0.98349|6.34756|11.0817|11.3787|8.36267
0.868186|0.785771|2.56239|7.97339|9.18607|11.9092
2.32056|0.388214|4.55303|7.98792|8.53485|17.7595
2.3009|2.19805|5.07432|8.42453|9.63262|21.4167
1.01952|1.57333|4.39348|9.63153|11.4553|21.2146
1.11587|1.50217|4.89635|9.48093|10.6288|9.24065
0.781112|3.44616|3.20176|7.67429|10.3601|5.81632
0.46059|nan|3.7647|7.56366|9.52821|7.84489
0.517398|nan|3.76893|6.8856|5.61355|11.644
1.76375|nan|3.87353|4.87388|4.66221|nan"""

    # Read data into pandas DataFrame
    df = pd.read_csv(io.StringIO(csv_data), sep='|')
    
    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]

    # 2. Calculate Statistics
    # Calculate Mean and Standard Error of the Mean (SEM)
    means = df.mean()
    sems = df.sem()
    
    # 3. Setup Plotting Parameters
    # Define colors based on the image
    # 0: Black, 5: Salmon, 10: Red, 20: Dark Red, 30: Darker Red, 50: Darkest Red
    colors = [
        '#1a1a1a',  # saline (blackish)
        '#ea8685',  # K5 (salmon/pink)
        '#b33939',  # K10 (medium red)
        '#881e19',  # K20 (dark red)
        '#6d1512',  # K30 (darker red)
        '#4a0d0b'   # K50 (very dark red/brown)
    ]
    
    x_labels = ['0', '5', '10', '20', '30', '50']
    x_pos = np.arange(len(x_labels))

    # Create figure
    fig, ax = plt.subplots(figsize=(4, 5)) # Portrait orientation

    # 4. Draw Bars and Error Bars
    # Plot bars
    bars = ax.bar(x_pos, means, 
                  yerr=sems, 
                  color=colors, 
                  capsize=4, 
                  width=0.7, 
                  edgecolor='none',
                  error_kw={'elinewidth': 1.5, 'ecolor': 'gray', 'alpha': 0.8},
                  zorder=1)

    # 5. Draw Scatter Points (Jittered)
    np.random.seed(42) # For reproducible jitter
    jitter_strength = 0.15
    
    for i, col in enumerate(df.columns):
        # Get valid data (drop NaNs)
        y_values = df[col].dropna().values
        # Create jittered x coordinates
        x_values = np.random.normal(loc=i, scale=jitter_strength, size=len(y_values))
        # Clamp jitter to stay roughly within bar width
        x_values = np.clip(x_values, i - 0.3, i + 0.3)
        
        ax.scatter(x_values, y_values, 
                   color='#555555', 
                   s=15, 
                   alpha=0.8, 
                   zorder=2, 
                   edgecolors='none')

    # 6. Add Statistical Annotations
    # Helper function to draw significance brackets
    def add_significance(x1, x2, y_line, text):
        # Draw the line
        ax.plot([x1, x2], [y_line, y_line], color='black', linewidth=0.8)
        # Add text
        ax.text((x1 + x2) * 0.5, y_line + 0.2, text, 
                ha='center', va='bottom', color='black', fontsize=12)

    # Dynamically calculate p-values and add annotations
    comparisons = [
        ('saline', 'K5', 0, 1, 5.0),
        ('K5', 'K10', 1, 2, 8.8),
        ('K10', 'K20', 2, 3, 13.2),
        ('K20', 'K30', 3, 4, 17.0),
        ('K30', 'K50', 4, 5, 23.0)
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
            # Formatting as math text for P values to match original style if needed, 
            # but simple string is usually sufficient. 
            # Original used r'$P = 0.20$' etc, let's match that style for non-significant ones.
            sig_text = r'$P = ' + f'{p_val:.2f}' + r'$'
            
        add_significance(x1, x2, y_pos, sig_text)

    # 7. Styling and Layout
    
    # Axis Labels
    ax.set_ylabel('AUC normalized', fontsize=14, labelpad=10)
    ax.set_xlabel(r'Ketamine (mg kg$^{-1}$)', fontsize=14, labelpad=10)
    
    # Ticks
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x_labels, fontsize=12)
    ax.set_yticks([0, 5, 10, 15, 20, 25])
    ax.set_yticklabels([0, 5, 10, 15, 20, 25], fontsize=12)
    
    # Axis Limits
    ax.set_ylim(-1, 25)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Adjust tick parameters (outward ticks)
    ax.tick_params(axis='both', direction='out', length=6, width=1)

    # Add Figure Label "g"
    # Placed in the top left, outside the axes
    ax.text(-0.25, 1.05, 'g', transform=ax.transAxes, 
            fontsize=20, fontweight='bold', va='top', ha='left')

    # Layout adjustment
    plt.tight_layout()

    # 8. Save Output
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')

if __name__ == "__main__":
    # Handle command line argument for output filename
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        output_file = "output.png"
    
    generate_chart(output_file)