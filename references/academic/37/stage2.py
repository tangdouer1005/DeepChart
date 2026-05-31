import matplotlib.pyplot as plt
import numpy as np
import sys

def main():
    # 1. Data Preparation
    # Extracted directly from the provided Markdown tables.
    # Structure: Name, Y-values (CCD), X-values (Crystallite size), Color (approximate hex)
    
    data_points = [
        {
            "name": "LiAsF$_6$",
            "y_raw": [36, 36],
            "x_raw": [2.9, 2.6, 2.6, 2.7],
            "color": "#D32F2F", # Red
            "label_pos": (-10, 20) # Offset for text (x, y)
        },
        {
            "name": "LiPF$_6$",
            "y_raw": [32, 28],
            "x_raw": [3.0, 3.3, 2.8, 3.3],
            "color": "#305496", # Dark Blue
            "label_pos": (15, 15)
        },
        {
            "name": "LiFSI",
            "y_raw": [29, 22],
            "x_raw": [3.2, 3.1, 3.3, 3.0],
            "color": "#F4C63D", # Yellow/Gold
            "label_pos": (-35, -5)
        },
        {
            "name": "LiTFSI",
            "y_raw": [20, 18],
            "x_raw": [3.9, 3.4, 3.0, 3.7],
            "color": "#6AA84F", # Green
            "label_pos": (-40, -15)
        },
        {
            "name": "LiClO$_4$",
            "y_raw": [26, 23],
            "x_raw": [4.1, 4.8, 4.2, 3.8],
            "color": "#674EA7", # Purple
            "label_pos": (-10, 10)
        },
        {
            "name": "LiBF$_4$",
            "y_raw": [21, 17],
            "x_raw": [3.9, 4.1, 5.4, 4.4],
            "color": "#8E8E8E", # Grey
            "label_pos": (-35, -25)
        },
        {
            "name": "LiDFOB",
            "y_raw": [20, 16],
            "x_raw": [4.7, 4.5, 4.9, 5.4],
            "color": "#E06666", # Salmon/Red
            "label_pos": (15, 15)
        },
        {
            "name": "LiNO$_3$",
            "y_raw": [15, 15],
            "x_raw": [5.2, 5.2, 6.2, 5.3],
            "color": "#6D9EEB", # Light Blue
            "label_pos": (10, -15)
        }
    ]

    # 2. Plot Setup
    fig, ax = plt.subplots(figsize=(7, 6))
    
    # Set font styles to match scientific publication
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
    
    # 3. Processing and Plotting
    for point in data_points:
        # Calculate Mean
        x_mean = np.mean(point["x_raw"])
        y_mean = np.mean(point["y_raw"])
        
        # Calculate Standard Deviation for Error Bars
        # Using ddof=1 for sample standard deviation, though ddof=0 is also common in plots.
        # Visual inspection suggests standard deviation is used.
        x_err = np.std(point["x_raw"], ddof=1)
        y_err = np.std(point["y_raw"], ddof=1)
        
        # Plot Error Bars
        # fmt='none' prevents plotting the marker again in the errorbar call
        ax.errorbar(x_mean, y_mean, xerr=x_err, yerr=y_err, 
                    fmt='none', ecolor='black', elinewidth=0.8, capsize=3, capthick=0.8, zorder=1)
        
        # Plot Marker
        ax.scatter(x_mean, y_mean, s=120, marker='s', color=point["color"], zorder=2, edgecolors='none')
        
        # Add Label with Leader Line
        # We use annotate to draw the text and the line pointing to the marker
        ax.annotate(point["name"], 
                    xy=(x_mean, y_mean), 
                    xytext=point["label_pos"], 
                    textcoords='offset points',
                    fontsize=12,
                    color='black',
                    arrowprops=dict(arrowstyle='-', color='black', linewidth=0.8, shrinkA=0, shrinkB=5))

    # 4. Statistical Text
    from scipy import stats
    x_means = [np.mean(p["x_raw"]) for p in data_points]
    y_means = [np.mean(p["y_raw"]) for p in data_points]
    corr, p_value = stats.spearmanr(x_means, y_means)
    
    # Format p-value to LaTeX scientific notation
    exponent = int(np.floor(np.log10(p_value)))
    coeff = p_value / (10**exponent)
    p_text = f"{coeff:.1f} \\times 10^{{{exponent}}}"
    
    stats_text = f"Correlation coefficient: {corr:.2f}\n$P$ value: ${p_text}$"
    ax.text(0.95, 0.8, stats_text, transform=ax.transAxes, ha='right', va='top', fontsize=12)

    # 5. Axis Formatting
    ax.set_xlabel("Crystallite size in SEI (nm)", fontsize=12)
    ax.set_ylabel("$J_{\mathrm{Crit.}}$ (mA cm$^{-2}$)", fontsize=12)
    
    ax.set_xlim(2.0, 6.0)
    ax.set_ylim(10, 40)
    
    # Tick formatting
    ax.tick_params(axis='both', which='major', direction='out', length=6, width=0.8, labelsize=10)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # 6. Figure Label "d"
    # Placed in the top left corner, outside the axes
    fig.text(0.02, 0.92, 'd', fontsize=20, fontweight='bold')

    # Adjust layout
    plt.tight_layout(rect=[0.03, 0, 1, 1])

    # 7. Save Output
    output_filename = "output.png"
    if len(sys.argv) > 1:
        output_filename = sys.argv[1]
        
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')

if __name__ == "__main__":
    main()