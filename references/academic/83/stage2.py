import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

def generate_chart(output_filename):
    # 1. Source Data Loading
    csv_data = """
| Extended Figure 3 a)   | Unnamed: 1   | Unnamed: 2   | Unnamed: 3     | Unnamed: 4     | Unnamed: 5     |
|:-----------------------|:-------------|:-------------|:---------------|:---------------|:---------------|
| Type                   | PM_size      | Season       | OP_v_AA_median | OP_v_AA_Q1     | OP_v_AA_Q3     |
| nan                    | nan          | nan          | nmol min-1 m-3 | nmol min-1 m-3 | nmol min-1 m-3 |
| Traffic                | PM10         | Cold         | 3.55           | 2.27           | 5.18           |
| Traffic                | PM10         | Warm         | 2.45           | 1.69           | 3.25           |
| Urban                  | PM10         | Cold         | 1.68           | 1.04           | 2.77           |
| Urban                  | PM10         | Warm         | 0.77           | 0.46           | 1.14           |
| Industrial             | PM10         | Cold         | 1.34           | 0.76           | 2.43           |
| Industrial             | PM10         | Warm         | 0.49           | 0.33           | 0.74           |
| Suburban               | PM10         | Cold         | 3.41           | 1.69           | 5.91           |
| Suburban               | PM10         | Warm         | 0.42           | 0.3            | 0.59           |
| Rural                  | PM10         | Cold         | 0.78           | 0.37           | 1.85           |
| Rural                  | PM10         | Warm         | 0.34           | 0.18           | 0.54           |
| Traffic                | PM2.5        | Cold         | 1.63           | 1.11           | 2.21           |
| Traffic                | PM2.5        | Warm         | 0.9            | 0.7            | 1.19           |
| Urban                  | PM2.5        | Cold         | 1.01           | 0.65           | 1.69           |
| Urban                  | PM2.5        | Warm         | 0.46           | 0.32           | 0.73           |
| Suburban               | PM2.5        | Cold         | 0.86           | 0.44           | 1.44           |
| Suburban               | PM2.5        | Warm         | 0.24           | 0.18           | 0.32           |
| Rural                  | PM2.5        | Cold         | 0.46           | 0.24           | 0.83           |
| Rural                  | PM2.5        | Warm         | 0.21           | 0.1            | 0.3            |
| Urban                  | PM1          | Cold         | 0.84           | 0.54           | 1.46           |
| Urban                  | PM1          | Warm         | 0.35           | 0.23           | 0.5            |
| Rural                  | PM1          | Cold         | 0.52           | 0.29           | 1.02           |
| Rural                  | PM1          | Warm         | 0.23           | 0.13           | 0.34           |
"""
    # Strip leading/trailing whitespace from the data string
    csv_data = csv_data.strip()

    # Parse the markdown table
    # header=2 corresponds to the line starting with "| Type | PM_size ..."
    df = pd.read_csv(io.StringIO(csv_data), sep="|", header=2, skipinitialspace=True)

    # Clean column names: remove whitespace
    df.columns = [c.strip() for c in df.columns]
    
    # Keep only relevant columns
    target_cols = ['Type', 'PM_size', 'Season', 'OP_v_AA_median', 'OP_v_AA_Q1', 'OP_v_AA_Q3']
    # Filter columns that match target_cols
    df = df[[c for c in df.columns if c in target_cols]]

    # Clean string data: strip whitespace from all string columns
    # This is crucial to handle " nan " vs "nan"
    for col in ['Type', 'PM_size', 'Season']:
        df[col] = df[col].astype(str).str.strip()

    # Filter out the unit row. The unit row has Type="nan"
    df = df[df['Type'] != 'nan']
    
    # Convert numeric columns, coercing errors to NaN (handles any remaining non-numeric text)
    numeric_cols = ['OP_v_AA_median', 'OP_v_AA_Q1', 'OP_v_AA_Q3']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop any rows that failed numeric conversion (safety check)
    df = df.dropna(subset=numeric_cols)

    # 2. Plot Configuration
    # Colors extracted to match the image
    color_cold = '#7ea6c9'  # Muted blue
    color_warm = '#cc9a52'  # Muted orange/brown
    
    # Setup figure with 3 subplots sharing Y axis
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5), sharey=True)
    plt.subplots_adjust(wspace=0.08) # Reduce space between plots

    # Define categories and order
    pm_order = ['PM10', 'PM2.5', 'PM1']
    type_order = ['Traffic', 'Urban', 'Industrial', 'Suburban', 'Rural']
    
    # 3. Plotting Logic
    for i, pm in enumerate(pm_order):
        ax = axes[i]
        subset = df[df['PM_size'] == pm]
        
        # Determine which types exist for this PM size to set x-axis correctly
        present_types = [t for t in type_order if t in subset['Type'].unique()]
        
        # Iterate through types to draw boxplots manually
        for x_idx, loc_type in enumerate(present_types):
            
            # We group by Season: Cold (left), Warm (right)
            seasons = [('Cold', -0.2, color_cold), ('Warm', 0.2, color_warm)]
            
            for season_name, offset, color in seasons:
                row = subset[(subset['Type'] == loc_type) & (subset['Season'] == season_name)]
                
                if row.empty:
                    continue
                
                # Extract stats
                med = row['OP_v_AA_median'].values[0]
                q1 = row['OP_v_AA_Q1'].values[0]
                q3 = row['OP_v_AA_Q3'].values[0]
                
                # Calculate whiskers (1.5 * IQR)
                iqr = q3 - q1
                whislo = max(0, q1 - 1.5 * iqr) # Clamp to 0
                whishi = q3 + 1.5 * iqr
                
                # Construct stats dictionary for matplotlib.axes.Axes.bxp
                stats = [{
                    'med': med,
                    'q1': q1,
                    'q3': q3,
                    'whislo': whislo,
                    'whishi': whishi,
                    'label': loc_type
                }]
                
                # Draw the box
                box = ax.bxp(stats, positions=[x_idx + offset], widths=0.35, 
                             patch_artist=True, showfliers=False, manage_ticks=False)
                
                # Apply Styling
                plt.setp(box['boxes'], facecolor=color, edgecolor='black', linewidth=1, alpha=0.9)
                plt.setp(box['medians'], color='#333333', linewidth=1.5)
                plt.setp(box['whiskers'], color='#333333', linewidth=1)
                plt.setp(box['caps'], color='#333333', linewidth=1)

        # Configure X-Axis
        ax.set_xticks(range(len(present_types)))
        ax.set_xticklabels(present_types, fontsize=11)
        ax.tick_params(axis='x', length=0) # Hide x ticks marks
        
        # Configure Title
        if pm == 'PM10':
            title_str = r'$PM_{10}$'
        elif pm == 'PM2.5':
            title_str = r'$PM_{2.5}$'
        else:
            title_str = r'$PM_{1}$'
        ax.set_title(title_str, fontsize=14, pad=10)
        
        # Grid
        ax.grid(axis='y', linestyle='--', alpha=0.5, color='gray', linewidth=0.7)
        ax.set_axisbelow(True)

    # 4. Global Styling
    
    # Y-Axis Label (only on first plot)
    # Note: Using nmolAA as per the visual label in the image, even though table says nmol
    axes[0].set_ylabel(r'$OP^{AA}_v$ (nmolAA min$^{-1}$ m$^{-3}$)', fontsize=12)
    axes[0].set_ylim(0, 12)
    axes[0].set_yticks(np.arange(0, 13, 2))
    axes[0].tick_params(axis='y', labelsize=11)

    # Add "a)" tag to the first plot
    axes[0].text(0.03, 0.93, 'a)', transform=axes[0].transAxes, 
                 fontsize=14, fontweight='bold', va='top')

    # Legend (only on the last plot)
    legend_patches = [
        mpatches.Patch(facecolor=color_cold, edgecolor='black', label='Cold'),
        mpatches.Patch(facecolor=color_warm, edgecolor='black', label='Warm')
    ]
    
    # Create legend with specific styling
    leg = axes[2].legend(handles=legend_patches, title='Season', loc='upper right', 
                         fontsize=10, title_fontsize=11, framealpha=1, edgecolor='#d0d0d0')
    leg.get_frame().set_linewidth(1.5)

    # Save the plot
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    # Handle command line argument for output filename
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        output_file = "output.png"
    
    generate_chart(output_file)