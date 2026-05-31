import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import matplotlib.patches as mpatches

# ---------------------------------------------------------
# 1. Source Data (Embedded)
# ---------------------------------------------------------
csv_data = """
Log [NT], M|0 µM|Unnamed: 2|Unnamed: 3|Unnamed: 4|Unnamed: 5|Unnamed: 6|1 µM|Unnamed: 8|Unnamed: 9|Unnamed: 10|Unnamed: 11|Unnamed: 12|3 µM|Unnamed: 14|Unnamed: 15|Unnamed: 16|Unnamed: 17|Unnamed: 18|10 µM|Unnamed: 20|Unnamed: 21|Unnamed: 22|Unnamed: 23|Unnamed: 24|30 µM|Unnamed: 26|Unnamed: 27|Unnamed: 28|Unnamed: 29|Unnamed: 30
nan|12-1-22|12-1-22|12-2-22|12-2-22|1-6-23|1-6-23|12-1-22|12-1-22|12-2-22|12-2-22|1-6-23|1-6-23|12-1-22|12-1-22|12-2-22|12-2-22|1-6-23|1-6-23|12-1-22|12-1-22|12-2-22|12-2-22|1-6-23|1-6-23|12-1-22|12-1-22|12-2-22|12-2-22|1-6-23|1-6-23
1e-05|-0.12501|-0.11543|-0.15495|-0.14832|-0.11541|-0.11137|-0.08634|-0.0914|-0.09776|-0.0976|-0.07446|-0.07173|-0.08575|-0.08264|-0.10806|-0.10881|-0.07253|-0.07123|-0.07877|-0.07568|-0.09212|-0.07981|-0.06454|-0.06734|-0.04873|-0.05515|-0.0544|-0.06509|-0.04587|-0.03539
1e-06|-0.11303|-0.10088|-0.1488|-0.1436|-0.11614|-0.1111|-0.08716|-0.09048|-0.10488|-0.11389|-0.08322|-0.07903|-0.08634|-0.09279|-0.10144|-0.11438|-0.07555|-0.07765|-0.07899|-0.0781|-0.09373|-0.08447|-0.0698|-0.07351|-0.04468|-0.06397|-0.06249|-0.05982|-0.04621|-0.0433
1e-07|0.008859*|0.002487*|-0.15451|-0.14176|-0.12567|-0.11085|-0.00519|-0.00425|-0.10825|-0.09687|-0.07649|-0.07325|-0.04394|-0.03601|-0.09999|-0.11395|-0.08157|-0.07591|-0.06937|-0.07426|-0.092|-0.09977|-0.06874|-0.07374|-0.07911|-0.09397|-0.06598|-0.0653|-0.05851|-0.04544
1e-08|0.005812*|-0.00252*|-0.10029|-0.09974|-0.06979|-0.02204|-0.00998|-0.01697|-0.12732|-0.11885|-0.04918|-0.0531|-0.04289|-0.05518|-0.13458|-0.12332|-0.07192|-0.0809|-0.07373|-0.08029|-0.13311|-0.12803|-0.0927|-0.08928|-0.08459|-0.09058|-0.11191|-0.10188|-0.09369|-0.0931
1e-09|0.016234*|-0.00408*|-0.00441|-0.0444|-0.01716|0.004415|-0.01403|-0.01562|-0.08819|-0.0916|-0.02873|-0.02678|-0.05576|-0.0446|-0.08681|-0.09517|-0.06098|-0.06379|-0.07342|-0.07937|-0.11328|-0.11803|-0.08464|-0.09724|-0.08554|-0.09744|-0.12495|-0.13063|-0.10121|-0.09707
1e-10|0.01268|-0.01244|0.028266|0.043423|0.010132|0.017608|-0.03351|-0.02174|-0.04225|-0.03835|-0.0323|-0.01918|-0.04487|-0.03264|-0.08057|-0.07828|-0.05333|-0.06887|-0.08224|-0.08022|-0.10941|-0.10173|-0.08606|-0.09465|-0.09168|-0.09695|-0.12157|-0.12074|-0.09896|-0.09931
1e-11|-0.00791|0.004317|-0.00549|-0.01595|-0.0026|0.01314|-0.03384|-0.03345|-0.04437|-0.04434|-0.03596|-0.0238|-0.0721|-0.04605|-0.07867|-0.07216|-0.05546|-0.06387|-0.07213|-0.09165|-0.10405|-0.12106|-0.09096|-0.09773|-0.09016|-0.09565|-0.12672|-0.1248|-0.10155|-0.10501
1e-12|-0.01603|-0.00549|-0.00765|-0.00646|-0.00886|0.002393|-0.03192|-0.03237|-0.04281|-0.04556|-0.03332|-0.03298|-0.05017|-0.04641|-0.07472|-0.06257|-0.06639|-0.06146|-0.0889|-0.07802|-0.11746|-0.10203|-0.09624|-0.09634|-0.09361|-0.09892|-0.12459|-0.12962|-0.10798|-0.10786
"""

