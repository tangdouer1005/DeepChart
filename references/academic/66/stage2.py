import sys
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import matplotlib.ticker as ticker

# 1. Source Data (Embedded)
# Using the "Figure 2C Gi1" table from the prompt
csv_data = """
|   Log [NT], M | 0 µM      | Unnamed: 2   | Unnamed: 3   | Unnamed: 4   | Unnamed: 5       | Unnamed: 6     | Unnamed: 7      | Unnamed: 8     | 1 µM      | Unnamed: 10   | Unnamed: 11   | Unnamed: 12   | Unnamed: 13    | Unnamed: 14    | Unnamed: 15    | Unnamed: 16     | 3 µM      | Unnamed: 18   | Unnamed: 19   | Unnamed: 20   | Unnamed: 21    | Unnamed: 22    | Unnamed: 23    | Unnamed: 24    | 10 µM     | Unnamed: 26   | Unnamed: 27   | Unnamed: 28   | Unnamed: 29    | Unnamed: 30     | Unnamed: 31     | Unnamed: 32    | 30 µM     | Unnamed: 34   | Unnamed: 35   | Unnamed: 36   | Unnamed: 37     | Unnamed: 38    | Unnamed: 39    | Unnamed: 40    |
|--------------:|:----------|:-------------|:-------------|:-------------|:-----------------|:---------------|:----------------|:---------------|:----------|:--------------|:--------------|:--------------|:---------------|:---------------|:---------------|:----------------|:----------|:--------------|:--------------|:--------------|:---------------|:---------------|:---------------|:---------------|:----------|:--------------|:--------------|:--------------|:---------------|:----------------|:----------------|:---------------|:----------|:--------------|:--------------|:--------------|:----------------|:---------------|:---------------|:---------------|
|       nan     | 10-6-2022 | 10-6-2022    | 10-20-22     | 10-20-22     | KP 4/25/24       | KP 4/25/24     | KP 4/26/24      | KP 4/26/24     | 10-6-2022 | 10-6-2022     | 10-20-22      | 10-20-22      | KP 4/25/24     | KP 4/25/24     | KP 4/26/24     | KP 4/26/24      | 10-6-2022 | 10-6-2022     | 10-20-22      | 10-20-22      | KP 4/25/24     | KP 4/25/24     | KP 4/26/24     | KP 4/26/24     | 10-6-2022 | 10-6-2022     | 10-20-22      | 10-20-22      | KP 4/25/24     | KP 4/25/24      | KP 4/26/24      | KP 4/26/24     | 10-6-2022 | 10-6-2022     | 10-20-22      | 10-20-22      | KP 4/25/24      | KP 4/25/24     | KP 4/26/24     | KP 4/26/24     |
|         1e-05 | -0.3062   | -0.29489     | -0.25684     | -0.28092     | -0.2279320324    | -0.2377617241  | -0.2938953197   | -0.2645505406  | -0.24587  | -0.24365      | -0.24592      | -0.2479       | -0.1890359761  | -0.1896169061  | -0.2406297587  | -0.2285065465   | -0.24602  | -0.24802      | -0.2516       | -0.24151      | -0.1988590094  | -0.1944416572  | -0.2156770772  | -0.2251826784  | -0.24594  | -0.2511       | -0.22899      | -0.24138      | -0.1781649577  | -0.1923056307   | -0.2178158737   | -0.2107066886  | -0.23117  | -0.23337      | -0.24693      | -0.24115      | -0.1746639812   | -0.2096176391  | -0.2060531745  | -0.2164194239  |
|         1e-06 | -0.2969   | -0.28171     | -0.27497     | -0.27072     | -0.2310407839    | -0.2196222985  | -0.2639688241   | -0.2653554518  | -0.24444  | -0.25502      | -0.25619      | -0.22986      | -0.1764106393  | -0.1968943428  | -0.2039993934  | -0.2282610229   | -0.2452   | -0.24179      | -0.23897      | -0.23821      | -0.1847868318  | -0.1908588982  | -0.2065227395  | -0.2047811955  | -0.2383   | -0.243        | -0.22853      | -0.23488      | -0.1819762157  | -0.2012977982   | -0.2087176718   | -0.2084229409  | -0.1991   | -0.23073      | -0.22507      | -0.23041      | -0.1848718046   | -0.1994591372  | -0.2063106233  | -0.211655193   |
|         1e-07 | -0.29038  | -0.2843      | -0.2902      | -0.27223     | -0.2414617952    | -0.21483346    | -0.2795283295   | -0.251038841   | -0.22977  | -0.22757      | -0.23343      | -0.24816      | -0.1936812666  | -0.1756418542  | -0.2333913554  | -0.2084784589   | -0.22492  | -0.21909      | -0.23733      | -0.24541      | -0.1742167149  | -0.1904510095  | -0.1979461568  | -0.2059765919  | -0.22508  | -0.2299       | -0.23682      | -0.23729      | -0.1908489243  | -0.1792177425   | -0.2050454183   | -0.2035239643  | -0.19847  | -0.19304      | -0.23395      | -0.22108      | -0.1768740446   | -0.2082031063  | -0.2066961481  | -0.2081272606  |
|         1e-08 | -0.04921  | -0.09429     | -0.09734     | -0.09155     | -0.2352947412    | -0.2257474569  | -0.2664057806   | -0.2464156687  | -0.08699  | -0.05526      | -0.0908       | -0.08313      | -0.1818149763  | -0.1803234492  | -0.1847326591  | -0.1638052754   | -0.07099  | -0.08198      | -0.08925      | -0.16234      | -0.1600776667  | -0.1732059926  | -0.1747879437  | -0.1232183897  | -0.09546  | -0.11009      | -0.13423      | -0.15709      | -0.1688055642  | -0.1647333859   | -0.1710947528   | -0.1421351882  | -0.10823  | -0.09036      | -0.16186      | -0.13138      | -0.156173921    | -0.1539709896  | -0.1521859917  | -0.1363204245  |
|         1e-09 | -0.01155  | -0.02455     | -0.03208     | -0.01143     | -0.1708846154    | -0.1836113757  | -0.1452019557   | -0.05750493889 | -0.01058  | -0.02461      | -0.02288      | -0.04076      | -0.08556263724 | -0.1084522232  | -0.03937189772 | -0.002042974758 | -0.01308  | -0.00953      | -0.03031      | -0.05455      | -0.04358022466 | -0.1113905219  | -0.01400815208 | -0.01638931521 | -0.02333  | -0.03378      | -0.05853      | -0.05946      | -0.08928946443 | -0.08619691377  | -0.03913367008  | -0.03316096631 | -0.04142  | -0.06022      | -0.1185       | -0.10077      | -0.09647689475  | -0.1080567863  | -0.06721489544 | -0.06358824685 |
|         1e-10 | -0.0041   | -0.02044     | -0.01486     | -0.00063     | -0.02451194389   | -0.03518122406 | -0.01850617106  | 0.0350555442   | 0.007747  | -0.00706      | -0.04829      | -0.03825      | 0.003415222446 | 0.009639545614 | 0.03656638267  | 0.03376067873   | -0.02498  | -0.00879      | -0.02371      | -0.03807      | -0.01820811757 | 0.008356976777 | 0.0333941498   | 0.02168599105  | -0.02033  | -0.03279      | -0.0577       | -0.0376       | 0.005642285583 | -0.03070792858  | -0.002405684985 | 0.009383600216 | -0.04597  | -0.05179      | -0.10032      | -0.08327      | -0.0127789267   | -0.02322688814 | -0.01836230278 | -0.03546211348 |
|         1e-11 | -0.02146  | -0.0058      | -3e-05       | -0.00587     | -0.0002011497776 | -0.01057952988 | 0.0009966819672 | 0.02881487171  | 0.00715   | -0.01886      | -0.02011      | -0.02293      | 0.01663691993  | 0.02774018458  | -0.01447820949 | 0.07182981649   | -0.02958  | -0.00846      | -0.02033      | -0.01905      | 0.02398385416  | 0.02069519459  | 0.04014459092  | 0.02346142977  | -0.01764  | -0.04479      | -0.04812      | -0.02537      | 0.001720723969 | 2.445347708e-05 | 0.004200718283  | 0.01472632118  | -0.04716  | -0.04774      | -0.08697      | -0.07575      | -0.009657258353 | -0.02527234885 | -0.02340426442 | -0.031866378   |
|         1e-12 | -0.00333  | -0.01633     | -0.00848     | -0.00095     | -0.007812837545  | 0.007812837545 | -0.0164136723   | 0.0164136723   | -0.01602  | -0.01022      | -0.00749      | -0.01179      | 0.01945034701  | 0.04678234822  | 0.01674773678  | -0.002136965943 | -0.02265  | 0.001042      | -0.0016       | -0.00529      | 0.01973054172  | 0.03553490487  | 0.01818531522  | 0.01130011262  | -0.00789  | -0.01959      | -0.01059      | 0.026732      | 0.007470355342 | -0.00899383185  | -0.00403285544  | 0.00340288416  | -0.04573  | -0.0443       | -0.06137      | -0.06198      | -0.03249878998  | -0.02930006158 | -0.02216069367 | -0.04053750775 |
"""

