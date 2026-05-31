import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# 1. Source Data (Embedded exactly as provided)
csv_data = """
| UF   |   Total |         Domestic |            China |               EU |   Other_countries | Biome          |
|:-----|--------:|-----------------:|-----------------:|-----------------:|------------------:|:---------------|
| RO   |  338642 | 150386           |      0           | 104896           |   41127.9         | AMAZÔNIA       |
| AC   |    3280 |   3279.86        |      0           |      0           |       0           | AMAZÔNIA       |
| AM   |    2700 |   2699.97        |      0           |      0           |       0           | AMAZÔNIA       |
| RR   |   49800 |  49800           |      0           |      0           |       0           | AMAZÔNIA       |
| PA   |  634831 |      0           |  85888.5         | 126133           |  140613           | AMAZÔNIA       |
| AP   |   20300 |      0           |      0           |      0           |       0           | AMAZÔNIA       |
| TO   |   24274 |   6425.91        |   4051.05        |    764.353       |    1463.07        | AMAZÔNIA       |
| MA   |  137374 |  49119.9         |  11034.4         |   3487.91        |    3623.39        | AMAZÔNIA       |
| MT   | 4228843 | 186657           | 883894           | 398242           |       1.01623e+06 | AMAZÔNIA       |
| RO   |   54000 |      0           |    179.011       |  37988.4         |   15254.7         | CERRADO        |
| PA   |    8436 |      0           |      0           |      0           |       0           | CERRADO        |
| TO   |  943325 | 119698           | 383314           |  59737.4         |  140541           | CERRADO        |
| MA   |  823526 |  13323           | 449035           |  81298.9         |   91124.4         | CERRADO        |
| PI   |  757978 | 105178           | 182462           |  29943.5         |   52557.6         | CERRADO        |
| BA   | 1614550 | 251491           | 597877           | 345972           |  160695           | CERRADO        |
| MG   | 1427871 | 227638           | 584290           |  63274.4         |  280472           | CERRADO        |
| SP   |  414415 |  73593.3         | 245878           |   7796.82        |   68113.9         | CERRADO        |
| PR   |   41100 |  14176.4         |  25019.9         |      0           |    1514.64        | CERRADO        |
| MS   | 2416981 | 543300           |      1.18335e+06 | 276129           |  317171           | CERRADO        |
| MT   | 5760806 | 968009           |      2.00269e+06 | 528306           |       1.4266e+06  | CERRADO        |
| GO   | 3576103 |      1.10374e+06 |      1.538e+06   | 245174           |  489912           | CERRADO        |
| DF   |   74500 |  41978.8         |  28653.7         |     44.4968      |    2926.13        | CERRADO        |
| PI   |       0 |      0           |      0           |      0           |       0           | CAATINGA       |
| CE   |     450 |      0           |    449.547       |      0           |       0           | CAATINGA       |
| RN   |       0 |      0           |      0           |      0           |       0           | CAATINGA       |
| PB   |       0 |      0           |      0           |      0           |       0           | CAATINGA       |
| PE   |       0 |      0           |      0           |      0           |       0           | CAATINGA       |
| AL   |       0 |      0           |      0           |      0           |       0           | CAATINGA       |
| SE   |       0 |      0           |      0           |      0           |       0           | CAATINGA       |
| BA   |    7925 |   6470.26        |   1449.99        |      0           |       0           | CAATINGA       |
| MG   |    1390 |      0           |     89.8935      |      0           |      57.6345      | CAATINGA       |
| RN   |       0 |      0           |      0           |      0           |       0           | MATA ATLÂNTICA |
| PB   |       0 |      0           |      0           |      0           |       0           | MATA ATLÂNTICA |
| PE   |       0 |      0           |      0           |      0           |       0           | MATA ATLÂNTICA |
| AL   |    1224 |      0           |   1221.64        |      0           |       0           | MATA ATLÂNTICA |
| SE   |       0 |      0           |      0           |      0           |       0           | MATA ATLÂNTICA |
| BA   |       0 |      0           |      0           |      0           |       0           | MATA ATLÂNTICA |
| MG   |  266441 |  88147.7         |  96966.3         |   7324.07        |   38202.8         | MATA ATLÂNTICA |
| ES   |       0 |      0           |      0           |      0           |       0           | MATA ATLÂNTICA |
| RJ   |       0 |      0           |      0           |      0           |       0           | MATA ATLÂNTICA |
| SP   |  718550 | 155578           | 368910           |  50870.3         |   74352.9         | MATA ATLÂNTICA |
| PR   | 5493743 |      1.27815e+06 |      2.9639e+06  | 482759           |  567806           | MATA ATLÂNTICA |
| SC   |  664795 | 129116           | 412226           |  38743           |   59429.4         | MATA ATLÂNTICA |
| RS   | 1864870 | 813182           | 818890           |  38723           |  106262           | MATA ATLÂNTICA |
| MS   |  704541 | 170630           | 310075           | 107695           |   71153.8         | MATA ATLÂNTICA |
| GO   |    1597 |   1551.34        |      0           |      0           |       0           | MATA ATLÂNTICA |
| RS   | 4131501 | 907101           |      2.56704e+06 | 150768           |  342051           | PAMPA          |
| MS   |       0 |      0           |      0           |      0           |       0           | PANTANAL       |
| MT   |       0 |      0           |      0           |      0           |       0           | PANTANAL       |
| nan  |       0 |     74.5038      |      2.05422e+06 |      1.71344e+06 |       1.65472e+06 | nan            |
"""

