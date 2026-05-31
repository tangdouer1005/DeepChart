import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io

def generate_chart(output_filename):
    # 1. Load and Process Source Data
    # The provided data contains the raw measurements for the "Experimental" series.
    csv_data = """Electrolyte|measurement #1|measurement #2|measurement #3|measurement #4
LiAsF6 electrolyte|2.9|2.6|2.6|2.7
LiPF6 electrolyte|3|3.3|2.8|3.3
LiFSI electrolyte|3.2|3.1|3.3|3
LiTFSI electrolyte|3.9|3.4|3|3.7
LiClO4 electrolyte|4.1|4.8|4.2|3.8
LiBF4 electrolyte|3.9|4.1|5.4|4.4
LiDFOB electrolyte|4.7|4.5|4.9|5.4
LiNO3 electrolyte|5.2|5.2|6.2|5.3"""

    # Parse the CSV data
    df = pd.read_csv(io.StringIO(csv_data), sep='|')
    
    # Clean up column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Clean up electrolyte names (strip whitespace)
    df['Electrolyte'] = df['Electrolyte'].str.strip()

    # Calculate Mean and Standard Deviation for the Experimental series (Blue Diamonds)
    measurement_cols = ['measurement #1', 'measurement #2', 'measurement #3', 'measurement #4']
    df['Experimental_Mean'] = df[measurement_cols].mean(axis=1)
    df['Experimental_Std'] = df[measurement_cols].std(axis=1)

    # 2. Define Simulation Data
    # The provided source data table only contained the Experimental raw values.
    # The "Simulation (MD)" values (Grey Circles) are extracted visually from the target image 
    # to ensure the chart is replicated faithfully.
    simulation_values = [
        2.05,  # LiAsF6
        2.32,  # LiPF6
        2.65,  # LiFSI
        2.75,  # LiTFSI
        2.95,  # LiClO4
        3.15,  # LiBF4
        3.40,  # LiDFOB
        4.32   # LiNO3
    ]
    df['Simulation_Mean'] = simulation_values

    # 3. Prepare Plotting Labels (Formatting chemical formulas)
    # Mapping full names to the abbreviated labels with LaTeX-style subscripts seen in the image
    label_map = {
        'LiAsF6 electrolyte': r'AsF$_6$',
        'LiPF6 electrolyte': r'PF$_6$',
        'LiFSI electrolyte': 'FSI',
        'LiTFSI electrolyte': 'TFSI',
        'LiClO4 electrolyte': r'ClO$_4$',
        'LiBF4 electrolyte': r'BF$_4$',
        'LiDFOB electrolyte': 'DFOB',
        'LiNO3 electrolyte': r'NO$_3$'
    }
    df['Label'] = df['Electrolyte'].map(label_map)

    # 4. Plotting
    fig, ax = plt.subplots(figsize=(5, 6)) # Portrait aspect ratio

    # X-axis positions
    x_pos = np.arange(len(df))

    # Plot Simulation Series (Grey Circles)
    # Using zorder to manage layering, though scatter usually sits on top
    ax.scatter(x_pos, df['Simulation_Mean'], 
               color='gray', 
               edgecolors='dimgray', 
               s=60, 
               label='Simulation (MD)', 
               zorder=3)

    # Plot Experimental Series (Blue Diamonds with Error Bars)
    # We use errorbar for the points + bars.
    # fmt='' prevents a line connecting them.
    ax.errorbar(x_pos, df['Experimental_Mean'], 
                yerr=df['Experimental_Std'], 
                fmt='D',             # Diamond marker
                markersize=6,
                markerfacecolor='#aaccff', # Light blue fill
                markeredgecolor='#4477aa', # Darker blue edge
                ecolor='#333333',    # Dark grey/black error bars
                elinewidth=1.0,
                capsize=3,           # Caps on error bars
                label='Experimental (cryo-TEM)',
                zorder=4)

    # 5. Styling and Layout

    # Axis Labels
    ax.set_ylabel('Cluster diameter (nm)', fontsize=14, labelpad=10)
    ax.set_xlabel('Anion', fontsize=14, labelpad=10)

    # X-Axis Ticks
    ax.set_xticks(x_pos)
    ax.set_xticklabels(df['Label'], rotation=45, ha='right', rotation_mode='anchor', fontsize=12)

    # Y-Axis Ticks and Range
    ax.set_ylim(1.0, 6.0)
    ax.set_yticks([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    ax.tick_params(axis='y', labelsize=12)
    
    # Tick styling (outward facing)
    ax.tick_params(direction='out', length=6, width=1)

    # Spines (Borders)
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # Keep left and bottom, make them standard black
    ax.spines['left'].set_color('black')
    ax.spines['bottom'].set_color('black')

    # Legend
    # Located in bottom right, no frame
    legend = ax.legend(loc='lower right', frameon=False, fontsize=11, handletextpad=0.1)
    
    # Add the "b" label in the top left
    # Using figure coordinates or axes coordinates. 
    # In the image, 'b' is outside the plot area, top left.
    ax.text(-0.15, 1.05, 'b', transform=ax.transAxes, 
            fontsize=20, fontweight='bold', va='top', ha='right')

    # Adjust layout to prevent clipping of rotated labels
    plt.tight_layout()
    
    # Save output
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)