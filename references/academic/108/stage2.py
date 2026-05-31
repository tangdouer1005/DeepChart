import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import sys

def generate_chart(output_filename):
    # ---------------------------------------------------------
    # 1. Data Preparation
    # ---------------------------------------------------------
    
    # Raw replicate data extracted from the provided source table (Rows 3, 4, 5)
    # Columns 0-4: iFSP1 group
    # Columns 5-9: FSEN1 group
    # Columns 10-14: icFSP1 group
    # Columns 15-19: viFSP1 group
    raw_data = [
        [
            100.859599, 120.057307, 67.6217765, 26.0744986, 103.724928, 
            100.865801, 91.3419913, 93.5064935, 15.8008658, 87.012987, 
            105.707763, 111.415525, 60.2739726, 24.4292237, 108.219178, 
            100.149158, 94.8220754, 58.3848285, 33.0279139, 93.5435755
        ],
        [
            99.1404011, 122.922636, 65.6160458, 27.2206304, 112.320917, 
            100.649351, 88.7445887, 89.3939394, 18.1818182, 82.4675325, 
            99.3150685, 107.990868, 60.9589041, 25.5707763, 109.13242, 
            104.197741, 101.214575, 54.9754954, 33.2409972, 91.4127424
        ],
        [
            100.0, 121.776504, 63.8968481, 29.7994269, 105.157593, 
            98.9177489, 85.2813853, 92.6406926, 16.6666667, 78.1385281, 
            94.9771689, 102.283105, 52.9680365, 22.8310502, 97.716895, 
            95.6744087, 94.6089921, 50.0745792, 29.1924142, 98.0183252
        ]
    ]

    # Calculate mean for the heatmap
    data_means = np.mean(raw_data, axis=0).reshape(1, -1)

    # P-values extracted from the "Statistical test" section of the source data
    # Format: (Group Index, Start Column relative to group, End Column relative to group, Label)
    # Groups are 5 columns wide.
    # Comparisons: 
    # 1. Vehicle (0) vs Inhibitor+BSO (3)
    # 2. Inhibitor+BSO (3) vs Inhibitor+BSO+Liprox (4)
    
    # Note: P-values are formatted to match the visual style (scientific notation)
    # Source values:
    # iFSP1: 3.00e-11, 1.19e-11
    # FSEN1: 1.57e-11, 1.65e-10
    # icFSP1: 1.06e-8, 5.64e-9
    # viFSP1: 2.24e-9, 5.26e-9
    
    annotations = [
        # iFSP1 Group (Indices 0-4)
        (0, 0, 3, r"$P = 3 \times 10^{-11}$"),
        (0, 3, 4, r"$P = 1.2 \times 10^{-11}$"),
        
        # FSEN1 Group (Indices 5-9)
        (1, 0, 3, r"$P = 1.6 \times 10^{-11}$"),
        (1, 3, 4, r"$P = 1.7 \times 10^{-10}$"),
        
        # icFSP1 Group (Indices 10-14)
        (2, 0, 3, r"$P = 1.1 \times 10^{-8}$"),
        (2, 3, 4, r"$P = 5.6 \times 10^{-9}$"),
        
        # viFSP1 Group (Indices 15-19)
        (3, 0, 3, r"$P = 2.2 \times 10^{-9}$"),
        (3, 3, 4, r"$P = 5.3 \times 10^{-9}$"),
    ]

    group_labels = ["iFSP1 (10 µM)", "FSEN1 (10 µM)", "icFSP1 (15 µM)", "viFSP1 (15 µM)"]

    # ---------------------------------------------------------
    # 2. Plot Setup
    # ---------------------------------------------------------
    
    fig, ax = plt.subplots(figsize=(14, 4.5))
    
    # Adjust margins to fit the table below
    plt.subplots_adjust(bottom=0.35, top=0.85, left=0.08, right=0.92)

    # ---------------------------------------------------------
    # 3. Draw Heatmap
    # ---------------------------------------------------------
    
    # Create the heatmap
    # Using pcolormesh to easily add grid lines
    mesh = ax.pcolormesh(data_means, cmap='viridis', vmin=25, vmax=100, edgecolors='k', linewidth=0.5)
    
    # Aspect ratio to make cells square-ish
    ax.set_aspect('equal')
    
    # Y-axis Label
    ax.set_yticks([0.5])
    ax.set_yticklabels(['21% O$_2$'], fontsize=12)
    ax.tick_params(axis='y', length=5)
    
    # Remove X-axis ticks for now (we will build a custom table)
    ax.set_xticks([])
    
    # ---------------------------------------------------------
    # 4. Statistical Annotations (Brackets)
    # ---------------------------------------------------------
    
    def draw_bracket(ax, x1, x2, y_base, text, height_bracket=0.5, text_offset=0.2):
        # x1, x2 are column indices (0-based)
        # y_base is the top of the heatmap (which is 1.0)
        
        # Calculate coordinates
        # The cells are centered at x + 0.5
        lx = x1 + 0.5
        rx = x2 + 0.5
        
        # Bracket lines
        # Up, Across, Down
        line_x = [lx, lx, rx, rx]
        line_y = [y_base + 0.2, y_base + height_bracket, y_base + height_bracket, y_base + 0.2]
        
        ax.plot(line_x, line_y, color='black', lw=1, clip_on=False)
        
        # Text
        mid_x = (lx + rx) / 2
        ax.text(mid_x, y_base + height_bracket + text_offset, text, 
                ha='center', va='bottom', fontsize=10, clip_on=False)

    # Draw annotations
    # We stagger heights slightly if needed, but in the image they are mostly two levels
    # Level 1: Vehicle vs Inh+BSO (Wide)
    # Level 2: Inh+BSO vs Triple (Narrow) - This can be lower or same height?
    # In the image, the wide bracket is higher.
    
    for group_idx, start_rel, end_rel, label in annotations:
        abs_start = group_idx * 5 + start_rel
        abs_end = group_idx * 5 + end_rel
        
        # Determine height based on span
        if (end_rel - start_rel) > 1:
            h = 1.5 # Higher bracket for wide comparison
        else:
            h = 0.5 # Lower bracket for adjacent comparison
            
        draw_bracket(ax, abs_start, abs_end, 1.0, label, height_bracket=h)

    # ---------------------------------------------------------
    # 5. Custom X-Axis Table (Matrix of + / -)
    # ---------------------------------------------------------
    
    # Define the rows of the table
    row_labels = [
        "Vehicle",
        "BSO (100 µM)",
        "FSP1 inhibitors",
        "Liproxstatin-1 (1 µM)"
    ]
    
    # Define the pattern for one group (5 columns)
    # Columns: Vehicle, Inh, BSO, Inh+BSO, Inh+BSO+Liprox
    # Wait, let's verify column order from data headers:
    # 1. Vehicle (iFSP1)
    # 2. iFSP1
    # 3. BSO
    # 4. iFSP1 + BSO
    # 5. iFSP1 + BSO + Liprox
    
    # Matrix Logic (1=+, 0=-)
    # Row 1 (Vehicle): Only Col 1
    # Row 2 (BSO): Col 3, 4, 5
    # Row 3 (Inhibitor): Col 2, 4, 5
    # Row 4 (Liprox): Col 5
    
    group_pattern = [
        ["+", "-", "-", "-", "-"], # Vehicle Row
        ["-", "-", "+", "+", "+"], # BSO Row
        ["-", "+", "-", "+", "+"], # Inhibitor Row
        ["-", "-", "-", "-", "+"]  # Liprox Row
    ]
    
    # Construct full matrix for 20 columns
    full_matrix = []
    for r in range(4):
        full_row = []
        for g in range(4):
            full_row.extend(group_pattern[r])
        full_matrix.append(full_row)
        
    # Draw the matrix text
    y_start = -0.5 # Just below the heatmap (heatmap is y=0 to y=1)
    y_step = 0.6
    
    for i, label in enumerate(row_labels):
        y_pos = y_start - (i * y_step)
        
        # Draw Row Label
        ax.text(20.5, y_pos, "+ " + label, ha='left', va='center', fontsize=11)
        
        # Draw +/- signs
        for col in range(20):
            sign = full_matrix[i][col]
            # Bold the plus signs slightly or just use regular font
            fw = 'bold' if sign == '+' else 'normal'
            ax.text(col + 0.5, y_pos, sign, ha='center', va='center', fontsize=10, fontweight=fw)

    # ---------------------------------------------------------
    # 6. Group Labels and Separators
    # ---------------------------------------------------------
    
    # Draw vertical lines separating groups
    for i in range(1, 4):
        x_line = i * 5
        # Line from top of heatmap down to bottom of table
        # Heatmap top = 1. Table bottom approx -3.0
        ax.plot([x_line, x_line], [-2.8, 1.0], color='black', lw=1, clip_on=False)

    # Draw Group Labels at the bottom
    label_y_pos = y_start - (4 * y_step) + 0.2
    for i, label in enumerate(group_labels):
        center_x = (i * 5) + 2.5
        ax.text(center_x, label_y_pos, label, ha='center', va='top', fontsize=12)
        
        # Draw a horizontal line above the label (optional, matches style of some charts, 
        # but in the image it looks like the vertical lines define the groups)
        # The image has a line under the matrix for the group label.
        ax.plot([i*5 + 0.2, (i+1)*5 - 0.2], [label_y_pos + 0.1, label_y_pos + 0.1], 
                color='black', lw=1, clip_on=False)

    # ---------------------------------------------------------
    # 7. Colorbar
    # ---------------------------------------------------------
    
    # Create an inset axis for the colorbar
    # [left, bottom, width, height] relative to figure
    cax = fig.add_axes([0.93, 0.45, 0.015, 0.25])
    cbar = plt.colorbar(mesh, cax=cax, ticks=[25, 50, 75, 100])
    cbar.set_label('Relative\nviability\n(%)', fontsize=11)
    cbar.ax.set_yticklabels(['25', '50', '75', '100'])
    
    # ---------------------------------------------------------
    # 8. Final Adjustments and Save
    # ---------------------------------------------------------
    
    # Turn off main axis frame lines except left (for O2 label)? 
    # Actually, the heatmap has its own borders. We can turn off the main spines.
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(True) # Keep left for "21% O2" tick
    
    # Ensure the "21% O2" tick mark is visible
    ax.yaxis.set_ticks_position('left')

    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    generate_chart(output_file)