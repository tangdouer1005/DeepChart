import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# 1. Source Data embedded as a string
SOURCE_DATA = """
|   Unnamed: 0 | Unnamed: 1                                                                                  |
|-------------:|:--------------------------------------------------------------------------------------------|
|          nan | Figure 5:                                                                                   |
|          nan | Data on water use for soybeans in Brazil are reported in this file (unit: cubic kilometers) |

# 2012
| UF   |       Total |    Domestic |       China |          EU |   Other countries | Biome          |
|:-----|------------:|------------:|------------:|------------:|------------------:|:---------------|
| RO   |  0.489138   | 0.162627    | 0           | 0.270817    |       0.0553949   | AMAZÔNIA       |
| AC   |  0          | 0           | 0           | 0           |       0           | AMAZÔNIA       |
| AM   |  0.00100049 | 0.00100049  | 0           | 0           |       0           | AMAZÔNIA       |
| RR   |  0.0212041  | 0.0211216   | 0           | 0           |       8.25081e-05 | AMAZÔNIA       |
| PA   |  0.460453   | 0.0463854   | 0.0832068   | 0.240372    |       0.0644473   | AMAZÔNIA       |
| AP   |  0          | 0           | 0           | 0           |       0           | AMAZÔNIA       |
| TO   |  0.00681717 | 0           | 0.000903865 | 0.0059133   |       0           | AMAZÔNIA       |
| MA   |  0.00121452 | 0           | 0.000570446 | 0.000186396 |       0.00025902  | AMAZÔNIA       |
| MT   |  8.35218    | 1.15457     | 2.58274     | 0.98045     |       0.900024    | AMAZÔNIA       |
| RO   |  0.185048   | 0           | 0           | 0.161486    |       0.0235618   | CERRADO        |
| PA   |  0.0195673  | 0           | 0.00758645  | 0.00694813  |       0.00469114  | CERRADO        |
| TO   |  2.57853    | 0.119757    | 0.558597    | 1.20598     |       0.474085    | CERRADO        |
| MA   |  2.90213    | 0.238213    | 0.720007    | 1.2529      |       0.574956    | CERRADO        |
| PI   |  2.59514    | 0.463114    | 0.226178    | 1.20184     |       0.251866    | CERRADO        |
| BA   |  5.44566    | 1.0393      | 1.3445      | 1.91414     |       0.921806    | CERRADO        |
| MG   |  4.80725    | 0.813701    | 2.53475     | 0.781597    |       0.479927    | CERRADO        |
| SP   |  1.22089    | 0.112457    | 0.626372    | 0.134307    |       0.237839    | CERRADO        |
| PR   |  0.372971   | 0           | 0.370254    | 0           |       0           | CERRADO        |
| MS   |  6.18903    | 1.9196      | 1.37792     | 1.4869      |       1.10989     | CERRADO        |
| MT   | 19.7381     | 3.47543     | 7.17141     | 4.50499     |       3.32551     | CERRADO        |
| GO   | 11.3169     | 4.49351     | 3.88629     | 1.57867     |       1.09906     | CERRADO        |
| DF   |  0.292076   | 0.22708     | 0.0447509   | 0.00489012  |       0.0152516   | CERRADO        |
| PI   |  0          | 0           | 0           | 0           |       0           | CAATINGA       |
| CE   |  0.00414158 | 0           | 0           | 0.00334586  |       0.000795645 | CAATINGA       |
| RN   |  0          | 0           | 0           | 0           |       0           | CAATINGA       |
| PB   |  0          | 0           | 0           | 0           |       0           | CAATINGA       |
| PE   |  0          | 0           | 0           | 0           |       0           | CAATINGA       |
| AL   |  0          | 0           | 0           | 0           |       0           | CAATINGA       |
| SE   |  0          | 0           | 0           | 0           |       0           | CAATINGA       |
| BA   |  0.012676   | 0           | 0           | 0.0084054   |       0.000578225 | CAATINGA       |
| MG   |  0.00134266 | 0           | 0           | 0.00024078  |       0.000213213 | CAATINGA       |
| RN   |  0          | 0           | 0           | 0           |       0           | MATA ATLÂNTICA |
| PB   |  0          | 0           | 0           | 0           |       0           | MATA ATLÂNTICA |
| PE   |  0          | 0           | 0           | 0           |       0           | MATA ATLÂNTICA |
| AL   |  0          | 0           | 0           | 0           |       0           | MATA ATLÂNTICA |
| SE   |  0          | 0           | 0           | 0           |       0           | MATA ATLÂNTICA |
| BA   |  0          | 0           | 0           | 0           |       0           | MATA ATLÂNTICA |
| MG   |  0.572842   | 0.303058    | 0.198936    | 0.00640423  |       0.0213916   | MATA ATLÂNTICA |
| ES   |  0          | 0           | 0           | 0           |       0           | MATA ATLÂNTICA |
| RJ   |  0          | 0           | 0           | 0           |       0           | MATA ATLÂNTICA |
| SP   |  2.00848    | 0.628002    | 0.978497    | 0.117234    |       0.0828354   | MATA ATLÂNTICA |
| PR   | 23.7797     | 8.19883     | 8.00448     | 4.36941     |       2.57902     | MATA ATLÂNTICA |
| SC   |  2.46684    | 0.834658    | 0.795146    | 0.331747    |       0.321397    | MATA ATLÂNTICA |
| RS   |  6.72967    | 3.37986     | 1.45936     | 1.08309     |       0.656413    | MATA ATLÂNTICA |
| MS   |  2.05315    | 0.663404    | 0.912557    | 0.184921    |       0.219525    | MATA ATLÂNTICA |
| GO   |  0.00198916 | 0           | 0.00197814  | 0           |       0           | MATA ATLÂNTICA |
| RS   | 10.9793     | 4.20276     | 2.65267     | 2.17404     |       1.48846     | PAMPA          |
| MS   |  0          | 0           | 0           | 0           |       0           | PANTANAL       |
| MT   |  0          | 0           | 0           | 0           |       0           | PANTANAL       |
| nan  |  0          | 0.000430101 | 3.30758     | 3.25883     |       1.83799     | nan            |
"""

