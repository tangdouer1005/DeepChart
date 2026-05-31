import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def generate_chart(output_filename):
    # 1. Source Data
    # Using the exact data provided in the prompt
    csv_data = """service_type|state|fairnes_index|number_HighAging_CBG
Health Care Services|AZ|0.0413625|274
Health Care Services|CA|-0.075969|215
Health Care Services|FL|0.146886|851
Health Care Services|IL|0.423423|37
Health Care Services|MD|0.311111|40
Health Care Services|MA|-0.105105|37
Health Care Services|MI|0.00740741|30
Health Care Services|NV|0.255556|40
Health Care Services|NJ|-0.266055|109
Health Care Services|NY|0.0896921|83
Health Care Services|OH|0.160494|36
Health Care Services|PA|0.106667|50
Health Care Services|SC|-0.045045|37
Health Care Services|TX|-0.100529|63
Health Care Services|VA|0.117845|33
Health Care Services|WA|0.247312|31
Grocery and Food Supply|AZ|-0.0841503|272
Grocery and Food Supply|CA|-0.167186|214
Grocery and Food Supply|FL|0.12178|854
Grocery and Food Supply|IL|0.141141|37
Grocery and Food Supply|MD|0.19883|38
Grocery and Food Supply|MA|-0.117284|36
Grocery and Food Supply|MI|-0.103704|30
Grocery and Food Supply|NV|-0.015873|42
Grocery and Food Supply|NJ|-0.323232|110
Grocery and Food Supply|NY|-0.259259|84
Grocery and Food Supply|NC|-0.25448|31
Grocery and Food Supply|OH|0.123457|36
Grocery and Food Supply|PA|-0.12854|51
Grocery and Food Supply|SC|0.00900901|37
Grocery and Food Supply|TX|-0.107584|63
Grocery and Food Supply|VA|0.0505051|33
Grocery and Food Supply|WA|0.139785|31
Housing and Real Estate|AZ|0.0178427|274
Housing and Real Estate|CA|-0.00253678|219
Housing and Real Estate|FL|0.142783|856
Housing and Real Estate|IL|0.171171|37
Housing and Real Estate|MD|0.138889|40
Housing and Real Estate|MA|-0.135135|37
Housing and Real Estate|NV|0.0757576|44
Housing and Real Estate|NJ|-0.232143|112
Housing and Real Estate|NY|0.0534979|81
Housing and Real Estate|OH|0.117284|36
Housing and Real Estate|PA|-0.0283224|51
Housing and Real Estate|SC|-0.0643275|38
Housing and Real Estate|TX|0.00529101|63
Housing and Real Estate|VA|0.030303|33
Housing and Real Estate|WA|0.194444|32"""

    # Load data
    df = pd.read_csv(io.StringIO(csv_data), sep='|')

    # 2. Data Preprocessing
    # Map full names to abbreviations used in the chart
    name_map = {
        'Health Care Services': 'HCS',
        'Grocery and Food Supply': 'GFS',
        'Housing and Real Estate': 'HRE'
    }
    df['service_type_abbr'] = df['service_type'].map(name_map)
    
    # Define order
    order = ['HCS', 'GFS', 'HRE']

    # 3. Setup Plot
    # Set style
    sns.set_theme(style="ticks")
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
    
    fig, ax = plt.subplots(figsize=(5, 4))

    # Define custom colors to match the image
    # HCS: Muted Blue, GFS: Muted Purple, HRE: Muted Teal/Green
    palette = {
        'HCS': '#8da0cb', 
        'GFS': '#bebada', 
        'HRE': '#a6d854'  # Using a muted green similar to image
    }
    # Fine-tuning colors based on visual inspection of the provided image
    palette = {
        'HCS': '#90a4c2', # Blue-grey
        'GFS': '#b0a4c2', # Purple-grey
        'HRE': '#a4c2b6'  # Green-grey (Teal-ish)
    }

    # Create Violin Plot
    sns.violinplot(
        data=df, 
        x='service_type_abbr', 
        y='fairnes_index', 
        order=order,
        palette=palette,
        linewidth=1.2,
        saturation=0.75,
        ax=ax,
        cut=0 # Limit violin range to data range if desired, but default usually looks better. 
              # Image shows tails extending, so default cut is fine.
    )

    # 4. Annotations (Statistical Significance)
    # Coordinates for lines
    y_max = df['fairnes_index'].max()
    
    # Define heights for the brackets
    h1 = 0.78  # Height for HCS-GFS and GFS-HRE
    h2 = 0.98  # Height for HCS-HRE
    dh = 0.05  # Height of the vertical ticks
    
    # Function to draw significance bracket
    def draw_bracket(x1, x2, y, text, ax):
        # Draw the horizontal line
        ax.plot([x1, x1, x2, x2], [y - dh, y, y, y - dh], lw=0.8, c='k')
        # Add text
        ax.text((x1 + x2) * 0.5, y + 0.02, text, ha='center', va='bottom', color='k', fontsize=10)

    # Calculate P-values
    from scipy import stats
    g_hcs = df[df['service_type_abbr'] == 'HCS']['fairnes_index']
    g_gfs = df[df['service_type_abbr'] == 'GFS']['fairnes_index']
    g_hre = df[df['service_type_abbr'] == 'HRE']['fairnes_index']
    
    _, p1 = stats.ttest_ind(g_hcs, g_gfs, equal_var=False)
    _, p2 = stats.ttest_ind(g_gfs, g_hre, equal_var=False)
    _, p3 = stats.ttest_ind(g_hcs, g_hre, equal_var=False)

    # Draw brackets based on image
    draw_bracket(0, 1, h1, f"P = {p1:.3f}", ax)
    
    # GFS (1) vs HRE (2)
    draw_bracket(1, 2, h1, f"P = {p2:.3f}", ax)
    
    # HCS (0) vs HRE (2)
    draw_bracket(0, 2, h2, f"P = {p3:.3f}", ax)

    # 5. Formatting
    # Y-axis label with LaTeX for Delta F bar
    ax.set_ylabel(r'$\Delta \bar{F}$', fontsize=12)
    ax.set_xlabel('') # No X label
    
    # Ticks
    ax.set_yticks([-0.4, 0, 0.4, 0.8])
    ax.tick_params(axis='x', labelsize=11)
    ax.tick_params(axis='y', labelsize=10)
    
    # Set Y limit to accommodate annotations
    ax.set_ylim(-0.55, 1.15)

    # Add "a" label in the top left corner outside the plot
    # Using figure coordinates or axes coordinates with negative offset
    ax.text(-0.15, 1.05, 'a', transform=ax.transAxes, fontsize=16, fontweight='bold', va='bottom', ha='right')

    # Remove top and right spines
    sns.despine()

    # Adjust layout
    plt.tight_layout()

    # 6. Save Output
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    generate_chart(output_file)