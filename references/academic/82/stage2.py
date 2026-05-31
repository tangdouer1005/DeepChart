import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def generate_chart(output_filename):
    # 1. Load Source Data
    data_str = """
| Station                | PM_size      | Site_type    | N_samples    | OP_DTT_m_mean   | OP_DTT_m_SD     | PM_mass_mean | PM_mass_SD   |
| nan                    | nan          | nan          | nan          | nmol min-1 µg-1 | nmol min-1 µg-1 | µg m-3       | µg m-3       |
| BERN                   | PM10         | Traffic      | 738          | 0.14            | 0.03            | 19.42        | 10.22        |
| BERN                   | PM2.5        | Traffic      | 644          | 0.1             | 0.02            | 12.61        | 7.52         |
| ZURICH                 | PM10         | Urban        | 204          | 0.13            | 0.05            | 18.38        | 12.57        |
| ZURICH                 | PM2.5        | Urban        | 90           | 0.08            | 0.02            | 10.8         | 6.97         |
| BCN                    | PM1          | Urban        | 94           | 0.06            | 0.02            | 14.71        | 4.91         |
| BCN                    | PM10         | Urban        | 270          | 0.11            | 0.04            | 23.31        | 8.94         |
| BCN                    | PM2.5        | Urban        | 197          | 0.07            | 0.02            | 17.48        | 6.32         |
| MRS-lcp                | PM1          | Urban        | 262          | 0.09            | 0.07            | 13.65        | 13.48        |
| MRS-lcp                | PM10         | Urban        | 271          | 0.1             | 0.04            | 18.69        | 8.2          |
| PARIS-lcpp             | PM10         | Urban        | 184          | 0.12            | 0.06            | 19.4         | 9.26         |
| PARIS-lcpp             | PM2.5        | Urban        | 69           | 0.08            | 0.04            | 12.51        | 7.26         |
| PARIS-lh               | PM10         | Urban        | 386          | 0.09            | 0.02            | 20.74        | 13.22        |
| PARIS-lh               | PM2.5        | Urban        | 807          | 0.08            | 0.03            | 10.32        | 6.06         |
| ATH                    | PM10         | Urban        | 147          | 0.08            | 0.02            | 31.99        | 14.89        |
| ATH                    | PM2.5        | Urban        | 152          | 0.08            | 0.03            | 24.7         | 16.61        |
| KRAK                   | PM1          | Urban        | 63           | 0.06            | 0.01            | 19.73        | 17.28        |
| KRAK                   | PM10         | Urban        | 63           | 0.07            | 0.02            | 28.69        | 18.9         |
| BASEL                  | PM10         | Suburban     | 90           | 0.06            | 0.02            | 13.97        | 9.26         |
| BASEL                  | PM2.5        | Suburban     | 90           | 0.06            | 0.02            | 10.6         | 7.76         |
| MGD                    | PM10         | Rural        | 240          | 0.09            | 0.05            | 16.7         | 10.6         |
| MGD                    | PM2.5        | Rural        | 153          | 0.08            | 0.04            | 10.61        | 7.2          |
| PAYRN                  | PM10         | Rural        | 103          | 0.07            | 0.03            | 13.49        | 8.31         |
| PAYRN                  | PM2.5        | Rural        | 102          | 0.06            | 0.03            | 9.68         | 6.73         |
| MSY                    | PM1          | Rural        | 93           | 0.04            | 0.02            | 9.35         | 4.39         |
| MSY                    | PM10         | Rural        | 106          | 0.05            | 0.02            | 12.82        | 6.24         |
| MSY                    | PM2.5        | Rural        | 107          | 0.05            | 0.04            | 9.62         | 4.68         |
| OPE                    | PM10         | Rural        | 200          | 0.07            | 0.06            | 9.54         | 6.54         |
| OPE                    | PM2.5        | Rural        | 102          | 0.05            | 0.03            | 9            | 7.23         |
    """

    # Robust Manual Parsing of Markdown Table
    lines = data_str.strip().split('\n')
    # Remove leading/trailing pipes and whitespace from each line
    cleaned_lines = []
    for line in lines:
        # Remove outer pipes if they exist
        content = line.strip()
        if content.startswith('|'): content = content[1:]
        if content.endswith('|'): content = content[:-1]
        cleaned_lines.append(content)
    
    # Split by pipe
    header = [c.strip() for c in cleaned_lines[0].split('|')]
    data_rows = []
    for line in cleaned_lines[1:]:
        row = [c.strip() for c in line.split('|')]
        data_rows.append(row)
        
    df = pd.DataFrame(data_rows, columns=header)
    
    # Drop the units row (index 0)
    # The units row has 'nan' in Station or 'nmol...' in values.
    # We can identify it by checking if 'N_samples' is 'nan'
    df = df[df['N_samples'] != 'nan'].copy()
    
    # Convert numeric columns
    numeric_cols = ['N_samples', 'OP_DTT_m_mean', 'OP_DTT_m_SD', 'PM_mass_mean', 'PM_mass_SD']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col])

    # Define Station Order
    station_order = [
        'BERN', 'ZURICH', 'BCN', 'MRS-lcp', 'PARIS-lcpp', 'PARIS-lh', 
        'ATH', 'KRAK', 'BASEL', 'MGD', 'PAYRN', 'MSY', 'OPE'
    ]

    # 2. Setup Plotting Parameters
    
    # Colors (Tableau 10 style matches the image well)
    colors = {
        'PM1': '#4E79A7',   # Blue
        'PM2.5': '#F28E2B', # Orange
        'PM10': '#59A14F'   # Green
    }
    
    # PM Size Order for sorting within station
    pm_order = {'PM1': 0, 'PM2.5': 1, 'PM10': 2}
    
    bar_width = 0.22

    # Initialize Figure with Dual Axes
    fig, ax1 = plt.subplots(figsize=(15, 5))
    ax2 = ax1.twinx()

    # 3. Plotting Loop
    
    x_positions = np.arange(len(station_order))
    
    for i, station in enumerate(station_order):
        station_data = df[df['Station'] == station].copy()
        
        # Sort by PM size
        station_data['pm_sort'] = station_data['PM_size'].map(pm_order)
        station_data = station_data.sort_values('pm_sort')
        
        # Calculate offsets to center the group
        n_bars = len(station_data)
        total_width = n_bars * bar_width
        start_offset = -total_width / 2 + bar_width / 2
        
        for j, (_, row) in enumerate(station_data.iterrows()):
            pm_size = row['PM_size']
            if pm_size not in colors:
                continue
                
            offset = start_offset + j * bar_width
            x_pos = i + offset
            color = colors[pm_size]
            
            # Plot Bar (Left Axis: OP_DTT)
            ax1.bar(x_pos, row['OP_DTT_m_mean'], 
                    width=bar_width, 
                    color=color, 
                    yerr=row['OP_DTT_m_SD'], 
                    capsize=3, 
                    error_kw={'ecolor': 'gray', 'alpha': 0.8, 'elinewidth': 1.5},
                    edgecolor='none',
                    zorder=2)
            
            # Plot Scatter Dot (Right Axis: PM Mass)
            ax2.scatter(x_pos, row['PM_mass_mean'], 
                        color=color, 
                        edgecolors='black', 
                        linewidth=1,
                        s=80, 
                        zorder=3)

    # 4. Styling and Layout
    
    # Axis Limits
    ax1.set_ylim(0, 0.25)
    ax2.set_ylim(0, 50)
    
    # Axis Labels
    ax1.set_ylabel(r'$OP_m^{DTT}$ (nmolDTT min$^{-1}$ $\mu$g$^{-1}$)', fontsize=13)
    ax2.set_ylabel(r'PM ($\mu$g m$^{-3}$)', fontsize=13)
    
    # X-Axis Ticks
    ax1.set_xticks(x_positions)
    ax1.set_xticklabels(station_order, rotation=60, ha='right', fontsize=12)
    ax1.set_xlim(-0.6, len(station_order) - 0.4)
    
    # Grid
    ax1.grid(axis='y', linestyle='--', linewidth=1.5, alpha=0.5, zorder=0)
    
    # Vertical Separators
    # BERN (0) | ZURICH(1)...KRAK(7) | BASEL(8) | MGD(9)...OPE(12)
    separators = [0.5, 7.5, 8.5]
    for sep in separators:
        ax1.axvline(x=sep, color='gray', linewidth=2.5, zorder=1)
        
    # Add "b)" label
    ax1.text(0.02, 0.90, 'b)', transform=ax1.transAxes, fontsize=16, fontweight='bold')

    # Adjust layout
    plt.tight_layout()
    
    # Save output
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    generate_chart(output_file)