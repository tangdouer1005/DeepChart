import matplotlib.pyplot as plt
import numpy as np
import sys

def generate_chart(output_filename):
    """
    Generates a boxplot with overlaid scatter points to replicate the provided chart image.
    """
    
    # ---------------------------------------------------------
    # 1. Source Data
    # ---------------------------------------------------------
    # Data extracted directly from the provided table
    vehicle_data = np.array([
        0.6362426544252882, 
        1.3637573455747118, 
        1.3186889049497537, 
        0.7234410435525506, 
        0.6335460026377365, 
        1.2396240761070576, 
        0.7431799017428403, 
        1.4644298527637458, 
        0.8770902182463151
    ])
    
    fsen1_data = np.array([
        0.642841400598503, 
        0.35865193141724816, 
        0.2055757563149134, 
        0.7189498587703381, 
        0.6489407265757056, 
        0.6164231377015815, 
        0.6317029164814143, 
        0.48835837703325524
    ])

    # ---------------------------------------------------------
    # 2. Plot Setup
    # ---------------------------------------------------------
    # The chart has a tall, narrow aspect ratio.
    fig, ax = plt.subplots(figsize=(2.8, 5.5))
    
    # Define colors based on visual inspection of the chart
    # Vehicle: Light grey box, dark grey edge, grey points
    color_vehicle_fill = '#D9D9D9'
    color_vehicle_edge = '#595959'
    color_vehicle_pts = '#999999'
    
    # FSEN1: Salmon/Light Red box, Dark Red edge, Red points
    color_fsen1_fill = '#F28E82'
    color_fsen1_edge = '#B03A2E'
    color_fsen1_pts = '#E74C3C'
    
    # ---------------------------------------------------------
    # 3. Reference Line
    # ---------------------------------------------------------
    # Dashed line at y=1.0
    ax.axhline(y=1.0, color='black', linestyle='--', linewidth=1.2, zorder=1, dashes=(5, 3))

    # ---------------------------------------------------------
    # 4. Boxplots
    # ---------------------------------------------------------
    # Create boxplots with custom styling
    bp = ax.boxplot([vehicle_data, fsen1_data], positions=[1, 2], widths=0.5,
                    patch_artist=True, showfliers=False,
                    medianprops=dict(color='black', linewidth=1.2),
                    boxprops=dict(linewidth=1.2),
                    whiskerprops=dict(color='black', linewidth=1.2),
                    capprops=dict(color='black', linewidth=1.2))

    # Apply specific colors to the boxes
    # Vehicle Box
    bp['boxes'][0].set_facecolor(color_vehicle_fill)
    bp['boxes'][0].set_edgecolor(color_vehicle_edge)
    # FSEN1 Box
    bp['boxes'][1].set_facecolor(color_fsen1_fill)
    bp['boxes'][1].set_edgecolor(color_fsen1_edge)

    # ---------------------------------------------------------
    # 5. Scatter Points (Jittered)
    # ---------------------------------------------------------
    np.random.seed(42) # Fixed seed for reproducible jitter
    
    def jitter(x, width, n):
        return np.random.uniform(x - width, x + width, n)

    # Jitter width to keep points within the box area
    jitter_width = 0.12
    
    # Vehicle Points
    ax.scatter(jitter(1, jitter_width, len(vehicle_data)), vehicle_data,
               color=color_vehicle_pts, edgecolor='black', linewidth=1, s=80, zorder=3)
    
    # FSEN1 Points
    ax.scatter(jitter(2, jitter_width, len(fsen1_data)), fsen1_data,
               color=color_fsen1_pts, edgecolor='black', linewidth=1, s=80, zorder=3)

    # ---------------------------------------------------------
    # 6. Statistical Significance
    # ---------------------------------------------------------
    # Line connecting the two groups with P-value text
    # The line is positioned above the highest data point/tick
    line_y = 1.6
    text_y = line_y + 0.02
    
    ax.plot([1, 2], [line_y, line_y], color='black', linewidth=1)
    # Note: P is italicized in the chart
    ax.text(1.5, text_y, '$P$ = 0.0038', ha='center', va='bottom', fontsize=12, color='black')

    # ---------------------------------------------------------
    # 7. Axis Configuration
    # ---------------------------------------------------------
    # Custom Y-ticks as seen in the image
    yticks = [0, 0.3, 0.5, 0.8, 1.0, 1.3, 1.5]
    ytick_labels = ['0', '0.3', '0.5', '0.8', '1.0', '1.3', '1.5']
    
    ax.set_yticks(yticks)
    ax.set_yticklabels(ytick_labels, fontsize=12)
    ax.set_ylim(0, 1.8) # Extend upper limit to accommodate the significance bar
    
    # Y-axis Label
    ax.set_ylabel('End-point tumour volume\n(compared with vehicle)', fontsize=13, labelpad=10)
    
    # X-axis Configuration
    ax.set_xticks([1, 2])
    ax.set_xticklabels(['Vehicle', 'FSEN1'], rotation=45, ha='right', fontsize=13)
    ax.set_xlim(0.4, 2.6)

    # Remove top and right spines for cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1)
    
    # Tick parameters
    ax.tick_params(axis='both', which='major', width=1, length=5)

    # ---------------------------------------------------------
    # 8. Figure Label
    # ---------------------------------------------------------
    # Add the bold 'h' label in the top left corner
    ax.text(-0.45, 1.0, 'h', transform=ax.transAxes, fontsize=24, fontweight='bold', va='top', ha='left')

    # ---------------------------------------------------------
    # 9. Save Output
    # ---------------------------------------------------------
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')

if __name__ == "__main__":
    # Handle command line argument for output filename
    output_file = sys.argv[1] if len(sys.argv) > 1 else 'output.png'
    generate_chart(output_file)