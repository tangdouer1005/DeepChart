import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Arc

# ---------------------------------------------------------
# 1. Source Data Embedding
# ---------------------------------------------------------
csv_data = """UF|Total|Domestic|China|EU|Other countries|Biome
RO|0.2662|0.184207|0|0.0816574|0|AMAZÔNIA
AC|0|0|0|0|0|AMAZÔNIA
AM|0.000830623|0.000830623|0|0|0|AMAZÔNIA
RR|0.0336407|0.0336438|0|0|0|AMAZÔNIA
PA|0.242622|0.0482524|0.0218832|0.149485|0.000626649|AMAZÔNIA
AP|0|0|0|0|0|AMAZÔNIA
TO|0.00525824|0.00525824|0|0|0|AMAZÔNIA
MA|0|0|0|0|0|AMAZÔNIA
MT|5.03942|0.611752|0.265206|1.30759|0.246126|AMAZÔNIA
RO|0.168092|0.0376296|0|0.127656|0.00276714|CERRADO
PA|0.021702|0.0050899|0.00914977|0.00739724|3.2943e-05|CERRADO
TO|1.85553|0.177023|0.483385|0.774701|0.0549997|CERRADO
MA|2.19982|0.353354|0.684955|0.986659|0.0742376|CERRADO
PI|1.42544|0.601774|0.323796|0.323643|0.0842349|CERRADO
BA|4.82165|1.77931|0.565417|1.90293|0.479344|CERRADO
MG|3.77077|1.76648|0.662089|0.891373|0.299876|CERRADO
SP|0.908815|0.184582|0.38839|0.12108|0.0565109|CERRADO
PR|0.287668|0.0875665|0.036569|0.112925|0.042047|CERRADO
MS|4.80526|2.41897|0.199595|1.52314|0.35073|CERRADO
MT|17.3693|4.44551|2.57547|5.93238|2.07917|CERRADO
GO|8.57938|4.68816|2.03702|1.14917|0.662888|CERRADO
DF|0.218021|0|0.0962528|0.0553294|0.0664021|CERRADO
PI|0|0|0|0|0|CAATINGA
CE|0.00217979|0|0|0|0.00208539|CAATINGA
RN|0|0|0|0|0|CAATINGA
PB|0|0|0|0|0|CAATINGA
PE|0|0|0|0|0|CAATINGA
AL|0.000376263|0|0|0|0.000376263|CAATINGA
SE|0|0|0|0|0|CAATINGA
BA|0.0105912|0|0|0.00655603|0.000173411|CAATINGA
MG|4.47174e-05|0|0|0|0|CAATINGA
RN|0|0|0|0|0|MATA ATLÂNTICA
PB|0|0|0|0|0|MATA ATLÂNTICA
PE|0|0|0|0|0|MATA ATLÂNTICA
AL|0|0|0|0|0|MATA ATLÂNTICA
SE|0|0|0|0|0|MATA ATLÂNTICA
BA|0|0|0|0|0|MATA ATLÂNTICA
MG|0.395984|0.0995238|0.187476|0.036686|0.0503248|MATA ATLÂNTICA
ES|0|0|0|0|0|MATA ATLÂNTICA
RJ|0|0|0|0|0|MATA ATLÂNTICA
SP|2.08255|0.635369|0.714721|0.277265|0.109141|MATA ATLÂNTICA
PR|21.3322|7.953|4.74818|5.77727|2.56227|MATA ATLÂNTICA
SC|1.98196|0.871507|0.524725|0.375392|0.111931|MATA ATLÂNTICA
RS|5.57091|2.41155|1.00844|1.12714|0.939832|MATA ATLÂNTICA
MS|1.5106|0.650771|0.424072|0.285241|0.144463|MATA ATLÂNTICA
GO|0.00275451|0.00275451|0|0|0|MATA ATLÂNTICA
RS|9.2411|3.41109|2.12871|1.5593|2.07498|PAMPA
MS|0|0|0|0|0|PANTANAL
MT|0|0|0|0|0|PANTANAL
NA|0|0.000390173|2.3444|4.29908|1.73003|NA"""

def get_data():
    # Read the embedded CSV data
    df = pd.read_csv(io.StringIO(csv_data), sep='|')
    
    # Clean numeric columns
    cols = ['Total', 'Domestic', 'China', 'EU', 'Other countries']
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Define the specific order of Biomes as seen in the chart (Clockwise)
    # Visual inspection: Amazônia -> Pantanal -> Cerrado -> Caatinga -> Pampa -> Mata Atlântica -> NA
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
    df = df.sort_values('Biome')
    
    return df, biome_order

