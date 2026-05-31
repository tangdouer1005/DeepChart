import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# 1. Load Source Data
# We embed the data directly as a string to ensure the script is self-contained.
csv_data = """
UF|Total|Domestic|China|EU|Other countries|Biome
RO|0.889164|0.42801|0.152716|0.215917|0.091916|AMAZÔNIA
AC|0|0|0|0|0|AMAZÔNIA
AM|0|0|0|0|0|AMAZÔNIA
RR|0.105008|0.104795|0|0|0.000212607|AMAZÔNIA
PA|1.58271|0.0950292|0.551001|0.671685|0.14383|AMAZÔNIA
AP|0.067138|0|0|0.0379322|0|AMAZÔNIA
TO|0.0931787|0.027217|0.0393144|0.0264442|0|AMAZÔNIA
MA|0.266676|0.12271|0.0477404|0.00390637|0.0190575|AMAZÔNIA
MT|14.2444|0.858222|3.70748|2.21389|2.14395|AMAZÔNIA
RO|0.244054|0|0.0721874|0.135157|0.0366261|CERRADO
PA|0.0550185|0|0.00530147|0.00568574|0.00133762|CERRADO
TO|4.86451|1.20177|1.74741|1.52155|0.214859|CERRADO
MA|3.73388|0.600306|1.73935|0.897921|0.467115|CERRADO
PI|2.81416|1.38696|0.750725|0.283503|0.16784|CERRADO
BA|6.57289|2.51835|1.64725|1.44533|0.808875|CERRADO
MG|6.37774|1.47775|2.59487|0.972055|1.09499|CERRADO
SP|1.91952|0.185938|1.38244|0.0428669|0.256277|CERRADO
PR|0.379938|0|0.304605|0.000296198|0.0714852|CERRADO
MS|7.97434|2.35714|1.62995|1.69072|1.5285|CERRADO
MT|22.1982|6.47418|6.80724|3.41044|3.90981|CERRADO
GO|13.709|7.50225|3.57765|1.0861|1.25681|CERRADO
DF|0.351429|0.130677|0.167283|0.0163992|0.0368531|CERRADO
PI|0|0|0|0|0|CAATINGA
CE|0|0|0|0|0|CAATINGA
RN|0|0|0|0|0|CAATINGA
PB|0|0|0|0|0|CAATINGA
PE|0|0|0|0|0|CAATINGA
AL|0|0|0|0|0|CAATINGA
SE|0|0|0|0|0|CAATINGA
BA|0.0179572|0.0170261|0.000910982|0|0|CAATINGA
MG|0.00514199|0|0.00316291|0|0.00111873|CAATINGA
RN|0|0|0|0|0|MATA ATLÂNTICA
PB|0|0|0|0|0|MATA ATLÂNTICA
PE|0|0|0|0|0|MATA ATLÂNTICA
AL|0.000953549|0|0|0.000953517|0|MATA ATLÂNTICA
SE|0|0|0|0|0|MATA ATLÂNTICA
BA|0|0|0|0|0|MATA ATLÂNTICA
MG|1.14379|0.249163|0.554815|0.0754145|0.231935|MATA ATLÂNTICA
ES|0|0|0|0|0|MATA ATLÂNTICA
RJ|0|0|0|0|0|MATA ATLÂNTICA
SP|3.4042|0.820036|2.14107|0.0351306|0.276878|MATA ATLÂNTICA
PR|32.9761|11.1358|14.3749|2.768|3.9394|MATA ATLÂNTICA
SC|3.86536|0.787649|1.53009|0.467788|0.558936|MATA ATLÂNTICA
RS|9.01536|3.7042|3.15373|0.685776|1.05507|MATA ATLÂNTICA
MS|2.93363|0.920377|0.998459|0.337178|0.455984|MATA ATLÂNTICA
GO|0.00526863|0.000424816|0.000489741|0.00367306|0.000655903|MATA ATLÂNTICA
RS|18.3157|4.14094|8.8696|2.14767|2.72434|PAMPA
MS|0.000380705|0|0|0|0|PANTANAL
MT|0|0|0|0|0|PANTANAL
NA|0|0.000405953|7.38215|1.13064|3.28723|NA
"""

