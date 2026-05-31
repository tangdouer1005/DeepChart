import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import io

def generate_chart(output_filename='output.png'):
    # 1. Source Data Loading
    # Using the exact data provided in the prompt
    csv_data = """Unnamed: 0|GHG emission intensity,gCO2e/MJ
MSW transport|2.2
Pre-treatment+Gasification|24
Water gas shift reaction|-13.6
Rectisol Process|92.6
Fischer Tropsch|5.7
Hydrotreating|0.4
Hydrocracking|0.5
Others|9.8
Fuel transport|0.4
Operation|73.2
Biogenic content|-176.7
Credit|-4.3"""

    # Read data
    df = pd.read_csv(io.StringIO(csv_data), sep="|")
    
    # Clean column names and data
    df.columns = [c.strip() for c in df.columns]
    df.rename(columns={df.columns[0]: 'Category', df.columns[1]: 'Value'}, inplace=True)
    df['Category'] = df['Category'].str.strip()
    
    # 2. Configuration for Visual Replication
    # Colors extracted to match the image as closely as possible
    colors = [
        '#5F8D9B', # MSW transport (Teal/Grey)
        '#D1E5EB', # Pre-treatment (Light Blue)
        '#7FA4C0', # Water gas shift (Medium Blue)
        '#1F548A', # Rectisol Process (Dark Blue)
        '#757575', # Fischer Tropsch (Dark Grey)
        '#C0C0C0', # Hydrotreating (Light Grey)
        '#C0C0C0', # Hydrocracking (Light Grey)
        '#757575', # Others (Dark Grey)
        '#333333', # Fuel transport (Black/Dark Grey)
        '#EBC084', # Operation (Tan/Gold)
        '#C65D48', # Biogenic content (Terracotta/Red)
        '#5F8D9B'  # Credit (Teal/Grey)
    ]

    # Text colors for category labels (matching image style)
    text_colors = [
        '#5F8D9B', # MSW
        '#B0D0D9', # Pre-treatment (Light Blue text)
        '#7FA4C0', # Water gas
        '#1F548A', # Rectisol
        '#BDBDBD', # Fischer (Light Grey text)
        '#BDBDBD', # HydroT
        '#BDBDBD', # HydroC
        '#BDBDBD', # Others
        '#5F8D9B', # Fuel
        '#EBC084', # Operation (Gold text)
        '#FFFFFF', # Biogenic (White text)
        '#5F8D9B'  # Credit
    ]

    # 3. Plotting Setup
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Set font globally to sans-serif to match image
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']

    # Waterfall Logic
    running_total = 0
    x_positions = np.arange(len(df))
    bar_width = 0.96  # Slight gap to show separation, though image bars touch closely

    for i, (idx, row) in enumerate(df.iterrows()):
        val = row['Value']
        cat = row['Category']
        
        # Determine bar geometry
        if val >= 0:
            bottom = running_total
            height = val
            label_y = running_total + val + 3 # Position for value label
            cat_y_base = running_total + val # Base for category label
        else:
            bottom = running_total + val # Matplotlib draws up from bottom, so for neg we start lower
            # Actually, simpler to use bottom=running_total and height=val (which is neg)
            # But to control edges better, let's stick to positive heights for drawing logic if possible,
            # or just let matplotlib handle negative height.
            # Matplotlib: bar(x, height=-10, bottom=100) draws from 100 down to 90.
            bottom = running_total
            height = val
            label_y = running_total + val - 8 # Position for value label (below)
            cat_y_base = running_total # Base for category label (top of bar)

        # Plot Bar
        ax.bar(x_positions[i], height, bottom=bottom, width=bar_width, 
               color=colors[i], edgecolor='gray', linewidth=0.5)

        # 4. Labels and Annotations
        
        # Value Label (Bold Black Number)
        # Format: 1 decimal place
        val_str = f"{val:.1f}"
        # Adjust vertical alignment based on positive/negative
        va = 'bottom' if val >= 0 else 'top'
        ax.text(x_positions[i], label_y, val_str, 
                ha='center', va=va, 
                fontsize=16, fontweight='bold', color='black')

        # Category Label (Vertical Colored Text)
        # Logic: "Operation" and "Biogenic content" are inside the bar. Others are above.
        # "Rectisol" is above.
        
        is_inside = cat in ['Operation', 'Biogenic content']
        
        if is_inside:
            # Place inside the bar, near the top
            # For Operation (pos): top is running_total + val
            # For Biogenic (neg): top is running_total
            if val >= 0:
                text_y = running_total + val - 5
            else:
                text_y = running_total - 5
            
            ax.text(x_positions[i], text_y, cat, 
                    rotation=90, ha='center', va='top', 
                    fontsize=14, color=text_colors[i])
        else:
            # Place outside/above the bar
            # Calculate visual top of the stack at this point
            visual_top = max(running_total, running_total + val)
            
            # Special handling for "Pre-treatment+Gasification" to match image formatting
            display_text = cat
            if "Pre-treatment" in cat:
                display_text = "Pretreatment + gasification" # Matching image casing/spacing
            elif "Rectisol" in cat:
                display_text = "Rectisol process" # Lowercase 'p' in image
            elif "Water gas" in cat:
                display_text = "Water gas shift reaction"
            
            # Offset slightly above the value label or the bar
            offset = 15 if val >= 0 else 5 # Give space for the number if positive
            if val < 0: offset = 5 # If negative bar, text sits on previous baseline
            
            # Specific tweaks for visual alignment with image
            if i == 0: offset = 10 # MSW
            if i == 1: offset = 10 # Pre-treat
            if i == 2: offset = 5  # Water gas (bar goes down, text sits on top line)
            if i == 3: offset = 10 # Rectisol
            
            ax.text(x_positions[i], visual_top + offset, display_text, 
                    rotation=90, ha='center', va='bottom', 
                    fontsize=14, color=text_colors[i])

        # Update running total
        running_total += val

    # 5. Axis and Layout Styling
    
    # Y-Axis
    ax.set_ylabel('GHG emission intensity breakdown\n(gCO$_2$e MJ$^{-1}$)', fontsize=16, color='black')
    ax.set_ylim(0, 250)
    ax.tick_params(axis='y', labelsize=12, length=4, color='black')
    
    # X-Axis
    ax.set_xticks([]) # Remove x ticks
    ax.set_xlim(-0.8, len(df) - 0.2)
    
    # Add a baseline at 0
    ax.axhline(0, color='black', linewidth=1)

    # Add the "a" tag in the top left
    ax.text(-0.8, 250, 'a', fontsize=24, fontweight='bold', va='top', ha='left')

    # Remove top and right spines for cleaner look (optional, but matches scientific style often)
    # Image has a box, so we keep spines but make them thin
    for spine in ax.spines.values():
        spine.set_linewidth(0.8)
        spine.set_color('gray')

    plt.tight_layout()
    
    # Save output
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)