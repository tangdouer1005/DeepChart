import sys
import numpy as np
import matplotlib.pyplot as plt

def generate_chart(output_filename):
    # ---------------------------------------------------------
    # 1. Data Preparation
    # ---------------------------------------------------------
    # Data extracted manually from the provided Markdown table (Viability section).
    # Mapping logic based on chart trends:
    # "Acute" corresponds to "Teff" (Blue line, high viability at end)
    # "Chronic" corresponds to "Tex" (Pink line, low viability at end)
    
    days = [0, 2, 4, 6, 8]
    
    # Raw data for Acute (Teff)
    # Columns: Unnamed: 1, Unnamed: 2, Unnamed: 3, Unnamed: 4
    raw_acute = [
        [99, 98, 99, 97],  # Day 0
        [90, 82, 90, 86],  # Day 2
        [84, 75, 75, 83],  # Day 4
        [94, 87, 90, 92],  # Day 6
        [96, 92, 94, 95]   # Day 8
    ]
    
    # Raw data for Chronic (Tex)
    # Columns: Unnamed: 5, Unnamed: 6, Unnamed: 7, Unnamed: 8
    raw_chronic = [
        [99, 98, 99, 97],  # Day 0
        [90, 82, 90, 86],  # Day 2
        [54, 56, 55, 49],  # Day 4
        [62, 60, 50, 50],  # Day 6
        [59, 54, 59, 58]   # Day 8
    ]

    # Calculate Mean and Standard Deviation for plotting
    teff_means = [np.mean(row) for row in raw_acute]
    teff_stds = [np.std(row, ddof=1) for row in raw_acute] # Using sample SD
    
    tex_means = [np.mean(row) for row in raw_chronic]
    tex_stds = [np.std(row, ddof=1) for row in raw_chronic]

    # ---------------------------------------------------------
    # 2. Plotting Setup
    # ---------------------------------------------------------
    # Colors estimated from the image
    color_teff = '#7793A8'  # Muted Blue-Grey
    color_tex = '#D59CA0'   # Muted Pink/Rose
    
    fig, ax = plt.subplots(figsize=(5, 4.5), dpi=150)

    # ---------------------------------------------------------
    # 3. Draw Lines and Error Bars
    # ---------------------------------------------------------
    # Teff (Acute)
    ax.errorbar(days, teff_means, yerr=teff_stds, 
                label='Teff',
                color=color_teff,
                fmt='-o',           # Line with circle markers
                linewidth=2, 
                markersize=7,
                capsize=4,          # Width of error bar caps
                elinewidth=1.5,
                capthick=1.5)

    # Tex (Chronic)
    ax.errorbar(days, tex_means, yerr=tex_stds, 
                label='Tex',
                color=color_tex,
                fmt='-s',           # Line with square markers
                linewidth=2, 
                markersize=7,
                capsize=4,
                elinewidth=1.5,
                capthick=1.5)

    # ---------------------------------------------------------
    # 4. Styling and Formatting
    # ---------------------------------------------------------
    # Axis Limits and Ticks
    ax.set_ylim(0, 120)
    ax.set_yticks([0, 40, 80, 120])
    
    ax.set_xlim(-0.5, 10.5)
    ax.set_xticks([0, 2, 4, 6, 8, 10])

    # Labels and Title
    ax.set_ylabel('live cells (%)', fontsize=14, color='black')
    ax.set_xlabel('Days', fontsize=14, color='black')
    ax.set_title('Viability', fontsize=16, pad=15, color='black')

    # Tick styling
    ax.tick_params(axis='both', which='major', labelsize=12, width=1.5, length=5, direction='out')

    # Spines (Borders) - Remove top and right to match "Prism" style
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)

    # Legend
    # Frameon=False removes the box around the legend
    ax.legend(loc='upper right', frameon=False, fontsize=12, handletextpad=0.5)

    # ---------------------------------------------------------
    # 5. Statistical Annotation
    # ---------------------------------------------------------
    # Coordinates for the bracket at Day 8
    x_pos = 8.5
    y_top = teff_means[-1]
    y_bottom = tex_means[-1]
    bracket_width = 0.5
    
    # Draw the bracket lines
    # Top horizontal, Vertical, Bottom horizontal
    ax.plot([x_pos, x_pos + bracket_width, x_pos + bracket_width, x_pos], 
            [y_top, y_top, y_bottom, y_bottom], 
            color='black', lw=1)

    # Add P-value text
    # Using LaTeX formatting for the scientific notation
    from scipy import stats
    # Day 8 data is at index 4
    _, p_val = stats.ttest_ind(raw_acute[4], raw_chronic[4])
    
    exponent = int(np.floor(np.log10(p_val)))
    coeff = p_val / (10**exponent)
    p_value_text = f"P = {coeff:.2f} $\\times$ 10$^{{{exponent}}}$"
    
    ax.text(x_pos + bracket_width + 0.5, (y_top + y_bottom) / 2, 
            p_value_text, 
            ha='left', va='center', fontsize=12, color='black')

    # ---------------------------------------------------------
    # 6. Save Output
    # ---------------------------------------------------------
    plt.tight_layout()
    plt.savefig(output_filename, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    # Handle command line argument for output filename
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    else:
        output_path = "output.png"
        
    generate_chart(output_path)