import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def generate_chart(output_filename):
    # ---------------------------------------------------------
    # 1. Data Preparation
    # ---------------------------------------------------------
    # Based on the provided Source Data tables.
    # X-axis: "Thickness of deposited Li (μm)" from the first table.
    # Y-axis: Calculated Mean from "Average crystallite size measurement" (Section 3).
    # Error Bars: Calculated Standard Deviation from the measurements.
    
    data = {
        'Electrolyte': [
            'LiAsF6', 'LiPF6', 'LiFSI', 'LiTFSI', 
            'LiClO4', 'LiBF4', 'LiDFOB', 'LiNO3'
        ],
        # Extracted from Table 1: Thickness of deposited Li (μm)
        'Thickness_Li_um': [
            11.7, 12.3, 14.2, 15.8, 
            15.8, 16.1, 14.9, 17.0
        ],
        # Extracted from Table 3: Measurements #1, #2, #3, #4
        'Measurements': [
            [2.9, 2.6, 2.6, 2.7],   # LiAsF6
            [3.0, 3.3, 2.8, 3.3],   # LiPF6
            [3.2, 3.1, 3.3, 3.0],   # LiFSI
            [3.9, 3.4, 3.0, 3.7],   # LiTFSI
            [4.1, 4.8, 4.2, 3.8],   # LiClO4
            [3.9, 4.1, 5.4, 4.4],   # LiBF4
            [4.7, 4.5, 4.9, 5.4],   # LiDFOB
            [5.2, 5.2, 6.2, 5.3]    # LiNO3
        ]
    }

    df = pd.DataFrame(data)
    
    # Calculate Mean and Std Dev for Y-axis
    df['Crystallite_Mean'] = df['Measurements'].apply(np.mean)
    df['Crystallite_Std'] = df['Measurements'].apply(np.std) # Using population std or sample std? Usually sample (ddof=1) for error bars, but numpy default is 0. Let's use ddof=1 for sample.
    df['Crystallite_Std'] = df['Measurements'].apply(lambda x: np.std(x, ddof=1))

    # ---------------------------------------------------------
    # 2. Plotting Setup
    # ---------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 7))
    
    # Define Colors (approximated from the image)
    colors = {
        'LiAsF6': '#d62728',   # Red
        'LiPF6': '#3b5b92',    # Dark Blue
        'LiFSI': '#eecb5f',    # Yellow/Gold
        'LiTFSI': '#74c476',   # Light Green
        'LiClO4': '#756bb1',   # Purple
        'LiBF4': '#969696',    # Grey
        'LiDFOB': '#ef8a84',   # Salmon/Pink
        'LiNO3': '#6baed6'     # Light Blue
    }

    # Define Label Offsets (dx, dy) to match the visual placement in the image
    # These are manual adjustments to replicate the "look"
    label_configs = {
        'LiAsF6': {'xytext': (-35, 0), 'ha': 'right', 'va': 'center'},
        'LiPF6':  {'xytext': (-35, 10), 'ha': 'right', 'va': 'bottom'},
        'LiFSI':  {'xytext': (-35, 0), 'ha': 'right', 'va': 'center'},
        'LiTFSI': {'xytext': (-35, 0), 'ha': 'right', 'va': 'center'},
        'LiClO4': {'xytext': (-35, 0), 'ha': 'right', 'va': 'center'},
        'LiBF4':  {'xytext': (35, 0), 'ha': 'left', 'va': 'center'},
        'LiDFOB': {'xytext': (-35, 0), 'ha': 'right', 'va': 'center'},
        'LiNO3':  {'xytext': (-35, 15), 'ha': 'right', 'va': 'bottom'}
    }

    # Formatted Labels (LaTeX style for subscripts)
    formatted_names = {
        'LiAsF6': r'LiAsF$_6$',
        'LiPF6': r'LiPF$_6$',
        'LiFSI': r'LiFSI',
        'LiTFSI': r'LiTFSI',
        'LiClO4': r'LiClO$_4$',
        'LiBF4': r'LiBF$_4$',
        'LiDFOB': r'LiDFOB',
        'LiNO3': r'LiNO$_3$'
    }

    # ---------------------------------------------------------
    # 3. Plotting Loop
    # ---------------------------------------------------------
    for _, row in df.iterrows():
        name = row['Electrolyte']
        x = row['Thickness_Li_um']
        y = row['Crystallite_Mean']
        y_err = row['Crystallite_Std']
        color = colors.get(name, 'black')
        
        # Plot Error Bar
        ax.errorbar(x, y, yerr=y_err, fmt='none', ecolor='#444444', elinewidth=1, capsize=4, zorder=1)
        
        # Plot Marker (Square)
        ax.scatter(x, y, s=150, marker='s', color=color, edgecolors='none', zorder=2)
        
        # Add Annotation
        config = label_configs[name]
        ax.annotate(
            formatted_names[name],
            xy=(x, y),
            xytext=config['xytext'],
            textcoords='offset points',
            ha=config['ha'],
            va=config['va'],
            fontsize=12,
            arrowprops=dict(arrowstyle='-', color='black', lw=0.8, shrinkA=0, shrinkB=5)
        )

    # ---------------------------------------------------------
    # 4. Styling and Layout
    # ---------------------------------------------------------
    
    # Axis Limits
    ax.set_xlim(10, 18)
    ax.set_ylim(2.0, 6.0)
    
    # Axis Labels
    ax.set_xlabel(r'Thickness of deposited Li ($\mu$m)', fontsize=14, labelpad=10)
    ax.set_ylabel('Crystallite size in SEI (nm)', fontsize=14, labelpad=10)
    
    # Tick Styling
    ax.tick_params(axis='both', which='major', labelsize=11, direction='out', length=6)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add Statistical Text
    from scipy import stats
    corr, p_value = stats.spearmanr(df['Thickness_Li_um'], df['Crystallite_Mean'])
    stats_text = f"Correlation coefficient: {corr:.2f}\n$P$ value: {p_value:.3f}"
    ax.text(0.05, 0.85, stats_text, transform=ax.transAxes, fontsize=13, va='top', linespacing=1.5)
    
    # Add Figure Label "c"
    # Placing it outside the axes to the top left
    fig.text(0.02, 0.95, 'c', fontsize=20, fontweight='bold')

    # Adjust layout to prevent clipping
    plt.tight_layout(rect=[0.03, 0.03, 0.98, 0.95])
    
    # Save output
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)