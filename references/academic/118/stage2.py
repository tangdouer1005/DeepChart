import matplotlib.pyplot as plt
import numpy as np
import sys
import seaborn as sns
from matplotlib.patches import Rectangle

def generate_chart(output_filename):
    # 1. Data Preparation
    # Transcribed directly from the provided Markdown table
    
    # Group: LN Metastasis (Green in chart)
    # Columns: GCLC (X), FSP1 (Y)
    ln_data = [
        (0.0562, 0.0769), (0.0135, 0.105), (0.0133, 0.1191), (0.0095, 0.1346),
        (0.0095, 0.1102), (0, 0.0744), (0.0221, 0.0942), (0.0398, 0.0956),
        (0.0461, 0.1068), (0, 0.1209), (0.0123, 0.1431), (0, 0.0961),
        (0.0882, 0.0986), (0.0279, 0.049), (0.0408, 0.0947), (0.0944, 0.1197),
        (0.0039, 0.1331), (0.001, 0.0809), (0.082, 0.0849), (0, 0.1076),
        (0.0146, 0.0366), (0, 0.1132)
    ]
    
    # Group: Primary Tumor (Grey in chart)
    # Columns: GCLC (X), FSP1 (Y)
    pt_data = [
        (0.0558, 0.0802), (0.0758, 0.0968), (0.0426, 0.0871), (0.038, 0.0682),
        (0.1027, 0.1147), (0, 0.0646), (0.03, 0.1423), (0.0593, 0.1262),
        (0, 0.1117), (0.049, 0.1265), (0.0086, 0.0877), (0.0157, 0.0962),
        (0.0194, 0.1131), (0.0259, 0), (0.0072, 0.0587), (0.0889, 0.0995),
        (0.0764, 0.1306), (0.0438, 0.1284), (0, 0.0823), (0, 0.1239),
        (0.0264, 0.0969), (0.0668, 0.1038), (0.0443, 0.0749), (0.0272, 0.0746),
        (0.0806, 0.1051)
    ]

    # Separate into X and Y arrays
    ln_x = np.array([d[0] for d in ln_data])
    ln_y = np.array([d[1] for d in ln_data])
    
    pt_x = np.array([d[0] for d in pt_data])
    pt_y = np.array([d[1] for d in pt_data])

    # 2. Plot Setup
    # Set style to match scientific publication aesthetics
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
    plt.rcParams['axes.linewidth'] = 2  # Thicker spines
    
    fig, ax = plt.subplots(figsize=(6, 5))
    
    # Colors extracted visually from the chart
    color_pt = '#888888'  # Grey
    color_ln = '#55a630'  # Green
    
    # 3. Plotting Data
    
    # --- Primary Tumors (Grey) ---
    # Scatter: Open circles
    ax.scatter(pt_x, pt_y, facecolors='none', edgecolors=color_pt, s=60, linewidth=1.5, zorder=2)
    
    # Regression Line (Grey)
    # Calculate linear regression
    m_pt, b_pt = np.polyfit(pt_x, pt_y, 1)
    # Create line points spanning the range of the data
    x_range_pt = np.linspace(min(pt_x), max(pt_x), 100)
    ax.plot(x_range_pt, m_pt * x_range_pt + b_pt, color=color_pt, linewidth=3, zorder=1)

    # --- LN Metastasis (Green) ---
    # Scatter: Open circles
    ax.scatter(ln_x, ln_y, facecolors='none', edgecolors=color_ln, s=60, linewidth=1.5, zorder=2)
    
    # Regression Line (Green)
    m_ln, b_ln = np.polyfit(ln_x, ln_y, 1)
    x_range_ln = np.linspace(min(ln_x), max(ln_x), 100)
    ax.plot(x_range_ln, m_ln * x_range_ln + b_ln, color=color_ln, linewidth=3, zorder=1)

    # 4. Formatting Axes
    
    # Labels
    ax.set_ylabel("FSP1 protein levels (a.u)", fontsize=14, fontweight='bold', labelpad=10)
    # Note: X label is cut off in image, but based on data headers it is GCLC
    # We will leave it blank or minimal to match the visual crop, but usually scientific plots have it.
    # The image shows numbers 0.00, 0.05, 0.10.
    
    # Ticks
    ax.set_xticks([0.00, 0.05, 0.10])
    ax.set_yticks([0.00, 0.05, 0.10, 0.15])
    ax.tick_params(axis='both', which='major', labelsize=12, width=2, length=6)
    
    # Set limits to match image
    ax.set_xlim(-0.005, 0.11)
    ax.set_ylim(-0.005, 0.15)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # 5. Annotations
    
    # "r" label in top left
    ax.text(-0.15, 1.0, 'r', transform=ax.transAxes, fontsize=18, fontweight='bold', va='top', ha='right')

    # Group Labels (Bottom Right)
    # "Melanoma Primary tumors" (Grey)
    ax.text(0.105, 0.045, "Melanoma\nPrimary tumors", color=color_pt, 
            fontsize=11, fontweight='bold', ha='right', va='bottom')
    
    # "Melanoma LN metastasis" (Green)
    ax.text(0.105, 0.025, "Melanoma\nLN metastasis", color=color_ln, 
            fontsize=11, fontweight='bold', ha='right', va='top')

    # 6. Statistics Box
    # The image has a box with specific correlation stats.
    # We draw a rectangle and place text manually to support multiple colors.
    
    # Box coordinates (data coords approx)
    box_x, box_y = 0.115, 0.075
    box_width, box_height = 0.05, 0.035 # Relative sizing isn't perfect in data coords, using axis coords for text is safer
    
    # Using axis coordinates for the box to place it to the right of the data
    # The image shows the box floating to the right.
    
    # Create a custom legend-like box
    # We use a Rectangle patch and text.
    # Position: Right side, vertically centered roughly.
    
    # Define text content from source data
    from scipy import stats
    r_pt, _ = stats.pearsonr(pt_x, pt_y)
    s_pt, _ = stats.spearmanr(pt_x, pt_y)
    r_ln, _ = stats.pearsonr(ln_x, ln_y)
    s_ln, _ = stats.spearmanr(ln_x, ln_y)

    stats_text_lines = [
        (f"Pearson= {r_pt:.4f}", color_pt),
        (f"Spearman= {s_pt:.4f}", color_pt),
        (f"Pearson= {r_ln:.4f}", color_ln),
        (f"Spearman {s_ln:.4f}", color_ln) 
    ]
    
    # Adjusting text to match image exactly
    # Image:
    # Pearson= 0.2822 (Grey)
    # Spearman= 0.3522 (Grey)
    # Pearson= -0.1117 (Green)
    # Spearman -0.2482 (Green) -> The image actually looks like "Spearman -0.2482" or "Spearman= -0.2482". 
    # The source data table says: Spearman r: -0.2482. I will use "Spearman -0.2482" to match the visual density.
    
    # Draw the box border
    rect = Rectangle((0.115, 0.065), 0.045, 0.045, linewidth=2, edgecolor='black', facecolor='none', clip_on=False)
    ax.add_patch(rect)
    
    # Add text inside the box
    # We need to manually position these lines relative to the box
    start_x = 0.117
    start_y = 0.103
    line_spacing = 0.011
    
    ax.text(start_x, start_y, "Pearson= 0.2822", color=color_pt, fontsize=10, fontweight='bold')
    ax.text(start_x, start_y - line_spacing, "Spearman= 0.3522", color=color_pt, fontsize=10, fontweight='bold')
    ax.text(start_x, start_y - 2*line_spacing, "Pearson= -0.1117", color=color_ln, fontsize=10, fontweight='bold')
    ax.text(start_x, start_y - 3*line_spacing, "Spearman -0.2482", color=color_ln, fontsize=10, fontweight='bold')

    # Adjust layout to make room for the box on the right
    plt.subplots_adjust(right=0.75, bottom=0.15, left=0.2)

    # Save
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    generate_chart(output_file)