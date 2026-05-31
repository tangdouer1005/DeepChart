import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def generate_chart(output_filename):
    # 1. Data Preparation
    # Reconstructing the dataframe from the provided source data
    data = {
        'DMSO': [743, 799, 1143, 728],
        '40 nM': [370, 311, 245, 298],
        '100 nM': [357, 342, 247, 314],
        '200 nM': [645, 316, 291, 352],
        '1 μM (LY)': [584, 757, 600, 835],  # Renamed to distinguish from MK 1uM
        '5 μM': [567, 566, 504, 517],
        '10 μM': [513, 530, 521, 451],
        '0.2 μM': [2874, 2719, 2494, 2903],
        '1 μM (MK)': [3053, 2862, 2556, 2965] # Renamed to distinguish from LY 1uM
    }

    # Convert to Long Format for Seaborn
    df_list = []
    for condition, values in data.items():
        for val in values:
            # Clean label for display (remove the helper text in parentheses)
            display_label = condition.split(' (')[0]
            df_list.append({'Condition': condition, 'DisplayLabel': display_label, 'MFI': val})
    
    df = pd.DataFrame(df_list)

    # 2. Plot Setup
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
    
    fig, ax = plt.subplots(figsize=(7, 6))

    # Define Colors (matching the image)
    # DMSO: Grey
    # Rapamycin: Light Pink -> Dark Pink
    # LY294002: Light Blue -> Dark Blue
    # MK2206: Light Purple -> Dark Purple
    colors = [
        "#666666", # DMSO
        "#E6B0AA", "#D98880", "#C0392B", # Rapamycin (Pinks/Reds)
        "#AED6F1", "#5DADE2", "#2E86C1", # LY (Blues)
        "#D7BDE2", "#884EA0"             # MK (Purples)
    ]

    # 3. Draw Bar Plot
    # errorbar='sd' is used to represent Standard Deviation as seen in the spread of the chart
    bar_plot = sns.barplot(
        data=df, 
        x='Condition', 
        y='MFI', 
        palette=colors, 
        ax=ax, 
        errorbar='sd', 
        capsize=0.15, 
        err_kws={'linewidth': 1.5, 'color': 'gray'},
        alpha=0.8,
        edgecolor=None
    )

    # 4. Draw Individual Data Points (Strip Plot)
    sns.stripplot(
        data=df, 
        x='Condition', 
        y='MFI', 
        color='black', # Base color, will be overridden or blended
        palette=colors, # Use same palette to match tone
        ax=ax, 
        jitter=True, 
        size=6, 
        alpha=0.6,
        edgecolor='gray',
        linewidth=0.5
    )
    
    # Fix the point colors to be slightly darker versions of the bars or semi-transparent
    # The stripplot palette argument maps colors, but we want them slightly distinct.
    # Using the same palette with alpha/edgecolor usually achieves the look.

    # 5. Axis Formatting
    ax.set_ylabel("MFI", fontsize=14, fontweight='bold')
    ax.set_xlabel("")
    ax.set_title("CD107a", fontsize=16, pad=20)
    
    # Set Y-axis limit to accommodate significance lines
    ax.set_ylim(0, 4500)
    
    # X-Axis Labels
    # We use the 'DisplayLabel' logic to ensure "1 μM" appears correctly for both groups
    labels = [
        "DMSO", 
        "40 nM", "100 nM", "200 nM", 
        "1 μM", "5 μM", "10 μM", 
        "0.2 μM", "1 μM"
    ]
    ax.set_xticklabels(labels, rotation=90, fontsize=12)

    # Remove top and right spines
    sns.despine()

    # 6. Add Grouping Labels (Rapamycin, LY294002, MK2206)
    # We draw lines and text below the x-axis
    # Coordinates are data-relative. Y=0 is the x-axis line.
    
    def add_group_label(start_idx, end_idx, label, y_line, y_text):
        # Draw line
        ax.plot([start_idx, end_idx], [y_line, y_line], color='black', clip_on=False, linewidth=1)
        # Add text
        ax.text((start_idx + end_idx) / 2, y_text, label, ha='center', va='top', fontsize=12, clip_on=False)

    # Y-offsets for group labels (negative values to go below axis)
    y_line_pos = -600
    y_text_pos = -700
    
    # Rapamycin (Indices 1-3)
    add_group_label(1, 3, "Rapamycin", y_line_pos, y_text_pos)
    # LY294002 (Indices 4-6)
    add_group_label(4, 6, "LY294002", y_line_pos, y_text_pos)
    # MK2206 (Indices 7-8)
    add_group_label(7, 8, "MK2206", y_line_pos, y_text_pos)

    # 7. Add Statistical Significance Annotations
    def add_stat_annotation(x1, x2, y, text):
        h = 50 # height of the bracket ticks
        col = 'k' # color
        
        # Draw the line
        ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1, c=col)
        # Add the text
        ax.text((x1+x2)*.5, y+h, text, ha='center', va='bottom', color=col, fontsize=10)

    # Coordinates based on visual inspection of the chart
    # DMSO is index 0
    from scipy import stats
    
    def get_p_text(group1_name, group2_name):
        # Look up data lists by name
        # data dict keys: 'DMSO', '40 nM', '100 nM', '200 nM', '1 μM (LY)', '5 μM', '10 μM', '0.2 μM', '1 μM (MK)'
        g1 = data[group1_name]
        g2 = data[group2_name]
        _, p = stats.ttest_ind(g1, g2)
        if p < 0.0001:
            return "P < 0.0001"
        else:
            return f"P = {p:.4f}"
    
    # P < 0.0001 (DMSO vs Rapamycin 40nM [Index 1])
    add_stat_annotation(0, 1, 1300, get_p_text('DMSO', '40 nM'))
    
    # P = 0.0005 (DMSO vs Rapamycin 100nM [Index 2])
    add_stat_annotation(0, 2, 2100, get_p_text('DMSO', '100 nM'))
    
    # P = 0.0197 (DMSO vs Rapamycin 200nM [Index 3])
    add_stat_annotation(0, 3, 2750, get_p_text('DMSO', '200 nM'))
    
    # P = 0.0082 (DMSO vs LY 10uM [Index 6])
    add_stat_annotation(0, 6, 3300, get_p_text('DMSO', '10 μM')) # Wait, original code comments say LY 10uM, but logic connects 0 to 6.
    # Index 6 is '10 μM'. Let's verify.
    # Original code: add_stat_annotation(0, 6, 3300, "P = 0.0082")
    # Keys: DMSO(0), 40(1), 100(2), 200(3), LY1(4), LY5(5), LY10(6), MK0.2(7), MK1(8)
    # So yes, index 6 is LY 10 uM. 
    # BUT, the verification script for 57 calculated P for LY 10 and got 0.0126 vs 0.0082.
    # Let's use '10 μM' key.
    add_stat_annotation(0, 6, 3300, get_p_text('DMSO', '10 μM'))
    
    # P < 0.0001 (DMSO vs MK 1uM [Index 8])
    add_stat_annotation(0, 8, 4100, get_p_text('DMSO', '1 μM (MK)'))

    # Adjust layout to make room for bottom labels
    plt.subplots_adjust(bottom=0.25)

    # 8. Save Output
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    generate_chart(output_file)