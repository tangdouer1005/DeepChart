import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as mpatches

def generate_chart(output_filename='output.png'):
    # 1. Load Source Data
    csv_data = """Type|Food waste reduction approaches (operational strategies)|Frequency in literatures|Percentage
Canteen management|Reduce the size of the plate, provide appropriate portion sizes|19|0.141791
nan|Plan and assess menus regularly|13|0.0970149
nan|Improve sensory quality|11|0.0820896
nan|Go trayless|8|0.0597015
nan|Supervise children's meals|6|0.0447761
nan|Extend lunchtime|6|0.0447761
nan|Improve canteen atmosphere|5|0.0373134
nan|Taste test|5|0.0373134
nan|Survey student feedback|4|0.0298507
nan|Monitor food waste|4|0.0298507
nan|Allow sharing and saving of leftovers|3|0.0223881
nan|Optimize food production plan|3|0.0223881
Food education|Comprehensive food education|14|0.104478
nan|Poster information|13|0.0970149
nan|Train canteen staff|10|0.0746269
nan|Course teaching|6|0.0447761
nan|Train teacher|3|0.0223881
nan|Educational text messages|1|0.00746269"""

    df = pd.read_csv(io.StringIO(csv_data), sep='|')

    # 2. Data Preprocessing
    # Fill forward the 'Type' column to handle nan values
    df['Type'] = df['Type'].ffill()
    
    # Create Short Labels map based on the visual chart
    label_map = {
        "Reduce the size of the plate, provide appropriate portion sizes": "Reduce portions",
        "Plan and assess menus regularly": "Assess menu",
        "Improve sensory quality": "Improve\nsensory\nquality",
        "Go trayless": "Trayless",
        "Supervise children's meals": "Supervise\nchildren's\nmeals",
        "Extend lunchtime": "Extend\nlunchtime",
        "Improve canteen atmosphere": "Improve canteen\natmosphere",
        "Taste test": "Taste test",
        "Survey student feedback": "Survey feedback",
        "Monitor food waste": "Monitor food waste",
        "Allow sharing and saving of leftovers": "Share and pack",
        "Optimize food production plan": "Optimize\nproduction plan",
        "Comprehensive food education": "Comprehensive\nfood education",
        "Poster information": "Poster\ninformation",
        "Train canteen staff": "Train canteen staff",
        "Course teaching": "Course teaching",
        "Train teacher": "Train teacher",
        "Educational text messages": "Text messages"
    }
    df['ShortLabel'] = df['Food waste reduction approaches (operational strategies)'].map(label_map)

    # 3. Prepare Data for Plotting
    # Group data for the inner ring
    inner_data = df.groupby('Type')['Frequency in literatures'].sum().reset_index()
    # Sort to ensure Canteen Management comes first (to match clockwise order starting at top)
    # Canteen starts with 'C', Food starts with 'F', so standard sort works, but let's be explicit
    inner_data['sort_order'] = inner_data['Type'].apply(lambda x: 0 if 'Canteen' in x else 1)
    inner_data = inner_data.sort_values('sort_order')
    
    # Calculate percentages for inner ring text
    total_freq = inner_data['Frequency in literatures'].sum()
    inner_data['pct'] = (inner_data['Frequency in literatures'] / total_freq) * 100

    # Prepare data for outer ring
    # We need to maintain the order: Canteen items then Food Education items
    # Within Canteen, they seem sorted by frequency descending in the data, which matches the chart
    outer_data = df.copy()
    outer_data['pct_display'] = outer_data['Percentage'] * 100

    # 4. Color Palette Definition
    # Inner colors
    canteen_inner_color = '#533698'  # Deep Purple
    edu_inner_color = '#9C6536'      # Bronze/Brown

    # Generate gradients for outer rings
    def get_gradient(start_hex, end_hex, n):
        # Simple linear interpolation between two hex colors
        start = np.array([int(start_hex[i:i+2], 16) for i in (1, 3, 5)])
        end = np.array([int(end_hex[i:i+2], 16) for i in (1, 3, 5)])
        colors = []
        for i in range(n):
            c = start + (end - start) * (i / (n - 1) if n > 1 else 0)
            colors.append('#{:02x}{:02x}{:02x}'.format(int(c[0]), int(c[1]), int(c[2])))
        return colors

    # Canteen outer colors (Purple gradient)
    n_canteen = len(outer_data[outer_data['Type'] == 'Canteen management'])
    canteen_colors = get_gradient('#5e4fa2', '#d0d1e6', n_canteen)

    # Education outer colors (Brown/Tan gradient)
    n_edu = len(outer_data[outer_data['Type'] == 'Food education'])
    edu_colors = get_gradient('#bf812d', '#f6e8c3', n_edu)

    outer_colors = canteen_colors + edu_colors
    inner_colors = [canteen_inner_color, edu_inner_color]

    # 5. Plotting
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Chart parameters
    size = 0.35
    start_angle = 90
    
    # --- Outer Ring ---
    wedges_outer, texts_outer = ax.pie(
        outer_data['Frequency in literatures'], 
        radius=1, 
        colors=outer_colors, 
        startangle=start_angle,
        counterclock=False, # Clockwise to match image
        wedgeprops=dict(width=size, edgecolor='w', linewidth=1)
    )

    # --- Inner Ring ---
    wedges_inner, texts_inner, autotexts_inner = ax.pie(
        inner_data['Frequency in literatures'], 
        radius=1-size, 
        colors=inner_colors, 
        startangle=start_angle,
        counterclock=False,
        autopct='', # We will manually place text
        wedgeprops=dict(width=size, edgecolor='w', linewidth=1)
    )

    # 6. Annotations

    # Inner Ring Labels
    # Canteen
    ax.text(0.2, -0.2, f"Canteen\nmanagement\n{inner_data.iloc[0]['pct']:.1f}%", 
            ha='center', va='center', color='white', fontsize=11, fontweight='normal')
    # Food Education
    ax.text(-0.25, 0.1, f"Food\neducation\n{inner_data.iloc[1]['pct']:.1f}%", 
            ha='center', va='center', color='white', fontsize=11, fontweight='normal')

    # Outer Ring Labels with Leader Lines
    kw = dict(arrowprops=dict(arrowstyle="-", color="#999999", linewidth=0.8),
              zorder=0, va="center")

    for i, p in enumerate(wedges_outer):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        
        # Determine text alignment and position based on angle
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        
        # Connection style
        connectionstyle = f"angle,angleA=0,angleB={ang}"
        
        # Label Text
        label_text = outer_data.iloc[i]['ShortLabel']
        pct_val = outer_data.iloc[i]['pct_display']
        full_text = f"{label_text} {pct_val:.1f}%"
        
        # Specific adjustments for layout to match image closely
        # Push text out further
        r_text = 1.35
        
        # Manual fine-tuning for crowded areas (bottom left)
        if -110 < ang < -70: # Bottom area
             r_text = 1.5
        
        # Color of text matches the group theme roughly
        text_color = '#533698' if i < n_canteen else '#8c510a'
        
        # Calculate xy for annotation
        # Note: Matplotlib pie with counterclock=False calculates angles negative (clockwise)
        # or 360-x. Let's rely on x,y from sin/cos.
        
        ax.annotate(full_text, xy=(x, y), xytext=(r_text*x, r_text*y),
                    horizontalalignment=horizontalalignment,
                    color=text_color,
                    fontsize=10,
                    arrowprops=dict(arrowstyle="-", color="#aaaaaa", 
                                    connectionstyle=connectionstyle, linewidth=0.8))

    # 7. Final Styling
    ax.set_aspect('equal')
    
    # Add Figure Label "b"
    plt.text(-1.5, 1.2, 'b', fontsize=20, fontweight='bold', color='black')
    
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else 'output.png'
    generate_chart(output_file)