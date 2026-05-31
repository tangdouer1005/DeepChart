import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# ---------------------------------------------------------
# 1. Source Data Embedding
# ---------------------------------------------------------
csv_data = """Compound,Vehicle,Unnamed: 2,Unnamed: 3,Unnamed: 4,Unnamed: 5,Unnamed: 6,Unnamed: 7,Unnamed: 8,Unnamed: 9,Vehicle + 100 nM NT,Unnamed: 11,Unnamed: 12,Unnamed: 13,Unnamed: 14,Unnamed: 15,Unnamed: 16,Unnamed: 17,Unnamed: 18,SBI-553 + 100 nM NT,Unnamed: 20,Unnamed: 21,Unnamed: 22,Unnamed: 23,Unnamed: 24,Unnamed: 25,Unnamed: 26,Unnamed: 27,SR14 + 100 nM NT,Unnamed: 29,Unnamed: 30,Unnamed: 31,Unnamed: 32,Unnamed: 33,Unnamed: 34,Unnamed: 35,Unnamed: 36
nan,3/29/24,3/29/24,3/29/24,3/29/24 #2,3/29/24 #2,3/29/24 #2,3/15/24,3/15/24,3/15/24,3/29/24,3/29/24,3/29/24,3/29/24 #2,3/29/24 #2,3/29/24 #2,3/15/24,3/15/24,3/15/24,3/29/24,3/29/24,3/29/24,3/29/24 #2,3/29/24 #2,3/29/24 #2,3/15/24,3/15/24,3/15/24,3/29/24,3/29/24,3/29/24,3/29/24 #2,3/29/24 #2,3/29/24 #2,3/15/24,3/15/24,3/15/24
3e-06,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,0.0237167167*,0.0184386004*,0.02330029487,0.02912048179,0.02564827244,0.02343690857,0.0257143937,0.02320762774,0.03538207626,nan,nan,nan,nan,nan,nan,nan,nan,nan
1e-06,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,0.03750789843,0.02461968203,0.02361144357,0.03944354898,0.02885491301,0.02267562316,0.03536982371,0.02637872062,0.02998092636,nan,nan,nan,nan,nan,nan,nan,nan,nan
3e-07,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,0.01772792148,0.02885072186,0.03477926179,0.03200164886,0.02164380733,0.02465939072,0.0273727136,0.03151017894,0.03492496203,nan,nan,nan,nan,nan,nan,nan,nan,nan
1e-07,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,0.02768322358,0.02648855554,0.03990159729,0.02054370908,0.0246913736,0.02882308525,0.0259830471,0.0325810303,0.03405350462,nan,nan,nan,nan,nan,nan,nan,nan,nan
3e-08,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,0.02177107924,0.01658185402,0.03225073512,0.02170705279,0.02779036092,0.02875504571,0.02906712951,0.03106661754,0.04035930433,nan,nan,nan,nan,nan,nan,nan,nan,nan
1e-08,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,0.02472270725,0.02279129809,0.03463562017,0.02229650198,0.01864525965,0.02146662057,0.03165422784,0.02816028302,0.03239051284,nan,nan,nan,nan,nan,nan,nan,nan,nan
3e-09,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,0.01544192286,0.01687438814,0.02575574404,0.01847516748,0.01975255455,0.01612770062,0.02620887921,0.03274125771,0.02840080891,nan,nan,nan,nan,nan,nan,nan,nan,nan
1e-11,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,0.007188445104,0.01430723297,0.01961487601,0.01390322732,0.01278852388,0.01205829996,0.01746867944,0.0163298947,0.01560372567,nan,nan,nan,nan,nan,nan,nan,nan,nan
nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan
0.0001,0.0009864990007*,0.001745363314*,0.006177547366*,0.004305464603*,0.0005196975477*,0.00126557484*,0.003390877701*,0.004673038715*,0.0008750172885*,0.01560130729*,0.01382741186*,0.01231447406*,0.01499413268*,0.01506425401*,0.01789561938*,0.01024613621*,0.01077113366*,0.01254679898,nan,nan,nan,nan,nan,nan,nan,nan,nan,0.01736629879*,0.006787903995*,0.004451147135*,0.01098538767*,0.003533337705*,0.01237002778*,0.002937753116*,0.002264130414*,0.003789610174
1e-05,0.0008919789861,0.01004563499,0.002863534461,0.00120104637,-0.001746740573,0.008809669403,0.00283765486,0.0007933378576,0.00295290809,0.01566511986,0.02454023494,0.01562450888,0.02170524445,0.01496406426,0.01311157974,0.01470579814,0.01718822122,0.01966224047,nan,nan,nan,nan,nan,nan,nan,nan,nan,0.006300980763,0.01445128227,-0.002861001201,0.0005158872742,0.003446374664,0.004210354862,0.008818107974,0.005243292829,0.006778434363
1e-06,-0.002511250585,0.0115281637,0.007451513136,4.296608718e-06,0.002165030734,0.003934321082,-0.003069694523,0.006099484597,0.003161504749,0.02107307509,0.02312131628,0.01585223934,0.01238641679,0.01431408536,0.008090036851,0.007425663741,0.01639297436,0.01156616572,nan,nan,nan,nan,nan,nan,nan,nan,nan,0.0102627888,0.01059307848,0.01250043745,0.003496801529,0.005960181286,0.0002347375426,0.007709583386,0.002489886658,0.004003953692
1e-07,0.001736625842,0.01645194085,0.01060598314,0.00147482802,0.004424238312,-0.0003195015708,0.0007939131752,0.004372653712,0.005775769877,0.02788681741,0.01202647072,0.0208366328,0.01942812423,0.01522931422,0.01340528818,0.01560181047,0.01398575959,0.01767230734,nan,nan,nan,nan,nan,nan,nan,nan,nan,0.008522232466,0.009359425978,0.01136000041,0.007340163001,0.004336841242,0.002545645439,0.01357615675,0.006962771438,0.008101839753
1e-08,0.002549735734,0.009643207659,0.003450067395,0.01040145678,-0.009843135169,0.01350550276,-0.001362929915,0.001062834661,0.005782152724,0.0191082155,0.01641627445,0.01886407555,0.02498398035,0.01994201193,0.02130339552,0.01615171794,0.01869076285,0.02009679568,nan,nan,nan,nan,nan,nan,nan,nan,nan,0.003168897268,0.008101221893,0.01026122053,0.01096934363,0.009283429298,0.01525223433,0.01491864771,0.01092154983,0.01103102431
1e-09,0.005252772641,0.009801979436,-0.0001484835803,0.007503152166,-0.002552602571,0.005546485219,-0.002253306484,0.004463349946,0.004007413902,0.02046217831,0.01594880085,0.01828244271,0.01848551787,0.01003912579,0.02050497594,0.01667507971,0.01782489739,0.02006081584,nan,nan,nan,nan,nan,nan,nan,nan,nan,0.01030545396,0.01699493339,0.0108749609,0.01272295863,0.006378855037,0.008934226283,0.01866326513,0.01288811925,0.01667731132
1e-10,0.005282640564,0.002204823576,0.003117346173,0.003679603314,-0.00164675179,0.005388756614,0.0002870729759,0.003185047687,0.003473107725,0.01737749348,0.01513316539,0.01725334368,0.02099833712,0.01226342842,0.01425837179,0.01591307593,0.01684376994,0.01578673868,nan,nan,nan,nan,nan,nan,nan,nan,nan,0.01076521985,0.01225416402,0.01246681658,0.01057153881,0.01024732037,0.01065144579,0.01575356544,0.01317147149,0.01339874612
1e-11,0.005722786893,0.006331751293,0.004921292393,0.008625682025,-0.001142384929,0.002232291916,0.002721169625,0.00265685332,0.001349394732,0.01809178763,0.01684993926,0.01895675573,0.01053163313,0.008968200162,0.009886971914,0.01358853719,0.02060621052,0.01954807777,nan,nan,nan,nan,nan,nan,nan,nan,nan,0.01710170478,0.02085809905,0.01627080207,0.01254381792,0.00699290328,0.01048743704,0.01604709897,0.01216309114,0.02187649547
"""

