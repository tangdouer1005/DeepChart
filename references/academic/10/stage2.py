import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import numpy as np
from scipy import stats

def generate_chart(output_filename='output.png'):
    # 1. Load Source Data
    csv_data = """K5|DCK5|K10|DCK10
11.2415|22.4507|17.7663|40.1504
8.60784|14.6416|11.6146|35.3579
5.80698|21.3465|20.4368|31.5678
4.37638|22.6102|11.9981|31.5956
8.25921|12.2284|21.3436|39.3495
6.33075|19.2196|23.2706|32.4771
7.57759|26.028|18.3738|34.131
6.90356|23.0144|19.8777|nan
11.2284|nan|21.0958|nan
11.5802|nan|21.2376|nan
7.55002|nan|14.488|nan
12.2143|nan|15.5358|nan
5.02523|nan|11.0808|nan"""

    # Read data, handling the pipe separator and nan values
    df = pd.read_csv(io.StringIO(csv_data), sep='|')

    # Prepare data lists, removing NaNs for plotting
    data_k5 = df['K5'].dropna().values
    data_dck5 = df['DCK5'].dropna().values
    data_k10 = df['K10'].dropna().values
    data_dck10 = df['DCK10'].dropna().values

    data_to_plot = [data_k5, data_dck5, data_k10, data_dck10]

    # 2. Setup Plot
    fig, ax = plt.subplots(figsize=(5, 6))
    
    # Define positions: Group 1 at 1,2; Group 2 at 4,5 (gap at 3)
    positions = [1, 2, 4, 5]
    
    # Define Colors (approximated from image)
    # K5 (Pink), DCK5 (Teal), K10 (Dark Red), DCK10 (Dark Teal)
    colors = ['#F09494', '#408598', '#A62B2B', '#20637D']
    
    # 3. Create Boxplot
    # We use patch_artist=True to allow coloring, but we will set facecolor to 'none' later
    # to match the hollow style of the reference image.
    bp = ax.boxplot(data_to_plot, positions=positions, patch_artist=True, 
                    widths=0.6, showfliers=False)

    # 4. Style the Boxplot
    # Iterate through the components to color lines and edges
    for i in range(4):
        col = colors[i]
        
        # Box (Edge color only, white face)
        box = bp['boxes'][i]
        box.set(color=col, linewidth=2)
        box.set(facecolor='none') 
        
        # Medians
        median = bp['medians'][i]
        median.set(color=col, linewidth=2)
        
        # Whiskers (2 per box)
        bp['whiskers'][i*2].set(color=col, linewidth=2)
        bp['whiskers'][i*2+1].set(color=col, linewidth=2)
        
        # Caps (2 per box)
        bp['caps'][i*2].set(color=col, linewidth=2)
        bp['caps'][i*2+1].set(color=col, linewidth=2)

    # 5. Add Statistical Significance
    # Function to draw bracket and stars
    def add_significance(x1, x2, y_line, text):
        # Draw the line
        ax.plot([x1, x2], [y_line, y_line], color='black', linewidth=0.8)
        # Add text centered above line
        ax.text((x1 + x2) * 0.5, y_line, text, ha='center', va='bottom', 
                fontsize=14, color='black')

    # Significance for 5mg group (K5 vs DCK5)
    # Max of DCK5 is ~26. Place line around 32.
    t_stat_5, p_val_5 = stats.ttest_ind(data_k5, data_dck5)
    if p_val_5 < 0.001:
        sig_text_5 = '***'
    elif p_val_5 < 0.01:
        sig_text_5 = '**'
    elif p_val_5 < 0.05:
        sig_text_5 = '*'
    else:
        sig_text_5 = 'ns'
    add_significance(1, 2, 32.5, sig_text_5)

    # Significance for 10mg group (K10 vs DCK10)
    # Max of DCK10 is ~40. Place line around 44.
    t_stat_10, p_val_10 = stats.ttest_ind(data_k10, data_dck10)
    if p_val_10 < 0.001:
        sig_text_10 = '***'
    elif p_val_10 < 0.01:
        sig_text_10 = '**'
    elif p_val_10 < 0.05:
        sig_text_10 = '*'
    else:
        sig_text_10 = 'ns'
    add_significance(4, 5, 44, sig_text_10)

    # 6. Layout and Annotations
    
    # Vertical dashed separator line
    ax.axvline(x=3, color='black', linestyle='--', linewidth=1.2, ymax=0.95)

    # Y-Axis Label
    ax.set_ylabel(r'Ado peak ($\Delta F/F$ %)', fontsize=14, color='black')
    ax.set_ylim(0, 48) # Adjust to fit significance bars
    ax.tick_params(axis='y', labelsize=12)

    # X-Axis Labels (Drug Names)
    ax.set_xticks(positions)
    ax.set_xticklabels(['Ketamine', 'DCK', 'Ketamine', 'DCK'], 
                       rotation=45, ha='right', fontsize=14)

    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(0.8)
    ax.spines['bottom'].set_linewidth(0.8)

    # 7. Add Dosage Grouping Labels (Lines and Text below X-axis)
    # We use transforms to place these relative to the axes or data
    
    # Line for 5 mg kg-1
    line_y = -8  # Negative value relative to data coordinates for placement below axis
    text_y = -13
    
    # Since we rotated labels, we need to be careful with spacing. 
    # Using text coordinates relative to data is easiest here given the fixed layout.
    
    # Draw lines under groups
    # Group 1: x=0.6 to 2.4
    ax.plot([0.6, 2.4], [line_y, line_y], color='black', linewidth=1, clip_on=False)
    ax.text(1.5, text_y, r'5 mg kg$^{-1}$', ha='center', va='top', fontsize=14, color='black')

    # Group 2: x=3.6 to 5.4
    ax.plot([3.6, 5.4], [line_y, line_y], color='black', linewidth=1, clip_on=False)
    ax.text(4.5, text_y, r'10 mg kg$^{-1}$', ha='center', va='top', fontsize=14, color='black')

    # Figure Label "c"
    # Place in top left corner, outside axes
    ax.text(-0.2, 1.05, 'c', transform=ax.transAxes, 
            fontsize=20, fontweight='bold', va='bottom', ha='right')

    # Adjust layout to prevent clipping of bottom labels
    plt.tight_layout()
    
    # Extra margin at bottom for the manual labels
    plt.subplots_adjust(bottom=0.25)

    # Save
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)