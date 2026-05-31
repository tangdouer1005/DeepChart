import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

def generate_chart(output_filename):
    # ---------------------------------------------------------
    # 1. Data Preparation
    # ---------------------------------------------------------
    # Extracted directly from the provided Markdown table (Source Data)
    # Keys are Generations (LN0-LN9 -> 0-9), Values are the Y-values (Fsp1 TPM)
    raw_data = {
        0: [5.86566848, 8.15498, 8.072314491],
        1: [10.08575711, 10.8043, 8.624570815, 7.92934],
        2: [8.299775685, 10.4507, 9.935653318],
        3: [10.21662252, 8.68885, 12.23267],
        4: [13.14692214, 11.2483, 17.66730274],
        5: [11.23320993, 11.317, 14.40373849],
        6: [16.84068224, 20.4273, 9.949043375, 10.8217, 10.8965],
        7: [16.60248485, 12.4377, 13.09089132],
        8: [8.269548139, 12.3538, 17.2109045],
        9: [9.73430569, 16.1348]
    }

    # Flatten data for plotting and calculations
    x_vals = []
    y_vals = []
    
    # Define categories for coloring based on the chart legend and visual inspection
    # Gen 0: Black (Not in legend, but present in chart)
    # Gen 1-2: Early (Pink)
    # Gen 3-5: Mid (Orange)
    # Gen 6: Mid-late (Brown)
    # Gen 7-9: Late (Green)
    
    data_points = []

    for gen, values in raw_data.items():
        for val in values:
            if not np.isnan(val):
                x_vals.append(gen)
                y_vals.append(val)
                
                # Assign category
                if gen == 0:
                    cat = 'Zero'
                    color = 'black'
                elif 1 <= gen <= 2:
                    cat = 'Early'
                    color = '#E040FB' # Bright Pink/Magenta
                elif 3 <= gen <= 5:
                    cat = 'Mid'
                    color = '#F5A623' # Orange
                elif gen == 6:
                    cat = 'Mid-late'
                    color = '#8B572A' # Brown
                else: # 7-9
                    cat = 'Late'
                    color = '#417505' # Green
                
                data_points.append({'x': gen, 'y': val, 'cat': cat, 'color': color})

    df = pd.DataFrame(data_points)

    # ---------------------------------------------------------
    # 2. Statistical Calculations (Matching Source Data)
    # ---------------------------------------------------------
    # The table provides specific regression stats. We use these to ensure fidelity.
    slope = 0.676
    intercept = 8.724
    r_squared = 0.3089
    syx = 2.879  # Sy.x (Standard Error of Estimate) from table
    
    # To draw the confidence intervals (dashed lines), we need the formula for 
    # the Confidence Interval of the Mean Response.
    # Formula: y_hat +/- t * Syx * sqrt(1/n + (x - x_bar)^2 / Sxx)
    
    x_arr = np.array(x_vals)
    n = len(x_arr) # Should be 32 based on table
    x_bar = np.mean(x_arr)
    s_xx = np.sum((x_arr - x_bar)**2)
    
    # t-value for 95% confidence, df = n - 2
    # The table mentions DFd = 30
    t_val = stats.t.ppf(0.975, n - 2)

    # Generate line data
    x_line = np.linspace(0, 9, 100)
    y_line = slope * x_line + intercept
    
    # Calculate CI bands
    ci_offset = t_val * syx * np.sqrt(1/n + (x_line - x_bar)**2 / s_xx)
    y_upper = y_line + ci_offset
    y_lower = y_line - ci_offset

    # ---------------------------------------------------------
    # 3. Plotting
    # ---------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6, 5))

    # A. Plot Scatter Points
    # We plot by group to handle the legend correctly, excluding Gen 0 from legend
    groups = [
        ('Early', '#E040FB'), 
        ('Mid', '#F5A623'), 
        ('Mid-late', '#8B572A'), 
        ('Late', '#417505')
    ]
    
    # Plot Gen 0 first (no legend entry)
    gen0 = df[df['cat'] == 'Zero']
    ax.scatter(gen0['x'], gen0['y'], color='black', s=60, zorder=3, edgecolors='none')

    # Plot others
    for label, color in groups:
        subset = df[df['cat'] == label]
        ax.scatter(subset['x'], subset['y'], color=color, label=label, s=60, zorder=3, edgecolors='none')

    # B. Plot Regression Line
    ax.plot(x_line, y_line, color='black', linewidth=1.5, zorder=2)

    # C. Plot Confidence Intervals
    ax.plot(x_line, y_upper, color='black', linestyle='--', linewidth=1, zorder=2)
    ax.plot(x_line, y_lower, color='black', linestyle='--', linewidth=1, zorder=2)

    # ---------------------------------------------------------
    # 4. Styling
    # ---------------------------------------------------------
    
    # Axis Limits and Ticks
    ax.set_xlim(-0.5, 9.5)
    ax.set_ylim(0, 20)
    ax.set_xticks(range(10))
    ax.set_yticks(range(0, 21, 5))
    
    # Labels
    ax.set_xlabel('Generation', fontsize=12, labelpad=8)
    # Using mathtext for italic Fsp1
    ax.set_ylabel(r'$\it{Fsp1}$ TPM', fontsize=12, labelpad=8)
    
    # Title/Tag (The "c" in the corner)
    ax.text(-0.12, 1.0, 'c', transform=ax.transAxes, fontsize=20, fontweight='bold', va='top', ha='left')

    # R-squared text
    ax.text(0.5, 3, f'$R^2 = {r_squared}$', fontsize=12)

    # Legend
    # Remove frame, set title
    legend = ax.legend(title='Stage', loc='upper left', frameon=False, fontsize=11, title_fontsize=12, handletextpad=0.1)
    legend._legend_box.align = "left"
    
    # Spines (Remove top and right)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Tick styling
    ax.tick_params(axis='both', which='major', labelsize=11, length=5, width=1)

    # Layout adjustment
    plt.tight_layout()

    # ---------------------------------------------------------
    # 5. Save Output
    # ---------------------------------------------------------
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    # Handle command line argument for output filename
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        output_file = "output.png"
    
    generate_chart(output_file)