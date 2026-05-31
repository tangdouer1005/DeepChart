import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def main():
    # 1. Handle Output Filename
    output_filename = "output.png"
    if len(sys.argv) > 1:
        output_filename = sys.argv[1]

    # 2. Source Data
    # Hardcoding the data from the provided Markdown table to ensure integrity.
    # Structure: Current Density (mA/cm2) -> [Rep1, Rep2, Rep3]
    
    data_20c = {
        50:  [-1.95, -1.95, -1.97],
        100: [-2.02, -2.00, -2.04],
        200: [-2.15, -2.14, -2.17],
        300: [-2.23, -2.21, -2.25],
        400: [-2.28, -2.27, -2.30],
        500: [-2.33, -2.31, -2.35],
        600: [-2.37, -2.35, -2.41],
        700: [-2.42, -2.39, -2.46],
        800: [-2.46, -2.44, -2.50]
    }

    data_35c = {
        50:  [-1.85, -1.85, -1.87],
        100: [-1.93, -1.93, -1.95],
        200: [-2.00, -2.01, -2.02],
        300: [-2.07, -2.08, -2.08],
        400: [-2.13, -2.14, -2.14],
        500: [-2.17, -2.18, -2.18],
        600: [-2.21, -2.22, -2.22],
        700: [-2.25, -2.26, -2.25],
        800: [-2.30, -2.31, -2.31]
    }

    data_50c = {
        50:  [-1.80, -1.84, -1.83],
        100: [-1.89, -1.90, -1.90],
        200: [-1.95, -1.96, -1.95],
        300: [-2.03, -2.02, -2.01],
        400: [-2.08, -2.09, -2.06],
        500: [-2.13, -2.15, -2.11],
        600: [-2.17, -2.19, -2.15],
        700: [-2.21, -2.23, -2.19],
        800: [-2.24, -2.27, -2.24]
    }

    # Helper function to process data into plotting format (Mean and Std Dev)
    def process_data(raw_data):
        x = sorted(raw_data.keys())
        y_mean = []
        y_std = []
        for val in x:
            replicates = raw_data[val]
            y_mean.append(np.mean(replicates))
            y_std.append(np.std(replicates, ddof=1)) # Using sample standard deviation
        return np.array(x), np.array(y_mean), np.array(y_std)

    x_20, y_20, err_20 = process_data(data_20c)
    x_35, y_35, err_35 = process_data(data_35c)
    x_50, y_50, err_50 = process_data(data_50c)

    # 3. Visualization Setup
    # Setting style parameters to match the publication look
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Helvetica']
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.linewidth'] = 1.0
    
    fig, ax = plt.subplots(figsize=(6, 5))

    # Define Colors (Approximate matches to the image)
    # 20C: Dark Slate Blue
    c_20 = '#4F627C' 
    c_20_face = '#788CA8' # Slightly lighter for marker face
    
    # 35C: Light Steel Blue
    c_35 = '#8FA3C2'
    c_35_face = '#BCCBE3'
    
    # 50C: Muted Terracotta/Brown
    c_50 = '#BC8071'
    c_50_face = '#D9AFA6'

    # 4. Plotting
    # Note: The image has markers with a lighter face color and darker edge color.
    
    # Plot 20°C
    ax.errorbar(x_20, y_20, yerr=err_20, label='20 °C',
                color=c_20, marker='o', markersize=10, 
                markerfacecolor=c_20_face, markeredgewidth=1.5,
                linewidth=1.5, capsize=3)

    # Plot 35°C
    ax.errorbar(x_35, y_35, yerr=err_35, label='35 °C',
                color=c_35, marker='^', markersize=10,
                markerfacecolor=c_35_face, markeredgewidth=1.5,
                linewidth=1.5, capsize=3)

    # Plot 50°C
    ax.errorbar(x_50, y_50, yerr=err_50, label='50 °C',
                color=c_50, marker='D', markersize=9,
                markerfacecolor=c_50_face, markeredgewidth=1.5,
                linewidth=1.5, capsize=3)

    # 5. Formatting Axes
    
    # X Axis
    ax.set_xlabel('Current density (mA cm$^{-2}$)', fontsize=14)
    ax.set_xlim(0, 850)
    ax.set_xticks(np.arange(0, 801, 100))
    
    # Y Axis
    ax.set_ylabel('Cell voltage (V)', fontsize=14)
    
    # CRITICAL: The Y-axis in the image is inverted. 
    # Values are negative. -1.8 is at the bottom, -2.6 is at the top.
    # This means the axis goes from -1.7 (approx) down to -2.7 (approx) visually, 
    # or simply inverted standard axis.
    # Let's set limits to match the visual ticks: -1.7 to -2.7
    ax.set_ylim(-1.7, -2.7) 
    
    # Set Y-ticks to match image (-1.8 to -2.6)
    ax.set_yticks([-1.8, -2.0, -2.2, -2.4, -2.6])
    
    # Tick styling
    ax.tick_params(direction='out', length=6, width=1, colors='black', labelsize=12)

    # 6. Legend
    # Located in top-left, no frame
    legend = ax.legend(loc='upper left', frameon=False, fontsize=12, handletextpad=0.5)
    
    # 7. Add Figure Label "c"
    # Positioned outside the axes in the top left
    fig.text(0.02, 0.92, 'c', fontsize=20, fontweight='bold')

    # Adjust layout to prevent clipping
    plt.tight_layout()
    
    # 8. Save Output
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    main()