import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def get_source_data():
    """
    Returns the raw data provided in the prompt as a pandas DataFrame.
    """
    csv_data = """| Fig. 5d | Unnamed: 1 | Unnamed: 2 | Unnamed: 3 | Unnamed: 4 | Unnamed: 5 | Unnamed: 6 | Unnamed: 7 | Unnamed: 8 | Unnamed: 9 |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| Relative viability (%) | nan | nan | nan | nan | nan | nan | nan | nan | nan |
| F0Luc - Vehicule | F0Luc - viFSP1 (30 μM) | F0Luc - BSO (1mM) | F0Luc - viFSP1 (30 μM) + BSO (1mM) | F0Luc - viFSP1 (30 μM) + BSO (1mM) + Liprox (1μM) | LN8 - Vehicule | LN8 - viFSP1 (30 μM) | LN8 - BSO (1mM) | LN8 - viFSP1 (30 μM) + BSO (1mM) | LN8 -  viFSP1 (30 μM) + BSO (1mM) + Liprox (1μM) |
| 98.225957 | 98.8795518 | 74.4164332 | 78.2446312 | 105.50887 | 104.461688 | 110.766246 | 65.1794374 | 42.5800194 | 89.1367604 |
| 102.240896 | 102.521008 | 83.56676 | 89.9159664 | 99.1596639 | 98.6420951 | 100.969932 | 66.9253152 | 48.5935984 | 85.6450048 |
| 99.5331466 | 97.5723623 | 77.9645191 | 83.8468721 | 106.90943 | 97.0902037 | 95.4413191 | 63.5305529 | 51.2124151 | 86.3239573 |
"""
    # Read the markdown table format.
    # header=3 uses the 4th line (0-indexed index 3) as the header, which contains the group names.
    # This skips the title, separator, and unit rows.
    df = pd.read_csv(io.StringIO(csv_data), sep="|", header=3, skipinitialspace=True)
    
    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Drop the first and last columns which are empty due to markdown pipe borders
    df = df.iloc[:, 1:-1]
    
    # Convert all data to numeric, coercing errors just in case, though data should be clean now
    df = df.apply(pd.to_numeric, errors='coerce')
        
    return df

def draw_significance_bracket(ax, x1, x2, y, text, h=0.1, text_offset=0.1):
    """
    Draws a statistical significance bracket.
    x1, x2: horizontal indices (columns)
    y: vertical base position (in data coordinates, negative is up)
    h: height of the bracket legs
    text: P-value text
    """
    # Draw the bracket lines
    line_x = [x1, x1, x2, x2]
    line_y = [y + h, y, y, y + h] # Legs point down towards the plot (since y is inverted, 'up' is negative)
    
    # Actually, for imshow (origin upper), y increases downwards.
    # Top of heatmap is -0.5.
    # We want brackets above, so y < -0.5.
    # Legs should point downwards to the plot.
    # So if base is y (e.g. -1.0), legs go to y + h (e.g. -0.9).
    
    ax.plot(line_x, line_y, lw=1, c='k', clip_on=False)
    
    # Add text above the bracket
    # y is the horizontal bar level. Text goes above it (more negative y).
    ax.text((x1 + x2) / 2, y - text_offset, text, ha='center', va='bottom', fontsize=9, clip_on=False)

