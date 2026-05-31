import sys
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

# -----------------------------------------------------------------------------
# 1. Source Data Embedding
# -----------------------------------------------------------------------------
# The full markdown table provided in the prompt is embedded here to ensure
# data integrity. The script parses this string to extract the exact values.
SOURCE_DATA = """
| Fig. 2d-k                                 | Unnamed: 1         | Unnamed: 2         | Unnamed: 3                          | Unnamed: 4         | Unnamed: 5         | Unnamed: 6         | Unnamed: 7         | Unnamed: 8         | Unnamed: 9         | Unnamed: 10        | Unnamed: 11       | Unnamed: 12                             | Unnamed: 13        | Unnamed: 14        | Unnamed: 15        | Unnamed: 16        | Unnamed: 17        | Unnamed: 18        | Unnamed: 19        | Unnamed: 20        | Unnamed: 21        | Unnamed: 22        | Unnamed: 23        | Unnamed: 24        | Unnamed: 25        | Unnamed: 26        | Unnamed: 27        | Unnamed: 28        | Unnamed: 29        | Unnamed: 30        | Unnamed: 31        | Unnamed: 32        | Unnamed: 33        | Unnamed: 34        | Unnamed: 35        |
|:------------------------------------------|:-------------------|:-------------------|:------------------------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:------------------|:----------------------------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|
| Peak intensity                            | nan                | nan                | nan                                 | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan               | nan                                     | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| Data normalized                           | F0luc-2            | F0luc-3            | F0luc-1                             | F0luc-2            | F0luc-3            | F018IL-1           | F018IL-2           | F018IL-3           | F018IL-1           | F018IL-2           | F018IL-3          | LN7 1112AR-1                            | LN7 1112AR-2       | LN7 1112AR-3       | LN7 1120BL-1       | LN7 1120BL-2       | LN7 1120BL-3       | LN7 1134BL-1       | LN7 1134BL-2       | LN7 1134BL-3       | LN8 1194BR-1       | LN8 1194BR-2       | LN8 1194BR-3       | LN8 1198AR-1       | LN8 1198AR-2       | LN8 1198AR-3       | LN8 1205BL-1       | LN8 1205BL-2       | LN8 1205BL-3       | LN9 1315BL-1       | LN9 1315BL-2       | LN9 1315BL-3       | LN9 1358IR-1       | LN9 1358IR-2       | LN9 1358IR-3       |
| Glutamate                                 | 6204616.859286747  | 6031719.639947483  | 6442731.7845764635                  | 6859345.48128456   | 6764765.683211772  | 5488684.552477316  | 5918369.731594182  | 6200610.378068406  | 4942033.196682305  | 4714026.530272788  | 5095178.247521065 | 1478381.7987170925                      | 1081751.8498301418 | 3928401.4065465294 | 3922032.1950288094 | 3110395.9232401457 | 3495866.48103521   | 2662220.3343282263 | 1907977.6288138991 | 2795104.0071977014 | 3534860.737689079  | 3006628.029078749  | 3037851.004063388  | 4632932.147138998  | 3595460.617386489  | 3721260.394931968  | 3859800.6117266854 | 3909206.586895387  | 3731577.4010725464 | 4910662.424020618  | 4314128.730348152  | 4225639.093779526  | 3720654.2353181    | 3489159.2704787264 | 3663818.5393517087 |
| Glutathione                               | 455236.17862429336 | 374854.50703331234 | 500874.4223320226                   | 466937.56824526587 | 526218.035058101   | 259322.46890358912 | 325788.12749423034 | 369825.64488186385 | 320443.13257528073 | 394602.5657019295  | 528401.2831849745 | 7253.489863424753                       | 17490.643208638903 | 207263.77376446282 | 100374.46817310246 | 150631.5739676901  | 224441.8038986802  | 129019.30608176917 | 88956.35533622571  | 233707.8500794956  | 131170.17823033908 | 133441.93648697663 | 123497.4118948018  | 229925.4941502907  | 187742.7464008859  | 177946.0039862014  | 162259.7645429363  | 155074.21131701427 | 153575.2223311653  | 284545.9510167087  | 240852.638916042   | 222731.42120165497 | 215774.5807455938  | 206790.9561720754  | 196147.94800028956 |
| Glutathione disulfide                     | 21863.712354984018 | 24875.51895888996  | 22016.88534472098                   | 25814.18797596233  | 27246.77866410799  | 18036.00175694034  | 18830.5712372072   | 19307.194332221385 | 16733.692576658657 | 16079.186418829011 | 17297.56781852486 | 5248.1946577061535                      | 4320.354879247093  | 15541.987943068676 | 13139.913582885727 | 14483.39717982995  | 13964.363297837686 | 10780.695635644199 | 8743.865759079777  | 13898.341508026346 | 10198.568416990754 | 12314.923007748532 | 11617.386425505598 | 17421.548254970465 | 15474.152131782945 | 16688.727498423043 | 14176.337430747923 | 13151.321576226404 | 15637.465129727156 | 14238.328096084297 | 13632.089870994174 | 13037.781395889358 | 14076.181229212425 | 13737.782678088366 | 14613.457395722215 |
"""