def process_data(csv_text):
    # Read CSV from string, handling the markdown pipe format
    df = pd.read_csv(io.StringIO(csv_text), sep='|', skipinitialspace=True)
    
    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Drop the first and last columns which are empty due to markdown pipes
    df = df.iloc[:, 1:-1]
    
    # Handle the "NA" row (last row in source)
    # The source has 'nan' for UF and Biome in the last row.
    df['UF'] = df['UF'].astype(str).str.strip()
    df['Biome'] = df['Biome'].astype(str).str.strip()
    
    # Replace string 'nan' with actual NA logic for the chart
    df.loc[df['UF'] == 'nan', 'UF'] = 'NA'
    df.loc[df['Biome'] == 'nan', 'Biome'] = 'NA'
    
    # Convert numeric columns
    numeric_cols = ['Total', 'Domestic', 'China', 'EU', 'Other_countries']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    # Scale to Millions (as per chart axis 1.5, 3, 4.5, 6)
    for col in numeric_cols:
        df[col] = df[col] / 1_000_000
        
    return df

def generate_chart(df, output_path):
    # Define Biome Order (Clockwise starting from top-ish)
    # Based on visual inspection: Amazônia -> Pantanal -> Cerrado -> Caatinga -> Pampa -> Mata Atlântica -> NA
    biome_order = ['AMAZÔNIA', 'PANTANAL', 'CERRADO', 'CAATINGA', 'PAMPA', 'MATA ATLÂNTICA', 'NA']
    
    # Sort Data
    df['Biome'] = pd.Categorical(df['Biome'], categories=biome_order, ordered=True)
    # Secondary sort by UF (alphabetical seems to match most groups)
    df = df.sort_values(by=['Biome', 'UF'])
    
    # Setup Plot
    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(111, projection='polar')
    
    # Configuration
    OFFSET_RADIUS = 2.0  # Inner hole radius
    MAX_RADIUS = 6.5     # Outer limit
    BAR_WIDTH_FACTOR = 0.9 # Gap between bars
    BIOME_GAP = 0.15     # Gap between biomes in radians
    
    # Colors (matched from image)
    colors = {
        'Domestic': '#9ecae1', # Light Blue
        'China': '#5f9ea0',    # Teal/CadetBlue
        'EU': '#fdbf6f',       # Light Orange
        'Other_countries': '#d0746c' # Salmon/Red
    }
    stack_order = ['Domestic', 'China', 'EU', 'Other_countries']
    
    # Calculate Angles
    # We need to distribute bars around the circle, adding gaps between biomes
    
    # Count items per biome
    biome_counts = df['Biome'].value_counts()[biome_order]
    total_bars = len(df)
    num_biomes = len(biome_order)
    
    # Total available angle (2pi) minus gaps
    total_angle = 2 * np.pi - (num_biomes * BIOME_GAP)
    angle_per_bar = total_angle / total_bars
    
    # Assign angles to each row
    df['theta'] = 0.0
    current_angle = 0.0
    
    # Start slightly offset to align Amazônia at the top right (approx 12:30 position)
    # Matplotlib polar: 0 is East, counter-clockwise.
    # We want Clockwise.
    ax.set_theta_direction(-1)
    ax.set_theta_zero_location("N") # 0 is North
    
    # Adjust start angle to match image (Amazônia starts a bit after 12:00)
    current_angle = 0.1 
    
    biome_angles = {} # Store start/end for labels
    
    for biome in biome_order:
        biome_data = df[df['Biome'] == biome]
        start_angle = current_angle
        
        for idx, row in biome_data.iterrows():
            df.at[idx, 'theta'] = current_angle + (angle_per_bar / 2)
            current_angle += angle_per_bar
            
        end_angle = current_angle
        biome_angles[biome] = (start_angle, end_angle)
        current_angle += BIOME_GAP
        
    # Plot Bars
    for idx, row in df.iterrows():
        angle = row['theta']
        bottom = OFFSET_RADIUS
        
        for cat in stack_order:
            height = row[cat]
            if height > 0:
                ax.bar(angle, height, width=angle_per_bar * BAR_WIDTH_FACTOR, 
                       bottom=bottom, color=colors[cat], edgecolor='none', linewidth=0)
                bottom += height
        
        # UF Labels
        # Only label if there is data or if it's a specific placeholder in the chart
        # The chart shows labels even for small bars.
        label_radius = bottom + 0.1
        
        # Rotation logic: flip text if on the left side of the circle
        # Normalized angle in degrees [0, 360]
        deg = np.degrees(angle) % 360
        
        rotation = 90 - deg # Adjust for N zero and CW direction
        
        # Alignment adjustments based on quadrant
        if 90 < deg < 270:
            rotation += 180
            ha = 'right'
            va = 'center'
            label_radius += 0.05 # Push out slightly more
        else:
            ha = 'left'
            va = 'center'
            
        ax.text(angle, label_radius, row['UF'], rotation=rotation, 
                ha=ha, va=va, fontsize=11, color='#666666', rotation_mode='anchor')

    # Biome Labels and Arcs
    for biome, (start, end) in biome_angles.items():
        mid_angle = (start + end) / 2
        
        # Draw the curved line (arc) inside
        arc_radius = OFFSET_RADIUS - 0.2
        
        # Create theta range for the arc
        theta_range = np.linspace(start, end - (angle_per_bar*0.1), 50)
        ax.plot(theta_range, [arc_radius]*len(theta_range), color='black', linewidth=1.2)
        
        # Place Text
        # Adjust rotation for text
        deg = np.degrees(mid_angle) % 360
        rotation = 90 - deg
        
        # Specific adjustments for readability
        text_radius = arc_radius - 0.3
        
        # Flip text at bottom
        if 90 < deg < 270:
            rotation += 180
            
        # Title Case for Biomes (except NA)
        label_text = biome.title() if biome != 'NA' else 'NA'
        
        ax.text(mid_angle, text_radius, label_text, 
                ha='center', va='center', rotation=rotation, 
                fontsize=12, color='black')

    # Custom Grid Lines
    # Draw dashed circles at 1.5, 3.0, 4.5, 6.0 (plus offset)
    grid_values = [1.5, 3.0, 4.5, 6.0]
    for val in grid_values:
        r = OFFSET_RADIUS + val
        # Draw circle manually to control style
        theta_grid = np.linspace(0, 2*np.pi, 200)
        ax.plot(theta_grid, [r]*len(theta_grid), color='#cccccc', linestyle='-', linewidth=0.8, zorder=0)
        
        # Add value label at the top (North)
        ax.text(0, r, str(val), ha='center', va='center', color='#cccccc', fontsize=12, backgroundcolor='white')

    # Add "0" label
    ax.text(0, OFFSET_RADIUS, "0", ha='center', va='center', color='#cccccc', fontsize=12, backgroundcolor='white')

    # Styling
    ax.set_ylim(0, MAX_RADIUS + OFFSET_RADIUS)
    ax.axis('off') # Turn off default axis
    
    # Title
    plt.text(0.05, 0.95, "2020", transform=fig.transFigure, fontsize=20, ha='left')
    
    # Save
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    
    df_clean = process_data(csv_data)
    generate_chart(df_clean, output_file)