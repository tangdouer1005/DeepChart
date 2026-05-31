import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def generate_chart(output_filename):
    # 1. Load Source Data
    # The data is embedded directly as a string to ensure the script is self-contained.
    csv_data = """Country|Stage|value
USA|HIC|302.631
USA|HIC|266.816
USA|HIC|263
USA|HIC|245.96
USA|HIC|240.168
USA|HIC|229
USA|HIC|208.636
USA|HIC|178
USA|HIC|175.2
USA|HIC|169.996
Spain|HIC|164
Spain|HIC|164
USA|HIC|158
Portugal|HIC|156.877
Portugal|HIC|133.667
Italy|HIC|131.85
USA|HIC|121.3
South Africa|UMIC|118.794
South Africa|UMIC|118.794
Portugal|HIC|118.18
USA|HIC|117.08
Japan|HIC|112.1
USA|HIC|111
China|UMIC|109
China|UMIC|109
Russia|UMIC|106.333
USA|HIC|106.14
Spain|HIC|106
Portugal|HIC|99.4224
Italy|HIC|99.15
South Africa|UMIC|96.8182
South Africa|UMIC|96.8182
South Africa|UMIC|92.4859
Portugal|HIC|92.2
Latvia|HIC|89.3333
USA|HIC|89.01
South Africa|UMIC|88.7179
South Africa|UMIC|88.7179
USA|HIC|88.23
USA|HIC|88.23
Denmark|HIC|88
Spain|HIC|87
Portugal|HIC|86.366
Thailand|UMIC|85.6
Turkey|UMIC|81.71
USA|HIC|77.3168
China|UMIC|76.5
USA|HIC|76
France|HIC|75.68
Latvia|HIC|75
China|UMIC|73.7
USA|HIC|71.27
Jordan|UMIC|70.1833
USA|HIC|69.069
Brazil|UMIC|69.02
USA|HIC|68.78
China|UMIC|68.56
Japan|HIC|68
Brazil|UMIC|68
China|UMIC|67.58
Italy|HIC|67.3333
Portugal|HIC|66.6667
Latvia|HIC|64.3333
Japan|HIC|63.2
China|UMIC|63
China|UMIC|63
USA|HIC|62.76
China|UMIC|61.03
China|UMIC|61.03
USA|HIC|60.615
Portugal|HIC|58.92
USA|HIC|58.4172
Finland|HIC|58
Latvia|HIC|57.3333
Portugal|HIC|56.856
USA|HIC|56.8
USA|HIC|56.8
UK|HIC|56.35
Turkey|UMIC|56.06
Spain|HIC|55.85
Spain|HIC|55.85
Italy|HIC|54
China|UMIC|53.88
Portugal|HIC|53.5768
Italy|HIC|53.5667
USA|HIC|53.45
Sweden|HIC|53
USA|HIC|52.2
USA|HIC|50.81
Portugal|HIC|50.44
Thailand|UMIC|50
Sweden|HIC|49.46
Sweden|HIC|49.46
Sweden|HIC|49.46
Portugal|HIC|49.02
Latvia|HIC|48.3333
Latvia|HIC|48
France|HIC|47.58
Latvia|HIC|47.3333
Indonesia|LMIC|47.05
UK|HIC|46.96
UK|HIC|46.96
UK|HIC|46.96
Portugal|HIC|46.93
Brazil|UMIC|46.9
Sweden|HIC|46
Japan|HIC|45.8
Sweden|HIC|45
Sweden|HIC|44.89
Sweden|HIC|44.89
Sweden|HIC|44.89
Japan|HIC|44.7
Indonesia|LMIC|44.5
Sweden|HIC|43.43
Sweden|HIC|43.43
Sweden|HIC|43.43
Sweden|HIC|43.4
Sweden|HIC|43.4
Sweden|HIC|43.4
Sweden|HIC|42
USA|HIC|40.97
Sweden|HIC|40
Italy|HIC|40
India|LMIC|40
Russia|UMIC|39.3333
Italy|HIC|39
Portugal|HIC|38.68
Thailand|UMIC|38.4
Turkey|UMIC|38.04
USA|HIC|37.7
USA|HIC|37.7
Portugal|HIC|37.4376
USA|HIC|37.29
Sweden|HIC|37
Sweden|HIC|37
Sweden|HIC|37
Portugal|HIC|35.56
Sweden|HIC|35
Sweden|HIC|35
Sweden|HIC|35
Portugal|HIC|34.8619
Spain|HIC|34
Spain|HIC|34
South Africa|UMIC|33.6158
Portugal|HIC|32.44
Japan|HIC|32.1
Indonesia|LMIC|31.83
Ethiopia|LIC|31.33
Japan|HIC|31
Japan|HIC|30
Japan|HIC|30
Portugal|HIC|29.39
Indonesia|LMIC|27.83
Finland|HIC|27.5
Sweden|HIC|27
Sweden|HIC|27
Sweden|HIC|27
Philippines|LMIC|26.7
USA|HIC|26.2
Sweden|HIC|26.07
Sweden|HIC|25
USA|HIC|24
Sweden|HIC|24
Sweden|HIC|24
Sweden|HIC|24
USA|HIC|23.4
Sweden|HIC|22
Japan|HIC|22
Thailand|UMIC|21.9
Portugal|HIC|21.6
Switzerland|HIC|21.09
Japan|HIC|20
Sweden|HIC|19
Sweden|HIC|19
Sweden|HIC|19
Thailand|UMIC|18.9
USA|HIC|18
USA|HIC|17.9
Sweden|HIC|16.83
Switzerland|HIC|16.77
Malaysia|UMIC|16.2
Sweden|HIC|16
Japan|HIC|11
Malaysia|UMIC|10.6
Malaysia|UMIC|10.2
Japan|HIC|9
Japan|HIC|9
Switzerland|HIC|8.26
Japan|HIC|8
Japan|HIC|8
Malaysia|UMIC|7.7
Malaysia|UMIC|7.7
Malaysia|UMIC|7.6
Malaysia|UMIC|6
Japan|HIC|6
Japan|HIC|6
Malaysia|UMIC|5.6
Philippines|LMIC|5
Japan|HIC|5
Malaysia|UMIC|4.5
Malaysia|UMIC|3.7
Japan|HIC|2
Japan|HIC|1
Japan|HIC|1
Japan|HIC|1"""

    # Parse CSV data
    df = pd.read_csv(io.StringIO(csv_data), sep="|")
    
    # Clean column names and data
    df.columns = [c.strip() for c in df.columns]
    df['Country'] = df['Country'].str.strip()
    df['Stage'] = df['Stage'].str.strip()
    
    # Define the specific order of categories
    stage_order = ['LIC', 'LMIC', 'UMIC', 'HIC']
    
    # 2. Setup Plotting Style
    # Set a style that mimics the clean scientific look
    sns.set_style("ticks")
    sns.set_context("talk") # Larger fonts
    
    # Create figure
    fig, ax = plt.subplots(figsize=(7, 6))
    
    # 3. Calculate Statistics for Bar Chart
    # We need Mean and Standard Error of the Mean (SEM)
    means = df.groupby('Stage')['value'].mean().reindex(stage_order)
    sems = df.groupby('Stage')['value'].sem().reindex(stage_order)
    
    # Handle NaN for SEM if a group has only 1 item (LIC) by replacing with 0
    sems = sems.fillna(0)

    # 4. Draw Bar Chart (Background)
    # Light gray bars with black edges
    ax.bar(stage_order, means, 
           yerr=sems, 
           capsize=8,          # Width of the error bar caps
           color='#E0E0E0',    # Light gray fill
           edgecolor='black',  # Black border
           linewidth=1,        # Border thickness
           error_kw={'linewidth': 1, 'color': 'black'}, # Error bar style
           width=0.5,          # Bar width
           zorder=1)           # Draw behind points

    # 5. Draw Strip Plot (Foreground Points)
    # Define custom color palette to match the image
    # LIC: Peach/Orange, LMIC: Pink/Mauve, UMIC: Yellow-Green, HIC: Teal/Green
    custom_palette = {
        'LIC': '#FDBF6F',  # Soft Orange
        'LMIC': '#E78AC3', # Soft Pink/Purple
        'UMIC': '#B2DF8A', # Soft Yellow-Green
        'HIC': '#66C2A5'   # Soft Teal
    }

    sns.stripplot(data=df, x='Stage', y='value', order=stage_order,
                  palette=custom_palette,
                  size=10,              # Large points
                  alpha=0.5,            # Semi-transparent
                  linewidth=1,          # Border around points
                  edgecolor='#404040',  # Dark gray border for points
                  jitter=0.25,          # Spread width
                  ax=ax,
                  zorder=2)             # Draw on top of bars

    # 6. Formatting and Styling
    
    # Y-Axis Label
    ax.set_ylabel("Plate waste amount (g per capita per meal)", fontsize=14, color='black')
    ax.set_xlabel("") # No X label needed as categories are self-explanatory
    
    # Y-Axis Ticks
    ax.set_ylim(0, 320)
    ax.set_yticks(np.arange(0, 321, 40))
    
    # Remove top and right spines (borders)
    sns.despine()
    
    # Add the bold "a" title in the top left corner
    # Using text coordinates relative to axes (0,0 is bottom-left, 1,1 is top-right)
    ax.text(-0.15, 1.0, 'a', transform=ax.transAxes, 
            fontsize=20, fontweight='bold', va='top', ha='right')

    # Adjust layout to prevent clipping
    plt.tight_layout()
    
    # 7. Save Output
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    # Handle command line argument for output filename
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        output_file = "output.png"
        
    generate_chart(output_file)