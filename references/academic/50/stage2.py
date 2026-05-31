import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys

def main():
    # Handle output filename
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]

    # ---------------------------------------------------------
    # 1. Data Preparation
    # ---------------------------------------------------------
    # Raw data extracted from the provided Markdown table (Proliferation section)
    # Acute = Teff, Chronic = Tex
    
    days = np.array([0, 2, 4, 6, 8])
    
    # Acute (Teff) raw data columns
    acute_data = np.array([
        [1, 1, 1, 1],           # Day 0
        [1.34, 1.09, 1.4, 1],   # Day 2
        [8.64, 5.16, 7.21, 5.45], # Day 4
        [26.8, 17.3, 19.3, 20.6], # Day 6
        [97.8, 70, 91.7, 74]      # Day 8
    ])
    
    # Chronic (Tex) raw data columns
    chronic_data = np.array([
        [1, 1, 1, 1],           # Day 0
        [1.34, 1.09, 1.4, 1],   # Day 2
        [2.48, 2.47, 2.16, 2.1],  # Day 4
        [6.12, 5.8, 4.61, 4.62],  # Day 6
        [11.9, 11.7, 12.3, 13.5]  # Day 8
    ])

    # Calculate Mean and Standard Deviation
    # Using ddof=1 for sample standard deviation, which visually matches the error bars in the source image
    teff_mean = np.mean(acute_data, axis=1)
    teff_std = np.std(acute_data, axis=1, ddof=1)
    
    tex_mean = np.mean(chronic_data, axis=1)
    tex_std = np.std(chronic_data, axis=1, ddof=1)

    # ---------------------------------------------------------
    # 2. Plotting
    # ---------------------------------------------------------
    # Set up the figure size and resolution
    fig, ax = plt.subplots(figsize=(5, 4.5), dpi=150)

    # Define colors based on the image
    color_teff = '#7f9eb2'  # Muted blue-grey
    color_tex = '#dcb0b3'   # Muted pink-red

    # Plot Teff (Acute)
    ax.errorbar(days, teff_mean, yerr=teff_std, 
                fmt='-o',                 # Line with circle markers
                color=color_teff, 
                ecolor=color_teff,        # Error bar color
                capsize=4,                # Width of error bar caps
                linewidth=1.5, 
                markersize=6, 
                label='Teff')

    # Plot Tex (Chronic)
    ax.errorbar(days, tex_mean, yerr=tex_std, 
                fmt='-s',                 # Line with square markers
                color=color_tex, 
                ecolor=color_tex, 
                capsize=4, 
                linewidth=1.5, 
                markersize=6, 
                label='Tex')

    # ---------------------------------------------------------
    # 3. Styling and Formatting
    # ---------------------------------------------------------
    
    # Axis Limits and Ticks
    ax.set_xlim(-0.5, 10.5)
    ax.set_ylim(0, 100)
    
    ax.set_xticks([0, 2, 4, 6, 8, 10])
    ax.set_yticks([0, 25, 50, 75, 100])

    # Labels and Title
    # Using Arial-like font properties
    font_dict = {'family': 'sans-serif', 'size': 14, 'color': 'black'}
    
    ax.set_xlabel("Days", fontdict=font_dict, labelpad=8)
    ax.set_ylabel(r"Cell Number ($\times 10^6$)", fontdict=font_dict, labelpad=8)
    ax.set_title("Proliferation", fontsize=16, pad=15, color='black')

    # Legend
    # Frameon=False removes the box around the legend
    legend = ax.legend(loc='upper right', frameon=False, fontsize=12, handletextpad=0.5)
    
    # Spines (Borders)
    # Remove Top and Right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Make Left and Bottom spines thicker/blacker if needed (default is usually fine, but ensuring visibility)
    ax.spines['left'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1)
    ax.spines['left'].set_color('black')
    ax.spines['bottom'].set_color('black')
    
    # Tick parameters
    ax.tick_params(axis='both', which='major', labelsize=12, width=1, length=5, color='black')

    # ---------------------------------------------------------
    # 4. Statistical Annotation (Bracket and P-value)
    # ---------------------------------------------------------
    # Coordinates for the bracket at Day 8
    # Top of bracket aligns with Teff mean at Day 8
    # Bottom of bracket aligns with Tex mean at Day 8
    y_top = teff_mean[-1]
    y_bottom = tex_mean[-1]
    
    # X position for the bracket (to the right of the data points)
    x_bracket = 9.0
    bracket_width = 0.2  # Length of the horizontal tips of the bracket
    
    # Draw the bracket line
    # Shape is: [Top Tip] -- [Vertical Line] -- [Bottom Tip]
    ax.plot([x_bracket - bracket_width, x_bracket, x_bracket, x_bracket - bracket_width], 
            [y_top, y_top, y_bottom, y_bottom], 
            color='black', linewidth=1)

    # Add P-value text
    # Centered vertically relative to the bracket, placed to the right
    from scipy import stats
    # Using Student's t-test (equal variance) as requested
    _, p_val = stats.ttest_ind(acute_data[-1], chronic_data[-1], equal_var=True)
    
    exponent = int(np.floor(np.log10(p_val)))
    coeff = p_val / (10**exponent)
    p_value_text = f"P = {coeff:.2f} $\\times$ 10$^{{{exponent}}}$"
    
    ax.text(x_bracket + 0.3, (y_top + y_bottom) / 2, p_value_text, 
            ha='left', va='center', fontsize=12, color='black')

    # ---------------------------------------------------------
    # 5. Save Output
    # ---------------------------------------------------------
    plt.tight_layout()
    plt.savefig(output_file, bbox_inches='tight')
    print(f"Chart saved to {output_file}")

if __name__ == "__main__":
    main()