import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

def main():
    # 1. Data Preparation
    # Transcribing the provided source data exactly
    current_density = [50, 100, 200, 300, 400, 500, 600, 700, 800]

    # AEM Data (Voltage replicates)
    aem_data = np.array([
        [-2.19, -2.21, -2.18], # 50
        [-2.29, -2.32, -2.30], # 100
        [-2.42, -2.45, -2.43], # 200
        [-2.51, -2.55, -2.53], # 300
        [-2.60, -2.64, -2.62], # 400
        [-2.69, -2.73, -2.70], # 500
        [-2.76, -2.80, -2.77], # 600
        [-2.83, -2.86, -2.83], # 700
        [-2.89, -2.92, -2.89]  # 800
    ])

    # Separator Data (Voltage replicates)
    separator_data = np.array([
        [-2.11, -2.10, -2.13], # 50
        [-2.21, -2.19, -2.20], # 100
        [-2.29, -2.27, -2.30], # 200
        [-2.37, -2.34, -2.38], # 300
        [-2.44, -2.42, -2.46], # 400
        [-2.50, -2.48, -2.53], # 500
        [-2.56, -2.54, -2.60], # 600
        [-2.61, -2.57, -2.63], # 700
        [-2.65, -2.60, -2.66]  # 800
    ])

    # Calculate Mean and Standard Deviation
    aem_mean = np.mean(aem_data, axis=1)
    aem_std = np.std(aem_data, axis=1)

    sep_mean = np.mean(separator_data, axis=1)
    sep_std = np.std(separator_data, axis=1)

    # 2. Plotting Setup
    # Set font style to match the scientific publication style (sans-serif)
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
    plt.rcParams['font.size'] = 12
    
    fig, ax = plt.subplots(figsize=(6, 5))

    # Colors extracted from the image
    # AEM: Dark Blue-Grey line, Light Blue-Grey fill
    color_aem_line = '#5F768F'
    color_aem_face = '#CFD8E3'
    
    # Separator: Muted Red-Brown line, Light Red-Brown fill
    color_sep_line = '#C08376'
    color_sep_face = '#EEDCD8'

    # 3. Plotting Data
    # Plot AEM
    ax.errorbar(
        current_density, aem_mean, yerr=aem_std,
        fmt='-o',                 # Line with markers
        color=color_aem_line,     # Line and edge color
        markerfacecolor=color_aem_face, # Marker fill color
        markersize=10,            # Large markers
        markeredgewidth=1.0,      # Edge thickness
        linewidth=1.0,            # Line thickness
        capsize=3,                # Error bar cap width
        label='AEM',
        zorder=2                  # Ensure order
    )

    # Plot Separator
    ax.errorbar(
        current_density, sep_mean, yerr=sep_std,
        fmt='-o',
        color=color_sep_line,
        markerfacecolor=color_sep_face,
        markersize=10,
        markeredgewidth=1.0,
        linewidth=1.0,
        capsize=3,
        label='Separator',
        zorder=1
    )

    # 4. Axis Configuration
    # X Axis
    ax.set_xlabel('Current density (mA cm$^{-2}$)', fontsize=14)
    ax.set_xlim(0, 850)
    ax.set_xticks(np.arange(0, 900, 100))

    # Y Axis
    # The chart has an inverted Y-axis logic visually:
    # Values are negative. -2.0 is at the bottom, -3.0 is at the top.
    # This means values are decreasing as we go up.
    ax.set_ylabel('Cell voltage (V)', fontsize=14)
    ax.set_ylim(-2.0, -3.0) # Set limits: bottom=-2.0, top=-3.0
    
    # Ticks styling
    ax.tick_params(direction='out', length=6, width=1, top=True, right=True)
    
    # 5. Legend
    # Create a legend with no frame, located at top left
    legend = ax.legend(loc='upper left', frameon=False, handletextpad=0.5)
    
    # 6. Add Figure Label "e"
    # Positioned outside the plot area, top left, bold
    fig.text(0.02, 0.92, 'e', fontsize=20, fontweight='bold')

    # Adjust layout to prevent clipping
    plt.tight_layout()
    plt.subplots_adjust(left=0.15, top=0.9)

    # 7. Save Output
    output_path = 'output.png'
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    
    plt.savefig(output_path, dpi=300)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    main()