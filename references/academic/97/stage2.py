import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def generate_chart(output_filename):
    # 1. Data Extraction
    # Extracted directly from the provided Markdown table (Row: "Glutamate")
    # Parental Group: Columns Unnamed: 1 to Unnamed: 5 (F0luc columns)
    parental_values = [
        6204616.859286747,
        6031719.639947483,
        6442731.7845764635,
        6859345.48128456,
        6764765.683211772
    ]

    # LN Group: Columns Unnamed: 12 to Unnamed: 35 (LN columns)
    ln_values = [
        1478381.7987170925,
        1081751.8498301418,
        3928401.4065465294,
        3922032.1950288094,
        3110395.9232401457,
        3495866.48103521,
        2662220.3343282263,
        1907977.6288138991,
        2795104.0071977014,
        3534860.737689079,
        3006628.029078749,
        3037851.004063388,
        4632932.147138998,
        3595460.617386489,
        3721260.394931968,
        3859800.6117266854,
        3909206.586895387,
        3731577.4010725464,
        4910662.424020618,
        4314128.730348152,
        4225639.093779526,
        3720654.2353181,
        3489159.2704787264,
        3663818.5393517087
    ]

    # Create DataFrame
    df_parental = pd.DataFrame({'Intensity': parental_values, 'Group': 'Parental'})
    df_ln = pd.DataFrame({'Intensity': ln_values, 'Group': 'LN'})
    df = pd.concat([df_parental, df_ln], ignore_index=True)

    # Calculate Statistics for Bars
    means = df.groupby('Group', sort=False)['Intensity'].mean()
    stds = df.groupby('Group', sort=False)['Intensity'].std()
    
    # 2. Plot Setup
    # Figure size to match the vertical aspect ratio of the original image
    fig, ax = plt.subplots(figsize=(3.5, 6))
    
    # Define Colors
    color_parental_bar = '#D9D9D9'  # Light Grey
    color_parental_edge = 'black'
    color_parental_dots = 'black'
    
    color_ln_bar = '#A2CFA5'        # Muted Light Green
    color_ln_edge = '#2E7D32'       # Dark Green
    color_ln_dots = '#2E7D32'       # Dark Green

    # 3. Draw Bars
    # We draw bars manually to have full control over individual edge colors
    bar_width = 0.6
    
    # Parental Bar
    ax.bar(0, means['Parental'], width=bar_width, 
           color=color_parental_bar, edgecolor=color_parental_edge, 
           linewidth=1.5, yerr=stds['Parental'], capsize=6, 
           error_kw={'elinewidth': 1.5, 'ecolor': 'gray'})
    
    # LN Bar
    ax.bar(1, means['LN'], width=bar_width, 
           color=color_ln_bar, edgecolor=color_ln_edge, 
           linewidth=1.5, yerr=stds['LN'], capsize=6,
           error_kw={'elinewidth': 1.5, 'ecolor': '#2E7D32'})

    # 4. Draw Individual Points (Swarm/Strip plot)
    # Parental Points
    sns.stripplot(data=df[df['Group']=='Parental'], x='Group', y='Intensity', 
                  jitter=0.15, size=8, color=color_parental_dots, ax=ax, order=['Parental'])
    
    # LN Points (Need to shift x-coordinate to 1 because we are plotting separately)
    # We use a temporary dataframe with x=1 for LN to overlay correctly
    ln_points_x = np.random.normal(1, 0.08, size=len(ln_values)) # Manual jitter to control spread
    ax.scatter(ln_points_x, ln_values, color=color_ln_dots, s=60, zorder=10, alpha=0.9)

    # 5. Statistical Annotation
    # Line coordinates
    x1, x2 = 0, 1
    y_max = 1.0 * 10**7  # Top of the chart axis
    y_line = 0.95 * 10**7 # Height of the significance line
    y_text = 0.97 * 10**7 # Height of the text
    
    # Draw line
    ax.plot([x1, x2], [y_line, y_line], color='black', lw=1)
    
    # Add Text
    ax.text((x1+x2)*0.5, y_text, r'$P = 5 \times 10^{-10}$', ha='center', va='bottom', fontsize=12)

    # 6. Formatting Axes
    # Y-Axis
    ax.set_ylim(0, 1.05 * 10**7)
    ax.set_ylabel('Glutamate peak intensity', fontsize=12, labelpad=10)
    
    # Custom Y-ticks to match image style (2 x 10^6, etc.)
    yticks = [0, 2e6, 4e6, 6e6, 8e6, 1e7]
    yticklabels = [
        '0', 
        r'$2 \times 10^6$', 
        r'$4 \times 10^6$', 
        r'$6 \times 10^6$', 
        r'$8 \times 10^6$', 
        r'$1 \times 10^7$'
    ]
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticklabels, fontsize=11)
    
    # X-Axis
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Parental', 'LN'], rotation=45, ha='right', fontsize=12)
    ax.set_xlabel('') # No X label needed
    
    # Spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1)

    # 7. Figure Label "e"
    # Positioned in figure coordinates (top left)
    fig.text(0.02, 0.95, 'e', fontsize=20, fontweight='bold')

    # Adjust layout
    plt.tight_layout()
    
    # Save
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    generate_chart(output_file)