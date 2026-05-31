import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

def create_chart(output_filename):
    # 1. Source Data Preparation
    # Data extracted exactly from the provided Markdown table
    data = {
        'DMSO': [33.9, 34.6, 42.6, 39.4],
        'Rap_40nM': [33.7, 40.1, 35.5, 37.1],
        'Rap_100nM': [35.7, 36.2, 36.8, 36.0],
        'Rap_200nM': [37.2, 36.7, 37.6, 37.7],
        'LY_1uM': [31.7, 40.0, 37.7, 40.1],
        'LY_5uM': [41.5, 42.6, 43.4, 40.3],
        'LY_10uM': [34.4, 38.7, 39.9, 37.4],
        'MK_0.2uM': [50.3, 48.4, 49.7, 51.7],
        'MK_1uM': [46.8, 41.7, 46.0, 47.6]
    }
    
    df = pd.DataFrame(data)
    
    # Calculate Means and Standard Deviations
    means = df.mean()
    stds = df.std()
    
    # 2. Visual Configuration
    # Defining colors to match the image: (Edge/Point Color, Face Color)
    # The image uses solid outlines/points and semi-transparent fills
    colors = [
        ('#4D4D4D', '#808080'), # DMSO (Grey)
        ('#D68CA0', '#EBCBD5'), # Rap 40nM (Light Pink)
        ('#C96685', '#E0A8B8'), # Rap 100nM (Med Pink)
        ('#B84070', '#D690A8'), # Rap 200nM (Dark Pink)
        ('#7DA6C2', '#CBE0EE'), # LY 1uM (Light Blue)
        ('#6B9AC9', '#B5CEE6'), # LY 5uM (Med Blue)
        ('#3B5998', '#8FA0C8'), # LY 10uM (Dark Blue)
        ('#9E9AC8', '#D6D4E8'), # MK 0.2uM (Light Purple)
        ('#5E3C99', '#9E8CBF')  # MK 1uM (Dark Purple)
    ]

    fig, ax = plt.subplots(figsize=(7, 5))
    
    # Bar width and positions
    bar_width = 0.65
    indices = np.arange(len(df.columns))
    
    # 3. Plotting
    for i, col in enumerate(df.columns):
        edge_color, face_color = colors[i]
        
        # Bar Plot
        # Using a lighter face color (simulated by alpha or specific hex) and solid edge
        ax.bar(i, means[col], width=bar_width, 
               color=face_color, edgecolor=edge_color, linewidth=2, 
               zorder=1, alpha=0.6)
        
        # Error Bars (Standard Deviation)
        # Caps are visible in the image
        ax.errorbar(i, means[col], yerr=stds[col], 
                    fmt='none', ecolor=edge_color, elinewidth=2, 
                    capsize=5, capthick=2, zorder=2)
        
        # Scatter Plot (Individual Data Points)
        # Jittering x values slightly for visibility if points overlap, though image shows them mostly centered
        # The image shows points aligned vertically, so we keep x constant
        y_values = df[col].values
        x_values = np.full_like(y_values, i)
        
        ax.scatter(x_values, y_values, color=edge_color, s=40, zorder=3, clip_on=False)

    # 4. Statistical Annotations
    # Line 1: DMSO to MK 0.2uM (Index 0 to 7)
    # Line 2: DMSO to MK 1uM (Index 0 to 8)
    
    def draw_significance_line(ax, x1, x2, y, text, h=2):
        # Draw the bracket
        ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1.0, c='k')
        # Add text
        ax.text((x1+x2)*.5, y+h+1, text, ha='center', va='bottom', color='black', fontsize=12)

    # Determine heights based on max data + margin
    max_y = df.max().max()
    line1_y = 56
    line2_y = 65
    
    from scipy import stats
    
    # P1: DMSO vs MK 0.2uM (Index 0 vs 7)
    _, p1 = stats.ttest_ind(df['DMSO'], df['MK_0.2uM'], equal_var=True)
    p1_text = "P < 0.0001" if p1 < 0.0001 else f"P = {p1:.4f}"
    
    # P2: DMSO vs MK 1uM (Index 0 vs 8)
    _, p2 = stats.ttest_ind(df['DMSO'], df['MK_1uM'], equal_var=True)
    p2_text = "P < 0.0001" if p2 < 0.0001 else f"P = {p2:.4f}"
    
    draw_significance_line(ax, 0, 7, line1_y, p1_text)
    draw_significance_line(ax, 0, 8, line2_y, p2_text)

    # 5. Layout and Styling
    
    # Title
    # Using LaTeX for Greek letters
    ax.set_title(r'IFN$\gamma^+$TNF$\alpha^+$', fontsize=16, pad=35, color='black')
    
    # Y Axis
    ax.set_ylabel('% of live CD8$^+$', fontsize=14, color='black')
    ax.set_ylim(0, 75) # Extended limit to fit annotations
    ax.set_yticks([0, 20, 40, 60])
    ax.tick_params(axis='y', labelsize=12, color='black')
    
    # X Axis
    ax.set_xticks(indices)
    # The image does not show text labels for the x-axis categories, just ticks
    ax.set_xticklabels([]) 
    ax.tick_params(axis='x', length=5, width=1.5)

    # Spines (Borders)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    create_chart(output_file)