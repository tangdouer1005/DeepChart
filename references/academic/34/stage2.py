import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import gridspec

def main():
    # Handle output filename
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]

    # 1. Data Ingestion
    # We will parse the provided markdown-style data. 
    # Since the data is in three distinct blocks separated by 'nan' rows/headers, 
    # we will process them as three separate CSV-like strings.

    # Block 1: Main properties
    data_main_str = """Electrolyte|SSL ratio (%)|Li+ binding energy (eV)|Ionic conductivity (mS cm-1)|Initial interfacial resistance (Ohm)|SEI thickness (nm)|F ratio (%)|C ratio (%)|O ratio (%)|15th Rinterface (ohm)|15th overpotential (V)|Thickness of deposited Li (μm)|Cycle life
LiAsF6 electrolyte|90|-1.10496|0.346|88|9.8513|3.18|32.24|32.24|21.22|0.22|11.7|279
LiPF6 electrolyte|80|-1.11207|0.336|71|8.90335|7.99|38.74|22.7|9.5|0.17|12.3|115
LiFSI electrolyte|78.33333|-1.19801|0.344|47|10.2788|4.44|38.34|25.79|6.4|0.14|14.2|71
LiTFSI electrolyte|76.66667|-1.2481|0.322|52|9.10781|14.17|29.5|22.27|8|0.155|15.8|53
LiClO4 electrolyte|71.66667|-1.22465|0.28|35|8.86617|7.89|26.13|32.59|4.3|0.25|15.8|56
LiBF4 electrolyte|75|-1.20247|0.3|24|9.83271|9.65|27.63|23.13|30.1|0.22|16.1|38
LiDFOB electrolyte|70.4918|-1.36423|0.279|50|11.7379|7.07|32.83|29.61|6.6|0.16|14.9|45
LiNO3 electrolyte|68.33333|-1.40999|0.277|52|17.0074|7.47|33.73|24.44|4.54|0.18|17|30"""

    # Block 2: CCD measurements
    data_ccd_str = """Electrolyte|m1|m2
LiAsF6 electrolyte|36|36
LiPF6 electrolyte|32|28
LiFSI electrolyte|29|22
LiTFSI electrolyte|20|18
LiClO4 electrolyte|26|23
LiBF4 electrolyte|21|17
LiDFOB electrolyte|20|16
LiNO3 electrolyte|15|15"""

    # Block 3: Crystallite size measurements
    data_cryst_str = """Electrolyte|m1|m2|m3|m4
LiAsF6 electrolyte|2.9|2.6|2.6|2.7
LiPF6 electrolyte|3|3.3|2.8|3.3
LiFSI electrolyte|3.2|3.1|3.3|3
LiTFSI electrolyte|3.9|3.4|3|3.7
LiClO4 electrolyte|4.1|4.8|4.2|3.8
LiBF4 electrolyte|3.9|4.1|5.4|4.4
LiDFOB electrolyte|4.7|4.5|4.9|5.4
LiNO3 electrolyte|5.2|5.2|6.2|5.3"""

    # Parse DataFrames
    df_main = pd.read_csv(io.StringIO(data_main_str), sep='|')
    df_ccd_raw = pd.read_csv(io.StringIO(data_ccd_str), sep='|')
    df_cryst_raw = pd.read_csv(io.StringIO(data_cryst_str), sep='|')

    # 2. Data Processing
    # Calculate means for CCD and Crystallite size
    # Note: We assume the order of electrolytes is identical across tables (which it is in the source).
    
    # CCD Mean
    df_ccd_raw['J_crit'] = df_ccd_raw[['m1', 'm2']].mean(axis=1)
    
    # Crystallite Mean
    df_cryst_raw['Crystallite size'] = df_cryst_raw[['m1', 'm2', 'm3', 'm4']].mean(axis=1)

    # Merge into a single dataframe
    # We can just assign columns because the rows are aligned by Electrolyte
    df_final = df_main.copy()
    df_final['J_crit'] = df_ccd_raw['J_crit']
    df_final['Crystallite size'] = df_cryst_raw['Crystallite size']

    # 3. Prepare for Correlation
    # Map columns to the specific order and names required for the plot
    # Target Order based on the chart:
    # 1. SSL ratio
    # 2. Li+ binding energy (Eb)
    # 3. Ionic conductivity (sigma_ion)
    # 4. Initial interfacial resistance (Initial R_interface)
    # 5. SEI thickness
    # 6. F ratio (F%)
    # 7. C ratio (C%)
    # 8. O ratio (O%)
    # 9. 15th Rinterface (R_interface)
    # 10. 15th overpotential (eta_15th)
    # 11. J_crit (Calculated)
    # 12. Crystallite size (Calculated)
    # 13. Thickness of deposited Li
    # 14. Cycle life (Cycle performance)

    col_mapping = {
        'SSL ratio (%)': 'SSL ratio',
        'Li+ binding energy (eV)': 'Eb',
        'Ionic conductivity (mS cm-1)': 'sigma_ion',
        'Initial interfacial resistance (Ohm)': 'Initial R_interface',
        'SEI thickness (nm)': 'SEI thickness',
        'F ratio (%)': 'F%',
        'C ratio (%)': 'C%',
        'O ratio (%)': 'O%',
        '15th Rinterface (ohm)': 'R_interface',
        '15th overpotential (V)': 'eta_15th',
        'J_crit': 'J_crit',
        'Crystallite size': 'Crystallite size',
        'Thickness of deposited Li (μm)': 'Thickness',
        'Cycle life': 'Cycle performance'
    }

    # Select and rename columns
    df_corr_input = df_final[list(col_mapping.keys())].rename(columns=col_mapping)

    # Calculate Spearman Correlation
    corr_matrix = df_corr_input.corr(method='spearman')

    # 4. Plotting Setup
    
    # Define Labels
    # X-axis labels (Short)
    x_labels = [
        "SSL ratio", 
        "$E_b$", 
        "$\sigma_{ion}$", 
        "Initial $R_{interface}$", 
        "SEI thickness", 
        "F%", 
        "C%", 
        "O%", 
        "$R_{interface}$", 
        "$\eta_{15th}$", 
        "$J_{crit.}$", 
        "Crystallite size in SEI", 
        "Thickness of deposited Li", 
        "Cycle performance"
    ]

    # Y-axis labels (Long/Descriptive)
    y_labels = [
        "SSL ratio",
        "$E_b$ Li$^+$ binding energy",
        "$\sigma_{ion}$ ionic conductivity",
        "Initial $R_{interface}$\ninitial interfacial resistance",
        "SEI thickness",
        "F% F1s atomic percentage",
        "C% C1s atomic percentage",
        "O% O1s atomic percentage",
        "$R_{interface}$ interfacial resistance at 15th cycle",
        "$\eta_{15th}$ Li||Li overpotential at 15th cycle",
        "$J_{crit.}$ critical current density",
        "Crystallite size in SEI",
        "Thickness of deposited Li",
        "Cycle performance"
    ]

    # Setup Figure
    fig = plt.figure(figsize=(14, 12))
    
    # Use GridSpec to place colorbar on the left
    gs = gridspec.GridSpec(1, 2, width_ratios=[0.03, 1], wspace=0.05)
    ax_cbar = plt.subplot(gs[0])
    ax_heatmap = plt.subplot(gs[1])

    # Create Mask for the Lower Triangle (keep Upper Triangle including diagonal)
    # np.tril gives the lower triangle. We want to hide the lower triangle excluding diagonal?
    # The image shows the full upper triangle including diagonal.
    # Standard mask=mask hides True values.
    # We want to hide indices where i > j.
    mask = np.zeros_like(corr_matrix, dtype=bool)
    mask[np.tril_indices_from(mask, k=-1)] = True

    # Plot Heatmap
    sns.heatmap(
        corr_matrix,
        mask=mask,
        annot=True,
        fmt=".2f",
        cmap="RdBu",
        vmin=-1,
        vmax=1,
        center=0,
        square=True,
        linewidths=0.5,
        cbar=True,
        cbar_ax=ax_cbar,
        ax=ax_heatmap,
        annot_kws={"size": 10}
    )

    # 5. Styling

    # Axis Labels
    ax_heatmap.set_xticklabels(x_labels, rotation=90, ha='center', fontsize=12)
    ax_heatmap.set_yticklabels(y_labels, rotation=0, ha='right', fontsize=12)

    # Move X-axis to top
    ax_heatmap.xaxis.tick_top()
    ax_heatmap.xaxis.set_label_position('top')
    
    # Remove tick marks for cleaner look
    ax_heatmap.tick_params(axis='both', which='both', length=0)

    # Colorbar Styling
    # Move ticks to the left side of the colorbar
    ax_cbar.yaxis.set_ticks_position('left')
    ax_cbar.yaxis.set_label_position('left')
    # Set specific ticks
    ax_cbar.set_yticks(np.arange(-1.0, 1.1, 0.2))
    ax_cbar.tick_params(labelsize=12)
    # Label at the bottom of colorbar
    ax_cbar.set_xlabel("Spearman coefficient", fontsize=14, labelpad=10)
    # Align the label to the left/bottom visually
    ax_cbar.xaxis.set_label_coords(-1.5, -0.02) 

    # Add 'a' tag
    fig.text(0.02, 0.95, 'a', fontsize=24, fontweight='bold')

    # Adjust layout
    plt.tight_layout()
    
    # Save
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_file}")

if __name__ == "__main__":
    main()