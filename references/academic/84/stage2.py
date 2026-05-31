import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

def generate_chart(output_filename):
    # 1. Load Source Data
    # The data is embedded exactly as provided in the prompt.
    csv_data = """
| Extended Figure 3 b)   | Unnamed: 1   | Unnamed: 2   | Unnamed: 3      | Unnamed: 4     | Unnamed: 5     |
|:-----------------------|:-------------|:-------------|:----------------|:---------------|:---------------|
| Type                   | PM_size      | Season       | OP_v_DTT_median | OP_v_DTT_Q1    | OP_v_DTT_Q3    |
| nan                    | nan          | nan          | nmol min-1 m-3  | nmol min-1 m-3 | nmol min-1 m-3 |
| Traffic                | PM10         | Cold         | 2.63            | 1.66           | 3.63           |
| Traffic                | PM10         | Warm         | 1.97            | 1.46           | 2.53           |
| Urban                  | PM10         | Cold         | 1.79            | 1.17           | 2.73           |
| Urban                  | PM10         | Warm         | 1.39            | 0.88           | 2.05           |
| Industrial             | PM10         | Cold         | 1.28            | 0.81           | 2.06           |
| Industrial             | PM10         | Warm         | 1.13            | 0.78           | 1.68           |
| Suburban               | PM10         | Cold         | 2.22            | 1.33           | 3.72           |
| Suburban               | PM10         | Warm         | 0.8             | 0.53           | 1.27           |
| Rural                  | PM10         | Cold         | 0.82            | 0.48           | 1.51           |
| Rural                  | PM10         | Warm         | 0.79            | 0.47           | 1.13           |
| Traffic                | PM2.5        | Cold         | 1.45            | 0.89           | 2.03           |
| Traffic                | PM2.5        | Warm         | 0.89            | 0.65           | 1.18           |
| Urban                  | PM2.5        | Cold         | 0.89            | 0.61           | 1.56           |
| Urban                  | PM2.5        | Warm         | 0.70            | 0.44           | 1.14           |
| Suburban               | PM2.5        | Cold         | 0.63            | 0.37           | 1.54           |
| Suburban               | PM2.5        | Warm         | 0.33            | 0.2            | 0.43           |
| Rural                  | PM2.5        | Cold         | 0.45            | 0.24           | 0.88           |
| Rural                  | PM2.5        | Warm         | 0.47            | 0.25           | 0.73           |
| Urban                  | PM1          | Cold         | 0.71            | 0.45           | 1.01           |
| Urban                  | PM1          | Warm         | 0.75            | 0.42           | 1.27           |
| Rural                  | PM1          | Cold         | 0.44            | 0.24           | 0.88           |
| Rural                  | PM1          | Warm         | 0.50            | 0.33           | 0.77           |
"""

    # Parse the markdown table
    # Skip the first line (Title) and the separator line is handled by pandas automatically usually, 
    # but here we have a specific structure.
    # We read from line 2 (header) onwards.
    df = pd.read_csv(io.StringIO(csv_data), sep="|", header=2, skipinitialspace=True)
    
    # Clean up column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Drop empty columns created by leading/trailing pipes
    df = df.dropna(axis=1, how='all')
    
    # Rename columns to be cleaner
    df = df.rename(columns={
        'Type': 'Type',
        'PM_size': 'PM_size',
        'Season': 'Season',
        'OP_v_DTT_median': 'Median',
        'OP_v_DTT_Q1': 'Q1',
        'OP_v_DTT_Q3': 'Q3'
    })

    # Drop the row containing units (where Type is NaN or 'nan')
    df = df[pd.to_numeric(df['Median'], errors='coerce').notna()]

    # Convert numeric columns
    cols_to_numeric = ['Median', 'Q1', 'Q3']
    for col in cols_to_numeric:
        df[col] = pd.to_numeric(df[col])

    # Clean string columns
    df['Type'] = df['Type'].str.strip()
    df['PM_size'] = df['PM_size'].str.strip()
    df['Season'] = df['Season'].str.strip()

    # 2. Setup Plotting Parameters
    pm_sizes = ['PM10', 'PM2.5', 'PM1']
    site_types = ['Traffic', 'Urban', 'Industrial', 'Suburban', 'Rural']
    
    # Colors extracted visually from the chart
    colors = {
        'Cold': '#7aa0c4',  # Muted Blue
        'Warm': '#d49e56'   # Muted Orange/Brown
    }
    edge_color = '#333333'
    
    # Plot Setup
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True, gridspec_kw={'wspace': 0.08})
    
    # Global Y-axis limit
    y_max = 8.0
    
    # 3. Drawing Loop
    for i, pm in enumerate(pm_sizes):
        ax = axes[i]
        subset = df[df['PM_size'] == pm]
        
        # Grid setup
        ax.grid(True, which='major', axis='both', linestyle='--', alpha=0.6, zorder=0)
        ax.set_axisbelow(True)
        
        # X-axis setup
        x_positions = np.arange(len(site_types))
        ax.set_xticks(x_positions)
        ax.set_xticklabels(site_types, fontsize=11)
        
        # Only show labels for sites present in this PM size (though chart keeps spacing constant)
        # The chart keeps the "slots" for Traffic/Industrial even if empty for PM1.
        
        bar_width = 0.35
        
        for x_idx, site in enumerate(site_types):
            site_data = subset[subset['Type'] == site]
            
            if site_data.empty:
                continue
                
            for season_idx, season in enumerate(['Cold', 'Warm']):
                season_data = site_data[site_data['Season'] == season]
                
                if season_data.empty:
                    continue
                
                # Extract stats
                q1 = season_data['Q1'].values[0]
                q3 = season_data['Q3'].values[0]
                median = season_data['Median'].values[0]
                
                # Calculate Whiskers (Standard 1.5 * IQR)
                # Since source data lacks min/max, we derive standard boxplot whiskers
                iqr = q3 - q1
                upper_whisker = q3 + 1.5 * iqr
                lower_whisker = q1 - 1.5 * iqr
                
                # Clamp lower whisker to 0 (concentration cannot be negative)
                lower_whisker = max(0, lower_whisker)
                
                # Position
                # Cold on left (-offset), Warm on right (+offset)
                offset = -bar_width/2 if season == 'Cold' else bar_width/2
                x_pos = x_idx + offset
                
                # Draw Box (Rectangle)
                # (x, y), width, height
                rect = patches.Rectangle(
                    (x_pos - bar_width/2, q1), 
                    bar_width, 
                    q3 - q1, 
                    linewidth=1.2, 
                    edgecolor=edge_color, 
                    facecolor=colors[season],
                    zorder=3
                )
                ax.add_patch(rect)
                
                # Draw Median Line
                ax.plot(
                    [x_pos - bar_width/2, x_pos + bar_width/2], 
                    [median, median], 
                    color='#333333', 
                    linewidth=1.5, 
                    zorder=4
                )
                
                # Draw Whiskers and Caps
                # Vertical line
                ax.plot([x_pos, x_pos], [q3, upper_whisker], color=edge_color, linewidth=1.2, zorder=2)
                ax.plot([x_pos, x_pos], [q1, lower_whisker], color=edge_color, linewidth=1.2, zorder=2)
                
                # Horizontal caps
                cap_width = bar_width * 0.6
                ax.plot([x_pos - cap_width/2, x_pos + cap_width/2], [upper_whisker, upper_whisker], color=edge_color, linewidth=1.2, zorder=2)
                ax.plot([x_pos - cap_width/2, x_pos + cap_width/2], [lower_whisker, lower_whisker], color=edge_color, linewidth=1.2, zorder=2)

        # Axis styling
        ax.set_ylim(0, y_max)
        
        # Remove ticks from top and right
        ax.tick_params(top=False, right=False)
        
        # Add border box
        for spine in ax.spines.values():
            spine.set_linewidth(1.2)

    # 4. Final Layout Adjustments
    
    # Y-axis Label (only on first plot)
    # Using LaTeX formatting for the unit
    axes[0].set_ylabel(r'$OP_v^{DTT} \ (nmol \ min^{-1} \ m^{-3})$', fontsize=14)
    
    # Tick label size
    axes[0].tick_params(axis='y', labelsize=12)
    
    # Add "b)" label to the first subplot
    axes[0].text(0.03, 0.92, 'b)', transform=axes[0].transAxes, fontsize=16, fontweight='bold')

    # Adjust layout to prevent clipping
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    generate_chart(output_file)