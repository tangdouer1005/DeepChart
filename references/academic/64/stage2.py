import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

def solve():
    # Source Data for Figure 2C G11
    csv_data = """|   Log [NT], M | 0 µM        | Unnamed: 2   | Unnamed: 3   | Unnamed: 4   | Unnamed: 5   | Unnamed: 6   | 1 µM       | Unnamed: 8   | Unnamed: 9   | Unnamed: 10   | Unnamed: 11   | Unnamed: 12   | 3 µM       | Unnamed: 14   | Unnamed: 15   | Unnamed: 16   | Unnamed: 17   | Unnamed: 18   | 10 µM      | Unnamed: 20   | Unnamed: 21   | Unnamed: 22   | Unnamed: 23   | Unnamed: 24   | 30 µM      | Unnamed: 26   | Unnamed: 27   | Unnamed: 28   | Unnamed: 29   | Unnamed: 30   |
|--------------:|:------------|:-------------|:-------------|:-------------|:-------------|:-------------|:-----------|:-------------|:-------------|:--------------|:--------------|:--------------|:-----------|:--------------|:--------------|:--------------|:--------------|:--------------|:-----------|:--------------|:--------------|:--------------|:--------------|:--------------|:-----------|:--------------|:--------------|:--------------|:--------------|:--------------|
|       nan     | 10-27-2022  | 10-27-2022   | 1-26-23      | 1-26-23      | 2-3-23       | 2-3-23       | 10-27-2022 | 10-27-2022   | 1-26-23      | 1-26-23       | 2-3-23        | 2-3-23        | 10-27-2022 | 10-27-2022    | 1-26-23       | 1-26-23       | 2-3-23        | 2-3-23        | 10-27-2022 | 10-27-2022    | 1-26-23       | 1-26-23       | 2-3-23        | 2-3-23        | 10-27-2022 | 10-27-2022    | 1-26-23       | 1-26-23       | 2-3-23        | 2-3-23        |
|         1e-05 | -0.25533125 | -0.25607     | -0.27235     | -0.26065     | -0.26089     | -0.24886     | -0.22489   | -0.22837     | -0.2368      | -0.23745      | -0.19195      | -0.19895      | -0.25365   | -0.16761      | -0.19821      | -0.1996       | -0.15229      | -0.14697      | -0.06909   | -0.10261      | -0.12589      | -0.11783      | -0.0906       | -0.09287      | 0.015804   | 0.01052       | -0.04899      | -0.05219      | -0.03064      | -0.02697      |
|         1e-06 | -0.24256223 | -0.24514     | -0.26565     | -0.26652     | -0.25535     | -0.25241     | -0.22276   | -0.21694     | -0.25023     | -0.24772      | -0.227        | -0.22667      | -0.24579   | -0.1894       | -0.21509      | -0.21653      | -0.1787       | -0.17309      | -0.09893   | -0.11853      | -0.14629      | -0.14602      | -0.11598      | -0.10536      | 0.000675   | -0.01989      | -0.07648      | -0.07341      | -0.04267      | -0.04167      |
|         1e-07 | -0.27337452 | -0.27289     | -0.29253     | -0.29439     | -0.28212     | -0.27577     | -0.20251   | -0.21058     | -0.24171     | -0.24357      | -0.2248       | -0.2253       | -0.25905   | -0.17379      | -0.21717      | -0.20729      | -0.16888      | -0.17964      | -0.09642   | -0.08229      | -0.14673      | -0.14844      | -0.11083      | -0.1159       | 0.020686   | -0.00308      | -0.08475      | -0.07564      | -0.05092      | -0.04161      |
|         1e-08 | -0.15581094 | -0.13868*    | -0.20031     | -0.18757     | -0.26141     | -0.25256     | -0.01465   | -0.00281     | -0.16855     | -0.15349      | -0.1781       | -0.14486      | -0.10013   | -0.0147       | -0.05789      | -0.01409      | -0.02633      | -0.04493      | 0.023699   | 0.020062      | -0.0097       | -0.01441      | -0.02332      | 0.002         | 0.046415   | 0.043478      | -0.00347      | -0.00273      | 0.003088      | -0.00115      |
|         1e-09 | -0.01442042 | -0.0027      | -0.09317     | -0.08766     | -0.05349     | -0.05462     | 0.036721   | 0.049616     | -0.04868     | -0.05939      | -0.00098      | 0.0178        | 0.016964   | 0.001524      | -0.01765      | -0.03745      | 0.023377      | 0.016303      | 0.038645   | 0.030971      | -0.02788      | -0.0289       | 0.005156      | -0.00194      | 0.033174   | 0.051789      | -0.02571      | -0.03852      | 0.010576      | 0.013696      |
|         1e-10 | 0.009719375 | 0.003991     | -0.02408     | -0.02734     | -0.0092      | -0.00174     | 0.031132   | 0.045077     | -0.02063     | -0.02578      | 0.012791      | 0.014273      | 0.03776    | 0.000428      | -0.03273      | -0.02709      | 0.021795      | 0.020898      | 0.041191   | 0.042416      | -0.01735      | -0.02096      | 0.005783      | -0.00555      | 0.03232    | 0.050301      | -0.02449      | -0.0266       | 0.01043       | 0.020342      |
|         1e-11 | 0.010826331 | 0.021449     | -0.00568     | -0.0185      | -0.02445     | 0.000318     | 0.041841   | 0.042009     | -0.01621     | -0.01652      | -0.0057       | 0.005921      | 0.03084    | 0.041519      | -0.02166      | -0.01116      | 0.000415      | 0.005509      | 0.039856   | 0.026375      | -0.02719      | -0.01971      | 0.007265      | 0.004543      | 0.020326   | 0.054557      | -0.0255       | 0.00864       | 0.007999      | -0.00144      |
|         1e-12 | 0.008096614 | -0.01838     | -0.00687     | -0.00364     | 0.002655     | -0.01102     | 0.033675   | 0.033213     | 0.007319     | -0.01019      | -0.01146      | -0.00641      | 0.044538   | 0.013508      | -0.00379      | -0.00607      | 0.004172      | -0.01806      | 0.029873   | 0.038044      | 0.001942      | 0.003746      | -0.00626      | -0.00075      | 0.05826    | 0.071347      | -0.00801      | -0.00209      | 0.002806      | 0.006295      |"""

    # 1. Parse Data
    # Read the pipe-separated markdown table
    # skipinitialspace=True handles spaces after pipes
    df = pd.read_csv(io.StringIO(csv_data), sep='|', skipinitialspace=True, header=0)
    
    # Remove the first row (dates) and the separator row (dashes) if present
    # The provided string has a markdown separator line (row 1) and a date row (row 2)
    # Pandas read_csv might interpret the separator line as data.
    # Let's inspect and clean.
    
    # Drop rows that contain dashes (markdown separator)
    df = df[~df.iloc[:, 1].astype(str).str.contains('---')]
    
    # Drop the row with dates (contains 'nan' in first column usually, or dates)
    # In the source, row 0 is headers. Row 1 is separator. Row 2 is dates.
    # We need to filter out non-numeric rows in the first column.
    
    # Drop empty columns created by leading/trailing pipes
    df = df.dropna(axis=1, how='all')
    
    # Convert first column to numeric, coercing errors to NaN to identify data rows
    df['Log [NT], M'] = pd.to_numeric(df.iloc[:, 0], errors='coerce')
    df = df.dropna(subset=['Log [NT], M'])
    
    # Clean data: remove '*' and convert all columns to float
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.replace('*', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 2. Define Column Groups
    # Based on the table structure:
    # Col 0: Log [NT]
    # 0 µM: Cols 1-6
    # 1 µM: Cols 7-12
    # 3 µM: Cols 13-18
    # 10 µM: Cols 19-24
    # 30 µM: Cols 25-30
    
    concentrations = {
        '0 µM':  list(range(1, 7)),
        '1 µM':  list(range(7, 13)),
        '3 µM':  list(range(13, 19)),
        '10 µM': list(range(19, 25)),
        '30 µM': list(range(25, 31))
    }
    
    # X axis: Log10 of concentration
    x_vals = np.log10(df.iloc[:, 0].values)
    
    # 3. Setup Plot
    fig, ax = plt.subplots(figsize=(4, 3.5))
    
    # Colors matching the gradient in the image (Dark Blue -> Light Purple -> Dark Purple)
    # 0uM: Dark Blue
    # 1uM: Very Light Purple
    # 3uM: Light Purple
    # 10uM: Medium Purple
    # 30uM: Dark Purple
    colors = ['#000099', '#E0B0FF', '#DA70D6', '#9932CC', '#4B0082']
    
    # Markers: Circle for control (0uM), Squares for others (based on visual inspection)
    markers = ['o', 's', 's', 's', 's']
    
    # 4PL Sigmoid Function
    def sigmoid(x, Top, Bottom, LogEC50, HillSlope):
        return Bottom + (Top - Bottom) / (1 + 10**((LogEC50 - x) * HillSlope))

    # 4. Process and Plot Each Group
    for i, (label, cols) in enumerate(concentrations.items()):
        # Extract Y data
        y_data_raw = df.iloc[:, cols].values
        
        # Invert Y data to match the visual representation (assuming raw data is negative BRET change)
        y_data = -1 * y_data_raw
        
        # Calculate Mean and SEM
        y_mean = np.nanmean(y_data, axis=1)
        y_sem = np.nanstd(y_data, axis=1) / np.sqrt(y_data.shape[1])
        
        # Plot Data Points with Error Bars
        ax.errorbar(x_vals, y_mean, yerr=y_sem, fmt=markers[i], color=colors[i], 
                    capsize=3, markersize=6, label=label, linestyle='None', markeredgewidth=0)
        
        # Curve Fitting
        # Initial guesses: Top~0.25, Bottom~0, LogEC50~-9, HillSlope~1
        p0 = [0.25, 0, -9, 1.0]
        try:
            popt, _ = curve_fit(sigmoid, x_vals, y_mean, p0=p0, maxfev=10000)
            
            # Generate smooth line
            x_smooth = np.linspace(min(x_vals)-1, max(x_vals)+1, 200)
            y_smooth = sigmoid(x_smooth, *popt)
            
            ax.plot(x_smooth, y_smooth, color=colors[i], linewidth=1.5)
        except Exception as e:
            # Fallback to simple line if fit fails
            ax.plot(x_vals, y_mean, color=colors[i], linewidth=1.5, alpha=0.5)

    # 5. Styling
    # Dashed line at y=0
    ax.axhline(0, color='black', linestyle='--', linewidth=0.8)
    
    # Axis Limits
    ax.set_xlim(-15, -3)
    ax.set_ylim(-0.05, 0.35) # Matches visual range
    
    # Ticks
    ax.set_xticks([-14, -12, -10, -8, -6, -4])
    ax.set_yticks([0, 0.1, 0.2, 0.3, 0.4])
    
    # Tick parameters (inward facing)
    ax.tick_params(axis='both', which='major', labelsize=12, direction='in', top=False, right=False)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Title inside the plot area (top left)
    ax.text(0.05, 0.95, "G$_{11}$", transform=ax.transAxes, fontsize=14, verticalalignment='top')
    
    # Arrow indicating trend (Top Right -> Bottom Right)
    arrow_x = -3.8
    arrow_y_start = 0.30
    arrow_y_end = 0.02
    ax.annotate('', xy=(arrow_x, arrow_y_end), xytext=(arrow_x, arrow_y_start),
                arrowprops=dict(arrowstyle='->', color='#800080', lw=2))

    plt.tight_layout()
    
    # Save Output
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    plt.savefig(output_file, dpi=300)

if __name__ == "__main__":
    solve()