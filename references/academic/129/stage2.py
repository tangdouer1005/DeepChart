import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

# 1. Source Data embedded as a string
csv_data = """
|   Unnamed: 0 | Unnamed: 1                                                                         |
|-------------:|:-----------------------------------------------------------------------------------|
|          nan | Figure 4:                                                                          |
|          nan | Data on land use for soybeans in Brazil are reported in this file (unit: hectares) |
| UF   |   Total |         Domestic |       China |               EU |   Other_countries | Biome          |
| RO   |   24443 |  24443           |      0      |      0           |       0           | AMAZÔNIA       |
| AC   |       0 |      0           |      0      |      0           |       0           | AMAZÔNIA       |
| AM   |    2306 |   2300           |      0      |      0           |       0           | AMAZÔNIA       |
| RR   |   12000 |  12000           |      0      |      0           |       0           | AMAZÔNIA       |
| PA   |   33569 |      0           |      0      |   9883.44        |     706.923       | AMAZÔNIA       |
| AP   |       0 |      0           |      0      |      0           |       0           | AMAZÔNIA       |
| TO   |     770 |      0           |      0      |    400           |       0           | AMAZÔNIA       |
| MA   |       0 |      0           |      0      |      0           |       0           | AMAZÔNIA       |
| MT   |  739637 |      0           |  12383.7    |  39923.2         |   31156.7         | AMAZÔNIA       |
| RO   |   32000 |  32000           |      0      |      0           |       0           | CERRADO        |
| PA   |    1650 |      0           |      0      |      0           |       0           | CERRADO        |
| TO   |  253496 |      0           |  13234.1    | 110071           |    1672.52        | CERRADO        |
| MA   |  340403 |  34823.4         |  32304.6    |  88251.1         |   85365.5         | CERRADO        |
| PI   |  159281 |  78509.1         |    275.173  |  43959.1         |       0           | CERRADO        |
| BA   |  821000 | 211106           |      0      | 372659           |   96905.2         | CERRADO        |
| MG   |  950966 | 207090           |  46848.5    | 561802           |   86352.6         | CERRADO        |
| SP   |  231909 | 131597           |  16812.3    |  51190.7         |   23181.3         | CERRADO        |
| PR   |   55000 |  42590           |  12385.2    |      0           |       0           | CERRADO        |
| MS   | 1318891 | 365389           |  17253      | 346641           |  106072           | CERRADO        |
| MT   | 4540291 | 805247           | 221864      |      1.06649e+06 |  437541           | CERRADO        |
| GO   | 2588954 | 778464           | 160175      |      1.23922e+06 |  215061           | CERRADO        |
| DF   |   50383 |  20342.1         |    694.108  |  17208.7         |   11437.6         | CERRADO        |
| PI   |       0 |      0           |      0      |      0           |       0           | CAATINGA       |
| CE   |     350 |      0           |     67.2402 |    282.76        |       0           | CAATINGA       |
| RN   |       0 |      0           |      0      |      0           |       0           | CAATINGA       |
| PB   |       0 |      0           |      0      |      0           |       0           | CAATINGA       |
| PE   |       0 |      0           |      0      |      0           |       0           | CAATINGA       |
| AL   |     171 |      0           |     19.2115 |    138.155       |       0           | CAATINGA       |
| SE   |       0 |      0           |      0      |      0           |       0           | CAATINGA       |
| BA   |     270 |      0           |      0      |     24.5164      |       0           | CAATINGA       |
| MG   |      41 |      0           |      0      |      0           |       0           | CAATINGA       |
| RN   |       0 |      0           |      0      |      0           |       0           | MATA ATLÂNTICA |
| PB   |       0 |      0           |      0      |      0           |       0           | MATA ATLÂNTICA |
| PE   |       0 |      0           |      0      |      0           |       0           | MATA ATLÂNTICA |
| AL   |      30 |      0           |      0      |     24.2366      |       0           | MATA ATLÂNTICA |
| SE   |       0 |      0           |      0      |      0           |       0           | MATA ATLÂNTICA |
| BA   |       0 |      0           |      0      |      0           |       0           | MATA ATLÂNTICA |
| MG   |  145416 |  35739.6         |  13139.4    |  71533.8         |   17831.5         | MATA ATLÂNTICA |
| ES   |       0 |      0           |      0      |      0           |       0           | MATA ATLÂNTICA |
| RJ   |       0 |      0           |      0      |      0           |       0           | MATA ATLÂNTICA |
| SP   |  547971 | 197746           |  66327.3    | 165683           |   86614.9         | MATA ATLÂNTICA |
| PR   | 3956021 |      1.38135e+06 | 709033      |      1.14325e+06 |  669558           | MATA ATLÂNTICA |
| SC   |  314469 | 139741           |  41986      |  52740.3         |   67362.3         | MATA ATLÂNTICA |
| RS   | 1536638 | 544845           | 357305      | 191569           |  390989           | MATA ATLÂNTICA |
| MS   |  493115 | 173247           |  56374.5    | 150083           |   66407.6         | MATA ATLÂNTICA |
| GO   |    3000 |   2000           |    431.876  |      0           |     568.124       | MATA ATLÂNTICA |
| RS   | 2447699 | 646075           | 504690      | 410547           |  830028           | PAMPA          |
| MS   |       0 |      0           |      0      |      0           |       0           | PANTANAL       |
| MT   |       0 |      0           |      0      |      0           |       0           | PANTANAL       |
| nan  |       0 |    106.087       | 747449      |      2.69633e+06 |       1.07016e+06 | nan            |
"""

