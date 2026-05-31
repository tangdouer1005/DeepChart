import sys
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

def generate_chart(output_filename):
    # 1. Data Preparation
    # Extracting non-NaN values from the provided source table
    data = {
        "Vehicle": [
            1.67691414, 0.85776341, 0.85776341, 1.52754235, 0.79955316, 
            0.98719009, 0.5492265, 0.90853999, 1.4973423, 0.33816465, 
            0.91338701, 1.08661299, 1.3186889, 0.72344104, 0.633546, 
            1.23962408, 0.7431799, 1.46442985, 0.87709022
        ],
        "icFSP1": [
            0.63799637, 0.9680146, 0.82384558, 1.06462968, 0.21999558, 
            0.57015749, 1.46761419, 0.65525489
        ],
        "viFSP1": [
            0.414588, 0.11516141, 0.86840956, 0.15949909, 0.07711164, 
            0.61260379, 0.72365508, 0.59192079, 0.70135255, 0.62916065
        ],
        "BSO": [
            0.661774471, 1.4176097, 0.323789802, 1.406779054, 1.597920275, 
            1.487901399, 1.107086638, 1.572788207, 0.791496725, 0.879682758, 
            0.779937778, 0.924634707, 0.716008452, 1.334819278
        ],
        "icFSP1 + BSO": [
            1.48194219, 0.91662165, 0.14804192, 0.83834204, 0.80823838, 
            0.57720985, 0.76833597, 0.72874142
        ],
        "viFSP1 + BSO": [
            0.17624038, 0.29652135, 0.2772585, 1.12237907, 1.13213888, 
            0.76512095, 0.51511285, 0.71736243, 0.6371418, 0.54660466
        ]
    }

    # Convert to DataFrame for Seaborn
    df_list = []
    for group, values in data.items():
        for val in values:
            df_list.append({'Group': group, 'Value': val})
    df = pd.DataFrame(df_list)

    # 2. Plot Setup
    # Define colors based on visual inspection of the chart
    colors = [
        "#C0C0C0",  # Vehicle (Grey)
        "#6A6EA9",  # icFSP1 (Slate Blue/Purple)
        "#5F9EA0",  # viFSP1 (Teal)
        "#A4A048",  # BSO (Olive)
        "#FFFFA0",  # icFSP1 + BSO (Pale Yellow)
        "#9370DB"   # viFSP1 + BSO (Medium Purple)
    ]
    
    sns.set_style("ticks")
    fig, ax = plt.subplots(figsize=(5, 6))

    # 3. Draw Plots
    # Boxplot
    sns.boxplot(
        data=df, x='Group', y='Value', 
        palette=colors, 
        width=0.6, 
        linewidth=1, 
        fliersize=0, # Hide outliers as we will plot points
        ax=ax,
        boxprops=dict(alpha=0.8) # Slight transparency
    )

    # Swarm/Strip plot for individual points
    sns.stripplot(
        data=df, x='Group', y='Value', 
        palette=colors, 
        size=8, 
        linewidth=1, 
        edgecolor='black', 
        jitter=True,
        ax=ax
    )

    # 4. Reference Lines
    # Horizontal dashed line at y=1.0
    ax.axhline(y=1.0, color='black', linestyle='--', linewidth=1.5, alpha=0.7)
    
    # Vertical dashed line separating single treatments from combinations
    # Between index 3 (BSO) and 4 (icFSP1 + BSO)
    ax.axvline(x=3.5, color='black', linestyle='--', linewidth=1, alpha=0.7)

    # 5. Statistical Annotations
    # Helper function to draw significance brackets
    def draw_significance(ax, x1, x2, y, p_value):
        h = 0.05  # height of the bracket legs
        col = 'k' # color
        
        # Draw the bracket
        ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1, c=col)
        
        # Add text
        text = f"P = {p_value}"
        ax.text((x1+x2)*.5, y+h, text, ha='center', va='bottom', color=col, fontsize=10)

    # Coordinates for groups
    # Vehicle=0, icFSP1=1, viFSP1=2, BSO=3, icFSP1+BSO=4, viFSP1+BSO=5
    
    # Define y-positions for stacking annotations to match the image layout
    # Base max value is around 1.7. We need to stack upwards.
    
    # Level 1 (Lowest)
    draw_significance(ax, 0, 1, 1.75, "0.7767") # Vehicle vs icFSP1
    draw_significance(ax, 3, 4, 1.75, "0.4194") # BSO vs icFSP1+BSO
    
    # Level 2
    draw_significance(ax, 0, 2, 1.95, "0.0038") # Vehicle vs viFSP1
    draw_significance(ax, 3, 5, 1.95, "0.0232") # BSO vs viFSP1+BSO
    
    # Level 3
    draw_significance(ax, 0, 3, 2.15, "0.9974") # Vehicle vs BSO
    
    # Level 4
    draw_significance(ax, 0, 4, 2.35, "0.6975") # Vehicle vs icFSP1+BSO
    
    # Level 5 (Highest)
    draw_significance(ax, 0, 5, 2.55, "0.0573") # Vehicle vs viFSP1+BSO

    # 6. Formatting
    # Y-axis
    ax.set_ylabel("End-point tumour volume\n(compared with vehicle)", fontsize=12, color='black')
    ax.set_ylim(0, 2.8) # Adjust limit to fit annotations
    ax.set_yticks([0, 0.3, 0.5, 0.8, 1.0, 1.3, 1.5, 1.8, 2.0])
    
    # X-axis
    ax.set_xlabel("")
    ax.set_xticklabels(
        ["Vehicle", "icFSP1", "viFSP1", "BSO", "icFSP1 + BSO", "viFSP1 + BSO"], 
        rotation=45, ha='right', fontsize=11
    )
    
    # Title "g"
    ax.text(-0.15, 1.05, "g", transform=ax.transAxes, fontsize=20, fontweight='bold', va='top', ha='right')

    # Remove top and right spines
    sns.despine()

    # Save output
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    generate_chart(output_file)