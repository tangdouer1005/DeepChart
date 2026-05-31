import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math

def generate_chart(output_filename):
    # 1. Load Data
    # We embed the data directly as a string to ensure the script is standalone.
    csv_data = """
UF|Total|Domestic|China|EU|Other_countries|Biome
RO|60206|42006.1|0|18118.8|0|AMAZÔNIA
AC|50|50|0|0|0|AMAZÔNIA
AM|200|200|0|0|0|AMAZÔNIA
RR|8000|8000.73|0|0|0|AMAZÔNIA
PA|63600|13792.6|5634.79|38185.3|162.346|AMAZÔNIA
AP|0|0|0|0|0|AMAZÔNIA
TO|1000|1000|0|0|0|AMAZÔNIA
MA|0|0|0|0|0|AMAZÔNIA
MT|1322956|156352|69331.4|344324|64384.5|AMAZÔNIA
RO|39000|8730.68|0|29618.3|642.021|CERRADO
PA|7460|1700|3172.16|2565.43|11.6822|CERRADO
TO|331508|32840.4|86651.2|137273|9821.01|CERRADO
MA|421520|66562.9|132082|189301|14228.9|CERRADO
PI|253566|107704|57351.3|57255.3|15025.2|CERRADO
BA|903000|332655|104003|357408|90534.5|CERRADO
MG|793077|368037|139259|189950|63178.3|CERRADO
SP|161189|30265|70955.5|21572.1|10284.7|CERRADO
PR|55200|16838.4|7011.74|21661.9|8064.83|CERRADO
MS|1281130|646417|54106.8|404804|92195.5|CERRADO
MT|4336193|1.07509e+06|639150|1.49716e+06|523573|CERRADO
GO|2179921|1.21275e+06|501814|286943|167406|CERRADO
DF|48712|0|21505.6|12362.1|14836.1|CERRADO
PI|0|0|0|0|0|CAATINGA
CE|512|0|0|0|489.827|CAATINGA
RN|0|0|0|0|0|CAATINGA
PB|0|0|0|0|0|CAATINGA
PE|0|0|0|0|0|CAATINGA
AL|180|0|0|0|180|CAATINGA
SE|0|0|0|0|0|CAATINGA
BA|2018|0|0|1251.34|33.1283|CAATINGA
MG|10|0|0|0|0|CAATINGA
RN|0|0|0|0|0|MATA ATLÂNTICA
PB|0|0|0|0|0|MATA ATLÂNTICA
PE|0|0|0|0|0|MATA ATLÂNTICA
AL|0|0|0|0|0|MATA ATLÂNTICA
SE|0|0|0|0|0|MATA ATLÂNTICA
BA|0|0|0|0|0|MATA ATLÂNTICA
MG|77515|19450|36472.3|7262.13|9873.45|MATA ATLÂNTICA
ES|0|0|0|0|0|MATA ATLÂNTICA
RJ|0|0|0|0|0|MATA ATLÂNTICA
SP|364751|106006|129440|49437|19647.3|MATA ATLÂNTICA
PR|3913913|1.44108e+06|884692|1.06045e+06|474172|MATA ATLÂNTICA
SC|373358|161633|101470|71402.7|20705.3|MATA ATLÂNTICA
RS|1460074|626134|263333|298653|250711|MATA ATLÂNTICA
MS|450901|193762|128630|83871.4|42814.4|MATA ATLÂNTICA
GO|650|650|0|0|0|MATA ATLÂNTICA
RS|2344351|866785|539985|398787|522266|PAMPA
MS|0|0|0|0|0|PANTANAL
MT|0|0|0|0|0|PANTANAL
nan|0|86.6477|520399|954720|384197|nan
"""
    
    # Parse CSV data
    df = pd.read_csv(io.StringIO(csv_data), sep='|')
    
    # Clean Data
    # Handle the 'nan' row at the end which represents "NA" (Not Assigned/Unknown)
    df.loc[df['Biome'].astype(str) == 'nan', 'Biome'] = 'NA'
    df.loc[df['UF'].astype(str) == 'nan', 'UF'] = 'NA'
    
    # Convert columns to numeric
    cols = ['Domestic', 'China', 'EU', 'Other_countries']
    for col in cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Convert to Millions of Hectares
    df[cols] = df[cols] / 1_000_000
    
    # Define the specific order of Biomes as seen in the chart (Clockwise starting from top-right)
    # Visual inspection: Amazônia -> Pantanal -> Cerrado -> Caatinga -> Pampa -> Mata Atlântica -> NA
    biome_order = ['AMAZÔNIA', 'PANTANAL', 'CERRADO', 'CAATINGA', 'PAMPA', 'MATA ATLÂNTICA', 'NA']
    
    # Define Colors (matching the image)
    colors = {
        'Domestic': '#9ecae1',       # Light Blue
        'China': '#fec44f',          # Orange/Yellow
        'EU': '#5f8d8b',             # Teal/Greenish
        'Other_countries': '#d77668' # Muted Red/Pink
    }
    
    # 2. Setup Polar Plot
    fig = plt.figure(figsize=(12, 12))
    ax = plt.subplot(111, polar=True)
    
    # Configuration for layout
    start_angle = np.pi / 2 + 0.2 # Start slightly to the right of 12 o'clock
    direction = -1 # Clockwise
    
    # Calculate angles
    # We need to count total bars and add gaps between groups
    group_gap = 3  # Gap size in terms of bar width units
    bar_width_unit = 1
    
    # Group data
    grouped = df.groupby('Biome')
    
    # Create a structured list based on biome_order
    plot_data = []
    for biome in biome_order:
        if biome in grouped.groups:
            group_df = grouped.get_group(biome)
            # For specific biomes, we might need to sort UFs or keep original order.
            # The chart seems to follow the CSV order roughly, but let's stick to CSV order within groups.
            plot_data.append({
                'biome': biome,
                'data': group_df
            })
    
    total_bars = sum(len(g['data']) for g in plot_data)
    total_gaps = len(plot_data)
    total_units = total_bars * bar_width_unit + total_gaps * group_gap
    
    # Angle per unit
    angle_per_unit = (2 * np.pi) / total_units
    
    # Plotting Loop
    current_angle = start_angle
    
    # Inner hole radius (negative ylim creates the hole)
    inner_radius_offset = -2.5
    ax.set_ylim(inner_radius_offset, 6.5) # Max value is around 6
    
    # Remove standard elements
    ax.spines['polar'].set_visible(False)
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.grid(False)
    
    # Draw custom grid lines
    grid_values = [0, 1.5, 3, 4.5, 6]
    for val in grid_values:
        if val == 0:
            # Solid line for 0 baseline
            ax.plot(np.linspace(0, 2*np.pi, 100), [val]*100, color='black', linewidth=0.8, zorder=1)
        else:
            # Dashed lines for values
            ax.plot(np.linspace(0, 2*np.pi, 100), [val]*100, color='gray', linestyle=(0, (5, 10)), linewidth=0.5, zorder=0)
            # Add grid labels
            ax.text(np.pi/2, val, str(val), ha='center', va='center', color='silver', fontsize=10, fontweight='light')

    # Iterate through groups and plot
    for group in plot_data:
        biome_name = group['biome']
        df_group = group['data']
        
        n_bars = len(df_group)
        
        # Calculate start and end angles for the group (for the arc label)
        group_start_angle = current_angle
        
        for idx, row in df_group.iterrows():
            # Calculate bar position
            # Center of the bar
            theta = current_angle + (direction * angle_per_unit * bar_width_unit / 2)
            width = angle_per_unit * bar_width_unit * 0.9 # 0.9 for slight gap between bars
            
            # Stack values
            bottom = 0
            for col in cols:
                val = row[col]
                if val > 0:
                    ax.bar(theta, val, width=width, bottom=bottom, color=colors[col], edgecolor='none', zorder=2)
                    bottom += val
            
            # Add UF Label
            # Rotate label
            rot = math.degrees(theta)
            # Normalize rotation to -180 to 180
            # Adjust for readability
            label_rot = rot
            text_anchor = theta
            
            # Distance for label
            label_r = max(bottom, 0) + 0.2
            if label_r < 0.5: label_r = 0.5 # Minimum distance for empty bars
            
            # Logic to flip text on the left side of the circle
            # In polar plot with direction -1 and offset pi/2:
            # 0 to -pi is right side, -pi to -2pi is left side
            # Normalize angle to 0-360 relative to screen
            screen_angle = (math.degrees(theta) % 360)
            
            # Matplotlib polar rotation logic is tricky. 
            # Let's calculate alignment based on geometric quadrants.
            # Top-Right (90 to 0), Bottom-Right (0 to -90), Bottom-Left (-90 to -180), Top-Left (-180 to -270)
            
            # Simplified: if the bar is on the left side, flip text 180
            # Left side is roughly when cos(theta) < 0
            if np.cos(theta) < 0:
                rot_text = rot + 180
                ha = 'right'
                va = 'center'
                # Push label out a bit more on left side to avoid overlap
                label_r += 0.1 
            else:
                rot_text = rot
                ha = 'left'
                va = 'center'
            
            if row['UF'] != 'NA':
                ax.text(theta, label_r, row['UF'], rotation=rot_text, ha=ha, va=va, fontsize=9, color='#555555')
            
            # Advance angle
            current_angle += direction * angle_per_unit * bar_width_unit
            
        group_end_angle = current_angle
        
        # Draw Biome Arc and Label
        # The arc should be inside the zero line (negative radius visually, but here radius < 0 is hidden)
        # We used set_ylim(-2.5, ...). 0 is the baseline.
        # We can draw the arc at radius = -0.3 or similar.
        
        # Calculate mean angle for label
        # Note: angles are decreasing because direction is -1
        # We need the midpoint between start and end
        mid_angle = (group_start_angle + group_end_angle) / 2
        
        # Draw Arc line
        arc_r = -0.3
        # Create linspace for arc
        arc_theta = np.linspace(group_start_angle, group_end_angle, 50)
        # Add slight padding to arc so it doesn't touch the next group
        pad = angle_per_unit * 0.2
        arc_theta_padded = np.linspace(group_start_angle - direction*pad, group_end_angle + direction*pad, 50)
        
        ax.plot(arc_theta_padded, [arc_r]*50, color='black', linewidth=1)
        
        # Biome Label
        # Fix capitalization for display
        display_name = biome_name.title()
        if display_name == "Na": display_name = "NA"
        if display_name == "Mata Atlântica": display_name = "Mata Atlântica" # Keep accent
        
        # Text placement
        text_r = -0.8
        
        # Rotation for biome label
        # Similar logic to UF labels but perpendicular to radius
        text_rot = math.degrees(mid_angle)
        
        # Adjust rotation so text is upright
        if np.cos(mid_angle) < 0:
            text_rot += 180
        
        # Special adjustment for "Pantanal" which is very small
        if biome_name == 'PANTANAL':
            text_r = -1.2 # Move it further in
        
        ax.text(mid_angle, text_r, display_name, rotation=text_rot, ha='center', va='center', fontsize=10)
        
        # Add Gap
        current_angle += direction * angle_per_unit * group_gap

    # 3. Final Touches
    plt.title("2008", loc='left', fontsize=16, y=0.95)
    
    # Legend (Manual construction to match style)
    # Since we can't easily use the default legend with polar plots without overlap, 
    # we assume the colors are self-explanatory or would be added externally, 
    # but let's try to add a small custom legend if needed. 
    # The provided image doesn't explicitly show a legend box, but the colors imply categories.
    # We will skip a formal legend box to match the clean look of the provided image, 
    # as the prompt asks to reproduce the chart image.
    
    # Save
    plt.savefig(output_filename, dpi=300, bbox_inches='tight', facecolor='white')
    # plt.close() # Good practice but not strictly required for script end

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    generate_chart(output_file)