# -----------------------------------------------------------------------------
# 2. Data Parsing
# -----------------------------------------------------------------------------
def extract_data():
    """
    Parses the markdown table to extract 'Glutathione disulfide' values.
    Based on the table structure:
    - 'Parental' corresponds to columns 1-5 (F0luc samples).
    - 'LN' corresponds to columns 12-35 (LN7, LN8, LN9 samples).
    """
    # Read the markdown string into a pandas DataFrame
    # We skip the first two rows (header and separator) to get to data
    # The separator is '|', and markdown tables often have leading/trailing pipes
    df = pd.read_csv(io.StringIO(SOURCE_DATA), sep='|', header=None, skiprows=2)
    
    # Clean up column names and whitespace
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    
    # Locate the row for "Glutathione disulfide" (GSSG)
    # Column 1 contains the row labels in the parsed dataframe (index 0 is empty due to leading pipe)
    gssg_row = df[df[1] == 'Glutathione disulfide']
    
    if gssg_row.empty:
        raise ValueError("Could not find 'Glutathione disulfide' row in source data.")
    
    # Extract values. 
    # Note: In the raw markdown, columns are:
    # 0: empty (before first pipe)
    # 1: Row Label
    # 2-6: F0luc (Parental) -> Indices 2,3,4,5,6 in pandas (since col 0 is empty)
    # 7-12: F018IL (Not used in Fig 2i)
    # 13-36: LN samples -> Indices 13 to 36
    
    # Let's verify indices based on the provided table string structure:
    # | Label | Val1 | Val2 ...
    # Pandas read_csv with sep='|' will create:
    # Col 0: NaN (before first |)
    # Col 1: Label
    # Col 2: Val1
    
    # Parental (F0luc): Columns 2 to 6 inclusive
    parental_vals = gssg_row.iloc[0, 2:7].astype(float).values
    
    # LN (Lymph Node): Columns 13 to 36 inclusive
    ln_vals = gssg_row.iloc[0, 13:37].astype(float).values
    
    return parental_vals, ln_vals

# -----------------------------------------------------------------------------
# 3. Visualization Logic
# -----------------------------------------------------------------------------
def create_chart(parental, ln, output_path):
    # Set random seed for reproducible jitter
    np.random.seed(42)
    
    # Calculate statistics
    means = [np.mean(parental), np.mean(ln)]
    stds = [np.std(parental, ddof=1), np.std(ln, ddof=1)]
    
    # Plot setup
    fig, ax = plt.subplots(figsize=(2.5, 4.5)) # Tall and narrow aspect ratio
    
    # Define Colors
    color_parental_bar = '#D9D9D9'  # Light grey
    color_parental_dot = 'black'
    color_ln_bar = '#98C996'        # Muted light green
    color_ln_dot = '#2E8B57'        # Darker green (SeaGreen)
    
    bar_width = 0.6
    x_pos = [0, 1]
    
    # 1. Draw Bars
    bars = ax.bar(x_pos, means, 
                  yerr=stds, 
                  color=[color_parental_bar, color_ln_bar],
                  edgecolor='black', 
                  linewidth=0.8,
                  width=bar_width,
                  capsize=5,
                  error_kw={'elinewidth': 1, 'capthick': 1})
    
    # 2. Draw Individual Points (Swarm/Jitter)
    # Parental points
    jitter_p = np.random.normal(0, 0.06, size=len(parental))
    ax.scatter(x_pos[0] + jitter_p, parental, 
               color=color_parental_dot, s=30, zorder=3, edgecolors='none')
    
    # LN points
    jitter_ln = np.random.normal(0, 0.1, size=len(ln))
    ax.scatter(x_pos[1] + jitter_ln, ln, 
               color=color_ln_dot, s=30, zorder=3, edgecolors='none')
    
    # 3. Statistical Annotation
    # P = 2.6 x 10^-5
    # Draw line connecting the two bars
    y_max_data = max(max(parental), max(ln))
    y_line = 38000  # Position line near the top
    y_text = 39000
    
    ax.plot([0, 1], [y_line, y_line], color='black', linewidth=1)
    ax.text(0.5, y_text, r'$P = 2.6 \times 10^{-5}$', 
            ha='center', va='bottom', fontsize=10, color='black')
    
    # 4. Axis Formatting
    # Y-Axis
    ax.set_ylim(0, 42000)
    ax.set_yticks([0, 10000, 20000, 30000, 40000])
    
    # Custom formatter for scientific notation: 1 x 10^4
    def sci_formatter(x, pos):
        if x == 0:
            return '0'
        base = int(x / 10000)
        return r'${} \times 10^4$'.format(base)
    
    ax.yaxis.set_major_formatter(FuncFormatter(sci_formatter))
    ax.set_ylabel('GSSG peak intensity', fontsize=11, labelpad=5)
    
    # X-Axis
    ax.set_xticks(x_pos)
    ax.set_xticklabels(['Parental', 'LN'], rotation=45, ha='right', fontsize=11)
    
    # 5. Styling
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add Figure Label "i"
    # Positioned in figure coordinates relative to axes
    ax.text(-0.35, 1.05, 'i', transform=ax.transAxes, 
            fontsize=16, fontweight='bold', va='top', ha='left')
    
    # Adjust layout to prevent clipping
    plt.tight_layout()
    
    # Save output
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_path}")

# -----------------------------------------------------------------------------
# 4. Main Execution
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Handle command line argument for output filename
    output_filename = "output.png"
    if len(sys.argv) > 1:
        output_filename = sys.argv[1]
        
    try:
        # Extract data
        p_data, ln_data = extract_data()
        
        # Generate chart
        create_chart(p_data, ln_data, output_filename)
        
    except Exception as e:
        print(f"Error generating chart: {e}")
        sys.exit(1)