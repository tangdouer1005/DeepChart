import sys
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from scipy import stats

# ---------------------------------------------------------
# 1. Source Data Embedding
# ---------------------------------------------------------
raw_data = """
| Electrolyte        | SSL ratio (%)                                | Li+ binding energy (eV)   | Ionic conductivity (mS cm-1)   | Initial interfacial resistance (Ohm)   |   SEI thickness (nm) |   F ratio (%) |   C ratio (%) |   O ratio (%) |   15th Rinterface (ohm) |   15th overpotential (V) |   Thickness of deposited Li (μm) |   Cycle life |
|:-------------------|:---------------------------------------------|:--------------------------|:-------------------------------|:---------------------------------------|---------------------:|--------------:|--------------:|--------------:|------------------------:|-------------------------:|---------------------------------:|-------------:|
| LiAsF6 electrolyte | 90                                           | -1.10496                  | 0.346                          | 88                                     |              9.8513  |          3.18 |         32.24 |         32.24 |                   21.22 |                    0.22  |                             11.7 |          279 |
| LiPF6 electrolyte  | 80                                           | -1.11207                  | 0.336                          | 71                                     |              8.90335 |          7.99 |         38.74 |         22.7  |                    9.5  |                    0.17  |                             12.3 |          115 |
| LiFSI electrolyte  | 78.33333                                     | -1.19801                  | 0.344                          | 47                                     |             10.2788  |          4.44 |         38.34 |         25.79 |                    6.4  |                    0.14  |                             14.2 |           71 |
| LiTFSI electrolyte | 76.66667                                     | -1.2481                   | 0.322                          | 52                                     |              9.10781 |         14.17 |         29.5  |         22.27 |                    8    |                    0.155 |                             15.8 |           53 |
| LiClO4 electrolyte | 71.66667                                     | -1.22465                  | 0.28                           | 35                                     |              8.86617 |          7.89 |         26.13 |         32.59 |                    4.3  |                    0.25  |                             15.8 |           56 |
| LiBF4 electrolyte  | 75                                           | -1.20247                  | 0.3                            | 24                                     |              9.83271 |          9.65 |         27.63 |         23.13 |                   30.1  |                    0.22  |                             16.1 |           38 |
| LiDFOB electrolyte | 70.4918                                      | -1.36423                  | 0.279                          | 50                                     |             11.7379  |          7.07 |         32.83 |         29.61 |                    6.6  |                    0.16  |                             14.9 |           45 |
| LiNO3 electrolyte  | 68.33333                                     | -1.40999                  | 0.277                          | 52                                     |             17.0074  |          7.47 |         33.73 |         24.44 |                    4.54 |                    0.18  |                             17   |           30 |
| nan                | nan                                          | nan                       | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| nan                | nan                                          | nan                       | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| Electrolyte        | CCD measurement #1 (mA cm-2)                 | measurement #2            | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiAsF6 electrolyte | 36                                           | 36                        | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiPF6 electrolyte  | 32                                           | 28                        | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiFSI electrolyte  | 29                                           | 22                        | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiTFSI electrolyte | 20                                           | 18                        | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiClO4 electrolyte | 26                                           | 23                        | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiBF4 electrolyte  | 21                                           | 17                        | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiDFOB electrolyte | 20                                           | 16                        | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiNO3 electrolyte  | 15                                           | 15                        | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| nan                | nan                                          | nan                       | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| nan                | nan                                          | nan                       | nan                            | nan                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| Electrolyte        | Average crystallite size measurement #1 (nm) | measurement #2            | measurement #3                 | measurement #4                         |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiAsF6 electrolyte | 2.9                                          | 2.6                       | 2.6                            | 2.7                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiPF6 electrolyte  | 3                                            | 3.3                       | 2.8                            | 3.3                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiFSI electrolyte  | 3.2                                          | 3.1                       | 3.3                            | 3                                      |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiTFSI electrolyte | 3.9                                          | 3.4                       | 3                              | 3.7                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiClO4 electrolyte | 4.1                                          | 4.8                       | 4.2                            | 3.8                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiBF4 electrolyte  | 3.9                                          | 4.1                       | 5.4                            | 4.4                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiDFOB electrolyte | 4.7                                          | 4.5                       | 4.9                            | 5.4                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
| LiNO3 electrolyte  | 5.2                                          | 5.2                       | 6.2                            | 5.3                                    |            nan       |        nan    |        nan    |        nan    |                  nan    |                  nan     |                            nan   |          nan |
"""

# ---------------------------------------------------------
# 2. Data Processing
# ---------------------------------------------------------

