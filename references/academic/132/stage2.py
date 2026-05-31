import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math

# 1. Source Data Embedded
csv_data = """UF,Total,Domestic,China,EU,Other_countries,Biome
RO,192171,92975,32773.1,46514.5,19776.9,AMAZÔNIA
AC,100,100,0,0,0,AMAZÔNIA
AM,0,0,0,0,0,AMAZÔNIA
RR,24035,23986.3,0,0,48.6071,AMAZÔNIA
PA,415073,24021.8,134484,178165,40557.2,AMAZÔNIA
AP,15442,0,0,8823.84,0,AMAZÔNIA
TO,16400,4800,6928.99,4635.81,0,AMAZÔNIA
MA,48220,22110.5,8596.73,682.216,3393.44,AMAZÔNIA
MT,3586371,219923,937849,560079,539078,AMAZÔNIA
RO,54000,0,15972.4,29905.2,8103.99,CERRADO
PA,18740,0,1813.03,1932.31,403.943,CERRADO
TO,832445,204571,298330,261551,36658.5,CERRADO
MA,735434,117847,340054,178733,93318.9,CERRADO
PI,563084,274307,154581,57954.3,34303.9,CERRADO
BA,1532113,596249,378943,334986,186090,CERRADO
MG,1259933,284464,506049,198103,218211,CERRADO
SP,311627,28978.6,225465,6808.06,42054.6,CERRADO
PR,62500,0,50023.2,49.7085,11841.6,CERRADO
MS,1762332,525466,364488,368673,335641,CERRADO
MT,5561492,1.59356e+06,1.71516e+06,864313,987993,CERRADO
GO,3321325,1.82668e+06,860216,262669,302562,CERRADO
DF,70875,26354.6,33737.1,3307.34,7432.41,CERRADO
PI,0,0,0,0,0,CAATINGA
CE,0,0,0,0,0,CAATINGA
RN,0,0,0,0,0,CAATINGA
PB,0,0,0,0,0,CAATINGA
PE,0,0,0,0,0,CAATINGA
AL,0,0,0,0,0,CAATINGA
SE,0,0,0,0,0,CAATINGA
BA,4565,4328.29,231.435,0,0,CAATINGA
MG,1320,0,810.823,0,287.273,CAATINGA
RN,0,0,0,0,0,MATA ATLÂNTICA
PB,0,0,0,0,0,MATA ATLÂNTICA
PE,0,0,0,0,0,MATA ATLÂNTICA
AL,343,0,0,342.987,0,MATA ATLÂNTICA
SE,0,0,0,0,0,MATA ATLÂNTICA
BA,0,0,0,0,0,MATA ATLÂNTICA
MG,210971,44405.3,101374,14396.8,44607.1,MATA ATLÂNTICA
ES,0,0,0,0,0,MATA ATLÂNTICA
RJ,0,0,0,0,0,MATA ATLÂNTICA
SP,537212,126978,340183,5536.81,43555.6,MATA ATLÂNTICA
PR,5392239,1.82118e+06,2.3494e+06,452330,648287,MATA ATLÂNTICA
SC,660764,131772,267156,76739.3,94463.4,MATA ATLÂNTICA
RS,1811940,750697,636769,133032,208583,MATA ATLÂNTICA
MS,685918,213725,235504,78762.4,105903,MATA ATLÂNTICA
GO,1197,97,111.217,834.128,148.951,MATA ATLÂNTICA
RS,3652144,822125,1.78025e+06,419074,545225,PAMPA
MS,80,0,0,0,0,PANTANAL
MT,0,0,0,0,0,PANTANAL
nan,0,83.9931,1.52661e+06,233932,680138,nan"""

