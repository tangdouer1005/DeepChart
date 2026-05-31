import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D

# 1. Data Loading
# Using the provided markdown data exactly
csv_data = """
Unnamed: 0|Observed diets|Red and processed meat (25%)|Red and processed meat (50%)|Dairy (25%)|Dairy (50%)
Vegetables and fruits|0.468|0.632|0.645|0.6035|0.6275
Whole-grain foods|0.236|0.192|0.184|0.166|0.156
Grain foods ratio|0.282|0.282|0.282|0.282|0.282
Protein foods|0.714|0.802|0.814|0.848|0.866
Plant-based protein foods|0.282|0.624|0.65|0.76|0.794
Beverages|0.788|0.788|0.788|0.546|0.516
Fatty acids ratio|0.514|0.568|0.608|0.634|0.75
Saturated fats|0.712|0.728|0.746|0.788|0.864
Free sugars|0.741|0.737|0.739|0.736|0.734
Sodium|0.51|0.534|0.555|0.534|0.552
"""

def radar_factory(num_vars, frame='polygon'):
    """
    Create a radar chart with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle', 'polygon'}
        Shape of frame surrounding axes.
    """
    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)

    class RadarAxes(PolarAxes):
        name = 'radar'
        # use 1 line segment to connect specified points
        RESOLUTION = 1

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # rotate plot such that the first axis is at the top
            self.set_theta_zero_location('N')

        def fill(self, *args, closed=True, **kwargs):
            """Override fill so that line is closed by default"""
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.append(x, x[0])
                y = np.append(y, y[0])
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            # The Axes patch must be centered at (0.5, 0.5) and of radius 0.5
            # in axes coordinates.
            if frame == 'circle':
                return Circle((0.5, 0.5), 0.5)
            elif frame == 'polygon':
                return RegularPolygon((0.5, 0.5), num_vars,
                                      radius=0.5, edgecolor="k")
            else:
                raise ValueError("unknown value for 'frame': %s" % frame)

        def _gen_axes_spines(self):
            if frame == 'circle':
                return super()._gen_axes_spines()
            elif frame == 'polygon':
                # spine_type must be 'left'/'right'/'top'/'bottom'/'circle'.
                # spine.axis must be 'x'/'y'.
                # But these are deprecated.
                # The proper way to do this is to create a Path for the spine.
                # However, for simplicity in this specific replication task, 
                # we will rely on the grid lines to define the shape visually
                # and hide the outer spine if necessary.
                return super()._gen_axes_spines()

    register_projection(RadarAxes)
    return theta

