import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# ---------------------------------------------------------
# 1. Source Data Embedding
# ---------------------------------------------------------
# The data is embedded exactly as provided in the prompt.
csv_data = """
| Unnamed: 0       | Gq              | Unnamed: 2      | Unnamed: 3      | Unnamed: 4     | Unnamed: 5     | Unnamed: 6      | Unnamed: 7   | Unnamed: 8   | Unnamed: 9   |   Unnamed: 10 | Unnamed: 11        | Unnamed: 12     | Unnamed: 13     | Unnamed: 14    | Unnamed: 15     | Unnamed: 16     | Unnamed: 17     | Unnamed: 18   | Unnamed: 19   | Unnamed: 20   |
|:-----------------|:----------------|:----------------|:----------------|:---------------|:---------------|:----------------|:-------------|:-------------|:-------------|--------------:|:-------------------|:----------------|:----------------|:---------------|:----------------|:----------------|:----------------|:--------------|:--------------|:--------------|
| Log [NT], M      | nan             | nan             | nan             | nan            | nan            | nan             | nan          | nan          | nan          |           nan | Log [SR142948A], M | nan             | nan             | nan            | nan             | nan             | nan             | nan           | nan           | nan           |
| nan              | 9-29-2022       | 9-29-2022       | 9-29-2022       | 9-30-2022      | 9-30-2022      | 9-30-2022       | 10-20-22     | 10-20-22     | 10-20-22     |           nan | nan                | 9-29-2022       | 9-29-2022       | 9-29-2022      | 9-30-2022       | 9-30-2022       | 9-30-2022       | 10-20-22      | 10-20-22      | 10-20-22      |
| 1e-05            | -0.2846707733   | -0.2922985717   | -0.3193177434   | -0.3065884008  | -0.3204788423  | -0.325865056    | -0.2960383   | -0.31831     | -0.31534     |           nan | 0.0001             | 0.01551835518   | -0.009531307549 | 0.02556414581  | 0.03727658243   | 0.04267700414   | 0.03471723089   | 0.003298      | -0.01579      | 0.008178      |
| 1e-06            | -0.2837755147   | -0.2790089656   | -0.3184799264   | -0.3001126777  | -0.3363730402  | -0.329891852    | -0.29029718  | -0.31151     | -0.31947     |           nan | 1e-05              | -0.006806356965 | 0.00325625729   | 0.0282819784   | 0.04511932267   | 0.03243180303   | 0.01454354078   | -0.02388      | -0.0164       | 0.011033      |
| 1e-07            | -0.2845085962   | -0.2884077651   | -0.3221942222   | -0.302998495   | -0.3220711242  | -0.2961996195   | -0.30170406  | -0.31268     | -0.31973     |           nan | 1e-06              | 0.01871456628   | 0.0009482251578 | 0.02596617074  | 0.02877222398   | 0.02188480918   | 0.0318877293    | -0.00356      | -0.0346       | -0.00949      |
| 1e-08            | -0.2861371087   | -0.2937983124   | -0.3064097402   | -0.1745302564  | -0.196284247   | -0.1691147899   | -0.25900445  | -0.31037     | -0.27897     |           nan | 1e-07              | 0.01906760018   | 0.00254628934   | 0.02176789121  | 0.009862852531  | 0.02745551133   | -0.003120962184 | -0.01416      | -0.03401      | -0.00575      |
| 1e-09            | -0.1364206378   | -0.1539867212   | -0.08216952403  | 0.005149619583 | 0.01530646611  | 0.02295521923   | -0.06382135  | -0.09468     | -0.07666     |           nan | 1e-08              | 0.01653917056   | -0.01479382846  | 0.005373306705 | 0.01719663542   | -0.006388936239 | 0.0006392670214 | -0.00387      | -0.03053      | -0.00429      |
| 1e-10            | -0.01474690403  | -0.002808660416 | -0.01810853665  | 0.006762902844 | 0.02158308969  | 0.005950253723  | -0.02435792  | -0.00096     | 0.011162     |           nan | 1e-09              | 0.01125208223   | -0.01402880121  | 0.001006920087 | 0.02193310818   | 0.002682548168  | -0.01002280404  | -0.00749      | -0.02674      | -0.00044      |
| 1e-11            | -0.01579522443  | 0.004394906898  | -0.01337023148  | 0.01556749636  | 0.002418979757 | -0.01260954458  | -0.00932098  | 0.001582     | 0.007514     |           nan | 1e-10              | 0.01279465807   | -0.02011770642  | 0.01028645084  | 0.0272334621    | -0.01156297641  | -0.02599588148  | -0.00415      | -0.02971      | -0.00589      |
| 1e-12            | 0               | 0               | 0               | 0              | 0              | 0               | 0            | 0            | 0            |           nan | 1e-12              | 0               | 0               | 0              | 0               | 0               | 0               | 0             | 0             | 0             |
| nan              | nan             | nan             | nan             | nan            | nan            | nan             | nan          | nan          | nan          |           nan | nan                | nan             | nan             | nan            | nan             | nan             | nan             | nan           | nan           | nan           |
| nan              | nan             | nan             | nan             | nan            | nan            | nan             | nan          | nan          | nan          |           nan | nan                | nan             | nan             | nan            | nan             | nan             | nan             | nan           | nan           | nan           |
| Log [SBI-553], M | nan             | nan             | nan             | nan            | nan            | nan             | nan          | nan          | nan          |           nan | Log [PD149163], M  | nan             | nan             | nan            | nan             | nan             | nan             | nan           | nan           | nan           |
| nan              | 9-29-2022       | 9-29-2022       | 9-29-2022       | 9-30-2022      | 9-30-2022      | 9-30-2022       | 10-20-22     | 10-20-22     | 10-20-22     |           nan | nan                | 9-29-2022       | 9-29-2022       | 9-29-2022      | 9-30-2022       | 9-30-2022       | 9-30-2022       | 10-20-22      | 10-20-22      | 10-20-22      |
| 3e-05            | -0.01784590087  | -0.01786160807  | 0.01066236004   | 0.02248613077  | 0.01276301501  | 6.222282921e-05 | -0.01537     | 0.00931      | 0.00336      |           nan | 3e-05              | -0.338614818    | -0.3405346276   | -0.3328287892  | -0.3257737864   | -0.3081186091   | -0.3407366527   | -0.33512      | -0.34039006   | -0.34201      |
| 1e-05            | -0.01078614784  | -0.01783481942  | 0.01053609922   | 0.03255674649  | 0.004401341327 | 0.02165624513   | -0.01002     | -0.00154     | 0.00063      |           nan | 1e-05              | -0.3418162118   | -0.3367490733   | -0.3211403983  | -0.259265497    | -0.2453636257   | -0.2986696077   | -0.30747      | -0.289431762  | -0.30654      |
| 3e-06            | -0.002834037491 | -0.005377666716 | 0.00834612671   | 0.03628485793  | 0.006906849447 | 0.01410939454   | -0.01118     | -0.01431     | -0.01113     |           nan | 3e-06              | -0.3046899353   | -0.3092269811   | -0.3031103094  | -0.191687865    | -0.1868550215   | -0.233524305    | -0.27924      | -0.269188268  | -0.26957      |
| 1e-06            | 0.003823173438  | -0.01830586944  | -0.001833846773 | 0.03465847306  | 0.002538107204 | 0.03278517843   | -0.01912     | -0.01871     | -0.00198     |           nan | 1e-06              | -0.2334956111   | -0.2564710655   | -0.2683567328  | -0.08709610759  | -0.07243301327  | -0.1110112919   | -0.20001      | -0.183127389  | -0.19983      |
| 3e-07            | -0.003435117025 | 0.0005049550199 | -0.005930616238 | 0.01571439573  | 0.01389873352  | 0.01591047888   | -0.01264     | -0.00377     | 0.00266      |           nan | 3e-07              | -0.08323249529  | -0.1507142521   | -0.1939446581  | -0.006178763395 | -0.02816936576  | -0.04315777776  | -0.08875      | -0.072633535  | -0.10661      |
| 1e-07            | -0.01297468774  | -0.00693527962  | 0.003296560107  | 0.03097132517  | -0.01082877846 | -0.003031684702 | -0.01612     | 0.001852     | -0.01071     |           nan | 1e-07              | -0.02705875732  | -0.05281870506  | -0.113820769   | -0.005425441483 | -0.04175331565  | 0.0008431300221 | -0.01583      | -0.030061404  | -0.03099      |
| 1e-12            | 0               | 0               | 0               | 0              | 0              | 0               | 0            | 0            | 0            |           nan | 1e-12              | 0               | 0               | 0              | 0               | 0               | 0               | 0             | 0             | 0             |
"""

