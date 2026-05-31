import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from scipy import stats

def generate_chart(output_filename):
    # 1. Data Preparation
    # Extracting raw data points from the provided table (LN0 to LN9)
    # Columns Unnamed: 1 to Unnamed: 6 contain the TPM values.
    raw_data = {
        0: [109.65, 195.875, 109.068],
        1: [100.79, 114.565, 133.259, 133.781],
        2: [91.3753, 141.924, 77.3639],
        3: [99.6594, 151.292, 122.839],
        4: [140.845, 180.585, 125.153],
        5: [197.032, 183.955, 146.76],
        6: [151.958, 96.4668, 134.488, 81.04, 59.3186],
        7: [130.808, 121.361, 131.118],
        8: [136.999, 123.907, 98.043],
        9: [165.937, 131.635]
    }

    # Flatten data for plotting and regression
    x_vals = []
    y_vals = []
    
    # Create a list for plotting to handle colors easily
    plot_data = []

    for gen, tpms in raw_data.items():
        for tpm in tpms:
            if not np.isnan(tpm):
                x_vals.append(gen)
                y_vals.append(tpm)
                plot_data.append({'Gen': gen, 'TPM': tpm})

    df = pd.DataFrame(plot_data)

    # 2. Setup Plot
    fig, ax = plt.subplots(figsize=(7, 5.5))
    
    # Set background to white
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # 3. Define Colors and Categories
    # Based on the legend and visual inspection:
    # Gen 0: Black (Not in legend, but present on graph)
    # Gen 1-2: "early" (Magenta/Orchid)
    # Gen 3-5: "mid" (Orange/Goldenrod)
    # Gen 6: "mid-late" (Brown)
    # Gen 7-9: "late" (Green)

    colors = {
        'zero': '#000000',
        'early': '#E055D8',    # Bright Orchid/Magenta
        'mid': '#E69F35',      # Golden/Orange
        'mid_late': '#8B5A2B', # Brown
        'late': '#6AA84F'      # Green
    }

    # 4. Plot Scatter Points
    # We plot by group to assign colors
    
    # Gen 0
    ax.scatter(df[df['Gen'] == 0]['Gen'], df[df['Gen'] == 0]['TPM'], 
               color=colors['zero'], s=60, zorder=3, edgecolors='none')

    # Early (Gen 1-2)
    ax.scatter(df[df['Gen'].isin([1, 2])]['Gen'], df[df['Gen'].isin([1, 2])]['TPM'], 
               color=colors['early'], s=60, zorder=3, label='early', edgecolors='none')

    # Mid (Gen 3-5)
    ax.scatter(df[df['Gen'].isin([3, 4, 5])]['Gen'], df[df['Gen'].isin([3, 4, 5])]['TPM'], 
               color=colors['mid'], s=60, zorder=3, label='mid', edgecolors='none')

    # Mid-late (Gen 6)
    ax.scatter(df[df['Gen'] == 6]['Gen'], df[df['Gen'] == 6]['TPM'], 
               color=colors['mid_late'], s=60, zorder=3, label='mid-late', edgecolors='none')

    # Late (Gen 7-9)
    ax.scatter(df[df['Gen'].isin([7, 8, 9])]['Gen'], df[df['Gen'].isin([7, 8, 9])]['TPM'], 
               color=colors['late'], s=60, zorder=3, label='late', edgecolors='none')

    # 5. Regression Line and Confidence Intervals
    # Calculate linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(x_vals, y_vals)
    
    # Generate X points for the line (spanning the full axis)
    x_line = np.linspace(0, 9, 100)
    y_line = slope * x_line + intercept

    # Calculate Confidence Intervals
    # Formula for CI of the mean response
    # y_hat +/- t_crit * s_err * sqrt(1/n + (x - x_mean)^2 / Sxx)
    
    n = len(x_vals)
    x_mean = np.mean(x_vals)
    Sxx = np.sum((np.array(x_vals) - x_mean)**2)
    
    # Residuals
    residuals = np.array(y_vals) - (slope * np.array(x_vals) + intercept)
    # Mean Squared Error (Variance of residuals)
    mse = np.sum(residuals**2) / (n - 2)
    # Standard Error of the Estimate
    syx = np.sqrt(mse)
    
    # t-critical value for 95% CI (two-tailed)
    t_crit = stats.t.ppf(0.975, df=n-2)

    # Calculate bands
    ci_interval = t_crit * syx * np.sqrt(1/n + (x_line - x_mean)**2 / Sxx)
    lower_bound = y_line - ci_interval
    upper_bound = y_line + ci_interval

    # Plot Regression Line (Solid Black)
    ax.plot(x_line, y_line, color='black', linewidth=1.5, zorder=2)

    # Plot Confidence Intervals (Dashed Black)
    ax.plot(x_line, lower_bound, color='black', linestyle='--', linewidth=1.2, zorder=2)
    ax.plot(x_line, upper_bound, color='black', linestyle='--', linewidth=1.2, zorder=2)

    # 6. Formatting and Styling

    # Title
    ax.set_title('Acsl3', fontsize=16, fontweight='bold', style='italic', pad=15)

    # Axis Labels
    ax.set_xlabel('Generation', fontsize=14, fontweight='bold')
    ax.set_ylabel('Transcripts per million', fontsize=14, fontweight='bold')

    # Axis Ticks
    ax.set_xticks(range(10))
    ax.set_xlim(-0.5, 9.5)
    ax.set_ylim(0, 250)

    # Customizing Y-axis to scientific notation (2.5 x 10^2)
    class SciFormatter(ticker.Formatter):
        def __call__(self, x, pos=None):
            if x == 0:
                return "0.0"
            exponent = 2
            coeff = x / (10**exponent)
            return r"${:.1f}\times10^{{{}}}$".format(coeff, exponent)

    ax.yaxis.set_major_formatter(SciFormatter())
    
    # Make ticks thicker and point outwards/inwards as per standard matplotlib
    ax.tick_params(axis='both', which='major', labelsize=12, width=1.5, length=5, direction='out')
    
    # Make axis spines thicker
    for spine in ax.spines.values():
        spine.set_linewidth(1.5)

    # 7. Legend
    # Create custom legend handles to match the box style
    # The legend title is "Stage"
    # The box has a black border and rounded corners
    legend = ax.legend(title='Stage', loc='upper right', 
                       frameon=True, framealpha=1, edgecolor='black', 
                       fontsize=11, title_fontsize=12,
                       handletextpad=0.1, borderpad=0.6)
    
    # Bold the legend title
    plt.setp(legend.get_title(), fontweight='bold')
    # Bold the legend labels
    for text in legend.get_texts():
        text.set_fontweight('bold')
    
    # Thicken legend border
    legend.get_frame().set_linewidth(1.5)
    legend.get_frame().set_boxstyle("Round,pad=0.4,rounding_size=0.5")

    # 8. Add R-squared Text
    # The image shows R^2 = 0.002086
    # Positioned bottom left
    ax.text(0.03, 0.08, r'R$^2$ = 0.002086', transform=ax.transAxes, 
            fontsize=14, color='black')

    # Add 'g' label in top left corner (outside plot)
    fig.text(0.02, 0.92, 'g', fontsize=20, fontweight='bold')

    # Adjust layout
    plt.tight_layout()
    
    # Save output
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    generate_chart(output_file)