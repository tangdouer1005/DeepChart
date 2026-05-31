import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Rectangle

def generate_chart(output_filename):
    # ---------------------------------------------------------
    # 1. Source Data Embedding
    # ---------------------------------------------------------
    # We embed the raw data exactly as provided in the markdown table.
    # We only include the relevant rows for the heatmap values (headers + data).
    
    csv_data = """
RSL3|F0Luc 1|F0Luc 2|F0Luc 3|LN71112-1|LN71112-2|LN71112-3|LN71120 1|LN71120 2|LN71120 3|LN71134 1|LN71134 2|LN71134 3|LN81194 1|LN81194 2|LN81194 3|LN81198 -1|LN81198 -2|LN81198 -3|LN81205-1|LN81205-2|LN81205-3|LN91315 1|LN91315 2|LN91315 3|LN91358 1|LN91358 2|LN91358 3|F0Luc 1_H|F0Luc 2_H|F0Luc 3_H|LN71112 1_H|LN71112 2_H|LN71112 3_H|LN71120 1_H|LN71120 2_H|LN71120 3_H|LN71134 1_H|LN71134 2_H|LN71134 3_H|LN81194 1_H|LN81194 2_H|LN81194 3_H|LN81198 1_H|LN81198 2_H|LN81198 3_H|LN81205 1_H|LN81205 2_H|LN81205 3_H|LN91315 1_H|LN91315 2_H|LN91315 3_H|LN91358 1_H|LN91358 2_H|LN91358 3_H
0|107.3287077|95.22983521|97.44145707|98.51239669|103.9669421|97.52066116|93.91513211|106.4051241|99.6797438|105.7198255|97.28550654|96.99466796|99.99999999|93.31306991|93.61702128|98.96907216|99.51485749|101.5160703|100.5235602|102.3186238|97.15781601|101.8121911|97.36408567|100.8237232|101.0791367|98.56115108|100.3597122|98.36909871|99.1416309|102.4892704|103.4427966|102.6483051|93.90889831|100.6407323|101.1899314|98.16933638|97.71938523|101.1403074|101.1403074|100.2558854|105.4759468|94.26816786|99.25201381|100.1150748|100.6329114|101.1348465|101.7356475|97.12950601|101.9847328|102.1374046|95.8778626|103.125|101.9097222|94.96527778
0.25|85.47267997|85.73287077|76.10581093|48.26446281|49.58677686|42.80991736|52.36188951|54.40352282|52.48198559|29.66553563|28.356762|27.33882695|28.2674772|26.89969605|23.10030395|22.55912674|26.01576713|25.65191025|32.08676141|35.67688856|36.57442034|42.50411862|38.22075783|39.37397035|46.04316547|46.04316547|42.08633094|96.56652361|106.8669528|101.7167382|85.96398305|87.87076271|72.13983051|87.32265446|92.26544622|88.97025172|47.89291026|48.48785325|49.67773922|63.56192426|60.64483112|49.89764585|38.83774453|44.36133487|45.91484465|61.68224299|60.68090788|57.27636849|74.96183206|74.50381679|66.10687023|79.34027778|80.03472222|78.64583333
0.5|55.55073721|52.81873374|61.92541197|44.62809917|36.36363636|32.72727273|31.82546037|38.4307446|32.42594075|25.01211827|21.08579738|20.94037809|20.51671733|21.12462006|18.23708207|17.82898727|17.46513038|18.37477259|25.355273|29.1697831|26.02842184|30.80724876|28.99505766|25.70016474|37.94964029|36.33093525|37.41007194|88.71244635|93.73390558|95.40772532|70.86864407|69.75635593|60.54025424|74.69107551|80.4576659|80.04576659|41.19980169|41.64600892|46.70302429|55.88536336|59.26305015|49.74411464|26.75489068|30.37974684|30.37974684|50.46728972|47.6635514|47.06275033|68.24427481|67.02290076|54.04580153|72.56944444|73.26388889|65.79861111
1|28.62098873|30.83261058|30.70251518|30.90909091|26.28099174|19.83471074|15.01200961|16.69335468|18.85508407|18.61366941|19.77702375|18.904508|16.56534954|16.71732523|15.50151976|14.00848999|14.73620376|15.10006064|21.31637996|21.76514585|21.09199701|21.08731466|19.93410214|16.96869852|26.97841727|28.95683453|27.69784173|69.27038627|78.02575107|76.22317597|54.02542373|51.00635593|41.79025424|46.54462243|50.11441648|50.11441648|33.31680714|32.72186415|30.34209222|39.76458547|39.15046059|34.23746162|17.95166858|20.02301496|21.23130035|35.84779706|31.84245661|33.84512684|46.87022901|50.07633588|36.64122137|52.77777778|48.61111111|49.82638889
"""
    
    # P-values from the "Statistical comparisons" section of the source data
    # Mapped to the cell lines in order
    p_values = [
        "P=5.7x10⁻⁶",   # B16-F0
        "P=4.3x10⁻¹²",  # LN7 1112AR
        "P=1.5x10⁻¹²",  # LN7 1120BL
        "P=2.3x10⁻⁶",   # LN7 1134BL
        "P=5.7x10⁻¹¹",  # LN8 1194BR
        "P=1.5x10⁻⁵",   # LN8 1198AR
        "P=2.3x10⁻⁸",   # LN8 1205BL
        "P=6.3x10⁻¹¹",  # LN9 1315BL
        "P=6.4x10⁻¹²"   # LN9 1358IR
    ]

    # Cell line labels for the X-axis
    cell_lines = [
        "B16-F0", "LN7 1112AR", "LN7 1120BL", "LN7 1134BL", 
        "LN8 1194BR", "LN8 1198AR", "LN8 1205BL", "LN9 1315BL", "LN9 1358IR"
    ]

    # ---------------------------------------------------------
    # 2. Data Processing
    # ---------------------------------------------------------
    
    # Read the embedded CSV data
    df_raw = pd.read_csv(io.StringIO(csv_data), sep='|')
    
    # The raw data has triplicates for Normoxia (cols 1-27) and Hypoxia (cols 28-54)
    # We need to calculate the mean for each triplet.
    
    # Define column indices (0-based from the dataframe which has 'RSL3' as index 0 effectively)
    # Actually, 'RSL3' is the index column in the CSV string logic above? No, it's a column.
    # Let's set RSL3 (concentration) as index.
    df_raw.set_index('RSL3', inplace=True)
    
    # Initialize containers for means
    normoxia_means = pd.DataFrame()
    hypoxia_means = pd.DataFrame()
    
    # There are 9 cell lines, each has 3 replicates.
    # Normoxia: Columns 0 to 26 (27 columns)
    # Hypoxia: Columns 27 to 53 (27 columns)
    
    for i in range(9):
        # Normoxia block
        start_col_n = i * 3
        end_col_n = start_col_n + 3
        # Calculate mean across the 3 columns for this cell line
        col_name = cell_lines[i]
        normoxia_means[col_name] = df_raw.iloc[:, start_col_n:end_col_n].mean(axis=1)
        
        # Hypoxia block
        start_col_h = 27 + (i * 3)
        end_col_h = start_col_h + 3
        hypoxia_means[col_name] = df_raw.iloc[:, start_col_h:end_col_h].mean(axis=1)

    # Combine for plotting: Normoxia first, then Hypoxia
    plot_data = pd.concat([normoxia_means, hypoxia_means], axis=1)
    
    # ---------------------------------------------------------
    # 3. Plotting
    # ---------------------------------------------------------
    
    # Setup figure
    fig, ax = plt.subplots(figsize=(12, 5))
    
    # Create Heatmap
    # We use aspect='auto' to fill the space, but 'equal' squares are typical for this look.
    # Given the dimensions (4 rows, 18 cols), 'equal' might make it too wide/short.
    # We'll manually adjust aspect.
    im = ax.imshow(plot_data, cmap='viridis', vmin=20, vmax=100, aspect='equal')
    
    # ---------------------------------------------------------
    # 4. Styling and Annotations
    # ---------------------------------------------------------
    
    # Grid lines
    # We want black borders around every cell.
    # Minor ticks are often used for grid lines in imshow.
    ax.set_xticks(np.arange(plot_data.shape[1]) - 0.5, minor=True)
    ax.set_yticks(np.arange(plot_data.shape[0]) - 0.5, minor=True)
    ax.grid(which="minor", color="black", linestyle='-', linewidth=1.5)
    ax.tick_params(which="minor", bottom=False, left=False)
    
    # Axis Labels
    # Y-axis: Concentrations
    concentrations = [0, 0.25, 0.5, 1]
    ax.set_yticks(np.arange(len(concentrations)))
    ax.set_yticklabels(concentrations, fontsize=12, fontweight='bold')
    ax.set_ylabel("RSL3 (µM)", fontsize=12, fontweight='bold')
    
    # X-axis: Cell Lines
    # The labels are repeated twice.
    all_labels = cell_lines + cell_lines
    ax.set_xticks(np.arange(len(all_labels)))
    ax.set_xticklabels(all_labels, rotation=90, fontsize=12, fontweight='bold')
    
    # Remove standard axis ticks to clean up look
    ax.tick_params(axis='both', which='major', length=4, width=1.5)
    
    # Add vertical divider line between Normoxia and Hypoxia
    # The split is after the 9th column (index 8). Line should be at 8.5.
    ax.axvline(x=8.5, color='black', linewidth=2)
    
    # ---------------------------------------------------------
    # 5. Grouping Labels (21% O2 vs 1% O2)
    # ---------------------------------------------------------
    
    # We need to draw lines and text below the x-axis labels.
    # Since x-labels are rotated, they take up vertical space.
    # We use transforms to place these relative to the axes.
    
    # Coordinates for the lines (in data coordinates for x, axes coordinates for y)
    # Normoxia group (cols 0-8)
    line_y = -0.45 # Adjust based on label length
    text_y = -0.52
    
    # To make this robust, we can use the figure transform or just experiment with y-offset.
    # Given the fixed aspect ratio, data coordinates for y extend downwards.
    # The heatmap rows are 0, 1, 2, 3. 
    # The x-labels extend roughly from y=3.5 to y=6.5 in data coords.
    
    # Let's use a transform relative to the bottom of the axes
    import matplotlib.transforms as mtransforms
    trans = mtransforms.blended_transform_factory(ax.transData, ax.transAxes)
    
    # Draw lines
    # Left side (Normoxia)
    ax.plot([0, 8], [-0.55, -0.55], transform=trans, color='black', linewidth=2, clip_on=False)
    ax.text(4, -0.62, "21% O$_2$", transform=trans, ha='center', va='top', fontsize=14, fontweight='bold')
    
    # Right side (Hypoxia)
    ax.plot([9, 17], [-0.55, -0.55], transform=trans, color='black', linewidth=2, clip_on=False)
    ax.text(13, -0.62, "1% O$_2$", transform=trans, ha='center', va='top', fontsize=14, fontweight='bold')
    
    # ---------------------------------------------------------
    # 6. P-Value Annotations
    # ---------------------------------------------------------
    
    # P-values go above the Hypoxia columns (indices 9-17).
    # They are rotated 90 degrees.
    for i, p_val in enumerate(p_values):
        col_idx = 9 + i
        ax.text(col_idx, -0.6, p_val, rotation=90, ha='center', va='bottom', fontsize=11)

    # ---------------------------------------------------------
    # 7. Colorbar
    # ---------------------------------------------------------
    
    # Create an axes for the colorbar on the right
    # [left, bottom, width, height]
    # We adjust position manually to match the figure layout
    cbar_ax = fig.add_axes([0.82, 0.35, 0.02, 0.3]) # x, y, width, height
    cbar = fig.colorbar(im, cax=cbar_ax, ticks=[20, 40, 60, 80, 100])
    cbar.ax.tick_params(labelsize=12)
    # Bold tick labels
    for l in cbar.ax.yaxis.get_ticklabels():
        l.set_weight("bold")
    cbar.set_label("Relative viability (%)", fontsize=14, fontweight='bold', labelpad=10)
    
    # ---------------------------------------------------------
    # 8. The Bracket
    # ---------------------------------------------------------
    
    # There is a bracket on the right side of the main plot, grouping rows 0 and 0.25 (indices 0 and 1).
    # It sits between the plot and the colorbar.
    # Coordinates: x=17.5 (right edge of plot), y range covers row 0 and 1.
    
    bracket_x = 17.6
    bracket_h = 0.1 # width of bracket arms
    
    # Top of row 0 is -0.5, Bottom of row 1 is 1.5
    # The bracket centers on the boundary between 0 and 1? 
    # In the image, it spans the center of row 0 to center of row 1.
    # Center of row 0 = 0. Center of row 1 = 1.
    
    ax.plot([bracket_x, bracket_x + bracket_h, bracket_x + bracket_h, bracket_x], 
            [0, 0, 1, 1], color='black', linewidth=1.5, clip_on=False)

    # ---------------------------------------------------------
    # 9. Final Layout Adjustments
    # ---------------------------------------------------------
    
    # Add the 'j' label in the top left corner
    fig.text(0.02, 0.92, 'j', fontsize=24, fontweight='bold')
    
    # Adjust margins to accommodate the rotated labels and P-values
    plt.subplots_adjust(left=0.1, right=0.8, top=0.75, bottom=0.35)
    
    # Save
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    generate_chart(output_file)