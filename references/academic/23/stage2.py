import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats

def generate_chart(output_filename):
    # 1. Data Preparation
    # We reconstruct the dataframe based on the provided Source Data.
    # Only the categories present in the chart (Morphology, Biomarker, Prognosis) are included.
    
    data_records = [
        {'Model': 'conch', 'Category': 'Morphology', 'AUROC': 0.7659939108398429, 'Dataset': 1.2},
        {'Model': 'biomedclip', 'Category': 'Morphology', 'AUROC': 0.7331658780868027, 'Dataset': 15},
        {'Model': 'plip', 'Category': 'Morphology', 'AUROC': 0.6983860366946149, 'Dataset': 0.208},
        
        {'Model': 'conch', 'Category': 'Biomarker', 'AUROC': 0.726168367463843, 'Dataset': 1.2},
        {'Model': 'biomedclip', 'Category': 'Biomarker', 'AUROC': 0.667361737958213, 'Dataset': 15},
        {'Model': 'plip', 'Category': 'Biomarker', 'AUROC': 0.6516216846643966, 'Dataset': 0.208},
        
        {'Model': 'conch', 'Category': 'Prognosis', 'AUROC': 0.6318876255522493, 'Dataset': 1.2},
        {'Model': 'biomedclip', 'Category': 'Prognosis', 'AUROC': 0.6051941716893544, 'Dataset': 15},
        {'Model': 'plip', 'Category': 'Prognosis', 'AUROC': 0.5674663216946358, 'Dataset': 0.208},
    ]
    
    df = pd.DataFrame(data_records)

    # Color mapping approximation based on the image
    colors = {
        'Morphology': '#684778',  # Dark Purple
        'Biomarker': '#BC6C88',   # Muted Rose/Pink
        'Prognosis': '#8D4E52'    # Brownish Red
    }

    # 2. Plotting Setup
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(6, 5))

    # Categories in the specific order shown in the legend
    categories = ['Morphology', 'Biomarker', 'Prognosis']

    # 3. Plotting Loop
    for cat in categories:
        subset = df[df['Category'] == cat]
        color = colors[cat]
        
        # Construct label with stats
        if len(subset) > 1:
            r_val, p_val = stats.pearsonr(subset['Dataset'], subset['AUROC'])
            
            # Formatting to match image
            if cat == 'Prognosis':
                p_str = f"{p_val:.1f}"
            else:
                p_str = f"{p_val:.2f}"
                
            label = f"{cat} ($r = {r_val:.2f}, P = {p_str}$)"
        else:
            label = cat
        
        # Plot Scatter points
        ax.scatter(
            subset['Dataset'], 
            subset['AUROC'], 
            color=color, 
            s=80,           # Marker size
            label=label, 
            zorder=3,
            edgecolor='none'
        )
        
        # Plot Regression Line
        # We use numpy polyfit for a simple linear regression (degree 1)
        x = subset['Dataset']
        y = subset['AUROC']
        m, b = np.polyfit(x, y, 1)
        
        # Create line points spanning the visual x-axis range (0 to 15)
        x_line = np.array([0.2, 15.2]) 
        y_line = m * x_line + b
        
        ax.plot(x_line, y_line, color=color, linewidth=2, zorder=2)

    # 4. Styling and Layout
    
    # Axis Labels
    ax.set_xlabel("Pretraining dataset (M ICPs)", fontsize=12)
    ax.set_ylabel("Average downstream performance\nby task type (AUROC)", fontsize=12)
    
    # Axis Limits
    ax.set_xlim(-0.5, 15.8)
    ax.set_ylim(0.50, 0.85)
    
    # Ticks
    ax.set_xticks(np.arange(0, 16, 2))
    ax.set_yticks(np.arange(0.50, 0.86, 0.05))
    
    # Grid styling
    ax.grid(True, color='#E0E0E0', linestyle='-', linewidth=1.5)
    
    # Legend
    # Positioned top right, no frame or very light frame
    leg = ax.legend(loc='upper right', frameon=True, fontsize=9.5, handletextpad=0.1)
    leg.get_frame().set_edgecolor('white')
    leg.get_frame().set_facecolor('white')
    leg.get_frame().set_alpha(0.8)

    # Add the bold 'b' annotation in the top left corner
    # We place it relative to the figure or axes. In the image, it's to the left of the Y-axis.
    fig.text(0.02, 0.92, 'b', fontsize=24, fontweight='bold', fontfamily='sans-serif')

    # Adjust layout to make room for labels
    plt.tight_layout()
    
    # 5. Save Output
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    # Handle command line argument for output filename
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        output_file = "output.png"
        
    generate_chart(output_file)