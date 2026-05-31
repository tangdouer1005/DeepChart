import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

def generate_chart(output_filename):
    # 1. Data Preparation
    # We reconstruct the dataframe based on the provided source table.
    # Note: P-values are not in the source table but are visible in the chart image.
    # We manually transcribe the P-values from the image to ensure faithful reproduction.
    
    data = [
        # Potassium
        {'Scenario': 'Red and processed meat (25%)', 'Nutrient': 'Potassium', 'Mean': -0.089396, 'CI': '(-0·091, -0·087)', 'P_text': 'P < 0.0001'},
        {'Scenario': 'Red and processed meat (50%)', 'Nutrient': 'Potassium', 'Mean': -0.186498, 'CI': '(-0·19, -0·18)',   'P_text': 'P < 0.0001'},
        {'Scenario': 'Dairy (25%)',                  'Nutrient': 'Potassium', 'Mean': -0.362246, 'CI': '(-0·37, -0·36)',   'P_text': 'P < 0.0001'},
        {'Scenario': 'Dairy (50%)',                  'Nutrient': 'Potassium', 'Mean': -0.799946, 'CI': '(-0·81, -0·79)',   'P_text': 'P = 0.0001'},
        
        # Iron
        {'Scenario': 'Red and processed meat (25%)', 'Nutrient': 'Iron',      'Mean': -0.136205, 'CI': '(-0·14, -0·13)',    'P_text': 'P = 0.02'},
        {'Scenario': 'Red and processed meat (50%)', 'Nutrient': 'Iron',      'Mean': -0.269597, 'CI': '(-0·274, -0·265)',  'P_text': 'P = 0.01'},
        {'Scenario': 'Dairy (25%)',                  'Nutrient': 'Iron',      'Mean': -0.873633, 'CI': '(-0·88, -0·87)',    'P_text': 'P < 0.0001'},
        {'Scenario': 'Dairy (50%)',                  'Nutrient': 'Iron',      'Mean': -1.49412,  'CI': '(-1·5, -1·48)',     'P_text': 'P < 0.0001'},
        
        # Calcium
        {'Scenario': 'Red and processed meat (25%)', 'Nutrient': 'Calcium',   'Mean': -1.11836,  'CI': '(-1·13, -1·11)',    'P_text': 'P < 0.0001'},
        {'Scenario': 'Red and processed meat (50%)', 'Nutrient': 'Calcium',   'Mean': -2.25949,  'CI': '(-2·28, -2·24)',    'P_text': 'P < 0.0001'},
        {'Scenario': 'Dairy (25%)',                  'Nutrient': 'Calcium',   'Mean': 4.66082,   'CI': '(4·64, 4·69)',      'P_text': 'P < 0.0001'},
        {'Scenario': 'Dairy (50%)',                  'Nutrient': 'Calcium',   'Mean': 9.37513,   'CI': '(9·33, 9·42)',      'P_text': 'P < 0.0001'},
        
        # Vitamin D
        {'Scenario': 'Red and processed meat (25%)', 'Nutrient': 'Vitamin D', 'Mean': 0.119448,  'CI': '(0·116, 0·123)',    'P_text': 'P < 0.0001'},
        {'Scenario': 'Red and processed meat (50%)', 'Nutrient': 'Vitamin D', 'Mean': 0.231836,  'CI': '(0·23, 0·24)',      'P_text': 'P < 0.0001'},
        {'Scenario': 'Dairy (25%)',                  'Nutrient': 'Vitamin D', 'Mean': 0.428505,  'CI': '(0·42, 0·43)',      'P_text': 'P < 0.0001'},
        {'Scenario': 'Dairy (50%)',                  'Nutrient': 'Vitamin D', 'Mean': 0.815726,  'CI': '(0·81, 0·83)',      'P_text': 'P = 0.0001'},
    ]

    df = pd.DataFrame(data)

    # Clean CI strings: replace middle dot '·' with standard dot '.'
    df['CI_clean'] = df['CI'].str.replace('·', '.')

    # Define Colors
    colors = {
        'Red and processed meat (25%)': '#D97C28', # Light Brown/Orange
        'Red and processed meat (50%)': '#8C4B15', # Dark Brown
        'Dairy (25%)': '#5B8CC0',                  # Light Blue
        'Dairy (50%)': '#265586'                   # Dark Blue
    }

    # Define Order
    # Nutrients from bottom to top
    nutrient_order = ['Potassium', 'Iron', 'Calcium', 'Vitamin D']
    
    # Scenarios within a nutrient group (bottom to top visually)
    scenario_order = [
        'Red and processed meat (25%)',
        'Red and processed meat (50%)',
        'Dairy (25%)',
        'Dairy (50%)'
    ]

    # 2. Plotting Setup
    fig, ax = plt.subplots(figsize=(12, 14))
    
    # Define Y-positions
    # We will manually calculate y-coordinates to create groups
    # Group spacing = 1.5 units. Within group spacing = 1 unit.
    
    y_positions = {}
    current_y = 0
    group_centers = {}
    
    # Iterate through nutrients to assign Y coordinates
    for nutrient in nutrient_order:
        group_start = current_y
        nutrient_data = df[df['Nutrient'] == nutrient]
        
        # Iterate through scenarios in the specific order
        for scenario in scenario_order:
            row = nutrient_data[nutrient_data['Scenario'] == scenario].iloc[0]
            y_positions[(nutrient, scenario)] = current_y
            
            # Plot the dot
            ax.scatter(row['Mean'], current_y, color=colors[scenario], s=180, zorder=3)
            
            # Add Annotation Text
            # Logic: If Mean < 0, text to the left. If Mean > 0, text to the right.
            # Text format: "(CI) P_text"
            label_text = f"{row['CI_clean']} {row['P_text']}"
            
            if row['Mean'] < 0:
                ax.text(row['Mean'] - 0.3, current_y, label_text, 
                        va='center', ha='right', fontsize=11, color='black')
            else:
                ax.text(row['Mean'] + 0.3, current_y, label_text, 
                        va='center', ha='left', fontsize=11, color='black')
            
            current_y += 1.2 # Spacing between dots within a group
            
        # Calculate center for the nutrient label
        group_end = current_y - 1.2
        group_centers[nutrient] = (group_start + group_end) / 2
        
        # Add separator line above the group (except for the last one)
        if nutrient != nutrient_order[-1]:
            separator_y = current_y + 0.5
            ax.axhline(y=separator_y, color='#d9d9d9', linewidth=1.5)
            current_y = separator_y + 1.5 # Spacing between groups
        else:
            current_y += 0.5

    # 3. Axis Formatting
    
    # X-axis
    ax.set_xlim(-6, 12)
    ax.set_xlabel('Mean difference from observed diets (%)', fontsize=14, labelpad=15)
    ax.tick_params(axis='x', labelsize=12)
    
    # Vertical dashed line at 0
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=1.5, zorder=1)
    
    # Y-axis (Custom Labels)
    ax.set_yticks(list(group_centers.values()))
    ax.set_yticklabels(list(group_centers.keys()), fontsize=14, ha='left')
    
    # Move Y-tick labels to the far left inside the plot area or align them nicely
    # The chart shows labels aligned left, effectively as a separate column.
    # We can adjust tick params to move them out or use text.
    # Let's use standard y-ticks but adjust alignment.
    ax.tick_params(axis='y', length=0, pad=100) # Push labels left
    
    # Actually, standard y-labels center align by default or right align to the axis.
    # To match the chart exactly (labels far left), let's turn off y-axis and place text manually.
    ax.yaxis.set_visible(False)
    for nutrient, y_pos in group_centers.items():
        ax.text(-6, y_pos, nutrient, fontsize=16, ha='left', va='center')

    # Remove spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('black')
    ax.spines['bottom'].set_linewidth(1)

    # 4. Legend
    # Create custom legend handles
    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], marker='o', color='w', label='Red and processed meat (25%)',
               markerfacecolor=colors['Red and processed meat (25%)'], markersize=12),
        Line2D([0], [0], marker='o', color='w', label='Red and processed meat (50%)',
               markerfacecolor=colors['Red and processed meat (50%)'], markersize=12),
        Line2D([0], [0], marker='o', color='w', label='Dairy (25%)',
               markerfacecolor=colors['Dairy (25%)'], markersize=12),
        Line2D([0], [0], marker='o', color='w', label='Dairy (50%)',
               markerfacecolor=colors['Dairy (50%)'], markersize=12),
    ]
    
    # Place legend at bottom right
    ax.legend(handles=legend_elements, loc='lower right', bbox_to_anchor=(1.0, 0.1), 
              frameon=False, fontsize=14, labelspacing=0.8, handletextpad=0.5)

    # Adjust layout to accommodate labels
    plt.tight_layout()
    
    # Save
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)