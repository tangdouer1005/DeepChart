import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def main():
    # 1. Handle Output Filename
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]

    # 2. Prepare Data
    # Data transcribed exactly from the provided Source Data table.
    # NaN values are omitted from the lists.
    raw_data = {
        "B16-F0": [
            0.94, 1.00, 1.06, 0.98, 1.05, 1.11, 1.01, 0.96, 1.04, 0.99, 
            0.97, 1.04, 0.93, 0.96, 1.12, 0.94, 0.99, 1.07, 1.01, 0.93, 
            1.06, 1.10, 0.89, 1.00, 1.04, 0.93, 1.03, 1.00, 1.00, 1.00
        ],
        "LN1-18IL": [
            0.90, 1.07, 0.97, 0.94, 1.12, 1.01, 0.82, 0.90, 0.89, 1.08, 
            1.12, 1.05, 1.07, 1.24, 1.01, 1.07, 1.11, 1.24, 0.60, 0.66, 
            0.60, 0.53, 0.66, 0.62, 0.56, 0.67, 0.59, 0.66, 1.20, 1.02
        ],
        "LN7-1112AR": [
            0.32, 0.31, 0.39, 0.31, 0.34, 0.41, 0.33, 0.55, 0.32
        ],
        "LN7-1120BL": [
            0.43, 0.42, 0.45, 0.29, 0.42, 0.43, 0.35, 0.68, 0.45
        ],
        "LN7-1134BL": [
            0.34, 0.32, 0.41, 0.45, 0.49, 0.45, 0.33, 0.76, 0.44
        ],
        "LN8-1194BR": [
            0.40, 0.35, 0.43, 0.35, 0.34, 0.35, 0.44, 0.45, 0.36, 0.31, 0.46, 0.27
        ],
        "LN8-1198AR": [
            0.54, 0.51, 0.50, 0.43, 0.46, 0.44, 0.48, 0.48, 0.45, 0.38, 0.57, 0.37
        ],
        "LN8-1205BL": [
            0.45, 0.44, 0.47, 0.33, 0.35, 0.30, 0.39, 0.35, 0.35, 0.25, 0.49, 0.28
        ],
        "LN9-1315BL": [
            0.40, 0.48, 0.46, 0.30, 0.43, 0.34
        ],
        "LN9-1358IR": [
            0.70, 0.42, 0.54, 0.40, 0.69, 0.39
        ]
    }

    # P-values from the "Statistical test" columns in Source Data
    # Note: The chart uses scientific notation.
    p_values = {
        "LN7-1112AR": r"$P = 4 \times 10^{-15}$",
        "LN7-1120BL": r"$P = 4 \times 10^{-15}$",
        "LN7-1134BL": r"$P = 4 \times 10^{-15}$",
        "LN8-1194BR": r"$P = 4 \times 10^{-15}$",
        "LN8-1198AR": r"$P = 4 \times 10^{-15}$",
        "LN8-1205BL": r"$P = 4 \times 10^{-15}$",
        "LN9-1315BL": r"$P = 4 \times 10^{-15}$",
        "LN9-1358IR": r"$P = 1.8 \times 10^{-12}$"
    }

    # Convert to DataFrame for plotting
    # We create a list of records to handle unequal lengths
    plot_data = []
    for group, values in raw_data.items():
        for v in values:
            plot_data.append({'Group': group, 'Value': v})
    
    df = pd.DataFrame(plot_data)

    # Calculate Means and SD for bar plot
    summary = df.groupby('Group', sort=False)['Value'].agg(['mean', 'std']).reset_index()

    # 3. Setup Plot
    fig, ax = plt.subplots(figsize=(7, 6))
    
    # Define Colors
    # B16-F0: Light Gray, LN1-18IL: Light Purple, Others: Green
    bar_colors = ['#d9d9d9', '#eeb7e6'] + ['#8cc685'] * 8
    edge_colors = ['#4d4d4d', '#4d4d4d'] + ['#2e6b2e'] * 8 # Darker outlines
    
    # 4. Draw Bar Plot (Means with SD error bars)
    # We iterate to set individual colors easily
    groups = summary['Group'].tolist()
    x_pos = np.arange(len(groups))
    
    bars = ax.bar(x_pos, summary['mean'], yerr=summary['std'], 
                  color=bar_colors, edgecolor=edge_colors, 
                  linewidth=1.5, capsize=4, width=0.6, 
                  error_kw={'elinewidth': 1.5, 'ecolor': '#333333'})

    # 5. Draw Strip Plot (Individual Points)
    # We need custom colors for points: Black for first two, Dark Green for rest
    
    # Create a custom palette for seaborn stripplot
    point_palette = {'B16-F0': 'black', 'LN1-18IL': 'black'}
    for g in groups[2:]:
        point_palette[g] = '#2e6b2e' # Dark green

    sns.stripplot(data=df, x='Group', y='Value', hue='Group', palette=point_palette,
                  jitter=True, size=5, ax=ax, legend=False, alpha=0.9, zorder=3)

    # 6. Annotations
    
    # A. Vertical P-values
    # The text is rotated 90 degrees and aligned to the top area
    # Based on the image, the text tops are roughly aligned.
    text_y_anchor = 1.95 
    
    for i, group in enumerate(groups):
        if group in p_values:
            ax.text(i, text_y_anchor, p_values[group], 
                    rotation=90, ha='center', va='top', fontsize=9, color='black')

    # B. Top Statistical Bracket and Label
    # Line spans from index 2 (LN7-1112AR) to index 9 (LN9-1358IR)
    line_start = 2
    line_end = 9
    line_y = 2.05
    
    # Draw the horizontal line
    ax.plot([line_start, line_end], [line_y, line_y], color='black', linewidth=0.8, clip_on=False)
    
    # Add the text above the line
    ax.text((line_start + line_end) / 2, line_y + 0.05, r"$P < 1 \times 10^{-15}$", 
            ha='center', va='bottom', fontsize=12, color='black')

    # 7. Formatting
    
    # Axis Labels
    ax.set_ylabel("Relative GCLC levels", fontsize=12, color='black')
    ax.set_xlabel("") # No X label needed as ticks explain it
    
    # X Ticks
    ax.set_xticks(x_pos)
    ax.set_xticklabels(groups, rotation=45, ha='right', rotation_mode='anchor', fontsize=12)
    
    # Y Ticks and Limits
    ax.set_ylim(0, 2.0)
    ax.set_yticks([0, 0.5, 1.0, 1.5, 2.0])
    ax.tick_params(axis='y', labelsize=11)
    
    # Spines (Remove top and right)
    sns.despine()
    
    # Add Figure Label "e"
    # Positioned in the top left, outside the axes
    fig.text(0.02, 0.95, "e", fontsize=20, fontweight='bold', va='top')

    # Adjust layout to prevent clipping of rotated labels
    plt.tight_layout()
    
    # Adjust top margin manually to make room for the "e" and the top annotation
    plt.subplots_adjust(top=0.85, left=0.15, bottom=0.25)

    # 8. Save Output
    plt.savefig(output_file, dpi=300)
    print(f"Chart saved to {output_file}")

if __name__ == "__main__":
    main()