import sys
import io
import pandas as pd
import matplotlib.pyplot as plt

def generate_chart(output_filename):
    # 1. Source Data
    # The data is provided as a Markdown table string.
    data_str = """
| Unnamed: 0        | Unnamed: 1      |   low,gCO2e/MJ |   high,gCO2e/MJ |
|:------------------|:----------------|---------------:|----------------:|
| MSW management    | MSW composition |           13.9 |            28.1 |
| nan               | MSW moisture    |           11.4 |            16.7 |
| nan               | Pre-treatment   |            9.9 |            14.1 |
| nan               | nan             |          nan   |           nan   |
| SAF production    | Syngas yield    |           10.3 |            16.7 |
| nan               | CO+H2 ratio     |           12.7 |            22.5 |
| nan               | CO conversion   |           14.1 |            15.1 |
| nan               | nan             |          nan   |           nan   |
| Energy and others | Electricity     |            3.6 |            20.9 |
| nan               | Others          |           11.9 |            20.3 |
"""
    
    # Read CSV
    # Use pipe separator. skipinitialspace=True handles spaces after pipes.
    try:
        df = pd.read_csv(io.StringIO(data_str), sep="|", skipinitialspace=True)
    except Exception as e:
        print(f"Error reading data: {e}")
        return

    # Clean columns: The markdown format results in empty first and last columns due to leading/trailing pipes.
    # We expect columns: [Empty, Group, Parameter, Low, High, Empty]
    # We select indices 1, 2, 3, 4 to get the actual data columns.
    if len(df.columns) >= 5:
        df = df.iloc[:, 1:5]
    
    df.columns = ['Group', 'Parameter', 'Low', 'High']
    
    # Filter out the separator row (contains dashes or starts with :)
    # We convert to string to be safe against NaNs
    df = df[~df['Group'].astype(str).str.contains('---')]
    df = df[~df['Group'].astype(str).str.startswith(':')]
    
    # Clean data values
    # Convert numeric columns, coercing errors (like 'nan' strings) to NaN
    df['Low'] = pd.to_numeric(df['Low'], errors='coerce')
    df['High'] = pd.to_numeric(df['High'], errors='coerce')
    
    # Forward fill the Group column to propagate group names to rows with 'nan'
    df['Group'] = df['Group'].ffill()
    
    # Remove rows where Parameter is NaN (these are the spacer rows in the source table)
    df = df.dropna(subset=['Parameter'])
    
    # Strip whitespace from string columns
    df['Group'] = df['Group'].str.strip()
    df['Parameter'] = df['Parameter'].str.strip()

    # 2. Plotting Setup
    fig, ax = plt.subplots(figsize=(12, 5))
    
    # Define Colors based on the image
    colors = {
        'MSW management': '#3F5D68',    # Dark Slate Blue/Grey
        'SAF production': '#DDAA55',    # Mustard/Gold
        'Energy and others': '#993333'  # Dark Red/Brown
    }
    
    # Text colors for labels inside bars (to ensure contrast)
    text_colors = {
        'MSW management': '#C0D0D8',    # Light Grey-Blue
        'SAF production': '#967130',    # Darker Gold/Brown
        'Energy and others': '#E0B0B0'  # Light Pinkish
    }
    
    # Layout parameters
    bar_width = 0.65
    bar_gap = 0.15
    group_gap = 0.8
    
    x_pos = 0
    group_centers = {}
    
    # Get unique groups preserving order
    groups = df['Group'].unique()
    
    # 3. Plotting Loop
    for group in groups:
        group_data = df[df['Group'] == group]
        
        # Track start position for group label centering
        group_start_x = x_pos
        
        for _, row in group_data.iterrows():
            low = row['Low']
            high = row['High']
            height = high - low
            
            # Draw Bar
            # Using x_pos as center of the bar
            ax.bar(x_pos, height, bottom=low, width=bar_width, 
                   color=colors.get(group, 'grey'), edgecolor='none')
            
            # Add Label inside bar
            label = row['Parameter']
            # Minor text adjustment to match image exactly
            if label == "Pre-treatment": label = "Pretreatment" 
            
            # Y position for label: just above the bottom of the bar
            label_y = low + 0.5
            
            ax.text(x_pos, label_y, label, rotation=90, ha='center', va='bottom',
                    color=text_colors.get(group, 'black'), fontsize=11, family='sans-serif')
            
            # Advance x position
            x_pos += (bar_width + bar_gap)
        
        # Calculate center of the group for the top label
        # The last bar was centered at: x_pos - bar_gap - bar_width
        first_bar_center = group_start_x
        last_bar_center = x_pos - (bar_width + bar_gap)
        group_center = (first_bar_center + last_bar_center) / 2
        
        group_centers[group] = group_center
        
        # Add extra gap after group
        x_pos += (group_gap - bar_gap)

    # 4. Annotations and Styling
    
    # Baseline Line
    baseline_val = 14.1
    # Determine plot width for line and text
    total_width = x_pos - group_gap # Approximate end of data
    
    # Set x limits to include space for the right-side label
    ax.set_xlim(-1, total_width + 3)
    
    # Draw dashed line
    ax.axhline(y=baseline_val, color='grey', linestyle='--', linewidth=1, zorder=0)
    
    # Baseline Text
    ax.text(total_width + 0.2, baseline_val, "Baseline\n14.1\ngCO$_2$e MJ$^{-1}$", 
            va='center', ha='left', color='#2F4F4F', fontsize=12)
    
    # Group Labels (Top)
    for group, center in group_centers.items():
        ax.text(center, 28.5, group, ha='center', va='bottom', 
                color=colors.get(group, 'black'), fontsize=13)
        
    # Axis Labels and Ticks
    ax.set_ylabel('GHG emission intensity\nvariation (gCO$_2$e MJ$^{-1}$)', fontsize=12)
    ax.set_ylim(0, 30)
    
    # Remove X ticks and labels
    ax.set_xticks([])
    
    # Figure Label 'c'
    ax.text(-0.05, 1.0, 'c', transform=ax.transAxes, fontsize=20, fontweight='bold', va='top')
    
    # Tick styling
    ax.tick_params(axis='y', direction='in')

    # Save Output
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    generate_chart(output_file)