# ---------------------------------------------------------
# 2. Data Parsing and Processing
# ---------------------------------------------------------

def parse_and_process_data():
    # Read the markdown table
    # Use '|' as separator, skip initial/trailing whitespace
    df = pd.read_csv(io.StringIO(csv_data), sep='|', skipinitialspace=True)
    
    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Remove the first and last columns if they are empty (artifacts of markdown pipes)
    if 'Unnamed: 0' in df.columns and df.iloc[:, 0].astype(str).str.contains('Log').any():
        pass # Keep it, it has data
    else:
        # Sometimes markdown tables have empty columns at start/end
        df = df.iloc[:, 1:-1]

    # Define the 4 datasets based on the table structure
    # Structure:
    # Top Left: NT (Rows 2-9, Cols 0, 1-9)
    # Top Right: SR (Rows 2-9, Cols 11, 12-20)
    # Bottom Left: SBI (Rows 15-21, Cols 0, 1-9)
    # Bottom Right: PD (Rows 15-21, Cols 11, 12-20)

    datasets = []

    # Helper to extract block
    def extract_block(row_start, row_end, x_col_idx, y_col_start, y_col_end, name, color):
        # Extract subset
        subset = df.iloc[row_start:row_end+1, :].copy()
        
        # Get X values
        x_raw = subset.iloc[:, x_col_idx]
        # Convert to numeric, coerce errors
        x_vals = pd.to_numeric(x_raw, errors='coerce')
        
        # Get Y values
        y_raw = subset.iloc[:, y_col_start:y_col_end+1]
        y_vals = y_raw.apply(pd.to_numeric, errors='coerce')
        
        # Calculate Mean and SEM
        # Note: The raw data is negative (e.g., -0.3), but the chart shows positive activation (0 to 0.3).
        # We invert the signal (-1 * val) to match the visual representation of "Activation".
        y_mean = y_vals.mean(axis=1) * -1
        y_sem = y_vals.sem(axis=1) # SEM scale is same regardless of sign flip
        
        # Log transform X (Concentration)
        # Values are like 1e-05. Log10(1e-05) = -5.
        x_log = np.log10(x_vals)
        
        return {
            'name': name,
            'x': x_log.values,
            'y': y_mean.values,
            'y_err': y_sem.values,
            'color': color
        }

    # 1. NT (Neurotensin) - Top Left
    # Rows 2 to 9 (indices)
    nt_data = extract_block(2, 9, 0, 1, 9, 'NT', '#0000B2') # Dark Blue
    datasets.append(nt_data)

    # 2. PD (PD149163) - Bottom Right
    # Rows 15 to 21. Note: Row 15 is 3e-05. Row 21 is 1e-12.
    pd_data = extract_block(15, 21, 11, 12, 20, 'PD', '#4C9F70') # Green/Teal
    datasets.append(pd_data)

    # 3. SR (SR142948A) - Top Right
    # Rows 2 to 9.
    sr_data = extract_block(2, 9, 11, 12, 20, 'SR', '#B200B2') # Purple/Magenta
    datasets.append(sr_data)

    # 4. SBI (SBI-553) - Bottom Left
    # Rows 15 to 21.
    sbi_data = extract_block(15, 21, 0, 1, 9, 'SBI', '#F59B00') # Orange
    datasets.append(sbi_data)

    return datasets

