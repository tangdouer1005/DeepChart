import sys
import pandas as pd
import matplotlib.pyplot as plt
import io

def generate_chart(output_filename):
    # 1. Source Data
    # Extracted specifically for Fig 7a based on the provided markdown table.
    # Columns: Water flowrate [LPM], Heat power [kW], H2 power (HHV) [kW]
    csv_data = """flow_rate,heat_power,h2_power
4,12.54969,2.56383
4.22222,12.94205,2.55607
4.44444,13.30578,2.54881
4.66667,13.64379,2.54199
4.88889,13.95868,2.53551
5.11111,14.25273,2.52925
5.33333,14.52797,2.52308
5.55556,14.78616,2.51698
5.77778,15.02868,2.51115
6,15.25653,2.5061
"""
    
    # Load data
    df = pd.read_csv(io.StringIO(csv_data))

    # 2. Plotting Setup
    # Using a figure size that approximates the aspect ratio of the provided image
    fig, ax1 = plt.subplots(figsize=(5, 4))

    # Define Colors
    color_fuel = '#757575'  # Grey for Fuel/H2
    color_heat = '#D35E5E'  # Muted Red for Heat

    # 3. Plotting Data
    
    # --- Left Axis (Power Fuel / H2 Power) ---
    # Style: Grey squares, thin solid line
    ax1.plot(df['flow_rate'], df['h2_power'], 
             color=color_fuel, 
             marker='s', 
             linestyle='-', 
             linewidth=0.8, 
             markersize=9, 
             label='Power fuel')
    
    # --- Right Axis (Power Heat) ---
    ax2 = ax1.twinx()
    # Style: Red triangles, thin dashed line
    ax2.plot(df['flow_rate'], df['heat_power'], 
             color=color_heat, 
             marker='^', 
             linestyle='--', 
             linewidth=0.8, 
             markersize=9, 
             label='Power heat')

    # 4. Vertical Dashed Line
    # The line in the image passes through the 5th data point (index 4).
    # x value at index 4 is 4.88889
    vertical_line_x = df['flow_rate'].iloc[4]
    ax1.axvline(x=vertical_line_x, color='gray', linestyle='--', linewidth=0.8, ymax=1)

    # 5. Styling and Formatting

    # --- Axis Limits and Ticks ---
    # X Axis
    ax1.set_xlim(3.7, 6.3)
    ax1.set_xticks([4, 5, 6])
    
    # Left Y Axis (Fuel)
    # Image range approx 2.50 to 2.57
    ax1.set_ylim(2.50, 2.57)
    ax1.set_yticks([2.50, 2.52, 2.54, 2.56])
    
    # Right Y Axis (Heat)
    # Image range approx 12 to 15.5
    ax2.set_ylim(12, 15.5)
    ax2.set_yticks([12, 13, 14, 15])

    # --- Labels ---
    # Font properties
    label_font = {'size': 12, 'family': 'sans-serif'}
    
    ax1.set_xlabel(r'Water flow rate (l min$^{-1}$)', **label_font, labelpad=10)
    ax1.set_ylabel('Power fuel (kW)', **label_font, color='black', labelpad=10)
    
    # The right axis label is colored red in the image
    ax2.set_ylabel('Power heat (kW)', **label_font, color=color_heat, labelpad=10)

    # --- Spines and Ticks Styling ---
    # Remove top spine
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    
    # Configure tick parameters
    ax1.tick_params(axis='y', colors='#333333', labelsize=10, direction='out', length=6)
    ax1.tick_params(axis='x', colors='#333333', labelsize=10, direction='out', length=6)
    ax2.tick_params(axis='y', colors='#333333', labelsize=10, direction='out', length=6)

    # --- Figure Tag ---
    # Add the bold 'a' in the top left corner
    ax1.text(-0.15, 1.0, 'a', transform=ax1.transAxes, 
             fontsize=16, fontweight='bold', va='top', ha='right')

    # Adjust layout to prevent clipping
    plt.tight_layout()

    # 6. Save Output
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    # Handle command line argument for output filename
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        output_file = "output.png"
    
    generate_chart(output_file)