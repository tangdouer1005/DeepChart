import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def main():
    # 1. Handle Output Filename
    output_filename = "output.png"
    if len(sys.argv) > 1:
        output_filename = sys.argv[1]

    # 2. Data Preparation
    # Raw data transcribed exactly from the provided source table
    
    # IrOx Data
    irox_raw = {
        'current_density': [50, 100, 200, 300, 400, 500, 600, 700, 800],
        'r1': [-2.11, -2.21, -2.29, -2.37, -2.44, -2.50, -2.56, -2.61, -2.65],
        'r2': [-2.10, -2.19, -2.27, -2.34, -2.42, -2.48, -2.54, -2.57, -2.60],
        'r3': [-2.13, -2.20, -2.30, -2.38, -2.46, -2.53, -2.60, -2.63, -2.66]
    }
    
    # NiFe-B Data
    nife_raw = {
        'current_density': [50, 100, 200, 300, 400, 500, 600, 700, 800],
        'r1': [-1.95, -2.02, -2.15, -2.23, -2.28, -2.33, -2.37, -2.42, -2.46],
        'r2': [-1.95, -2.00, -2.14, -2.21, -2.27, -2.31, -2.35, -2.39, -2.44],
        'r3': [-1.97, -2.04, -2.17, -2.25, -2.30, -2.35, -2.41, -2.46, -2.50]
    }

    # Create DataFrames
    df_irox = pd.DataFrame(irox_raw)
    df_nife = pd.DataFrame(nife_raw)

    # Calculate Mean and Std Dev (using ddof=1 for sample standard deviation)
    # Axis 1 calculates across the replicate columns
    df_irox['mean'] = df_irox[['r1', 'r2', 'r3']].mean(axis=1)
    df_irox['std'] = df_irox[['r1', 'r2', 'r3']].std(axis=1)

    df_nife['mean'] = df_nife[['r1', 'r2', 'r3']].mean(axis=1)
    df_nife['std'] = df_nife[['r1', 'r2', 'r3']].std(axis=1)

    # 3. Plotting Setup
    # Set figure size to match the aspect ratio of the provided image
    fig, ax = plt.subplots(figsize=(6.5, 5))

    # Define Colors (picked to match the image closely)
    # IrOx: Blue-grey
    irox_edge = '#5C7495'
    irox_face = '#BCC8D9'
    
    # NiFe-B: Red-brown
    nife_edge = '#B87466'
    nife_face = '#E8CFCB'

    # Common plotting parameters
    marker_size = 10
    line_width = 1.5
    cap_size = 3
    err_width = 1.5

    # 4. Plot Data
    
    # Plot IrOx
    ax.errorbar(
        df_irox['current_density'], 
        df_irox['mean'], 
        yerr=df_irox['std'],
        label='IrOx',
        fmt='-o', # Line and marker
        color=irox_edge, # Line color
        markerfacecolor=irox_face,
        markeredgecolor=irox_edge,
        markeredgewidth=1.5,
        markersize=marker_size,
        linewidth=line_width,
        capsize=cap_size,
        elinewidth=err_width
    )

    # Plot NiFe-B
    ax.errorbar(
        df_nife['current_density'], 
        df_nife['mean'], 
        yerr=df_nife['std'],
        label='NiFe-B',
        fmt='-o',
        color=nife_edge,
        markerfacecolor=nife_face,
        markeredgecolor=nife_edge,
        markeredgewidth=1.5,
        markersize=marker_size,
        linewidth=line_width,
        capsize=cap_size,
        elinewidth=err_width
    )

    # 5. Formatting

    # Axis Limits
    # X-axis: 0 to 850 based on visual spacing
    ax.set_xlim(0, 850)
    
    # Y-axis: The chart shows -1.8 at the bottom and -2.8 at the top.
    # This is an inverted axis mathematically (-2.8 < -1.8), but visually ascending magnitude.
    # Setting ylim(bottom, top) works.
    ax.set_ylim(-1.8, -2.8)

    # Ticks
    ax.set_xticks(np.arange(0, 801, 100))
    ax.set_yticks([-1.8, -2.0, -2.2, -2.4, -2.6, -2.8])

    # Labels
    # Using LaTeX formatting for superscripts
    ax.set_xlabel('Current density (mA cm$^{-2}$)', fontsize=14, labelpad=8)
    ax.set_ylabel('Cell voltage (V)', fontsize=14, labelpad=8)

    # Tick Parameters
    ax.tick_params(axis='both', which='major', labelsize=12, direction='out', length=6)

    # Legend
    # Frameon=False removes the box around the legend
    legend = ax.legend(loc='upper left', frameon=False, fontsize=12, handletextpad=0.5)
    
    # Add the "a" tag
    # Positioned relative to the figure or axes. 
    # In the image, it's to the left of the Y-axis top.
    ax.text(-0.18, 1.0, 'a', transform=ax.transAxes, fontsize=20, fontweight='bold', va='top', ha='left')

    # Layout adjustment
    plt.tight_layout()
    
    # Adjust margins slightly to accommodate the 'a' tag if needed, 
    # though tight_layout usually handles the plot area well.
    plt.subplots_adjust(left=0.15)

    # 6. Save Output
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    main()