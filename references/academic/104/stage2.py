import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import matplotlib.ticker as ticker

def get_source_data():
    """
    Reconstructs the dataframe exactly from the provided Markdown table source data.
    """
    # X-axis values (Concentration log[RSL3])
    x_vals = [-2.0, -0.3, 0.0, 0.3979, 0.6989, 1.0]
    
    # Data organized by group. 
    # Structure: Key = Group Name, Value = List of lists (rows=concentrations, cols=replicates n1,n2,n3)
    # Note: Values are transcribed exactly from the provided source table.
    
    data = {
        "B16-F0 WT": [
            [100, 100, 100],                                # -2
            [106.5217, 104.9917, 129.6482],                 # -0.3
            [109.9638, 116.4725, 116.9179],                 # 0
            [86.23188, 89.35108, 92.62982],                 # 0.3979
            [61.23188, 55.24126, 53.76884],                 # 0.6989
            [36.41304, 31.78037, 30.48576]                  # 1
        ],
        "B16-F0 Fsp1 KO": [
            [100, 100, 100],                                # -2
            [110.9756, 105.0715, 107.0423],                 # -0.3
            [100.813, 89.20676, 99.37402],                  # 0
            [61.11111, 56.69701, 62.28482],                 # 0.3979
            [36.99187, 38.23147, 40.37559],                 # 0.6989
            [30.4878, 27.56827, 30.51643]                   # 1
        ],
        "LN7-1134BL WT": [
            [100, 100, 100],                                # -2
            [83.71336, 88.78101, 83.44444],                 # -0.3
            [70.03257, 76.05178, 74],                       # 0
            [44.84256, 48.00431, 51],                       # 0.3979
            [28.77307, 30.52859, 31.44444],                 # 0.6989
            [23.88708, 24.59547, 26.88889]                  # 1
        ],
        "LN7-1134BL Fsp1 KO": [
            [100, 100, 100],                                # -2
            [66.82879, 68.39482, 56.55022],                 # -0.3
            [58.85214, 55.2343, 43.34061],                  # 0
            [33.07393, 32.00399, 31.33188],                 # 0.3979
            [21.49805, 25.92223, 21.61572],                 # 0.6989
            [17.89883, 17.54736, 16.48472]                  # 1
        ]
    }
    
    return x_vals, data

def sigmoid_func(x, Top, Bottom, LogEC50, HillSlope):
    """
    4-Parameter Logistic (4PL) Equation for Dose-Response.
    """
    return Bottom + (Top - Bottom) / (1 + 10**((LogEC50 - x) * HillSlope))

def main():
    # Handle output filename
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]

    # Load Data
    x_vals, raw_data = get_source_data()
    x_arr = np.array(x_vals)

    # Setup Plot
    fig, ax = plt.subplots(figsize=(4, 5)) # Portrait aspect ratio similar to source
    
    # Styling Configuration
    # Map: Group Name -> (Color, Marker, LineStyle, MarkerFaceColor, MarkerEdgeColor)
    style_map = {
        "B16-F0 WT": {
            "color": "black", "marker": "o", "ls": "-", 
            "mfc": "black", "mec": "black", "label": "B16-F0 WT"
        },
        "B16-F0 Fsp1 KO": {
            "color": "black", "marker": "o", "ls": "--", 
            "mfc": "white", "mec": "black", "label": r"B16-F0 $\it{Fsp1}$ KO"
        },
        "LN7-1134BL WT": {
            "color": "gray", "marker": "^", "ls": "-", 
            "mfc": "gray", "mec": "gray", "label": "LN7-1134BL WT"
        },
        "LN7-1134BL Fsp1 KO": {
            "color": "#87CEFA", "marker": "v", "ls": "--", # Light Sky Blue
            "mfc": "white", "mec": "#87CEFA", "label": r"LN7-1134BL $\it{Fsp1}$ KO"
        }
    }

    # Plotting Loop
    for group_name, replicates in raw_data.items():
        style = style_map[group_name]
        
        # Calculate Mean and SD
        replicates_arr = np.array(replicates)
        y_mean = np.mean(replicates_arr, axis=1)
        y_std = np.std(replicates_arr, axis=1, ddof=1) # Sample standard deviation
        
        # 1. Plot Error Bars and Markers
        # zorder is high to put markers on top of lines
        ax.errorbar(x_arr, y_mean, yerr=y_std, 
                    fmt=style['marker'], 
                    color=style['color'],
                    markerfacecolor=style['mfc'],
                    markeredgecolor=style['mec'],
                    markeredgewidth=1.5,
                    elinewidth=1.5,
                    capsize=4,
                    markersize=8,
                    linestyle='None', # Don't connect points with straight lines
                    zorder=10)

        # 2. Curve Fitting
        # Initial guesses: Top=100, Bottom=20, LogEC50=0, HillSlope=1
        p0 = [100, 20, 0.0, 1.0]
        
        # Bounds to keep fit reasonable
        # Top: 80-130, Bottom: 0-50, LogEC50: -2 to 1, HillSlope: 0.1 to 5
        bounds = ([80, 0, -2, 0.1], [130, 50, 1.5, 10])
        
        try:
            popt, _ = curve_fit(sigmoid_func, x_arr, y_mean, p0=p0, bounds=bounds, maxfev=5000)
            
            # Generate smooth x for curve
            x_smooth = np.linspace(-2, 1.1, 200)
            y_smooth = sigmoid_func(x_smooth, *popt)
            
            # Plot the fitted curve
            ax.plot(x_smooth, y_smooth, 
                    color=style['color'], 
                    linestyle=style['ls'], 
                    linewidth=2,
                    zorder=5)
            
        except Exception as e:
            print(f"Could not fit curve for {group_name}: {e}")
            # Fallback: simple interpolation if fit fails (unlikely here)
            ax.plot(x_arr, y_mean, color=style['color'], linestyle=style['ls'])

    # Custom Legend Construction
    # We construct handles manually to match the visual style (marker + line)
    from matplotlib.lines import Line2D
    legend_elements = []
    for group_name, style in style_map.items():
        line = Line2D([0], [0], 
                      color=style['color'], 
                      lw=2, 
                      linestyle=style['ls'],
                      marker=style['marker'], 
                      markerfacecolor=style['mfc'],
                      markeredgecolor=style['mec'],
                      markeredgewidth=1.5,
                      markersize=8,
                      label=style['label'])
        legend_elements.append(line)

    # Legend placement
    ax.legend(handles=legend_elements, 
              loc='lower left', 
              frameon=False, 
              fontsize=11,
              handlelength=1.5,
              borderpad=0.2,
              labelspacing=0.4)

    # Axis Formatting
    ax.set_xlim(-2.0, 1.1)
    ax.set_ylim(0, 135) # Slightly higher to accommodate error bars
    
    # Ticks
    ax.set_xticks([-2, -1, 0, 1])
    ax.set_yticks([0, 25, 50, 75, 100, 125])
    
    # Labels
    ax.set_xlabel(r"log[RSL3 ($\mu$M)]", fontsize=12, labelpad=5)
    ax.set_ylabel("Relative viability (%)", fontsize=12, labelpad=5)
    
    # Tick params
    ax.tick_params(axis='both', which='major', labelsize=11, width=1, length=5)
    
    # Spines (Top and Right off)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1)

    # Add Figure Label "a"
    # Placed in figure coordinates relative to axes
    ax.text(-0.2, 1.05, 'a', transform=ax.transAxes, 
            fontsize=20, fontweight='bold', va='top', ha='right')

    # Layout adjustment
    plt.tight_layout()
    
    # Save
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_file}")

if __name__ == "__main__":
    main()