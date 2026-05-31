import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def generate_chart(output_filename='output.png'):
    # 1. Source Data
    csv_data = """
| Unnamed: 0    | Unnamed: 1   |   central estimate,Mt/yr |   low |   high |
|:--------------|:-------------|-------------------------:|------:|-------:|
| China         | S1           |                      5.8 |   4.3 |    9.5 |
| nan           | S2           |                     11   |   7.5 |   14.8 |
| nan           | S3           |                     16.5 |  11.2 |   22.1 |
| nan           | nan          |                    nan   | nan   |  nan   |
| EU27          | S1           |                      2.8 |   2.1 |    4.7 |
| nan           | S2           |                      5.4 |   3.6 |    7.3 |
| nan           | S3           |                      8.1 |   5.4 |   10.9 |
| nan           | nan          |                    nan   | nan   |  nan   |
| United States | S1           |                      2.6 |   1.9 |    4.4 |
| nan           | S2           |                      5.1 |   3.3 |    7   |
| nan           | S3           |                      7.6 |   5   |   10.4 |
| nan           | nan          |                    nan   | nan   |  nan   |
| India         | S1           |                      2.5 |   1.9 |    4.2 |
| nan           | S2           |                      4.8 |   3.2 |    6.5 |
| nan           | S3           |                      7.2 |   4.8 |    9.7 |
"""

    # 2. Data Processing
    # Read the markdown table. 
    # sep='|' splits by pipe. skipinitialspace=True handles spaces after pipes.
    df = pd.read_csv(io.StringIO(csv_data), sep='|', skipinitialspace=True)

    # Markdown tables often result in empty columns at the start (index 0) and end due to outer pipes.
    # We select the 5 content columns by index: 1, 2, 3, 4, 5.
    df = df.iloc[:, 1:6]

    # Rename columns to standard names
    df.columns = ['Region', 'Scenario', 'Central', 'Low', 'High']

    # Filter out the markdown separator row (e.g., |:---|---|...)
    # This row usually appears as the first data row and contains dashes.
    df = df[~df['Region'].astype(str).str.contains('---')]

    # Filter out spacer rows where Scenario is NaN or 'nan' string
    df = df[df['Scenario'].notna()]
    df = df[df['Scenario'].astype(str).str.strip() != 'nan']

    # Convert numeric columns to float
    cols_numeric = ['Central', 'Low', 'High']
    for col in cols_numeric:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Clean Region column for Forward Fill
    # Ensure 'nan' strings are treated as actual NaNs
    df['Region'] = df['Region'].replace({'nan': np.nan, 'NaN': np.nan})
    
    # Forward fill the Region column to propagate region names to S2 and S3 rows
    df['Region'] = df['Region'].ffill()

    # Clean whitespace
    df['Region'] = df['Region'].str.strip()
    df['Scenario'] = df['Scenario'].str.strip()

    # Rename 'United States' to 'US' to match the chart labels
    df['Region'] = df['Region'].replace('United States', 'US')

    # Create the X-axis label (e.g., "China-S1")
    df['Label'] = df['Region'] + '-' + df['Scenario']

    # Calculate Error Bars
    # Matplotlib yerr expects [lower_error, upper_error] relative to the bar height
    lower_error = df['Central'] - df['Low']
    upper_error = df['High'] - df['Central']
    yerr = [lower_error.values, upper_error.values]

    # 3. Visualization Setup
    # Define colors based on the image
    color_map = {
        'China': '#Eeb456',  # Yellow/Gold
        'EU27': '#D46a4e',   # Terracotta/Red-Orange
        'US': '#265b96',     # Dark Blue
        'India': '#366e78'   # Teal/Dark Cyan
    }
    bar_colors = [color_map.get(r, '#333333') for r in df['Region']]

    # Set font style
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Helvetica']

    # Create Figure and Axes
    fig, ax = plt.subplots(figsize=(12, 3.5))

    # Plot Bars
    bars = ax.bar(
        df['Label'],
        df['Central'],
        yerr=yerr,
        color=bar_colors,
        capsize=12,       # Wide caps on error bars
        width=0.8,        # Bar width
        edgecolor='gray', # Thin grey border around bars
        linewidth=0.5,
        error_kw={
            'elinewidth': 0.8, # Thin error lines
            'ecolor': '#555555', # Dark grey error lines
            'capthick': 0.8
        }
    )

    # 4. Styling Details
    # Y-Axis
    ax.set_ylabel('MSW-SAF potential (Mt yr$^{-1}$)', fontsize=12, color='black')
    ax.set_ylim(0, 25)
    ax.set_yticks([0, 5, 10, 15, 20, 25])
    ax.tick_params(axis='y', direction='in', length=4, colors='black')
    
    # X-Axis
    # Remove tick marks, keep labels with padding
    ax.tick_params(axis='x', length=0, pad=10, labelsize=11)
    
    # Spines (Borders)
    for spine in ax.spines.values():
        spine.set_color('black')
        spine.set_linewidth(0.8)

    # Add the bold "b" label in the top left corner
    # Positioned slightly outside the axes to the left
    ax.text(-0.06, 1.02, 'b', transform=ax.transAxes, fontsize=18, fontweight='bold', va='bottom', ha='right')

    # Layout adjustment
    plt.tight_layout()

    # 5. Save Output
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    # Handle command line argument for output filename
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    else:
        output_path = "output.png"
    
    generate_chart(output_path)