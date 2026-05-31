import sys
import io
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.lines as lines
import numpy as np

def generate_chart(output_filename):
    # 1. Load Source Data
    # Using the exact data provided in the prompt
    csv_data = """Unnamed: 0,control,Unnamed: 2,Unnamed: 3,K2,Unnamed: 5,Unnamed: 6,K10,Unnamed: 8,Unnamed: 9,K50,Unnamed: 11,Unnamed: 12
Pyruvate,0.223058,0.210762,0.149665,0.379206,0.293885,0.464718,0.442063,0.254092,0.40376,0.614279,0.562326,0.429538
Citrate,0.258809,0.309936,0.356968,0.30788,0.325941,0.289485,0.296881,0.274078,0.282906,0.279333,0.314928,0.289988
Glutamate,0.367758,0.344181,0.376461,0.347516,0.379106,0.342397,0.314315,0.281335,0.302929,0.284958,0.332328,0.30411
Succinate,0.382252,0.328351,0.398149,0.360708,0.386626,0.357401,0.335758,0.298984,0.327873,0.297441,0.350486,0.323474
Fumarate,0.097648,0.104257,0.106706,0.0843699,0.0890736,0.0680718,0.0878835,0.0631375,0.0819516,0.0646776,0.0777998,0.0697304
Malate,0.0979276,0.11186,0.113111,0.0915563,0.0970604,0.069992,0.0949667,0.0724992,0.0904031,0.0690075,0.0817405,0.0725173
Aspartic acid,0.140544,0.158885,0.161802,0.132497,0.130524,0.105984,0.137745,0.0969118,0.124096,0.10052,0.12154,0.103243
"""
    
    # Read data
    df = pd.read_csv(io.StringIO(csv_data))
    
    # 2. Data Preprocessing
    # Set index to metabolite names
    df = df.set_index('Unnamed: 0')
    
    # Rename index to match the chart (lowercase, specific mapping)
    index_mapping = {
        'Pyruvate': 'pyruvate',
        'Citrate': 'citrate',
        'Glutamate': 'glutamate',
        'Succinate': 'succinate',
        'Fumarate': 'fumarate',
        'Malate': 'malate',
        'Aspartic acid': 'aspartate'
    }
    df = df.rename(index=index_mapping)
    
    # Calculate Z-score row-wise (normalized to vehicle control group)
    # Normalized to control means: (x - mean(control)) / std(all)
    # This centers the control group at 0.
    def zscore_to_control(row):
        # Control samples are the first 3 columns
        control_mean = row.iloc[0:3].mean()
        # Use global standard deviation for scaling to avoid exploding values if control variance is low
        # and to maintain the standard Z-score scale interpretation relative to dataset variance.
        global_std = row.std() 
        return (row - control_mean) / global_std

    df_zscore = df.apply(zscore_to_control, axis=1)

    # 3. Plotting Setup
    sns.set_theme(style="white")
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # Define custom colormap to match the image (Blue -> White -> Red)
    # 'vlag' is Seaborn's default diverging palette which matches closely
    cmap = sns.diverging_palette(255, 15, s=90, l=60, n=256, center="light", as_cmap=True)
    # Alternatively, use 'vlag' directly if preferred, but custom tuning matches the specific red/blue hues better.
    # Let's stick to a standard 'vlag' style or 'coolwarm'. The image uses a fairly standard "coolwarm" or "vlag".
    # 'vlag' is usually Blue-White-Red.
    
    # Draw Heatmap
    # vmin/vmax set to -3.5/3.5 to match the colorbar range in the image roughly
    g = sns.heatmap(df_zscore, 
                    cmap="vlag", 
                    center=0, 
                    vmin=-3.5, 
                    vmax=3.5,
                    ax=ax,
                    cbar_kws={"shrink": 0.8, "ticks": [-3, -2, -1, 0, 1, 2, 3]},
                    xticklabels=False, # Hide individual sample names
                    yticklabels=True)

    # 4. Styling
    
    # Y-axis labels styling
    ax.set_ylabel('') # Remove default y-label
    ax.tick_params(axis='y', length=0, labelsize=12)
    plt.yticks(rotation=0) # Horizontal labels

    # Colorbar styling
    cbar = ax.collections[0].colorbar
    cbar.set_label('Z-score (normalized to control)', rotation=270, labelpad=20, fontsize=12)
    cbar.outline.set_visible(False) # Remove colorbar border
    
    # Add vertical separators between groups
    # Groups are 3 columns each. Total 12 columns. Lines at 3, 6, 9.
    for x in [3, 6, 9]:
        ax.axvline(x, color='black', linewidth=2)

    # 5. Add Group Brackets and Labels
    # We need to draw lines and text below the heatmap
    
    groups = [
        ("control", 0, 3),
        ("2 µM ket", 3, 6),
        ("10 µM ket", 6, 9),
        ("50 µM ket", 9, 12)
    ]
    
    # Get y-limits to position brackets below
    y_min, y_max = ax.get_ylim()
    # In heatmap, y starts at 0 (top) and goes to N (bottom). 
    # We want to draw below the bottom (which is y_max).
    
    bracket_y = y_max + 0.2  # Slightly below the heatmap
    text_y = y_max + 0.6     # Below the bracket
    
    for label, start, end in groups:
        # Draw the bracket line
        # A horizontal line with small vertical ticks at ends
        center = (start + end) / 2
        
        # Bracket width (add padding)
        pad = 0.2
        line_start = start + pad
        line_end = end - pad
        
        # Draw horizontal line
        ax.plot([line_start, line_end], [bracket_y, bracket_y], color='black', linewidth=1, clip_on=False)
        
        # Draw vertical ticks for bracket
        tick_height = 0.1
        ax.plot([line_start, line_start], [bracket_y, bracket_y - tick_height], color='black', linewidth=1, clip_on=False)
        ax.plot([line_end, line_end], [bracket_y, bracket_y - tick_height], color='black', linewidth=1, clip_on=False)
        
        # Add Text
        ax.text(center, text_y, label, ha='center', va='top', fontsize=12, color='black')

    # Add "b" label in top left corner
    # Position relative to figure or axes. 
    # In the image, 'b' is to the left of the heatmap title area.
    fig.text(0.02, 0.95, 'b', fontsize=16, fontweight='bold')

    # Adjust layout to make room for bottom labels
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.15, left=0.15) # Add extra space at bottom for brackets

    # 6. Save Output
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    generate_chart(output_file)