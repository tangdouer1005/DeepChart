import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def generate_chart(output_filename="output.png"):
    # 1. Data Preparation
    # We reconstruct the dataframes exactly from the provided source data.
    
    # Part 1: SSL Ratios (from the first section of the source table)
    ssl_data = {
        "Electrolyte": [
            "LiAsF6 electrolyte", "LiPF6 electrolyte", "LiFSI electrolyte", 
            "LiTFSI electrolyte", "LiClO4 electrolyte", "LiBF4 electrolyte", 
            "LiDFOB electrolyte", "LiNO3 electrolyte"
        ],
        "SSL ratio (%)": [
            90, 80, 78.33333, 
            76.66667, 71.66667, 75, 
            70.4918, 68.33333
        ]
    }
    
    # Part 2: Crystallite Size Measurements (from the third section of the source table)
    # Columns: measurement #1, #2, #3, #4
    size_data = {
        "Electrolyte": [
            "LiAsF6 electrolyte", "LiPF6 electrolyte", "LiFSI electrolyte", 
            "LiTFSI electrolyte", "LiClO4 electrolyte", "LiBF4 electrolyte", 
            "LiDFOB electrolyte", "LiNO3 electrolyte"
        ],
        "m1": [2.9, 3.0, 3.2, 3.9, 4.1, 3.9, 4.7, 5.2],
        "m2": [2.6, 3.3, 3.1, 3.4, 4.8, 4.1, 4.5, 5.2],
        "m3": [2.6, 2.8, 3.3, 3.0, 4.2, 5.4, 4.9, 6.2],
        "m4": [2.7, 3.3, 3.0, 3.7, 3.8, 4.4, 5.4, 5.3]
    }

    # Create DataFrames
    df_ssl = pd.DataFrame(ssl_data)
    df_size = pd.DataFrame(size_data)

    # Merge DataFrames
    df = pd.merge(df_ssl, df_size, on="Electrolyte")

    # Clean Electrolyte names (remove " electrolyte" suffix) for labeling
    df["Label"] = df["Electrolyte"].str.replace(" electrolyte", "")

    # Calculate Mean and Standard Deviation for Crystallite Size
    measurements = ["m1", "m2", "m3", "m4"]
    df["Mean_Size"] = df[measurements].mean(axis=1)
    df["Std_Size"] = df[measurements].std(axis=1)

    # 2. Plotting Setup
    # Set style parameters to match the publication look
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
    plt.rcParams['font.size'] = 12
    
    fig, ax = plt.subplots(figsize=(7, 6))

    # Define Colors based on visual inspection of the provided image
    # Mapping labels to approximate hex codes
    colors = {
        "LiNO3": "#6b9ac9",   # Light Blue
        "LiDFOB": "#e67e75",  # Salmon/Red
        "LiClO4": "#666699",  # Purple/Slate
        "LiBF4": "#999999",   # Grey
        "LiTFSI": "#6bc985",  # Green
        "LiFSI": "#f2c65e",   # Yellow/Gold
        "LiPF6": "#4d73a0",   # Dark Blue
        "LiAsF6": "#d64541"   # Red
    }

    # 3. Plotting Data Points
    for _, row in df.iterrows():
        label = row["Label"]
        x = row["SSL ratio (%)"]
        y = row["Mean_Size"]
        yerr = row["Std_Size"]
        color = colors.get(label, "black")

        # Plot Error Bar and Marker
        # fmt='s' means square marker
        ax.errorbar(x, y, yerr=yerr, fmt='s', color=color, 
                    ecolor='black', elinewidth=0.8, capsize=3, 
                    markersize=10, markeredgewidth=0, zorder=5)

        # 4. Annotations (Labels with lines)
        # We manually adjust positions to match the image layout
        xytext_offset = (0, 0)
        ha = 'left'
        va = 'center'
        
        # Specific adjustments per label to replicate the image layout
        if label == "LiNO3":
            xytext_offset = (15, 15) # Top Right
        elif label == "LiDFOB":
            xytext_offset = (15, 15) # Top Right
        elif label == "LiClO4":
            xytext_offset = (-35, 0) # Left
            ha = 'right'
        elif label == "LiBF4":
            xytext_offset = (20, 0)  # Right
        elif label == "LiTFSI":
            xytext_offset = (15, 10) # Top Right
        elif label == "LiFSI":
            xytext_offset = (-10, -20) # Bottom Left
            ha = 'right'
        elif label == "LiPF6":
            xytext_offset = (20, 0)  # Right
        elif label == "LiAsF6":
            xytext_offset = (-15, 0) # Left
            ha = 'right'

        ax.annotate(label, 
                    xy=(x, y), 
                    xytext=xytext_offset, 
                    textcoords='offset points',
                    ha=ha, va=va,
                    fontsize=11,
                    arrowprops=dict(arrowstyle='-', color='black', lw=0.8))

    # 5. Statistical Text
    from scipy import stats
    corr, p_value = stats.spearmanr(df["SSL ratio (%)"], df["Mean_Size"])

    # Format p-value to LaTeX scientific notation
    exponent = int(np.floor(np.log10(p_value)))
    coeff = p_value / (10**exponent)
    p_text = f"{coeff:.1f} \\times 10^{{{exponent}}}"

    stats_text = f"Correlation coefficient: {corr:.2f}\n$P$ value: ${p_text}$"
    ax.text(0.95, 0.75, stats_text, transform=ax.transAxes, 
            ha='right', va='top', fontsize=12)

    # 6. Axis Formatting
    ax.set_xlabel("SSL ratio (%)", fontsize=12, labelpad=10)
    ax.set_ylabel("Crystallite size in SEI (nm)", fontsize=12, labelpad=10)

    # Set Limits
    ax.set_xlim(65, 95)
    ax.set_ylim(2.0, 6.0)

    # Set Ticks
    ax.set_xticks(np.arange(65, 96, 5))
    ax.set_yticks(np.arange(2.0, 6.1, 0.5))

    # Tick styling
    ax.tick_params(axis='both', which='major', length=6, width=0.8, direction='out')
    
    # Remove top and right spines for cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Add 'e' label in top left corner (Figure label)
    ax.text(-0.12, 1.0, 'e', transform=ax.transAxes, 
            fontsize=16, fontweight='bold', va='top', ha='right')

    # 7. Save Output
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    generate_chart(output_file)