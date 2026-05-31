import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# 1. Source Data (Embedded)
csv_data = """
| Fig. 7a              | Unnamed: 1      | Unnamed: 2          |   Unnamed: 3 | Fig. 7b                    | Unnamed: 5      | Unnamed: 6          |   Unnamed: 7 | Fig. 7c                       | Unnamed: 9      | Unnamed: 10         |   Unnamed: 11 | Fig. 7d                    | Unnamed: 13     | Unnamed: 14         |
|:---------------------|:----------------|:--------------------|-------------:|:---------------------------|:----------------|:--------------------|-------------:|:------------------------------|:----------------|:--------------------|--------------:|:---------------------------|:----------------|:--------------------|
| nan                  | nan             | nan                 |          nan | nan                        | nan             | nan                 |          nan | nan                           | nan             | nan                 |           nan | nan                        | nan             | nan                 |
| nan                  | nan             | nan                 |          nan | nan                        | nan             | nan                 |          nan | nan                           | nan             | nan                 |           nan | nan                        | nan             | nan                 |
| Water flowrate [LPM] | Heat power [kW] | H2 power (HHV) [kW] |          nan | Number of EC in series [-] | Heat power [kW] | H2 power (HHV) [kW] |          nan | Fraction increase PV area [-] | Heat power [kW] | H2 power (HHV) [kW] |           nan | Fraction inhomogeneity [-] | Heat power [kW] | H2 power (HHV) [kW] |
| 4                    | 12.54969        | 2.56383             |          nan | 30                         | 14.06738        | 2.42885             |          nan | -0.01                         | 14.00903        | 2.44504             |           nan | 0                          | 14.00411        | 2.52974             |
| 4.22222              | 12.94205        | 2.55607             |          nan | 31                         | 14.0313         | 2.48638             |          nan | 0.00222                       | 13.99935        | 2.55441             |           nan | 0.11111                    | 13.97707        | 2.57286             |
| 4.44444              | 13.30578        | 2.54881             |          nan | 32                         | 14.00105        | 2.53463             |          nan | 0.01444                       | 13.99101        | 2.66164             |           nan | 0.22222                    | 13.94922        | 2.61728             |
| 4.66667              | 13.64379        | 2.54199             |          nan | 33                         | 13.97772        | 2.57183             |          nan | 0.02667                       | 13.98485        | 2.7654              |           nan | 0.33333                    | 13.91881        | 2.66577             |
| 4.88889              | 13.95868        | 2.53551             |          nan | 34                         | 13.95487        | 2.60828             |          nan | 0.03889                       | 13.97775        | 2.87066             |           nan | 0.44444                    | 13.88884        | 2.71358             |
| 5.11111              | 14.25273        | 2.52925             |          nan | 35                         | 13.94783        | 2.6195              |          nan | 0.05111                       | 13.96978        | 2.9773              |           nan | 0.55556                    | 13.85947        | 2.76041             |
| 5.33333              | 14.52797        | 2.52308             |          nan | 36                         | 13.93679        | 2.63711             |          nan | 0.06333                       | 13.96196        | 3.0837              |           nan | 0.66667                    | 13.82843        | 2.80991             |
| 5.55556              | 14.78616        | 2.51698             |          nan | 37                         | 13.92168        | 2.66119             |          nan | 0.07556                       | 13.95426        | 3.18993             |           nan | 0.77778                    | 13.79622        | 2.86128             |
| 5.77778              | 15.02868        | 2.51115             |          nan | 38                         | 13.95207        | 2.61274             |          nan | 0.08778                       | 13.94662        | 3.29604             |           nan | 0.88889                    | 13.76039        | 2.91842             |
| 6                    | 15.25653        | 2.5061              |          nan | 39                         | 13.94198        | 2.62883             |          nan | 0.1                           | 13.93902        | 3.40209             |           nan | 1                          | 13.73574        | 2.95773             |
| nan                  | nan             | nan                 |          nan | 40                         | 13.93424        | 2.64117             |          nan | nan                           | nan             | nan                 |           nan | nan                        | nan             | nan                 |
| nan                  | nan             | nan                 |          nan | 41                         | 13.92495        | 2.65599             |          nan | nan                           | nan             | nan                 |           nan | nan                        | nan             | nan                 |
| nan                  | nan             | nan                 |          nan | 42                         | 13.9187         | 2.66595             |          nan | nan                           | nan             | nan                 |           nan | nan                        | nan             | nan                 |
| nan                  | nan             | nan                 |          nan | 43                         | 13.9798         | 2.56851             |          nan | nan                           | nan             | nan                 |           nan | nan                        | nan             | nan                 |
| nan                  | nan             | nan                 |          nan | 44                         | 14.13696        | 2.31789             |          nan | nan                           | nan             | nan                 |           nan | nan                        | nan             | nan                 |
| nan                  | nan             | nan                 |          nan | 45                         | 14.32758        | 2.0139              |          nan | nan                           | nan             | nan                 |           nan | nan                        | nan             | nan                 |
"""

