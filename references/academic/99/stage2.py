import matplotlib.pyplot as plt
import numpy as np
import sys

def generate_chart(output_filename='output.png'):
    # ---------------------------------------------------------
    # 1. Source Data Extraction
    # ---------------------------------------------------------
    # Data extracted directly from the provided Markdown table.
    # Row: "Glutathione"
    # Group 1: "Parental" (Columns F0luc-1 to F0luc-3)
    # Group 2: "LN" (Columns LN7... to LN9...)
    
    parental_data = [
        455236.17862429336, 
        374854.50703331234, 
        500874.4223320226, 
        466937.56824526587, 
        526218.035058101
    ]

    ln_data = [
        # LN7 1112AR
        7253.489863424753, 17490.643208638903, 207263.77376446282,
        # LN7 1120BL
        100374.46817310246, 150631.5739676901, 224441.8038986802,
        # LN7 1134BL
        129019.30608176917, 88956.35533622571, 233707.8500794956,
        # LN8 1194BR
        131170.17823033908, 133441.93648697663, 123497.4118948018,
        # LN8 1198AR
        229925.4941502907, 187742.7464008859, 177946.0039862014,
        # LN8 1205BL
        162259.7645429363, 155074.21131701427, 153575.2223311653,
        # LN9 1315BL
        284545.9510167087, 240852.638916042, 222731.42120165497,
        # LN9 1358IR
        215774.5807455938, 206790.9561720754, 196147.94800028956
    ]

    # ---------------------------------------------------------
    # 2. Calculations
    # ---------------------------------------------------------
    means = [np.mean(parental_data), np.mean(ln_data)]
    stds = [np.std(parental_data, ddof=1), np.std(ln_data, ddof=1)]
    
    # ---------------------------------------------------------
    # 3. Plotting Setup
    # ---------------------------------------------------------
    # Figure size to match the portrait aspect ratio of the original image
    fig, ax = plt.subplots(figsize=(3.5, 5.5))
    
    # Styling constants
    bar_width = 0.5
    x_positions = [0, 1]
    
    # Colors based on visual inspection
    color_parental_bar = '#D9D9D9'  # Light gray
    color_parental_edge = '#808080' # Darker gray edge
    color_parental_dots = '#000000' # Black
    
    color_ln_bar = '#A9D18E'        # Muted light green
    color_ln_edge = '#548235'       # Darker green edge
    color_ln_dots = '#2E7D32'       # Dark green dots
    
    # ---------------------------------------------------------
    # 4. Draw Bars and Error Bars
    # ---------------------------------------------------------
    # Bar 1: Parental
    ax.bar(x_positions[0], means[0], width=bar_width, 
           color=color_parental_bar, edgecolor=color_parental_edge, 
           linewidth=1, zorder=1)
    
    # Bar 2: LN
    ax.bar(x_positions[1], means[1], width=bar_width, 
           color=color_ln_bar, edgecolor=color_ln_edge, 
           linewidth=1, zorder=1)
    
    # Error bars (Standard Deviation)
    ax.errorbar(x_positions, means, yerr=stds, fmt='none', 
                ecolor='gray', elinewidth=1.5, capsize=6, zorder=2)

    # ---------------------------------------------------------
    # 5. Draw Scatter Points (Jittered)
    # ---------------------------------------------------------
    np.random.seed(42) # For reproducibility of jitter
    
    # Jitter function
    def jitter(x, width, n):
        return np.random.uniform(x - width/3.5, x + width/3.5, n)

    # Parental Points
    ax.scatter(jitter(x_positions[0], bar_width, len(parental_data)), parental_data, 
               color=color_parental_dots, s=40, edgecolor='none', zorder=3, alpha=0.9)
    
    # LN Points
    ax.scatter(jitter(x_positions[1], bar_width, len(ln_data)), ln_data, 
               color=color_ln_dots, s=40, edgecolor='none', zorder=3, alpha=0.9)

    # ---------------------------------------------------------
    # 6. Statistical Annotation
    # ---------------------------------------------------------
    # P-value from source data: 2.88e-05 -> 2.9 x 10^-5
    p_value_text = r'$P = 2.9 \times 10^{-5}$'
    
    # Line coordinates
    line_y = 750000  # Height for the significance line
    line_h = 10000   # Tick height for the line ends (optional, flat line in image)
    
    ax.plot([0, 1], [line_y, line_y], color='black', linewidth=1)
    ax.text(0.5, line_y + 15000, p_value_text, ha='center', va='bottom', fontsize=12)

    # ---------------------------------------------------------
    # 7. Axis Formatting
    # ---------------------------------------------------------
    # Y-Axis
    ax.set_ylim(0, 850000)
    yticks = [0, 200000, 400000, 600000, 800000]
    ytick_labels = [r'$0$', r'$2 \times 10^5$', r'$4 \times 10^5$', r'$6 \times 10^5$', r'$8 \times 10^5$']
    ax.set_yticks(yticks)
    ax.set_yticklabels(ytick_labels, fontsize=12)
    ax.set_ylabel('GSH peak intensity', fontsize=13, labelpad=10)
    
    # X-Axis
    ax.set_xticks(x_positions)
    ax.set_xticklabels(['Parental', 'LN'], rotation=45, ha='right', fontsize=13)
    
    # Spines (Remove top and right)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1)

    # ---------------------------------------------------------
    # 8. Figure Label
    # ---------------------------------------------------------
    # Add the bold 'g' in the top left corner
    ax.text(-0.3, 1.05, 'g', transform=ax.transAxes, 
            fontsize=24, fontweight='bold', va='top', ha='left')

    # ---------------------------------------------------------
    # 9. Save Output
    # ---------------------------------------------------------
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)