# ---------------------------------------------------------
# 2. Data Processing
# ---------------------------------------------------------
def clean_value(val):
    if pd.isna(val):
        return np.nan
    if isinstance(val, str):
        val = val.replace('*', '')
        try:
            return float(val)
        except ValueError:
            return np.nan
    return float(val)

def process_data():
    # Read CSV
    df = pd.read_csv(io.StringIO(csv_data), header=0)
    
    # The data is split into two blocks.
    # Block 1: Rows 1-8 (indices 1-8 in 0-based index after header, but row 0 is dates)
    # Actually, let's inspect the dataframe structure.
    # Row 0 is dates.
    # Rows 1-8 are the first block of concentrations.
    # Row 9 is nan separator.
    # Rows 10-17 are the second block.
    
    # Define column ranges
    # Vehicle: cols 1-9 (indices 1-9)
    # Vehicle + NT: cols 10-18 (indices 10-18)
    # SBI + NT: cols 19-27 (indices 19-27)
    # SR14 + NT: cols 28-36 (indices 28-36)
    
    groups = {
        'SBI-553 + 100 nM NT': {'rows': range(1, 9), 'cols': range(19, 28), 'color': '#bf2bb9', 'marker': 'o'},
        'Vehicle + 100 nM NT': {'rows': range(10, 18), 'cols': range(10, 19), 'color': '#0000b3', 'marker': 'o'},
        'SR14 + 100 nM NT':    {'rows': range(10, 18), 'cols': range(28, 37), 'color': '#f58025', 'marker': 'o'},
        'Vehicle':             {'rows': range(10, 18), 'cols': range(1, 10),   'color': '#808080', 'marker': 'o'}
    }
    
    processed_groups = {}
    
    for name, config in groups.items():
        rows = config['rows']
        cols = config['cols']
        
        x_vals = []
        y_means = []
        y_sems = []
        
        for r in rows:
            # Get concentration from column 0
            conc_str = df.iloc[r, 0]
            conc = clean_value(conc_str)
            
            # Get values for the group
            vals = []
            for c in cols:
                val = clean_value(df.iloc[r, c])
                if not np.isnan(val):
                    vals.append(val)
            
            if vals:
                x_vals.append(np.log10(conc))
                y_means.append(np.mean(vals))
                y_sems.append(np.std(vals, ddof=1) / np.sqrt(len(vals)))
        
        processed_groups[name] = {
            'x': np.array(x_vals),
            'y': np.array(y_means),
            'yerr': np.array(y_sems),
            'color': config['color'],
            'marker': config['marker']
        }
        
    return processed_groups

