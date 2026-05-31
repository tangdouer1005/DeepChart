import sys
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import matplotlib.ticker as ticker

# ---------------------------------------------------------
# 1. Source Data Embedding
# ---------------------------------------------------------
csv_data = """
| Unnamed: 0       | G15      | Unnamed: 2   | Unnamed: 3   | Unnamed: 4   | Unnamed: 5   | Unnamed: 6   | Unnamed: 7   | Unnamed: 8   | Unnamed: 9   |   Unnamed: 10 | Unnamed: 11        | Unnamed: 12   | Unnamed: 13   | Unnamed: 14   | Unnamed: 15   | Unnamed: 16   | Unnamed: 17   | Unnamed: 18   | Unnamed: 19   |
|:-----------------|:---------|:-------------|:-------------|:-------------|:-------------|:-------------|:-------------|:-------------|:-------------|--------------:|:-------------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|
| Log [NT], M      | nan      | nan          | nan          | nan          | nan          | nan          | nan          | nan          | nan          |           nan | Log [SR142948A], M | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           |
| nan              | 12-1-22  | 12-1-22      | 12-1-22      | 12-2-22      | 12-2-22      | 12-2-22      | 1-6-23       | 1-6-23       | 1-6-23       |           nan | nan                | 12-1-22       | 12-1-22       | 12-2-22       | 12-2-22       | 12-2-22       | 1-6-23        | 1-6-23        | 1-6-23        |
| 1e-05            | -0.15699 | -0.15583     | -0.13842     | -0.17349     | -0.1744      | -0.1799      | -0.15584     | -0.16021     | -0.16043     |           nan | 0.0001             | -0.08855      | -0.07396      | 0.014147      | -0.00459      | 0.020789      | 0.001533      | -0.01233      | 0.013925      |
| 1e-06            | -0.14506 | -0.15197     | -0.13142     | -0.16774     | -0.17165     | -0.1679      | -0.14829     | -0.15678     | -0.16133     |           nan | 1e-05              | -0.1119       | -0.10256      | 0.016763      | -0.00982      | 0.024122      | 0.012708      | 0.004646      | 0.018639      |
| 1e-07            | -0.1586  | -0.15624     | -0.14344     | -0.1686      | -0.1768      | -0.17126     | -0.15202     | -0.16272     | -0.16294     |           nan | 1e-06              | -0.08887      | -0.07024      | 0.018878      | -0.00223      | 0.021951      | 0.007269      | 0.000506      | 0.011629      |
| 1e-08            | -0.16128 | -0.1576      | -0.13469     | -0.16385     | -0.17005     | -0.17705     | -0.12016     | -0.13279     | -0.11306     |           nan | 1e-07              | -0.07601      | -0.05359      | 0.012458      | 0.000247      | 0.011935      | 0.003732      | 0.001799      | 0.015379      |
| 1e-09            | -0.07889 | -0.10819     | -0.09195     | -0.05223     | -0.04897     | -0.03298     | -0.02096     | -0.01439     | -0.01883     |           nan | 1e-08              | -0.03534      | -0.02908      | 0.010749      | -0.01373      | 0.016429      | -0.00083      | -0.01497      | 0.005099      |
| 1e-10            | -0.00973 | -0.0362      | -0.00634     | -0.00497     | -0.00965     | 0.006698     | 0.000145     | 0.011711     | 0.010737     |           nan | 1e-09              | -0.01628      | -0.00839      | 0.022166      | 0.005624      | 0.017054      | 0.004413      | 0.001778      | -0.0044       |
| 1e-11            | 0.005662 | -0.00953     | 0.025505     | -0.00727     | 0.006723     | 0.004518     | 0.0113       | 0.005111     | 0.008033     |           nan | 1e-10              | 0.012795      | 0.008625      | 0.007496      | -0.00362      | 0.011097      | 0.003117      | -0.00945      | -0.00504      |
| 1e-12            | 0        | 0            | 0            | 0            | 0            | 0            | 0            | 0            | 0            |           nan | 1e-12              | 0             | 0             | 0             | 0             | 0             | 0             | 0             | 0             |
| nan              | nan      | nan          | nan          | nan          | nan          | nan          | nan          | nan          | nan          |           nan | nan                | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           |
| nan              | nan      | nan          | nan          | nan          | nan          | nan          | nan          | nan          | nan          |           nan | nan                | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           |
| Log [SBI-553], M | nan      | nan          | nan          | nan          | nan          | nan          | nan          | nan          | nan          |           nan | Log [PD149163], M  | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           |
| nan              | 12-1-22  | 12-2-22      | 12-2-22      | 12-2-22      | 1-6-23       | 1-6-23       | 1-6-23       | nan          | nan          |           nan | 3e-05              | 12-1-22       | 12-1-22       | 12-2-22       | 12-2-22       | 12-2-22       | 1-6-23        | 1-6-23        | 1-6-23        |
| 3e-05            | -0.09861 | -0.1157      | -0.13439     | -0.1263      | -0.119       | -0.12425     | -0.12537     | nan          | nan          |           nan | 1e-05              | -0.17917      | -0.17341      | -0.18797      | -0.17452      | -0.17156      | -0.17573      | -0.17123      | -0.17414      |
| 1e-05            | -0.07934 | -0.09966     | -0.12632     | -0.12164     | -0.11093     | -0.12119     | -0.11141     | nan          | nan          |           nan | 3e-06              | -0.16581      | -0.15996      | -0.17919      | -0.17172      | -0.1786       | -0.17259      | -0.1696       | -0.16955      |
| 3e-06            | -0.06782 | -0.07933     | -0.08956     | -0.0753      | -0.0785      | -0.0927      | -0.07484     | nan          | nan          |           nan | 1e-06              | -0.16122      | -0.16283      | -0.16361      | -0.16151      | -0.15474      | -0.16296      | -0.16501      | -0.16523      |
| 1e-06            | -0.02858 | -0.03532     | -0.03994     | -0.02481     | -0.04323     | -0.0461      | -0.03574     | nan          | nan          |           nan | 3e-07              | -0.14928      | -0.14424      | -0.14512      | -0.13367      | -0.03465      | -0.14537      | -0.14434      | -0.13877      |
| 3e-07            | -0.00326 | -0.02527     | -0.02127     | -0.00201     | -0.01642     | -0.02961     | -0.01341     | nan          | nan          |           nan | 1e-07              | -0.12364      | -0.11216      | -0.11982      | -0.12027      | -0.00655      | -0.11756      | -0.11853      | -0.11684      |
| 1e-07            | -0.02363 | 0.002412     | -0.00762     | -0.00611     | -0.00318     | -0.00824     | -0.005       | nan          | nan          |           nan | 3e-08              | -0.09071      | -0.08362      | -0.07866      | -0.07205      | -0.0127       | -0.09354      | -0.08725      | -0.07885      |
| 1e-12            | 0        | 0            | 0            | 0            | 0            | 0            | 0            | nan          | nan          |           nan | 1e-14              | 0             | 0             | 0             | 0             | 0             | 0             | 0             | 0             |
"""

