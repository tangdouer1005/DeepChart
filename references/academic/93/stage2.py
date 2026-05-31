import sys
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def generate_chart(output_filename):
    # ---------------------------------------------------------
    # 1. Data Preparation
    # ---------------------------------------------------------
    # Data extracted exactly from the provided Source Data table.
    
    # Column: Fig. 1j (Parental)
    parental_data = [
        1, 
        1.000328, 
        1.000005, 
        0.861667, 
        1.003191, 
        1.136075, 
        1
    ]

    # Column: Unnamed: 1 (Lymph node / LN)
    ln_data = [
        0.587407, 0.932256, 0.847907, 0.563434468, 1.054753, 
        1.447167, 1.117306, 0.270697051, 0.731263444, 0.744321601, 
        0.463934401, 0.179749188, 0.782426964, 0.479145444, 0.70873371, 
        1.548417104, 1.414139626, 0.485153079, 1.03000271, 0.782000195, 
        0.492599693, 0.953486003, 0.618357257, 0.371824586, 0.625783402, 
        0.705343274, 0.451463534, 0.33207914, 0.455197984, 0.453811153, 
        0.537530998, 0.160409973, 0.327652464, 0.318659655
    ]

    # Create a DataFrame for plotting
    df = pd.DataFrame({
        'Group': ['Parental'] * len(parental_data) + ['LN'] * len(ln_data),
        'Value': parental_data + ln_data
    })

    # ---------------------------------------------------------
    # 2. Plot Configuration
    # ---------------------------------------------------------
    # Set style to match the scientific publication look (clean, white background)
    sns.set_theme(style="ticks")
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
    
    # Figure size: Tall and narrow aspect ratio
    fig, ax = plt.subplots(figsize=(2.5, 5))

    # Define Colors
    # Parental: Light Gray bar, Black dots
    # LN: Muted Green bar, Dark Green dots
    bar_colors = ['#D9D9D9', '#8FBC8F'] # Light Grey, Sage Green
    point_palette = {'Parental': 'black', 'LN': '#2E7D32'} # Black, Forest Green

    # ---------------------------------------------------------
    # 3. Drawing the Chart
    # ---------------------------------------------------------
    
    # A. Bar Plot (Mean + Standard Deviation)
    # Using errorbar='sd' because the visual spread in the source image matches 
    # the standard deviation of the provided data (approx 0.3-0.4 for LN).
    sns.barplot(
        data=df, 
        x='Group', 
        y='Value', 
        palette=bar_colors,
        errorbar='sd',       # Standard Deviation
        capsize=0.2,         # Width of the error bar caps
        edgecolor='black',   # Black border around bars
        linewidth=1,
        ax=ax,
        zorder=1             # Draw bars behind points
    )

    # B. Strip Plot (Individual Data Points)
    sns.stripplot(
        data=df, 
        x='Group', 
        y='Value', 
        hue='Group', 
        palette=point_palette,
        jitter=0.2,          # Spread points horizontally
        size=6,              # Dot size
        ax=ax,
        zorder=2,            # Draw points on top of bars
        legend=False
    )

    # ---------------------------------------------------------
    # 4. Styling and Annotations
    # ---------------------------------------------------------

    # Axis Labels
    ax.set_ylabel('Relative GPX4 levels', fontsize=14, color='black')
    ax.set_xlabel('') # No X-axis label needed
    
    # X-Tick Labels (Rotated)
    ax.set_xticklabels(['Parental', 'LN'], rotation=45, ha='right', fontsize=14, color='black')
    
    # Y-Axis Ticks
    ax.set_yticks([0, 0.5, 1.0, 1.5])
    ax.tick_params(axis='y', labelsize=12)

    # Remove top and right spines
    sns.despine()

    # Statistical Significance Annotation
    # P value from source data: 2.1922068708e-05 -> 2.2 x 10^-5
    y_max = 1.65 # Height for the line
    y_text = 1.70 # Height for the text
    
    # Draw the horizontal line
    ax.plot([0, 1], [y_max, y_max], color='black', linewidth=1.2)
    
    # Add the P-value text
    ax.text(
        0.5, y_text, 
        r'$P = 2.2 \times 10^{-5}$', 
        ha='center', 
        va='bottom', 
        fontsize=13, 
        color='black'
    )

    # Figure Tag "j"
    # Positioned in the top-left, outside the axes
    ax.text(
        -0.4, 1.08, 
        'j', 
        transform=ax.transAxes, 
        fontsize=24, 
        fontweight='bold', 
        color='black'
    )

    # Adjust layout to prevent clipping of labels/tags
    plt.tight_layout()

    # ---------------------------------------------------------
    # 5. Output
    # ---------------------------------------------------------
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    # Handle command line argument for output filename
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    else:
        output_path = "output.png"
        
    generate_chart(output_path)