import sys
import matplotlib.pyplot as plt
import pandas as pd
import io
import numpy as np

def main():
    # 1. Handle Output Filename
    output_filename = "output.png"
    if len(sys.argv) > 1:
        output_filename = sys.argv[1]

    # 2. Load Data
    # Creating a DataFrame directly from the provided source data values.
    # Mapping the raw rows to the labels seen in the chart.
    data = [
        # Label, PM_mass_mean (X), PM_mass_SEM (Xerr), OP_AA_m_mean (Y), OP_AA_m_SEM (Yerr), Color, Text Offset
        ("I",   20.22, 1.78, 0.07, 0.02, "#EA899A", (-5, 5)),   # Industrial (Pink)
        ("R",   15.52, 1.00, 0.06, 0.01, "#D966E8", (-10, -10)), # Rural (Purple)
        ("SU",  20.73, 6.58, 0.12, 0.03, "#6FAEE5", (-5, 5)),   # Suburban (Blue)
        ("T",   22.44, 3.26, 0.13, 0.03, "#C4B068", (5, 5)),    # Traffic (Gold/Brown)
        ("U",   21.91, 0.99, 0.07, 0.00, "#7FB866", (5, 5)),    # Urban (Green)
        ("(V)", 20.34, 2.10, 0.11, 0.01, "#C0C0C0", (-15, -5))  # Valley (Grey)
    ]
    
    df = pd.DataFrame(data, columns=["Label", "X", "Xerr", "Y", "Yerr", "Color", "Offset"])

    # 3. Setup Plot
    # The chart is taller than it is wide.
    fig, ax = plt.subplots(figsize=(3.5, 6))
    
    # 4. Plotting
    for _, row in df.iterrows():
        # Plot Error Bars and Marker
        # fmt='o' creates the dot. 
        # elinewidth controls thickness of error bars.
        # capsize=0 removes the perpendicular caps on error bars (matching the image style).
        # alpha controls transparency (error bars look slightly lighter/softer in image).
        
        # We plot the error bars first so the marker sits on top if needed, 
        # though in the image the marker seems integrated.
        ax.errorbar(
            x=row['X'], 
            y=row['Y'], 
            xerr=row['Xerr'], 
            yerr=row['Yerr'], 
            fmt='o', 
            color=row['Color'], 
            ecolor=row['Color'], # Error bar color same as marker
            elinewidth=2.5,      # Thick error bars
            markersize=9,        # Large markers
            capsize=0,
            alpha=0.8            # Slight transparency to match the "soft" look
        )
        
        # Add Text Labels
        # Using annotate with offset points for precise positioning relative to the dot
        ax.annotate(
            row['Label'], 
            (row['X'], row['Y']),
            xytext=row['Offset'], 
            textcoords='offset points',
            fontsize=12,
            color='black',
            fontfamily='sans-serif'
        )

    # 5. Styling
    
    # Axis Limits
    ax.set_xlim(12, 28)
    ax.set_ylim(0.04, 0.165)
    
    # Axis Ticks
    ax.set_xticks([15, 20, 25])
    ax.set_yticks([0.04, 0.06, 0.08, 0.10, 0.12, 0.14, 0.16])
    
    # Tick Parameters
    ax.tick_params(axis='both', which='major', labelsize=12, direction='out', length=6, width=1)
    
    # Spines (Borders)
    # Remove Top and Right spines to match scientific publication style
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1)

    # Axis Labels
    # Using LaTeX formatting for superscripts and subscripts
    # Y-axis: OP_m^AA (nmol AA min^-1 ug^-1)
    ax.set_ylabel(r'OP$_m^{\mathrm{AA}}$ (nmolAA min$^{-1}$ $\mu$g$^{-1}$)', fontsize=13, labelpad=10)
    
    # X-axis: PM_10 (ug m^-3)
    ax.set_xlabel(r'PM$_{10}$ ($\mu$g m$^{-3}$)', fontsize=13, labelpad=10)

    # Figure Label "a"
    # Placing the bold 'a' in the top left corner outside the plot area
    fig.text(0.02, 0.95, 'a', fontsize=20, fontweight='bold', fontfamily='sans-serif')

    # Adjust layout to prevent clipping
    plt.tight_layout(rect=[0.05, 0.05, 1, 0.95])

    # 6. Save Output
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    main()