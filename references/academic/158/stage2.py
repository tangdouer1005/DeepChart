import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def generate_chart(output_filename):
    # 1. Source Data Loading
    csv_data = """
| million$                               |   Unnamed: 1 |   central estimate of SAF cost |   low SAF cost |   high SAF cost |
|:---------------------------------------|-------------:|-------------------------------:|---------------:|----------------:|
| central estimate of CORSIA offset cost |         2027 |                         3413.1 |         1962.7 |          4236.8 |
| nan                                    |         2028 |                         3374   |         1859.9 |          4350.1 |
| nan                                    |         2029 |                         3335   |         1734   |          4465.8 |
| nan                                    |         2030 |                         3310.8 |         1590.8 |          4595.4 |
| nan                                    |         2031 |                         3317.2 |         1436.4 |          4751.7 |
| nan                                    |         2032 |                         3044.9 |         1173.7 |          4632.6 |
| nan                                    |         2033 |                         2712.1 |          850.7 |          4464.3 |
| nan                                    |         2034 |                         2379.4 |          565.7 |          4294.6 |
| nan                                    |         2035 |                         2046.7 |          303.2 |          4141   |
| nan                                    |          nan |                          nan   |          nan   |           nan   |
| low estimate of CORSIA offset cost     |         2027 |                         3784.4 |         2333.9 |          4608   |
| nan                                    |         2028 |                         3833.8 |         2319.6 |          4809.9 |
| nan                                    |         2029 |                         3894   |         2293   |          5024.8 |
| nan                                    |         2030 |                         3980.3 |         2260.3 |          5264.9 |
| nan                                    |         2031 |                         4108.8 |         2228   |          5543.2 |
| nan                                    |         2032 |                         3970.6 |         2099.4 |          5558.3 |
| nan                                    |         2033 |                         3802.5 |         1941.1 |          5554.7 |
| nan                                    |         2034 |                         3633   |         1819.3 |          5548.2 |
| nan                                    |         2035 |                         3477.4 |         1734   |          5571.8 |
| nan                                    |          nan |                          nan   |          nan   |           nan   |
| high estimate of CORSIA offset cost    |         2027 |                         2989.5 |         1539   |          3813.1 |
| nan                                    |         2028 |                         2848.2 |         1334.1 |          3824.4 |
| nan                                    |         2029 |                         2694.6 |         1093.6 |          3825.4 |
| nan                                    |         2030 |                         2542.8 |          822.8 |          3827.4 |
| nan                                    |         2031 |                         2408.1 |          527.3 |          3842.6 |
| nan                                    |         2032 |                         1980.6 |          109.4 |          3568.3 |
| nan                                    |         2033 |                         1457.5 |         -403.9 |          3209.7 |
| nan                                    |         2034 |                          935.9 |         -877.9 |          2851.1 |
| nan                                    |         2035 |                          398.1 |        -1345.4 |          2492.4 |
"""

    # Parse the markdown table
    # Use '|' as separator, skip initial spaces.
    df = pd.read_csv(io.StringIO(csv_data), sep="|", skipinitialspace=True)
    
    # Clean column names: remove whitespace
    df.columns = [c.strip() for c in df.columns]
    
    # The markdown format results in empty first and last columns (due to leading/trailing pipes), remove them
    df = df.iloc[:, 1:-1]
    
    # Rename columns for easier access
    df.columns = ['Scenario', 'Year', 'Central', 'Low', 'High']
    
    # Clean 'Scenario' column: strip whitespace and replace string 'nan' with np.nan
    df['Scenario'] = df['Scenario'].astype(str).str.strip()
    df['Scenario'] = df['Scenario'].replace({'nan': np.nan, 'None': np.nan})
    
    # Forward fill the 'Scenario' column to propagate the group names
    df['Scenario'] = df['Scenario'].ffill()
    
    # Coerce 'Year' to numeric. This handles 'nan' strings, separator lines '---', etc. by turning them into NaN
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    
    # Drop rows where Year is NaN (this removes the separator rows and empty spacer rows)
    df = df.dropna(subset=['Year'])
    
    # Convert Year to integer
    df['Year'] = df['Year'].astype(int)
    
    # Convert data columns to numeric
    for col in ['Central', 'Low', 'High']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 2. Setup Plotting
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Define styles based on the visual analysis
    # "low estimate of CORSIA" -> Blue line (Highest values in chart) -> "Low offset price"
    # "central estimate of CORSIA" -> Red line (Middle values) -> "Medium offset price"
    # "high estimate of CORSIA" -> Yellow line (Lowest values) -> "High offset price"
    
    style_map = {
        "low estimate of CORSIA offset cost": {
            "color": "#345e80",      # Dark Blue
            "fill_color": "#dbe6f0", # Light Blue
            "label": "Low offset price",
            "zorder_line": 12,
            "zorder_fill": 0         # Background fill
        },
        "central estimate of CORSIA offset cost": {
            "color": "#e07a7a",      # Salmon/Red
            "fill_color": "#ebdada", # Light Red/Pink
            "label": "Medium offset price",
            "zorder_line": 13,
            "zorder_fill": 1         # Middle fill
        },
        "high estimate of CORSIA offset cost": {
            "color": "#dede5d",      # Yellow/Gold
            "fill_color": "#f5eac6", # Light Yellow
            "label": "High offset price",
            "zorder_line": 14,
            "zorder_fill": 2         # Foreground fill
        }
    }

    # Store handles for custom legend ordering
    handles_dict = {}

    # 3. Plot Data
    # Iterate through unique scenarios
    for scenario in df['Scenario'].unique():
        if scenario not in style_map:
            continue
            
        subset = df[df['Scenario'] == scenario].sort_values('Year')
        style = style_map[scenario]
        
        # Plot the main line
        line, = ax.plot(subset['Year'], subset['Central'], 
                        color=style['color'], 
                        linewidth=3, 
                        label=style['label'],
                        zorder=style['zorder_line'])
        
        # Fill the confidence interval
        ax.fill_between(subset['Year'], subset['Low'], subset['High'], 
                        color=style['fill_color'], 
                        alpha=0.9, 
                        zorder=style['zorder_fill'])
        
        handles_dict[style['label']] = line
        
        # Calculate Total Sum for the annotation (Billion)
        total_sum = subset['Central'].sum() / 1000.0
        
        # Add text annotation at the end of the line
        last_y = subset['Central'].iloc[-1]
        
        # Fine-tuning text position based on the specific line to match image
        text_y_offset = 0
        text_color = style['color']
        
        if "High offset price" in style['label']: # Yellow line
            text_color = "#b8b840" # Slightly darker for text readability
            text_y_offset = 800
        elif "Low offset price" in style['label']: # Blue line
            text_y_offset = 300
        elif "Medium offset price" in style['label']: # Red line
            text_y_offset = 0
            
        ax.text(2034.2, last_y + text_y_offset, f"{total_sum:.1f} B", 
                color=text_color, 
                fontsize=12, 
                fontweight='normal',
                ha='left', va='center',
                zorder=20)

    # 4. Chart Styling
    
    # Zero line
    ax.axhline(0, color='grey', linestyle=':', linewidth=1.5, zorder=5)
    
    # Axis Limits
    ax.set_xlim(2027, 2035)
    ax.set_ylim(-4000, 6000)
    
    # Axis Labels
    ax.set_ylabel("Net costs of max usage of SAF (million US$)", fontsize=12, color='black')
    
    # Ticks
    ax.tick_params(axis='both', which='major', labelsize=11, direction='in', length=4)
    
    # X-axis ticks explicitly set to integers
    ax.set_xticks(range(2027, 2036))
    
    # Y-axis formatting (comma separator)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

    # Legend
    # Order in image: High (Yellow), Low (Blue), Medium (Red)
    legend_order = ["High offset price", "Low offset price", "Medium offset price"]
    ordered_handles = [handles_dict[label] for label in legend_order]
    
    leg = ax.legend(ordered_handles, legend_order, 
              title="China-S1", 
              loc='lower left', 
              frameon=False, 
              fontsize=12,
              title_fontsize=13,
              handlelength=1.0,
              borderpad=1.5)
    
    # Align legend title left
    leg._legend_box.align = "left"

    # Add the bold 'b' label in the top left corner outside the plot
    fig.text(0.02, 0.92, 'b', fontsize=20, fontweight='bold', va='top')

    # Adjust layout
    plt.tight_layout()
    plt.subplots_adjust(left=0.15, top=0.92) # Make room for 'b' and y-label

    # 5. Save Output
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    generate_chart(output_file)