# ---------------------------------------------------------
# 3. Curve Fitting
# ---------------------------------------------------------

def sigmoid(x, Top, Bottom, LogEC50, HillSlope):
    return Bottom + (Top - Bottom) / (1 + 10**((LogEC50 - x) * HillSlope))

def fit_and_plot(ax, data):
    x = data['x']
    y = data['y']
    y_err = data['y_err']
    color = data['color']
    
    # Plot data points with error bars
    ax.errorbar(x, y, yerr=y_err, fmt='o', color=color, 
                ecolor=color, elinewidth=1.5, capsize=3, 
                markersize=8, markeredgewidth=0, zorder=5)
    
    # Attempt curve fit
    # Initial guesses: Top=0.3, Bottom=0, EC50=-7, Slope=1
    p0 = [0.3, 0, -7, 1.0]
    
    # Handle flat lines (inactive compounds) where curve fit might fail or produce weird results
    # If the range of Y is very small, just plot a line connecting points or a flat line
    y_range = np.max(y) - np.min(y)
    
    if y_range < 0.05:
        # Likely inactive, plot straight line connecting points for visual fidelity to chart
        # Or a smooth spline. The chart shows flat lines.
        ax.plot(x, y, color=color, linewidth=2, zorder=4)
    else:
        try:
            # Constrain Hill Slope to be positive (standard dose-response)
            # Bounds: Top, Bottom, LogEC50, HillSlope
            popt, _ = curve_fit(sigmoid, x, y, p0=p0, maxfev=5000)
            
            # Generate smooth curve
            x_smooth = np.linspace(min(x), max(x), 100)
            y_smooth = sigmoid(x_smooth, *popt)
            ax.plot(x_smooth, y_smooth, color=color, linewidth=2, zorder=4)
        except:
            # Fallback if fit fails
            ax.plot(x, y, color=color, linewidth=2, zorder=4)

