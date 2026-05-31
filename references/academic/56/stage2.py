import sys
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import io
from scipy import stats

def create_chart(output_filename):
    # ---------------------------------------------------------
    # 1. Data Processing
    # ---------------------------------------------------------
    # Reconstructing the data from the source table provided
    # Structure: Dictionary of 'Label' -> [Values]
    
    data_map = {
        "DMSO": {
            "vals": [9.07, 10.2, 12.2, 10.4],
            "group": "DMSO",
            "conc": "DMSO"
        },
        "Rapa_40": {
            "vals": [61.6, 56.6, 58.1, 57.0],
            "group": "Rapamycin",
            "conc": "40 nM"
        },
        "Rapa_100": {
            "vals": [59.0, 59.2, 60.1, 59.3],
            "group": "Rapamycin",
            "conc": "100 nM"
        },
        "Rapa_200": {
            "vals": [62.8, 60.0, 59.8, 60.8],
            "group": "Rapamycin",
            "conc": "200 nM"
        },
        "LY_1": {
            "vals": [20.8, 26.5, 27.6, 26.5],
            "group": "LY294002",
            "conc": "1 μM"
        },
        "LY_5": {
            "vals": [59.0, 59.6, 59.2, 56.7],
            "group": "LY294002",
            "conc": "5 μM"
        },
        "LY_10": {
            "vals": [78.6, 76.9, 75.5, 75.0],
            "group": "LY294002",
            "conc": "10 μM"
        },
        "MK_0.2": {
            "vals": [66.3, 67.1, 66.7, 67.3],
            "group": "MK2206",
            "conc": "0.2 μM"
        },
        "MK_1": {
            "vals": [71.1, 73.7, 74.1, 71.7],
            "group": "MK2206",
            "conc": "1 μM"
        }
    }

    # Order of plotting
    order = [
        "DMSO", 
        "Rapa_40", "Rapa_100", "Rapa_200", 
        "LY_1", "LY_5", "LY_10", 
        "MK_0.2", "MK_1"
    ]

    # X-axis positions (Manual spacing to create gaps between groups)
    # DMSO at 0, Gap, Rapa at 1.5, 2.3, 3.1, Gap, LY at 4.6, 5.4, 6.2, Gap, MK at 7.7, 8.5
    # We use roughly 0.8 spacing between bars in a group, larger gaps between groups.
    positions = [0, 1.5, 2.3, 3.1, 4.6, 5.4, 6.2, 7.7, 8.5]
    
    # ---------------------------------------------------------
    # 2. Styling Configuration
    # ---------------------------------------------------------
    # Colors (Face colors)
    colors = [
        "#666666", # DMSO (Grey)
        "#F2C6D4", "#E897B3", "#D96593", # Rapamycin (Light -> Dark Pink)
        "#D1EBF5", "#A8CCEB", "#6D8CC4", # LY (Light -> Dark Blue)
        "#DCCBE6", "#967EB3"             # MK (Light -> Dark Purple)
    ]
    
    # Border colors (Slightly darker or same as fill with solid alpha)
    edge_colors = [
        "#444444", 
        "#DFA0B6", "#D07A9A", "#B84A78",
        "#B0D5E5", "#8BB0D0", "#5070A8",
        "#C0B0D0", "#7A6095"
    ]

    # ---------------------------------------------------------
    # 3. Plotting
    # ---------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6, 5))

    bar_width = 0.65

    # Lists to store coordinates for significance lines
    bar_tops = []
    
    for i, key in enumerate(order):
        vals = data_map[key]["vals"]
        x_pos = positions[i]
        
        # Calculate statistics
        mean_val = np.mean(vals)
        std_val = np.std(vals) # Not explicitly used for error bars in image, but good to have
        
        # 1. Draw Bar
        ax.bar(x_pos, mean_val, width=bar_width, 
               color=colors[i], edgecolor=colors[i], 
               linewidth=1.5, alpha=0.9, zorder=2)
        
        # 2. Draw Scatter Points (Individual replicates)
        # Using the same color but slightly darker/solid for visibility
        ax.scatter([x_pos] * len(vals), vals, 
                   color=colors[i], edgecolor=edge_colors[i], 
                   s=40, zorder=3, alpha=1.0, linewidth=1.0)
        
        # Store top for reference if needed, though significance lines are fixed height
        bar_tops.append(mean_val)

    # ---------------------------------------------------------
    # 4. Significance Lines (The "Ladder")
    # ---------------------------------------------------------
    # The lines originate from above DMSO and extend to specific bars.
    # Looking at the image, there is a master vertical line at DMSO x-pos.
    # Horizontal lines branch off to the significant bars.
    # The non-significant bar (LY 1uM, index 4) is skipped.
    
    # Indices of bars to connect to DMSO (index 0)
    # Dynamically determine significant columns
    target_indices = []
    dmso_vals = data_map[order[0]]["vals"]
    p_threshold = 0.0001
    
    for i in range(1, len(order)):
        vals = data_map[order[i]]["vals"]
        t_stat, p_val = stats.ttest_ind(dmso_vals, vals)
        if p_val < p_threshold:
            target_indices.append(i)
    
    dmso_x = positions[0]
    
    # Start height for the lowest line in the stack
    start_y = 66
    step_y = 4.5  # Vertical spacing between lines
    
    if target_indices:
        # Draw the vertical spine at DMSO
        # It goes from the lowest significance line to the highest
        max_y_line = start_y + (len(target_indices) - 1) * step_y
        ax.plot([dmso_x, dmso_x], [start_y, max_y_line], color='black', linewidth=0.8, zorder=1)

        # Draw horizontal lines to targets
        for idx, target_idx in enumerate(target_indices):
            y_pos = start_y + idx * step_y
            target_x = positions[target_idx]
            ax.plot([dmso_x, target_x], [y_pos, y_pos], color='black', linewidth=0.8, zorder=1)

        # Add the P-value text
        # Centered roughly over the whole spread or the top line
        # The image has it centered above the top line which spans most of the chart
        text_y = max_y_line + 3
        text_x = (positions[0] + positions[-1]) / 2  # Center of chart
        ax.text(text_x, text_y, f"P < {p_threshold}", ha='center', va='bottom', fontsize=12, color='black')

    # ---------------------------------------------------------
    # 5. Axis Formatting & Labels
    # ---------------------------------------------------------
    
    # Y Axis
    ax.set_ylim(0, 100)
    ax.set_ylabel("% of live CD8$^+$", fontsize=14, color='black')
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.tick_params(axis='y', labelsize=12, width=1, length=4)
    
    # X Axis
    ax.set_xticks(positions)
    xtick_labels = [data_map[k]["conc"] for k in order]
    ax.set_xticklabels(xtick_labels, rotation=90, fontsize=12)
    
    # Remove standard bottom spine to draw custom group lines? 
    # No, keep spine, just add extra lines below for groups.
    
    # Add Group Labels (Rapamycin, LY..., MK...)
    # We draw a line under the group and place text below it.
    
    def add_group_label(start_idx, end_idx, label):
        x1 = positions[start_idx]
        x2 = positions[end_idx]
        # Line Y position (in axis coordinates, negative to be under labels)
        # We need to use data coordinates for X and strictly offsets for Y relative to axis
        # Easier to just use data coordinates for Y if we turn off clipping, 
        # but plotting outside axes can be tricky.
        # Let's use transforms to place relative to X axis.
        
        line_y = -0.22 # Relative to axes height (negative means below)
        text_y = -0.32
        
        # Calculate centered x
        mid_x = (x1 + x2) / 2
        
        # Draw the line
        # We use ax.transData for x, and a blended transform for y is complex, 
        # so let's stick to hardcoded negative Y values in data coordinates 
        # (assuming ylim is 0, we can plot at negative y).
        # To do this, we must allow plotting outside [0, 100] visually or turn off clipping.
        # Actually, simpler: Standard plot at negative Y data coords works if ylim isn't strict clipping.
        # But we set ylim(0, 100).
        # Solution: Use transformation.
        
        import matplotlib.transforms as mtransforms
        trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
        
        # Draw line
        ax.plot([x1, x2], [line_y, line_y], transform=trans, color='black', clip_on=False, linewidth=1)
        
        # Draw Text
        ax.text(mid_x, text_y, label, transform=trans, ha='center', va='top', fontsize=12, color='black')

    # Group indices in 'order' list:
    # Rapamycin: indices 1 to 3
    add_group_label(1, 3, "Rapamycin")
    # LY294002: indices 4 to 6
    add_group_label(4, 6, "LY294002")
    # MK2206: indices 7 to 8
    add_group_label(7, 8, "MK2206")

    # Title
    ax.set_title("CD44$^+$CD62L$^+$", fontsize=16, pad=15)

    # Adjust Layout
    # Increase bottom margin to fit the rotated labels and group names
    plt.subplots_adjust(bottom=0.25, left=0.15, right=0.95, top=0.88)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # ---------------------------------------------------------
    # 6. Save Output
    # ---------------------------------------------------------
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    create_chart(output_file)