def clean_and_load_data(csv_text):
    # Read the raw text, skipping the first few lines of metadata manually
    lines = csv_text.strip().split('\n')
    
    # Find the header line (starts with | UF)
    header_idx = 0
    for i, line in enumerate(lines):
        if '| UF' in line:
            header_idx = i
            break
            
    # Extract relevant lines
    data_lines = lines[header_idx:]
    data_str = '\n'.join(data_lines)
    
    # Read into pandas
    df = pd.read_csv(io.StringIO(data_str), sep='|', skipinitialspace=True)
    
    # Clean column names (remove whitespace and empty columns from markdown pipes)
    df.columns = [c.strip() for c in df.columns]
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Clean string columns
    df['UF'] = df['UF'].astype(str).str.strip()
    df['Biome'] = df['Biome'].astype(str).str.strip()
    
    # Handle the last row (NA/nan)
    # The last row has 'nan' in the first column in the source string
    df.loc[df['Biome'] == 'nan', 'Biome'] = 'NA'
    df.loc[df['UF'] == 'nan', 'UF'] = 'NA'
    
    # Convert numeric columns
    numeric_cols = ['Total', 'Domestic', 'China', 'EU', 'Other_countries']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        # Convert to Millions
        df[col] = df[col] / 1_000_000
        
    return df

def get_chart_colors():
    # Colors approximated from the image
    return {
        'Domestic': '#9AC9DB',  # Light Blue
        'China': '#F0AB56',     # Orange/Yellow
        'EU': '#539093',        # Teal/Green
        'Other': '#D67D6B'      # Salmon/Red
    }

