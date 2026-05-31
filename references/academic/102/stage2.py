import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def generate_chart(output_filename):
    # ---------------------------------------------------------
    # 1. Data Preparation
    # ---------------------------------------------------------
    # Raw data extracted from the provided source table
    data = {
        'B16-F0': [1.0524294, 0.99642126, 0.95114935],
        'LN7-1134BL': [0.74170805, 0.7873782, 0.75957924],
        'LN8-1194BR': [0.57713831, 0.54398637, 0.56088287],
        'LN9-1315BL': [0.54237196, 0.53865737, 0.50458335],
        'F0Luc, -Cys': [0.03989584, 0.0410516, 0.03855378], # Header in data was "B16-F0 - Cys"
        'LN7-1134BL, -Cys': [0.01544157, 0.0159137, 0.01655506],
        'LN8-1194BR, -Cys': [0.01384739, 0.01401451, 0.01451768],
        'LN9-1315BL, -Cys': [0.01376061, 0.01339609, 0.01397419]
    }

    # Convert to DataFrame for easier handling
    df = pd.DataFrame(data)
    
    # Calculate Means and Standard Deviations
    means = df.mean()
    stds = df.std()
    
    # X-axis labels matching the chart image
    labels = [
        'B16-F0', 'LN7-1134BL', 'LN8-1194BR', 'LN9-1315BL',
        'F0Luc, -Cys', 'LN7-1134BL, -Cys', 'LN8-1194BR, -Cys', 'LN9-1315BL, -Cys'
    ]
    
    # ---------------------------------------------------------
    # 2. Plot Setup
    # ---------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 6), dpi=150)
    
    # Colors
    # Grey for controls, Green for treatments
    bar_colors = [
        '#D9D9D9', # Grey
        '#78C679', # Green
        '#78C679', 
        '#78C679',
        '#D9D9D9', # Grey
        '#78C679', 
        '#78C679', 
        '#78C679'
    ]
    
    edge_colors = ['black'] * 8
    
    # Scatter point colors: Black for grey bars, Darker Green for green bars
    scatter_colors = [
        'black', 
        '#2E7D32', 
        '#2E7D32', 
        '#2E7D32', 
        'black', 
        '#2E7D32', 
        '#2E7D32', 
        '#2E7D32'
    ]

    x_pos = np.arange(len(labels))
    
    # ---------------------------------------------------------
    # 3. Drawing Bars and Points
    # ---------------------------------------------------------
    # Draw Bars
    bars = ax.bar(x_pos, means, yerr=stds, align='center', 
                  color=bar_colors, edgecolor='black', linewidth=0.8, 
                  capsize=5, width=0.6, error_kw={'elinewidth': 1, 'markeredgewidth': 1})

    # Draw Scatter Points
    for i, col in enumerate(df.columns):
        y_vals = df[col].values
        x_vals = np.full(len(y_vals), x_pos[i])
        ax.scatter(x_vals, y_vals, color=scatter_colors[i], s=25, zorder=5, edgecolors='none')

    # ---------------------------------------------------------
    # 4. Significance Annotations
    # ---------------------------------------------------------
    # Helper function to draw significance brackets
    def draw_significance(x1, x2, y_line, text, y_text_offset=0.02):
        # Draw the bracket line
        # Legs of the bracket
        leg_height = 0.02
        ax.plot([x1, x1, x2, x2], [y_line - leg_height, y_line, y_line, y_line - leg_height], 
                lw=0.8, c='black')
        
        # Add text
        ax.text((x1 + x2) * 0.5, y_line + y_text_offset, text, 
                ha='center', va='bottom', color='black', fontsize=9)

    # Group 1 (Left side)
    # B16-F0 vs LN7 (Index 0 vs 1)
    draw_significance(0, 1, 1.15, r'$P = 3.6 \times 10^{-5}$')
    # B16-F0 vs LN8 (Index 0 vs 2)
    draw_significance(0, 2, 1.30, r'$P = 3.2 \times 10^{-7}$')
    # B16-F0 vs LN9 (Index 0 vs 3)
    draw_significance(0, 3, 1.45, r'$P = 1.8 \times 10^{-7}$')

    # Group 2 (Right side)
    # F0Luc vs LN7-Cys (Index 4 vs 5)
    draw_significance(4, 5, 0.25, r'$P = 4.1 \times 10^{-10}$')
    # F0Luc vs LN8-Cys (Index 4 vs 6)
    draw_significance(4, 6, 0.38, r'$P = 2.2 \times 10^{-10}$')
    # F0Luc vs LN9-Cys (Index 4 vs 7)
    draw_significance(4, 7, 0.52, r'$P = 2 \times 10^{-10}$')

    # ---------------------------------------------------------
    # 5. Styling and Layout
    # ---------------------------------------------------------
    # Axis Labels
    ax.set_ylabel('Relative GSH levels', fontsize=12, labelpad=10)
    
    # X-Axis Ticks
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=10)
    
    # Y-Axis Limits
    ax.set_ylim(0, 1.6)
    ax.set_yticks([0, 0.5, 1.0, 1.5])
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add Figure Label "j"
    ax.text(-0.15, 1.0, 'j', transform=ax.transAxes, 
            fontsize=20, fontweight='bold', va='top', ha='right')

    # Adjust layout to prevent clipping of rotated labels
    plt.tight_layout()
    
    # Save output
    plt.savefig(output_filename, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    generate_chart(output_file)