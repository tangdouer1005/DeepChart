import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_chart(output_filename):
    # 1. Load Source Data
    csv_data = """Unnamed: 0,Unnamed: 1,central estimate,low,high
MSW-SAF,MSW management,14.1,8.1,30.1
nan,SAF production,nan,8.6,33.5
nan,Energy and Others,nan,10.4,24.7
nan,nan,nan,nan,nan
MSW-H2,MSW management,7.3,3.2,17.3
nan,SAF production,nan,3.6,20.3
nan,Energy and Others,nan,5.1,11.5
nan,nan,nan,nan,nan
MSW-PTL,MSW management,25.4,23.4,30.3
nan,SAF production,nan,23.6,31.8
nan,Energy and Others,nan,7.6,30.8"""

    # Read data
    df = pd.read_csv(io.StringIO(csv_data))
    
    # Clean Data
    # Forward fill the group column (Unnamed: 0)
    df['Unnamed: 0'] = df['Unnamed: 0'].fillna(method='ffill')
    # Drop rows where 'low' or 'high' is NaN (the spacer rows in the source)
    df = df.dropna(subset=['low', 'high'])
    
    # Rename columns for clarity
    df.columns = ['Group', 'Subcategory', 'Central', 'Low', 'High']

    # 2. Setup Plot
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    # Define Colors (approximated from image)
    colors = {
        'MSW-SAF': '#405E68',  # Dark Slate Blue/Grey
        'MSW-H2':  # Golden/Mustard
                   '#DFA855', 
        'MSW-PTL': '#8F3B38'   # Dark Red/Brown
    }
    
    # Define Layout Parameters
    bar_width = 0.65
    group_spacing = 1.5  # Space between groups
    intra_group_spacing = 1.0 # Space between bars within a group
    
    # Get unique groups preserving order
    groups = df['Group'].unique()
    
    current_x = 0
    
    # Iterate through groups to plot
    for group_name in groups:
        group_data = df[df['Group'] == group_name].reset_index(drop=True)
        color = colors.get(group_name, 'grey')
        
        # Calculate x positions for this group
        x_positions = [current_x + (i * intra_group_spacing) for i in range(len(group_data))]
        
        # 1. Draw Bars (Floating bars: bottom=Low, height=High-Low)
        ax.bar(
            x_positions, 
            height=group_data['High'] - group_data['Low'], 
            bottom=group_data['Low'], 
            width=bar_width, 
            color=color,
            edgecolor='none'
        )
        
        # 2. Draw Central Estimate Line (Dashed)
        # The central estimate is usually in the first row of the group in the source data
        central_val = group_data.iloc[0]['Central']
        if pd.notna(central_val):
            # Line spans the width of the group
            x_start_line = x_positions[0] - (bar_width/2) - 0.1
            x_end_line = x_positions[-1] + (bar_width/2) + 0.1
            
            ax.hlines(y=central_val, xmin=x_start_line, xmax=x_end_line, 
                      colors=color, linestyles='--', linewidth=1.5, alpha=0.8)
            
            # Add value label to the right of the line
            ax.text(x_end_line + 0.2, central_val + 0.5, f"{central_val}", 
                    color=color, fontsize=12, va='bottom', ha='left')

        # 3. Add Group Label at the top
        # Center of the group
        group_center = sum(x_positions) / len(x_positions)
        ax.text(group_center, 38, group_name.replace('H2', 'H$_2$'), 
                color=color, fontsize=14, ha='center', va='top')

        # 4. Add Vertical Subcategory Labels (Only for the middle group MSW-H2 based on image)
        if group_name == 'MSW-H2':
            for i, row in group_data.iterrows():
                label_text = row['Subcategory']
                # Fix capitalization to match chart image exactly
                if "Energy" in label_text:
                    label_text = "Energy and others"
                
                # Position text above the bar, rotated 90 degrees
                ax.text(x_positions[i], row['High'] + 1.0, label_text, 
                        rotation=90, ha='center', va='bottom', 
                        color=color, fontsize=12, alpha=0.9)

        # Update x cursor for next group
        current_x = x_positions[-1] + group_spacing + 1

    # 3. Axis Styling
    
    # Y Axis
    ax.set_ylim(0, 40)
    ax.set_ylabel('GHG emission intensity\nvariation (gCO$_2$e MJ$^{-1}$)', fontsize=14, color='black')
    ax.tick_params(axis='y', labelsize=12, length=4, color='black')
    
    # X Axis
    ax.set_xticks([]) # Hide x ticks
    ax.set_xlim(-1, current_x - group_spacing) # Adjust limits to center content
    
    # Remove top and right spines for cleaner look (optional, but matches scientific style often)
    # The provided image has a box, so we keep spines but make them thin/black
    for spine in ax.spines.values():
        spine.set_edgecolor('black')
        spine.set_linewidth(0.8)

    # 4. Add Figure Label 'a'
    ax.text(-0.08, 1.02, 'a', transform=ax.transAxes, 
            fontsize=20, fontweight='bold', color='black', va='top', ha='left')

    # Save output
    plt.tight_layout()
    plt.savefig(output_filename, bbox_inches='tight', dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    generate_chart(output_file)