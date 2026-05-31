import matplotlib.pyplot as plt
import numpy as np
import sys

def generate_chart(output_filename):
    """
    Generates a bar chart reproducing Fig. 2f using the provided source data.
    """
    # Set seed for reproducibility of the scatter jitter
    np.random.seed(42)

    # Data extracted directly from the provided Source Data table.
    # Row: 'Glutathione'
    # Columns mapped to groups based on headers (e.g., F0luc -> B16-F0)
    data = {
        "B16-F0":     [455236.1786, 374854.507, 500874.4223],
        "LN1-18IL":   [259322.4689, 325788.1275, 369825.6449],
        "LN7-1112AR": [7253.489863, 17490.64321, 207263.7738],
        "LN7-1120BL": [100374.4682, 150631.574, 224441.8039],
        "LN7-1134BL": [129019.3061, 88956.35534, 233707.8501],
        "LN8-1194BR": [131170.1782, 133441.9365, 123497.4119],
        "LN8-1198AR": [229925.4942, 187742.7464, 177946.004],
        "LN8-1205BL": [162259.7645, 155074.2113, 153575.2223],
        "LN9-1315BL": [284545.951, 240852.6389, 222731.4212],
        "LN9-1358IR": [215774.5807, 206790.9562, 196147.948]
    }

    # P-values extracted from the 'Adjusted P Value' column in the Fig. 2f section of the table.
    # Formatted as LaTeX strings for the plot.
    p_values_text = {
        "LN7-1112AR": r"$P = 1.2 \times 10^{-7}$",
        "LN7-1120BL": r"$P = 6.9 \times 10^{-6}$",
        "LN7-1134BL": r"$P = 4.6 \times 10^{-6}$",
        "LN8-1194BR": r"$P = 1.6 \times 10^{-6}$",
        "LN8-1198AR": r"$P = 5.8 \times 10^{-5}$",
        "LN8-1205BL": r"$P = 6.4 \times 10^{-6}$",
        "LN9-1315BL": r"$P = 0.0009$",
        "LN9-1358IR": r"$P = 8.8 \times 10^{-5}$"
    }

    labels = list(data.keys())
    means = [np.mean(v) for v in data.values()]
    # Using sample standard deviation (ddof=1) for error bars
    stds = [np.std(v, ddof=1) for v in data.values()]

    # Define colors based on the chart image
    # B16-F0: Light Grey
    # LN1-18IL: Light Pink/Magenta
    # Others: Muted Green
    colors = ['#D9D9D9', '#F0A0F0'] + ['#8FBC8F'] * 8

    # Initialize Figure
    fig, ax = plt.subplots(figsize=(10, 6))

    # 1. Plot Bars
    x_pos = np.arange(len(labels))
    ax.bar(x_pos, means, yerr=stds, align='center', alpha=1.0, 
           color=colors, edgecolor='black', linewidth=1, width=0.65,
           capsize=5, error_kw={'ecolor': 'gray', 'elinewidth': 1.5})

    # 2. Plot Individual Data Points (Scatter)
    for i, (label, values) in enumerate(data.items()):
        # Add random jitter to x-coordinates to prevent overlap
        jitter = np.random.uniform(-0.15, 0.15, size=len(values))
        ax.scatter(x_pos[i] + jitter, values, color='black', s=35, zorder=10, alpha=0.8, edgecolors='none')

    # 3. Add Vertical P-value Annotations
    for i, label in enumerate(labels):
        if label in p_values_text:
            text = p_values_text[label]
            
            # Calculate Y position: ensure text starts above the error bar or highest point
            max_val = max(data[label])
            error_top = means[i] + stds[i]
            y_start = max(max_val, error_top) + 25000
            
            # Visual adjustment: align the start of the text for lower bars to a minimum height
            # to match the visual style of the original image
            if y_start < 280000:
                y_start = 280000
            
            ax.text(x_pos[i], y_start, text, rotation=90, ha='center', va='bottom', fontsize=10)

    # 4. Add Main P-value Annotation (Top Line)
    # Extracted from 'P value' row for Fig 2f: 7.64e-08
    line_y = 620000
    ax.plot([x_pos[0], x_pos[-1]], [line_y, line_y], color='black', linewidth=1)
    ax.text((x_pos[0] + x_pos[-1])/2, line_y + 10000, r"$P = 7.6 \times 10^{-8}$", 
            ha='center', va='bottom', fontsize=12)

    # 5. Formatting Axes
    ax.set_ylabel('GSH peak intensity', fontsize=12)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=11)
    
    # Custom Y-ticks to match scientific notation in image
    ax.set_yticks([0, 200000, 400000, 600000])
    ax.set_yticklabels(['0', r'$2 \times 10^5$', r'$4 \times 10^5$', r'$6 \times 10^5$'], fontsize=11)
    
    # Set Y-limit to accommodate the top annotation
    ax.set_ylim(0, 700000)

    # Remove top and right spines for scientific style
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # Add Figure Label 'f'
    ax.text(-0.12, 1.0, 'f', transform=ax.transAxes, fontsize=20, fontweight='bold', va='top', ha='right')

    # Save output
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300)

if __name__ == "__main__":
    # Handle command line argument for output filename
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)