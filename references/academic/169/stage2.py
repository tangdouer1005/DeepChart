import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.cm import ScalarMappable

def generate_chart(output_filename):
    # 1. Load Source Data
    csv_data = """
| Country      |   Plate waste rate |        sd |
|:-------------|-------------------:|----------:|
| Brazil       |          0.147553  |   7.84035 |
| Canada       |          0.361057  |   0       |
| China        |          0.241117  |   0       |
| Croatia      |          0.155559  |   0       |
| Denmark      |          0.258459  |   8.91632 |
| Ethiopia     |          0.116182  |   0       |
| Finland      |          0.221753  |   0       |
| France       |          0.283855  |   0       |
| Germany      |          0.18335   |   0       |
| Hungary      |          0.277409  |   0       |
| India        |        nan         | nan       |
| Indonesia    |        nan         | nan       |
| Iran         |          0.201225  |   1.66657 |
| Italy        |          0.322202  |  11.8637  |
| Japan        |          0.0401832 |   5.1598  |
| Jordan       |          0.168129  |   0       |
| Latvia       |          0.319073  |   7.07593 |
| Malaysia     |        nan         | nan       |
| Philippines  |          0.0366431 |   2.6163  |
| Portugal     |          0.290535  |  19.6385  |
| Russia       |        nan         | nan       |
| South Africa |          0.463137  |  11.3842  |
| Spain        |          0.242257  |   9.88582 |
| Sweden       |          0.0834352 |   1.04935 |
| Switzerland  |        nan         | nan       |
| Thailand     |          0.124509  |   9.46044 |
| Turkey       |          0.136616  |   0       |
| UK           |          0.208682  |   7.1671  |
| USA          |          0.287659  |  12.9019  |
"""
    
    # Parse the markdown table
    # Use | as separator to correctly split columns
    df = pd.read_csv(io.StringIO(csv_data), sep='|', engine='python')
    
    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Drop empty columns (often created by leading/trailing pipes)
    df = df.dropna(axis=1, how='all')
    # Filter out any remaining unnamed columns
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Clean string data
    df['Country'] = df['Country'].astype(str).str.strip()
    
    # Convert numeric columns, coercing errors (like 'nan' string) to actual NaN
    df['Plate waste rate'] = pd.to_numeric(df['Plate waste rate'], errors='coerce')
    df['sd'] = pd.to_numeric(df['sd'], errors='coerce')
    
    # Drop rows where 'Plate waste rate' is NaN (e.g., India, Indonesia)
    df = df.dropna(subset=['Plate waste rate'])
    
    # Convert rate to percentage
    df['rate_pct'] = df['Plate waste rate'] * 100
    
    # Sort descending by rate
    df = df.sort_values('rate_pct', ascending=False).reset_index(drop=True)
    
    # 2. Setup Plot
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # 3. Color Mapping
    # Create a custom colormap matching the image (Light Cream -> Dark Copper/Brown)
    colors_list = ['#FFF5E1', '#FDD0A2', '#FDAE6B', '#D97C30', '#A65628']
    cmap = mcolors.LinearSegmentedColormap.from_list("custom_copper", colors_list)
    
    # Normalize data for color mapping (0 to 50 based on data range)
    norm = mcolors.Normalize(vmin=0, vmax=50)
    bar_colors = cmap(norm(df['rate_pct']))
    
    # 4. Draw Bars
    x = np.arange(len(df))
    ax.bar(x, df['rate_pct'], color=bar_colors, edgecolor='black', linewidth=0.7, width=0.75)
    
    # 5. Draw Error Bars
    # Only draw error bars where sd > 0
    for i in range(len(df)):
        sd_val = df.loc[i, 'sd']
        if sd_val > 0:
            ax.errorbar(x[i], df.loc[i, 'rate_pct'], yerr=sd_val, 
                        fmt='none', ecolor='#333333', elinewidth=1, capsize=3, capthick=1)

    # 6. Formatting Axes
    # X-axis
    ax.set_xticks(x)
    ax.set_xticklabels(df['Country'], rotation=90, fontsize=12, ha='center')
    ax.tick_params(axis='x', which='both', bottom=False) # Hide x ticks markers
    
    # Y-axis
    ax.set_ylabel('Plate waste rate (%)', fontsize=12, labelpad=10)
    ax.set_ylim(0, 70)
    ax.set_yticks(np.arange(0, 71, 10))
    ax.tick_params(axis='y', labelsize=11)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(0.8)
    ax.spines['bottom'].set_linewidth(0.8)

    # 7. Inset Colorbar Legend
    # Position: [x, y, width, height] in relative axes coordinates
    cax = ax.inset_axes([0.65, 0.88, 0.25, 0.05]) 
    
    sm = ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    
    cbar = fig.colorbar(sm, cax=cax, orientation='horizontal')
    
    # Colorbar formatting
    cbar.set_ticks([10, 20, 30, 40])
    cbar.ax.tick_params(labelsize=11, size=0) # size=0 hides tick marks
    cbar.outline.set_visible(False) # Remove border around colorbar
    
    # Add title above the colorbar
    ax.text(0.775, 0.96, 'Plate waste rate (%)', transform=ax.transAxes, 
            ha='center', fontsize=12)

    # Adjust layout to prevent clipping of x-labels
    plt.tight_layout()
    
    # Save
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)