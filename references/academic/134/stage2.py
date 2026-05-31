import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def get_source_data():
    """
    Returns the pandas DataFrame created from the provided source data.
    """
    data_str = """
| UF   |        Total |    Domestic |       China |           EU |   Other countries | Biome          |
|:-----|-------------:|------------:|------------:|-------------:|------------------:|:---------------|
| RO   |  0.114415    | 0.114415    | 0           |  0           |        0          | AMAZÔNIA       |
| AC   |  0           | 0           | 0           |  0           |        0          | AMAZÔNIA       |
| AM   |  0.00962643  | 0.00960139  | 0           |  0           |        0          | AMAZÔNIA       |
| RR   |  0.0512527   | 0.0512527   | 0           |  0           |        0          | AMAZÔNIA       |
| PA   |  0.125305    | 0           | 0           |  0.0366658   |        0.00290931 | AMAZÔNIA       |
| AP   |  0           | 0           | 0           |  0           |        0          | AMAZÔNIA       |
| TO   |  0.00400667  | 0           | 0           |  0.00202471  |        0          | AMAZÔNIA       |
| MA   |  0           | 0           | 0           |  0           |        0          | AMAZÔNIA       |
| MT   |  2.97692     | 0           | 0.0500429   |  0.160889    |        0.125164   | AMAZÔNIA       |
| RO   |  0.141925    | 0.141925    | 0           |  0           |        0          | CERRADO        |
| PA   |  0.00498554  | 0           | 0           |  0           |        0          | CERRADO        |
| TO   |  1.43321     | 0           | 0.0741484   |  0.624675    |        0.00936783 | CERRADO        |
| MA   |  1.64168     | 0.163763    | 0.15678     |  0.43545     |        0.409197   | CERRADO        |
| PI   |  0.880661    | 0.437205    | 0.00150225  |  0.238742    |        0          | CERRADO        |
| BA   |  4.60401     | 1.1847      | 0           |  2.09371     |        0.5447     | CERRADO        |
| MG   |  4.56039     | 1.02729     | 0.230682    |  2.64935     |        0.421712   | CERRADO        |
| SP   |  1.31924     | 0.739402    | 0.0980305   |  0.294762    |        0.133971   | CERRADO        |
| PR   |  0.313118    | 0.243411    | 0.0695648   |  0           |        0          | CERRADO        |
| MS   |  6.03992     | 1.64629     | 0.0797918   |  1.58092     |        0.484488   | CERRADO        |
| MT   | 18.6892      | 3.33661     | 0.894709    |  4.40742     |        1.8195     | CERRADO        |
| GO   | 10.3227      | 3.03384     | 0.637851    |  5.02027     |        0.856332   | CERRADO        |
| DF   |  0.225615    | 0.0910918   | 0.00310821  |  0.0770602   |        0.0512176  | CERRADO        |
| PI   |  0           | 0           | 0           |  0           |        0          | CAATINGA       |
| CE   |  0.00149772  | 0           | 0.000287734 |  0.00120999  |        0          | CAATINGA       |
| RN   |  0           | 0           | 0           |  0           |        0          | CAATINGA       |
| PB   |  0           | 0           | 0           |  0           |        0          | CAATINGA       |
| PE   |  0           | 0           | 0           |  0           |        0          | CAATINGA       |
| AL   |  0.000538864 | 0           | 5.94989e-05 |  0.000435362 |        0          | CAATINGA       |
| SE   |  0           | 0           | 0           |  0           |        0          | CAATINGA       |
| BA   |  0.00171117  | 0           | 0           |  0.000155377 |        0          | CAATINGA       |
| MG   |  0.000212819 | 0           | 0           |  0           |        0          | CAATINGA       |
| RN   |  0           | 0           | 0           |  0           |        0          | MATA ATLÂNTICA |
| PB   |  0           | 0           | 0           |  0           |        0          | MATA ATLÂNTICA |
| PE   |  0           | 0           | 0           |  0           |        0          | MATA ATLÂNTICA |
| AL   |  0.000111864 | 0           | 0           |  9.03731e-05 |        0          | MATA ATLÂNTICA |
| SE   |  0           | 0           | 0           |  0           |        0          | MATA ATLÂNTICA |
| BA   |  0           | 0           | 0           |  0           |        0          | MATA ATLÂNTICA |
| MG   |  0.755314    | 0.185852    | 0.068604    |  0.373973    |        0.0916257  | MATA ATLÂNTICA |
| ES   |  0           | 0           | 0           |  0           |        0          | MATA ATLÂNTICA |
| RJ   |  0           | 0           | 0           |  0           |        0          | MATA ATLÂNTICA |
| SP   |  3.081       | 1.11031     | 0.37609     |  0.927829    |        0.485674   | MATA ATLÂNTICA |
| PR   | 21.1121      | 7.3909      | 3.78398     |  6.06268     |        3.59111    | MATA ATLÂNTICA |
| SC   |  1.73768     | 0.790946    | 0.229827    |  0.271224    |        0.370402   | MATA ATLÂNTICA |
| RS   |  6.42229     | 2.29844     | 1.49619     |  0.784473    |        1.62655    | MATA ATLÂNTICA |
| MS   |  2.30378     | 0.805498    | 0.259331    |  0.706551    |        0.310066   | MATA ATLÂNTICA |
| GO   |  0.0130812   | 0.00868897  | 0.0018969   |  0           |        0.00249533 | MATA ATLÂNTICA |
| RS   |  9.63679     | 2.52987     | 1.97878     |  1.61103     |        3.28818    | PAMPA          |
| MS   |  0           | 0           | 0           |  0           |        0          | PANTANAL       |
| MT   |  0           | 0           | 0           |  0           |        0          | PANTANAL       |
| nan  |  0           | 0.000487474 | 3.43685     | 12.3897      |        4.91744    | nan            |
    """
    
    # Process the markdown table string
    lines = data_str.strip().split('\n')
    # Filter out separator lines (e.g., |---|)
    lines = [line for line in lines if '---' not in line]
    
    # Create a clean CSV string
    csv_str = '\n'.join(lines)
    
    # Read into pandas
    df = pd.read_csv(io.StringIO(csv_str), sep='|', skipinitialspace=True)
    
    # Clean column names (remove whitespace and empty columns from markdown pipes)
    df.columns = [c.strip() for c in df.columns]
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Clean string columns
    df['UF'] = df['UF'].str.strip()
    df['Biome'] = df['Biome'].str.strip()
    
    # Handle the last row (NA)
    # The source data has 'nan' in the first column for the last row
    # We identify it by the index or by checking for NaN in UF/Biome
    mask_na = df['UF'].astype(str) == 'nan'
    df.loc[mask_na, 'UF'] = 'NA'
    df.loc[mask_na, 'Biome'] = 'NA'
    
    return df

