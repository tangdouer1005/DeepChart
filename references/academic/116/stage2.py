import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import stats

def generate_chart(output_filename):
    # ---------------------------------------------------------
    # 1. Data Preparation
    # ---------------------------------------------------------
    # Raw data extracted from the provided Markdown table
    raw_data = {
        0: [4.10245, 11.6237, 29.64],
        1: [79.815, 127.6, 43.9972, 7.03619],
        2: [26.9305, 94.9128, 74.5187],
        3: [54.9296, 5.20333, 86.6899],
        4: [17.0596, 51.9138, 95.6225],
        5: [49.2182, 11.0186, 3.77802],
        6: [68.2353, 39.2656, 2.02585, 1.70821, 2.8439],
        7: [22.2469, 3.55125, 2.04192],
        8: [1.71285, 6.08144, 30.3082],
        9: [33.2841, 20.0993]
    }

    # Flatten data for plotting
    x_vals = []
    y_vals = []
    stages = []
    
    # Define stage mapping based on visual grouping in the chart
    # Gen 0: Black (Not in legend)
    # Gen 1-2: early
    # Gen 3-5: mid
    # Gen 6: mid-late
    # Gen 7-9: late
    
    for gen, values in raw_data.items():
        for val in values:
            x_vals.append(gen)
            y_vals.append(val)
            if gen == 0:
                stages.append('zero')
            elif 1 <= gen <= 2:
                stages.append('early')
            elif 3 <= gen <= 5:
                stages.append('mid')
            elif gen == 6:
                stages.append('mid-late')
            elif gen >= 7:
                stages.append('late')

    df = pd.DataFrame({'Generation': x_vals, 'TPM': y_vals, 'Stage': stages})

    # ---------------------------------------------------------
    # 2. Statistical Calculations (Regression & CI)
    # ---------------------------------------------------------
    # While the table provides slope/intercept, we calculate the CI bands 
    # from the raw data to ensure the dashed lines match the data distribution.
    
    x = df['Generation'].values
    y = df['TPM'].values
    
    # Linear Regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    # Provided values from source table (to be exact with the line)
    # The table says: Slope -4.451, Y-intercept 53.99
    # We will use these for the main line to be faithful to the text data provided.
    provided_slope = -4.451
    provided_intercept = 53.99
    
    # Generate points for the regression line
    x_fit = np.linspace(0, 9, 100)
    y_fit = provided_slope * x_fit + provided_intercept

    # Calculate 95% Confidence Interval for the regression line
    # (Using calculated stats for the bands to ensure they wrap the points correctly)
    # Formula for CI of the mean response
    n = len(x)
    t_score = stats.t.ppf(0.975, df=n-2) # 95% CI
    
    # Mean of x
    x_mean = np.mean(x)
    # Sum of squared differences of x
    Sxx = np.sum((x - x_mean)**2)
    # Standard Error of the Estimate (Sy.x is given as 32.73 in table, let's calculate to be safe)
    residuals = y - (slope * x + intercept)
    sse = np.sum(residuals**2)
    sy_x = np.sqrt(sse / (n - 2)) # This should be close to 32.73
    
    # Calculate CI bands
    ci_interval = t_score * sy_x * np.sqrt(1/n + (x_fit - x_mean)**2 / Sxx)
    
    # We center the CI on the *provided* regression line for visual consistency
    y_ci_upper = y_fit + ci_interval
    y_ci_lower = y_fit - ci_interval

    # ---------------------------------------------------------
    # 3. Plotting
    # ---------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6, 4.5))

    # Color Palette
    colors = {
        'zero': 'black',
        'early': '#E040FB',   # Bright Magenta/Pink
        'mid': '#E69F00',     # Orange/Gold
        'mid-late': '#8C564B',# Brown
        'late': '#55A630'     # Green
    }

    # Plot Scatter Points
    # We plot them group by group to handle colors easily
    for stage in ['zero', 'early', 'mid', 'mid-late', 'late']:
        subset = df[df['Stage'] == stage]
        ax.scatter(subset['Generation'], subset['TPM'], 
                   color=colors[stage], 
                   s=50, 
                   alpha=1.0, 
                   edgecolors='none',
                   zorder=3)

    # Plot Regression Line
    ax.plot(x_fit, y_fit, color='black', linewidth=1.5, zorder=2)

    # Plot Confidence Interval Lines (Dashed)
    ax.plot(x_fit, y_ci_upper, color='black', linestyle='--', linewidth=1, zorder=2)
    ax.plot(x_fit, y_ci_lower, color='black', linestyle='--', linewidth=1, zorder=2)

    # ---------------------------------------------------------
    # 4. Styling and Formatting
    # ---------------------------------------------------------
    
    # Axis Limits and Ticks
    ax.set_xlim(-0.5, 9.5)
    ax.set_ylim(-50, 200) # Visual estimation
    
    ax.set_xticks(range(10))
    ax.set_yticks([0, 100, 200])
    
    # Custom Y-axis formatter for scientific notation (1x10^2)
    def scientific_formatter(x, pos):
        if x == 0:
            return "0"
        exponent = int(np.log10(x))
        coeff = int(x / (10**exponent))
        return r"${}\times10^{}$".format(coeff, exponent)
    
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(scientific_formatter))

    # Labels
    ax.set_xlabel("Generation", fontsize=12, fontweight='bold')
    ax.set_ylabel("Transcripts per million", fontsize=12, fontweight='bold')
    
    # Title
    ax.set_title("Slc7a11 (xCT)", fontsize=14, fontweight='bold', style='italic')
    # The "(xCT)" part is usually not italicized in gene nomenclature, but the image title is bold.
    # We will construct a title where Slc7a11 is italic and (xCT) is normal, but matplotlib bold applies to all.
    # Let's stick to the visual appearance: Bold centered text.
    
    # "h" label in top left
    fig.text(0.02, 0.92, "h", fontsize=18, fontweight='bold')

    # R-squared text
    # Positioned roughly at x=0.5, y=10 based on visual
    ax.text(0.5, -25, r"R$^2$ = 0.1304", fontsize=12)

    # Legend
    # Create custom handles for the legend (excluding 'zero')
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='early',
               markerfacecolor=colors['early'], markersize=8),
        Line2D([0], [0], marker='o', color='w', label='mid',
               markerfacecolor=colors['mid'], markersize=8),
        Line2D([0], [0], marker='o', color='w', label='mid-late',
               markerfacecolor=colors['mid-late'], markersize=8),
        Line2D([0], [0], marker='o', color='w', label='late',
               markerfacecolor=colors['late'], markersize=8)
    ]
    
    # Legend styling
    leg = ax.legend(handles=legend_elements, title="Stage", loc='upper right', 
                    frameon=True, edgecolor='black', fancybox=True)
    leg.get_title().set_fontweight('bold')
    leg.get_frame().set_linewidth(1.0)
    
    # Grid and Spines
    ax.grid(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.2)
    ax.spines['bottom'].set_linewidth(1.2)
    
    # Tick parameters
    ax.tick_params(axis='both', which='major', width=1.2, length=5, labelsize=10)

    # Layout adjustment
    plt.tight_layout()
    
    # Save
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    generate_chart(output_file)