# ---------------------------------------------------------
# 2. Data Processing
# ---------------------------------------------------------
def load_and_process_data(csv_str):
    # Read CSV, skipping the date row (row index 1)
    df = pd.read_csv(io.StringIO(csv_str), sep='|', header=0)
    df = df.drop(0).reset_index(drop=True) # Drop the date row
    
    # Clean numeric data (remove asterisks)
    for col in df.columns:
        df[col] = df[col].astype(str).str.replace('*', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Define groups based on column structure
    # 0 uM: cols 1-6 (indices)
    # 1 uM: cols 7-12
    # 3 uM: cols 13-18
    # 10 uM: cols 19-24
    # 30 uM: cols 25-30
    
    groups = {
        '0 µM':  list(range(1, 7)),
        '1 µM':  list(range(7, 13)),
        '3 µM':  list(range(13, 19)),
        '10 µM': list(range(19, 25)),
        '30 µM': list(range(25, 31))
    }
    
    processed_data = []
    
    for label, col_indices in groups.items():
        # Extract subset
        subset = df.iloc[:, col_indices]
        
        # Calculate Mean and SEM
        means = subset.mean(axis=1)
        sems = subset.sem(axis=1)
        
        # Get X values (Log [NT])
        x_vals = df.iloc[:, 0]
        
        # Store
        processed_data.append({
            'label': label,
            'x': np.log10(x_vals), # Convert to Log10
            'y': -1 * means,       # Invert Y to match chart visual (upward trend)
            'y_err': sems
        })
        
    return processed_data

# ---------------------------------------------------------
# 3. Curve Fitting (4-Parameter Logistic)
# ---------------------------------------------------------
def sigmoid(x, top, bottom, log_ec50, hill_slope):
    return bottom + (top - bottom) / (1 + 10**((log_ec50 - x) * hill_slope))

def fit_curve(x, y):
    # Initial guesses: Top=max, Bottom=min, EC50=midpoint, Slope=1
    p0 = [max(y), min(y), np.median(x), 1.0]
    try:
        popt, _ = curve_fit(sigmoid, x, y, p0=p0, maxfev=10000)
        return popt
    except:
        return None

# ---------------------------------------------------------
# 4. Plotting
# ---------------------------------------------------------
def generate_plot(data, output_path):
    fig, ax = plt.subplots(figsize=(4, 3.5), dpi=300)
    
    # Styling constants
    colors = {
        '0 µM':  '#00008B', # Dark Blue
        '1 µM':  '#D8BFD8', # Thistle (Light Purple)
        '3 µM':  '#DA70D6', # Orchid
        '10 µM': '#BA55D3', # Medium Orchid
        '30 µM': '#9400D3'  # Dark Violet
    }
    
    markers = {
        '0 µM': 'o',
        '1 µM': 's',
        '3 µM': 's',
        '10 µM': 's',
        '30 µM': 's'
    }
    
    # Plot each series
    for series in data:
        label = series['label']
        x = series['x']
        y = series['y']
        y_err = series['y_err']
        
        color = colors.get(label, 'black')
        marker = markers.get(label, 'o')
        
        # Scatter with Error Bars
        ax.errorbar(x, y, yerr=y_err, fmt=marker, color=color, 
                    ecolor=color, elinewidth=1.5, capsize=3, 
                    markersize=7, label=label, zorder=5)
        
        # Curve Fit
        popt = fit_curve(x, y)
        if popt is not None:
            x_smooth = np.linspace(min(x), max(x), 100)
            y_smooth = sigmoid(x_smooth, *popt)
            ax.plot(x_smooth, y_smooth, color=color, linewidth=1.5, zorder=4)
        else:
            # Fallback if fit fails
            ax.plot(x, y, color=color, linewidth=1.5, zorder=4)

    # Axes configuration
    ax.set_xlim(-15, -3)
    ax.set_xticks([-14, -12, -10, -8, -6, -4])
    ax.set_xticklabels([-14, -12, -10, -8, -6, -4], fontsize=14)
    
    ax.set_ylim(-0.03, 0.16) # Approximate from image
    ax.set_yticks([0, 0.1, 0.2])
    ax.set_yticklabels(['0', '0.1', '0.2'], fontsize=14)
    
    # Dashed line at y=0
    ax.axhline(0, color='black', linestyle='--', linewidth=0.8, alpha=0.7)
    
    # Spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1)
    ax.spines['bottom'].set_linewidth(1)
    ax.tick_params(width=1, length=5)

    # Title inside plot
    ax.text(0.05, 0.95, r'G$_{15}$', transform=ax.transAxes, 
            fontsize=16, verticalalignment='top')

    # Decorative Arrows (Gradient approximation)
    # Left Arrow (Upward)
    ax.annotate('', xy=(-13.5, 0.13), xytext=(-13.5, 0.01),
                arrowprops=dict(facecolor='#9400D3', edgecolor='#9400D3', 
                                width=4, headwidth=12, headlength=10))
    
    # Right Arrow (Downward)
    ax.annotate('', xy=(-3.5, 0.04), xytext=(-3.5, 0.14),
                arrowprops=dict(facecolor='#9400D3', edgecolor='#9400D3', 
                                width=4, headwidth=12, headlength=10))

    # Adjust layout
    plt.tight_layout()
    
    # Save
    plt.savefig(output_path, bbox_inches='tight')
    print(f"Chart saved to {output_path}")

# ---------------------------------------------------------
# 5. Main Execution
# ---------------------------------------------------------
if __name__ == "__main__":
    # Determine output filename
    output_filename = "output.png"
    if len(sys.argv) > 1:
        output_filename = sys.argv[1]
        
    # Process
    processed_data = load_and_process_data(csv_data)
    generate_plot(processed_data, output_filename)