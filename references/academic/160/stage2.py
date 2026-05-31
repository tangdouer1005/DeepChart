import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

def generate_chart(output_filename):
    # 1. Source Data
    # Embedding the provided markdown data directly
    csv_data = """| million$                               |   Unnamed: 1 |   central estimate of SAF cost |   low SAF cost |   high SAF cost |
|:---------------------------------------|-------------:|-------------------------------:|---------------:|----------------:|
| central estimate of CORSIA offset cost |         2027 |                         2250.3 |         1062.2 |          3057.8 |
| nan                                    |         2028 |                         2016.3 |          803   |          2952.4 |
| nan                                    |         2029 |                         1818.1 |          549.4 |          2888.1 |
| nan                                    |         2030 |                         1655.5 |          301   |          2865   |
| nan                                    |         2031 |                         1528.6 |           58   |          2883.3 |
| nan                                    |         2032 |                         1362.6 |         -180   |          2883.9 |
| nan                                    |         2033 |                         1213.7 |         -381.8 |          2875.3 |
| nan                                    |         2034 |                         1064.8 |         -604.1 |          2909   |
| nan                                    |         2035 |                          915.9 |         -821.1 |          2955.7 |
| nan                                    |          nan |                          nan   |          nan   |           nan   |
| low estimate of CORSIA offset cost     |         2027 |                         2726.8 |         1538.7 |          3534.3 |
| nan                                    |         2028 |                         2599.5 |         1386.2 |          3535.6 |
| nan                                    |         2029 |                         2518.8 |         1250.1 |          3588.8 |
| nan                                    |         2030 |                         2484.7 |         1130.2 |          3694.2 |
| nan                                    |         2031 |                         2497.4 |         1026.7 |          3852.1 |
| nan                                    |         2032 |                         2482.1 |          939.5 |          4003.4 |
| nan                                    |         2033 |                         2464.2 |          868.7 |          4125.8 |
| nan                                    |         2034 |                         2483.1 |          814.2 |          4327.3 |
| nan                                    |         2035 |                         2513   |          776   |          4552.8 |
| nan                                    |          nan |                          nan   |          nan   |           nan   |
| high estimate of CORSIA offset cost    |         2027 |                         1706.5 |          518.4 |          2514   |
| nan                                    |         2028 |                         1349.4 |          136.1 |          2285.5 |
| nan                                    |         2029 |                         1015.4 |         -253.3 |          2085.4 |
| nan                                    |         2030 |                          704.3 |         -650.1 |          1913.8 |
| nan                                    |         2031 |                          416   |        -1054.6 |          1770.7 |
| nan                                    |         2032 |                           75.6 |        -1467   |          1596.9 |
| nan                                    |         2033 |                         -225.2 |        -1820.8 |          1436.4 |
| nan                                    |         2034 |                         -568.3 |        -2237.2 |          1275.9 |
| nan                                    |         2035 |                         -924.4 |        -2661.4 |          1115.4 |"""

    # 2. Data Processing
    # Read as string first to avoid type inference errors on the markdown separator line
    df = pd.read_csv(io.StringIO(csv_data), sep="|", skipinitialspace=True, dtype=str, header=0)
    
    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Remove the first and last columns which are empty due to markdown pipe format
    # The columns are likely ['', 'million$', 'Unnamed: 1', ..., '']
    df = df.iloc[:, 1:-1]
    
    # Rename columns for easier access
    df.columns = ['Category', 'Year', 'Central', 'Low', 'High']
    
    # Drop the separator row (index 0 in the dataframe, which corresponds to the markdown separator line)
    df = df.drop(index=0).reset_index(drop=True)
    
    # Clean Category column and forward fill
    df['Category'] = df['Category'].str.strip()
    df['Category'] = df['Category'].replace({'nan': np.nan, '': np.nan}).ffill()
    
    # Convert numeric columns, coercing errors to handle 'nan' strings
    cols_to_numeric = ['Year', 'Central', 'Low', 'High']
    for col in cols_to_numeric:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    # Drop rows where Year is NaN (separator rows between data blocks)
    df = df.dropna(subset=['Year'])

    # 3. Plotting Setup
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Define styles based on visual analysis of the image
    styles = {
        "high estimate of CORSIA offset cost": {
            "color": "#dcdb55", # Yellow/Gold
            "fill_color": "#f6ecc8", # Light Yellow/Beige
            "label": "High offset price",
            "annotation": "3.5 B",
            "zorder": 2
        },
        "low estimate of CORSIA offset cost": {
            "color": "#2b4f76", # Dark Blue
            "fill_color": "#dce7f1", # Light Blue
            "label": "Low offset price",
            "annotation": "22.8 B",
            "zorder": 1
        },
        "central estimate of CORSIA offset cost": {
            "color": "#e07b7b", # Salmon/Red
            "fill_color": "#ebd6d8", # Light Pink
            "label": "Medium offset price",
            "annotation": "13.8 B",
            "zorder": 1.5
        }
    }

    # Plot each group
    for category, group_df in df.groupby('Category'):
        style = styles.get(category)
        if not style:
            continue
            
        # Plot shaded area (Confidence Interval)
        ax.fill_between(
            group_df['Year'], 
            group_df['Low'], 
            group_df['High'], 
            color=style['fill_color'], 
            alpha=0.9,
            edgecolor=None,
            zorder=style['zorder']
        )
        
        # Plot central line
        ax.plot(
            group_df['Year'], 
            group_df['Central'], 
            color=style['color'], 
            linewidth=3.5, 
            label=style['label'],
            zorder=style['zorder'] + 10
        )
        
        # Add text annotation at the end of the line (Year 2035)
        last_row = group_df.iloc[-1]
        
        # Adjust text color for visibility (darker yellow for the yellow line)
        text_color = style['color']
        if "high estimate" in category:
            text_color = "#bfbd4d"
            
        ax.text(
            last_row['Year'], 
            last_row['Central'] + 250, # Offset slightly up
            style['annotation'], 
            color=text_color, 
            fontsize=14, 
            ha='right', 
            va='bottom',
            weight='normal',
            zorder=style['zorder'] + 20
        )

    # 4. Chart Styling
    
    # Zero line
    ax.axhline(0, color='gray', linestyle=':', linewidth=1.5, zorder=0.5)
    
    # Axis Limits
    ax.set_xlim(2027, 2035)
    ax.set_ylim(-4000, 6000)
    
    # Axis Labels
    ax.set_ylabel("Net costs of max usage of SAF (million US$)", fontsize=12, color='black')
    
    # Ticks
    ax.tick_params(axis='both', which='major', labelsize=11, direction='in', length=4)
    
    # Y-axis formatting (comma separator)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))
    
    # Legend
    # Sort handles/labels to match specific order: High, Low, Medium
    handles, labels = ax.get_legend_handles_labels()
    order_map = {"High offset price": 0, "Low offset price": 1, "Medium offset price": 2}
    
    # Create a dictionary to map labels to handles
    hl_dict = {l: h for h, l in zip(handles, labels)}
    
    # Reconstruct lists in desired order
    ordered_labels = ["High offset price", "Low offset price", "Medium offset price"]
    ordered_handles = [hl_dict[l] for l in ordered_labels if l in hl_dict]
    
    legend = ax.legend(
        ordered_handles, 
        ordered_labels, 
        title="US-S1", 
        loc='lower left', 
        frameon=False, 
        fontsize=12,
        title_fontsize=14,
        handlelength=1.0,
        borderpad=1.5
    )
    legend._legend_box.align = "left" # Align title left
    
    # Add the "d" label in the top left corner
    ax.text(
        -0.12, 1.0, "d", 
        transform=ax.transAxes, 
        fontsize=24, 
        fontweight='bold', 
        va='top', 
        ha='left'
    )

    # Remove top and right spines ticks but keep the box
    ax.tick_params(top=False, right=False)
    
    # Save output
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    generate_chart(output_file)