def process_data(csv_text):
    # Read the entire CSV as string first to handle the markdown structure safely
    df = pd.read_csv(io.StringIO(csv_text), sep='|', header=None, dtype=str)
    
    # Clean whitespace from all cells
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    
    # Locate the header row for "Fig. 7b" data
    # We search for the specific column header "Number of EC in series [-]"
    start_row = -1
    col_idx = -1
    
    for r in range(len(df)):
        for c in range(len(df.columns)):
            val = str(df.iloc[r, c]).strip()
            if val == "Number of EC in series [-]":
                start_row = r
                col_idx = c
                break
        if start_row != -1:
            break
            
    if start_row == -1:
        raise ValueError("Could not find the target data header in the provided CSV.")
        
    # Extract the relevant columns: N_EC, Heat Power, H2 Power
    # These are contiguous in the source table: col_idx, col_idx+1, col_idx+2
    # The data starts immediately after the header row
    target_df = df.iloc[start_row+1:, col_idx:col_idx+3].copy()
    target_df.columns = ['N_EC', 'Heat_Power', 'H2_Power']
    
    # Convert columns to numeric
    # errors='coerce' turns "nan" strings and other non-numerics into actual NaNs
    for col in target_df.columns:
        target_df[col] = pd.to_numeric(target_df[col], errors='coerce')
        
    # Drop rows where N_EC is NaN (this removes the trailing 'nan' rows)
    target_df = target_df.dropna(subset=['N_EC'])
    
    return target_df

def plot_chart(df, output_path):
    # Define colors based on the image
    color_fuel = '#757575'  # Grey for Power fuel (H2 Power)
    color_heat = '#d65f5f'  # Red for Power heat
    
    # Create figure
    fig, ax1 = plt.subplots(figsize=(6, 5))
    
    # --- Left Axis (Power Fuel / H2 Power) ---
    # Data: H2 Power (Grey Squares)
    ax1.plot(df['N_EC'], df['H2_Power'], 
             color=color_fuel, 
             marker='s', 
             markersize=11, 
             linewidth=0.8, 
             linestyle='-',
             label='Power fuel')
    
    # Use raw string r'' to avoid SyntaxWarning with latex escape sequences
    ax1.set_xlabel(r'$N_{\mathrm{EC}}$ (–)', fontsize=14)
    ax1.set_ylabel('Power fuel (kW)', fontsize=14, color='black')
    
    # Styling ticks
    ax1.tick_params(axis='y', labelcolor='black', direction='out', length=6, width=0.8)
    ax1.tick_params(axis='x', direction='out', length=6, width=0.8)
    
    # Set Left Y-axis limits and ticks to match image
    ax1.set_ylim(1.9, 2.8)
    ax1.set_yticks([2.0, 2.2, 2.4, 2.6, 2.8])
    
    # --- Right Axis (Power Heat) ---
    ax2 = ax1.twinx()
    
    # Data: Heat Power (Red Triangles)
    ax2.plot(df['N_EC'], df['Heat_Power'], 
             color=color_heat, 
             marker='^', 
             markersize=12, 
             linewidth=0.8, 
             linestyle='-',
             label='Power heat')
    
    ax2.set_ylabel('Power heat (kW)', fontsize=14, color=color_heat, rotation=270, labelpad=20)
    ax2.tick_params(axis='y', labelcolor='black', direction='out', length=6, width=0.8)
    
    # Set Right Y-axis limits and ticks to match image
    ax2.set_ylim(13.8, 14.4)
    ax2.set_yticks([13.8, 14.0, 14.2, 14.4])
    
    # --- Additional Styling ---
    
    # Vertical dashed line at N_EC = 32
    ax1.axvline(x=32, color='grey', linestyle='--', linewidth=1, ymax=0.95)
    
    # X-axis ticks
    ax1.set_xticks([30, 35, 40, 45])
    ax1.set_xlim(28, 47)
    
    # Remove top spine
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    
    # Manage side spines for dual axis
    ax1.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    
    # Add the bold 'b' label in the top left
    ax1.text(-0.18, 1.0, 'b', transform=ax1.transAxes, 
             fontsize=24, fontweight='bold', va='top', ha='left')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    # Handle command line arguments for output filename
    output_filename = "output.png"
    if len(sys.argv) > 1:
        output_filename = sys.argv[1]
        
    try:
        df = process_data(csv_data)
        plot_chart(df, output_filename)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)