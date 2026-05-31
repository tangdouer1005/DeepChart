import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import seaborn as sns
import numpy as np
from scipy import stats

def get_source_data():
    """
    Returns the raw data provided in the prompt as a pandas DataFrame.
    """
    csv_data = """Cancer Type|Model|Percentage of Slides in Pretraining Dataset (%)|Average Downstream Performance (AUROC)
LUNG|ctranspath|8.4|0.7101566922966756
BRCA|ctranspath|7.5|0.6901946923437127
STAD|ctranspath|3.4|0.6727500426566878
CRC|ctranspath|11.7|0.6402351975254987
LUNG|phikon|9.7|0.7086469364758765
BRCA|phikon|8.8|0.6333019990370683
STAD|phikon|4|0.6650650873334706
CRC|phikon|5.7|0.6335703165007269
LUNG|uni|9.8|0.7582049929810751
BRCA|uni|3.3|0.6884572772690907
STAD|uni|6.7|0.6769115022211536
CRC|uni|8.3|0.6585192894528652
LUNG|kaiko|9.7|0.7311053739265448
BRCA|kaiko|8.8|0.685518762408426
STAD|kaiko|4|0.6679383667204072
CRC|kaiko|5.7|0.609584221956904
LUNG|prov-gigapath|45|0.7578128341867243
BRCA|prov-gigapath|2.7|0.66703719221213
STAD|prov-gigapath|0.7|0.6867942247149665
CRC|prov-gigapath|30|0.6796362735454282
LUNG|virchow-class|6.1|0.7174955993098335
BRCA|virchow-class|25|0.6589119444462541
STAD|virchow-class|3.5|0.6845577051089727
CRC|virchow-class|3.2|0.6476261453717196
LUNG|virchow2-class|4|0.7453463548176368
BRCA|virchow2-class|19|0.7043400914608242
STAD|virchow2-class|3|0.7171710064688561
CRC|virchow2-class|6|0.6911429496854462
LUNG|panakeia|0|0.7136461434822977
BRCA|panakeia|82|0.7080816433172487
STAD|panakeia|0|0.6830453013043695
CRC|panakeia|18|0.6616418630330357"""
    
    df = pd.read_csv(io.StringIO(csv_data), sep='|')
    return df

