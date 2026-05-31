import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def generate_chart(output_filename):
    # 1. Load Source Data
    # Using the exact data provided in the prompt
    csv_data = """Region,Scenario,Central,Low,High
China,S1,18.6,14.4,23.4
nan,S2,35.5,25.3,36.3
nan,S3,57.8,41.6,70.8
nan,nan,nan,nan,nan
EU27,S1,9,7,11.5
nan,S2,17.4,12.2,17.9
nan,S3,28.4,20.1,35
nan,nan,nan,nan,nan
United States,S1,8.3,6.5,10.8
nan,S2,16.5,11.3,17.1
nan,S3,26.8,18.6,33.4
nan,nan,nan,nan,nan
India,S1,8.1,6.3,10.2
nan,S2,15.5,11,15.9
nan,S3,25.3,18.1,31"""

    # Read data into DataFrame
    df = pd.read_csv(io.StringIO(csv_data))

    # 2. Data Cleaning and Preparation
    # Forward fill the Region column to handle the 'nan' values for S2/S3
    df['Region'] = df['Region'].ffill()
    
    # Drop rows where Scenario is NaN (the spacer rows)
    df = df.dropna(subset=['Scenario'])

    # Rename "United States" to "US" to match the chart labels
    df['Region'] = df['Region'].replace('United States', 'US')

    # Create the combined label (e.g., "China-S1")
    df['Label'] = df['Region'] + '-' + df['Scenario']

    # Calculate error bar values relative to the central estimate
    # Matplotlib requires error bars to be relative lengths, not absolute coordinates
    # Shape needs to be (2, N) for asymmetric errors: [lower_error, upper_error]
    lower_error = df['Central'] - df['Low']
    upper_error = df['High'] - df['Central']
    yerr = [lower_error, upper_error]

    # 3. Define Visual Style
    # Colors extracted from the image
    colors_map = {
        'China': '#F0B956',  # Yellow/Orange
        'EU27': '#D66A48',   # Terracotta/Red
        'US': '#235793',     # Dark Blue
        'India': '#316B75'   # Teal/Greenish-Blue
    }
    
    # Map colors to the dataframe rows
    bar_colors = df['Region'].map(colors_map)

    # 4. Plotting
    fig, ax = plt.subplots(figsize=(12, 4))

    # Create bars
    bars = ax.bar(
        x=df['Label'],
        height=df['Central'],
        yerr=yerr,
        color=bar_colors,
        capsize=10,       # Width of the error bar caps
        error_kw={'elinewidth': 1, 'ecolor': 'gray'}, # Style of error lines
        edgecolor='grey', # Slight border on bars
        linewidth=0.5,
        width=0.75
    )

    # 5. Formatting Axes and Labels
    
    # Y-Axis Label with LaTeX formatting for subscripts/superscripts
    ax.set_ylabel(r'GHG mitigation (MtCO$_2$e yr$^{-1}$)', fontsize=12, color='black')
    
    # Y-Axis Limits and Ticks
    ax.set_ylim(0, 90)
    ax.set_yticks(np.arange(0, 91, 10))
    
    # Tick styling
    ax.tick_params(axis='y', direction='in', length=4, colors='black')
    ax.tick_params(axis='x', length=0, pad=10) # Hide x tick marks, keep labels
    
    # X-Axis Labels styling
    plt.xticks(fontsize=11)
    plt.yticks(fontsize=11)

    # Add the bold "d" annotation in the top left corner
    # Coordinates are relative to figure (0,0 is bottom-left, 1,1 is top-right)
    # Adjusting x and y to place it outside the axes like the source image
    ax.text(-0.06, 1.02, 'd', transform=ax.transAxes, 
            fontsize=24, fontweight='bold', va='bottom', ha='right')

    # Remove top and right spines? The image has a box, so we keep them.
    # Ensure spines are black and visible
    for spine in ax.spines.values():
        spine.set_edgecolor('black')
        spine.set_linewidth(0.8)

    # Layout adjustment
    plt.tight_layout()

    # 6. Save Output
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    # Handle command line argument for output filename
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        output_file = "output.png"
    
    generate_chart(output_file)