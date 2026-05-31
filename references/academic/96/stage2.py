import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def generate_chart(output_filename):
    # 1. Source Data Embedding
    # We embed the raw markdown table data as a string to ensure data integrity.
    csv_data = """
| Fig. 2d-k                                 | Unnamed: 1         | Unnamed: 2         | Unnamed: 3                          | Unnamed: 4         | Unnamed: 5         | Unnamed: 6         | Unnamed: 7         | Unnamed: 8         | Unnamed: 9         | Unnamed: 10        | Unnamed: 11       | Unnamed: 12                             | Unnamed: 13        | Unnamed: 14        | Unnamed: 15        | Unnamed: 16        | Unnamed: 17        | Unnamed: 18        | Unnamed: 19        | Unnamed: 20        | Unnamed: 21        | Unnamed: 22        | Unnamed: 23        | Unnamed: 24        | Unnamed: 25        | Unnamed: 26        | Unnamed: 27        | Unnamed: 28        | Unnamed: 29        | Unnamed: 30        | Unnamed: 31        | Unnamed: 32        | Unnamed: 33        | Unnamed: 34        | Unnamed: 35        |
|:------------------------------------------|:-------------------|:-------------------|:------------------------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:------------------|:----------------------------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|
| Peak intensity                            | nan                | nan                | nan                                 | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan               | nan                                     | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| Data normalized                           | F0luc-2            | F0luc-3            | F0luc-1                             | F0luc-2            | F0luc-3            | F018IL-1           | F018IL-2           | F018IL-3           | F018IL-1           | F018IL-2           | F018IL-3          | LN7 1112AR-1                            | LN7 1112AR-2       | LN7 1112AR-3       | LN7 1120BL-1       | LN7 1120BL-2       | LN7 1120BL-3       | LN7 1134BL-1       | LN7 1134BL-2       | LN7 1134BL-3       | LN8 1194BR-1       | LN8 1194BR-2       | LN8 1194BR-3       | LN8 1198AR-1       | LN8 1198AR-2       | LN8 1198AR-3       | LN8 1205BL-1       | LN8 1205BL-2       | LN8 1205BL-3       | LN9 1315BL-1       | LN9 1315BL-2       | LN9 1315BL-3       | LN9 1358IR-1       | LN9 1358IR-2       | LN9 1358IR-3       |
| Glutamate                                 | 6204616.859286747  | 6031719.639947483  | 6442731.7845764635                  | 6859345.48128456   | 6764765.683211772  | 5488684.552477316  | 5918369.731594182  | 6200610.378068406  | 4942033.196682305  | 4714026.530272788  | 5095178.247521065 | 1478381.7987170925                      | 1081751.8498301418 | 3928401.4065465294 | 3922032.1950288094 | 3110395.9232401457 | 3495866.48103521   | 2662220.3343282263 | 1907977.6288138991 | 2795104.0071977014 | 3534860.737689079  | 3006628.029078749  | 3037851.004063388  | 4632932.147138998  | 3595460.617386489  | 3721260.394931968  | 3859800.6117266854 | 3909206.586895387  | 3731577.4010725464 | 4910662.424020618  | 4314128.730348152  | 4225639.093779526  | 3720654.2353181    | 3489159.2704787264 | 3663818.5393517087 |
| Glutathione                               | 455236.17862429336 | 374854.50703331234 | 500874.4223320226                   | 466937.56824526587 | 526218.035058101   | 259322.46890358912 | 325788.12749423034 | 369825.64488186385 | 320443.13257528073 | 394602.5657019295  | 528401.2831849745 | 7253.489863424753                       | 17490.643208638903 | 207263.77376446282 | 100374.46817310246 | 150631.5739676901  | 224441.8038986802  | 129019.30608176917 | 88956.35533622571  | 233707.8500794956  | 131170.17823033908 | 133441.93648697663 | 123497.4118948018  | 229925.4941502907  | 187742.7464008859  | 177946.0039862014  | 162259.7645429363  | 155074.21131701427 | 153575.2223311653  | 284545.9510167087  | 240852.638916042   | 222731.42120165497 | 215774.5807455938  | 206790.9561720754  | 196147.94800028956 |
| Glutathione disulfide                     | 21863.712354984018 | 24875.51895888996  | 22016.88534472098                   | 25814.18797596233  | 27246.77866410799  | 18036.00175694034  | 18830.5712372072   | 19307.194332221385 | 16733.692576658657 | 16079.186418829011 | 17297.56781852486 | 5248.1946577061535                      | 4320.354879247093  | 15541.987943068676 | 13139.913582885727 | 14483.39717982995  | 13964.363297837686 | 10780.695635644199 | 8743.865759079777  | 13898.341508026346 | 10198.568416990754 | 12314.923007748532 | 11617.386425505598 | 17421.548254970465 | 15474.152131782945 | 16688.727498423043 | 14176.337430747923 | 13151.321576226404 | 15637.465129727156 | 14238.328096084297 | 13632.089870994174 | 13037.781395889358 | 14076.181229212425 | 13737.782678088366 | 14613.457395722215 |
| nan                                       | nan                | nan                | nan                                 | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan               | nan                                     | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| nan                                       | nan                | nan                | nan                                 | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan               | nan                                     | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| Stadistical test                          | nan                | nan                | nan                                 | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan               | nan                                     | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| Table Analyzed                            | Fig. 2d            | nan                | Dunnett's multiple comparisons test | Mean diff.         | 95.00% CI of diff. | Below threshold?   | Summary            | Adjusted P Value   | A-?                | nan                | nan               | Table Analyzed                          | nan                | Fig. 2e            | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| Data sets analyzed                        | A-J                | nan                | B16-F0 vs. LN1 18IL                 | 1067485            | 8231 to 2126740    | Yes                | *                  | 0.047510547790651  | B                  | LN1 18IL           | nan               | nan                                     | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| Distribution assumption                   | Normal (Gaussian)  | nan                | B16-F0 vs. LN7 1112AR               | 4297791            | 3020282 to 5575300 | Yes                | ****               | 3.623749e-09       | C                  | LN7 1112AR         | nan               | Column B                                | nan                | Lymph node         | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| nan                                       | nan                | nan                | B16-F0 vs. LN7 1120BL               | 2951204            | 1673695 to 4228713 | Yes                | ****               | 3.594651952e-06    | D                  | LN7 1120BL         | nan               | vs.                                     | nan                | vs.                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| ANOVA summary                             | nan                | nan                | B16-F0 vs. LN7 1134BL               | 4005535            | 2728026 to 5283044 | Yes                | ****               | 1.4586543e-08      | E                  | LN7 1134BL         | nan               | Column A                                | nan                | Parental           | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| F                                         | 19.38              | nan                | B16-F0 vs. LN8 1194BR               | 3267523            | 1990013 to 4545032 | Yes                | ****               | 6.3676645e-07      | F                  | LN8 1194BR         | nan               | nan                                     | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| P value                                   | 3.640803e-09       | nan                | B16-F0 vs. LN8 1198AR               | 2477418            | 1199909 to 3754927 | Yes                | ****               | 5.3467408461e-05   | G                  | LN8 1198AR         | nan               | Unpaired t test with Welch's correction | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| P value summary                           | ****               | nan                | B16-F0 vs. LN8 1205BL               | 2627108            | 1349599 to 3904617 | Yes                | ****               | 2.2519176402e-05   | H                  | LN8 1205BL         | nan               | P value                                 | nan                | 4.96471e-10        | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| Significant diff. among means (P < 0.05)? | Yes                | nan                | B16-F0 vs. LN9 1315BL               | 1977159            | 699650 to 3254668  | Yes                | **                 | 0.001000242673301  | I                  | LN9 1315BL         | nan               | P value summary                         | nan                | ****               | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
| R squared                                 | 0.8746             | nan                | B16-F0 vs. LN9 1358IR               | 2836092            | 1558583 to 4113601 | Yes                | ****               | 6.852518877e-06    | J                  | LN9 1358IR         | nan               | Significantly different (P < 0.05)?     | nan                | Yes                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |
    """

    # 2. Data Parsing
    # Read the markdown table format
    df_raw = pd.read_csv(io.StringIO(csv_data), sep="|", header=None, skipinitialspace=True)
    
    # Clean up column names and whitespace
    df_raw = df_raw.apply(lambda x: x.str.strip() if x.dtype == "object" else x)
    
    # Extract Data Values (Row with "Glutamate")
    # The row index for "Glutamate" is 3 (0-based index in the provided snippet, but let's find it dynamically)
    glutamate_row_idx = df_raw[df_raw[1] == 'Glutamate'].index[0]
    header_row_idx = df_raw[df_raw[1] == 'Data normalized'].index[0]
    
    # Extract headers (Group names) and Values
    # Columns 2 to 36 contain the data (indices 1 to 35 in 0-based pandas, but read_csv with | creates empty first/last cols)
    # Let's inspect the dataframe structure. The markdown | creates an empty column at 0 and at the end.
    # Data starts at column 2 (index 2) which corresponds to 'Unnamed: 1' in the source.
    
    headers = df_raw.iloc[header_row_idx, 2:-1].values
    values = df_raw.iloc[glutamate_row_idx, 2:-1].values
    
    # Create a clean DataFrame for plotting
    plot_data = []
    
    # Mapping raw headers to clean group names
    # Logic: "F0luc..." -> "B16-F0", "F018IL..." -> "LN1-18IL", others are "LN..."
    # We also need to preserve the order.
    
    current_group = None
    group_map = {} # To store list of values for each group
    group_order = []
    
    for h, v in zip(headers, values):
        if pd.isna(h) or pd.isna(v):
            continue
            
        # Determine Group Name based on header prefix
        if "F0luc" in h:
            group_name = "B16-F0"
        elif "F018IL" in h:
            group_name = "LN1-18IL"
        else:
            # Extract the main part, e.g., "LN7 1112AR" from "LN7 1112AR-1"
            # Split by '-' and take everything before the last part if it ends in digit
            parts = h.rsplit('-', 1)
            group_name = parts[0].strip()
            # Fix spacing if necessary (Source has "LN7 1112AR", Image has "LN7-1112AR")
            # The source data has space, image has hyphen. Let's convert space to hyphen for LN groups
            if "LN" in group_name and " " in group_name:
                group_name = group_name.replace(" ", "-")
        
        if group_name not in group_order:
            group_order.append(group_name)
            group_map[group_name] = []
        
        group_map[group_name].append(float(v))

    # Extract P-values from the table
    # Look for rows starting with "B16-F0 vs." in column 3 (index 3)
    p_values = {}
    
    # Iterate through rows to find statistical comparisons
    for idx, row in df_raw.iterrows():
        comp = row[3] # Column 'Unnamed: 3'
        if isinstance(comp, str) and "B16-F0 vs." in comp:
            target_group = comp.split("vs.")[1].strip()
            # Convert target group format to match our keys (Space to Hyphen)
            if " " in target_group:
                target_group = target_group.replace(" ", "-")
            
            p_val_raw = row[8] # Column 'Unnamed: 8' (Adjusted P Value)
            try:
                p_values[target_group] = float(p_val_raw)
            except:
                pass

    # Global P-value (ANOVA)
    # Found in row with "P value" in column 1
    global_p_row = df_raw[df_raw[1] == 'P value'].index[0]
    global_p = float(df_raw.iloc[global_p_row, 2]) # Column 2

    # 3. Plotting
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Define Colors
    # B16-F0: Light Grey
    # LN1-18IL: Light Purple/Pink
    # Others: Green
    bar_colors = []
    point_colors = []
    
    for g in group_order:
        if g == "B16-F0":
            bar_colors.append("#D3D3D3") # Light Grey
            point_colors.append("#222222") # Dark Grey/Black
        elif g == "LN1-18IL":
            bar_colors.append("#EEAEEE") # Plum/Violet
            point_colors.append("#222222")
        else:
            bar_colors.append("#8FBC8F") # Dark Sea Green
            point_colors.append("#1E601E") # Dark Green

    # Calculate Means and SDs
    means = [np.mean(group_map[g]) for g in group_order]
    stds = [np.std(group_map[g], ddof=1) for g in group_order] # Sample SD
    x_pos = np.arange(len(group_order))
    
    # Draw Bars
    bars = ax.bar(x_pos, means, yerr=stds, align='center', alpha=1.0, 
                  color=bar_colors, edgecolor='black', linewidth=0.8, 
                  capsize=5, width=0.6, error_kw={'elinewidth': 1, 'markeredgewidth': 1})

    # Draw Scatter Points
    for i, g in enumerate(group_order):
        vals = group_map[g]
        # Add some jitter to x
        # jitter = np.random.normal(0, 0.04, size=len(vals)) 
        # To exactly match "reproduce", we usually don't use random jitter if we want pixel perfect, 
        # but standard swarm/strip plots use jitter. Let's use a fixed pattern or slight random.
        # Given the image, points are somewhat centered.
        x_vals = np.full(len(vals), x_pos[i]) + np.random.uniform(-0.1, 0.1, len(vals))
        ax.scatter(x_vals, vals, color=point_colors[i], s=30, zorder=10, edgecolor='none', alpha=0.9)

    # 4. Formatting and Annotations
    
    # Helper for scientific notation
    def format_p_value(p):
        # Format as 3.6 x 10^-9
        s = "{:.1e}".format(p)
        base, exponent = s.split('e')
        return r"$P = {} \times 10^{{{}}}$".format(base, int(exponent))

    def format_p_value_short(p):
        # For the vertical text
        if p >= 0.001:
            return r"$P = {:.3f}$".format(p).rstrip('0')
        s = "{:.1e}".format(p)
        base, exponent = s.split('e')
        return r"$P = {} \times 10^{{{}}}$".format(base, int(exponent))

    # Global P-value line
    line_y = 1.02 * 1e7 # Slightly above top tick
    ax.plot([x_pos[0], x_pos[-1]], [line_y, line_y], color='black', linewidth=1, clip_on=False)
    ax.text(np.mean(x_pos), line_y + 0.02e7, format_p_value(global_p), 
            ha='center', va='bottom', fontsize=12)

    # Vertical P-values
    # The image shows vertical text above bars starting from the 3rd bar (LN7-1112AR)
    # The text is positioned high up, aligned roughly at y=6e6 to 9e6
    
    for i, g in enumerate(group_order):
        if g in p_values:
            p_text = format_p_value_short(p_values[g])
            # Specific adjustments based on image visual
            # The text starts high and goes down (rotated 90 deg)
            # X position: center of bar
            # Y position: The image aligns them roughly at the top area.
            ax.text(x_pos[i], 8.5e6, p_text, rotation=90, ha='center', va='center', fontsize=10)

    # Axes styling
    ax.set_ylabel("Glutamate peak intensity", fontsize=12)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(group_order, rotation=45, ha='right', fontsize=11)
    
    # Y-axis ticks
    ax.set_ylim(0, 1e7)
    ax.yaxis.set_major_locator(ticker.FixedLocator([0, 5e6, 1e7]))
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: f'{int(x/1e6)}' if x==0 else f'{int(x/1e6)} $\\times 10^6$' if x < 1e7 else f'{int(x/1e7)} $\\times 10^7$'))
    # Custom formatting to match image exactly: "1 x 10^7", "5 x 10^6", "0"
    def custom_y_fmt(x, pos):
        if x == 0: return "0"
        if x == 5e6: return r"$5 \times 10^6$"
        if x == 1e7: return r"$1 \times 10^7$"
        return ""
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(custom_y_fmt))

    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add "d" label
    # Position relative to axes: negative x, top y
    ax.text(-0.15, 1.05, "d", transform=ax.transAxes, fontsize=20, fontweight='bold', va='top', ha='right')

    # Adjust layout to prevent clipping
    plt.tight_layout()
    
    # Save
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)