# ---------------------------------------------------------
# 2. Data Parsing Logic
# ---------------------------------------------------------
def parse_datasets(csv_text):
    # Read the markdown table
    # sep='|' handles the markdown pipes. skipinitialspace handles spaces after pipes.
    df = pd.read_csv(io.StringIO(csv_text), sep='|', header=None, skipinitialspace=True)
    
    # Clean up: remove first and last columns if they are empty (common in markdown)
    # The first column (index 0) might be empty string due to leading pipe
    if df.iloc[0, 0] == '' or pd.isna(df.iloc[0, 0]):
        df = df.drop(columns=[0])
    
    # Reset columns to be 0-indexed for easier handling
    df.columns = range(df.shape[1])
    
    # Remove the last column if it's empty/NaN (trailing pipe)
    if df.iloc[:, -1].isna().all():
        df = df.iloc[:, :-1]

    datasets = {}

    # --- Block 1: Rows 0-9 ---
    # NT Data: Conc in Col 0, Values in Cols 1-9
    # SR Data: Conc in Col 11, Values in Cols 12-19
    
    # Helper to extract and clean
    def extract_block(df_subset, conc_col_idx, val_col_start, val_col_end, name):
        # Filter rows where concentration is valid (not nan, not header)
        # We assume data starts at row 2 (index 2) relative to the block start
        # But we need to be careful about the exact row indices.
        
        data_rows = []
        for i in range(2, len(df_subset)):
            conc_val = df_subset.iloc[i, conc_col_idx]
            # Check if it's a number
            try:
                conc_float = float(conc_val)
                if not np.isnan(conc_float):
                    vals = pd.to_numeric(df_subset.iloc[i, val_col_start:val_col_end+1], errors='coerce')
                    data_rows.append({'conc': conc_float, 'vals': vals.values})
            except (ValueError, TypeError):
                continue
        
        if not data_rows:
            return None

        # Aggregate
        concs = []
        means = []
        sems = []
        
        for row in data_rows:
            c = row['conc']
            v = row['vals']
            v = v[~np.isnan(v)] # Remove NaNs
            if len(v) > 0:
                # Invert signal (multiply by -1) to match chart (positive response)
                # The data is negative, chart is positive.
                v = -1 * v 
                concs.append(np.log10(c))
                means.append(np.mean(v))
                sems.append(np.std(v, ddof=1) / np.sqrt(len(v)))
        
        return pd.DataFrame({'log_conc': concs, 'mean': means, 'sem': sems}).sort_values('log_conc')

    # Extract NT (Neurotensin)
    # Block 1 is roughly rows 0 to 10
    block1 = df.iloc[0:11].reset_index(drop=True)
    datasets['NT'] = extract_block(block1, 0, 1, 9, 'NT')
    
    # Extract SR (SR142948A)
    datasets['SR'] = extract_block(block1, 11, 12, 19, 'SR')

    # --- Block 2: Rows 12-20 ---
    # Find the row where 'Log [SBI-553]' is in column 0
    start_row_2 = df[df[0].astype(str).str.contains('SBI')].index[0]
    block2 = df.iloc[start_row_2:].reset_index(drop=True)
    
    # Extract SBI (SBI-553)
    # Conc in Col 0, Values in Cols 1-7
    datasets['SBI'] = extract_block(block2, 0, 1, 7, 'SBI')
    
    # Extract PD (PD149163)
    # Conc in Col 11, Values in Cols 12-19
    datasets['PD'] = extract_block(block2, 11, 12, 19, 'PD')

    return datasets