def load_and_clean_data():
    # Read the data, skipping the initial metadata lines
    # We look for the header line starting with "| UF"
    lines = SOURCE_DATA.strip().split('\n')
    start_idx = 0
    for i, line in enumerate(lines):
        if "| UF" in line:
            start_idx = i
            break
    
    data_str = '\n'.join(lines[start_idx:])
    
    # Use pandas to parse the markdown table
    df = pd.read_csv(io.StringIO(data_str), sep='|', skipinitialspace=True)
    
    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Drop the first and last columns which are empty due to markdown pipes
    df = df.iloc[:, 1:-1]
    
    # Handle the last row (NA group)
    # The last row has nan in UF and nan in Biome. We want to label it NA.
    # Identify it by index or by checking for nan in Biome
    mask_na_biome = df['Biome'].isna()
    df.loc[mask_na_biome, 'Biome'] = 'NA'
    df.loc[mask_na_biome, 'UF'] = 'NA'
    
    # Convert numeric columns to float
    numeric_cols = ['Total', 'Domestic', 'China', 'EU', 'Other countries']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    # Clean string columns
    df['UF'] = df['UF'].astype(str).str.strip()
    df['Biome'] = df['Biome'].astype(str).str.strip()
    
    return df

def generate_chart(df, output_filename):
    # --- Configuration ---
    # Biome Order based on the chart (Clockwise starting from top-right roughly)
    # Visual analysis: Amazônia -> Pantanal -> Cerrado -> Caatinga -> Pampa -> Mata Atlântica -> NA
    biome_order = [
        'AMAZÔNIA', 
        'PANTANAL', 
        'CERRADO', 
        'CAATINGA', 
        'PAMPA', 
        'MATA ATLÂNTICA', 
        'NA'
    ]
    
    # Colors (Inner to Outer)
    # Domestic (Lightest), China, EU, Other (Darkest)
    colors = ['#deebf7', '#9ecae1', '#4292c6', '#084594']
    stack_cols = ['Domestic', 'China', 'EU', 'Other countries']
    
    # Layout parameters
    INNER_RADIUS = 10
    BAR_WIDTH_RATIO = 0.9  # Width of bar relative to available slot
    GROUP_GAP = 3  # Gap between biomes in terms of bar slots
    
    # --- Data Preparation ---
    
    # Sort data: Custom Biome order, then Alphabetical UF
    df['Biome'] = pd.Categorical(df['Biome'], categories=biome_order, ordered=True)
    df = df.sort_values(['Biome', 'UF'])
    
    # Create a list of bars with their properties
    bars = []
    
    current_angle = 0
    # Total slots = number of bars + (number of groups * gap)
    # We map this to 2*pi
    
    # Group data
    grouped = df.groupby('Biome', observed=True)
    
    # Calculate total steps for angle normalization
    total_bars = len(df)
    total_gaps = len(biome_order) * GROUP_GAP
    total_steps = total_bars + total_gaps
    step_angle = (2 * np.pi) / total_steps
    
    # Start angle: The chart starts Amazônia at roughly 12 o'clock (pi/2) and goes clockwise.
    # However, in polar plots, 0 is usually East. 
    # We will set the offset later in the plot.
    # Let's build the list of bars and their angles.
    
    processed_bars = []
    group_labels = []
    
    # Iterate through biomes in specific order
    for biome in biome_order:
        group_data = df[df['Biome'] == biome]
        
        if group_data.empty:
            continue
            
        # Start angle for this group
        group_start_idx = len(processed_bars)
        
        for _, row in group_data.iterrows():
            bar_info = {
                'label': row['UF'],
                'values': [row[c] for c in stack_cols],
                'total': row['Total'],
                'biome': biome
            }
            processed_bars.append(bar_info)
        
        # Calculate label position for the group (average angle)
        group_end_idx = len(processed_bars)
        
        # Add gap after group (add dummy bars or just skip angles)
        # We will handle angles by index
        processed_bars.extend([None] * GROUP_GAP)
        
        # Store group info for labeling
        group_labels.append({
            'text': biome.title().replace('Na', 'NA'), # Title case, fix NA
            'start_idx': group_start_idx,
            'end_idx': group_end_idx
        })

    # --- Plotting ---
    
    fig = plt.figure(figsize=(10, 10), dpi=150)
    ax = plt.subplot(111, polar=True)
    
    # Set direction: Clockwise, starting from Top
    ax.set_theta_direction(-1)
    ax.set_theta_offset(np.pi / 2)
    
    # Draw Bars
    for i, bar in enumerate(processed_bars):
        if bar is None:
            continue
            
        angle = i * step_angle
        
        # Stacked Bar
        bottom = INNER_RADIUS
        for val, color in zip(bar['values'], colors):
            if val > 0:
                ax.bar(angle, val, width=step_angle * BAR_WIDTH_RATIO, 
                       bottom=bottom, color=color, edgecolor='none', linewidth=0)
                bottom += val
        
        # State Label
        # Place label at the end of the bar + padding
        # If bar is very small, place it just outside inner radius
        label_radius = max(bottom, INNER_RADIUS) + 0.5
        
        # Rotation logic
        # Convert angle to degrees for text rotation
        # Matplotlib angles are in radians. 
        # Visual rotation needs to be readable.
        # Angle in degrees (0 at top, clockwise)
        rot_angle = np.degrees(angle)
        
        # Adjust text rotation and alignment based on quadrant
        # In standard polar (0 at East, CCW):
        # Here we transformed to (0 at North, CW).
        # We need to calculate the standard angle to determine flip.
        
        # Simplified logic for readability:
        # If angle is between 90 (East) and 270 (West) in the plot's coordinate system?
        # Since we set theta_offset=pi/2 and direction=-1:
        # 0 is North. pi/2 is East. pi is South. 3pi/2 is West.
        
        # Text rotation needs to be relative to the screen.
        # We want the text to radiate outwards.
        text_rot = 90 - np.degrees(angle) # Convert to standard cartesian degrees
        
        # Flip text on the left side of the circle
        alignment = 'left'
        if np.pi < angle < 2 * np.pi:
            text_rot += 180
            alignment = 'right'
            label_radius += 0.5 # Extra padding for right-aligned text
        
        ax.text(angle, label_radius, bar['label'], 
                rotation=text_rot, ha=alignment, va='center', 
                fontsize=8, color='#555555')

    # Draw Biome Labels
    for grp in group_labels:
        # Calculate mean angle
        # Indices include the gaps, so we map indices to angles
        start_angle = grp['start_idx'] * step_angle
        end_angle = (grp['end_idx'] - 1) * step_angle
        mid_angle = (start_angle + end_angle) / 2
        
        # Radius for biome label (inside the hole)
        label_r = INNER_RADIUS - 2.5
        
        # Rotation for biome label
        # Similar logic to state labels but inside
        text_rot = 90 - np.degrees(mid_angle)
        
        # Flip if on bottom half to be readable? 
        # The chart has them following the curve. 
        # Standard matplotlib text is straight. We align it tangentially or radially.
        # Chart shows them curved along the circle. 
        # Approximating with straight text rotated tangentially.
        
        # Tangential rotation
        tangent_rot = text_rot # This is radial.
        # For tangential, subtract 90.
        tangent_rot -= 90
        
        # Fix upside down text
        if 90 < mid_angle * 180 / np.pi < 270:
             tangent_rot += 180
        
        ax.text(mid_angle, label_r, grp['text'], 
                rotation=tangent_rot, ha='center', va='center', 
                fontsize=9, fontweight='normal', color='black')

    # --- Grid and Styling ---
    
    # Remove default spines and grids
    ax.spines['polar'].set_visible(False)
    ax.grid(False)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    
    # Custom Grid Lines (Dashed circles)
    grid_values = [5, 15, 25, 35]
    for val in grid_values:
        r = INNER_RADIUS + val
        # Draw circle
        circle = plt.Circle((0, 0), r, transform=ax.transData._b, 
                            fill=False, edgecolor='#cccccc', linestyle='--', linewidth=0.5, alpha=0.7)
        # Note: In polar, Circle patch is tricky. 
        # Easier to plot a line at constant radius
        theta = np.linspace(0, 2*np.pi, 100)
        ax.plot(theta, [r]*100, color='#cccccc', linestyle='--', linewidth=0.8, zorder=0)
        
        # Add value label
        # Place label at a specific angle (e.g., top slightly left)
        label_angle = -0.2 # Slightly to the left of North
        ax.text(label_angle, r, str(val), color='#999999', fontsize=8, ha='center', va='center', backgroundcolor='white')

    # Title
    plt.title("2012", loc='left', x=0.0, y=0.95, fontsize=14, color='black')
    
    # Adjust limits
    ax.set_ylim(0, INNER_RADIUS + 38)
    
    # Save
    plt.tight_layout()
    plt.savefig(output_filename, bbox_inches='tight', dpi=150)
    # plt.close() # Good practice, but script ends anyway

if __name__ == "__main__":
    # Determine output filename
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
        
    # Run pipeline
    df = load_and_clean_data()
    generate_chart(df, output_file)
    print(f"Chart saved to {output_file}")