import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

def get_source_data():
    """
    Returns the raw data as a CSV string derived from the provided Markdown table.
    """
    csv_data = """
Unnamed: 0,G11,Unnamed: 2,Unnamed: 3,Unnamed: 4,Unnamed: 5,Unnamed: 6,Unnamed: 7,Unnamed: 8,Unnamed: 9,Unnamed: 10,Unnamed: 11,Unnamed: 12,Unnamed: 13,Unnamed: 14,Unnamed: 15,Unnamed: 16,Unnamed: 17,Unnamed: 18,Unnamed: 19,Unnamed: 20
Log [NT] M,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,Log [SR142948A] M,nan,nan,nan,nan,nan,nan,nan,nan,nan
nan,10-27-2022,10-27-2022,10-27-2022,10-28-22,10-28-22,10-28-22,1-26-23,1-26-23,1-26-23,nan,nan,10-27-2022,10-27-2022,10-27-2022,10-28-22,10-28-22,10-28-22,1-26-23,1-26-23,1-26-23
1e-05,-0.30303,-0.30282,-0.28583,-0.30089,-0.28729,-0.30189,-0.25323,-0.25536,-0.25034,nan,0.0001,0.00041,0.015236,0.000381,-0.02693,-0.03254,-0.03043,-0.00501,-0.01106,-0.01598
1e-06,-0.31003,-0.29578,-0.29356,-0.30663,-0.28465,-0.30822,-0.24806,-0.25629,-0.25088,nan,1e-05,0.020088,0.002293,0.012814,-0.00333,-0.02885,-0.02846,-0.01216,-0.00682,-0.00417
1e-07,-0.33322,-0.31046,-0.33121,-0.32247,-0.31273,-0.30752,-0.26004,-0.26857,-0.26028,nan,1e-06,0.026049,-0.00424,0.034537,-0.02108,-0.03401,-0.01226,0.011219,0.000242,-0.00854
1e-08,-0.26646,-0.21203,-0.22524,-0.29949,-0.28921,-0.25745,-0.27731,-0.29487,-0.28025,nan,1e-07,-0.0117,-0.01407,0.004829,-0.01594,-0.00954,-0.01617,-0.00368,0.004866,-0.01149
1e-09,-0.07168,-0.06128,-0.05854,-0.06981,-0.06586,-0.0414,-0.18718,-0.22246,-0.22065,nan,1e-08,0.031768,-0.0068,0.031635,-0.00072,-0.00809,-0.00801,-0.01716,-0.02464,-0.00803
1e-10,-0.0109,0.013042,0.00957,-0.00538,0.003219,0.021555,-0.00899,-0.02872,-0.02977,nan,1e-09,-0.00107,0.003729,0.011285,-0.01865,-0.01439,0.005616,-0.00749,-0.00187,-0.0012
1e-11,-0.0248,-0.00236,0.000497,-0.00841,0.019556,0.027191,0.011828,-0.01373,-0.00675,nan,1e-10,0.002425,-0.02784,0.006075,0.011147,-0.01826,0.007284,-0.00457,-0.01237,-0.00729
1e-12,0,0,0,0,0,0,0,0,0,nan,1e-12,0,0,0,0,0,0,0,0,0
nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan
nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan
Log [SBI-553] M,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,Log [PD149163] M,nan,nan,nan,nan,nan,nan,nan,nan,nan
nan,10-27-2022,10-27-2022,10-27-2022,10-28-22,10-28-22,10-28-22,1-26-23,1-26-23,1-26-23,nan,nan,1-26-23,1-26-23,3-2-23,3-2-23,3-2-23,5-26-23,5-26-23,5-26-23,nan
3e-05,0.005378,0.042057,0.007707,0.020865,0.0239,0.006675,0.004195,0.001597,-0.00743,nan,3e-05,-0.27204,-0.29712,-0.29818,-0.29176,-0.2658,nan,nan,nan,nan
1e-05,0.023098,0.043557,0.015936,0.031693,-0.0037,0.006687,0.019648,0.003516,0.010053,nan,1e-05,-0.26599,-0.28802,-0.29799,-0.28387,-0.26445,nan,nan,nan,nan
3e-06,-0.00561,0.052117,0.020797,0.015179,0.012205,-0.08769,0.011891,-0.00562,-0.0053,nan,3e-06,-0.26244,-0.27857,-0.29463,-0.2905,-0.23894,-0.25836,-0.25825,-0.27552,nan
1e-06,0.021415,0.015621,0.006367,0.002298,-0.0067,-0.00221,0.004357,-0.00415,-0.00662,nan,1e-06,-0.26427,-0.27816,-0.25785,-0.25866,-0.21631,-0.21645,-0.25024,-0.21577,nan
3e-07,-0.01279,0.015919,-0.00114,0.000707,-0.00339,-0.0035,0.011367,-0.00365,0.003233,nan,3e-07,-0.20815,-0.23486,-0.21603,-0.21307,-0.19013,-0.16447,-0.15812,-0.17147,nan
1e-07,-0.00507,0.013791,-0.00432,-0.00635,-0.02843,0.004074,0.004932,-0.02226,-0.00432,nan,1e-07,-0.12406,-0.17286,-0.13609,-0.13711,-0.16775,-0.08329,-0.09085,-0.11236,nan
1e-12,0,0,0,0,0,0,0,0,0,nan,3e-08,nan,nan,nan,nan,nan,-0.02941,-0.00624,-0.02679,nan
nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,1e-08,nan,nan,nan,nan,nan,-0.0031,-0.02306,0.012733,nan
nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,3e-09,nan,nan,nan,nan,nan,0.000368,0.018503,0.009733,nan
nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,1e-12,0,0,0,0,0,0,0,0,nan
"""
    return csv_data

