import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def generate_chart(output_filename):
    # 1. Source Data
    csv_data = """Unnamed: 0,central estimate,low,high
MSW-SAF,102.7,33.1,197
MSW-H2,170.7,69.4,306.6
MSW-PTL,177,81.7,395.3"""

    df = pd.read_csv(io.StringIO(csv_data))

    # 2. Setup Plot
    # Figure size chosen to match the vertical aspect ratio of the original image
    fig, ax = plt.subplots(figsize=(4.5, 6))
    
    # Set background to white
    fig.patch.set_facecolor('white')
    ax.set_facecolor('white')

    # 3. Define Styles
    # Colors approximated from the image
    colors = {
        'MSW-SAF': '#46636E',  # Slate Blue/Grey
        'MSW-H2': '#D6A659',   # Mustard/Gold
        'MSW-PTL': '#8B3A3A'   # Dark Red/Brown
    }
    error_bar_color = '#421C1C' # Very dark brown/black for error bars
    
    # Marker size
    marker_size = 700

    # 4. Plotting Loop
    # We iterate to handle specific styling per category
    categories = df['Unnamed: 0'].tolist()
    x_positions = range(len(categories))

    for i, category in enumerate(categories):
        row = df[df['Unnamed: 0'] == category].iloc[0]
        
        central = row['central estimate']
        low = row['low']
        high = row['high']
        
        # Calculate error relative to central point for matplotlib
        yerr_low = central - low
        yerr_high = high - central
        
        # Draw Error Bar
        # zorder=1 ensures lines are behind the text but we want them visible. 
        # In the image, the dot is on top of the line.
        ax.errorbar(
            x=i, 
            y=central, 
            yerr=[[yerr_low], [yerr_high]], 
            fmt='none', 
            ecolor=error_bar_color, 
            elinewidth=1.5, 
            capsize=5, 
            capthick=1.5,
            zorder=1
        )
        
        # Draw Central Marker
        ax.scatter(
            x=i, 
            y=central, 
            s=marker_size, 
            color=colors[category], 
            zorder=2,
            edgecolor='none'
        )
        
        # Add Text Label
        # Labels are placed above the dots. 
        # MSW-H2 needs subscript formatting.
        label_text = category
        if "H2" in label_text:
            label_text = "MSW-H$_2$"
            
        # Offset text slightly above the marker. 
        # Visual estimation: text is roughly 30-40 units above the center.
        text_y_offset = 40 
        
        ax.text(
            x=i, 
            y=central + text_y_offset, 
            s=label_text, 
            color=colors[category], 
            ha='center', 
            va='center', 
            fontsize=14,
            fontfamily='sans-serif',
            zorder=3,
            # Add a small white outline to text to separate it from the error bar if they overlap
            path_effects=[
                import_patheffects().withStroke(linewidth=2, foreground='white')
            ]
        )

    # 5. Axis Formatting
    
    # Y-Axis
    ax.set_ylim(0, 450)
    ax.set_yticks(range(0, 451, 50))
    ax.tick_params(axis='y', labelsize=12, direction='in', length=4)
    
    # Y-Axis Label
    # Using LaTeX for subscripts and superscripts
    ax.set_ylabel(
        "GHG mitigation potential per ton\nMSW (kgCO$_2$e t$^{-1}$)", 
        fontsize=14, 
        labelpad=10,
        color='black'
    )

    # X-Axis
    # Remove x-axis ticks and labels as they are handled by the text annotations
    ax.set_xticks([])
    ax.set_xlim(-0.5, 2.5)

    # 6. Final Touches
    # Add the bold 'b' label in the top left corner outside the plot
    ax.text(
        -0.2, 1.0, 
        'b', 
        transform=ax.transAxes, 
        fontsize=24, 
        fontweight='bold', 
        va='top', 
        ha='right',
        color='black'
    )

    # Adjust layout to prevent clipping of the 'b' label and y-axis label
    plt.tight_layout()
    
    # Save
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

def import_patheffects():
    import matplotlib.patheffects as path_effects
    return path_effects

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    generate_chart(output_file)