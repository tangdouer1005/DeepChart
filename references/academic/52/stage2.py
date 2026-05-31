import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

def generate_chart(output_filename='output.png'):
    # 1. Source Data Preparation
    # Data is manually extracted from the provided markdown table and reordered 
    # to match the visual order of the chart (DMSO -> Rapamycin -> LY294002 -> MK2206).
    
    # Raw data dictionary
    raw_data = {
        'DMSO': [16.4, 18.8, 18.2, 17.6],
        
        # Rapamycin (Columns 2, 3, 4 in source)
        'Rapamycin_40nM':  [32.0, 28.7, 30.1, 28.7],
        'Rapamycin_100nM': [31.6, 31.1, 31.5, 27.2],
        'Rapamycin_200nM': [30.5, 30.4, 32.1, 29.5],
        
        # LY294002 (Columns 8, 9, 10 in source - Note: Chart places LY before MK)
        # Source headers: LY294002 1uM, 5uM, 10uM
        'LY294002_1uM':  [19.0, 19.7, 20.3, 19.1],
        'LY294002_5uM':  [32.4, 31.1, 28.5, 27.8],
        'LY294002_10uM': [44.3, 40.8, 43.6, 39.8],
        
        # MK2206 (Columns 5, 6, 7 in source)
        # Source headers: MK2206 0.2uM, 1uM, 5uM
        'MK2206_0.2uM': [29.9, 30.3, 30.8, 29.0],
        'MK2206_1uM':   [27.8, 30.5, 35.3, 30.4],
        'MK2206_5uM':   [1.59, 1.34, 1.49, 1.77]
    }

    # Convert to DataFrame for easier handling
    df = pd.DataFrame(raw_data)
    
    # Calculate Means and Standard Deviations
    means = df.mean()
    stds = df.std()
    
    # 2. Plot Configuration
    fig, ax = plt.subplots(figsize=(7, 6))
    
    # X-axis positions
    x_pos = np.arange(len(df.columns))
    
    # Define Colors (matching the chart image)
    # DMSO: Grey
    # Rapamycin: Pinkish/Mauve
    # LY294002: Light Blue -> Dark Blue
    # MK2206: Light Purple -> Dark Purple
    
    bar_colors = [
        '#808080', # DMSO
        '#D8A6B8', '#D8A6B8', '#D8A6B8', # Rapamycin (Uniform pinkish)
        '#CDE4F3', '#90CAF9', '#5C6BC0', # LY294002 (Gradient Blue)
        '#D1C4E9', '#9575CD', '#4527A0'  # MK2206 (Gradient Purple)
    ]
    
    # Edge colors (darker versions for borders and points)
    edge_colors = [
        '#404040', # DMSO
        '#C06080', '#C06080', '#C06080', # Rapamycin
        '#82B1FF', '#42A5F5', '#303F9F', # LY
        '#B39DDB', '#7E57C2', '#311B92'  # MK
    ]

    # 3. Drawing Bars and Scatter Points
    for i, col in enumerate(df.columns):
        # Draw Bar with Error Bars
        ax.bar(i, means[col], yerr=stds[col], capsize=4, color=bar_colors[i], edgecolor=edge_colors[i], 
               width=0.6, linewidth=1.5, alpha=0.7, zorder=1, error_kw={'ecolor': 'black', 'elinewidth': 1.5})
        
        # Draw Scatter Points (Individual data points)
        y_vals = df[col].values
        # Add slight jitter to x for scatter
        x_jitter = np.random.normal(i, 0.04, size=len(y_vals))
        ax.scatter(x_jitter, y_vals, color=edge_colors[i], s=40, zorder=2, alpha=0.9)

    # 4. Formatting Axes
    
    # Y-Axis
    ax.set_ylabel('% of Total', fontsize=14, color='black')
    ax.set_ylim(0, 65) # Extended limit for significance lines
    ax.tick_params(axis='y', labelsize=12)
    
    # X-Axis Labels
    x_labels = [
        'DMSO', 
        '40 nM', '100 nM', '200 nM', 
        '1 μM', '5 μM', '10 μM', 
        '0.2 μM', '1 μM', '5 μM'
    ]
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x_labels, rotation=90, fontsize=12)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.2)
    ax.spines['bottom'].set_linewidth(1.2)

    # 5. Adding Group Labels (Rapamycin, LY294002, MK2206)
    # We draw lines and text below the x-axis
    
    def add_group_label(start_idx, end_idx, label, y_line_pos, y_text_pos):
        # Draw line
        line_x = [start_idx, end_idx]
        line_y = [y_line_pos, y_line_pos]
        # Transform data coords to axes coords for y to place below axis
        ax.plot(line_x, line_y, color='black', linewidth=1.2, clip_on=False, transform=ax.get_xaxis_transform())
        # Add text
        ax.text((start_idx + end_idx) / 2, y_text_pos, label, 
                ha='center', va='top', fontsize=14, color='black', transform=ax.get_xaxis_transform())

    # Coordinates relative to x-axis (negative y means below)
    add_group_label(1, 3, 'Rapamycin', -0.25, -0.27)
    add_group_label(4, 6, 'LY294002', -0.25, -0.27)
    add_group_label(7, 9, 'MK2206', -0.25, -0.27)

    # 6. Statistical Significance Annotations
    # Drawing the stack of horizontal lines originating from DMSO
    
    start_y = 39 # Base height for lines
    step_y = 1.8 # Increment per line
    
    # Lines connect DMSO (index 0) to every other bar (indices 1-9)
    # The lines are stacked vertically.
    
    for i in range(1, 10):
        y_h = start_y + (i * step_y)
        # Draw horizontal line
        ax.plot([0, i], [y_h, y_h], color='black', linewidth=0.8)
        # No vertical ticks at ends in the specific style of the image, just the horizontal lines
    
    # Add P-value text
    from scipy import stats
    # Comparing DMSO (raw_data['DMSO']) vs MK2206 5uM (raw_data['MK2206_5uM'])
    _, p_val = stats.ttest_ind(raw_data['DMSO'], raw_data['MK2206_5uM'])
    
    if p_val < 0.0001:
        p_text = 'P < 0.0001'
    else:
        p_text = f'P = {p_val:.4f}'
        
    top_line_y = start_y + (9 * step_y)
    ax.text(4.5, top_line_y + 2, p_text, ha='center', fontsize=12)
    
    # Title
    ax.set_title('Live cells', fontsize=16, pad=20)

    # Adjust layout to prevent clipping of bottom labels
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.25) # Extra space for group labels

    # Save output
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)