def load_and_clean_data(raw_str):
    # Read the full markdown table structure
    # We use '|' as separator and skip initial/trailing whitespace
    df_raw = pd.read_csv(io.StringIO(raw_str), sep='|', skipinitialspace=True, header=None)
    
    # Clean up column names and drop empty columns (first and last usually empty due to markdown | borders)
    df_raw = df_raw.dropna(axis=1, how='all')
    
    # The data is split into 3 sections by 'nan' rows. 
    # We identify sections by looking for the 'Electrolyte' keyword in the first valid column.
    
    # Find indices where a new table starts
    start_indices = df_raw[df_raw.iloc[:, 0].str.contains("Electrolyte", na=False)].index.tolist()
    
    # --- Table 1: Main Properties ---
    # Rows: start_indices[0] + 1 (header) to start_indices[0] + 9 (data)
    # Actually, row start_indices[0] is header, next is separator (---), but pandas read_csv might have read it as data.
    # Let's slice carefully.
    
    # Slice 1: Main Data
    # Header is at start_indices[0], Data follows immediately (ignoring the markdown separator line if present)
    # The provided raw string doesn't have the '---' line as a separate row in the CSV parse usually if not careful, 
    # but here we read with header=None.
    # Row 0 is header. Row 1 is separator line (contains '---'). Row 2-9 are data.
    
    # Helper to extract a block
    def extract_block(start_row, num_rows):
        block = df_raw.iloc[start_row:start_row+num_rows+1].copy()
        # Set header
        block.columns = block.iloc[0].str.strip()
        block = block[1:] # Drop header row
        # Drop separator row if it exists (starts with :)
        block = block[~block.iloc[:,0].str.contains('---', na=False, regex=False)]
        block = block[~block.iloc[:,0].str.contains(':', na=False, regex=False)]
        return block.reset_index(drop=True)

    # Main Table
    # Based on visual inspection of raw_data string:
    # Row 0: Header
    # Row 1: Separator
    # Row 2-9: Data
    df_main = extract_block(0, 9)
    
    # CCD Table
    # Find the row with "CCD measurement"
    ccd_start = start_indices[1]
    df_ccd_raw = extract_block(ccd_start, 9)
    
    # Crystallite Table
    cryst_start = start_indices[2]
    df_cryst_raw = extract_block(cryst_start, 9)

    # --- Process Main Table ---
    # Convert numeric columns
    cols_main = df_main.columns
    for c in cols_main:
        if c != 'Electrolyte':
            df_main[c] = pd.to_numeric(df_main[c], errors='coerce')
            
    df_main.set_index('Electrolyte', inplace=True)

    # --- Process CCD Table ---
    # Columns: Electrolyte, measurement #1, measurement #2
    # We need to average the measurements
    df_ccd = pd.DataFrame()
    df_ccd['Electrolyte'] = df_ccd_raw['Electrolyte']
    # Extract measurement columns (contain numbers)
    meas_cols = [c for c in df_ccd_raw.columns if 'measurement' in c.lower()]
    for c in meas_cols:
        df_ccd_raw[c] = pd.to_numeric(df_ccd_raw[c], errors='coerce')
    
    df_ccd['J_crit'] = df_ccd_raw[meas_cols].mean(axis=1)
    df_ccd.set_index('Electrolyte', inplace=True)

    # --- Process Crystallite Table ---
    df_cryst = pd.DataFrame()
    df_cryst['Electrolyte'] = df_cryst_raw['Electrolyte']
    meas_cols_c = [c for c in df_cryst_raw.columns if 'measurement' in c.lower()]
    for c in meas_cols_c:
        df_cryst_raw[c] = pd.to_numeric(df_cryst_raw[c], errors='coerce')
        
    df_cryst['Crystallite_size'] = df_cryst_raw[meas_cols_c].mean(axis=1)
    df_cryst.set_index('Electrolyte', inplace=True)

    # --- Merge All ---
    df_final = df_main.join(df_ccd['J_crit']).join(df_cryst['Crystallite_size'])
    
    return df_final

df = load_and_clean_data(raw_data)

# ---------------------------------------------------------
# 3. Prepare Data for Correlation Matrix
# ---------------------------------------------------------

# Map DataFrame columns to Chart Labels and desired order
# Chart Order (Top to Bottom / Left to Right):
# 1. SSL ratio
# 2. Eb (Li+ binding energy)
# 3. Sigma_ion (Ionic conductivity)
# 4. Initial R_interface
# 5. SEI thickness
# 6. F%
# 7. C%
# 8. O%
# 9. R_interface (15th cycle)
# 10. Eta_15th (Overpotential)
# 11. J_crit (CCD)
# 12. Crystallite size in SEI
# 13. Thickness of deposited Li
# 14. Cycle performance

