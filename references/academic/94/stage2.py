import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io

def generate_chart(output_filename):
    # 1. Source Data Loading
    # Using the exact data provided in the markdown table.
    # We only extract the raw measurement columns (A-J) and the relevant headers.
    csv_data = """
B16-F0,LN1 18IL,LN7 1112AR,LN7 1120BL,LN7 1134BL,LN8 1194BR,LN8 1198AR,LN8 1205BL,LN9 1315BL,LN9 1358IR
0.8299296674003414,1.928546998833788,0.8025826043362723,2.222764945615544,0.37278141648377583,0.6090772699389065,0.5369301638703191,0.13994083686105493,0.5357799907267852,0.5369725529955741
1.0355057637490246,2.146987063268871,0.5586761586545418,1.625153697906596,0.21125251548675206,0.5130045874571015,0.589444402175406,0.10597787396603812,0.7520433000113403,0.735953968614233
1.134564568850634,1.1800532877406624,0.981485217508094,2.496864417961382,0.2840339839626573,0.618016249272412,0.43573465345652695,0.18815322961925368,0.8726564170965828,0.5482852964188359
1.067366156351031,1.139263648683155,0.6828174503771713,1.1651481165731932,0.4938553059954519,0.555341273528883,0.5996181837280969,0.2869213153964222,0.20897275168862095,0.5125056222512814
1.0214732863448737,1.296021888185411,0.8991676521394686,1.54030017361637,0.9079694495974822,0.9781711654635805,0.8639109240152595,0.8911277607591113,1.2240086468234774,1.0522782074088821
0.9111623735995769,0.9354895635383239,0.8518380020755709,1.1177187016815318,0.6916331033068995,0.45367395258469567,1.2218269477581314,0.40339876934736785,0.3036788001925242,0.5448505274112878
0.7882105310868032,1.446763836975741,,,,,,,,
0.9514894525471388,1.7365729543386705,,,,,,,,
1.2603002786479676,1.3206856278467825,,,,,,,,
1.151744305174724,1.5762741597162917,,,,,,,,
0.8150691363293474,1.2557090017283161,,,,,,,,
1.033186952433866,1.2621057179113198,,,,,,,,
1.0000178133667066,1.112049159854708,,,,,,,,
1.0001977922468785,1.3090844939710062,,,,,,,,
1.000081804170821,1.1182582188956112,,,,,,,,
"""
    df = pd.read_csv(io.StringIO(csv_data))

    # 2. Data Preparation
    # Calculate Mean and Std Dev for bars and error bars
    means = df.mean()
    stds = df.std()
    
    # Rename columns to match the chart labels (adding hyphens)
    # Chart labels: B16-F0, LN1-18IL, LN7-1112AR, etc.
    # Data headers: B16-F0, LN1 18IL, LN7 1112AR, etc.
    new_labels = []
    for col in df.columns:
        if " " in col:
            new_labels.append(col.replace(" ", "-"))
        else:
            new_labels.append(col)
    
    # 3. Plot Setup
    fig, ax = plt.subplots(figsize=(7, 6))
    
    # Define Colors
    # Bar 1: Gray, Bar 2: Pink/Lilac, Bars 3-10: Green
    bar_colors = ['#D9D9D9', '#EAB8F5'] + ['#96D691'] * 8
    
    # Define Point Colors
    # Bar 1-2: Black, Bars 3-10: Darker Green
    point_colors = ['black', 'black'] + ['#4A8A45'] * 8

    x_pos = np.arange(len(means))
    
    # 4. Draw Bars
    bars = ax.bar(x_pos, means, yerr=stds, align='center', 
                  color=bar_colors, edgecolor='black', linewidth=1.0,
                  capsize=4, error_kw={'elinewidth': 1, 'capthick': 1})

    # 5. Draw Scatter Points (Jittered)
    np.random.seed(42) # For reproducible jitter
    jitter_strength = 0.15
    
    for i, col in enumerate(df.columns):
        data = df[col].dropna()
        # Create jittered x coordinates
        x_jitter = np.random.normal(i, 0.06, size=len(data))
        # Clamp jitter to stay within bar width roughly
        x_jitter = np.clip(x_jitter, i - 0.2, i + 0.2)
        
        ax.scatter(x_jitter, data, color=point_colors[i], s=25, zorder=10, edgecolors='none')

    # 6. Annotations (P-values)
    # Based on the image and source data column 18
    p_values = {
        2: "P = 0.6982",      # LN7-1112AR
        3: r"P = 4.8 $\times$ 10$^{-5}$", # LN7-1120BL
        4: "P = 0.0051",      # LN7-1134BL
        5: "P = 0.0688",      # LN8-1194BR
        6: "P = 0.2721",      # LN8-1198AR
        7: "P = 0.0001",      # LN8-1205BL
        8: "P = 0.1122",      # LN9-1315BL
        9: "P = 0.1231"       # LN9-1358IR
    }

    # Add vertical P-values above bars
    y_max_limit = 4.0
    for idx, text in p_values.items():
        # Position text slightly above the error bar
        # We pick a fixed height relative to the plot or dynamic based on bar?
        # The chart aligns them somewhat, but they follow the bar height loosely.
        # Actually, in the chart, they are all aligned at different heights but vertical.
        # Let's place them a bit above the error bar.
        
        y_pos = means.iloc[idx] + stds.iloc[idx] + 0.2
        
        # Adjust specific heights to match visual layout if needed, 
        # but dynamic placement is safer.
        # The chart shows them starting at varying heights.
        
        ax.text(idx, y_pos, text, rotation=90, ha='center', va='bottom', fontsize=10)

    # 7. Global Statistical Annotation
    # Line spanning all bars
    line_y = 4.15
    ax.plot([0, 9], [line_y, line_y], color='black', linewidth=1)
    ax.text(4.5, line_y + 0.05, r"$P = 2.2 \times 10^{-13}$", ha='center', va='bottom', fontsize=12)

    # 8. Formatting
    
    # X-Axis
    ax.set_xticks(x_pos)
    ax.set_xticklabels(new_labels, rotation=45, ha='right', fontsize=12)
    
    # Y-Axis
    ax.set_ylabel("Relative ACSL4 levels", fontsize=12)
    ax.set_ylim(0, 4.5) # Adjust to fit the top annotation
    ax.set_yticks(np.arange(0, 4.1, 0.5))
    ax.tick_params(axis='y', labelsize=12)
    
    # Spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Figure Label "k"
    # Placed in the top left corner, outside the axes usually
    fig.text(0.02, 0.95, "k", fontsize=24, fontweight='bold')

    # Layout adjustment to prevent clipping of x-labels
    plt.tight_layout()
    
    # Adjust top margin for the global p-value
    plt.subplots_adjust(top=0.85, bottom=0.25, left=0.15)

    # 9. Save
    plt.savefig(output_filename, dpi=300)

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    generate_chart(output_file)