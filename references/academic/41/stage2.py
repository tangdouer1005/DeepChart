import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
import numpy as np
import sys

def generate_chart(output_filename):
    # ---------------------------------------------------------
    # 1. Data Preparation
    # ---------------------------------------------------------
    # Raw data transcribed exactly from the provided source table.
    # Values are fractions, will be converted to % later.
    
    data = {
        'Current_Density': [200, 200, 200, 400, 400, 400, 600, 600, 600] * 2, # Repeated for AEM and Separator
        'Replicate': [1, 2, 3] * 6,
        'Configuration': ['AEM']*9 + ['Separator']*9,
        
        # H2 Values
        'H2': [
            # AEM (200, 400, 600)
            0.0005102, 0.0004747, 0.0002913, # 200
            0.0004292, 0.0003801, 0.0001648, # 400
            0.0002917, 0.0003309, 0.0001181, # 600
            # Separator (200, 400, 600)
            0.0007523, 0.0009948, 0.00078201, # 200
            0.0006943, 0.0007962, 0.00060853, # 400
            0.0004785, 0.0005823, 0.0004726   # 600
        ],
        
        # C2H4 Values
        'C2H4': [
            # AEM
            0.0003829, 0.0002889, 0.0002951, # 200
            0.0004542, 0.0003147, 0.0003559, # 400
            0.0002639, 0.0001960, 0.0002229, # 600
            # Separator
            0.00024107, 0.0002489, 0.0002301, # 200
            0.0002284,  0.0002373, 0.0002208, # 400
            0.0001712,  0.0001792, 0.0001823  # 600
        ],
        
        # CO Values
        'CO': [
            # AEM
            0.0010257, 0.0008115, 0.0012724, # 200
            0.0007593, 0.0006018, 0.0008532, # 400
            0.0005042, 0.0004595, 0.0005854, # 600
            # Separator
            0.0009924, 0.0006823, 0.0009586, # 200
            0.0008031, 0.0005694, 0.0006918, # 400
            0.0006532, 0.0004572, 0.0005008  # 600
        ]
    }

    df = pd.DataFrame(data)

    # Convert fractions to percentages (multiply by 100)
    cols_to_scale = ['H2', 'C2H4', 'CO']
    df[cols_to_scale] = df[cols_to_scale] * 100

    # Calculate Mean and Std Dev for each group
    grouped = df.groupby(['Current_Density', 'Configuration'])[cols_to_scale].agg(['mean', 'std'])
    
    # Flatten MultiIndex columns
    grouped.columns = ['_'.join(col) for col in grouped.columns]
    grouped = grouped.reset_index()

    # ---------------------------------------------------------
    # 2. Plotting Setup
    # ---------------------------------------------------------
    
    # Define Colors (matching the image)
    colors = {
        'H2': '#aebcd1',    # Light Periwinkle
        'C2H4': '#6b84b5',  # Medium Blue/Slate
        'CO': '#cccccc'     # Light Grey
    }
    
    # Define Layout
    fig, ax = plt.subplots(figsize=(6, 5))
    
    # Bar settings
    bar_width = 0.25
    x_labels = [200, 400, 600]
    x_pos = np.arange(len(x_labels))
    
    # Order of stacking: H2 (bottom), C2H4 (middle), CO (top)
    stack_order = ['H2', 'C2H4', 'CO']
    
    # ---------------------------------------------------------
    # 3. Drawing the Bars
    # ---------------------------------------------------------
    
    configs = ['AEM', 'Separator']
    offsets = [-bar_width/2 - 0.02, bar_width/2 + 0.02] # Slight gap between groups
    
    for i, config in enumerate(configs):
        # Filter data for this config
        subset = grouped[grouped['Configuration'] == config].set_index('Current_Density')
        subset = subset.reindex(x_labels) # Ensure order
        
        # Calculate positions
        positions = x_pos + offsets[i]
        
        # Initialize bottom accumulator for stacking
        bottoms = np.zeros(len(x_labels))
        
        for gas in stack_order:
            means = subset[f'{gas}_mean'].values
            stds = subset[f'{gas}_std'].values
            
            # Determine styling based on config
            hatch_pattern = '////' if config == 'Separator' else None
            edge_color = 'white' if config == 'Separator' else None
            # For hatched bars in matplotlib, to get white lines on color, 
            # we usually set edgecolor='white'.
            
            # Plot Bar
            bars = ax.bar(
                positions, 
                means, 
                bar_width, 
                bottom=bottoms, 
                color=colors[gas], 
                hatch=hatch_pattern,
                edgecolor=edge_color,
                linewidth=0.5,
                label=gas if i == 0 else "" # Avoid duplicate labels
            )
            
            # If using white hatch, the border disappears. We might want a thin border back?
            # The image shows very faint borders for Separator. 
            # Let's leave it as is or add a very thin grey edge if needed.
            # To match image perfectly, Separator bars have white stripes.
            
            # Plot Error Bars
            # Error bars are centered at the top of the current segment (bottoms + means)
            # They represent the SD of the specific gas component.
            ax.errorbar(
                positions, 
                bottoms + means, 
                yerr=stds, 
                fmt='none', 
                ecolor='black', 
                capsize=3, 
                elinewidth=1,
                capthick=1,
                alpha=0.8
            )
            
            # Update bottoms for next stack
            bottoms += means

    # ---------------------------------------------------------
    # 4. Styling and Formatting
    # ---------------------------------------------------------
    
    # Axis Labels
    ax.set_ylabel('Anode gas composition (%)', fontsize=14, color='black')
    ax.set_xlabel('Current density (mA cm$^{-2}$)', fontsize=14, color='black')
    
    # Ticks
    ax.set_xticks(x_pos)
    ax.set_xticklabels(x_labels, fontsize=12)
    ax.set_ylim(0, 0.3)
    ax.set_yticks([0.0, 0.1, 0.2, 0.3])
    ax.tick_params(axis='y', labelsize=12)
    
    # Remove top and right spines for cleaner look (optional, but matches scientific style)
    # Image has a box, so we keep spines.
    
    # ---------------------------------------------------------
    # 5. Custom Legend
    # ---------------------------------------------------------
    # The legend in the image is split: Gas types (colors) and Config types (patterns)
    
    # Create proxy artists
    legend_handles = []
    
    # Row 1: Gases
    legend_handles.append(mpatches.Patch(color=colors['H2'], label='H$_2$'))
    legend_handles.append(mpatches.Patch(color=colors['C2H4'], label='C$_2$H$_4$'))
    legend_handles.append(mpatches.Patch(color=colors['CO'], label='CO'))
    
    # Row 2: Configs
    # AEM: Solid color (using a neutral grey-blue to represent the style)
    legend_handles.append(mpatches.Patch(facecolor='#aebcd1', label='AEM')) 
    # Separator: Hatched
    legend_handles.append(mpatches.Patch(facecolor='#aebcd1', hatch='////', edgecolor='white', label='Separator'))
    
    # Create the legend
    # ncol=3 to match the layout roughly (3 items top, 2 items bottom is tricky with standard legend)
    # We will use ncol=3. The empty slot will just be empty.
    # Actually, the image has:
    # H2   C2H4   CO
    # AEM  Separator
    
    # To achieve exact alignment, we can use two legends or a specific list order with ncol=3
    # List: [H2, C2H4, CO, AEM, Separator, Empty]
    
    # Let's try a single legend with ncol=3
    leg = ax.legend(
        handles=legend_handles, 
        loc='upper right', 
        ncol=3, 
        frameon=False, 
        columnspacing=1.0,
        handletextpad=0.4,
        fontsize=11
    )
    
    # ---------------------------------------------------------
    # 6. Final Touches
    # ---------------------------------------------------------
    
    # Add "f" tag in top left
    ax.text(-0.12, 1.02, 'f', transform=ax.transAxes, fontsize=20, fontweight='bold', va='bottom', ha='right')

    plt.tight_layout()
    
    # Save output
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    generate_chart(output_file)