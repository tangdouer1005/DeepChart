import matplotlib.pyplot as plt
import pandas as pd
import io
import sys
from scipy import stats

def generate_chart(output_filename):
    # 1. Source Data
    # Embedding the data exactly as provided in the prompt's table structure
    # We extract the relevant columns: "Left" (Vehicle + K) and "Unnamed: 1" (Dipy + K)
    csv_data = """vehicle_K,dipy_K
20.2038371448114,17.2002793898328
28.2841222234369,14.5098132817267
17.6957721587514,7.73067754218708
24.5982083872017,16.8116512414254
4.51862967654018,2.32638463554246
22.5550309385981,17.2686735656735
9.47358789887242,1.96725015719119
12.6892037800691,6.56186138881869"""

    # Load data into DataFrame
    df = pd.read_csv(io.StringIO(csv_data))

    # 2. Plot Setup
    # Create figure with a tall, narrow aspect ratio to match the image
    fig, ax = plt.subplots(figsize=(2.5, 5))

    # Set global font properties to match academic style (sans-serif)
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Helvetica']

    # 3. Plotting Data
    # Define x-coordinates for the two groups
    x_vehicle = 0
    x_dipy = 1
    
    # Define colors
    color_vehicle = 'black'
    color_dipy = '#8B1C1C'  # Dark red/brown color matching the image

    # Iterate through rows to plot points and connecting lines
    for i, row in df.iterrows():
        y_v = row['vehicle_K']
        y_d = row['dipy_K']
        
        # Plot connecting dashed line
        ax.plot([x_vehicle, x_dipy], [y_v, y_d], 
                color='black', linestyle='--', linewidth=1, zorder=1)
        
        # Plot points
        ax.scatter(x_vehicle, y_v, color=color_vehicle, s=40, zorder=2, clip_on=False)
        ax.scatter(x_dipy, y_d, color=color_dipy, s=40, zorder=2, clip_on=False)

    # 4. Formatting Axes
    # Y-axis
    ax.set_ylim(0, 30)
    ax.set_yticks([0, 10, 20, 30])
    ax.set_ylabel('Ado peak ($\Delta F/F$ %)', fontsize=14, labelpad=5)
    ax.tick_params(axis='y', labelsize=12, direction='out', length=4)

    # X-axis
    ax.set_xlim(-0.5, 1.5)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Vehicle + ketamine', 'Dipyridamole + ketamine'], 
                       rotation=50, ha='right', fontsize=13)
    # Hide x-axis tick marks but keep labels
    ax.tick_params(axis='x', length=0)

    # Spines (Remove top and right)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(0.8)
    ax.spines['bottom'].set_linewidth(0.8)

    # 5. Statistical Annotation
    # Calculate Paired T-test
    v = df['vehicle_K']
    d = df['dipy_K']
    t_stat, p_val = stats.ttest_rel(v, d)
    
    if p_val < 0.001:
        sig_text = '***'
    elif p_val < 0.01:
        sig_text = '**'
    elif p_val < 0.05:
        sig_text = '*'
    else:
        sig_text = f'P = {p_val:.2f}'

    # Draw the horizontal line and asterisks
    # Position based on the max value in the dataset (approx 28.28)
    stat_line_y = 29
    stat_line_x_start = 0.2
    stat_line_x_end = 0.8
    
    ax.plot([stat_line_x_start, stat_line_x_end], [stat_line_y, stat_line_y], 
            color='black', linewidth=0.8)
    
    # Add text centered above the line
    ax.text((stat_line_x_start + stat_line_x_end) / 2, stat_line_y, sig_text, 
            ha='center', va='bottom', fontsize=14, fontweight='bold')

    # 6. Figure Label
    # Add "c" in the top left corner
    # Using figure coordinates or axes coordinates with negative offset
    ax.text(-0.6, 1.0, 'c', transform=ax.transAxes, 
            fontsize=18, fontweight='bold', va='bottom', ha='right')

    # 7. Save Output
    plt.tight_layout()
    # Adjust margins manually to ensure rotated labels and figure tag fit
    plt.subplots_adjust(left=0.4, bottom=0.3, top=0.9)
    
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    # Handle command line argument for output filename
    output_file = sys.argv[1] if len(sys.argv) > 1 else 'output.png'
    generate_chart(output_file)