import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def generate_chart(output_filename='output.png'):
    # 1. Source Data
    # Using the provided markdown table converted to a CSV string
    csv_data = """Site_type,Site_topography,N_stations,PM_size,N_samples,OP_DTT_m_mean,OP_DTT_m_SEM,PM_mass_mean,PM_mass_SEM
nan,nan,nan,nan,nan,nmol min-1 µg-1,nmol min-1 µg-1,µg m-3,µg m-3
Industrial,nan,6,PM10,696,0.07,0.01,20.22,1.78
Rural,nan,9,PM10,1252,0.07,0.01,15.52,1.0
Suburban,nan,3,PM10,695,0.09,0.02,20.73,6.58
Traffic,nan,4,PM10,1140,0.12,0.01,22.44,3.26
Urban,nan,20,PM10,4243,0.1,0.0,21.91,0.99
"Urban, Industrial, Suburban, Rural",Valley,9,PM10,2572,0.1,0.01,20.34,2.10"""

    # 2. Data Processing
    # Read CSV, skipping the unit row (row index 1)
    df = pd.read_csv(io.StringIO(csv_data), header=0)
    
    # Drop the unit row (index 0 in the dataframe after header load)
    df = df.drop(0)
    
    # Convert numeric columns to float
    numeric_cols = ['OP_DTT_m_mean', 'OP_DTT_m_SEM', 'PM_mass_mean', 'PM_mass_SEM']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col])

    # Define mapping for labels and colors based on the chart visual analysis
    # Logic: Map Site_type/Topography to the specific labels (R, I, SU, T, U, (V))
    
    plot_config = []
    
    for _, row in df.iterrows():
        site_type = row['Site_type']
        topography = row['Site_topography']
        
        label = ""
        color = ""
        text_offset = (0, 0) # (x, y) offset for text
        ha = 'center'
        va = 'center'
        
        if topography == 'Valley':
            label = '(V)'
            color = '#bdbdbd' # Grey
            text_offset = (-1.5, 0.003)
            ha = 'right'
            va = 'bottom'
        elif 'Industrial' in site_type and ',' not in site_type:
            label = 'I'
            color = '#ea8c9f' # Pinkish Red
            text_offset = (-0.5, -0.003)
            ha = 'right'
            va = 'top'
        elif 'Rural' in site_type and ',' not in site_type:
            label = 'R'
            color = '#d67fe2' # Orchid/Purple
            text_offset = (-0.5, -0.003)
            ha = 'right'
            va = 'top'
        elif 'Suburban' in site_type and ',' not in site_type:
            label = 'SU'
            color = '#6fa8dc' # Light Blue
            text_offset = (-1.0, 0.003)
            ha = 'right'
            va = 'bottom'
        elif 'Traffic' in site_type:
            label = 'T'
            color = '#cdae63' # Gold/Mustard
            text_offset = (0.8, 0.003)
            ha = 'left'
            va = 'bottom'
        elif 'Urban' in site_type and ',' not in site_type:
            label = 'U'
            color = '#7bc068' # Green
            text_offset = (0.8, 0.003)
            ha = 'left'
            va = 'bottom'
            
        plot_config.append({
            'x': row['PM_mass_mean'],
            'y': row['OP_DTT_m_mean'],
            'xerr': row['PM_mass_SEM'],
            'yerr': row['OP_DTT_m_SEM'],
            'label': label,
            'color': color,
            'text_offset': text_offset,
            'ha': ha,
            'va': va
        })

    # 3. Plotting
    fig, ax = plt.subplots(figsize=(3.5, 6)) # Portrait aspect ratio

    # Set font style to match scientific publication (sans-serif)
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']

    for item in plot_config:
        # Plot Error Bars
        # Using a lighter alpha for the lines to match the visual style
        ax.errorbar(
            x=item['x'], 
            y=item['y'], 
            xerr=item['xerr'], 
            yerr=item['yerr'], 
            fmt='o', 
            color=item['color'],
            ecolor=item['color'],
            elinewidth=2, # Thicker error bars
            capsize=0,    # No caps on error bars
            markersize=8,
            alpha=0.9,    # Slight transparency for overlap
            zorder=2
        )
        
        # Add Text Labels
        # We apply the manual offsets defined above to position text like the image
        ax.text(
            item['x'] + item['text_offset'][0], 
            item['y'] + item['text_offset'][1], 
            item['label'], 
            fontsize=12, 
            color='black',
            ha=item['ha'],
            va=item['va'],
            zorder=3
        )

    # 4. Styling and Formatting

    # Axis Limits (approximate from visual inspection)
    ax.set_xlim(13, 28)
    ax.set_ylim(0.055, 0.13)

    # Axis Labels with LaTeX formatting for units
    # Note: Using raw strings for LaTeX
    ax.set_xlabel(r'PM$_{10}$ ($\mu$g m$^{-3}$)', fontsize=12, labelpad=10)
    ax.set_ylabel(r'OP$_{\mathrm{m}}^{\mathrm{DTT}}$ (nmolDTT min$^{-1}$ $\mu$g$^{-1}$)', fontsize=12, labelpad=10)

    # Ticks
    ax.xaxis.set_major_locator(ticker.MultipleLocator(5)) # 15, 20, 25
    ax.yaxis.set_major_locator(ticker.MultipleLocator(0.01)) # 0.06, 0.07...
    
    # Tick params
    ax.tick_params(axis='both', which='major', labelsize=11, length=6, direction='out')

    # Spines (Remove top and right)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Adjust spine thickness
    ax.spines['left'].set_linewidth(0.8)
    ax.spines['bottom'].set_linewidth(0.8)

    # Add the figure label "b" in the top left corner
    # Positioned relative to axes coordinates
    ax.text(-0.25, 1.0, 'b', transform=ax.transAxes, fontsize=16, fontweight='bold', va='top', ha='left')

    # Layout adjustment
    plt.tight_layout()

    # 5. Save Output
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)