# ---------------------------------------------------------
# 4. Main Plotting Routine
# ---------------------------------------------------------

def main():
    # Handle output filename
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]

    datasets = parse_and_process_data()

    # Setup Figure
    fig, ax = plt.subplots(figsize=(5, 4))
    
    # Styling
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
    plt.rcParams['font.size'] = 14

    # Plot dashed zero line
    ax.axhline(0, color='black', linestyle='--', linewidth=0.8, zorder=1)

    # Plot each dataset
    for ds in datasets:
        fit_and_plot(ax, ds)

    # Axis Labels
    ax.set_ylabel('Transducer activation\n(± Δ Net BRET)', fontsize=14)
    # X-axis labels are just numbers in the image, no title "Log [M]" shown explicitly 
    # but implied. The image just shows ticks.
    
    # Axis Limits and Ticks
    ax.set_xlim(-12.5, -3.5)
    ax.set_ylim(-0.1, 0.6)
    
    ax.set_xticks([-12, -10, -8, -6, -4])
    ax.set_yticks([0.0, 0.2, 0.4, 0.6])
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add "Gq" text label
    ax.text(0.05, 0.95, 'G$_\mathrm{q}$', transform=ax.transAxes, 
            fontsize=16, verticalalignment='top')

    # Tick parameters
    ax.tick_params(axis='both', which='major', direction='in', length=4, width=1)

    # Save
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)
    print(f"Chart saved to {output_file}")

if __name__ == "__main__":
    main()