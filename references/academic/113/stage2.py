import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import matplotlib.ticker as ticker

def generate_chart(output_filename):
    # 1. Data Preparation
    # Parsing the provided "Source Data" table manually into a structure
    # Keys are Generation (LN#), Values are the non-nan TPM values
    raw_data = {
        0: [521.144, 502.542, 418.634],
        1: [406.000, 546.786, 438.859, 507.417],
        2: [431.356, 439.983, 451.431],
        3: [596.385, 427.692, 397.725],
        4: [556.008, 535.857, 556.679],
        5: [490.246, 469.509, 611.647],
        6: [491.132, 475.304, 531.666, 427.445, 628.977],
        7: [662.653, 640.417, 525.559],
        8: [508.716, 410.376, 512.663],
        9: [501.776, 518.009]
    }

    # Flatten into a DataFrame for plotting
    rows = []
    for gen, values in raw_data.items():
        for val in values:
            # Determine stage for coloring based on the legend and visual inspection
            if gen == 0:
                stage = 'zero' # Not in legend, black in plot
            elif gen in [1, 2]:
                stage = 'early'
            elif gen in [3, 4, 5]:
                stage = 'mid'
            elif gen == 6:
                stage = 'mid-late'
            elif gen in [7, 8, 9]:
                stage = 'late'
            rows.append({'Generation': gen, 'TPM': val, 'Stage': stage})

    df = pd.DataFrame(rows)

    # 2. Setup Plot
    fig, ax = plt.subplots(figsize=(7, 5))
    
    # Style settings
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
    
    # 3. Define Colors
    # Matching colors from the image
    colors = {
        'zero': '#000000',      # Black
        'early': '#E040FB',     # Magenta/Pink
        'mid': '#E69F00',       # Orange/Gold
        'mid-late': '#8D6E63',  # Brown
        'late': '#55A868'       # Green
    }

    # 4. Plot Scatter Points
    # We plot manually to control z-order and specific styling
    for stage, color in colors.items():
        subset = df[df['Stage'] == stage]
        ax.scatter(
            subset['Generation'], 
            subset['TPM'], 
            color=color, 
            s=60, 
            alpha=1.0, 
            edgecolor='none',
            label=stage if stage != 'zero' else "" # Exclude zero from legend
        )

    # 5. Regression Analysis & Plotting
    x = df['Generation'].values
    y = df['TPM'].values
    
    # Calculate linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    # Create trend line data
    x_fit = np.linspace(0, 9.5, 100)
    y_fit = slope * x_fit + intercept
    
    # Calculate Confidence Intervals (95%)
    # CI formula for the mean response
    n = len(x)
    t_score = stats.t.ppf(0.975, df=n-2) # Two-sided t-score
    
    # Mean of x
    x_mean = np.mean(x)
    # Sum of squared differences of x
    Sxx = np.sum((x - x_mean)**2)
    # Standard error of the estimate (residuals)
    residuals = y - (slope * x + intercept)
    Se = np.sqrt(np.sum(residuals**2) / (n - 2))
    
    # Calculate CI bands
    ci = t_score * Se * np.sqrt(1/n + (x_fit - x_mean)**2 / Sxx)
    upper_bound = y_fit + ci
    lower_bound = y_fit - ci

    # Plot Regression Line (Solid Black)
    ax.plot(x_fit, y_fit, color='black', linewidth=1.5, zorder=1)
    
    # Plot Confidence Intervals (Dashed Black)
    ax.plot(x_fit, upper_bound, color='black', linestyle='--', linewidth=1.2, zorder=1)
    ax.plot(x_fit, lower_bound, color='black', linestyle='--', linewidth=1.2, zorder=1)

    # 6. Formatting Axes and Labels
    
    # Y-Axis: Scientific Notation (e.g., 8x10^2)
    ax.set_ylim(300, 800)
    ax.set_yticks([300, 400, 500, 600, 700, 800])
    
    # Custom formatter to match "8x10^2" style
    def scientific_formatter(x, pos):
        if x == 0: return "0"
        exponent = 2
        coeff = int(x / (10**exponent))
        return r"${}\times10^{}$".format(coeff, exponent)
    
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(scientific_formatter))
    
    # X-Axis
    ax.set_xlim(-0.2, 9.5)
    ax.set_xticks(range(10))
    
    # Labels
    ax.set_xlabel("Generation", fontsize=14, fontweight='bold')
    ax.set_ylabel("Transcripts per million", fontsize=14, fontweight='bold')
    
    # Title
    # "e" is the figure panel label, "Gpx4" is the gene name
    ax.set_title("Gpx4", fontsize=16, fontweight='bold', style='italic', pad=10)
    ax.text(-0.12, 1.05, "e", transform=ax.transAxes, fontsize=18, fontweight='bold', va='top', ha='right')

    # 7. Legend
    # Custom legend to match the box style
    handles, labels = ax.get_legend_handles_labels()
    # Reorder if necessary, but dictionary order is usually preserved in Py3.7+
    # We need to ensure the order: early, mid, mid-late, late
    order_map = {'early': 0, 'mid': 1, 'mid-late': 2, 'late': 3}
    # Filter out handles that might not be in the map (like 'zero')
    sorted_pairs = sorted(
        [(h, l) for h, l in zip(handles, labels) if l in order_map],
        key=lambda pair: order_map[pair[1]]
    )
    if sorted_pairs:
        sorted_handles, sorted_labels = zip(*sorted_pairs)
        legend = ax.legend(
            sorted_handles, 
            sorted_labels, 
            title="Stage", 
            loc='upper right', 
            frameon=True, 
            edgecolor='black',
            facecolor='white',
            framealpha=1,
            fontsize=11,
            title_fontsize=12,
            handletextpad=0.1
        )
        legend.get_frame().set_linewidth(1.5)
        legend.get_title().set_fontweight('bold')

    # 8. Annotations
    # R-squared value
    # Using the value from the image/source data explicitly
    r_squared_text = r"R$^2$ = 0.09551"
    ax.text(0.5, 350, r_squared_text, fontsize=14, color='black')

    # 9. Final Layout Adjustments
    # Make axes lines thicker
    for axis in ['top','bottom','left','right']:
        ax.spines[axis].set_linewidth(1.5)
    
    ax.tick_params(width=1.5, length=5, labelsize=11)

    plt.tight_layout()
    
    # Save output
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    generate_chart(output_file)