def main():
    # Handle output filename
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]

    # 1. Prepare Data
    df = clean_and_load_data(csv_data)
    
    # Define the specific order of Biomes as seen in the chart (Clockwise)
    # Amazônia -> Pantanal -> Cerrado -> Caatinga -> Pampa -> Mata Atlântica -> NA
    biome_order = ['AMAZÔNIA', 'PANTANAL', 'CERRADO', 'CAATINGA', 'PAMPA', 'MATA ATLÂNTICA', 'NA']
    
    # Sort Data
    df['Biome'] = pd.Categorical(df['Biome'], categories=biome_order, ordered=True)
    df = df.sort_values(by=['Biome', 'UF'])
    
    # 2. Setup Polar Plot Parameters
    # Constants
    OFFSET = 2.5  # Radius of the inner white circle
    MAX_HEIGHT = 6.0 # Max value on scale
    BAR_WIDTH = 1.0 # Relative width
    GROUP_GAP = 4.0 # Gap between biomes
    
    # Calculate angles
    # We need to assign an angular width to every row.
    # Total units = (Number of rows * BAR_WIDTH) + (Number of groups * GROUP_GAP)
    n_rows = len(df)
    n_groups = len(biome_order)
    total_units = (n_rows * BAR_WIDTH) + (n_groups * GROUP_GAP)
    
    # Calculate theta for each bar
    # We want to start slightly clockwise from top (approx 12:30 position)
    # In polar coordinates, 0 is East (3 o'clock). 
    # We will set theta_offset to pi/2 (12 o'clock) and direction -1 (clockwise).
    
    current_angle = 0
    angles = []
    widths = []
    
    # To store group label positions
    group_angles = {} 
    
    last_biome = None
    
    # Iterate to calculate positions
    for i, row in df.iterrows():
        biome = row['Biome']
        
        # Add gap if new biome
        if biome != last_biome:
            if last_biome is not None:
                current_angle += (GROUP_GAP * 2 * np.pi / total_units)
            
            group_start_angle = current_angle
            last_biome = biome
        
        # Calculate bar width in radians
        w = (BAR_WIDTH * 2 * np.pi / total_units)
        
        # Store angle (center of the bar)
        angles.append(current_angle + w/2)
        widths.append(w * 0.8) # Make bars slightly thinner than the slot for spacing
        
        # Update group end angle
        group_angles[biome] = (group_start_angle, current_angle + w)
        
        current_angle += w

    df['theta'] = angles
    df['width'] = widths

    # 3. Plotting
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
    
    # Set orientation: Start at top, go clockwise
    ax.set_theta_offset(np.pi / 2 - 0.2) # -0.2 to shift start slightly right like image
    ax.set_theta_direction(-1)
    
    # Set Y limits (Inner hole and outer limit)
    # We shift everything by OFFSET so the bars start at radius OFFSET
    ax.set_ylim(0, MAX_HEIGHT + OFFSET)
    ax.set_rorigin(-OFFSET) # This creates the hole in the middle
    
    colors = get_chart_colors()
    
    # Draw Bars
    # Stack order: Domestic, China, EU, Other
    bottoms = np.zeros(len(df))
    
    # Domestic
    ax.bar(df['theta'], df['Domestic'], width=df['width'], bottom=bottoms, 
           color=colors['Domestic'], edgecolor='none', label='Domestic')
    bottoms += df['Domestic']
    
    # China
    ax.bar(df['theta'], df['China'], width=df['width'], bottom=bottoms, 
           color=colors['China'], edgecolor='none', label='China')
    bottoms += df['China']
    
    # EU
    ax.bar(df['theta'], df['EU'], width=df['width'], bottom=bottoms, 
           color=colors['EU'], edgecolor='none', label='EU')
    bottoms += df['EU']
    
    # Other
    ax.bar(df['theta'], df['Other_countries'], width=df['width'], bottom=bottoms, 
           color=colors['Other'], edgecolor='none', label='Other')

    # 4. Labels and Styling
    
    # UF Labels (Inner Ring)
    for i, row in df.iterrows():
        angle_rad = row['theta']
        angle_deg = np.degrees(angle_rad)
        
        # Adjust rotation for readability
        # Since we rotated the plot origin, we need to calculate absolute rotation relative to screen
        # The plot starts at 90deg and goes clockwise.
        # Screen angle = 90 - 0.2(rad_to_deg) - angle_deg
        
        # Simplified logic:
        # In standard polar (0 is East, CCW):
        # We mapped our data to specific radians.
        # We need to rotate text so it points outwards.
        
        # Calculate the actual screen rotation of the bar
        # Start (90) - Offset - Angle
        screen_angle = 90 - np.degrees(0.2) - np.degrees(angle_rad)
        
        # Normalize to 0-360
        screen_angle = screen_angle % 360
        
        rotation = screen_angle
        
        # Flip text if it's on the left side of the circle
        if 90 < screen_angle < 270:
            rotation += 180
            alignment = 'right'
            padding = 0.1
        else:
            alignment = 'left'
            padding = 0.1
            
        # Place text just inside the 0 line (which is actually radius 0 in data coords)
        # But visually it's at radius 0 relative to bars.
        # We use a negative y value slightly to put it inside the ring
        ax.text(angle_rad, -0.2, row['UF'], 
                ha='center', va='center', 
                rotation=rotation, rotation_mode='anchor',
                fontsize=9, color='#555555')

    # Biome Labels (Curved Lines)
    for biome, (start, end) in group_angles.items():
        mid = (start + end) / 2
        
        # Draw the arc line
        # We draw a line at radius = -0.8 (inside UF labels)
        arc_radius = -1.0
        
        # Create points for the arc
        theta_range = np.linspace(start, end, 50)
        r_range = [arc_radius] * 50
        ax.plot(theta_range, r_range, color='black', linewidth=1, alpha=0.8)
        
        # Place Label
        # Calculate screen angle for rotation logic
        screen_angle = 90 - np.degrees(0.2) - np.degrees(mid)
        screen_angle = screen_angle % 360
        
        rotation = screen_angle
        # Text follows the curve roughly
        if 90 < screen_angle < 270:
            rotation += 180
            va = 'bottom' # Text inside line
        else:
            va = 'top' # Text inside line (visually outside relative to center)
            
        # Adjust text placement slightly further in
        text_radius = arc_radius - 0.3
        
        # Title Case for Biomes
        label_text = biome.title()
        if label_text == 'Na': label_text = 'NA'
        
        ax.text(mid, text_radius, label_text, 
                ha='center', va='center', 
                rotation=rotation, rotation_mode='anchor',
                fontsize=10, color='black')

    # 5. Grid and Axes
    ax.axis('off') # Turn off default polar axis
    
    # Draw custom grid lines (circles)
    grid_values = [1.5, 3.0, 4.5, 6.0]
    for val in grid_values:
        # Draw circle
        theta = np.linspace(0, 2*np.pi, 100)
        r = [val] * 100
        ax.plot(theta, r, color='#cccccc', linestyle='-', linewidth=0.8, alpha=0.5)
        
        # Add label at the top (near 12 o'clock)
        # We place it at angle 0 (relative to our offset) which is top
        ax.text(0, val, str(val), ha='center', va='center', 
                fontsize=9, color='#999999', backgroundcolor='white')

    # Add Title
    plt.text(0.05, 0.95, "2004", transform=fig.transFigure, fontsize=16, color='black')

    # Save
    plt.savefig(output_file, bbox_inches='tight', dpi=300)

if __name__ == "__main__":
    main()