import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def generate_chart(output_filename='output.png'):
    # 1. Load Source Data
    # The data is embedded exactly as provided in the prompt.
    csv_data = """
Unnamed: 0|Unnamed: 1|central estimate of country/region|low|high|Unnamed: 5|Unnamed: 6|Unnamed: 7|Percentile value of cities on map|Unnamed: 9|Unnamed: 10|Unnamed: 11|Unnamed: 12|Unnamed: 13|Unnamed: 14|Unnamed: 15|Unnamed: 16|Unnamed: 17|Unnamed: 18|Unnamed: 19
China|S1|0.154|0.114|0.254|nan|nan|Percentile (%)|China-S1|China-S2|China-S3|EU27-S1|EU27-S2|EU27-S3|United States-S1|United States-S2|United States-S3|India-S1|India-S2|India-S3
nan|S2|0.294|0.199|0.394|nan|nan|10|0.026|0.049|0.073|0.007|0.013|0.02|0.006|0.011|0.017|0.021|0.04|0.06
nan|S3|0.439|0.297|0.588|nan|nan|25|0.04|0.077|0.115|0.021|0.04|0.06|0.018|0.035|0.053|0.042|0.08|0.12
nan|nan|nan|nan|nan|nan|nan|50|0.076|0.144|0.216|0.056|0.109|0.162|0.064|0.127|0.189|0.094|0.179|0.268
EU27|S1|0.067|0.05|0.113|nan|nan|75|0.235|0.449|0.67|0.139|0.269|0.401|0.211|0.418|0.624|0.223|0.427|0.637
nan|S2|0.13|0.087|0.176|nan|nan|90|0.397|0.757|1.13|0.328|0.636|0.95|0.592|1.17|1.747|0.726|1.393|2.079
nan|S3|0.194|0.13|0.263|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan
nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan
United States|S1|0.044|0.033|0.075|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan
nan|S2|0.087|0.057|0.119|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan
nan|S3|0.13|0.085|0.178|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan
nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan
India|S1|0.376|0.278|0.623|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan
nan|S2|0.721|0.486|0.97|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan
nan|S3|1.076|0.725|1.448|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan
"""

    # Read CSV
    df = pd.read_csv(io.StringIO(csv_data), sep="|")
    
    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]

    # --- Process Bar Chart Data (Left side of table) ---
    # Extract relevant columns
    bar_cols = ['Unnamed: 0', 'Unnamed: 1', 'central estimate of country/region', 'low', 'high']
    df_bars = df[bar_cols].copy()
    df_bars.columns = ['Region', 'Scenario', 'Central', 'Low', 'High']

    # Forward fill the Region column (China, EU27, etc.)
    df_bars['Region'] = df_bars['Region'].ffill()

    # Drop rows where Scenario or Central estimate is NaN (spacer rows)
    df_bars = df_bars.dropna(subset=['Scenario', 'Central'])

    # Create a composite label for the X-axis
    df_bars['Label'] = df_bars['Region'] + '-' + df_bars['Scenario']
    
    # Fix US label to match chart image (United States -> US)
    df_bars['Label'] = df_bars['Label'].str.replace('United States', 'US')

    # --- Process Scatter/Percentile Data (Right side of table) ---
    # The scatter data is in columns 8 to 19 (indices). 
    # The headers for these columns are actually in the first row of data (index 0) in the raw CSV read.
    # The values (10%, 25%, etc.) are in rows 1 to 5.
    
    # Extract the specific block for percentiles
    # Columns 8 through 19 correspond to the regions (China-S1 ... India-S3)
    scatter_data = df.iloc[1:6, 8:20].copy()
    
    # Get column names from the first row of the dataframe (which contains the labels like China-S1)
    scatter_cols = df.iloc[0, 8:20].values
    scatter_data.columns = [c.strip() for c in scatter_cols]
    
    # Convert to numeric
    scatter_data = scatter_data.apply(pd.to_numeric)

    # --- Plotting ---
    
    # Define Colors based on the image
    colors = {
        'China': '#EBC05C',       # Gold/Yellow
        'EU27': '#CC5C45',        # Terracotta/Red
        'United States': '#265586', # Dark Blue
        'India': '#306873'        # Teal/Dark Cyan
    }

    fig, ax = plt.subplots(figsize=(14, 4.5))

    # X positions
    x_pos = np.arange(len(df_bars))
    
    # Loop through data to plot bars and error bars
    for i, row in df_bars.iterrows():
        region = row['Region']
        label = row['Label']
        central = row['Central']
        low = row['Low']
        high = row['High']
        
        # Determine color
        color = colors.get(region, '#333333')
        
        # Calculate error margins (matplotlib requires relative values for yerr)
        # yerr shape: [lower_error, upper_error]
        yerr_low = central - low
        yerr_high = high - central
        
        # Plot Bar
        ax.bar(i, central, color=color, width=0.75, alpha=0.9, zorder=2)
        
        # Plot Error Bar
        ax.errorbar(i, central, yerr=[[yerr_low], [yerr_high]], 
                    fmt='none', ecolor='gray', capsize=10, elinewidth=1, capthick=1, zorder=3)

        # Plot Scatter Points (Percentiles)
        # Map the bar label to the scatter column name
        # Note: df_bars label uses "US", scatter data uses "United States" or "US"?
        # Let's check the scatter columns extracted: ['China-S1', ..., 'United States-S1', ...]
        # We need to match the current bar to the correct scatter column.
        
        # Construct key for scatter lookup
        scatter_key = f"{region}-{row['Scenario']}"
        
        if scatter_key in scatter_data.columns:
            points = scatter_data[scatter_key].values
            # Add some jitter to x for visual effect (swarm style)
            # Since we only have 5 percentile points, we plot them directly. 
            # To mimic the "swarm" look of the original image which implies many cities, 
            # we will plot these specific percentile markers.
            # The original image has many dots. We only have the 10, 25, 50, 75, 90 percentiles.
            # We will plot these 5 points.
            
            # Jitter x slightly for each point to avoid perfect vertical alignment if desired, 
            # but keeping them centered is cleaner for just 5 points. 
            # However, to mimic the "cloud" look, let's add slight random jitter.
            np.random.seed(42) # For reproducibility
            x_jitter = np.random.uniform(-0.1, 0.1, size=len(points))
            
            # Plot points: Hollow circles with grey outline
            ax.scatter(np.full(len(points), i) + x_jitter, points, 
                       facecolors='none', edgecolors='grey', s=30, linewidths=0.8, zorder=4, alpha=0.8)

    # Formatting
    ax.set_ylabel('Ratio of MSW-SAF/jet fuel', fontsize=12, color='black')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(df_bars['Label'], fontsize=11)
    
    # Y-axis limits and ticks
    ax.set_ylim(0, 2.0)
    ax.set_yticks([0, 0.5, 1.0, 1.5, 2.0])
    
    # Styling
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='x', length=0, pad=10) # Hide x ticks, keep labels
    ax.tick_params(axis='y', direction='in', length=4)
    
    # Add the "c" label in the top left corner
    ax.text(-0.08, 1.0, 'c', transform=ax.transAxes, fontsize=20, fontweight='bold', va='top', ha='right')

    plt.tight_layout()
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)