import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def generate_chart(output_filename='output.png'):
    # 1. Load Data
    # Using the provided source data exactly as a string buffer
    csv_data = """
UF|Total|Domestic|China|EU|Other countries|Biome
RO|1.7028|0.714085|0|0.546341|0.214683|AMAZÔNIA
AC|0|0|0|0|0|AMAZÔNIA
AM|0.0122237|0.0122236|0|0|0|AMAZÔNIA
RR|0.218045|0.218045|0|0|0|AMAZÔNIA
PA|2.36176|0|0.359321|0.477212|0.50947|AMAZÔNIA
AP|0.0885287|0|0|0|0|AMAZÔNIA
TO|0.133839|0.0358671|0.0221865|0.00423591|0.00800975|AMAZÔNIA
MA|0.701576|0.250605|0.0567376|0.0185344|0.018738|AMAZÔNIA
MT|17.9337|0.801797|3.71661|1.68935|4.2973|AMAZÔNIA
RO|0.268529|0|0.000890181|0.188907|0.0758579|CERRADO
PA|0.0281624|0|0|0|0|CERRADO
TO|5.87683|0.750694|2.405|0.368623|0.875614|CERRADO
MA|4.66546|0.0746332|2.54759|0.462159|0.51833|CERRADO
PI|4.6205|0.625936|1.09801|0.18551|0.316376|CERRADO
BA|9.16888|1.41234|3.39683|1.97755|0.914535|CERRADO
MG|7.46717|1.2042|3.0454|0.336829|1.47383|CERRADO
SP|2.31141|0.426538|1.35377|0.0449633|0.37721|CERRADO
PR|0.222688|0.076108|0.136252|2.69587e-09|0.00823693|CERRADO
MS|11.5686|2.52942|5.72548|1.32195|1.52692|CERRADO
MT|23.8678|3.99933|8.19591|2.19776|5.91568|CERRADO
GO|14.882|4.52926|6.42301|1.03616|2.05772|CERRADO
DF|0.385592|0.217271|0.148304|0.000229712|0.0151448|CERRADO
PI|0|0|0|0|0|CAATINGA
CE|0.0021375|0|0.00213535|0|0|CAATINGA
RN|0|0|0|0|0|CAATINGA
PB|0|0|0|0|0|CAATINGA
PE|0|0|0|0|0|CAATINGA
AL|0|0|0|0|0|CAATINGA
SE|0|0|0|0|0|CAATINGA
BA|0.0508217|0.0415239|0.0092731|-1.33004e-07|0|CAATINGA
MG|0.00712854|0|0.000410985|0|0.000307625|CAATINGA
RN|0|0|0|0|0|MATA ATLÂNTICA
PB|0|0|0|0|0|MATA ATLÂNTICA
PE|0|0|0|0|0|MATA ATLÂNTICA
AL|0.00342842|0|0.00342191|0|0|MATA ATLÂNTICA
SE|0|0|0|0|0|MATA ATLÂNTICA
BA|0|0|0|0|0|MATA ATLÂNTICA
MG|1.40751|0.495722|0.498626|0.0387838|0.194424|MATA ATLÂNTICA
ES|0|0|0|0|0|MATA ATLÂNTICA
RJ|0|0|0|0|0|MATA ATLÂNTICA
SP|4.19579|0.936257|2.13859|0.299379|0.423268|MATA ATLÂNTICA
PR|31.4401|7.33527|16.782|2.83486|3.29996|MATA ATLÂNTICA
SC|3.80972|0.751658|2.37845|0.208518|0.323453|MATA ATLÂNTICA
RS|8.18601|3.60894|3.51158|0.184026|0.489045|MATA ATLÂNTICA
MS|3.03427|0.746492|1.32953|0.456528|0.308773|MATA ATLÂNTICA
GO|0.0068595|0.0066709|0|0|0|MATA ATLÂNTICA
RS|17.5383|3.79974|10.8462|0.680015|1.52441|PAMPA
MS|0|0|0|0|0|PANTANAL
MT|0|0|0|0|0|PANTANAL
nan|0|0.000359487|9.92086|8.27656|7.98418|nan
"""
    
    # Read CSV
    df = pd.read_csv(io.StringIO(csv_data), sep='|')
    
    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Clean string columns
    df['UF'] = df['UF'].astype(str).str.strip()
    df['Biome'] = df['Biome'].astype(str).str.strip()
    
    # Handle the 'nan' row
    df.loc[df['UF'] == 'nan', 'UF'] = 'NA'
    df.loc[df['Biome'] == 'nan', 'Biome'] = 'NA'
    
    # Define the specific order of Biomes as seen in the chart (Clockwise)
    # Visual order: Amazônia -> Pantanal -> Cerrado -> Caatinga -> Pampa -> Mata Atlântica -> NA
    biome_order = ['AMAZÔNIA', 'PANTANAL', 'CERRADO', 'CAATINGA', 'PAMPA', 'MATA ATLÂNTICA', 'NA']
    
    # Sort dataframe
    df['Biome'] = pd.Categorical(df['Biome'], categories=biome_order, ordered=True)
    # Within biome, sort by UF alphabetically
    df = df.sort_values(['Biome', 'UF']).reset_index(drop=True)
    
    # 2. Plot Configuration
    
    # Colors extracted from the image
    # Order: Domestic (Bottom), China, EU, Other (Top)
    # Based on visual analysis:
    # Domestic: Very Light Blue
    # China: Medium Steel Blue (Darker than EU)
    # EU: Light Blue (Lighter than China)
    # Other: Dark Navy
    colors = {
        'Domestic': '#dbebf7',       # Very light
        'China': '#5a8ac6',          # Medium/Steel
        'EU': '#9ecae1',             # Light blue
        'Other countries': '#102a42' # Dark Navy
    }
    
    # Setup Polar Plot
    fig = plt.figure(figsize=(12, 12), dpi=100)
    ax = plt.subplot(111, projection='polar')
    
    # Parameters for layout
    # Start from top (pi/2) and go clockwise (-1)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    
    # Define gaps and widths
    num_bars = len(df)
    num_groups = len(biome_order)
    
    # We need to calculate angles manually to insert gaps between groups
    # Total available angle is 2*pi. Let's reserve some for gaps.
    gap_size = 0.08  # Radians for gap between biomes
    total_gap = gap_size * num_groups
    available_angle = 2 * np.pi - total_gap
    bar_width = available_angle / num_bars
    
    # Calculate angles for each bar
    angles = []
    current_angle = 0
    
    # Store label positions
    label_data = []
    biome_label_data = []
    
    for biome in biome_order:
        group_data = df[df['Biome'] == biome]
        if len(group_data) == 0:
            continue
            
        start_angle = current_angle
        
        for _, row in group_data.iterrows():
            angles.append(current_angle + bar_width/2)
            
            # Store data for plotting labels later
            total_val = row['Domestic'] + row['China'] + row['EU'] + row['Other countries']
            label_data.append({
                'angle': current_angle + bar_width/2,
                'text': row['UF'],
                'val': total_val
            })
            
            current_angle += bar_width
        
        # Calculate center of the group for Biome label
        end_angle = current_angle
        mid_angle = (start_angle + end_angle) / 2
        biome_label_data.append({
            'angle': mid_angle,
            'text': biome.title() if biome != 'NA' else 'NA' # Title case for biomes
        })
        
        # Add gap
        current_angle += gap_size

    # 3. Draw Bars
    
    # Prepare data vectors aligned with the calculated angles
    # We iterate through the sorted dataframe again to match the angles list
    # (The dataframe was sorted by Biome then UF, which matches our loop above)
    
    # Stack values
    domestic = df['Domestic'].values
    china = df['China'].values
    eu = df['EU'].values
    other = df['Other countries'].values
    
    # Plot stacks
    # Layer 1: Domestic
    ax.bar(angles, domestic, width=bar_width, color=colors['Domestic'], edgecolor='none')
    
    # Layer 2: China
    ax.bar(angles, china, width=bar_width, bottom=domestic, color=colors['China'], edgecolor='none')
    
    # Layer 3: EU
    ax.bar(angles, eu, width=bar_width, bottom=domestic+china, color=colors['EU'], edgecolor='none')
    
    # Layer 4: Other
    ax.bar(angles, other, width=bar_width, bottom=domestic+china+eu, color=colors['Other countries'], edgecolor='none')
    
    # 4. Styling and Labels
    
    # Remove spines
    ax.spines['polar'].set_visible(False)
    
    # Set Grid
    # The chart has a hole in the middle. We simulate this by setting negative ylim.
    inner_radius = -10
    ax.set_ylim(inner_radius, 38) # Max value is around 31 (PR), grid goes to 35
    
    # Custom Gridlines
    grid_values = [5, 15, 25, 35]
    ax.set_yticks(grid_values)
    ax.set_yticklabels([str(x) for x in grid_values], color='#999999', fontsize=12)
    ax.set_rlabel_position(0) # Labels at the top
    
    # Customize grid style
    ax.grid(axis='y', linestyle='--', alpha=0.5, color='gray')
    ax.grid(axis='x', visible=False) # Hide radial lines
    
    # Add UF Labels (States)
    for item in label_data:
        angle_rad = item['angle']
        angle_deg = np.degrees(angle_rad)
        val = item['val']
        text = item['text']
        
        # Skip labels for 0 values if they clutter (though chart shows some small ones)
        # The chart shows labels for almost all bars.
        
        # Rotation logic
        # In polar plot with offset pi/2 and direction -1:
        # 0 deg (Top) -> 90 deg (Right) -> 180 deg (Bottom) -> 270 deg (Left)
        # We want text to radiate outwards.
        
        # Normalize angle to 0-360
        norm_angle = angle_deg % 360
        
        # Determine rotation
        if 90 < norm_angle < 270:
            rotation = 90 - norm_angle + 180
            alignment = 'right' # Text ends at bar
            # For left side, we might want to flip logic if we want text outside
            # Actually, standard is:
            rotation = 90 - norm_angle + 180
        else:
            rotation = 90 - norm_angle
        
        # Distance from center
        # Add a small buffer
        dist = max(val, 0) + 1
        
        # Adjust text alignment and position based on hemisphere to ensure readability
        # Top-Right to Bottom-Right (0 to 180): Text reads bottom-to-top?
        # Let's stick to standard radial rotation
        
        # Refined rotation for readability
        rot = np.degrees(angle_rad)
        if 0 <= rot < 180:
            rot_text = 90 - rot
            ha = 'left'
            va = 'center'
            dist_offset = 0.5
        else:
            rot_text = 90 - rot + 180
            ha = 'right'
            va = 'center'
            dist_offset = 1.5
            
        # Special handling for very small bars to push labels out slightly?
        # The chart puts labels right on top of the bar.
        
        ax.text(angle_rad, max(val, 0) + 1, text, 
                rotation=rot_text, ha=ha, va=va, 
                fontsize=11, color='#555555')

    # Add Biome Labels (Inner Circle)
    for item in biome_label_data:
        angle_rad = item['angle']
        text = item['text']
        
        # Position inside the hole
        # inner_radius is -10. We place text around -2 or 0 relative to the data start?
        # Matplotlib polar plot: 0 is the center of data. -10 is the hole.
        # We want to place text just outside the hole, i.e., near 0.
        
        # Rotation
        rot = np.degrees(angle_rad)
        
        # Flip text on the left side for readability
        if 90 < rot < 270:
            rot_text = 90 - rot + 180
        else:
            rot_text = 90 - rot
            
        ax.text(angle_rad, -2, text, 
                rotation=rot_text, ha='center', va='center', 
                fontsize=10, color='black')

    # 5. Final Touches
    
    # Title "2020"
    # Place it manually in figure coordinates or axes coordinates
    plt.text(0.05, 0.95, "2020", transform=fig.transFigure, fontsize=20, color='black')
    
    # Remove the circle line around the plot
    ax.spines['polar'].set_visible(False)
    
    # Save
    plt.savefig(output_filename, bbox_inches='tight', dpi=150, facecolor='white')
    # plt.close() # Good practice, but script ends anyway

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)