# 2. Data Processing
def parse_markdown_table(table_str):
    lines = table_str.strip().split('\n')
    # Remove separator lines
    lines = [line for line in lines if '---' not in line]
    
    # Parse headers
    header_line = lines[0].strip()
    # Remove leading/trailing pipes
    if header_line.startswith('|'): header_line = header_line[1:]
    if header_line.endswith('|'): header_line = header_line[:-1]
    headers = [h.strip() for h in header_line.split('|')]
    
    data = []
    for line in lines[1:]:
        line = line.strip()
        if not line: continue
        if line.startswith('|'): line = line[1:]
        if line.endswith('|'): line = line[:-1]
        row = [c.strip() for c in line.split('|')]
        # Handle row length mismatch by padding or truncating
        if len(row) < len(headers):
            row += [''] * (len(headers) - len(row))
        else:
            row = row[:len(headers)]
        data.append(row)
        
    df = pd.DataFrame(data, columns=headers)
    return df

def load_and_process_data(csv_str):
    df = parse_markdown_table(csv_str)
    
    # The first column is 'Log [NT], M'
    # Filter out rows where this is not a number (e.g. the date row 'nan')
    # Convert first column to numeric, coerce errors to NaN
    col0_numeric = pd.to_numeric(df.iloc[:, 0], errors='coerce')
    
    # Keep rows where col0 is valid number
    df = df[col0_numeric.notna()]
    
    # Convert entire dataframe to float
    df = df.apply(pd.to_numeric, errors='coerce')
    
    # Extract X (Log Concentration)
    # The values are like 1e-05. We need log10 of them.
    x_val_raw = df.iloc[:, 0].values.astype(float)
    x_val_log = np.log10(x_val_raw)
    
    # Extract Groups
    # 0 µM: Columns 1 to 8 (indices 1 to 9 in python slice)
    # 30 µM: Columns 33 to 40 (indices 33 to 41 in python slice)
    
    group_0_data = df.iloc[:, 1:9]
    group_30_data = df.iloc[:, 33:41]
    
    # Calculate Mean and SEM
    # Invert signal (-1 * val) to match the visual plot direction
    y_mean_0 = group_0_data.mean(axis=1).values.astype(float) * -1
    y_err_0 = group_0_data.sem(axis=1).values.astype(float)
    
    y_mean_30 = group_30_data.mean(axis=1).values.astype(float) * -1
    y_err_30 = group_30_data.sem(axis=1).values.astype(float)
    
    return x_val_log, y_mean_0, y_err_0, y_mean_30, y_err_30

