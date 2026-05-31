import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def generate_chart(output_filename):
    # 1. Source Data
    # Extracted specifically from the "Fig. 7d" columns in the provided markdown table.
    # Columns: Fraction inhomogeneity [-], Heat power [kW], H2 power (HHV) [kW]
    csv_data = """fraction,heat_power,h2_power
0,14.00411,2.52974
0.11111,13.97707,2.57286
0.22222,13.94922,2.61728
0.33333,13.91881,2.66577
0.44444,13.88884,2.71358
0.55556,13.85947,2.76041
0.66667,13.82843,2.80991
0.77778,13.79622,2.86128
0.88889,13.76039,2.91842
1,13.73574,2.95773
"""

    # Load data
    df = pd.read_csv(io.StringIO(csv_data))

    # Transform X-axis data: Fraction (0-1) to Percentage (0-100)
    df['percent'] = df['fraction'] * 100

    # 2. Plotting Setup
    # Define colors based on the image
    color_grey = '#757575'  # For H2 Power (squares)
    color_red = '#D6504D'   # For Heat Power (triangles)
    
    # Create figure and primary axis
    fig, ax1 = plt.subplots(figsize=(6, 5.5))
    
    # Adjust layout to make room for labels
    plt.subplots_adjust(left=0.15, right=0.85, bottom=0.2, top=0.9)

    # 3. Plotting Data
    
    # --- Left Axis (H2 Power / Power fuel) ---
    # Style: Grey squares, thin line
    ax1.plot(df['percent'], df['h2_power'], 
             color=color_grey, 
             marker='s', 
             linestyle='-', 
             linewidth=0.8, 
             markersize=11, 
             label='Power fuel')
    
    # --- Right Axis (Heat Power / Power heat) ---
    # Create twin axis
    ax2 = ax1.twinx()
    
    # Style: Red triangles, thin line
    ax2.plot(df['percent'], df['heat_power'], 
             color=color_red, 
             marker='^', 
             linestyle='-', 
             linewidth=0.8, 
             markersize=12, 
             label='Power heat')

    # 4. Styling and Formatting

    # --- Vertical Dashed Line at 0 ---
    ax1.axvline(x=0, color='black', linestyle='--', linewidth=0.8, zorder=0)

    # --- X-Axis Configuration ---
    ax1.set_xlabel("Linear interpolation of homogeneity (%)\n0% = actual experiment,\n100% = fully homogeneous light", 
                   fontsize=12, labelpad=10)
    ax1.set_xlim(-15, 115) # Add padding
    ax1.set_xticks([0, 50, 100])
    ax1.tick_params(axis='x', labelsize=12, length=6)

    # --- Left Y-Axis Configuration (Power fuel) ---
    ax1.set_ylabel("Power fuel (kW)", fontsize=12, color='#333333', labelpad=10)
    ax1.set_ylim(2.45, 3.0)
    ax1.set_yticks([2.5, 2.6, 2.7, 2.8, 2.9, 3.0])
    ax1.tick_params(axis='y', labelsize=11, colors='#333333', length=6)
    
    # --- Right Y-Axis Configuration (Power heat) ---
    ax2.set_ylabel("Power heat (kW)", fontsize=12, color=color_red, rotation=270, labelpad=20)
    ax2.set_ylim(13.65, 14.05) # Adjusted to match visual spacing
    ax2.set_yticks([13.7, 13.8, 13.9, 14.0])
    ax2.tick_params(axis='y', labelsize=11, colors='#333333', length=6) # Ticks are dark, label is red

    # --- Spines (Borders) ---
    # Remove top spine for a cleaner look
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    
    # Ensure axis colors match their data (optional, but good for dual axis)
    # The image keeps the axis lines black/grey, so we leave default spines.

    # --- Figure Label "d" ---
    # Place the bold 'd' in the top left corner outside the axes
    fig.text(0.02, 0.92, 'd', fontsize=24, fontweight='bold', color='black')

    # 5. Save Output
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    # Handle command line arguments for output filename
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    else:
        output_path = "output.png"
    
    generate_chart(output_path)