column_mapping = {
    'SSL ratio (%)': 'SSL ratio',
    'Li+ binding energy (eV)': r'$E_{\mathrm{b}}$ Li$^{+}$ binding energy',
    'Ionic conductivity (mS cm-1)': r'$\sigma_{\mathrm{ion}}$ ionic conductivity',
    'Initial interfacial resistance (Ohm)': r'Initial $R_{\mathrm{interface}}$' + '\n' + r'initial interfacial resistance',
    'SEI thickness (nm)': 'SEI thickness',
    'F ratio (%)': r'F% F1s atomic percentage',
    'C ratio (%)': r'C% C1s atomic percentage',
    'O ratio (%)': r'O% O1s atomic percentage',
    '15th Rinterface (ohm)': r'$R_{\mathrm{interface}}$ interfacial resistance at 15th cycle',
    '15th overpotential (V)': r'$\eta_{\mathrm{15th}}$ Li||Li overpotential at 15th cycle',
    'J_crit': r'$J_{\mathrm{crit.}}$ critical current density',
    'Crystallite_size': 'Crystallite size in SEI',
    'Thickness of deposited Li (μm)': 'Thickness of deposited Li',
    'Cycle life': 'Cycle performance'
}

# Reorder and rename
ordered_keys = [
    'SSL ratio (%)',
    'Li+ binding energy (eV)',
    'Ionic conductivity (mS cm-1)',
    'Initial interfacial resistance (Ohm)',
    'SEI thickness (nm)',
    'F ratio (%)',
    'C ratio (%)',
    'O ratio (%)',
    '15th Rinterface (ohm)',
    '15th overpotential (V)',
    'J_crit',
    'Crystallite_size',
    'Thickness of deposited Li (μm)',
    'Cycle life'
]

df_chart = df[ordered_keys].copy()
df_chart.columns = [column_mapping[k] for k in ordered_keys]

# Calculate P-values
n_vars = len(df_chart.columns)
p_values = np.zeros((n_vars, n_vars))

for i in range(n_vars):
    for j in range(n_vars):
        if i == j:
            p_values[i, j] = np.nan
        else:
            # Pearson correlation
            # Note: The chart likely uses the absolute correlation strength, 
            # but displays the P-value of that correlation.
            col1 = df_chart.iloc[:, i]
            col2 = df_chart.iloc[:, j]
            # Handle potential NaNs if any (though data seems complete)
            valid = ~np.isnan(col1) & ~np.isnan(col2)
            if np.sum(valid) > 2:
                _, p = stats.pearsonr(col1[valid], col2[valid])
                p_values[i, j] = p
            else:
                p_values[i, j] = 1.0

# ---------------------------------------------------------
# 4. Plotting
# ---------------------------------------------------------

# Setup output path
output_file = "output.png"
if len(sys.argv) > 1:
    output_file = sys.argv[1]

# Define Color Map
# The chart uses a discrete log scale for P-values.
# Ranges: >0.1 (White), 0.1-0.01, 0.01-0.001, etc.
# Colors approximated from image
colors = [
    '#FFFFFF', # > 0.1 (White)
    '#DEEBF7', # 0.1 - 0.01 (Very Light Blue)
    '#C6DBEF', # 0.01 - 0.001
    '#9ECAE1', # 1e-3 - 1e-4
    '#6BAED6', # 1e-4 - 1e-5
    '#4292C6', # 1e-5 - 1e-6
    '#2171B5', # 1e-6 - 1e-7
    '#084594'  # < 1e-7 (Dark Blue)
]
# Bounds for the colormap
bounds = [1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1.0]
# We need to handle values < 1e-7. Let's extend the lower bound.
bounds = [0] + bounds 
# But matplotlib BoundaryNorm works best with specific bins.
# Let's reverse logic: High P-value = White. Low P-value = Dark.
# The legend goes 1 -> 10^-7.
cmap = mcolors.ListedColormap(colors[::-1]) # Reverse colors to match bounds low->high
# Bounds: 0, 1e-7, 1e-6, ..., 0.1, 1.0
norm_bounds = [0, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1.0]
norm = mcolors.BoundaryNorm(norm_bounds, cmap.N)

fig, ax = plt.subplots(figsize=(12, 12))

# Create the matrix data for plotting
# We only want the upper triangle.
plot_data = p_values.copy()

# Draw the heatmap
# We iterate to draw rectangles to have perfect control over borders and text
labels = df_chart.columns

# Axis settings
ax.set_xlim(0, n_vars)
ax.set_ylim(0, n_vars)
ax.set_aspect('equal')
ax.invert_yaxis() # Top is 0
ax.axis('off') # Turn off standard axis, we will add custom labels

# Font settings
font_size_val = 9
font_size_label = 11
font_family = 'sans-serif'

