import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import io
import numpy as np

def generate_chart(output_filename):
    # 1. Source Data
    # Note: P-values are not in the provided table but are visible in the image.
    # They are manually added here to ensure visual replication.
    csv_data = """Scenario|Nutrient|Mean difference from observed (%)|95% CI
Red and processed meat (25%)|Free sugars|-0.588834|(-0·56, -0·62)
Red and processed meat (50%)|Free sugars|-0.867064|(-0·83, -0·91)
Dairy (25%)|Free sugars|0.211354|(0·2, 0·22)
Dairy (50%)|Free sugars|0.640388|(0·61, 0·67)
Red and processed meat (25%)|Saturated fat|-0.838248|(-0·8, -0·88)
Red and processed meat (50%)|Saturated fat|-4.70775|(-4·5, -4·92)
Dairy (25%)|Saturated fat|-13.4857|(-12·88, -14·09)
Dairy (50%)|Saturated fat|-33.3778|(-31·89, -34·87)
Red and processed meat (25%)|Sodium|-1.51633|(-1·45, -1·58)
Red and processed meat (50%)|Sodium|-3.18769|(-3·05, -3·33)
Dairy (25%)|Sodium|-1.4256|(-1·36, -1·49)
Dairy (50%)|Sodium|-2.9479|(-2·82, -3·08)
"""
    
    # Load data
    df = pd.read_csv(io.StringIO(csv_data), sep="|")
    
    # Clean data: Remove NaNs if any (though the string above is clean, the prompt had empty rows)
    df = df.dropna(how='all')
    
    # Clean CI column: replace middle dot with decimal point
    df['95% CI'] = df['95% CI'].str.replace('·', '.')

    # Map P-values based on the image content (Visual Replication)
    # Key: (Nutrient, Scenario) -> P-value string
    p_values = {
        ('Free sugars', 'Red and processed meat (25%)'): 'P < 0.0001',
        ('Free sugars', 'Red and processed meat (50%)'): 'P < 0.0001',
        ('Free sugars', 'Dairy (25%)'): 'P = 0.08',
        ('Free sugars', 'Dairy (50%)'): 'P = 0.008',
        ('Saturated fat', 'Red and processed meat (25%)'): 'P < 0.0001',
        ('Saturated fat', 'Red and processed meat (50%)'): 'P < 0.0001',
        ('Saturated fat', 'Dairy (25%)'): 'P < 0.0001',
        ('Saturated fat', 'Dairy (50%)'): 'P < 0.0001',
        ('Sodium', 'Red and processed meat (25%)'): 'P < 0.0001',
        ('Sodium', 'Red and processed meat (50%)'): 'P < 0.0001',
        ('Sodium', 'Dairy (25%)'): 'P < 0.0001',
        ('Sodium', 'Dairy (50%)'): 'P < 0.0001',
    }

    # Define Colors
    colors = {
        'Red and processed meat (25%)': '#D37228',  # Orange/Brown
        'Red and processed meat (50%)': '#8B4513',  # Dark Brown
        'Dairy (25%)': '#4A86BC',                   # Medium Blue
        'Dairy (50%)': '#205283'                    # Dark Blue
    }

    # Define Order
    # Nutrients from bottom to top
    nutrient_order = ['Free sugars', 'Saturated fat', 'Sodium']
    
    # Scenarios within nutrient (bottom to top visually in the chart)
    # In the chart: Meat 25 (bottom), Meat 50, Dairy 25, Dairy 50 (top)
    scenario_order = [
        'Red and processed meat (25%)',
        'Red and processed meat (50%)',
        'Dairy (25%)',
        'Dairy (50%)'
    ]

    # Setup Plot
    fig, ax = plt.subplots(figsize=(12, 15))
    
    # Plotting Logic
    y_base = 0
    y_ticks = []
    y_tick_labels = []
    
    # Group spacing
    group_gap = 2.5
    
    # Iterate through nutrients
    for nutrient in nutrient_order:
        subset = df[df['Nutrient'] == nutrient]
        
        # Calculate center for y-label
        group_y_start = y_base
        
        for i, scenario in enumerate(scenario_order):
            row = subset[subset['Scenario'] == scenario]
            if row.empty:
                continue
            
            mean_val = row['Mean difference from observed (%)'].values[0]
            ci_text = row['95% CI'].values[0]
            p_val = p_values.get((nutrient, scenario), "")
            
            # Current Y position
            y_pos = y_base + i
            
            # Color
            color = colors[scenario]
            
            # Plot Dot
            ax.scatter(mean_val, y_pos, color=color, s=180, zorder=3)
            
            # Add Annotation Text
            # Logic: Generally to the left. If value is very negative (outlier), to the right.
            label_text = f"{ci_text} {p_val}"
            
            if mean_val < -30: # Specific case for Saturated Fat Dairy 50%
                ax.text(mean_val + 1, y_pos, label_text, 
                        va='center', ha='left', fontsize=14, color='black')
            else:
                ax.text(mean_val - 0.8, y_pos, label_text, 
                        va='center', ha='right', fontsize=14, color='black')

        # Add Y-axis label for the group
        # Center of the group (0, 1, 2, 3) -> 1.5
        y_center = y_base + 1.5
        ax.text(-38, y_center, nutrient, fontsize=16, va='center', ha='left')
        
        # Add separator line above the group (except for the last one)
        if nutrient != nutrient_order[-1]:
            line_y = y_base + 4 + (group_gap / 2) - 0.5 # Approximate midpoint
            ax.axhline(y=line_y, color='#D3D3D3', linewidth=1.5)
        
        # Increment base for next group
        y_base += 4 + group_gap

    # Vertical dashed line at 0
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=2, zorder=1)

    # X-axis settings
    ax.set_xlim(-35, 5)
    ax.set_xlabel("Mean difference from observed diets (%)", fontsize=16, labelpad=15)
    ax.tick_params(axis='x', labelsize=14)
    
    # Y-axis settings
    ax.set_ylim(-1, y_base - group_gap + 1)
    ax.set_yticks([]) # Hide default y ticks
    
    # Spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_linewidth(1.2)

    # Legend
    # Create custom handles
    legend_handles = []
    # Reverse order for legend to match the visual stack in the legend area of the image
    # Image legend order (top to bottom): Meat 25, Meat 50, Dairy 25, Dairy 50
    legend_order = [
        'Red and processed meat (25%)',
        'Red and processed meat (50%)',
        'Dairy (25%)',
        'Dairy (50%)'
    ]
    
    for scenario in legend_order:
        handle = mlines.Line2D([], [], color=colors[scenario], marker='o', linestyle='None',
                              markersize=12, label=scenario)
        legend_handles.append(handle)

    # Position legend inside the plot, bottom left area (near Free sugars)
    # Coordinates are relative to data or axes. Using data coords roughly.
    # Free sugars starts at y=0. Legend is roughly at x=-25, y=0 to 3.
    leg = ax.legend(handles=legend_handles, loc='lower left', 
                    bbox_to_anchor=(0.18, 0.08), # Fine-tuned position
                    frameon=False, fontsize=14, handletextpad=0.5, labelspacing=0.8)

    plt.tight_layout()
    
    # Save output
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    generate_chart(output_file)