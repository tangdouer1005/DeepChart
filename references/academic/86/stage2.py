import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from matplotlib.lines import Line2D

def main():
    # 1. Handle Output Filename
    output_filename = "output.png"
    if len(sys.argv) > 1:
        output_filename = sys.argv[1]

    # 2. Source Data Extraction
    # Data manually extracted from the provided Markdown table
    raw_data = {
        0: [22.24282, 24.3151, 33.77154006],
        1: [29.69386628, 35.7741, 26.7349662, 17.4729],
        2: [27.76888379, 31.5131, 34.78990566],
        3: [21.63897886, 18.9419, 24.82969103],
        4: [22.8033279, 18.9751, 16.29963747],
        5: [14.40172411, 15.255, 15.71326136],
        6: [13.65891836, 14.7051, 11.66789317, 26.5091, 12.755],
        7: [9.399249219, 13.8694, 12.82817673],
        8: [9.341106996, 11.7371, 12.8697357],
        9: [13.1699329, 17.5931]
    }

    # Flatten data into a DataFrame
    data_rows = []
    for gen, values in raw_data.items():
        for val in values:
            if not np.isnan(val):
                data_rows.append({'Generation': gen, 'TPM': val})
    
    df = pd.DataFrame(data_rows)

    # 3. Define Visual Styles
    # Colors mapped to stages based on the chart legend and points
    color_map = {
        0: '#000000',                     # Gen 0 (Black)
        1: '#E055E0', 2: '#E055E0',       # Early (Magenta)
        3: '#F59E3F', 4: '#F59E3F', 5: '#F59E3F', # Mid (Orange)
        6: '#8B5A2B',                     # Mid-late (Brown)
        7: '#458B25', 8: '#458B25', 9: '#458B25'  # Late (Green)
    }
    
    df['Color'] = df['Generation'].map(color_map)

    # 4. Statistical Calculations (using numpy/scipy instead of statsmodels)
    x = df['Generation'].values
    y = df['TPM'].values
    n = len(x)

    # Linear Regression
    slope, intercept = np.polyfit(x, y, 1)
    
    # Calculate R-squared
    y_pred = slope * x + intercept
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)

    # Calculate Confidence Intervals
    # Generate smooth x for plotting lines
    x_plot = np.linspace(0, 9, 100)
    y_plot = slope * x_plot + intercept

    # Standard Error of the Estimate
    # dof = n - 2
    dof = n - 2
    t_value = stats.t.ppf(0.975, dof) # 95% CI (two-tailed)
    
    s_err = np.sqrt(ss_res / dof)
    
    # Calculate CI bands for the regression line
    # Formula: y_hat +/- t * s_err * sqrt(1/n + (x - x_mean)^2 / Sxx)
    x_mean = np.mean(x)
    s_xx = np.sum((x - x_mean) ** 2)
    
    ci_width = t_value * s_err * np.sqrt(1/n + (x_plot - x_mean)**2 / s_xx)
    
    lower_bound = y_plot - ci_width
    upper_bound = y_plot + ci_width

    # 5. Plotting
    fig, ax = plt.subplots(figsize=(6, 5))

    # Plot Confidence Intervals (Upper and Lower bounds)
    # The chart shows these as solid black lines, slightly thinner than the main regression line
    ax.plot(x_plot, lower_bound, color='black', linestyle='-', linewidth=1.2, zorder=1)
    ax.plot(x_plot, upper_bound, color='black', linestyle='-', linewidth=1.2, zorder=1)
    
    # Plot Regression Line (Center)
    ax.plot(x_plot, y_plot, color='black', linewidth=1.5, zorder=2)

    # Plot Scatter Points
    ax.scatter(df['Generation'], df['TPM'], c=df['Color'], s=60, alpha=1.0, zorder=3, edgecolors='none')

    # 6. Formatting and Styling
    
    # Axes Limits and Ticks
    ax.set_xlim(-0.2, 9.5)
    ax.set_ylim(0, 40)
    ax.set_xticks(range(10))
    ax.set_yticks([0, 10, 20, 30, 40])
    
    # Labels
    ax.set_xlabel("Generation", fontsize=14, labelpad=8)
    ax.set_ylabel(r"$\it{Gclc}$ TPM", fontsize=14, labelpad=8) # Italicize gene name
    
    # Tick styling (outward facing ticks)
    ax.tick_params(axis='both', which='major', direction='out', length=6, width=1, labelsize=12)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add R-squared text
    # Using the calculated value
    r_squared_text = f"$R^2 = {r_squared:.4f}$"
    ax.text(0.5, 5, r_squared_text, fontsize=14)

    # Add Figure Label "b"
    # Positioned in figure coordinates to be top-left outside axes
    fig.text(0.02, 0.92, 'b', fontsize=24, fontweight='bold')

    # 7. Custom Legend
    # The legend groups specific generations. 
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Early',
               markerfacecolor='#E055E0', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='Mid',
               markerfacecolor='#F59E3F', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='Mid-late',
               markerfacecolor='#8B5A2B', markersize=10),
        Line2D([0], [0], marker='o', color='w', label='Late',
               markerfacecolor='#458B25', markersize=10),
    ]

    # Legend positioning
    legend = ax.legend(handles=legend_elements, title='Stage', 
                       loc='upper right', frameon=False, 
                       fontsize=12, title_fontsize=14,
                       bbox_to_anchor=(1.0, 1.0), handletextpad=0.1)
    
    # Align legend title to the left
    legend._legend_box.align = "left"

    plt.tight_layout()
    
    # 8. Save Output
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    main()