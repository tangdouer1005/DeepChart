import sys
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import matplotlib.ticker as ticker

def main():
    # 1. Handle Output Filename
    output_filename = "output.png"
    if len(sys.argv) > 1:
        output_filename = sys.argv[1]

    # 2. Source Data Extraction
    # Data manually extracted from the provided Markdown table to ensure integrity.
    # X-axis: ML210 [log] (mapped to log[RSL3] in chart)
    x_data = np.array([-2.0, -0.3, 0.0, 0.3979, 0.6989, 1.0])

    # LN7 1134BL WT Data (Columns 7, 8, 9)
    # Rows correspond to the x_data points
    wt_replicates = np.array([
        [100.0, 100.0, 100.0],                      # -2
        [102.763158, 100.938338, 99.6083551],       # -0.3
        [100.657895, 99.463807, 94.1253264],        # 0
        [90.7894737, 92.4932976, 88.381201],        # 0.3979
        [83.1578947, 82.30563, 86.8146214],         # 0.6989
        [85.0, 76.1394102, 80.5483029]              # 1
    ])

    # LN7 1134BL FSP1 KO Data (Columns 10, 11, 12)
    ko_replicates = np.array([
        [100.0, 100.0, 100.0],                      # -2
        [86.3945578, 82.860262, 89.088729],         # -0.3
        [80.1587302, 78.0567686, 86.0911271],       # 0
        [68.1405896, 67.3580786, 76.0191847],       # 0.3979
        [65.9863946, 66.7030568, 70.263789],        # 0.6989
        [59.2970522, 54.5851528, 63.0695444]        # 1
    ])

    # Calculate Mean and Standard Deviation
    wt_mean = np.mean(wt_replicates, axis=1)
    wt_std = np.std(wt_replicates, axis=1, ddof=1)

    ko_mean = np.mean(ko_replicates, axis=1)
    ko_std = np.std(ko_replicates, axis=1, ddof=1)

    # 3. Curve Fitting Logic (4-Parameter Logistic Regression)
    # This creates the smooth dose-response curves seen in the image
    def logistic_curve(x, top, bottom, ec50, hill_slope):
        return bottom + (top - bottom) / (1 + 10**((ec50 - x) * hill_slope))

    # Generate smooth X for plotting lines
    x_smooth = np.linspace(-2, 1.2, 200)

    # Fit WT
    # Initial guesses: Top=100, Bottom=0, EC50=0.5, Slope=1
    p0_wt = [100, 0, 0.5, 1]
    try:
        popt_wt, _ = curve_fit(logistic_curve, x_data, wt_mean, p0=p0_wt, maxfev=5000)
        y_smooth_wt = logistic_curve(x_smooth, *popt_wt)
    except:
        # Fallback if fit fails (unlikely with this data)
        y_smooth_wt = np.interp(x_smooth, x_data, wt_mean)

    # Fit KO
    p0_ko = [100, 0, 0, 1]
    try:
        popt_ko, _ = curve_fit(logistic_curve, x_data, ko_mean, p0=p0_ko, maxfev=5000)
        y_smooth_ko = logistic_curve(x_smooth, *popt_ko)
    except:
        y_smooth_ko = np.interp(x_smooth, x_data, ko_mean)

    # 4. Plotting Setup
    fig, ax = plt.subplots(figsize=(5, 6))

    # Colors and Styles matching the image
    # WT: Black solid line, Grey filled triangle up
    # KO: Light Blue dashed line, Open/White filled triangle down (mimicking KO1/KO2 style)
    
    color_wt = 'black'
    color_ko = '#89CFF0' # Light sky blue

    # --- Plot WT Series ---
    # Smooth Line
    ax.plot(x_smooth, y_smooth_wt, color=color_wt, linewidth=2.5, zorder=1)
    # Error Bars & Markers
    ax.errorbar(x_data, wt_mean, yerr=wt_std, fmt='^', 
                color=color_wt, 
                ecolor='gray', # Error bar color
                elinewidth=1.5, 
                capsize=4, 
                markersize=10, 
                markerfacecolor='gray', 
                markeredgecolor='black',
                markeredgewidth=1,
                zorder=2,
                label='LN9-1315BL WT') # Using Image label for visual reproduction

    # --- Plot KO Series ---
    # Smooth Line
    ax.plot(x_smooth, y_smooth_ko, color=color_ko, linewidth=2.5, linestyle='--', zorder=1)
    # Error Bars & Markers
    ax.errorbar(x_data, ko_mean, yerr=ko_std, fmt='v', # Triangle down
                color=color_ko, 
                ecolor=color_ko, 
                elinewidth=1.5, 
                capsize=4, 
                markersize=10, 
                markerfacecolor='white', 
                markeredgecolor=color_ko,
                markeredgewidth=1.5,
                zorder=2,
                label='LN9-1315BL $\it{Fsp1}$ KO 1') # Using Image label, italicizing gene name

    # Note: The source data only contains one KO condition for LN7. 
    # The image shows two KO lines. We plot the available data mapped to the KO1 style.

    # 5. Styling and Layout
    
    # Axis Limits
    ax.set_xlim(-2.2, 1.2)
    ax.set_ylim(0, 110)

    # Axis Ticks
    ax.set_xticks([-2, -1, 0, 1])
    ax.set_yticks([0, 25, 50, 75, 100])
    
    # Tick Parameters
    ax.tick_params(axis='both', which='major', labelsize=14, length=6, width=1)

    # Axis Labels
    ax.set_xlabel('log[RSL3 (µM)]', fontsize=16, labelpad=10)
    ax.set_ylabel('Relative viability (%)', fontsize=16, labelpad=10)

    # Spines (Box style: remove top and right)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1)

    # Legend
    # Customizing legend to match the bottom-left/center placement and style
    legend = ax.legend(loc='lower left', frameon=False, fontsize=14, handletextpad=0.5)
    
    # Title / Figure Label "b"
    # Placed outside the axes to the top left
    ax.text(-0.15, 1.05, 'b', transform=ax.transAxes, 
            fontsize=24, fontweight='bold', va='top', ha='right')

    # 6. Save Output
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    main()