def sigmoid(x, Top, Bottom, LogEC50, HillSlope):
    """4-parameter logistic function."""
    return Bottom + (Top - Bottom) / (1 + 10**((LogEC50 - x) * HillSlope))

def process_data_block(df, row_start, row_end, x_col_idx, y_col_start, y_col_end):
    """
    Extracts a block of data, cleans it, and calculates stats.
    """
    # Extract subset
    subset = df.iloc[row_start:row_end, [x_col_idx] + list(range(y_col_start, y_col_end))]
    
    # Convert to numeric, coercing errors to NaN
    subset = subset.apply(pd.to_numeric, errors='coerce')
    
    # Drop rows where X is NaN
    subset = subset.dropna(subset=[subset.columns[0]])
    
    # Extract X and Y
    x_vals = subset.iloc[:, 0].values
    y_data = subset.iloc[:, 1:].values
    
    # Log transform X (Concentration)
    # Handle 0 or negative values if any (though concentration shouldn't be <= 0)
    # 1e-12 is the smallest value, so log10 is safe.
    x_log = np.log10(x_vals)
    
    # Calculate Mean and SEM
    # Note: The chart Y-axis is positive (0 to 0.6), but data is negative (-0.3 to 0).
    # We multiply by -1 to match the visual representation.
    y_mean = np.nanmean(y_data, axis=1) * -1
    y_sem = np.nanstd(y_data, axis=1, ddof=1) / np.sqrt(np.sum(~np.isnan(y_data), axis=1))
    
    return x_log, y_mean, y_sem