def generate_chart(output_filename):
    # 1. Get Data
    df = get_source_data()
    
    # Calculate means for the heatmap
    means = df.mean(axis=0).values
    # Reshape for imshow (1 row, 10 columns)
    heatmap_data = means.reshape(1, -1)

    # 2. Setup Figure
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # Adjust margins to make room for the table below and brackets above
    plt.subplots_adjust(bottom=0.35, top=0.75, left=0.1, right=0.85)

    # 3. Draw Heatmap
    # Use viridis colormap, range approx 40 to 100 based on data and visual
    cmap = plt.cm.viridis
    # origin='upper' is default, so y=0 is center, y=-0.5 is top edge
    im = ax.imshow(heatmap_data, cmap=cmap, vmin=40, vmax=100, aspect='auto')

    # Add black borders to cells
    for i in range(10):
        # Rectangle((x,y), width, height). 
        # x: i-0.5 (left edge). y: -0.5 (top edge).
        rect = patches.Rectangle((i - 0.5, -0.5), 1, 1, linewidth=1, edgecolor='black', facecolor='none')
        ax.add_patch(rect)

    # 4. Configure Axes
    ax.set_xticks(np.arange(10))
    ax.set_yticks([]) # Hide Y ticks
    ax.set_xticklabels([]) # Hide default X labels
    
    # Remove spines
    for spine in ax.spines.values():
        spine.set_visible(False)

    # 5. Add Colorbar
    cbar_ax = fig.add_axes([0.87, 0.45, 0.02, 0.15]) # [left, bottom, width, height]
    cbar = fig.colorbar(im, cax=cbar_ax, ticks=[40, 60, 80, 100])
    cbar.ax.set_ylabel('Relative\nviability\n(%)', rotation=90, labelpad=10, fontsize=10)
    cbar.ax.tick_params(labelsize=9)

    # 6. Draw Custom X-Axis Table/Matrix
    row_labels = ["Vehicle", "viFSP1 (30 μM)", "L-BSO (1 mM)", "Liproxstatin-1 (1 μM)"]
    
    # Matrix state (0=minus, 1=plus)
    # Col indices: 0  1  2  3  4  | 5  6  7  8  9
    # Logic:
    # Col 0/5: Vehicle Control -> Vehicle row (+), others (-)
    # Col 1/6: viFSP1 -> viFSP1 (+), others (-)
    # Col 2/7: BSO -> BSO (+), others (-)
    # Col 3/8: viFSP1 + BSO -> Both (+)
    # Col 4/9: Triple -> All three (+)
    matrix = [
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 0], # Vehicle
        [0, 1, 0, 1, 1, 0, 1, 0, 1, 1], # viFSP1
        [0, 0, 1, 1, 1, 0, 0, 1, 1, 1], # L-BSO
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 1]  # Liprox
    ]

    # Y-positions for the matrix rows (relative to axis coordinates)
    # Since y axis is inverted in imshow (down is positive), we go > 0.5
    start_y = 1.2 
    step_y = 0.6
    
    for row_idx, row_data in enumerate(matrix):
        y_pos = start_y + (row_idx * step_y)
        
        # Draw row label on the right
        ax.text(10.2, y_pos, row_labels[row_idx], ha='left', va='center', fontsize=10, transform=ax.get_xaxis_transform())
        
        # Draw +/- signs
        for col_idx, val in enumerate(row_data):
            symbol = "+" if val == 1 else "−" # Using proper minus sign
            weight = 'bold' if val == 1 else 'normal'
            ax.text(col_idx, y_pos, symbol, ha='center', va='center', fontsize=10, fontweight=weight, transform=ax.get_xaxis_transform())
            
            # Draw small tick mark connecting heatmap to matrix
            if row_idx == 0:
                # Draw tick from bottom of heatmap (0.5) to slightly below
                ax.plot([col_idx, col_idx], [0.5, 0.8], color='black', linewidth=1, clip_on=False)

    # 7. Add Group Labels and Lines
    # Vertical separator line between groups (between index 4 and 5)
    ax.plot([4.5, 4.5], [-0.5, 0.5], color='black', linewidth=1, clip_on=False) # Through heatmap
    
    # Line extending down through matrix
    matrix_bottom = start_y + (3 * step_y) + 0.5
    ax.plot([4.5, 4.5], [0.5, matrix_bottom], color='black', linewidth=1, clip_on=False, transform=ax.get_xaxis_transform())

    # Group Labels (B16-F0, LN8-1194BR)
    line_y = matrix_bottom + 0.3
    
    # Left Group Line
    ax.plot([0, 4], [line_y, line_y], color='black', linewidth=1, clip_on=False, transform=ax.get_xaxis_transform())
    ax.text(2, line_y + 0.4, "B16-F0", ha='center', va='top', fontsize=11, transform=ax.get_xaxis_transform())
    
    # Right Group Line
    ax.plot([5, 9], [line_y, line_y], color='black', linewidth=1, clip_on=False, transform=ax.get_xaxis_transform())
    ax.text(7, line_y + 0.4, "LN8-1194BR", ha='center', va='top', fontsize=11, transform=ax.get_xaxis_transform())

    # Bottom Label (1% O2)
    ax.plot([0, 9], [line_y + 1.2, line_y + 1.2], color='black', linewidth=1, clip_on=False, transform=ax.get_xaxis_transform())
    ax.text(4.5, line_y + 1.6, "1% O$_2$", ha='center', va='top', fontsize=11, transform=ax.get_xaxis_transform())

    # 8. Add Statistical Brackets
    # y coordinates are negative (above the heatmap).
    # Heatmap top is -0.5.
    
    # Bracket 1: Col 0 vs Col 3 (A vs D). P = 0.0057
    draw_significance_bracket(ax, 0, 3, -0.8, "P = 0.0057", h=0.1, text_offset=0.05)
    
    # Bracket 2: Col 3 vs Col 4 (D vs E). P = 0.0005
    draw_significance_bracket(ax, 3, 4, -1.5, "P = 0.0005", h=0.1, text_offset=0.05)
    
    # Bracket 3: Col 3 vs Col 8 (D vs I). P = 6.1 x 10^-8
    # This is the highest bracket spanning across groups
    draw_significance_bracket(ax, 3, 8, -2.5, r"$P = 6.1 \times 10^{-8}$", h=0.1, text_offset=0.05)
    
    # Bracket 4: Col 5 vs Col 8 (F vs I). P = 9.8 x 10^-11
    draw_significance_bracket(ax, 5, 8, -1.5, r"$P = 9.8 \times 10^{-11}$", h=0.1, text_offset=0.05)
    
    # Bracket 5: Col 8 vs Col 9 (I vs J). P = 1.6 x 10^-8
    draw_significance_bracket(ax, 8, 9, -0.8, r"$P = 1.6 \times 10^{-8}$", h=0.1, text_offset=0.05)

    # 9. Figure Label
    # Position relative to axes
    ax.text(-0.1, 1.15, "d", fontsize=18, fontweight='bold', ha='right', va='bottom', transform=ax.transAxes)

    # Save
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    generate_chart(output_file)