def generate_chart(output_filename):
    # 2. Data Processing
    df = pd.read_csv(io.StringIO(csv_data))
    
    # Handle the NA row at the bottom
    df['Biome'] = df['Biome'].fillna('NA')
    df['UF'] = df['UF'].fillna('NA')
    
    # Convert units to Millions of Hectares
    cols_to_scale = ['Total', 'Domestic', 'China', 'EU', 'Other_countries']
    df[cols_to_scale] = df[cols_to_scale] / 1_000_000
    
    # Define the specific order of Biomes as seen in the chart (Clockwise)
    # Visual inspection: Amazônia -> Pantanal -> Cerrado -> Caatinga -> Pampa -> Mata Atlântica -> NA
    # Note: The chart starts Amazônia around 12:00/1:00.
    biome_order = [
        'AMAZÔNIA', 
        'PANTANAL', 
        'CERRADO', 
        'CAATINGA', 
        'PAMPA', 
        'MATA ATLÂNTICA', 
        'NA'
    ]
    
    # Sort dataframe
    df['Biome'] = pd.Categorical(df['Biome'], categories=biome_order, ordered=True)
    # Within Biome, sort by UF alphabetically
    df = df.sort_values(by=['Biome', 'UF'])
    
    # 3. Plot Configuration
    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(111, projection='polar')
    
    # Colors based on visual inspection
    # Domestic (Base, Light Blue), EU (Yellow/Orange), China (Teal), Other (Red/Salmon)
    colors = {
        'Domestic': '#9ecae1',       # Light Blue
        'EU': '#fec44f',             # Sandy Yellow/Orange
        'China': '#568f8b',          # Teal/Slate Green
        'Other_countries': '#d97c6e' # Salmon Red
    }
    
    # Layout parameters
    inner_radius = 2.0  # Size of the hole
    bar_width = 0.8     # Width of bars relative to slot
    group_gap = 0.3     # Gap between biomes (in radians)
    
    # Calculate angles
    # We need to distribute bars around the circle, adding gaps between groups
    groups = df.groupby('Biome', observed=True)
    total_bars = len(df)
    num_groups = len(groups)
    
    # Calculate total available angle (2pi) minus gaps
    # We allocate space for bars and space for gaps
    # Let's define a unit 'step'
    # Total steps = total_bars + (num_groups * gap_size_in_bar_units)
    gap_in_steps = 2 # equivalent to 2 bars width
    total_steps = total_bars + (num_groups * gap_in_steps)
    step_angle = (2 * np.pi) / total_steps
    
    current_angle = np.pi / 2 - (step_angle * gap_in_steps / 2) # Start near top (12 o'clock), adjusted
    # Actually, let's start slightly to the right to match Amazônia position
    current_angle = 1.3 # Approximate starting radian for Amazônia based on image
    
    # Store label positions
    biome_labels = []
    
    # Iterate through groups and plot
    for biome_name, group_data in groups:
        # Start angle for this group
        group_start_angle = current_angle
        
        # Reverse group data to match clockwise filling if we subtract angles, 
        # but here we will subtract angles to go clockwise.
        # The chart goes Clockwise: Amazônia -> Pantanal -> ...
        
        n_bars = len(group_data)
        
        # Calculate angles for bars in this group
        # We go clockwise, so we subtract from current_angle
        theta = []
        for i in range(n_bars):
            theta.append(current_angle - (i * step_angle))
        
        theta = np.array(theta)
        
        # Plot bars
        # Stack order: Domestic -> EU -> China -> Other
        # Note: Based on visual analysis of MT bar: Blue base, Yellow next, Teal big, Red top.
        
        # Bottoms
        b1 = np.zeros(n_bars) + inner_radius
        b2 = b1 + group_data['Domestic'].values
        b3 = b2 + group_data['EU'].values
        b4 = b3 + group_data['China'].values
        
        # Draw segments
        ax.bar(theta, group_data['Domestic'], width=step_angle*bar_width, bottom=b1, color=colors['Domestic'], edgecolor='none')
        ax.bar(theta, group_data['EU'], width=step_angle*bar_width, bottom=b2, color=colors['EU'], edgecolor='none')
        ax.bar(theta, group_data['China'], width=step_angle*bar_width, bottom=b3, color=colors['China'], edgecolor='none')
        ax.bar(theta, group_data['Other_countries'], width=step_angle*bar_width, bottom=b4, color=colors['Other_countries'], edgecolor='none')
        
        # State Labels (UF)
        for t, (_, row) in zip(theta, group_data.iterrows()):
            total_height = row['Total']
            if total_height > 0 or row['UF'] == 'NA':
                label_r = inner_radius + total_height + 0.2
                rotation = np.degrees(t)
                
                # Flip text if on the left side
                if 90 < rotation < 270:
                    rotation += 180
                    ha = 'right'
                    va = 'center'
                else:
                    ha = 'left'
                    va = 'center'
                
                # Adjust rotation to be strictly radial
                # Matplotlib rotation is counter-clockwise, t is radians
                # We need to normalize t to 0-360
                deg = np.degrees(t) % 360
                
                # Logic for readability alignment
                if 90 < deg < 270:
                    align_rotation = deg + 180
                    alignment = 'right'
                    offset = 0.1
                else:
                    align_rotation = deg
                    alignment = 'left'
                    offset = 0.1
                
                ax.text(t, inner_radius + total_height + offset, row['UF'], 
                        rotation=align_rotation, ha=alignment, va='center', 
                        fontsize=11, color='#666666', rotation_mode='anchor')

        # Biome Group Label Logic
        group_end_angle = theta[-1]
        mid_angle = (group_start_angle + group_end_angle) / 2
        
        # Draw the curved line for the biome
        # Arc from start to end of bars, slightly inside inner radius
        arc_r = inner_radius - 0.2
        arc_theta = np.linspace(group_start_angle + (step_angle*bar_width/2), group_end_angle - (step_angle*bar_width/2), 50)
        ax.plot(arc_theta, [arc_r]*len(arc_theta), color='black', linewidth=1)
        
        # Biome Name
        # Title case the name
        display_name = biome_name.title()
        if display_name == "Na": display_name = "NA"
        
        # Adjust text rotation
        deg = np.degrees(mid_angle) % 360
        if 90 < deg < 270:
            text_rot = deg + 180
            va = 'bottom' # Since it's flipped, bottom is towards center
        else:
            text_rot = deg
            va = 'top'
            
        ax.text(mid_angle, arc_r - 0.1, display_name, 
                rotation=text_rot, ha='center', va=va, 
                fontsize=12, color='black')

        # Update current angle for next group (add gap)
        current_angle = group_end_angle - (step_angle * gap_in_steps)

    # 4. Styling and Grid
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1) # Clockwise
    ax.spines['polar'].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Custom Grid Lines (1.5, 3.0, 4.5)
    grid_values = [1.5, 3.0, 4.5]
    for val in grid_values:
        r = inner_radius + val
        # Draw dashed circle
        circle = plt.Circle((0, 0), r, transform=ax.transData._b, fill=False, 
                            edgecolor='#cccccc', linestyle='--', linewidth=0.8, alpha=0.7)
        ax.add_artist(circle)
        
        # Add label for the grid line
        # Position labels around 11 o'clock (approx 2.8 radians or 160 degrees)
        label_angle = np.radians(105) # Slightly past top
        ax.text(label_angle, r, str(val), ha='center', va='center', 
                color='#999999', fontsize=10, backgroundcolor='white')

    # Title
    plt.text(0.05, 0.95, "2016", transform=fig.transFigure, fontsize=18, ha='left')

    # Save output
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    generate_chart(output_file)