# ---------------------------------------------------------
# 3. Curve Fitting
# ---------------------------------------------------------
def sigmoid(x, top, log_ec50, hill_slope):
    bottom = 0 # Fixed to 0 based on data normalization
    return bottom + (top - bottom) / (1 + 10**((log_ec50 - x) * hill_slope))

def fit_and_plot(ax, name, df, color, marker_style='o'):
    x_data = df['log_conc'].values
    y_data = df['mean'].values
    
    # Plot raw points
    ax.plot(x_data, y_data, linestyle='None', marker=marker_style, 
            color=color, markersize=8, zorder=5)
    
    # Curve Fit
    # Initial guesses
    p0 = [max(y_data), np.median(x_data), 1.0]
    
    try:
        # If data is too flat (like SR), curve_fit might fail or produce wild results.
        # Check amplitude
        if (max(y_data) - min(y_data)) < 0.02:
            raise RuntimeError("Data too flat for sigmoid fit")

        popt, _ = curve_fit(sigmoid, x_data, y_data, p0=p0, maxfev=10000)
        
        # Generate smooth curve
        x_smooth = np.linspace(-13, -3.5, 200)
        y_smooth = sigmoid(x_smooth, *popt)
        ax.plot(x_smooth, y_smooth, color=color, linewidth=2, zorder=4)
        
    except (RuntimeError, TypeError, ValueError):
        # Fallback: Linear interpolation or simple connection
        # For the flat orange line, a simple connection is fine
        ax.plot(x_data, y_data, color=color, linewidth=2, zorder=4)

# ---------------------------------------------------------
# 4. Main Execution
# ---------------------------------------------------------
def main():
    # Determine output filename
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]

    # Parse Data
    datasets = parse_datasets(csv_data)

    # Setup Plot
    fig, ax = plt.subplots(figsize=(5, 4.5))
    
    # Define Styles based on visual analysis of the chart
    # NT (Blue) - High potency
    # PD (Green) - Lower potency, high efficacy
    # SBI (Purple) - Lower potency, lower efficacy
    # SR (Orange) - Flat/Low
    
    styles = {
        'NT': {'color': '#0000CD'},      # MediumBlue
        'PD': {'color': '#2E8B57'},      # SeaGreen
        'SBI': {'color': '#9932CC'},     # DarkOrchid
        'SR': {'color': '#FF8C00'}       # DarkOrange
    }

    # Plot each dataset
    # Order matters for z-order if overlapping, but here they are distinct enough.
    for name in ['NT', 'PD', 'SBI', 'SR']:
        if name in datasets and datasets[name] is not None:
            fit_and_plot(ax, name, datasets[name], styles[name]['color'])

    # Styling
    # Axis Limits
    ax.set_xlim(-13, -3.5)
    ax.set_ylim(-0.05, 0.6) # Matches the visual scale (0 to 0.6 ticks)

    # Ticks
    ax.xaxis.set_major_locator(ticker.MultipleLocator(2)) # -12, -10, -8...
    ax.yaxis.set_major_locator(ticker.MultipleLocator(0.2)) # 0, 0.2, 0.4, 0.6
    
    # Tick formatting
    ax.tick_params(axis='both', which='major', labelsize=14, direction='in', length=5, width=1)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Thicken remaining spines slightly
    ax.spines['left'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1)

    # Add dashed line at y=0
    ax.axhline(y=0, color='black', linestyle='--', linewidth=0.8, zorder=1)

    # Add Title "G15" inside the plot
    ax.text(0.05, 0.95, 'G$_{15}$', transform=ax.transAxes, 
            fontsize=16, verticalalignment='top', horizontalalignment='left')

    # Adjust layout
    plt.tight_layout()
    
    # Save
    plt.savefig(output_file, dpi=300)

if __name__ == "__main__":
    main()