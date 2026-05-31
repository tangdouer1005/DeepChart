import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.lines as mlines
import numpy as np

def generate_chart(output_filename='output.png'):
    # ---------------------------------------------------------
    # 1. Data Preparation
    # ---------------------------------------------------------
    
    # A. The Provided Source Data (Land use for soybeans - Solid Bars)
    # Using io.StringIO to load the provided markdown table data
    csv_data = """Category,2013,2014,2015,2016,2017,2018,2019,2020
Brazil/Domestic,8.12523,8.87591,8.80051,9.78178,8.97895,5.43421,9.32629,7.4605
China,11.0896,11.6053,13.3816,13.3039,15.8891,19.9617,16.7378,17.8011
EU28,4.97095,5.29244,4.75845,4.78287,3.91805,3.7941,4.03213,4.89951
Other countries,3.76588,4.53771,5.26896,5.4739,5.22136,5.65329,5.85281,7.04959"""
    
    df_land_use = pd.read_csv(io.StringIO(csv_data))
    df_land_use.set_index('Category', inplace=True)
    
    # B. Estimated Data for "Deforestation Exposure" (Hatched Bars)
    # These values are not in the source table but are required to reproduce the visual chart.
    # Values are estimated based on the visual height relative to the Left Y-Axis (0 - 1.20).
    deforestation_data = {
        'Brazil/Domestic': [0.18, 0.16, 0.20, 0.25, 0.21, 0.16, 0.15, 0.12],
        'China':           [0.26, 0.26, 0.40, 0.35, 0.53, 0.45, 0.40, 0.33],
        'EU28':            [0.18, 0.18, 0.22, 0.12, 0.12, 0.08, 0.10, 0.08],
        'Other countries': [0.12, 0.12, 0.18, 0.10, 0.15, 0.11, 0.10, 0.10]
    }
    df_deforestation = pd.DataFrame(deforestation_data, index=df_land_use.columns).T

    # C. Explicit Data for "Soy Appropriation" (Markers)
    # These values are explicitly labeled in the chart image (white boxes).
    appropriation_data = {
        'Brazil/Domestic': [23.9, 25.8, 26.3, 28.8, 30.8, 18.9, 30.1, 23.9],
        'China':           [32.8, 32.8, 41.0, 38.8, 54.0, 67.7, 52.6, 57.1],
        'EU28':            [14.4, 15.2, 15.9, 15.3, 17.0, 18.4, 18.7, 24.2],
        'Other countries': [10.6, 12.9, 14.2, 13.5, 12.9, 12.9, 12.9, 16.7]
    }
    
    # ---------------------------------------------------------
    # 2. Plot Setup
    # ---------------------------------------------------------
    
    years = df_land_use.columns.astype(int)
    x = np.arange(len(years))
    width = 0.35
    
    # Define Colors matching the image
    colors = {
        'Brazil/Domestic': '#d73027',  # Red
        'China': '#fdae61',            # Orange
        'EU28': '#abdda4',             # Light Green
        'Other countries': '#2b83ba'   # Blue
    }
    
    # Define Markers matching the image
    markers = {
        'Brazil/Domestic': 'o', # Circle
        'China': 's',           # Square
        'EU28': '^',            # Triangle
        'Other countries': 'D'  # Diamond
    }

    fig, ax1 = plt.subplots(figsize=(14, 8))
    ax2 = ax1.twinx()  # Create secondary y-axis

    # ---------------------------------------------------------
    # 3. Plotting Bars
    # ---------------------------------------------------------
    
    categories = ['Brazil/Domestic', 'China', 'EU28', 'Other countries']
    
    # Plot Hatched Bars (Deforestation) on Left Axis (ax1)
    bottom_def = np.zeros(len(years))
    for cat in categories:
        values = df_deforestation.loc[cat].values
        ax1.bar(x - width/2 - 0.02, values, width, bottom=bottom_def, 
                label=cat, color=colors[cat], edgecolor='black', linewidth=0.5, 
                hatch='//////', alpha=0.9) # Added hatch
        # We draw a white background behind hatched bars to make hatch visible clearly if needed, 
        # but matplotlib handles hatch over color well.
        # To match the "white hatch lines" look, we can set edgecolor to white? 
        # The image has black borders but the fill is hatched. 
        # Standard matplotlib hatch is black lines. To get white lines over color is complex.
        # We will stick to standard black hatching over color or white hatching.
        # Let's try setting hatch color by using a specific rcParam or trick, 
        # but standard black hatch over the color is the most robust reproduction.
        # Actually, looking closely, the hatch lines are white.
        # Matplotlib doesn't easily support white hatch lines over a facecolor in a single call.
        # Workaround: Plot solid color, then plot hatch with no facecolor and white edge.
        
        # Re-plotting for visual accuracy (White Hatching):
        # 1. Solid color base
        # (Already done above, but let's reset)
        # 2. Hatch overlay
        ax1.bar(x - width/2 - 0.02, values, width, bottom=bottom_def, 
                color='none', edgecolor='white', hatch='//////', linewidth=0, alpha=0.5)
        
        # Border
        ax1.bar(x - width/2 - 0.02, values, width, bottom=bottom_def, 
                color='none', edgecolor='black', linewidth=0.7)
        
        bottom_def += values

    # Plot Solid Bars (Land Use) on Right Axis (ax2)
    bottom_use = np.zeros(len(years))
    for cat in categories:
        values = df_land_use.loc[cat].values
        ax2.bar(x + width/2 + 0.02, values, width, bottom=bottom_use, 
                label=cat, color=colors[cat], edgecolor='black', linewidth=0.7)
        bottom_use += values

    # ---------------------------------------------------------
    # 4. Plotting Markers and Labels
    # ---------------------------------------------------------
    
    # Visual analysis suggests markers are plotted on the Right Axis scale.
    # However, the values (Mt) are different from the axis (Mha).
    # Visually, the marker Y-position is approximately Value / 2 on the Right Axis.
    # Example: 2018 China Value 67.7 is plotted at y=34 (approx).
    scaling_factor = 0.5 
    
    for i, year in enumerate(years):
        # We need to sort markers vertically to avoid overlap or match the image stacking order?
        # The image places them roughly in the middle of the relevant bar section or stacked?
        # No, they are floating.
        
        for cat in categories:
            val = appropriation_data[cat][i]
            y_pos = val * scaling_factor
            
            # Plot Marker
            ax2.plot(x[i] + width/2 + 0.02, y_pos, marker=markers[cat], 
                     markersize=12, markeredgecolor='black', markerfacecolor=colors[cat], 
                     linestyle='None', zorder=10)
            
            # Plot Label (White Box)
            # Adjust text position slightly above marker
            ax2.text(x[i] + width/2 + 0.02, y_pos + 1.5, f"{val:.1f}", 
                     ha='center', va='bottom', fontsize=9,
                     bbox=dict(boxstyle="square,pad=0.3", fc="white", ec="black", lw=0.5),
                     zorder=11)

    # ---------------------------------------------------------
    # 5. Axis Formatting
    # ---------------------------------------------------------
    
    # X Axis
    ax1.set_xticks(x)
    ax1.set_xticklabels(years, fontsize=11)
    ax1.tick_params(axis='x', length=0) # Hide ticks
    
    # Left Y Axis (Deforestation)
    ax1.set_ylabel("Brazil deforestation exposure (Mha)", fontsize=12)
    ax1.set_ylim(0, 1.25)
    ax1.tick_params(axis='y', labelsize=11)
    
    # Right Y Axis (Land Use)
    ax2.set_ylabel("Brazil soy land use (Mha)", fontsize=12, rotation=270, labelpad=20)
    ax2.set_ylim(0, 42)
    ax2.tick_params(axis='y', labelsize=11)
    
    # Remove top spines
    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)

    # ---------------------------------------------------------
    # 6. Custom Legend Construction
    # ---------------------------------------------------------
    # The legend in the image is a custom matrix at the top left.
    # We will draw this manually using axes coordinates.
    
    # Legend Configuration
    leg_x_start = 0.02
    leg_y_start = 0.98
    box_w = 0.04
    box_h = 0.05
    gap = 0.01
    
    # Column Headers (Rotated)
    headers = ["Brazil", "China", "EU28", "Other"]
    header_map = {'Brazil': 'Brazil/Domestic', 'China': 'China', 'EU28': 'EU28', 'Other': 'Other countries'}
    
    for j, head in enumerate(headers):
        ax1.text(leg_x_start + j*(box_w+gap) + box_w/2, leg_y_start, head, 
                 rotation=45, ha='left', va='bottom', fontsize=10, transform=ax1.transAxes)

    # Row 1: Solid Colors (Land Use)
    for j, head in enumerate(headers):
        cat = header_map[head]
        rect = patches.Rectangle((leg_x_start + j*(box_w+gap), leg_y_start - box_h), 
                                 box_w, box_h, linewidth=0.7, edgecolor='black', 
                                 facecolor=colors[cat], transform=ax1.transAxes, clip_on=False)
        ax1.add_patch(rect)
    
    # Label Row 1
    ax1.text(leg_x_start + 4*(box_w+gap), leg_y_start - box_h/2, "Brazil soy land use (Mha)", 
             va='center', fontsize=10, transform=ax1.transAxes)

    # Row 2: Hatched Colors (Deforestation)
    row2_y = leg_y_start - box_h - gap
    for j, head in enumerate(headers):
        cat = header_map[head]
        # Base color
        rect = patches.Rectangle((leg_x_start + j*(box_w+gap), row2_y - box_h), 
                                 box_w, box_h, linewidth=0, 
                                 facecolor=colors[cat], transform=ax1.transAxes, clip_on=False)
        ax1.add_patch(rect)
        # Hatch
        rect_h = patches.Rectangle((leg_x_start + j*(box_w+gap), row2_y - box_h), 
                                 box_w, box_h, linewidth=0, edgecolor='white', hatch='//////',
                                 facecolor='none', transform=ax1.transAxes, clip_on=False)
        ax1.add_patch(rect_h)
        # Border
        rect_b = patches.Rectangle((leg_x_start + j*(box_w+gap), row2_y - box_h), 
                                 box_w, box_h, linewidth=0.7, edgecolor='black', 
                                 facecolor='none', transform=ax1.transAxes, clip_on=False)
        ax1.add_patch(rect_b)

    # Label Row 2
    ax1.text(leg_x_start + 4*(box_w+gap), row2_y - box_h/2, "Brazil deforestation exposure (Mha)", 
             va='center', fontsize=10, transform=ax1.transAxes)

    # Row 3: Markers (Appropriation)
    row3_y = row2_y - box_h - gap
    for j, head in enumerate(headers):
        cat = header_map[head]
        # Draw white box container
        rect = patches.Rectangle((leg_x_start + j*(box_w+gap), row3_y - box_h), 
                                 box_w, box_h, linewidth=0.7, edgecolor='black', 
                                 facecolor='white', transform=ax1.transAxes, clip_on=False)
        ax1.add_patch(rect)
        
        # Draw Marker in center
        mx = leg_x_start + j*(box_w+gap) + box_w/2
        my = row3_y - box_h/2
        
        # We need to add a Line2D in axes coords. 
        # transform=ax1.transAxes works for the position, but marker size is in points.
        l = mlines.Line2D([mx], [my], marker=markers[cat], color=colors[cat], 
                          markeredgecolor='black', markersize=10, linestyle='None', 
                          transform=ax1.transAxes, clip_on=False)
        ax1.add_line(l)

    # Label Row 3
    ax1.text(leg_x_start + 4*(box_w+gap), row3_y - box_h/2, "Brazil soy appropriation (Mt)", 
             va='center', fontsize=10, transform=ax1.transAxes)

    # ---------------------------------------------------------
    # 7. Final Layout and Save
    # ---------------------------------------------------------
    plt.tight_layout()
    # Adjust top margin to accommodate the custom legend/headers
    plt.subplots_adjust(top=0.85, right=0.92)
    
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)