def generate_chart(output_filename):
    df = get_source_data()
    
    # Define the order of Biomes as they appear clockwise in the chart
    # Starting from top (12:00) and moving clockwise
    # Based on visual inspection: Amazônia -> Pantanal -> Cerrado -> Caatinga -> Pampa -> Mata Atlântica -> NA
    # Note: NA is at the very end/start (top).
    
    biome_order = ['AMAZÔNIA', 'PANTANAL', 'CERRADO', 'CAATINGA', 'PAMPA', 'MATA ATLÂNTICA', 'NA']
    
    # Sort dataframe
    df['Biome'] = pd.Categorical(df['Biome'], categories=biome_order, ordered=True)
    df = df.sort_values(['Biome', 'UF'])
    
    # Prepare data for plotting
    # Columns to stack
    stack_cols = ['Domestic', 'China', 'Other countries', 'EU']
    colors = ['#d0e1f2', '#9ecae1', '#6baed6', '#08306b'] # Light to Dark Blue
    
    # Setup Polar Plot
    fig = plt.figure(figsize=(10, 10), dpi=300)
    ax = plt.subplot(111, projection='polar')
    
    # Configuration
    INNER_RADIUS = 10  # The radius of the inner white circle
    BAR_WIDTH = 0.08   # Width of bars in radians
    GAP = 0.15         # Gap between biomes in radians
    
    # Calculate angles
    # We need to iterate to assign angles, adding gaps when biome changes
    
    angles = []
    current_angle = 0
    previous_biome = None
    
    # We want to start slightly to the right of 12 o'clock (pi/2)
    # Matplotlib polar: 0 is East (3 o'clock). 
    # We set theta_zero_location to 'N' (North) and direction -1 (Clockwise).
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    
    # Calculate positions
    # We need to pre-calculate total width to center it or just start plotting
    # Let's iterate and build a list of (angle, row_data)
    
    plot_data = []
    
    # Start angle offset to align visually
    start_offset = 0.1 
    current_angle = start_offset
    
    biome_groups = {} # To store start/end angles for labels
    
    for i, row in df.iterrows():
        biome = row['Biome']
        
        if previous_biome is not None and biome != previous_biome:
            current_angle += GAP
            
        if biome not in biome_groups:
            biome_groups[biome] = {'start': current_angle, 'count': 0, 'end': 0}
        
        plot_data.append({
            'angle': current_angle,
            'row': row
        })
        
        biome_groups[biome]['end'] = current_angle
        biome_groups[biome]['count'] += 1
        
        previous_biome = biome
        current_angle += BAR_WIDTH
        
    # Plot Bars
    for item in plot_data:
        angle = item['angle']
        row = item['row']
        
        bottom = INNER_RADIUS
        
        # Stack bars
        for col, color in zip(stack_cols, colors):
            height = row[col]
            # Only plot if height > 0 to avoid thin lines for 0 values
            if height > 0:
                ax.bar(angle, height, width=BAR_WIDTH, bottom=bottom, color=color, edgecolor='none')
            bottom += height
            
        # Add UF Label
        # Rotate label based on angle
        # Convert angle to degrees for rotation logic
        angle_deg = np.degrees(angle)
        
        # Adjust rotation so text is readable (not upside down)
        # In 'N' zero, -1 direction:
        # 0-180 is right side, 180-360 is left side.
        # Wait, with direction -1, angle increases clockwise.
        # 0 is Top. 90 is Right. 180 is Bottom. 270 is Left.
        
        # Normalize angle to 0-360
        norm_angle = angle_deg % 360
        
        if 0 <= norm_angle < 180:
            rot = 90 - norm_angle
            alignment = 'left'
            label_padding = 0.5
        else:
            rot = 90 - norm_angle + 180
            alignment = 'right'
            label_padding = 0.5
            
        # Place UF label just outside the bar (or at a fixed radius if bar is 0)
        # The chart shows labels at a fixed radius just outside the grid
        label_radius = 35 + INNER_RADIUS + 2
        
        ax.text(angle, label_radius, row['UF'], 
                rotation=rot, ha=alignment, va='center', 
                fontsize=8, color='#555555')

    # Add Biome Labels (Inner Circle)
    for biome, data in biome_groups.items():
        start = data['start']
        end = data['end']
        mid_angle = (start + end) / 2
        
        # Calculate rotation for the text to follow the curve
        # Tangent to the circle at mid_angle
        mid_deg = np.degrees(mid_angle)
        
        # Adjust rotation for readability
        if 90 < mid_deg < 270:
            text_rot = 90 - mid_deg + 180
        else:
            text_rot = 90 - mid_deg
            
        # Radius for biome labels (inside the inner circle)
        label_r = INNER_RADIUS - 1.5
        
        # Special adjustment for NA to match image
        if biome == 'NA':
            label_r = 35 + INNER_RADIUS + 5 # Put NA label outside at the top
            text_rot = 0
            # The image shows "NA" at the top of the bar, not inside.
            # Actually, looking at the image, "NA" is written vertically above the bar.
        
        ax.text(mid_angle, label_r, biome.title() if biome != 'NA' else 'NA', 
                rotation=text_rot, ha='center', va='center', 
                fontsize=9, color='black')

    # Custom Grid Lines
    # Remove default grid
    ax.grid(False)
    ax.spines['polar'].set_visible(False)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    
    # Draw dashed arcs for grid
    grid_values = [0, 5, 15, 25, 35]
    
    # We need to draw these arcs only where data exists or full circle?
    # The image shows dashed lines in the background, seemingly full circle but broken.
    # Let's draw full dashed circles.
    for val in grid_values:
        r = INNER_RADIUS + val
        # Draw circle
        ax.plot(np.linspace(0, 2*np.pi, 100), [r]*100, color='lightgray', linestyle='--', linewidth=0.8, zorder=0)
        
        # Add value label at the top (near 0 angle)
        # Slightly offset to the left or right? Image shows them at top center.
        ax.text(0, r, str(val), ha='center', va='center', color='#aaaaaa', fontsize=9, backgroundcolor='white')

    # Title
    plt.text(0.05, 0.95, "2004", transform=fig.transFigure, fontsize=16, ha='left')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save
    plt.savefig(output_filename, bbox_inches='tight', dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    generate_chart(output_file)