def generate_plot(output_path):
    # 1. Load and Prepare Data
    df = get_source_data()
    
    # Rename columns for easier access
    df.columns = ['Cancer Type', 'Model', 'Percentage', 'Performance']
    
    # 2. Define Visual Styles
    
    # Color Mapping (approximated from image)
    # LUNG (NSCLC): Light Blue, STAD: Salmon/Light Red, BRCA: Dark Red, CRC: Dark Blue
    colors = {
        'LUNG': '#6baed6',  # Light Blue
        'STAD': '#d6616b',  # Salmon
        'BRCA': '#8c1b2f',  # Dark Red
        'CRC':  '#316ca0'   # Medium/Dark Blue
    }
    
    # Marker Mapping
    # CTransPath: Circle, Phikon: Square, UNI: Diamond, Kaiko: Triangle Up
    # Prov-GigaPath: X, Virchow: Plus (filled P), Virchow2: Triangle Down, Panakeia: Pentagon
    markers = {
        'ctranspath': 'o',
        'phikon': 's',
        'uni': 'D',
        'kaiko': '^',
        'prov-gigapath': 'X',
        'virchow-class': 'P', 
        'virchow2-class': 'v',
        'panakeia': 'p'
    }
    
    # Legend Label Mapping (Model names)
    model_labels = {
        'ctranspath': 'CTransPath',
        'phikon': 'Phikon',
        'uni': 'UNI',
        'kaiko': 'Kaiko',
        'prov-gigapath': 'Prov-GigaPath',
        'virchow-class': 'Virchow',
        'virchow2-class': 'Virchow2',
        'panakeia': 'Panakeia'
    }

    # 3. Plotting
    fig, ax = plt.subplots(figsize=(7, 6))
    
    # Set background style
    ax.set_facecolor('white')
    ax.grid(True, color='#d9d9d9', linestyle='-', linewidth=0.8)
    ax.set_axisbelow(True) # Grid behind plot elements

    # A. Draw Regression Lines (per cancer type)
    # We iterate through the specific order to match legend order if possible, or just keys
    cancer_order = ['LUNG', 'STAD', 'BRCA', 'CRC']
    
    for c_type in cancer_order:
        subset = df[df['Cancer Type'] == c_type]
        # Use seaborn regplot for the line, but disable scatter (we draw scatter manually for markers)
        sns.regplot(
            data=subset, 
            x='Percentage', 
            y='Performance', 
            scatter=False, 
            color=colors[c_type], 
            ci=None, 
            ax=ax,
            line_kws={'linewidth': 1.5, 'alpha': 0.9}
        )

    # B. Draw Scatter Points (per row to handle specific markers)
    for _, row in df.iterrows():
        c_type = row['Cancer Type']
        model = row['Model']
        
        ax.scatter(
            row['Percentage'], 
            row['Performance'], 
            color=colors[c_type], 
            marker=markers[model], 
            s=45, # Size
            edgecolor=colors[c_type], # Same as face for solid look, or None
            linewidth=0.5,
            zorder=3 # Ensure points are above grid and lines
        )

    # 4. Configure Axes
    ax.set_xlabel('Percentage of slides in pretraining dataset (%)', fontsize=12, labelpad=8)
    ax.set_ylabel('Average downstream performance\nby cancer type (AUROC)', fontsize=12, labelpad=8)
    
    # Set limits to match image roughly
    ax.set_xlim(-5, 87)
    ax.set_ylim(0.60, 0.77)
    
    # 5. Create Legends
    
    # Legend 1: Cancer Type (Top Right)
    cancer_handles = []
    for c_type in cancer_order:
        # Calculate stats dynamically
        subset = df[df['Cancer Type'] == c_type]
        r_val, p_val = stats.pearsonr(subset['Percentage'], subset['Performance'])
        
        # Format label
        display_name = 'NSCLC' if c_type == 'LUNG' else c_type
        if c_type == 'STAD':
            p_str = f"{p_val:.1f}"
        else:
            p_str = f"{p_val:.2f}"
        label_text = f"{display_name} ($r={r_val:.2f}, P={p_str}$)"

        # Create a proxy artist (Line2D) for the legend
        handle = mlines.Line2D([], [], color=colors[c_type], marker='o', linestyle='None',
                              markersize=6, label=label_text)
        cancer_handles.append(handle)
        
    legend1 = ax.legend(
        handles=cancer_handles, 
        title='Cancer type', 
        loc='upper right', 
        frameon=False, # Transparent background for this legend in the image
        fontsize=9,
        title_fontsize=10,
        handletextpad=0.1
    )
    # Align text to the right visually? The image has standard alignment.
    
    # Add the first legend manually to the plot so we can add a second one
    ax.add_artist(legend1)
    
    # Legend 2: Model (Bottom Right)
    model_order = ['ctranspath', 'phikon', 'uni', 'kaiko', 'prov-gigapath', 'virchow-class', 'virchow2-class', 'panakeia']
    model_handles = []
    for m in model_order:
        handle = mlines.Line2D([], [], color='black', marker=markers[m], linestyle='None',
                              markersize=6, label=model_labels[m])
        model_handles.append(handle)
        
    legend2 = ax.legend(
        handles=model_handles, 
        title='Model', 
        loc='lower right', 
        bbox_to_anchor=(1.02, 0.15), # Fine tune position
        frameon=True,
        fontsize=9,
        title_fontsize=10,
        handletextpad=0.1,
        borderpad=0.6
    )
    
    # 6. Add Figure Label "c"
    # Positioned in the top left, outside the axes usually, or top-left corner of axes
    ax.text(-0.12, 1.02, 'c', transform=ax.transAxes, fontsize=24, fontweight='bold', va='top', ha='right')

    # 7. Save Output
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    generate_plot(output_file)