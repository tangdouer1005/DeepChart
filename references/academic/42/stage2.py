import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

def main():
    # 1. Handle Command Line Arguments
    output_filename = "output.png"
    if len(sys.argv) > 1:
        output_filename = sys.argv[1]

    # 2. Load Source Data
    # We embed the data exactly as provided in the prompt.
    # The data is cleaned of Markdown formatting for CSV parsing.
    csv_data = """Current Density (mA/cm2),Rep1_H2,Rep1_C2H4,nan1,Rep2_H2,Rep2_C2H4,nan2,Rep3_H2,Rep3_C2H4,nan3,Avg_H2,Avg_C2H4
50,0.09562508428860417,0.27377173745173744,nan,0.08166149696561024,0.2903888803088803,nan,0.09324558327714091,0.2774304864864865,nan,0.0901774,0.28053
100,0.07264598786244099,0.3495242213642214,nan,0.06387997302764666,0.3397964478764479,nan,0.08520040458530005,0.33606292921492914,nan,0.0739088,0.341795
200,0.051187457855697914,0.41262543114543115,nan,0.04671746459878625,0.4046474131274131,nan,0.061038705327039776,0.402314054054054,nan,0.0529812,0.406529
300,0.05160035963137784,0.4295400429000429,nan,0.04587592717464599,0.42223042471042466,nan,0.062447156664418954,0.4415946014586014,nan,0.0533078,0.431122
400,0.05305664194200944,0.45169425997425994,nan,0.0496608226567768,0.43887150579150574,nan,0.06659838165879972,0.4492887696267696,nan,0.0564386,0.446618
500,0.05537828725556304,0.47332697039897037,nan,0.057444639244774096,0.45714143629343634,nan,0.06460213081591368,0.45415355057915047,nan,0.0591417,0.461541
600,0.057465048325466395,0.4859334706134706,nan,0.05663385030343897,0.46232803088803087,nan,0.0663062261182288,0.5100811788931789,nan,0.060135,0.486114
700,0.06027588864271265,0.5073731494760066,nan,0.05893998651382333,0.4818689023717595,nan,0.06692542144302088,0.5251823614635042,nan,0.0620471,0.504808
800,0.06099511126095751,0.5276463577863578,nan,0.05805394470667566,0.49906922779922785,nan,0.06894325691166553,0.542612507078507,nan,0.0626641,0.523109"""

    df = pd.read_csv(io.StringIO(csv_data))

    # 3. Process Data
    # Extract replicates for H2 and C2H4
    # The source data is in fractions (e.g., 0.09), but the chart is in % (e.g., 9).
    # We multiply by 100.
    
    h2_reps = df[['Rep1_H2', 'Rep2_H2', 'Rep3_H2']].values * 100
    c2h4_reps = df[['Rep1_C2H4', 'Rep2_C2H4', 'Rep3_C2H4']].values * 100
    
    # Calculate Mean and Standard Deviation
    h2_mean = np.mean(h2_reps, axis=1)
    h2_std = np.std(h2_reps, axis=1)
    
    c2h4_mean = np.mean(c2h4_reps, axis=1)
    c2h4_std = np.std(c2h4_reps, axis=1)
    
    current_density = df['Current Density (mA/cm2)'].astype(str).tolist()

    # 4. Plotting Configuration
    # Colors extracted from the reference image
    colors = {
        'H2': '#B9C3D7',         # Light Periwinkle
        'C2H4': '#6D85AF',       # Muted Blue
        'Acetate': '#4E6990',    # Dark Blue (Legend only, data missing)
        'Ethanol': '#D5A79C',    # Pinkish Beige (Legend only, data missing)
        'n-propanol': '#A95D4E'  # Reddish Brown (Legend only, data missing)
    }

    fig, ax = plt.subplots(figsize=(6, 5.5))
    
    # Bar settings
    bar_width = 0.5
    indices = np.arange(len(current_density))
    
    # Error bar settings
    error_kw = dict(lw=1, capsize=2, capthick=1, ecolor='black')

    # 5. Create Stacked Bars
    # Layer 1: H2
    p1 = ax.bar(indices, h2_mean, bar_width, 
                yerr=h2_std, label='H$_2$', 
                color=colors['H2'], error_kw=error_kw)

    # Layer 2: C2H4 (Stacked on H2)
    p2 = ax.bar(indices, c2h4_mean, bar_width, 
                bottom=h2_mean, yerr=c2h4_std, label='C$_2$H$_4$', 
                color=colors['C2H4'], error_kw=error_kw)

    # Note: The source data provided does not contain values for Acetate, Ethanol, or n-propanol.
    # Therefore, we cannot plot bars for them without hallucinating data.
    # However, we will add them to the legend to match the visual style of the requested image.

    # 6. Styling
    
    # Axis Labels
    ax.set_ylabel('FE (%)', fontsize=12, color='black')
    ax.set_xlabel('Current density (mA cm$^{-2}$)', fontsize=12, color='black')
    
    # Ticks
    ax.set_xticks(indices)
    ax.set_xticklabels(current_density, fontsize=10)
    ax.set_ylim(0, 110)
    ax.set_yticks(np.arange(0, 120, 20))
    ax.tick_params(axis='y', labelsize=10, direction='out', length=6)
    ax.tick_params(axis='x', labelsize=10, direction='out', length=6)

    # Legend
    # We create custom handles to match the full legend of the original image
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=colors['H2'], label='H$_2$'),
        Patch(facecolor=colors['C2H4'], label='C$_2$H$_4$'),
        Patch(facecolor=colors['Acetate'], label='Acetate'),
        Patch(facecolor=colors['Ethanol'], label='Ethanol'),
        Patch(facecolor=colors['n-propanol'], label='n-propanol')
    ]
    
    # Position legend above the plot
    ax.legend(handles=legend_elements, 
              loc='lower center', 
              bbox_to_anchor=(0.5, 1.02), 
              ncol=5, 
              frameon=False, 
              fontsize=9,
              handlelength=1.2,
              handleheight=1.2,
              columnspacing=1.0)

    # Add the figure label "d"
    fig.text(0.02, 0.93, 'd', fontsize=24, fontweight='bold', va='top')

    # Adjust layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.88) # Make room for legend and title

    # 7. Save Output
    plt.savefig(output_filename, dpi=300)

if __name__ == "__main__":
    main()