def main():
    # Handle output filename
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]

    # Load data
    csv_content = get_source_data()
    df = pd.read_csv(io.StringIO(csv_content), header=None)

    # Define data blocks based on the table structure
    # Block 1: NT (Top Left)
    # Rows 2 to 10 (exclusive of 10 in slice logic, but row 9 is 1e-12)
    # Indices in pandas: 2 to 10
    x_nt, y_nt, sem_nt = process_data_block(df, 2, 10, 0, 1, 10)

    # Block 2: SR142948A (Top Right)
    # Rows 2 to 10
    x_sr, y_sr, sem_sr = process_data_block(df, 2, 10, 11, 12, 21)

    # Block 3: SBI-553 (Bottom Left)
    # Rows 14 to 21 (Row 20 is 1e-12)
    x_sbi, y_sbi, sem_sbi = process_data_block(df, 14, 21, 0, 1, 10)

    # Block 4: PD149163 (Bottom Right)
    # Rows 14 to 25 (Row 24 is 1e-12)
    x_pd, y_pd, sem_pd = process_data_block(df, 14, 25, 11, 12, 21)

    # Setup Plot
    fig, ax = plt.subplots(figsize=(5, 4.5))
    
    # Styling constants
    # Colors approximated from image
    color_nt = '#0000AA'      # Dark Blue
    color_pd = '#44AA77'      # Sea Green
    color_sr = '#AA00AA'      # Magenta/Purple
    color_sbi = '#FF9900'     # Orange
    
    marker_size = 8
    line_width = 2
    cap_size = 3

    # Helper to plot and fit
    def plot_series(x, y, sem, color, label, fit=True):
        # Plot points with error bars
        ax.errorbar(x, y, yerr=sem, fmt='o', color=color, 
                    markersize=marker_size, elinewidth=1.5, capsize=cap_size, 
                    label=label, zorder=5)
        
        if fit:
            try:
                # Initial guesses: Top=0.3, Bottom=0, LogEC50=midpoint, Hill=1
                p0 = [max(y), min(y), np.median(x), 1.0]
                # Bounds to keep things reasonable
                bounds = ([-0.1, -0.1, -14, 0.1], [1.0, 1.0, -3, 5])
                
                popt, _ = curve_fit(sigmoid, x, y, p0=p0, maxfev=5000)
                
                # Generate smooth line
                x_smooth = np.linspace(min(x), max(x), 100)
                y_smooth = sigmoid(x_smooth, *popt)
                ax.plot(x_smooth, y_smooth, color=color, linewidth=line_width, zorder=4)
            except:
                # Fallback if fit fails (e.g., flat line)
                ax.plot(x, y, color=color, linewidth=line_width, zorder=4)
        else:
            # Just connect lines for flat data if we prefer not to force a sigmoid
            ax.plot(x, y, color=color, linewidth=line_width, zorder=4)

    # Plot NT (Blue) - Sigmoidal
    plot_series(x_nt, y_nt, sem_nt, color_nt, "NT")

    # Plot PD (Green) - Sigmoidal
    plot_series(x_pd, y_pd, sem_pd, color_pd, "PD149163")

    # Plot SR (Purple) - Flat
    # The data is essentially noise around 0. A sigmoid fit might be unstable or produce weird shapes.
    # We will try to fit, but if the amplitude (max-min) is very small, we might just plot a line.
    # However, for visual consistency with the request "reproduce the chart", 
    # and the chart shows flat lines, a linear interpolation or a constrained fit is best.
    # Let's just use the generic plotter which attempts fit.
    plot_series(x_sr, y_sr, sem_sr, color_sr, "SR142948A")

    # Plot SBI (Orange) - Flat
    plot_series(x_sbi, y_sbi, sem_sbi, color_sbi, "SBI-553")

    # Axis formatting
    ax.set_xlim(-13, -3)
    ax.set_ylim(-0.1, 0.6)
    
    # Dashed line at 0
    ax.axhline(0, color='black', linestyle='--', linewidth=0.8, zorder=1)

    # Ticks styling
    ax.tick_params(direction='in', length=4, width=1, labelsize=14)
    ax.set_xticks([-12, -10, -8, -6, -4])
    ax.set_yticks([0, 0.2, 0.4, 0.6])
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add Text "G11"
    ax.text(0.1, 0.9, "G$_{11}$", transform=ax.transAxes, fontsize=16, verticalalignment='top')

    # Save output
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)

if __name__ == "__main__":
    main()