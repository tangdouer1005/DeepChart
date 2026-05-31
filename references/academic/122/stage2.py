import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np

def generate_chart(output_filename):
    # 1. Source Data (Embedded exactly as provided)
    csv_data = """
| ED Fig. 6k                                                     | Unnamed: 1         | Unnamed: 2         | Unnamed: 3                               | Unnamed: 4        | Unnamed: 5         | Unnamed: 6        | Unnamed: 7         | Unnamed: 8         | Unnamed: 9         | Unnamed: 10        | Unnamed: 11        | Unnamed: 12        | Unnamed: 13        | Unnamed: 14        | Unnamed: 15        | Unnamed: 16       | Unnamed: 17        | Unnamed: 18        | Unnamed: 19        | Unnamed: 20       | Unnamed: 21       | Unnamed: 22       | Unnamed: 23        | Unnamed: 24        | Unnamed: 25        | Unnamed: 26        | Unnamed: 27        | Unnamed: 28        | Unnamed: 29        | Unnamed: 30       | Unnamed: 31        | Unnamed: 32        | Unnamed: 33        | Unnamed: 34        | Unnamed: 35       | Unnamed: 36        | Unnamed: 37       | Unnamed: 38        | Unnamed: 39       | Unnamed: 40        | Unnamed: 41       | Unnamed: 42        | Unnamed: 43       | Unnamed: 44        | Unnamed: 45       | Unnamed: 46        | Unnamed: 47        | Unnamed: 48        | Unnamed: 49        | Unnamed: 50        | Unnamed: 51        | Unnamed: 52        | Unnamed: 53        | Unnamed: 54        |
|:---------------------------------------------------------------|:-------------------|:-------------------|:-----------------------------------------|:------------------|:-------------------|:------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:------------------|:-------------------|:-------------------|:-------------------|:------------------|:------------------|:------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:------------------|:-------------------|:-------------------|:-------------------|:-------------------|:------------------|:-------------------|:------------------|:-------------------|:------------------|:-------------------|:------------------|:-------------------|:------------------|:-------------------|:------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|
| Relative viability (%)                                         | nan                | nan                | nan                                      | nan               | nan                | nan               | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan               | nan               | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| nan                                                            | Normoxia           | Normoxia           | Normoxia                                 | Normoxia          | Normoxia           | Normoxia          | Normoxia           | Normoxia           | Normoxia           | Normoxia           | Normoxia           | Normoxia           | Normoxia           | Normoxia           | Normoxia           | Normoxia          | Normoxia           | Normoxia           | Normoxia           | Normoxia          | Normoxia          | Normoxia          | Normoxia           | Normoxia           | Normoxia           | Normoxia           | Normoxia           | Hypoxia            | Hypoxia            | Hypoxia           | Hypoxia            | Hypoxia            | Hypoxia            | Hypoxia            | Hypoxia           | Hypoxia            | Hypoxia           | Hypoxia            | Hypoxia           | Hypoxia            | Hypoxia           | Hypoxia            | Hypoxia           | Hypoxia            | Hypoxia           | Hypoxia            | Hypoxia            | Hypoxia            | Hypoxia            | Hypoxia            | Hypoxia            | Hypoxia            | Hypoxia            | Hypoxia            |
| E2 uM                                                          | F0Luc 1            | F0Luc 2            | F0Luc 3                                  | LN71112-1         | LN71112-2          | LN71112-3         | LN71120 1          | LN71120 2          | LN71120 3          | LN71134 1          | LN71134 2          | LN71134 3          | LN81194 1          | LN81194 2          | LN81194 3          | LN81198 -1        | LN81198 -2         | LN81198 -3         | LN81205-1          | LN81205-2         | LN81205-3         | LN91315 1         | LN91315 2          | LN91315 3          | LN91358 1          | LN91358 2          | LN91358 3          | F0Luc 1            | F0Luc 2            | F0Luc 3           | LN71112 1          | LN71112 2          | LN71112 3          | LN71120 1          | LN71120 2         | LN71120 3          | LN71134 1         | LN71134 2          | LN71134 3         | LN81194 1          | LN81194 2         | LN81194 3          | LN81198 1         | LN81198 2          | LN81198 3         | LN81205 1          | LN81205 2          | LN81205 3          | LN91315 1          | LN91315 2          | LN91315 3          | LN91358 1          | LN91358 2          | LN91358 3          |
| 0                                                              | 105.6637168141593  | 101.30973451327434 | 93.02654867256638                        | 99.94703389830507 | 97.24576271186439  | 102.8072033898305 | 100.33955857385399 | 99.83022071307302  | 99.83022071307302  | 99.21746293245471  | 99.71169686985174  | 101.07084019769357 | 105.69185475956819 | 107.31108930323843 | 86.99705593719331  | 99.80430528375733 | 100.09784735812133 | 100.09784735812133 | 102.27272727272728 | 99.79338842975206 | 97.93388429752066 | 97.11437565582371 | 101.83630640083945 | 101.04931794333682 | 98.16933638443938  | 102.63157894736844 | 99.19908466819223  | 103.39077265147304 | 100.55586436909394 | 96.053362979433   | 100.2127659574468  | 101.70212765957447 | 98.08510638297874  | 99.13466738777717  | 95.7274202271498  | 105.137912385073   | 99.51534733441036 | 102.58481421647821 | 97.89983844911148 | 91.23883928571429  | 113.671875        | 95.08928571428571  | 98.4345648090169  | 102.75516593613023 | 98.81026925485283 | 100.24752475247526 | 98.51485148514853  | 101.23762376237624 | 101.71503957783642 | 99.93403693931398  | 98.35092348284961  | 94.39655172413794  | 103.01724137931035 | 102.58620689655172 |
| 0.25                                                           | 87.82300884955752  | 87.29203539823008  | 83.89380530973452                        | 86.44067796610169 | 87.71186440677965  | 81.9915254237288  | 71.30730050933786  | 72.22410865874363  | 76.50254668930391  | 50.288303130148265 | 52.63591433278418  | 42.998352553542006 | 41.216879293424924 | 33.70951913640824  | 30.323846908734044 | 68.98238747553816 | 74.41291585127202  | 63.845401174168295 | 78.51239669421489  | 76.2396694214876  | 79.95867768595042 | 82.00419727177334 | 75.70828961175235  | 79.17103882476388  | 78.94736842105264  | 69.6796338672769   | 74.82837528604121  | 97.88771539744302  | 98.72151195108393  | 99.05503057254029 | 105.95744680851064 | 110.00000000000001 | 103.61702127659574 | 106.27366143861546 | 105.137912385073  | 111.79015684153595 | 96.4458804523425  | 94.99192245557352  | 97.7382875605816  | 88.56026785714286  | 93.41517857142857 | 94.41964285714283  | 94.30181590482152 | 101.81590482154037 | 95.61678146524731 | 116.58415841584159 | 105.19801980198021 | 107.67326732673268 | 109.43271767810027 | 115.76517150395779 | 108.04749340369393 | 100.86206896551725 | 105.60344827586208 | 99.5689655172414   |
| 0.5                                                            | 62.76106194690266  | 67.75221238938055  | 66.4778761061947                         | 74.20550847457626 | 76.27118644067795  | 72.77542372881356 | 52.359932088285234 | 59.18505942275043  | 57.0458404074703   | 29.036243822075782 | 35.09060955518945  | 26.07084019769357  | 23.552502453385667 | 22.522080471050042 | 18.400392541707554 | 50.34246575342466 | 49.02152641878669  | 47.99412915851272  | 55.371900826446286 | 49.79338842975206 | 53.30578512396694 | 64.37565582371458 | 62.486883525708286 | 67.6810073452256   | 39.645308924485136 | 36.04118993135012  | 33.63844393592678  | 87.21511951083936  | 91.38410227904392  | 97.38743746525847 | 92.34042553191489  | 88.29787234042554  | 83.61702127659576  | 94.42942130881556  | 95.24067063277445 | 99.94591671173606  | 79.3214862681745  | 78.99838449111472  | 78.35218093699517 | 79.35267857142857  | 76.84151785714285 | 76.84151785714285  | 75.89229805886036 | 84.53350031308702  | 78.71008140262991 | 86.88118811881188  | 86.38613861386139  | 85.3960396039604   | 92.61213720316624  | 89.05013192612138  | 85.29023746701847  | 90.51724137931035  | 93.75              | 85.77586206896554  |
| 1                                                              | 55.433628318584084 | 58.513274336283196 | 58.513274336283196                       | 69.91525423728812 | 64.83050847457626  | 63.08262711864406 | 52.05432937181664  | 52.25806451612904  | 51.44312393887946  | 24.217462932454698 | 24.588138385502475 | 17.545304777594726 | 21.1972522080471   | 15.603532875368005 | 15.456329735034345 | 35.51859099804305 | 35.37181996086105  | 37.13307240704501  | 49.3801652892562   | 48.1404958677686  | 47.93388429752067 | 58.70933892969568 | 52.25603357817418  | 53.043022035676806 | 27.63157894736843  | 25.228832951945083 | 23.169336384439365 | 82.04558087826571  | 80.04446914952752  | 86.38132295719845 | 74.8936170212766   | 73.82978723404254  | 70.63829787234043  | 97.18766901027581  | 91.18442401297999 | 91.83342347214709  | 66.07431340872375 | 61.873990306946695 | 66.23586429725364 | 61.439732142857146 | 64.28571428571428 | 56.752232142857146 | 63.11834690043831 | 69.88102692548527  | 69.50532247964932 | 74.25742574257426  | 74.5049504950495   | 71.78217821782178  | 72.62532981530345  | 75.59366754617415  | 70.84432717678101  | 70.90517241379311  | 75.64655172413792  | 69.61206896551725  |
"""
    # 2. Parse Data
    # Read CSV with pipe separator
    df = pd.read_csv(io.StringIO(csv_data), sep="|", header=None)
    
    # Clean up: remove first and last columns which are empty due to markdown pipes
    df = df.iloc[:, 1:-1]
    
    # Extract the rows containing the heatmap data (Rows labeled 0, 0.25, 0.5, 1)
    # In the provided raw data, these are rows with indices 4, 5, 6, 7 (0-based index from read_csv)
    # Let's verify by checking the first column values
    data_rows = []
    concentrations = ["0", "0.25", "0.5", "1"]
    
    for idx, row in df.iterrows():
        val = str(row.iloc[0]).strip()
        if val in concentrations:
            data_rows.append(row)
            
    data_df = pd.DataFrame(data_rows)
    
    # Convert numeric columns to float
    # Columns 1 to 54 contain the numeric data
    for col in data_df.columns[1:]:
        data_df[col] = pd.to_numeric(data_df[col], errors='coerce')

    # 3. Calculate Means for Heatmap
    # Structure: 9 Cell lines, 2 Conditions (Normoxia, Hypoxia)
    # Each cell line/condition has 3 replicates.
    # Normoxia columns: 1-3, 4-6, ..., 25-27 (Indices in data_df, which align with original columns 1-27)
    # Hypoxia columns: 28-30, ..., 52-54 (Indices in data_df, which align with original columns 28-54)
    
    # Note: data_df column indices are integers. Since we dropped col 0 of original df, 
    # the indices in data_df are shifted.
    # Original "Unnamed: 1" is now at data_df column index 1 (since col 0 is the label).
    # Actually, let's check the shape.
    # data_df shape is (4, 55). Col 0 is label. Cols 1..54 are data.
    
    heatmap_data = []
    
    # Iterate through rows (concentrations)
    for _, row in data_df.iterrows():
        row_means = []
        values = row.values[1:] # Skip label
        
        # Normoxia (First 27 values, chunks of 3)
        normoxia_vals = values[0:27]
        for i in range(0, 27, 3):
            replicates = normoxia_vals[i:i+3]
            row_means.append(np.mean(replicates))
            
        # Hypoxia (Next 27 values, chunks of 3)
        hypoxia_vals = values[27:54]
        for i in range(0, 27, 3):
            replicates = hypoxia_vals[i:i+3]
            row_means.append(np.mean(replicates))
            
        heatmap_data.append(row_means)
        
    heatmap_matrix = np.array(heatmap_data)
    
    # 4. Plotting
    fig, ax = plt.subplots(figsize=(12, 5))
    
    # Cell Labels
    cell_lines = [
        "B16-F0", "LN7 1112AR", "LN7 1120BL", "LN7 1134BL", 
        "LN8 1194BR", "LN8 1198AR", "LN8 1205BL", "LN9 1315BL", "LN9 1358IR"
    ]
    # Duplicate for Hypoxia
    x_labels = cell_lines + cell_lines
    
    # Create Heatmap
    # Use viridis colormap
    cmap = plt.cm.viridis
    # Normalize based on visual inspection of the chart (Yellow=100, Dark Blue ~20-30)
    norm = mcolors.Normalize(vmin=20, vmax=100)
    
    im = ax.imshow(heatmap_matrix, cmap=cmap, norm=norm, aspect='auto')
    
    # 5. Styling
    
    # Grid lines
    # We want borders around every cell.
    # Set minor ticks to place grid lines between cells
    ax.set_xticks(np.arange(heatmap_matrix.shape[1] + 1) - 0.5, minor=True)
    ax.set_yticks(np.arange(heatmap_matrix.shape[0] + 1) - 0.5, minor=True)
    ax.grid(which="minor", color="black", linestyle='-', linewidth=1)
    ax.tick_params(which="minor", bottom=False, left=False)
    
    # Axis Ticks and Labels
    ax.set_xticks(np.arange(len(x_labels)))
    ax.set_xticklabels(x_labels, rotation=90, fontsize=10, fontweight='bold')
    
    ax.set_yticks(np.arange(len(concentrations)))
    ax.set_yticklabels(concentrations, fontsize=10, fontweight='bold')
    
    ax.set_ylabel("Erastin 2 (µM)", fontsize=12, fontweight='bold')
    
    # Remove standard spines (we used grid for borders, but let's thicken the outer frame)
    for spine in ax.spines.values():
        spine.set_linewidth(1.5)
        
    # 6. Annotations and Grouping
    
    # Vertical line separating Normoxia and Hypoxia
    # The split is after the 9th column (index 8)
    ax.axvline(x=8.5, color='black', linewidth=2)
    
    # Group Labels (21% O2 vs 1% O2)
    # We can use text or a secondary x-axis. Text is easier for custom placement.
    # Coordinates are data coordinates. Y=3.5 is the bottom row. We need to go lower.
    # Transform to axes coordinates for easier placement relative to bottom
    trans = ax.get_xaxis_transform()
    
    # Add lines below labels
    # Line for 21% O2 (Columns 0-8)
    line_y = -0.45 # Adjust based on label length
    ax.plot([0, 8], [line_y, line_y], color="black", transform=trans, clip_on=False, linewidth=2)
    ax.text(4, line_y - 0.02, "21% O$_2$", ha="center", va="top", transform=trans, fontsize=12, fontweight='bold')
    
    # Line for 1% O2 (Columns 9-17)
    ax.plot([9, 17], [line_y, line_y], color="black", transform=trans, clip_on=False, linewidth=2)
    ax.text(13, line_y - 0.02, "1% O$_2$", ha="center", va="top", transform=trans, fontsize=12, fontweight='bold')
    
    # P-Values (Top of Hypoxia section)
    # Based on the chart image and data
    p_values = [
        "P=3.8x10$^{-11}$",
        "P=6x10$^{-5}$",
        "P<1x10$^{-15}$",
        "P<1x10$^{-15}$",
        "P<1x10$^{-15}$",
        "P=5.8x10$^{-13}$",
        "P=4.4x10$^{-14}$",
        "P=3.7x10$^{-10}$",
        "P<1x10$^{-15}$"
    ]
    
    for i, p_text in enumerate(p_values):
        # x coordinate is 9 + i
        # y coordinate is -0.5 (top of the heatmap)
        ax.text(9 + i, -0.6, p_text, rotation=90, ha="center", va="bottom", fontsize=10)

    # 7. Colorbar
    # Create an inset axes or use make_axes_locatable, but standard colorbar with shrink works
    # The chart has a specific bracket style, but a standard bar is robust.
    cbar = plt.colorbar(im, ax=ax, fraction=0.02, pad=0.02)
    cbar.set_label("Relative viability (%)", fontsize=12, fontweight='bold')
    cbar.ax.tick_params(labelsize=10)
    # Bold tick labels
    for l in cbar.ax.yaxis.get_ticklabels():
        l.set_weight("bold")
        
    # Add "k" label
    ax.text(-0.1, 1.15, "k", transform=ax.transAxes, fontsize=20, fontweight='bold', va='top', ha='right')

    # Adjust layout to prevent clipping of rotated labels
    plt.subplots_adjust(bottom=0.35, top=0.8)
    
    # Save
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')

if __name__ == "__main__":
    filename = "output.png"
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    generate_chart(filename)