def plot_chart(output_filename):
    df, biome_order = get_data()
    
    # ---------------------------------------------------------
    # 2. Chart Configuration
    # ---------------------------------------------------------
    # Colors extracted from the image
    colors = {
        'Domestic': '#dbe9f6',       # Very light blue
        'China': '#9ecae1',          # Light blue
        'EU': '#4292c6',             # Medium blue
        'Other countries': '#08306b' # Dark navy
    }
    
    # Dimensions
    INNER_RADIUS = 15  # Size of the hole
    MAX_HEIGHT = 35    # Max value on scale
    BAR_WIDTH = 0.8    # Width of bars relative to angular slot
    
    # Setup Figure
    fig = plt.figure(figsize=(12, 12), dpi=100)
    ax = fig.add_subplot(111, projection='polar')
    
    # Background and Grid
    ax.set_facecolor('white')
    ax.grid(False) # We will draw custom grid
    ax.spines['polar'].set_visible(False)
    
    # ---------------------------------------------------------
    # 3. Calculate Angles and Positions
    # ---------------------------------------------------------
    # We need gaps between groups. 
    # Total slots = number of data points + (number of groups * gap_size)
    
    groups = df.groupby('Biome', observed=True)
    group_names = list(groups.groups.keys())
    
    # Parameters for layout
    gap_in_radians = 0.15  # Gap between biomes
    total_bars = len(df)
    
    # Calculate starting angle for each bar
    # We start from top (pi/2) and go clockwise (negative direction)
    # However, matplotlib polar goes counter-clockwise by default.
    # We will calculate linear positions then map to angles.
    
    bar_angles = []
    bar_labels = []
    bar_heights = [] # List of dicts for stack components
    
    current_angle = np.pi / 2  # Start at 12 o'clock
    
    # To match the chart exactly, we need to iterate through the sorted groups
    # The chart goes Clockwise: Amazônia -> Pantanal -> ...
    
    group_meta = {} # Store start/end angles for group labels
    
    for biome in biome_order:
        group_data = df[df['Biome'] == biome]
        if group_data.empty:
            continue
            
        n_bars = len(group_data)
        # Calculate sector width for this group
        # We allocate equal width per bar. 
        # Let's define a unit width in radians.
        # Total circle = 2*pi. 
        # Let's say we have roughly 50 bars + gaps.
        
        start_angle_for_group = current_angle
        
        for _, row in group_data.iterrows():
            # Data for stacking
            heights = {
                'Domestic': row['Domestic'],
                'China': row['China'],
                'EU': row['EU'],
                'Other countries': row['Other countries']
            }
            
            # Calculate total height for label positioning
            total_h = sum(heights.values())
            
            bar_angles.append(current_angle)
            bar_labels.append((row['UF'], total_h))
            bar_heights.append(heights)
            
            # Move clockwise
            current_angle -= 0.12 # Fixed radian step per bar
            
        end_angle_for_group = current_angle + 0.12 # Compensate for last step
        
        group_meta[biome] = {
            'start': start_angle_for_group,
            'end': end_angle_for_group,
            'mean': (start_angle_for_group + end_angle_for_group) / 2
        }
        
        # Add gap after group
        current_angle -= gap_in_radians

    # ---------------------------------------------------------
    # 4. Plotting Bars
    # ---------------------------------------------------------
    
    for i, (angle, heights) in enumerate(zip(bar_angles, bar_heights)):
        bottom = INNER_RADIUS
        
        # Stack order: Domestic (inner), China, EU, Other (outer)
        for category in ['Domestic', 'China', 'EU', 'Other countries']:
            h = heights[category]
            if h > 0:
                ax.bar(angle, h, width=0.10, bottom=bottom, 
                       color=colors[category], edgecolor='none', align='center')
                bottom += h

    # ---------------------------------------------------------
    # 5. Labels (UF)
    # ---------------------------------------------------------
    for angle, (label, height) in zip(bar_angles, bar_labels):
        if height < 0.1 and label != 'NA': continue # Skip labels for empty bars unless it's NA group
        
        # Distance from center
        r_pos = INNER_RADIUS + height + 1.0
        
        # Rotation logic
        # Convert radians to degrees for text rotation
        # Matplotlib expects degrees. 0 is East.
        # Our angle is in radians.
        deg = np.degrees(angle)
        
        # Adjust rotation for readability
        if 0 <= deg <= 180:
            rot = deg - 90
            ha = 'center'
            va = 'bottom'
        else:
            rot = deg + 90
            ha = 'center'
            va = 'bottom' # Because we rotated 180, bottom becomes "inner" relative to text
            
        # Fine tuning rotation based on quadrants for the specific look
        # The chart labels radiate outwards.
        rotation = deg
        if 90 < deg < 270:
            rotation = deg + 180
        
        # Fix specific alignment based on side of circle
        if 0 <= deg < 180:
            alignment_ha = 'left'
            alignment_va = 'center'
            rotation = deg
        else:
            alignment_ha = 'right'
            alignment_va = 'center'
            rotation = deg - 180
            
        # Actually, looking at the chart, the text is perpendicular to the radius
        # For top half (0-180), text reads bottom-up or top-down?
        # Chart: "PR" at 10 o'clock is rotated ~ -45 deg.
        # "MT" at 2 o'clock is rotated ~ -45 deg (relative to vertical).
        
        # Let's use standard radial rotation logic
        rot_deg = np.degrees(angle)
        if 0 <= rot_deg <= 180:
            rot_final = rot_deg - 90
            ha_final = 'left'
            va_final = 'center'
            # Offset slightly
            r_pos += 0.5
        else:
            rot_final = rot_deg + 90
            ha_final = 'right'
            va_final = 'center'
            r_pos += 0.5

        ax.text(angle, r_pos, label, rotation=rot_final, 
                ha=ha_final, va=va_final, fontsize=9, color='#555555')

    # ---------------------------------------------------------
    # 6. Group Labels (Biomes) and Arcs
    # ---------------------------------------------------------
    for biome, meta in group_meta.items():
        start = meta['start']
        end = meta['end']
        mid = meta['mean']
        
        # Draw the arc line inside
        # We simulate an arc using a line plot with many points
        theta_range = np.linspace(start, end, 50)
        r_range = [INNER_RADIUS - 1.5] * 50
        ax.plot(theta_range, r_range, color='black', linewidth=0.8)
        
        # Place Label
        # Convert biome name to Title Case if needed, chart uses Title Case
        label_text = biome.title()
        if label_text == 'Na': label_text = 'NA'
        if label_text == 'Mata Atlântica': label_text = 'Mata Atlântica' # Keep accent
        
        # Calculate rotation for the label to follow the curve
        # Tangent to the circle at 'mid'
        rot_deg = np.degrees(mid)
        
        # Adjust for readability (bottom vs top)
        if 90 < rot_deg < 270:
            text_rot = rot_deg + 180
            r_text = INNER_RADIUS - 3.5
            va = 'top'
        else:
            text_rot = rot_deg
            r_text = INNER_RADIUS - 2.5
            va = 'bottom'
            
        # Special adjustments for specific labels to match image
        if label_text == 'Amazônia':
            text_rot = np.degrees(mid) - 180 # Flip to read inside
            va = 'top'
            r_text = INNER_RADIUS - 2.5
        elif label_text == 'Pantanal':
            text_rot = np.degrees(mid) - 180
            va = 'top'
        elif label_text == 'Cerrado':
            text_rot = np.degrees(mid) - 180
            va = 'top'
        elif label_text == 'Caatinga':
            text_rot = np.degrees(mid)
            va = 'bottom'
            r_text = INNER_RADIUS - 4.0
        elif label_text == 'Pampa':
            text_rot = np.degrees(mid)
            va = 'bottom'
            r_text = INNER_RADIUS - 4.0
        elif label_text == 'Mata Atlântica':
            text_rot = np.degrees(mid)
            va = 'bottom'
            r_text = INNER_RADIUS - 4.0
        elif label_text == 'NA':
            text_rot = np.degrees(mid) - 90 # Vertical
            r_text = INNER_RADIUS - 5
            
        # Simplified logic based on visual inspection of the provided chart
        # Top right (Amazônia, Pantanal): Text inside, rotated to read clockwise?
        # Actually, let's just place text at the midpoint with radial rotation
        
        # Re-evaluating rotation based on image:
        # Amazônia: Text follows curve, upright relative to center? No, it's inverted.
        # Let's try a simpler approach: Place text, rotate it to be tangent.
        
        tangent_rot = np.degrees(mid) - 90
        if 90 < np.degrees(mid) < 270:
            tangent_rot -= 180
            
        ax.text(mid, INNER_RADIUS - 2.5, label_text, 
                rotation=tangent_rot, ha='center', va='center', fontsize=10)

    # ---------------------------------------------------------
    # 7. Custom Gridlines and Axis Labels
    # ---------------------------------------------------------
    # Draw dashed circles
    grid_values = [0, 5, 15, 25, 35]
    for val in grid_values:
        if val == 0: continue
        # Draw circle
        theta = np.linspace(0, 2*np.pi, 200)
        r = [INNER_RADIUS + val] * 200
        # Gap at the top for labels? The chart has labels at ~12 o'clock
        ax.plot(theta, r, color='lightgray', linestyle=(0, (5, 10)), linewidth=0.8)
        
        # Add text label at top (pi/2)
        ax.text(np.pi/2, INNER_RADIUS + val, str(val), 
                ha='center', va='center', color='#999999', fontsize=10,
                backgroundcolor='white') # White bg to hide grid line behind text

    # Add "0" label
    ax.text(np.pi/2, INNER_RADIUS, "0", 
            ha='center', va='center', color='#999999', fontsize=10,
            backgroundcolor='white')

    # ---------------------------------------------------------
    # 8. Final Styling
    # ---------------------------------------------------------
    # Remove default y-tick labels
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    
    # Set limits
    ax.set_ylim(0, INNER_RADIUS + MAX_HEIGHT + 5)
    
    # Add Year Label
    # Since it's a polar plot, placing text in figure coordinates is easier
    plt.figtext(0.05, 0.92, "2008", fontsize=16, color='black')
    
    # Save
    plt.savefig(output_filename, bbox_inches='tight', dpi=150)
    # plt.close() # Good practice, but script ends anyway

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    plot_chart(output_file)