# 3. Curve Fitting
def sigmoid(x, Top, Bottom, LogEC50, HillSlope):
    return Bottom + (Top - Bottom) / (1 + 10**((LogEC50 - x) * HillSlope))

def fit_curve(x, y):
    # Ensure inputs are float arrays
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    
    # Remove NaNs/Infs from x and y before fitting
    mask = np.isfinite(x) & np.isfinite(y)
    x_clean = x[mask]
    y_clean = y[mask]
    
    if len(y_clean) < 4:
        return None
        
    # Initial guesses: Top, Bottom, LogEC50, HillSlope
    p0 = [max(y_clean), min(y_clean), np.median(x_clean), 1.0]
    try:
        popt, _ = curve_fit(sigmoid, x_clean, y_clean, p0=p0, maxfev=10000)
        return popt
    except:
        return None

# 4. Plotting
def create_plot(x, y0, err0, y30, err30, output_path):
    # Setup figure
    fig, ax = plt.subplots(figsize=(3.5, 3.5)) # Small square figure
    
    # Fit curves
    popt0 = fit_curve(x, y0)
    popt30 = fit_curve(x, y30)
    
    # Generate smooth x for plotting lines
    x_smooth = np.linspace(-14, -4, 200)
    
    # Colors
    color_0 = '#00008B' # Dark Blue
    color_30 = '#9400D3' # Dark Violet/Purple
    light_purple = '#BA55D3' # For arrows/glow
    
    # Plot 0 µM (Blue)
    if popt0 is not None:
        ax.plot(x_smooth, sigmoid(x_smooth, *popt0), color=color_0, linewidth=1.5, zorder=1)
    ax.errorbar(x, y0, yerr=err0, fmt='o', color=color_0, ecolor=color_0, 
                capsize=3, markersize=6, label='0 µM', zorder=2)
    
    # Plot 30 µM (Purple)
    if popt30 is not None:
        ax.plot(x_smooth, sigmoid(x_smooth, *popt30), color=color_30, linewidth=1.5, zorder=1)
        # Add a slight transparent glow/ribbon to the purple line
        ax.fill_between(x_smooth, 
                        sigmoid(x_smooth, *popt30) - 0.01, 
                        sigmoid(x_smooth, *popt30) + 0.01, 
                        color=color_30, alpha=0.2, zorder=0)

    ax.errorbar(x, y30, yerr=err30, fmt='s', color=color_30, ecolor=color_30, 
                capsize=3, markersize=6, label='30 µM', zorder=2)

    # Styling
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Dashed line at y=0
    ax.axhline(0, linestyle='--', color='black', linewidth=0.8, zorder=0)
    
    # Ticks
    ax.tick_params(direction='in', length=4, width=1)
    ax.set_xticks([-14, -12, -10, -8, -6, -4])
    ax.set_yticks([0.0, 0.1, 0.2, 0.3, 0.4])
    
    # Limits
    ax.set_xlim(-15, -3)
    ax.set_ylim(-0.05, 0.4)
    
    # Labels
    # The image has "Gi1" text inside the plot
    ax.text(0.05, 0.95, r'G$_{\mathrm{i1}}$', transform=ax.transAxes, fontsize=14, verticalalignment='top')
    
    # Font sizes
    ax.tick_params(axis='both', which='major', labelsize=12)
    
    # Arrows
    # Up arrow (Purple) at low concentration (~ -13.5)
    ax.arrow(-13.5, 0.01, 0, 0.05, head_width=0.6, head_length=0.03, fc=light_purple, ec=light_purple, width=0.15)
    
    # Down arrow (Purple) at high concentration (~ -4)
    ax.arrow(-4, 0.26, 0, -0.04, head_width=0.6, head_length=0.03, fc=light_purple, ec=light_purple, width=0.15)

    # Save
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)

# 5. Main Execution
if __name__ == "__main__":
    # Determine output filename
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
        
    # Process
    x_log, y0, err0, y30, err30 = load_and_process_data(csv_data)
    create_plot(x_log, y0, err0, y30, err30, output_file)