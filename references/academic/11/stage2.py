import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

def generate_chart(output_filename):
    # 1. Source Data
    # The data is provided as a markdown table string.
    csv_data = """K5 | DCK5 | K10 | DCK10
2.02859 | 7.2504 | 5.40501 | 9.87058
0.878401 | 3.31785 | 2.23115 | 8.92622
0.98349 | 7.06946 | 6.34756 | 7.82007
0.785771 | 7.76414 | 2.56239 | 8.22059
0.388214 | 4.70172 | 4.55303 | 10.6351
2.19805 | 6.59061 | 5.07432 | 6.57444
1.57333 | 7.09779 | 4.39348 | 11.0517
1.50217 | 6.17586 | 4.89635 | nan
3.44616 | nan | 3.20176 | nan
nan | nan | 3.7647 | nan
nan | nan | 3.76893 | nan
nan | nan | 3.87353 | nan"""
    
    # Load data
    # Use regex separator to handle spaces around pipes and ensure correct parsing
    # engine='python' is required for regex separators
    df = pd.read_csv(io.StringIO(csv_data), sep=r"\s*\|\s*", engine='python')
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    # Convert all columns to numeric, coercing errors to NaN (handles 'nan' strings and whitespace)
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Prepare data for plotting (remove NaNs)
    plot_data = [
        df['K5'].dropna().values,
        df['DCK5'].dropna().values,
        df['K10'].dropna().values,
        df['DCK10'].dropna().values
    ]
    
    # 2. Plot Setup
    fig, ax = plt.subplots(figsize=(4, 5))
    
    # Positions: Group 1 (1, 2), Group 2 (4, 5)
    positions = [1, 2, 4, 5]
    
    # Colors
    # K5: Light Red/Pink, DCK5: Teal
    # K10: Dark Red, DCK10: Dark Blue
    colors = ['#E08E8E', '#4D8596', '#992626', '#1A5276']
    
    # 3. Create Boxplot
    bplot = ax.boxplot(plot_data, 
                       positions=positions, 
                       widths=0.6, 
                       patch_artist=True,
                       showfliers=False,
                       boxprops=dict(linewidth=1.5),
                       whiskerprops=dict(linewidth=1.5),
                       capprops=dict(linewidth=1.5),
                       medianprops=dict(linewidth=1.5))
    
    # 4. Style Boxplot
    for i, patch in enumerate(bplot['boxes']):
        color = colors[i]
        patch.set_facecolor('white')
        patch.set_edgecolor(color)
        
        # Style whiskers, caps, medians
        bplot['whiskers'][i*2].set_color(color)
        bplot['whiskers'][i*2+1].set_color(color)
        bplot['caps'][i*2].set_color(color)
        bplot['caps'][i*2+1].set_color(color)
        bplot['medians'][i].set_color(color)

    # 5. Axes Styling
    ax.set_ylabel('AUC normalized', fontsize=12, color='black')
    ax.set_ylim(0, 13)
    ax.set_yticks([0, 4, 8, 12])
    
    # X-axis
    ax.set_xlim(0, 6)
    ax.set_xticks(positions)
    ax.set_xticklabels(['Ketamine', 'DCK', 'Ketamine', 'DCK'], 
                       rotation=45, ha='right', fontsize=12)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Dashed separator line
    ax.vlines(x=3, ymin=0, ymax=12, colors='black', linestyles='dashed', linewidth=1)
    
    # 6. Annotations (Significance)
    def add_significance_bar(x1, x2, y, text):
        ax.plot([x1, x2], [y, y], color='black', linewidth=0.8)
        ax.text((x1+x2)/2, y, text, ha='center', va='bottom', fontsize=12)

    # Left group
    t_stat_left, p_val_left = stats.ttest_ind(plot_data[0], plot_data[1])
    if p_val_left < 0.001:
        sig_text_left = '***'
    elif p_val_left < 0.01:
        sig_text_left = '**'
    elif p_val_left < 0.05:
        sig_text_left = '*'
    else:
        sig_text_left = 'ns'
    add_significance_bar(1, 2, 9.2, sig_text_left)

    # Right group
    t_stat_right, p_val_right = stats.ttest_ind(plot_data[2], plot_data[3])
    if p_val_right < 0.001:
        sig_text_right = '***'
    elif p_val_right < 0.01:
        sig_text_right = '**'
    elif p_val_right < 0.05:
        sig_text_right = '*'
    else:
        sig_text_right = 'ns'
    add_significance_bar(4, 5, 11.8, sig_text_right)
    
    # 7. Dosage Labels (Manual drawing below x-axis)
    # Coordinates are in data units. Negative y puts it below the axis.
    line_y = -2.5
    text_y = -3.0
    
    # Group 1 Line
    ax.plot([0.8, 2.2], [line_y, line_y], color='black', linewidth=1, clip_on=False)
    ax.text(1.5, text_y, '5 mg kg$^{-1}$', ha='center', va='top', fontsize=12, clip_on=False)
    
    # Group 2 Line
    ax.plot([3.8, 5.2], [line_y, line_y], color='black', linewidth=1, clip_on=False)
    ax.text(4.5, text_y, '10 mg kg$^{-1}$', ha='center', va='top', fontsize=12, clip_on=False)
    
    # Figure Label 'd'
    ax.text(-0.2, 1.0, 'd', transform=ax.transAxes, fontsize=16, fontweight='bold', va='top', ha='right')

    # Adjust layout
    plt.tight_layout()
    # Add extra bottom margin for the manual labels
    plt.subplots_adjust(bottom=0.3)
    
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    generate_chart(output_file)