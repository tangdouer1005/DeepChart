import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import Normalize

def get_data():
    """
    Returns the raw data and p-value annotations based on the provided source data.
    """
    # Raw viability data (3 replicates per condition)
    # Columns: 
    # 0-4: iFSP1 (Veh, Inh, BSO, Inh+BSO, Inh+BSO+Liprox)
    # 5-9: FSEN1
    # 10-14: icFSP1
    # 15-19: viFSP1
    
    # 21% O2 Data
    data_21_raw = [
        [98.7056719, 76.5021572, 79.2381353, 8.73408397, 77.1335368, 97.2427543, 90.1902811, 100.362117, 9.76496277, 89.1052853, 103.932584, 97.3033708, 102.247191, 9.43820225, 108.539326, 103.59955, 100.449944, 98.7626547, 29.2463442, 104.499438],
        [98.1795223, 80.8165842, 82.2898032, 9.89161317, 73.4504893, 101.447113, 88.0202894, 101.989611, 9.49371381, 87.2065425, 99.5505618, 103.820225, 95.9550562, 9.66292135, 97.5280899, 100.112486, 98.3127109, 93.1383577, 49.2688414, 101.799775],
        [103.125329, 84.078712, 82.8159529, 9.36546354, 76.817847, 101.311489, 96.7002563, 105.922721, 9.49371381, 90.7327791, 96.5168539, 100.898876, 95.0561798, 9.5505618, 100.224719, 96.287964, 92.0134983, 92.3509561, 38.920135, 99.4375703]
    ]

    # 1% O2 Data
    data_1_raw = [
        [109.105517, 95.8757365, 103.16015, 5.46331012, 88.0021425, 103.368906, 84.1703285, 109.123248, 9.67775685, 67.6919858, 98.8353284, 112.369244, 102.501887, 15.582875, 116.898523, 104.170905, 91.9125127, 110.834181, 67.5483215, 106.561546],
        [96.6791644, 88.2699518, 93.7332619, 5.57043385, 92.0728441, 98.3992467, 86.2628165, 94.1619586, 11.3517472, 81.0315966, 98.1882886, 113.501564, 100.938208, 14.9897552, 128.167799, 99.5422177, 102.899288, 95.930824, 75.4323499, 107.934893],
        [94.2153187, 92.0192823, 107.016604, 5.30262453, 82.3781468, 98.2423101, 80.5084746, 100.020925, 12.8164888, 75.0156937, 102.987167, 115.766203, 100.075488, 10.0830368, 109.026205, 96.3886063, 94.3540183, 114.954222, 72.5839268, 104.832146]
    ]

    # Calculate means
    mean_21 = np.mean(data_21_raw, axis=0)
    mean_1 = np.mean(data_1_raw, axis=0)

    # P-value annotations (Group Index, Start Col relative to group, End Col relative to group, Text)
    # Groups: 0=iFSP1, 1=FSEN1, 2=icFSP1, 3=viFSP1
    # Indices within group: 0=Veh, 3=Inh+BSO, 4=Inh+BSO+Liprox
    
    p_values_21 = [
        (0, 0, 3, r"$P = 2.6 \times 10^{-12}$"), (0, 3, 4, r"$P = 5.8 \times 10^{-11}$"),
        (1, 0, 3, r"$P = 8.1 \times 10^{-12}$"), (1, 3, 4, r"$P = 2.9 \times 10^{-11}$"),
        (2, 0, 3, r"$P = 2.2 \times 10^{-10}$"), (2, 3, 4, r"$P = 1.8 \times 10^{-10}$"),
        (3, 0, 3, r"$P = 3.7 \times 10^{-7}$"),  (3, 3, 4, r"$P = 2.8 \times 10^{-7}$"),
    ]

    p_values_1 = [
        (0, 0, 3, r"$P = 4.8 \times 10^{-9}$"), (0, 3, 4, r"$P = 1.9 \times 10^{-8}$"),
        (1, 0, 3, r"$P = 3.2 \times 10^{-9}$"), (1, 3, 4, r"$P = 8.7 \times 10^{-8}$"),
        (2, 0, 3, r"$P = 3 \times 10^{-9}$"),   (2, 3, 4, r"$P = 4.6 \times 10^{-10}$"),
        (3, 0, 3, r"$P = 0.0006$"),             (3, 3, 4, r"$P = 0.0001$"),
    ]

    return mean_21, mean_1, p_values_21, p_values_1