# ---------------------------------------------------------
# 3. Curve Fitting (4PL)
# ---------------------------------------------------------
def sigmoid(x, bottom, top, log_ec50, hill_slope):
    return bottom + (top - bottom) / (1 + 10**((log_ec50 - x) * hill_slope))

def fit_curve(x, y):
    # Initial guesses based on data range
    try:
        p0 = [min(y), max(y), np.median(x), 1.0]
        # Constrain hill slope to be reasonable (-5 to 5) to prevent wild oscillations
        # Constrain EC50 to be within x range
        bounds = ([-np.inf, -np.inf, min(x)-2, -10], [np.inf, np.inf, max(x)+2, 10])
        popt, _ = curve_fit(sigmoid, x, y, p0=p0, bounds=bounds, maxfev=10000)
        return popt
    except:
        return None

# ---------------------------------------------------------
# 4. Plotting
# ---------------------------------------------------------
def generate_plot(output_filename):
    data = process_data()
    
    fig, ax = plt.subplots(figsize=(5, 4))
    
    # Plot order: Grey, Orange, Blue, Purple (based on visual layering)
    order = ['Vehicle', 'SR14 + 100 nM NT', 'Vehicle + 100 nM NT', 'SBI-553 + 100 nM NT']
    
    for name in order:
        group = data[name]
        x = group['x']
        y = group['y']
        yerr = group['yerr']
        color = group['color']
        
        # Plot points with error bars
        ax.errorbar(x, y, yerr=yerr, fmt='o', color=color, ecolor=color, 
                    capsize=3, markersize=8, label=name, zorder=5)
        
        # Fit and plot curve
        popt = fit_curve(x, y)
        if popt is not None:
            x_smooth = np.linspace(min(x)-0.5, max(x)+0.5, 200)
            y_smooth = sigmoid(x_smooth, *popt)
            ax.plot(x_smooth, y_smooth, color=color, linewidth=2, zorder=4)
        else:
            # Fallback: simple interpolation if fit fails (unlikely for these datasets)
            ax.plot(x, y, color=color, linewidth=2, zorder=4)

    # Styling
    ax.axhline(0, color='black', linestyle=':', linewidth=1.5, zorder=1)
    
    # Axis limits and ticks
    ax.set_xlim(-12, -3.5)
    ax.set_xticks([-12, -10, -8, -6, -4])
    
    ax.set_ylim(-0.005, 0.033)
    ax.set_yticks([0, 0.01, 0.02, 0.03])
    
    # Labels
    ax.set_xlabel('log[Compound] (M)', fontsize=12)
    ax.set_ylabel('Mini G$_{12}$ recruitment\n($\Delta$ Net BRET)', fontsize=12)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Tick parameters
    ax.tick_params(axis='both', which='major', labelsize=11, direction='in', length=5)
    
    # Tight layout
    plt.tight_layout()
    
    # Save
    plt.savefig(output_filename, dpi=300)

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    generate_plot(output_file)