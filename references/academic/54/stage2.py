import matplotlib.pyplot as plt
import numpy as np
import sys

def generate_chart(output_filename):
    # 1. Source Data
    # Organized as a list of lists corresponding to the columns in the provided table
    # Mapping:
    # 0: DMSO
    # 1: Rapamycin 40 nM
    # 2: Rapamycin 100 nM
    # 3: Rapamycin 200 nM
    # 4: LY294002 1 uM
    # 5: LY294002 5 uM
    # 6: LY294002 10 uM
    # 7: MK2206 0.2 uM
    # 8: MK2206 1 uM
    
    data = [
        [3.22, 2.5, 2.29, 2.37],       # DMSO
        [2.15, 1.72, 1.35, 2.07],      # Rap 40 nM
        [1.79, 1.58, 1.35, 1.42],      # Rap 100 nM
        [2.01, 1.51, 1.19, 2.14],      # Rap 200 nM
        [3.42, 3.01, 4.06, 3.32],      # LY 1 uM
        [13, 11.7, 11.9, 11.7],        # LY 5 uM
        [15.8, 16.2, 16.2, 16.1],      # LY 10 uM
        [28, 31.5, 32.7, 32.6],        # MK 0.2 uM
        [78.8, 73.6, 82.3, 83.2]       # MK 1 uM
    ]

    # Calculate Means and Standard Deviations
    means = [np.mean(d) for d in data]
    stds = [np.std(d, ddof=1) for d in data] # Using sample standard deviation

    # 2. Visual Configuration
    
    # Define Colors based on the chart image
    # DMSO: Dark Grey
    # Rapamycin (3 bars): Pinkish/Rose
    # LY (3 bars): Light Blue -> Medium Blue
    # MK (2 bars): Light Purple -> Dark Purple
    colors = [
        '#444444', # DMSO
        '#CC7DA3', # Rap 40
        '#CC7DA3', # Rap 100
        '#CC7DA3', # Rap 200
        '#99C0DB', # LY 1 (Light Blue)
        '#99C0DB', # LY 5 (Light Blue)
        '#5C85AD', # LY 10 (Medium Blue)
        '#CDB5D9', # MK 0.2 (Light Purple)
        '#705592'  # MK 1 (Dark Purple)
    ]

    # Create Figure
    fig, ax = plt.subplots(figsize=(6, 5))

    # X positions
    x_pos = np.arange(len(data))

    # 3. Plotting
    
    for i in range(len(data)):
        # Bar Plot
        # Facecolor is transparent version of the main color
        # Edgecolor is the solid main color
        ax.bar(x_pos[i], means[i], 
               yerr=stds[i], 
               capsize=4, 
               color=colors[i], 
               alpha=0.3, 
               edgecolor=colors[i], 
               linewidth=2, 
               width=0.6,
               error_kw={'ecolor': colors[i], 'elinewidth': 2})
        
        # Scatter Plot (Individual Data Points)
        # Add jitter to x-axis
        jitter = np.random.normal(0, 0.04, size=len(data[i]))
        ax.scatter(x_pos[i] + jitter, data[i], 
                   color=colors[i], 
                   s=40, 
                   zorder=5, 
                   alpha=0.9)

    # 4. Annotations (Significance Lines)
    
    # The chart shows lines connecting DMSO (index 0) to specific bars
    # Lines are stacked above the highest bar
    
    line_color = 'black'
    line_width = 0.8
    
    # Base height for lines (above the highest bar which is ~80)
    y_start = 86
    y_step = 4
    
    # Line 1: DMSO to LY 5 uM (Index 5)
    y1 = y_start
    ax.plot([0, 5], [y1, y1], color=line_color, linewidth=line_width)
    
    # Line 2: DMSO to LY 10 uM (Index 6)
    y2 = y_start + y_step
    ax.plot([0, 6], [y2, y2], color=line_color, linewidth=line_width)
    
    # Line 3: DMSO to MK 0.2 uM (Index 7)
    y3 = y_start + (y_step * 2)
    ax.plot([0, 7], [y3, y3], color=line_color, linewidth=line_width)
    
    # Line 4: DMSO to MK 1 uM (Index 8) - Topmost
    y4 = y_start + (y_step * 3)
    ax.plot([0, 8], [y4, y4], color=line_color, linewidth=line_width)
    
    # P-value Text
    from scipy import stats
    # DMSO (index 0) vs MK 1uM (index 8)
    _, p_val = stats.ttest_ind(data[0], data[8])
    
    if p_val < 0.0001:
        p_text = 'P < 0.0001'
    else:
        p_text = f'P = {p_val:.4f}'
        
    ax.text(4, y4 + 5, p_text, ha='center', va='bottom', fontsize=12, color='black')

    # 5. Formatting
    
    # Axes Labels and Title
    ax.set_ylabel('% of live CD8$^+$', fontsize=12, color='black')
    ax.set_title('SLAMF6$^+$TIM-3$^-$', fontsize=14, pad=15, color='black')
    
    # Y-Axis Ticks
    ax.set_ylim(0, 115) # Extend limit to fit annotations
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.tick_params(axis='y', labelsize=11)
    
    # X-Axis Ticks
    # The chart shows ticks but no text labels for the bars
    ax.set_xticks(x_pos)
    ax.set_xticklabels([]) 
    
    # Styling Spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.2)
    ax.spines['bottom'].set_linewidth(1.2)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save output
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    generate_chart(output_file)