# Draw Grid
for i in range(n_vars): # Row
    for j in range(n_vars): # Col
        
        # Logic for Upper Triangular + Diagonal
        # The chart shows the full upper triangle including diagonal.
        if j >= i:
            val = plot_data[i, j]
            
            # Determine color
            if i == j:
                facecolor = '#808080' # Grey for diagonal
                text_str = "--"
                text_color = "black"
            else:
                # Get color from colormap
                # Handle floating point precision for boundary checks
                if val > 0.1:
                    facecolor = colors[0]
                    text_color = "black"
                elif val > 0.01:
                    facecolor = colors[1]
                    text_color = "black"
                elif val > 0.001:
                    facecolor = colors[2]
                    text_color = "black"
                elif val > 0.0001:
                    facecolor = colors[3]
                    text_color = "black"
                elif val > 0.00001:
                    facecolor = colors[4]
                    text_color = "white"
                elif val > 0.000001:
                    facecolor = colors[5]
                    text_color = "white"
                elif val > 0.0000001:
                    facecolor = colors[6]
                    text_color = "white"
                else:
                    facecolor = colors[7]
                    text_color = "white"
                
                # Format Text
                if val < 0.01:
                    text_str = "<0.01"
                else:
                    text_str = f"{val:.2f}"

            # Draw Rectangle
            rect = plt.Rectangle((j, i), 1, 1, facecolor=facecolor, edgecolor='none')
            ax.add_patch(rect)
            
            # Add Text
            ax.text(j + 0.5, i + 0.5, text_str, 
                    ha='center', va='center', 
                    color=text_color, fontsize=font_size_val, family=font_family)

# Add Labels
for i in range(n_vars):
    # Row Labels (Right aligned, to the left of the matrix)
    # Special handling for multi-line labels
    lbl = labels[i]
    ax.text(-0.1, i + 0.5, lbl, ha='right', va='center', 
            fontsize=font_size_label, family=font_family, color='black')

    # Column Labels (Vertical, above the matrix)
    # Only show columns that have data in the first row (0 to n)
    # Actually, the chart shows labels for all columns on top
    # Shorten labels for top if needed, or use same labels
    # The chart uses specific short labels on top for some:
    # e.g. "Eb", "Sigma_ion", "Initial R_interface", "SEI thickness", "F%", "C%", "O%", "R_interface", "eta_15th", "J_crit", "Crystallite...", "Thickness...", "Cycle..."
    
    # Let's map full labels to the slightly shorter top labels seen in image if necessary
    # The image actually uses almost the same text, just rotated.
    # Except "Li+ binding energy" is "Eb Li+ binding energy"
    # Let's just use the full labels defined in mapping, they match well.
    
    ax.text(i + 0.5, -0.1, lbl, ha='left', va='bottom', rotation=90,
            fontsize=font_size_label, family=font_family, color='black')

# ---------------------------------------------------------
# 5. Custom Colorbar (Legend)
# ---------------------------------------------------------
# Create a new axes for the colorbar
# Position: Left side, bottom aligned
cbar_ax = fig.add_axes([0.05, 0.05, 0.02, 0.3]) # [left, bottom, width, height]

# Create the colorbar patches
cmap_rev = mcolors.ListedColormap(colors) # White to Dark Blue
norm_rev = mcolors.BoundaryNorm(range(len(colors)+1), len(colors))
cb = plt.colorbar(plt.cm.ScalarMappable(norm=norm_rev, cmap=cmap_rev), 
             cax=cbar_ax, orientation='vertical', ticks=[])

# Custom ticks and labels for the colorbar
# The legend shows blocks corresponding to powers of 10
# 1 (top, white) down to 10^-7 (bottom, dark)
cbar_ax.invert_yaxis() # White on top
cbar_ax.set_yticks(np.arange(len(colors)) + 0.5)
cbar_ax.set_yticklabels(['1', r'$10^{-1}$', r'$10^{-2}$', r'$10^{-3}$', r'$10^{-4}$', r'$10^{-5}$', r'$10^{-6}$', r'$10^{-7}$'])
cbar_ax.tick_params(length=0) # Hide tick marks
cbar_ax.text(1.5, 8.0, 'P value', va='center', ha='left', fontsize=12, family=font_family)

# Add "b" label
fig.text(0.02, 0.95, 'b', fontsize=24, fontweight='bold', family=font_family)

# Adjust layout to accommodate labels
# Since we used fixed coordinates and turned off axis, we rely on figure size and placement.
# The main matrix is at (0,0) to (14,14).
# We need to shift the view to include labels.
ax.set_xlim(-6, 15) # Space for left labels
ax.set_ylim(15, -6) # Space for top labels

plt.savefig(output_file, bbox_inches='tight', dpi=300)