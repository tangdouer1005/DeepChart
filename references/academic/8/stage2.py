import sys
import pandas as pd
import matplotlib.pyplot as plt
import io
from scipy import stats

def generate_chart(output_filename):
    # 1. Load Data
    # Using the "Right" columns from the provided source data table.
    # The "Left" columns correspond to values ~20, which do not match the Y-axis (-0.5 to 2.0).
    csv_data = """vehicle_K,dipy_K
1.236048,0.989125
1.619549,0.56055
1.148544,0.32109
1.240917,0.850561
0.132969,-0.17079
1.456884,1.161851
0.517272,-0.22695
0.647817,0.167474"""

    df = pd.read_csv(io.StringIO(csv_data))

    # 2. Setup Plot
    # The image is tall and narrow.
    fig, ax = plt.subplots(figsize=(3, 5))

    # 3. Plotting
    # Define x-coordinates for the two conditions
    x_vehicle = 0
    x_dipy = 1
    
    # Colors
    color_vehicle = 'black'
    color_dipy = '#8B1C1C'  # Dark red/brown similar to the image
    
    # Plot lines and points
    for i in range(len(df)):
        y1 = df.iloc[i]['vehicle_K']
        y2 = df.iloc[i]['dipy_K']
        
        # Dashed connecting line
        ax.plot([x_vehicle, x_dipy], [y1, y2], 
                color='black', 
                linestyle='--', 
                linewidth=1.0, 
                zorder=1)
        
        # Points
        ax.scatter(x_vehicle, y1, color=color_vehicle, s=40, zorder=2, edgecolors='none')
        ax.scatter(x_dipy, y2, color=color_dipy, s=40, zorder=2, edgecolors='none')

    # 4. Styling and Layout
    
    # Axis Limits and Ticks
    ax.set_ylim(-0.5, 2.0)
    ax.set_yticks([-0.5, 0.0, 0.5, 1.0, 1.5, 2.0])
    
    # X-Axis Labels
    ax.set_xlim(-0.5, 1.5)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Vehicle + ketamine", "Dipyridamole + ketamine"], 
                       rotation=45, 
                       ha='right', 
                       fontsize=14,
                       color='black')
    
    # Y-Axis Label
    ax.set_ylabel("AUC normalized", fontsize=14, color='black')
    
    # Tick params
    ax.tick_params(axis='y', labelsize=12, color='black')
    ax.tick_params(axis='x', bottom=False) # Hide x-axis tick marks to match style
    
    # Spines (Borders)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(0.8)
    ax.spines['bottom'].set_linewidth(0.8)
    ax.spines['left'].set_color('black')
    ax.spines['bottom'].set_color('black')

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

    # Draw the line and asterisks for significance
    # Position based on visual estimation from the chart (above the highest point ~1.6)
    line_y = 1.85
    line_x_start = 0.2
    line_x_end = 0.8
    
    ax.plot([line_x_start, line_x_end], [line_y, line_y], color='black', linewidth=0.8)
    ax.text((line_x_start + line_x_end) / 2, line_y, sig_text, 
            ha='center', va='bottom', fontsize=16, color='black')

    # Adjust layout to accommodate rotated labels
    plt.tight_layout()

    # 6. Save Output
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)