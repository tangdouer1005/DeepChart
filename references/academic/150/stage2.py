import matplotlib.pyplot as plt
import pandas as pd
import io
import sys

def generate_chart(output_filename='output.png'):
    # 1. Source Data
    # Using a headerless CSV string to avoid parsing ambiguity with commas in headers
    csv_data = """Combustion,73.2
Others,4.7
Transport,2.6
Loss,103.5
Electricity,10.5
Heat,0.6
Credits,-4.3
Biogenic,-176.7"""

    # Load data
    df = pd.read_csv(io.StringIO(csv_data), header=None, names=['Category', 'Value'])

    # 2. Configuration & Styling
    colors = {
        'Combustion': '#E8BC85',  # Tan/Orange
        'Others': '#808080',      # Grey
        'Transport': '#468088',   # Teal
        'Loss': '#365D8D',        # Dark Blue
        'Electricity': '#9ABCA6', # Sage Green
        'Heat': '#8FBBD9',        # Light Blue
        'Credits': '#468088',     # Teal
        'Biogenic': '#D3654B'     # Terracotta/Red
    }

    # 3. Data Processing
    # Positive stack order (bottom-up for plotting): Heat -> Electricity -> Loss -> Transport -> Others -> Combustion
    # This results in visual top-down: Combustion -> Others -> Transport -> Loss -> Electricity -> Heat
    pos_order = ['Heat', 'Electricity', 'Loss', 'Transport', 'Others', 'Combustion']
    
    # Negative stack order (top-down from 0): Credits -> Biogenic
    neg_order = ['Credits', 'Biogenic']

    # 4. Plotting
    fig, ax = plt.subplots(figsize=(4, 7))
    
    bar_width = 0.8
    x_pos = 0

    # Plot Positive Bars
    current_bottom = 0
    for cat in pos_order:
        val = df[df['Category'] == cat]['Value'].values[0]
        ax.bar(x_pos, val, width=bar_width, bottom=current_bottom, 
               color=colors[cat], edgecolor='none', linewidth=0)
        current_bottom += val

    # Plot Negative Bars
    current_bottom = 0
    for cat in neg_order:
        val = df[df['Category'] == cat]['Value'].values[0]
        # val is negative, so adding it to current_bottom moves down
        ax.bar(x_pos, val, width=bar_width, bottom=current_bottom, 
               color=colors[cat], edgecolor='none', linewidth=0)
        current_bottom += val

    # 5. Labels
    # Manual Y-positions to match the visual layout of the reference image
    label_positions = {
        'Combustion': 150,
        'Others': 118,
        'Transport': 95,
        'Loss': 50,
        'Electricity': 15,
        'Heat': -5,         
        'Credits': -35,
        'Biogenic': -130
    }

    text_x = x_pos + (bar_width / 2) + 0.15 # Offset to the right

    for i, row in df.iterrows():
        cat = row['Category']
        val = row['Value']
        
        label_text = f"{cat} {val}"
        color = colors[cat]
        
        y_pos = label_positions.get(cat, 0)
        
        ax.text(text_x, y_pos, label_text, 
                ha='left', va='center', 
                color=color, fontsize=14, fontfamily='sans-serif')

    # 6. Total Label
    total_net = 14.1 
    # Positive stack height: 195.1
    ax.text(x_pos, 195.1 + 15, f"{total_net}\ngCO$_2$e MJ$^{{-1}}$", 
            ha='center', va='bottom', 
            color='#2F5566', fontsize=16, fontfamily='sans-serif')

    # 7. Axis Formatting
    ax.set_ylim(-200, 250)
    yticks = [-200.0, -150.0, -100.0, -50.0, 0.0, 50.0, 100.0, 150.0, 200.0, 250.0]
    ax.set_yticks(yticks)
    ax.set_yticklabels([f"{x:.1f}" for x in yticks], fontsize=12, color='#333333')
    
    ax.set_xticks([])
    
    # Spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    
    ax.spines['left'].set_color('#333333')
    ax.spines['left'].set_linewidth(0.8)
    ax.spines['left'].set_position(('data', -0.6)) # Move spine left
    
    ax.tick_params(axis='y', colors='#333333', length=4, direction='out')

    # 8. Figure Label 'b'
    ax.text(-0.45, 1.0, 'b', transform=ax.transAxes, 
            fontsize=24, fontweight='bold', color='black', va='top')

    plt.xlim(-1, 3.0) # Adjust to fit text
    
    plt.savefig(output_filename, bbox_inches='tight', dpi=300, facecolor='white')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else 'output.png'
    generate_chart(output_file)