def draw_bracket(ax, x_start, x_end, y, h, text):
    """Draws a statistical significance bracket."""
    ax.plot([x_start, x_start, x_end, x_end], [y, y + h, y + h, y], lw=1, c='k')
    ax.text((x_start + x_end) * 0.5, y + h + 0.05, text, ha='center', va='bottom', color='k', fontsize=9)

def main(output_file):
    mean_21, mean_1, p_values_21, p_values_1 = get_data()
    
    # Setup Figure and Grid
    # We need 3 main rows: 21% O2 heatmap, 1% O2 heatmap, and the table
    # We use height ratios to allocate space for P-values and the table
    fig = plt.figure(figsize=(14, 6))
    gs = gridspec.GridSpec(3, 2, width_ratios=[20, 1], height_ratios=[1, 1, 1.2], wspace=0.02, hspace=0.8)
    
    # Axes
    ax_21 = fig.add_subplot(gs[0, 0])
    ax_1 = fig.add_subplot(gs[1, 0])
    ax_table = fig.add_subplot(gs[2, 0])
    cbar_ax = fig.add_subplot(gs[:2, 1]) # Shared colorbar for heatmaps

    # --- Plot Heatmaps ---
    # Reshape for imshow (1 row, 20 cols)
    im_21 = ax_21.imshow(mean_21.reshape(1, -1), cmap='viridis', aspect='auto', vmin=0, vmax=100)
    im_1 = ax_1.imshow(mean_1.reshape(1, -1), cmap='viridis', aspect='auto', vmin=0, vmax=100)

    # Styling Heatmaps
    for ax in [ax_21, ax_1]:
        ax.set_xticks([])
        ax.set_yticks([])
        # Add black borders to cells
        # We can do this by setting minor ticks and grid, or drawing rectangles.
        # Drawing rectangles is cleaner for exact control.
        for x in range(20):
            rect = plt.Rectangle((x - 0.5, -0.5), 1, 1, fill=False, edgecolor='black', lw=1)
            ax.add_patch(rect)
        
        # Add thicker vertical lines to separate groups
        for x in [4.5, 9.5, 14.5]:
            ax.axvline(x=x, color='black', linewidth=2)

    # Y-Axis Labels for Heatmaps
    ax_21.set_ylabel("21% O$_2$", rotation=0, ha='right', va='center', fontsize=12, labelpad=10)
    ax_1.set_ylabel("1% O$_2$", rotation=0, ha='right', va='center', fontsize=12, labelpad=10)

    # --- Add P-Value Annotations ---
    # Coordinate system for imshow: x centers are 0, 1, 2... y center is 0.
    # Top edge is -0.5, Bottom edge is 0.5.
    
    # 21% O2 Annotations (Above the bar)
    y_base = -0.5
    h_bracket = 0.2
    # Offset for the second level of brackets (Combo vs Rescue) to avoid overlap if needed, 
    # but in the chart they are at similar heights.
    
    for grp_idx, start_rel, end_rel, text in p_values_21:
        x_start = grp_idx * 5 + start_rel
        x_end = grp_idx * 5 + end_rel
        
        # Shift the "Combo vs Rescue" bracket slightly higher if they overlap visually?
        # In the chart, they look aligned but distinct.
        # The text for the first bracket (Veh vs Combo) is centered over 0-3.
        # The text for the second bracket (Combo vs Rescue) is centered over 3-4.
        
        # Adjust height slightly for visual staggering if needed, but chart uses one level mostly.
        # However, the text for the wide bracket might overlap the narrow bracket.
        # Let's push the wide bracket (Veh vs Combo) higher.
        
        if start_rel == 0: # Wide bracket
            draw_bracket(ax_21, x_start, x_end, y_base - 0.2, h_bracket, text)
        else: # Narrow bracket
            draw_bracket(ax_21, x_start, x_end, y_base - 0.2, h_bracket, text)

    # 1% O2 Annotations (Above the bar)
    for grp_idx, start_rel, end_rel, text in p_values_1:
        x_start = grp_idx * 5 + start_rel
        x_end = grp_idx * 5 + end_rel
        if start_rel == 0:
            draw_bracket(ax_1, x_start, x_end, y_base - 0.2, h_bracket, text)
        else:
            draw_bracket(ax_1, x_start, x_end, y_base - 0.2, h_bracket, text)

    # --- Colorbar ---
    cbar = plt.colorbar(im_21, cax=cbar_ax)
    cbar.set_label('Relative viability (%)', fontsize=12)
    cbar.set_ticks([0, 25, 50, 75, 100])

    # --- Bottom Table ---
    ax_table.set_xlim(-0.5, 19.5)
    ax_table.set_ylim(0, 4)
    ax_table.axis('off')

    # Table Rows
    row_labels = ["Vehicle", "BSO (100 µM)", "FSP1 inhibitors", "Liproxstatin-1 (1 µM)"]
    # In the chart, Vehicle is top, Liprox is bottom.
    # Let's map y-coords: Vehicle=3.5, BSO=2.5, FSP1=1.5, Liprox=0.5
    
    # Draw Row Labels
    for i, label in enumerate(row_labels):
        y = 3.5 - i
        ax_table.text(20, y, label, ha='left', va='center', fontsize=11)
        # Add "-" and "+" signs
        ax_table.text(20.5, y, "-", ha='center', va='center', fontsize=11) # Legend key part

    # Draw Grid and Signs
    # Logic for columns within a group of 5:
    # 0: Vehicle (+)
    # 1: FSP1 (+)
    # 2: BSO (+)
    # 3: FSP1 (+) + BSO (+)
    # 4: FSP1 (+) + BSO (+) + Liprox (+)
    
    # Row indices corresponding to labels:
    # Vehicle: 0
    # BSO: 1
    # FSP1: 2
    # Liprox: 3
    
    for col in range(20):
        rel_idx = col % 5
        
        # Determine presence (+) or absence (-)
        # Initialize all as "-"
        signs = ["-", "-", "-", "-"] 
        
        if rel_idx == 0: # Vehicle
            signs[0] = "+"
        elif rel_idx == 1: # FSP1 only
            signs[2] = "+"
        elif rel_idx == 2: # BSO only
            signs[1] = "+"
        elif rel_idx == 3: # FSP1 + BSO
            signs[1] = "+"
            signs[2] = "+"
        elif rel_idx == 4: # FSP1 + BSO + Liprox
            signs[1] = "+"
            signs[2] = "+"
            signs[3] = "+"
            
        # Draw signs
        for row_idx, sign in enumerate(signs):
            y = 3.5 - row_idx
            weight = 'bold' if sign == '+' else 'normal'
            ax_table.text(col, y, sign, ha='center', va='center', fontsize=10, fontweight=weight)

    # Group Labels (Bottom of table)
    group_labels = ["iFSP1 (10 µM)", "FSEN1 (10 µM)", "icFSP1 (15 µM)", "viFSP1 (15 µM)"]
    for i, label in enumerate(group_labels):
        x_center = i * 5 + 2
        ax_table.text(x_center, -0.5, label, ha='center', va='top', fontsize=12)
        # Draw line above label
        ax_table.plot([i*5, i*5+4], [-0.2, -0.2], color='black', lw=1)
        
    # Vertical lines in table to separate groups
    for x in [4.5, 9.5, 14.5]:
        ax_table.plot([x, x], [0, 4], color='black', lw=1)

    # Figure Title
    fig.text(0.02, 0.95, 'f', fontsize=20, fontweight='bold')

    # Adjust layout to ensure P-values don't get clipped
    # The hspace in GridSpec handles the gap between heatmaps.
    # We need to make sure the top margin is enough for the top P-values.
    plt.subplots_adjust(top=0.85, bottom=0.1, right=0.85, left=0.1)

    plt.savefig(output_file, dpi=300, bbox_inches='tight')

if __name__ == "__main__":
    output_path = "output.png"
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    main(output_path)