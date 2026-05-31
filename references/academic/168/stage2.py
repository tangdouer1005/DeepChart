import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import numpy as np

def generate_chart(output_filename='output.png'):
    # 1. Source Data Loading
    # The data is provided as a Markdown table. We'll parse it into a pandas DataFrame.
    csv_data = """Country|Plate waste amount|sd
Brazil|46.7486|12.487
Canada|nan|nan
China|87.2099|18.7216
Croatia|nan|nan
Denmark|106.572|0
Ethiopia|35.2404|0
Finland|48.337|21.5668
France|72.1517|16.4234
Germany|nan|nan
Hungary|nan|nan
India|43.5447|0
Indonesia|39.8112|9.40734
Iran|nan|nan
Italy|55.445|34.3162
Japan|21.9694|27.4253
Jordan|73.6009|0
Latvia|86.3343|16.0132
Malaysia|8.92205|3.64655
Philippines|17.0031|15.3442
Portugal|84.9073|37.5819
Russia|42.9844|47.3762
South Africa|105.772|26.4915
Spain|75.6494|53.1506
Sweden|32.8335|10.9777
Switzerland|16.0593|6.52803
Thailand|31.2178|26.9765
Turkey|64.4366|21.9458
UK|55.5429|4.695
USA|133.085|80.0026"""

    # Read the data
    df = pd.read_csv(io.StringIO(csv_data), sep='|')

    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]

    # Convert numeric columns to float, coercing errors (like 'nan') to NaN
    df['Plate waste amount'] = pd.to_numeric(df['Plate waste amount'], errors='coerce')
    df['sd'] = pd.to_numeric(df['sd'], errors='coerce')

    # Drop rows with NaN values (as they are not plotted in the reference image)
    df = df.dropna(subset=['Plate waste amount'])

    # Sort by 'Plate waste amount' in descending order
    df = df.sort_values(by='Plate waste amount', ascending=False)

    # Reset index for clean plotting
    df = df.reset_index(drop=True)

    # 2. Setup Plotting
    # Set font style to match the sans-serif look of the chart
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Helvetica']
    plt.rcParams['font.size'] = 12

    # Create figure and axes
    fig, ax = plt.subplots(figsize=(10, 6))

    # 3. Color Mapping
    # Create a colormap that matches the green gradient
    # The gradient goes from light green to dark green based on the value
    cmap = cm.get_cmap('Greens')
    
    # Normalize the colors based on the data range, but slightly adjusted to match the visual
    # The colorbar goes up to 125, but USA is 133. We normalize to cover the full range.
    # We start the normalization slightly below 0 to ensure the lightest bar isn't pure white.
    norm = mcolors.Normalize(vmin=0, vmax=140)
    
    bar_colors = cmap(norm(df['Plate waste amount']))

    # 4. Draw Bars
    # Plot bars with error bars
    bars = ax.bar(
        df['Country'], 
        df['Plate waste amount'], 
        yerr=df['sd'],
        color=bar_colors,
        edgecolor='black', # Thin black border around bars
        linewidth=0.8,
        capsize=3,         # Width of the error bar caps
        error_kw={'elinewidth': 0.8, 'markeredgewidth': 0.8, 'ecolor': 'black'}
    )

    # 5. Formatting Axes
    
    # Y-Axis
    ax.set_ylim(0, 220)
    ax.set_yticks(range(0, 221, 20))
    ax.set_ylabel(r'Plate waste amount' + '\n' + r'($g \ capita^{-1} \ meal^{-1}$)', fontsize=14)
    
    # X-Axis
    ax.set_xticklabels(df['Country'], rotation=90, ha='center', va='top', fontsize=13)
    # Remove x-axis label (title) as it's just country names
    ax.set_xlabel('')

    # Spines (Borders)
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    # Ensure left and bottom are visible and black
    ax.spines['left'].set_color('black')
    ax.spines['bottom'].set_color('black')

    # 6. Add Colorbar Legend (Inset)
    # The legend is floating in the top right area. We use inset_axes to position it manually.
    # [x, y, width, height] in axis coordinates
    cax = ax.inset_axes([0.60, 0.85, 0.30, 0.04]) 
    
    # Create the colorbar
    cb = fig.colorbar(
        cm.ScalarMappable(norm=norm, cmap=cmap), 
        cax=cax, 
        orientation='horizontal',
        ticks=[25, 50, 75, 100, 125]
    )
    
    # Colorbar styling
    cax.set_title(r'Plate waste amount' + '\n' + r'($g \ capita^{-1} \ meal^{-1}$)', fontsize=12)
    cax.xaxis.set_ticks_position('bottom')
    cb.ax.tick_params(labelsize=10)
    
    # Remove the outline of the colorbar box to match the clean look (optional, but looks cleaner)
    cb.outline.set_linewidth(0)

    # 7. Final Layout Adjustments
    plt.tight_layout()
    
    # Save the plot
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)