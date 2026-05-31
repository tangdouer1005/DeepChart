import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

def get_source_data():
    """
    Returns the raw data provided in the prompt as a pandas DataFrame.
    """
    csv_data = """million$|Unnamed: 1|central estimate of SAF cost|low SAF cost|high SAF cost
central estimate of CORSIA offset cost|2027|343|-516.9|2100.1
nan|2028|121.4|-626.3|2003.8
nan|2029|-64.6|-746.6|1948.6
nan|2030|-214.9|-877.8|1934.7
nan|2031|-341.8|-1020.1|1953
nan|2032|-448.9|-1173.7|1953.6
nan|2033|-481.7|-1307.5|1945
nan|2034|-514.5|-1478|1978.7
nan|2035|-547.2|-1659.6|2025.4
nan|nan|nan|nan|nan
low estimate of CORSIA offset cost|2027|819.6|-40.4|2576.7
nan|2028|704.6|-43.1|2587
nan|2029|636|-45.9|2649.3
nan|2030|614.3|-48.6|2763.9
nan|2031|626.9|-51.4|2921.8
nan|2032|670.6|-54.2|3073.1
nan|2033|768.8|-56.9|3195.5
nan|2034|903.8|-59.7|3397
nan|2035|1049.9|-62.5|3622.5
nan|nan|nan|nan|nan
high estimate of CORSIA offset cost|2027|-200.7|-1060.7|1556.3
nan|2028|-545.5|-1293.2|1337
nan|2029|-867.3|-1549.2|1146
nan|2030|-1166.1|-1829|983.5
nan|2031|-1454.4|-2132.7|840.4
nan|2032|-1736|-2460.7|666.6
nan|2033|-1920.6|-2746.4|506.1
nan|2034|-2147.6|-3111.1|345.6
nan|2035|-2387.5|-3499.9|185.1"""

    # Read the pipe-separated data
    df = pd.read_csv(io.StringIO(csv_data), sep='|')
    
    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # The first column acts as a group header. We need to forward fill it.
    # However, the raw string has 'nan' strings, not actual NaNs initially if read as object,
    # but pandas read_csv usually handles 'nan' correctly.
    # Let's ensure we handle the grouping logic correctly.
    
    groups = []
    current_group = None
    
    # Iterate to fill the grouping column manually to be safe
    clean_rows = []
    
    for index, row in df.iterrows():
        # Check if the first column has a value (start of a new group)
        val = row['million$']
        if pd.notna(val) and str(val).strip() != 'nan':
            current_group = str(val).strip()
        
        # Check if the Year column is valid (contains data)
        year_val = row['Unnamed: 1']
        if pd.notna(year_val) and str(year_val).strip() != 'nan':
            # Create a clean row dictionary
            clean_rows.append({
                'Group': current_group,
                'Year': int(float(year_val)),
                'Central': float(row['central estimate of SAF cost']),
                'Low': float(row['low SAF cost']),
                'High': float(row['high SAF cost'])
            })
            
    return pd.DataFrame(clean_rows)