def generate_chart(output_filename):
    # 2. Process Data
    df = pd.read_csv(io.StringIO(csv_data), sep="|")
    
    # Clean column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Rename the first column to 'Category'
    df.rename(columns={'Unnamed: 0': 'Category'}, inplace=True)
    
    # Clean category names (strip whitespace)
    df['Category'] = df['Category'].str.strip()
    
    # Convert values to percentages (0-100 scale)
    data_cols = df.columns[1:]
    df[data_cols] = df[data_cols] * 100
    
    # Categories
    categories = df['Category'].tolist()
    N = len(categories)
    
    # Define angles
    theta = radar_factory(N, frame='polygon')
    
    # 3. Plotting Setup
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='radar'))
    
    # Adjust grid to look like the image (polygonal grid lines)
    # We hide the default circular grid and draw polygonal ones manually if needed,
    # but Matplotlib's polar plot with straight line segments between points approximates this.
    # However, standard grid() is circular. 
    # To replicate the image's polygonal grid (straight lines between axes):
    ax.grid(False) # Turn off default circular grid
    
    # Draw polygonal grid lines
    r_grids = [20, 40, 60, 80, 100]
    for r in r_grids:
        # Create a closed polygon for the grid
        grid_values = [r] * N
        ax.plot(theta, grid_values, color='grey', linestyle='--', linewidth=0.8, alpha=0.5, zorder=0)
        
        # Add percentage labels on the vertical axis (top spoke)
        # The image has labels on the top vertical axis (Vegetables and fruits)
        # But usually, they are placed slightly off-center.
        # Let's place them on the first axis (0 radians, which is North here)
        ax.text(0, r, f'{r}%', ha='right', va='bottom', color='grey', fontsize=10)

    # Draw spokes (radial axes)
    for angle in theta:
        ax.plot([angle, angle], [0, 100], color='grey', linestyle='--', linewidth=0.8, alpha=0.5, zorder=0)

    # 4. Plot Data Series
    # Define colors and styles based on the image
    # Observed diets: Grey dashed
    # Red (50%): Dark Brown
    # Red (25%): Light Brown/Orange
    # Dairy (50%): Dark Blue
    # Dairy (25%): Light Blue
    
    styles = {
        'Observed diets': {'color': '#999999', 'ls': '--', 'lw': 3, 'label': 'Observed diets'},
        'Red and processed meat (50%)': {'color': '#8B4513', 'ls': '-', 'lw': 2.5, 'label': 'Red and processed meat (50%)'},
        'Red and processed meat (25%)': {'color': '#D2691E', 'ls': '-', 'lw': 2.5, 'label': 'Red and processed meat (25%)'},
        'Dairy (50%)': {'color': '#1F4E79', 'ls': '-', 'lw': 2.5, 'label': 'Dairy (50%)'},
        'Dairy (25%)': {'color': '#4682B4', 'ls': '-', 'lw': 2.5, 'label': 'Dairy (25%)'}
    }
    
    # Plot order matters for layering. 
    # Usually solid lines on top of dashed.
    plot_order = [
        'Observed diets',
        'Red and processed meat (25%)',
        'Dairy (25%)',
        'Red and processed meat (50%)',
        'Dairy (50%)'
    ]
    
    for col in plot_order:
        values = df[col].tolist()
        style = styles[col]
        ax.plot(theta, values, color=style['color'], linestyle=style['ls'], linewidth=style['lw'], label=style['label'])

    # 5. Formatting
    
    # Set Category Labels
    # We need to adjust label position to avoid overlap
    ax.set_varlabels(categories)
    
    # Adjust label padding
    ax.tick_params(pad=20, labelsize=11)
    
    # Remove radial tick labels (the standard ones) since we added custom ones
    ax.set_yticklabels([])
    
    # Set limits
    ax.set_ylim(0, 100)
    
    # Remove the outer circle frame (spine) to match the "open" look of the chart
    ax.spines['polar'].set_visible(False)

    # 6. Legend
    # The image has a specific legend layout at the bottom.
    # We will create a custom legend below the chart.
    
    # Create legend handles manually to control order and layout exactly like the image
    # Image Layout:
    # Col 1: Observed (dashed), Red (50%), Dairy (50%)
    # Col 2: (Empty), Red (25%), Dairy (25%)
    # Actually, looking at the image:
    # Left: Observed diets
    # Middle-Left: Red (50%), Dairy (50%)
    # Middle-Right: Red (25%), Dairy (25%)
    # It looks like a 2-column legend or 3-column.
    # Let's use a standard flow:
    # Observed, Red(50), Dairy(50)
    # (Blank), Red(25), Dairy(25)
    
    # Let's just list them in a clean 2-column format which is standard and readable.
    # Column 1: Observed, Red (50%), Dairy (50%)
    # Column 2: (Spacer), Red (25%), Dairy (25%)
    
    from matplotlib.lines import Line2D
    
    legend_elements = [
        Line2D([0], [0], color=styles['Observed diets']['color'], lw=3, ls='--', label='Observed diets'),
        Line2D([0], [0], color='white', lw=0, label=''), # Spacer
        
        Line2D([0], [0], color=styles['Red and processed meat (50%)']['color'], lw=2.5, label='Red and processed meat (50%)'),
        Line2D([0], [0], color=styles['Red and processed meat (25%)']['color'], lw=2.5, label='Red and processed meat (25%)'),
        
        Line2D([0], [0], color=styles['Dairy (50%)']['color'], lw=2.5, label='Dairy (50%)'),
        Line2D([0], [0], color=styles['Dairy (25%)']['color'], lw=2.5, label='Dairy (25%)'),
    ]

    # Place legend at the bottom
    # ncol=2 to split into two columns
    leg = ax.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.1), 
              ncol=2, frameon=False, fontsize=11)
    
    # Align text to left
    for text in leg.get_texts():
        text.set_ha('left')

    plt.tight_layout()
    
    # Save output
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    generate_chart(output_file)