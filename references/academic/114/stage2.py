import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import stats

def generate_chart(output_filename):
    # 1. Data Preparation
    # Extracted directly from the provided Markdown table
    data_dict = {
        0: [18.3852, 18.9828, 29.2471],
        1: [23.8849, 22.2176, 30.8746, 16.6495],
        2: [28.1565, 50.9344, 25.8434],
        3: [18.4267, 44.67, 24.6989],
        4: [18.4647, 15.9874, 43.8441],
        5: [38.9606, 25.1849, 22.7408],
        6: [42.5473, 21.3322, 17.5755, 26.8835, 22.4924],
        7: [29.1812, 48.6689, 26.2712],
        8: [17.2065, 20.452, 23.9359],
        9: [18.4808, 26.2369]
    }

    # Flatten data for DataFrame
    rows = []
    for gen, values in data_dict.items():
        for val in values:
            rows.append({'Generation': gen, 'TPM': val})
    
    df = pd.DataFrame(rows)

    # Define Categories and Colors based on the chart legend and visual inspection
    # Gen 0 is black (not in legend text, but present on graph)
    # Gen 1-2: early (Pink/Magenta)
    # Gen 3-5: mid (Orange)
    # Gen 6: mid-late (Brown)
    # Gen 7-9: late (Green)
    
    colors = {
        'control': '#000000',      # Black for Gen 0
        'early': '#E040FB',        # Magenta/Pink
        'mid': '#E69F00',          # Orange/Gold
        'mid-late': '#8D6E63',     # Brown
        'late': '#66BB6A'          # Green
    }

    def get_stage(gen):
        if gen == 0: return 'control'
        if 1 <= gen <= 2: return 'early'
        if 3 <= gen <= 5: return 'mid'
        if gen == 6: return 'mid-late'
        if 7 <= gen <= 9: return 'late'
        return 'unknown'

    df['Stage'] = df['Generation'].apply(get_stage)

    # 2. Setup Plot
    fig, ax = plt.subplots(figsize=(7, 5))
    
    # Set background to white
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # 3. Plot Scatter Points
    # We plot by group to handle colors and legend labels correctly
    
    # Plot Gen 0 (Control) - No legend entry in the box
    control_data = df[df['Stage'] == 'control']
    ax.scatter(control_data['Generation'], control_data['TPM'], 
               color=colors['control'], s=60, zorder=3, edgecolors='none')

    # Plot Legend Groups
    groups = ['early', 'mid', 'mid-late', 'late']
    for group in groups:
        subset = df[df['Stage'] == group]
        ax.scatter(subset['Generation'], subset['TPM'], 
                   color=colors[group], label=group, s=60, zorder=3, edgecolors='none')

    # 4. Regression Line and Confidence Intervals
    x = df['Generation']
    y = df['TPM']
    
    # Calculate linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    # Create a sequence of x values for smooth lines
    x_seq = np.linspace(0, 9, 100)
    y_seq = slope * x_seq + intercept
    
    # Plot Regression Line (Solid Black)
    ax.plot(x_seq, y_seq, color='black', linewidth=1.5, zorder=2)
    
    # Calculate Confidence Intervals (95%)
    # Formula for CI of the mean response
    n = len(x)
    t_score = stats.t.ppf(0.975, df=n-2) # two-sided 95%
    
    # Mean of x
    mean_x = np.mean(x)
    # Sum of squares of x differences
    s_xx = np.sum((x - mean_x)**2)
    # Standard error of the estimate (residuals)
    residuals = y - (slope * x + intercept)
    s_err = np.sqrt(np.sum(residuals**2) / (n - 2))
    
    # Calculate CI bands
    ci = t_score * s_err * np.sqrt(1/n + (x_seq - mean_x)**2 / s_xx)
    
    lower_bound = y_seq - ci
    upper_bound = y_seq + ci
    
    # Plot CI Lines (Dashed Black)
    ax.plot(x_seq, lower_bound, color='black', linestyle='--', linewidth=1, zorder=2)
    ax.plot(x_seq, upper_bound, color='black', linestyle='--', linewidth=1, zorder=2)

    # 5. Formatting and Styling
    
    # Axis Limits
    ax.set_xlim(-0.2, 9.2)
    ax.set_ylim(0, 80)
    
    # X-Axis Ticks
    ax.set_xticks(range(10))
    ax.set_xticklabels(range(10), fontsize=12, fontweight='bold')
    ax.set_xlabel("Generation", fontsize=14, fontweight='bold')
    
    # Y-Axis Ticks and Scientific Notation
    ax.set_yticks([0, 20, 40, 60, 80])
    
    # Custom formatter to match "2x10^1" style
    def scientific_format(x, pos):
        if x == 0:
            return "0"
        exponent = 1
        coeff = int(x / 10)
        return r'{}$\times10^{}$'.format(coeff, exponent)
    
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(scientific_format))
    ax.tick_params(axis='y', labelsize=12)
    # Make y-tick labels bold (requires iterating as set_yticklabels overrides formatter often)
    for label in ax.get_yticklabels():
        label.set_fontweight('bold')
        
    ax.set_ylabel("Transcripts per million", fontsize=14, fontweight='bold')

    # Title
    ax.set_title("Acsl4", fontsize=16, fontweight='bold', style='italic', pad=15)
    
    # Add 'f' label in top left
    ax.text(-0.15, 1.05, 'f', transform=ax.transAxes, 
            fontsize=20, fontweight='bold', va='top', ha='left')

    # Add R-squared text
    # Using the exact value from the image/table
    r2_text = "R$^2$ = 0.0001256"
    ax.text(0.2, 8, r2_text, fontsize=14, color='black')

    # Legend
    # Create a custom legend to match the style
    legend = ax.legend(title="Stage", loc='upper right', 
                       fontsize=11, title_fontsize=12,
                       frameon=True, edgecolor='black', framealpha=1,
                       handletextpad=0.1, borderpad=0.6)
    
    # Bold the legend title
    legend.get_title().set_fontweight('bold')
    
    # Adjust legend marker size
    for handle in legend.legend_handles:
        handle.set_sizes([80])

    # Thicken axis spines
    for spine in ax.spines.values():
        spine.set_linewidth(1.5)
        spine.set_color('black')
        
    ax.tick_params(width=1.5, color='black')

    # 6. Save Output
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    generate_chart(output_file)