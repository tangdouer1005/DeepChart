import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def generate_chart(output_filename):
    # 1. Load Source Data
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

    # Read data, handling the pipe separator and stripping whitespace
    df = pd.read_csv(io.StringIO(csv_data), sep='|')
    df.columns = df.columns.str.strip()
    df['service_type'] = df['service_type'].str.strip()
    df['state'] = df['state'].str.strip()

    # 2. Data Preprocessing
    # Filter for only the states shown in the chart: FL, AZ, CA
    target_states = ['FL', 'AZ', 'CA']
    df_filtered = df[df['state'].isin(target_states)].copy()

    # Map full service names to abbreviations used in the chart
    service_map = {
        'Health Care Services': 'HCS',
        'Grocery and Food Supply': 'GFS',
        'Housing and Real Estate': 'HRE'
    }
    df_filtered['service_abbr'] = df_filtered['service_type'].map(service_map)

    # Enforce specific order for States (Legend/Bar order) and Services (X-axis)
    # Based on the chart, the bar order within groups is FL (Blue), AZ (Pink), CA (Yellow)
    df_filtered['state'] = pd.Categorical(
        df_filtered['state'], 
        categories=['FL', 'AZ', 'CA'], 
        ordered=True
    )
    
    # Based on the chart, X-axis order is HCS, GFS, HRE
    df_filtered['service_abbr'] = pd.Categorical(
        df_filtered['service_abbr'], 
        categories=['HCS', 'GFS', 'HRE'], 
        ordered=True
    )

    # 3. Plotting
    # Define colors based on visual inspection of the provided image
    # FL: Light Blue-Grey, AZ: Light Pink-Brown, CA: Light Beige-Yellow
    custom_palette = ["#dbe5eb", "#dcc0b3", "#eaddb3"]

    # Set up the figure
    plt.figure(figsize=(6, 5))
    sns.set_style("ticks") # White background with ticks
    
    # Create the grouped bar chart
    ax = sns.barplot(
        data=df_filtered,
        x='service_abbr',
        y='fairnes_index',
        hue='state',
        palette=custom_palette,
        edgecolor='none', # No border around bars
        width=0.6,        # Adjust bar width to match spacing
        errorbar=None     # Remove error bars if any (though data is single point per group)
    )

    # 4. Styling
    # Y-Axis Label with LaTeX formatting for Delta F bar
    ax.set_ylabel(r'$\Delta \bar{F}$', fontsize=14)
    ax.set_xlabel('') # No X-axis label needed as categories are self-explanatory
    
    # Set Y-axis limits and ticks to match the image exactly
    ax.set_ylim(-0.2, 0.2)
    ax.set_yticks([-0.2, -0.1, 0.0, 0.1, 0.2])
    
    # Add the 'b' label in the top left corner
    # Using figure coordinates or axes coordinates to place it outside/corner
    ax.text(-0.12, 1.02, 'b', transform=ax.transAxes, fontsize=20, fontweight='bold', va='bottom')

    # Customize the Legend
    # Remove the title 'state', set flat frame, position bottom right
    plt.legend(frameon=False, loc='lower right', fontsize=12, handlelength=1.0, handleheight=1.0)

    # Adjust tick parameters
    ax.tick_params(axis='x', labelsize=12)
    ax.tick_params(axis='y', labelsize=10)

    # Remove top and right spines for the clean scientific look
    sns.despine()

    # Add a horizontal line at y=0 for clarity (optional but often present in such charts, 
    # though the image relies on the axis line. We ensure the 0 tick is clear).
    # The image shows a clear x-axis line at the bottom (-0.2), not necessarily at 0.
    
    # 5. Save Output
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    # Handle command line argument for output filename
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        output_file = "output.png"
    
    generate_chart(output_file)