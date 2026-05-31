import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns

def generate_chart(output_filename):
    # 1. Data Preparation
    # Reconstructing the dataframe from the provided Markdown table source data.
    # Columns: DMSO, Rapa 40nM, Rapa 100nM, Rapa 200nM, LY 1uM, LY 5uM, LY 10uM, MK 0.2uM, MK 1uM
    
    data = {
        'DMSO': [62, 65, 65, 59],
        'Rapamycin_40nM': [70, 67, 66, 64],
        'Rapamycin_100nM': [71, 72, 71, 68],
        'Rapamycin_200nM': [70, 70, 72, 66],
        'LY294002_1uM': [66, 67, 66, 62],
        'LY294002_5uM': [74, 74, 68, 63],
        'LY294002_10uM': [80, 72, 69, 65],
        'MK2206_0.2uM': [84, 85, 85, 85],
        'MK2206_1uM': [80, 80, 84, 79]
    }
    
    df = pd.DataFrame(data)
    
    # Calculate means and standard deviations for plotting
    means = df.mean()
    stds = df.std()
    
    # 2. Plot Setup
    fig, ax = plt.subplots(figsize=(6, 5))
    
    # Define Colors based on the image
    # DMSO: Grey
    # Rapamycin: Light Pink -> Dark Pink
    # LY294002: Light Blue -> Dark Blue
    # MK2206: Light Purple -> Dark Purple
    
    colors_fill = [
        '#808080', # DMSO
        '#F4C2C2', '#E699A8', '#D8708F', # Rapamycin
        '#D6EAF8', '#AED6F1', '#5D8AA8', # LY294002 (Last one is darker blue/greyish)
        '#D7BDE2', '#8E44AD'  # MK2206
    ]
    
    # Edge colors (slightly darker versions for borders and dots)
    colors_edge = [
        '#404040', # DMSO
        '#D98896', '#C76B7E', '#B04060', # Rapamycin
        '#85C1E9', '#5DADE2', '#2E5A88', # LY294002
        '#AF7AC5', '#6C3483'  # MK2206
    ]

    x_pos = np.arange(len(df.columns))
    
    # 3. Draw Bars
    # We iterate to set individual colors
    for i, col in enumerate(df.columns):
        ax.bar(i, means[col], yerr=stds[col], capsize=4, color=colors_fill[i], edgecolor=colors_edge[i], 
               width=0.6, linewidth=1.5, alpha=0.8, zorder=1, error_kw={'ecolor': 'black', 'elinewidth': 1.5})
        
    # 4. Draw Scatter Points (Individual Data)
    # Using seaborn stripplot for the jitter effect, but mapping manually to match x_pos
    melted_df = df.melt(var_name='Group', value_name='Value')
    
    # Create a custom palette for seaborn to match our edge colors
    sns.stripplot(data=melted_df, x='Group', y='Value', jitter=True, ax=ax, 
                  palette=colors_edge, size=6, alpha=0.9, zorder=2, legend=False)

    # 5. Statistical Annotations
    # Replicating the lines and P-values exactly as shown in the image.
    # The lines stack vertically.
    from scipy import stats

    def get_p_text(group1, group2):
        _, p_val = stats.ttest_ind(data[group1], data[group2])
        if p_val < 0.0001:
            return "P < 0.0001"
        else:
            return f"P = {p_val:.4f}"
    
    def draw_significance(x1, x2, y_line, text, y_text_offset=3):
        # Draw the horizontal line
        ax.plot([x1, x2], [y_line, y_line], color='black', linewidth=0.8)
        # Draw text centered
        ax.text((x1 + x2) * 0.5, y_line + y_text_offset, text, 
                ha='center', va='bottom', color='black', fontsize=10)

    # Line 1: DMSO vs Rapamycin 40nM (Index 0 vs 1)
    draw_significance(0, 1, 85, get_p_text('DMSO', 'Rapamycin_40nM'))
    
    # Line 2: DMSO vs Rapamycin 100nM (Index 0 vs 2)
    draw_significance(0, 2, 115, get_p_text('DMSO', 'Rapamycin_100nM'))
    
    # Line 3: DMSO vs Rapamycin 200nM (Index 0 vs 3)
    draw_significance(0, 3, 145, get_p_text('DMSO', 'Rapamycin_200nM'))
    
    # Line 4: DMSO vs LY 1uM (Index 0 vs 4)
    draw_significance(0, 4, 175, get_p_text('DMSO', 'LY294002_1uM'))
    
    # Line 5: DMSO vs MK 0.2uM (Index 0 vs 7) - The highest line
    draw_significance(0, 7, 205, get_p_text('DMSO', 'MK2206_0.2uM'))

    # 6. Formatting
    
    # Y-Axis
    ax.set_ylabel("% of live CD8+", fontsize=12, color='black')
    ax.set_ylim(0, 230) # Extended to fit the top annotation
    ax.set_yticks([0, 50, 100, 150, 200])
    
    # X-Axis
    ax.set_xticks(x_pos)
    # The image does not show text labels on the x-axis, just ticks.
    ax.set_xticklabels([]) 
    
    # Title
    ax.set_title("Ki-67$^{+}$", fontsize=14, pad=20)
    
    # Styling
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1)
    
    # Adjust layout to prevent clipping
    plt.tight_layout()
    
    # Save
    plt.savefig(output_filename, dpi=300)

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    generate_chart(output_file)