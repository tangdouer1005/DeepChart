import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.patches as patches

def main():
    # 1. Handle Output Filename
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]

    # 2. Source Data
    # Extracted exactly from the provided Markdown table
    
    # Primary Tumor (PT) Data
    # Columns: GPX4 protein levels (a.u), FSP1 protein levels (a.u)
    pt_data = [
        (0.06784, 0.0802), (0.0908, 0.0968), (0.0579, 0.0871), (0.0372, 0.0682),
        (0.1016, 0.1147), (0.0, 0.0646), (0.0271, 0.1423), (0.0918, 0.1262),
        (0.0, 0.1117), (0.0, 0.1265), (0.0462, 0.0877), (0.0296, 0.0962),
        (0.0508, 0.1131), (0.0577, 0.0), (0.0206, 0.0587), (0.1052, 0.0995),
        (0.0421, 0.1306), (0.0481, 0.1284), (0.0458, 0.0823), (0.0268, 0.1239),
        (0.0837, 0.0969), (0.0445, 0.1038), (0.0547, 0.0749), (0.0391, 0.0746),
        (0.0763, 0.1051)
    ]

    # LN Metastasis (LN) Data
    # Columns: GPX4 protein levels (a.u), FSP1 protein levels (a.u)
    ln_data = [
        (0.0897, 0.0769), (0.0488, 0.105), (0.0082, 0.1191), (0.0635, 0.1346),
        (0.0197, 0.1102), (0.0041, 0.0744), (0.0757, 0.0942), (0.0758, 0.0956),
        (0.0702, 0.1068), (0.0735, 0.1209), (0.0378, 0.1431), (0.0, 0.0961),
        (0.0794, 0.0986), (0.1062, 0.049), (0.0652, 0.0947), (0.086, 0.1197),
        (0.0657, 0.1331), (0.0837, 0.0809), (0.1191, 0.0849), (0.0317, 0.1076),
        (0.0584, 0.0366), (0.0662, 0.1132)
    ]

    # Convert to DataFrames for easier handling
    df_pt = pd.DataFrame(pt_data, columns=['GPX4', 'FSP1'])
    df_ln = pd.DataFrame(ln_data, columns=['GPX4', 'FSP1'])

    # 3. Setup Plot
    fig, ax = plt.subplots(figsize=(6, 5))
    
    # Colors
    color_pt = '#888888'  # Grey for Primary Tumor
    color_ln = '#55a630'  # Green for LN Metastasis

    # 4. Plot Scatter Points
    # Primary Tumor: Hollow grey circles
    ax.scatter(df_pt['GPX4'], df_pt['FSP1'], 
               color='none', edgecolor=color_pt, s=60, linewidth=1.5, label='Primary tumor')
    
    # LN Metastasis: Hollow green circles
    ax.scatter(df_ln['GPX4'], df_ln['FSP1'], 
               color='none', edgecolor=color_ln, s=60, linewidth=1.5, label='LN metastasis')

    # 5. Plot Regression Lines
    # We use numpy polyfit to calculate the linear regression line (y = mx + b)
    
    # PT Regression
    m_pt, b_pt = np.polyfit(df_pt['GPX4'], df_pt['FSP1'], 1)
    x_range_pt = np.linspace(0, 0.11, 100) # Range matches visual extent of line
    ax.plot(x_range_pt, m_pt * x_range_pt + b_pt, color=color_pt, linewidth=4, alpha=0.9)

    # LN Regression
    m_ln, b_ln = np.polyfit(df_ln['GPX4'], df_ln['FSP1'], 1)
    x_range_ln = np.linspace(0, 0.12, 100) # Range matches visual extent of line
    ax.plot(x_range_ln, m_ln * x_range_ln + b_ln, color=color_ln, linewidth=4, alpha=0.9)

    # 6. Annotations and Styling
    
    # Axis Labels
    ax.set_xlabel("GPX4 protein levels (a.u)", fontsize=14, fontweight='bold', labelpad=5)
    ax.set_ylabel("FSP1 protein levels (a.u)", fontsize=14, fontweight='bold', labelpad=5)
    
    # Axis Limits and Ticks
    ax.set_xlim(0, 0.125)
    ax.set_ylim(0, 0.15)
    
    # Customize ticks
    ax.tick_params(axis='both', which='major', labelsize=12, width=1.5, length=5)
    # Set specific ticks to match image style if needed, but auto is close.
    # The image shows 0.00, 0.05, 0.10 on X
    ax.set_xticks([0.00, 0.05, 0.10])
    # The image shows 0.00, 0.05, 0.10, 0.15 on Y
    ax.set_yticks([0.00, 0.05, 0.10, 0.15])

    # Make spines thicker
    for spine in ax.spines.values():
        spine.set_linewidth(1.5)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # 7. Add Text Annotations
    
    # "s" label in top left
    ax.text(-0.15, 1.0, "s", transform=ax.transAxes, fontsize=20, fontweight='bold', va='top', ha='left')

    # In-plot Group Labels
    # "Melanoma Primary tumors" (Grey)
    ax.text(0.06, 0.035, "Melanoma\nPrimary tumors", color=color_pt, fontsize=11, fontweight='bold', ha='left')
    # "Melanoma LN metastasis" (Green)
    ax.text(0.06, 0.01, "Melanoma\nLN metastasis", color=color_ln, fontsize=11, fontweight='bold', ha='left')

    # 8. Statistical Box (Right side)
    # The box contains mixed colors, so we draw a rectangle and place text manually.
    
    # Box coordinates (data coords)
    box_x = 0.122
    box_y = 0.085
    box_width = 0.055 # Extends outside plot area
    box_height = 0.04
    
    # Since the box is partly outside the axes, it's easier to place relative to Axes coordinates
    # or just allow clipping to be off.
    
    # Let's use a fixed position relative to the axis for the text block
    # The box is roughly centered vertically around y=0.085
    
    # Draw the rectangle border
    rect = patches.Rectangle((0.118, 0.055), 0.055, 0.038, linewidth=2, edgecolor='black', facecolor='none', clip_on=False, zorder=10)
    ax.add_patch(rect)

    # Text inside the box
    # We use a small font size to fit
    text_x = 0.120
    line_spacing = 0.008
    start_y = 0.085
    
    font_props = {'fontsize': 9, 'fontweight': 'bold', 'ha': 'left'}
    
    from scipy import stats
    r_pt, _ = stats.pearsonr(df_pt['GPX4'], df_pt['FSP1'])
    s_pt, _ = stats.spearmanr(df_pt['GPX4'], df_pt['FSP1'])
    r_ln, _ = stats.pearsonr(df_ln['GPX4'], df_ln['FSP1'])
    s_ln, _ = stats.spearmanr(df_ln['GPX4'], df_ln['FSP1'])

    # Grey Text
    ax.text(text_x, start_y, f"Pearson= {r_pt:.4f}", color=color_pt, **font_props)
    ax.text(text_x, start_y - line_spacing, f"Spearman= {s_pt:.5f}", color=color_pt, **font_props)
    
    # Green Text
    ax.text(text_x, start_y - 2*line_spacing, f"Pearson= {r_ln:.4f}", color=color_ln, **font_props)
    ax.text(text_x, start_y - 3*line_spacing, f"Spearman {s_ln:.4f}", color=color_ln, **font_props)

    # Adjust layout to make room for the text box on the right
    plt.subplots_adjust(right=0.75, left=0.15, bottom=0.15, top=0.9)

    # Save
    plt.savefig(output_file, dpi=300)
    print(f"Chart saved to {output_file}")

if __name__ == "__main__":
    main()