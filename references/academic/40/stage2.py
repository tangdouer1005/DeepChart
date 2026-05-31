import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def generate_chart(output_filename):
    # 1. Source Data Loading
    # The data is embedded directly as a string to ensure the script is self-contained.
    csv_data = """
| Unnamed: 0               | Replicat 1   | Unnamed: 2          | Unnamed: 3          |   Unnamed: 4 | Replicat 2   | Unnamed: 6          | Unnamed: 7          |   Unnamed: 8 | Replicat 3   | Unnamed: 10         | Unnamed: 11         |
|:-------------------------|:-------------|:--------------------|:--------------------|-------------:|:-------------|:--------------------|:--------------------|-------------:|:-------------|:--------------------|:--------------------|
| Current Density (mA/cm2) | Voltage      | H2 FE               | C2H4 FE             |          nan | Voltage      | H2 FE               | C2H4 FE             |          nan | Voltage      | H2 FE               | C2H4 FE             |
| 50                       | -2.19        | 0.14772951293614345 | 0.2841110201559966  |          nan | -2.21        | 0.16659888570878167 | 0.28937132854531883 |          nan | -2.18        | 0.1888294403408317  | 0.25330493150718664 |
| 100                      | -2.29        | 0.13622886439877685 | 0.35598251602440345 |          nan | -2.32        | 0.14907543682901048 | 0.33550637114835125 |          nan | -2.3         | 0.15912463821740822 | 0.29676788789945335 |
| 200                      | -2.42        | 0.12530608096033213 | 0.36550238628465515 |          nan | -2.45        | 0.1377245152430452  | 0.37442304425052125 |          nan | -2.43        | 0.15254533565244513 | 0.3435177886402429  |
| 300                      | -2.51        | 0.11464390335081295 | 0.37335524493525885 |          nan | -2.55        | 0.11102635632320186 | 0.38879786512901043 |          nan | -2.53        | 0.13583593231820743 | 0.3632693180940613  |
| 400                      | -2.6         | 0.10910135072793622 | 0.388883534833731   |          nan | -2.64        | 0.09560740292701592 | 0.41619116019255026 |          nan | -2.62        | 0.12006939120524997 | 0.38904904838695203 |
| 500                      | -2.69        | 0.10381782093740254 | 0.4165935997695558  |          nan | -2.73        | 0.09430612734127848 | 0.42967953252503405 |          nan | -2.7         | 0.11820621568028583 | 0.4104312502649696  |
| 600                      | -2.76        | 0.09963402785714663 | 0.4330863305582307  |          nan | -2.8         | 0.09568653789232114 | 0.44928148891806313 |          nan | -2.77        | 0.11560445294969272 | 0.43694898384427705 |
| 700                      | -2.83        | 0.09538907521023639 | 0.4513225621393819  |          nan | -2.86        | 0.1038688813362222  | 0.45312933890831797 |          nan | -2.83        | 0.1152933475744668  | 0.4448906002539135  |
| 800                      | -2.89        | 0.09551489238377986 | 0.457784267885434   |          nan | -2.92        | 0.10198024060175066 | 0.4568219553633485  |          nan | -2.89        | 0.11540281057686111 | 0.4581472241460321  |
"""

    # 2. Data Parsing
    # The input is a markdown table. We parse it manually to handle the multi-level headers and structure.
    lines = [line.strip() for line in csv_data.strip().split('\n')]
    data_rows = []
    
    # Skip header rows (0 and 1) and separator row (2)
    # Data starts from row index 3 in the split list (which corresponds to value 50)
    for line in lines:
        if not line.startswith('|'): continue
        parts = [p.strip() for p in line.split('|')]
        # Filter out empty strings from split (start/end pipes)
        parts = [p for p in parts if p != '']
        
        # Check if it's a data row (starts with a number)
        if parts[0].replace('.', '', 1).isdigit():
            data_rows.append(parts)

    # Extract columns based on position in the markdown table
    # Col 0: Current Density
    # Col 1: V (Rep1), Col 2: H2 (Rep1), Col 3: C2H4 (Rep1)
    # Col 5: V (Rep2), Col 6: H2 (Rep2), Col 7: C2H4 (Rep2)
    # Col 9: V (Rep3), Col 10: H2 (Rep3), Col 11: C2H4 (Rep3)
    
    current_density = []
    
    # Lists to store replicates
    h2_reps = [[], [], []]
    c2h4_reps = [[], [], []]
    volt_reps = [[], [], []]

    for row in data_rows:
        current_density.append(float(row[0]))
        
        # Replicate 1
        volt_reps[0].append(float(row[1]))
        h2_reps[0].append(float(row[2]))
        c2h4_reps[0].append(float(row[3]))
        
        # Replicate 2
        volt_reps[1].append(float(row[5]))
        h2_reps[1].append(float(row[6]))
        c2h4_reps[1].append(float(row[7]))
        
        # Replicate 3
        volt_reps[2].append(float(row[9]))
        h2_reps[2].append(float(row[10]))
        c2h4_reps[2].append(float(row[11]))

    # Convert to numpy arrays for calculation
    h2_arr = np.array(h2_reps) * 100  # Convert fraction to percentage
    c2h4_arr = np.array(c2h4_reps) * 100
    volt_arr = np.array(volt_reps)

    # Calculate Mean and Std Dev
    h2_mean = np.mean(h2_arr, axis=0)
    h2_std = np.std(h2_arr, axis=0)
    
    c2h4_mean = np.mean(c2h4_arr, axis=0)
    c2h4_std = np.std(c2h4_arr, axis=0)
    
    volt_mean = np.mean(volt_arr, axis=0)
    volt_std = np.std(volt_arr, axis=0)

    # 3. Plotting
    fig, ax1 = plt.subplots(figsize=(8, 6))

    # Colors extracted from image
    color_h2 = '#BDC6D9'       # Light blue/grey
    color_c2h4 = '#7087B0'     # Medium blue
    color_acetate = '#4E668C'  # Dark blue (Legend only - data missing)
    color_ethanol = '#D9ADA7'  # Pinkish (Legend only - data missing)
    color_nprop = '#B36855'    # Brownish (Legend only - data missing)
    color_line = '#8D564A'     # Brown line

    bar_width = 0.5
    x_indices = np.arange(len(current_density))

    # --- Left Axis: Stacked Bars ---
    # Note: The provided data ONLY contains H2 and C2H4. 
    # Acetate, Ethanol, and n-propanol are missing from the source table, 
    # so they cannot be plotted, but we will include them in the legend to match the image style.
    
    # Plot H2
    p1 = ax1.bar(x_indices, h2_mean, width=bar_width, color=color_h2, 
                 yerr=h2_std, capsize=2, error_kw={'elinewidth': 1, 'alpha': 0.8})
    
    # Plot C2H4 (Stacked on H2)
    p2 = ax1.bar(x_indices, c2h4_mean, width=bar_width, bottom=h2_mean, color=color_c2h4,
                 yerr=c2h4_std, capsize=2, error_kw={'elinewidth': 1, 'alpha': 0.8})

    # Styling Left Axis
    ax1.set_ylabel('FE (%)', fontsize=14)
    ax1.set_xlabel('Current density (mA cm$^{-2}$)', fontsize=14)
    ax1.set_ylim(0, 110)
    ax1.set_xticks(x_indices)
    ax1.set_xticklabels([int(x) for x in current_density], fontsize=12)
    ax1.tick_params(axis='y', labelsize=12)

    # --- Right Axis: Voltage Line ---
    ax2 = ax1.twinx()
    
    # Plot Voltage Line
    # The image shows markers with white face and brown edge
    ax2.errorbar(x_indices, volt_mean, yerr=volt_std, color=color_line,
                 marker='o', markersize=7, markerfacecolor='white', markeredgewidth=1.5,
                 linewidth=1, capsize=2)

    # Styling Right Axis
    ax2.set_ylabel('Cell voltage (V)', fontsize=14, rotation=270, labelpad=20)
    
    # Invert axis logic: The chart shows -2.0 at bottom and -3.0 at top.
    # This is an inverted scale for negative numbers.
    ax2.set_ylim(-2.0, -3.0) 
    ax2.tick_params(axis='y', labelsize=12)

    # --- Legend ---
    # Create custom handles to match the image exactly, even for missing data series
    patches = [
        mpatches.Patch(color=color_h2, label='H$_2$'),
        mpatches.Patch(color=color_c2h4, label='C$_2$H$_4$'),
        mpatches.Patch(color=color_acetate, label='Acetate'),
        mpatches.Patch(color=color_ethanol, label='Ethanol'),
        mpatches.Patch(color=color_nprop, label='$n$-propanol')
    ]
    
    # Place legend at the top, spanning columns
    ax1.legend(handles=patches, loc='upper center', bbox_to_anchor=(0.45, 1.15), 
               ncol=3, frameon=False, fontsize=11, columnspacing=1.5)

    # --- Annotations ---
    # "c" label
    ax1.text(-0.12, 1.12, 'c', transform=ax1.transAxes, fontsize=20, fontweight='bold')

    # Arrow pointing to right axis
    # Coordinates approximated based on visual placement near the top right
    ax2.annotate('', xy=(1.02, 0.92), xycoords='axes fraction', 
                 xytext=(0.95, 0.92), textcoords='axes fraction',
                 arrowprops=dict(arrowstyle="->", color=color_line, lw=1.5))

    # Adjust layout to prevent clipping
    plt.tight_layout()
    plt.subplots_adjust(top=0.85) # Make room for legend

    # Save output
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    generate_chart(output_file)