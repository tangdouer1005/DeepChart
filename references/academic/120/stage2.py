import matplotlib.pyplot as plt
import numpy as np
import sys
from matplotlib.patches import Rectangle

def generate_chart(output_path):
    # ---------------------------------------------------------
    # 1. Source Data
    # ---------------------------------------------------------
    # Data extracted faithfully from the provided Markdown table.
    
    # Group: Primary Tumors (Gray)
    # Columns: GCLC (x), GPX4 (y)
    pt_gclc = [
        0.0558, 0.0758, 0.0426, 0.038, 0.1027, 0.0, 0.03, 0.0593, 0.0, 0.049, 
        0.0086, 0.0157, 0.0194, 0.0259, 0.0072, 0.0889, 0.0764, 0.0438, 0.0, 
        0.0, 0.0264, 0.0668, 0.0443, 0.0272, 0.0806
    ]
    pt_gpx4 = [
        0.06784, 0.0908, 0.0579, 0.0372, 0.1016, 0.0, 0.0271, 0.0918, 0.0, 0.0, 
        0.0462, 0.0296, 0.0508, 0.0577, 0.0206, 0.1052, 0.0421, 0.0481, 0.0458, 
        0.0268, 0.0837, 0.0445, 0.0547, 0.0391, 0.0763
    ]

    # Group: LN Metastasis (Green)
    # Columns: GCLC (x), GPX4 (y)
    ln_gclc = [
        0.0562, 0.0135, 0.0133, 0.0095, 0.0095, 0.0, 0.0221, 0.0398, 0.0461, 0.0, 
        0.0123, 0.0, 0.0882, 0.0279, 0.0408, 0.0944, 0.0039, 0.001, 0.082, 0.0, 
        0.0146, 0.0
    ]
    ln_gpx4 = [
        0.0897, 0.0488, 0.0082, 0.0635, 0.0197, 0.0041, 0.0757, 0.0758, 0.0702, 
        0.0735, 0.0378, 0.0, 0.0794, 0.1062, 0.0652, 0.086, 0.0657, 0.0837, 
        0.1191, 0.0317, 0.0584, 0.0662
    ]

    # ---------------------------------------------------------
    # 2. Setup and Styling
    # ---------------------------------------------------------
    # Define colors based on the image
    color_pt = '#888888'  # Gray for Primary Tumors
    color_ln = '#55a630'  # Green for LN Metastasis (approximate match)
    
    fig, ax = plt.subplots(figsize=(6, 5))
    
    # Set font properties globally for consistency
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']

    # ---------------------------------------------------------
    # 3. Plotting Data and Regression Lines
    # ---------------------------------------------------------
    
    # Helper function to plot scatter and regression
    def plot_group(x, y, color, label):
        # Scatter plot: Open circles (facecolor='none')
        ax.scatter(x, y, facecolors='none', edgecolors=color, s=60, linewidth=1.2, label=label, zorder=2)
        
        # Linear Regression
        x_arr = np.array(x)
        y_arr = np.array(y)
        m, b = np.polyfit(x_arr, y_arr, 1)
        
        # Create line points spanning the data range
        x_line = np.linspace(min(x_arr), max(x_arr), 100)
        y_line = m * x_line + b
        
        # Plot regression line
        ax.plot(x_line, y_line, color=color, linewidth=3, alpha=0.8, zorder=1)

    # Plot Primary Tumors
    plot_group(pt_gpx4, pt_gclc, color_pt, "Primary tumors")
    
    # Plot LN Metastasis
    plot_group(ln_gpx4, ln_gclc, color_ln, "LN metastasis")

    # ---------------------------------------------------------
    # 4. Chart Layout and Annotations
    # ---------------------------------------------------------
    
    # Axis Labels
    ax.set_xlabel("GCLC protein levels (a.u)", fontsize=14, fontweight='bold')
    ax.set_ylabel("GPX4 protein levels (a.u)", fontsize=14, fontweight='bold')
    
    # Axis Limits (approximate from visual inspection)
    ax.set_xlim(-0.005, 0.12)
    ax.set_ylim(-0.005, 0.15)
    
    # Tick styling
    ax.tick_params(axis='both', which='major', labelsize=12, width=1.5, length=5)
    
    # Remove top and right spines (scientific style)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(1.5)
    ax.spines['bottom'].set_linewidth(1.5)

    # ---------------------------------------------------------
    # 5. Custom Legend (Text on Plot)
    # ---------------------------------------------------------
    # The image uses text labels in the top-left corner instead of a standard legend box
    
    # "Melanoma Primary tumors" (Gray)
    ax.text(0.05, 0.95, "Melanoma", transform=ax.transAxes, 
            color=color_pt, fontsize=11, fontweight='bold', ha='left')
    ax.text(0.05, 0.90, "Primary tumors", transform=ax.transAxes, 
            color=color_pt, fontsize=11, fontweight='bold', ha='left')

    # "Melanoma LN metastasis" (Green)
    ax.text(0.05, 0.82, "Melanoma", transform=ax.transAxes, 
            color=color_ln, fontsize=11, fontweight='bold', ha='left')
    ax.text(0.05, 0.77, "LN metastasis", transform=ax.transAxes, 
            color=color_ln, fontsize=11, fontweight='bold', ha='left')

    # ---------------------------------------------------------
    # 6. Statistical Box
    # ---------------------------------------------------------
    # Draw the box with statistics on the right side
    
    # Box coordinates (data coords approx)
    box_x, box_y = 0.095, 0.065
    box_width, box_height = 0.045, 0.04
    
    # Since matplotlib text boxes don't support multi-color text easily,
    # we draw a rectangle and place individual text elements over it.
    
    # Draw the rectangle border
    rect = Rectangle((0.72, 0.45), 0.26, 0.20, transform=ax.transAxes, 
                     linewidth=1.5, edgecolor='black', facecolor='none', zorder=3)
    ax.add_patch(rect)

    # Text inside the box
    # Primary Tumors Stats (Gray)
    ax.text(0.73, 0.61, "Pearson= 0.6930", transform=ax.transAxes,
            color=color_pt, fontsize=9, fontweight='bold')
    ax.text(0.73, 0.57, "Spearman= 0.6367", transform=ax.transAxes,
            color=color_pt, fontsize=9, fontweight='bold')
    
    # LN Metastasis Stats (Green)
    ax.text(0.73, 0.52, "Pearson= 0.5908", transform=ax.transAxes,
            color=color_ln, fontsize=9, fontweight='bold')
    ax.text(0.73, 0.48, "Spearman 0.6237", transform=ax.transAxes,
            color=color_ln, fontsize=9, fontweight='bold')

    # ---------------------------------------------------------
    # 7. Save Output
    # ---------------------------------------------------------
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    # Handle command line argument for output filename
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)