def plot_chart(df, output_file):
    # Setup the plot style
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Define styles for each scenario
    # Mapping source data names to chart legend names and colors
    # Colors picked to match the image: 
    # High offset (Yellow), Low offset (Blue), Medium offset (Red/Pink)
    
    styles = {
        'high estimate of CORSIA offset cost': {
            'label': 'High offset price',
            'color_line': '#dede5d',      # Yellowish gold
            'color_fill': '#fcf5c9',      # Very light yellow
            'annotation': '-12.4 B',
            'zorder': 1
        },
        'low estimate of CORSIA offset cost': {
            'label': 'Low offset price',
            'color_line': '#3b5b7e',      # Dark Blue
            'color_fill': '#dbe9f6',      # Light Blue
            'annotation': '6.8 B',
            'zorder': 2
        },
        'central estimate of CORSIA offset cost': {
            'label': 'Medium offset price',
            'color_line': '#e77f82',      # Salmon Red
            'color_fill': '#eaccd4',      # Light Pink
            'annotation': '-2.1 B',
            'zorder': 3
        }
    }

    # Plot each group
    # We iterate through the styles keys to ensure we process them all
    for group_name, style in styles.items():
        subset = df[df['Group'] == group_name].sort_values('Year')
        
        if subset.empty:
            continue
            
        # Plot the shaded range (Low SAF cost to High SAF cost)
        ax.fill_between(
            subset['Year'], 
            subset['Low'], 
            subset['High'], 
            color=style['color_fill'], 
            alpha=0.8, 
            edgecolor=None,
            zorder=style['zorder']
        )
        
        # Plot the central line
        ax.plot(
            subset['Year'], 
            subset['Central'], 
            color=style['color_line'], 
            linewidth=3, 
            label=style['label'],
            zorder=style['zorder'] + 10 # Lines on top of all fills
        )
        
        # Add the annotation text (Billions)
        # Position: Year 2034.5, Y value based on the end of the line or visual placement
        last_year = subset['Year'].max()
        last_val = subset[subset['Year'] == last_year]['Central'].values[0]
        
        # Fine-tuning text position based on the visual chart
        text_y = last_val
        if "6.8" in style['annotation']:
            text_y = 1400 # Visual adjustment
            text_color = '#3b5b7e'
        elif "-2.1" in style['annotation']:
            text_y = -300 # Visual adjustment
            text_color = '#e77f82'
        elif "-12.4" in style['annotation']:
            text_y = -1800 # Visual adjustment
            text_color = '#bcbc40' # Darker yellow for text readability
            
        ax.text(
            2034.2, 
            text_y, 
            style['annotation'], 
            color=text_color, 
            fontsize=12, 
            ha='left', 
            va='center',
            zorder=20
        )

    # Add horizontal zero line
    ax.axhline(0, color='gray', linestyle=':', linewidth=1.5, zorder=5)

    # Configure Axes
    ax.set_xlim(2027, 2035)
    ax.set_ylim(-4000, 6000)
    
    # Y-axis formatting
    ax.set_ylabel('Net costs of max usage of SAF (million US$)', fontsize=12, color='black')
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    ax.tick_params(axis='y', labelsize=11, direction='in', length=5)
    
    # X-axis formatting
    ax.set_xticks(range(2027, 2036))
    ax.tick_params(axis='x', labelsize=11, direction='in', length=5)

    # Title "f"
    ax.text(-0.12, 1.0, 'f', transform=ax.transAxes, fontsize=20, fontweight='bold', va='top', ha='left')

    # Legend
    # The legend in the image has a specific order: High (Yellow), Low (Blue), Medium (Red)
    # But we plotted them differently. We need to construct the handles manually to match the image order.
    handles, labels = ax.get_legend_handles_labels()
    
    # Create a mapping to reorder
    order_map = {
        'High offset price': 0,
        'Low offset price': 1,
        'Medium offset price': 2
    }
    
    # Sort handles and labels based on the desired order
    # Note: The image order is actually High (Yellow), Low (Blue), Medium (Red) from top to bottom in the legend box?
    # Looking at the image:
    # Title: US-S1 with subsidy
    # - High offset price (Yellow)
    # - Low offset price (Blue)
    # - Medium offset price (Red)
    
    # Let's find the handles corresponding to these labels
    sorted_handles = [None] * 3
    sorted_labels = [None] * 3
    
    for h, l in zip(handles, labels):
        if l in order_map:
            idx = order_map[l]
            sorted_handles[idx] = h
            sorted_labels[idx] = l
            
    # Create the legend
    leg = ax.legend(
        sorted_handles, 
        sorted_labels, 
        title='US-S1 with subsidy', 
        loc='lower left', 
        frameon=False, 
        fontsize=12,
        title_fontsize=12,
        handlelength=1.0,
        borderaxespad=1.5
    )
    
    # Align legend title to the left
    leg._legend_box.align = "left"

    # Adjust layout
    plt.tight_layout()
    
    # Save
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_file}")

if __name__ == "__main__":
    output_filename = "output.png"
    if len(sys.argv) > 1:
        output_filename = sys.argv[1]
        
    df = get_source_data()
    plot_chart(df, output_filename)