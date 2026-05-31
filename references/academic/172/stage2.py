import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def generate_chart(output_filename):
    # 1. Load Source Data
    # Using the exact data provided in the prompt
    csv_data = """Stage|value
preschool|302.631
preschool|266.816
primary school|263
preschool|245.96
preschool|240.168
secondary school|229
preschool|208.636
secondary school|178
primary school|175.2
preschool|169.996
primary school|164
primary school|164
secondary school|158
primary school|156.877
primary school|133.667
primary school|131.85
primary school|121.3
university|118.794
university|118.794
university|118.18
university|117.08
primary school|112.1
university|111
secondary school|109
secondary school|109
preschool|106.333
university|106.14
primary school|106
primary school|99.4224
primary school|99.15
university|96.8182
university|96.8182
university|92.4859
university|92.2
secondary school|89.3333
university|89.01
university|88.7179
university|88.7179
university|88.23
university|88.23
primary school|88
preschool|87
primary school|86.366
preschool|85.6
university|81.71
university|77.3168
university|76.5
university|76
secondary school|75.68
primary school|75
university|73.7
university|71.27
university|70.1833
university|69.069
preschool|69.02
university|68.78
university|68.56
university|68
primary school|68
university|67.58
primary school|67.3333
university|66.6667
secondary school|64.3333
primary school|63.2
secondary school|63
secondary school|63
university|62.76
university|61.03
university|61.03
primary school|60.615
university|58.92
primary school|58.4172
university|58
secondary school|57.3333
primary school|56.856
university|56.8
university|56.8
university|56.35
university|56.06
secondary school|55.85
secondary school|55.85
secondary school|54
university|53.88
primary school|53.5768
primary school|53.5667
preschool|53.45
preschool|53
secondary school|52.2
university|50.81
university|50.44
preschool|50
secondary school|49.46
secondary school|49.46
primary school|49.46
university|49.02
secondary school|48.3333
secondary school|48
secondary school|47.58
secondary school|47.3333
university|47.05
secondary school|46.96
secondary school|46.96
primary school|46.96
university|46.93
university|46.9
secondary school|46
primary school|45.8
secondary school|45
secondary school|44.89
secondary school|44.89
primary school|44.89
primary school|44.7
university|44.5
secondary school|43.43
secondary school|43.43
primary school|43.43
secondary school|43.4
secondary school|43.4
primary school|43.4
primary school|42
university|40.97
university|40
primary school|40
preschool|40
preschool|39.3333
preschool|39
university|38.68
primary school|38.4
university|38.04
university|37.7
university|37.7
university|37.4376
university|37.29
secondary school|37
secondary school|37
primary school|37
university|35.56
secondary school|35
secondary school|35
primary school|35
university|34.8619
primary school|34
primary school|34
university|33.6158
university|32.44
primary school|32.1
university|31.83
university|31.33
primary school|31
primary school|30
primary school|30
university|29.39
university|27.83
university|27.5
secondary school|27
secondary school|27
primary school|27
secondary school|26.7
university|26.2
primary school|26.07
secondary school|25
university|24
secondary school|24
secondary school|24
primary school|24
university|23.4
primary school|22
preschool|22
primary school|21.9
university|21.6
university|21.09
primary school|20
secondary school|19
secondary school|19
primary school|19
university|18.9
university|18
university|17.9
preschool|16.83
university|16.77
primary school|16.2
primary school|16
primary school|11
primary school|10.6
primary school|10.2
primary school|9
primary school|9
university|8.26
primary school|8
primary school|8
secondary school|7.7
primary school|7.7
secondary school|7.6
primary school|6
primary school|6
primary school|6
secondary school|5.6
secondary school|5
primary school|5
primary school|4.5
primary school|3.7
primary school|2
primary school|1
primary school|1
primary school|1"""

    # Read data into pandas DataFrame
    df = pd.read_csv(io.StringIO(csv_data), sep="|")
    
    # Clean whitespace
    df.columns = df.columns.str.strip()
    df['Stage'] = df['Stage'].str.strip()

    # 2. Data Preprocessing
    # Map raw categories to the specific labels in the chart (including newlines)
    label_map = {
        'preschool': 'Preschool',
        'primary school': 'Primary\nschool',
        'secondary school': 'Secondary\nschool',
        'university': 'University'
    }
    df['Stage'] = df['Stage'].map(label_map)

    # Define the specific order of categories
    order = ['Preschool', 'Primary\nschool', 'Secondary\nschool', 'University']

    # 3. Setup Plot
    # Set figure size and resolution
    fig, ax = plt.subplots(figsize=(7, 6), dpi=150)

    # Define custom colors to match the image
    # Preschool: Muted Blue, Primary: Muted Purple, Secondary: Pale Yellow, University: Brown/Orange
    palette = {
        'Preschool': '#8da0cb',       
        'Primary\nschool': '#bebada', 
        'Secondary\nschool': '#ffffb3', 
        'University': '#bf812d'       
    }

    # 4. Plotting
    
    # A. Bar Plot (The underlying grey bars showing the mean)
    # Note: The image uses Standard Error (SE) for error bars based on visual inspection
    sns.barplot(
        data=df, 
        x='Stage', 
        y='value', 
        order=order,
        color='#d9d9d9',  # Light grey fill
        edgecolor='black', # Black border
        linewidth=1,
        errorbar='se',    # Standard Error
        capsize=0.15,     # Caps on error bars
        err_kws={'color': 'black', 'linewidth': 1},
        ax=ax,
        zorder=1
    )

    # B. Strip Plot (The jittered points)
    sns.stripplot(
        data=df, 
        x='Stage', 
        y='value', 
        order=order,
        hue='Stage',      # Color by stage
        palette=palette,
        jitter=0.25,      # Spread points horizontally
        size=9,           # Point size
        alpha=0.6,        # Transparency
        edgecolor='#555555', # Dark grey/black outline around points
        linewidth=1,
        legend=False,     # No legend needed
        ax=ax,
        zorder=2
    )

    # 5. Styling and Layout

    # Remove top and right spines (borders)
    sns.despine()

    # Y-Axis formatting
    ax.set_ylabel("Plate waste amount (g per capita per meal)", fontsize=12, color='black')
    ax.set_ylim(0, 320)
    ax.set_yticks(range(0, 321, 40))
    
    # X-Axis formatting
    ax.set_xlabel("") # No label for X-axis, just category names
    ax.tick_params(axis='x', labelsize=11)
    ax.tick_params(axis='y', labelsize=11)
    
    # Configure tick marks to point outwards
    ax.tick_params(direction='out', length=4, width=1, color='black')

    # Add the figure label "c" in the top left
    # We place it relative to the axes coordinates
    ax.text(-0.12, 1.0, 'c', transform=ax.transAxes, 
            fontsize=18, fontweight='bold', va='top', ha='right')

    # Adjust layout to prevent clipping
    plt.tight_layout()

    # 6. Save Output
    plt.savefig(output_filename, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    # Handle command line argument for output filename
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        output_file = "output.png"
    
    generate_chart(output_file)