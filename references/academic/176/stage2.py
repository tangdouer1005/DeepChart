import sys
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle

def generate_chart(output_filename='output.png'):
    # 1. Source Data
    csv_data = """feature_1,feature_2,feature_3,feature_4,feature_5,feature_6,feature_7,feature_8,feature_9,feature_10,feature_11,feature_12,feature_13,feature_14,feature_15,feature_16,feature_17,feature_18,feature_19,feature_20,feature_21,feature_22,feature_23,feature_24,source
86,87,91,7,95,105,8,23,103,14,1,88,9,101,21,17,111,11,11,87,92,87,25,20,NSF
98,8,28,87,56,60,72,112,82,86,70,5,81,3,80,83,12,98,109,3,25,14,143,88,NSFC
"""
    
    # Load data
    df = pd.read_csv(io.StringIO(csv_data))
    
    # 2. Data Preparation
    # Define the labels corresponding to feature_1 to feature_24 based on visual mapping
    # The chart starts at 11:30 (feature_1) and goes clockwise.
    # To plot programmatically starting from North (12:00) clockwise, we shift the data
    # so feature_2 is the first item and feature_1 is the last.
    
    labels_ordered = [
        "Frameworks and models",                  # feature_1
        "Exploring social and behavioral impacts",# feature_2
        "Enhancing urban efficiency",             # feature_3
        "Deploying smart city infrastructure",    # feature_4
        "Data-driven hypothesis testing",         # feature_5
        "Commercial products or services",        # feature_6
        "Collaboration with industry and government", # feature_7
        "Building practical solutions",           # feature_8
        "Understanding urban dynamics",           # feature_9
        "Theoretical framework development",      # feature_10
        "Technological innovation",               # feature_11
        "System integration",                     # feature_12
        "Supporting scalability and commercialization", # feature_13
        "Modeling and simulation",                # feature_14
        "Quantitative and qualitative analysis",  # feature_15
        "Prototyping and testing",                # feature_16
        "New theoretical insights",               # feature_17
        "Multidisciplinary collaboration",        # feature_18
        "Iterative design and development",       # feature_19
        "Investigating long-term trends",         # feature_20
        "Improved city services",                 # feature_21
        "Identification of knowledge gaps",       # feature_22
        "Guidance for policymakers",              # feature_23
        "Functioning prototypes or systems"       # feature_24
    ]
    
    # Extract values
    nsf_row = df[df['source'] == 'NSF'].iloc[0, :-1].astype(int).values
    nsfc_row = df[df['source'] == 'NSFC'].iloc[0, :-1].astype(int).values
    
    # Shift data to align with 12:00 start for plotting convenience
    # Original: [F1, F2, ..., F24]
    # Shifted:  [F2, F3, ..., F24, F1]
    # This puts "Exploring social..." (F2) at the first sector clockwise from North.
    
    labels_shifted = labels_ordered[1:] + labels_ordered[:1]
    nsf_shifted = np.concatenate([nsf_row[1:], nsf_row[:1]])
    nsfc_shifted = np.concatenate([nsfc_row[1:], nsfc_row[:1]])
    
    # 3. Plotting Setup
    num_vars = len(labels_shifted)
    
    # Compute angles
    # We want the first bar centered at 7.5 degrees (pi/24) if starting from North
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)
    angles = angles + (np.pi / num_vars) # Shift to center bars in sectors
    
    # Initialize Polar Plot
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    
    # Set Start to North and Direction Clockwise
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    
    # Styling Constants
    BAR_WIDTH = 0.12
    COLOR_NSF = '#9ebcda'   # Light Blue
    COLOR_NSFC = '#fdbf6f'  # Light Orange
    COLOR_GRID_BLUE = '#5B9BD5'
    COLOR_GRID_ORANGE = '#ED7D31'
    MAX_VAL = 160
    
    # 4. Draw Bars
    # NSF Bars (Left side of the group)
    ax.bar(angles - BAR_WIDTH/2, nsf_shifted, width=BAR_WIDTH, color=COLOR_NSF, 
           alpha=0.9, label='NSF (n = 179)', zorder=10)
    
    # NSFC Bars (Right side of the group)
    ax.bar(angles + BAR_WIDTH/2, nsfc_shifted, width=BAR_WIDTH, color=COLOR_NSFC, 
           alpha=0.9, label='NSFC (n = 196)', zorder=10)
    
    # 5. Custom Grid and Spines
    ax.set_ylim(0, MAX_VAL)
    ax.axis('off') # Turn off default axis
    
    # Draw Radial Separators
    # These are at the boundaries of the sectors (angles - pi/24)
    separator_angles = angles - (np.pi / num_vars)
    for ang in separator_angles:
        ax.plot([ang, ang], [0, MAX_VAL], color='gray', linewidth=0.5, linestyle='-', zorder=5)
        
    # Draw Concentric Circles (Grid Lines)
    # 1. Inner Blue Dashed Circle (approx value 80 based on visual inspection)
    grid_val_1 = 80
    ax.plot(np.linspace(0, 2*np.pi, 100), [grid_val_1]*100, color=COLOR_GRID_BLUE, 
            linestyle='--', linewidth=1, zorder=5, alpha=0.7)
            
    # 2. Outer Orange Dashed Circle (approx value 100 based on visual inspection)
    grid_val_2 = 100
    ax.plot(np.linspace(0, 2*np.pi, 100), [grid_val_2]*100, color=COLOR_GRID_ORANGE, 
            linestyle='--', linewidth=1, zorder=5, alpha=0.7)
            
    # 3. Outer Solid Boundary
    ax.plot(np.linspace(0, 2*np.pi, 100), [MAX_VAL]*100, color='black', 
            linewidth=0.8, zorder=5)

    # 6. Add Labels
    # Logic to rotate text to be readable
    for angle, label in zip(angles, labels_shifted):
        # Convert angle to degrees for rotation calculation
        angle_deg = np.degrees(angle)
        
        # Calculate rotation and alignment
        # Since we are N=0 and Clockwise:
        # 0-180 (Right side): Text should point outwards (Left aligned)
        # 180-360 (Left side): Text should point inwards (Right aligned)
        
        if 0 <= angle_deg < 180:
            ha = 'left'
            va = 'center'
            rotation = 90 - angle_deg # Convert to standard Cartesian rotation
        else:
            ha = 'right'
            va = 'center'
            rotation = 90 - angle_deg + 180
            
        ax.text(angle, MAX_VAL + 5, label, size=11, 
                horizontalalignment=ha, verticalalignment=va, 
                rotation=rotation, rotation_mode='anchor')

    # 7. Legend
    # Create custom legend handles to match the square/rect shape in the image
    import matplotlib.patches as mpatches
    patch_nsf = mpatches.Patch(color=COLOR_NSF, label='NSF ($n$ = 179)')
    patch_nsfc = mpatches.Patch(color=COLOR_NSFC, label='NSFC ($n$ = 196)')
    
    # Place legend at bottom left
    # We use fig.legend or ax.legend with bbox_to_anchor
    # The image has the legend in the bottom left corner relative to the circle
    plt.legend(handles=[patch_nsf, patch_nsfc], loc='lower left', 
               bbox_to_anchor=(-0.1, -0.1), frameon=False, fontsize=12,
               handlelength=1.0, handleheight=1.0)

    # 8. Title / Tag
    # Add the bold "a" in the top left
    plt.text(-0.1, 1.05, 'a', transform=ax.transAxes, fontsize=24, fontweight='bold', va='top')

    # Adjust layout to prevent clipping of labels
    plt.tight_layout()
    
    # Save
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)