def generate_chart(output_filename="output.png"):
    # 2. Data Processing
    df = pd.read_csv(io.StringIO(csv_data), sep='|')
    
    # Clean up whitespace in string columns
    df['UF'] = df['UF'].str.strip()
    df['Biome'] = df['Biome'].str.strip()
    
    # Define the specific order of Biomes as seen in the chart (Clockwise starting from top-right)
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
    
    # Create a categorical type for sorting
    df['Biome'] = pd.Categorical(df['Biome'], categories=biome_order, ordered=True)
    
    # Sort by Biome, then by UF (alphabetical)
    df = df.sort_values(by=['Biome', 'UF'])
    
    # Reset index for easier iteration
    df = df.reset_index(drop=True)

    # 3. Plot Configuration
    # Colors extracted from the image (Blues)
    colors = {
        'Domestic': '#d0e1f2',        # Lightest Blue
        'China': '#94c4df',           # Medium-Light Blue
        'EU': '#4a7bb7',              # Medium-Dark Blue
        'Other countries': '#08306b'  # Darkest Blue/Black
    }
    categories = ['Domestic', 'China', 'EU', 'Other countries']

    # Polar plot setup
    fig = plt.figure(figsize=(12, 12), dpi=150)
    ax = fig.add_subplot(111, projection='polar')
    
    # Parameters
    OFFSET = 10  # Inner hole radius
    WIDTH = 0.08 # Width of bars
    PAD = 0.15   # Gap between biomes (in radians)
    
    # Calculate angles
    # We need to manually calculate theta for each bar to insert gaps between groups
    thetas = []
    current_angle = 0
    
    # Starting angle: The chart starts Amazônia slightly to the right of 12 o'clock (North)
    # Matplotlib polar: 0 is East. North is pi/2.
    # We want to go Clockwise.
    ax.set_theta_direction(-1) # Clockwise
    ax.set_theta_zero_location('N') # 0 at Top
    
    # Initial offset to create the gap at the top
    current_angle = 0.1 
    
    group_angles = {} # Store start/end angles for biome labels
    
    grouped = df.groupby('Biome', observed=True)
    
    bar_data = [] # Store (theta, row_data)
    
    for name, group in grouped:
        start_angle = current_angle
        
        # Sort group alphabetically by UF to match chart
        group = group.sort_values('UF')
        
        for idx, row in group.iterrows():
            thetas.append(current_angle)
            bar_data.append({'theta': current_angle, 'row': row})
            current_angle += WIDTH
            
        end_angle = current_angle - WIDTH
        group_angles[name] = (start_angle, end_angle)
        
        # Add padding after each group
        current_angle += PAD

    # 4. Drawing the Bars
    for item in bar_data:
        theta = item['theta']
        row = item['row']
        
        bottom = OFFSET
        
        # Stack the bars
        for cat in categories:
            value = row[cat]
            # Handle small values for visibility if needed, but strictly using data here
            if value > 0:
                ax.bar(theta, value, width=WIDTH, bottom=bottom, 
                       color=colors[cat], edgecolor='none', linewidth=0)
                bottom += value
        
        # 5. UF Labels (State Codes)
        # Only label if total > 0 or if it's explicitly shown in the chart (some 0s are labeled like AC, AM)
        # In the chart, even 0 bars seem to have labels if space permits, or they are just very small bars.
        # Let's label all.
        
        total_height = bottom
        label_padding = 1.0
        
        # Calculate rotation
        # Convert theta to degrees for text rotation
        # In clockwise, North=0.
        # 0 to 180 (Right side): Text should be -theta + 90?
        # Let's use standard logic:
        rot = np.degrees(theta) * -1 # Because of clockwise direction
        
        # Adjust rotation for readability (flip text on left side)
        # In this setup (0=N, CW), 0-180 is Right, 180-360 is Left.
        # Actually, theta keeps increasing.
        normalized_theta = np.degrees(theta) % 360
        
        if 0 <= normalized_theta < 180:
            alignment = 'left'
            rotation = 90 - normalized_theta
        else:
            alignment = 'right'
            rotation = 90 - normalized_theta + 180
            
        ax.text(theta, total_height + 0.5, row['UF'], 
                ha=alignment, va='center', rotation=rotation, 
                fontsize=9, color='#555555')

    # 6. Biome Labels
    for name, (start, end) in group_angles.items():
        if name == 'nan': continue # Skip NA label on the inner circle if preferred, though chart has NA group
        
        mid_angle = (start + end) / 2
        
        # Convert name to Title Case (AMAZÔNIA -> Amazônia)
        label_text = name.title()
        if name == 'NA': label_text = 'NA'
        if name == 'MATA ATLÂNTICA': label_text = 'Mata Atlântica'
        
        # Rotation logic for inner labels
        normalized_mid = np.degrees(mid_angle) % 360
        
        # Text placement radius
        label_r = OFFSET - 0.5
        
        # Rotation to align with the circle tangent
        if 0 <= normalized_mid < 180:
            rot = 90 - normalized_mid - 90 # Tangent
            # To make it read along the curve:
            rot = -normalized_mid 
            # Actually, looking at image:
            # Amazônia (top right): Text is rotated ~ -45 deg.
            # Cerrado (bottom right): Text is rotated ~ -135 deg.
            # It seems text is rotated such that the baseline points to center? No.
            # Text is aligned with the radial line? No.
            # Text is perpendicular to radial line.
            rot = 90 - normalized_mid
        else:
            rot = 90 - normalized_mid + 180
            
        # Fine tuning rotation based on visual inspection
        # Amazônia is at ~45 deg. Text is rotated -45.
        # Mata Atlântica is at ~270 deg. Text is rotated 90.
        
        ax.text(mid_angle, label_r, label_text, 
                ha='center', va='bottom', rotation=rot,
                fontsize=10, color='black')

    # 7. Styling and Gridlines
    ax.set_frame_on(False)
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Custom Gridlines (Circles)
    # Levels: 0 (Inner), 5, 15, 25
    grid_levels = [0, 5, 15, 25]
    for level in grid_levels:
        # Draw circle
        # In polar, a circle is a line at constant radius
        r = OFFSET + level
        
        # Draw dashed line, but with gaps for text? No, image shows dashed lines.
        # We draw a full circle using a loop of angles
        x = np.linspace(0, 2*np.pi, 100)
        ax.plot(x, [r]*100, color='gray', linestyle=(0, (5, 10)), linewidth=0.5, alpha=0.5)
        
        # Add label at the top (North)
        if level > 0:
            ax.text(0, r, str(level), ha='center', va='center', 
                    fontsize=10, color='#999999', backgroundcolor='white')

    # Title
    plt.text(0.05, 0.95, "2016", transform=fig.transFigure, fontsize=16, color='black')

    # Adjust layout
    plt.tight_layout()
    
    # Save
    plt.savefig(output_filename, bbox_inches='tight', dpi=150)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)