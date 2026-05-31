import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io

def generate_chart(output_filename):
    # 1. Data Preparation
    # The data is provided in a Markdown table format where rows are Task Types and columns are Models.
    # We reconstruct this exactly to ensure data integrity.
    
    data = {
        'Task Type': ['Morphology', 'Biomarker', 'Prognosis'],
        'CONCH':        [0.765994, 0.726168, 0.631888],
        'Virchow2':     [0.762773, 0.732160, 0.606537],
        'ProvGigaPath': [0.724233, 0.722228, 0.587198],
        'DinoSSLPath':  [0.764277, 0.702064, 0.602773],
        'H-optimus-0':  [0.746789, 0.704686, 0.585751],
        'UNI':          [0.735135, 0.712024, 0.572176],
        'Panakeia*':    [0.730634, 0.706015, 0.586699],
        'Virchow':      [0.730047, 0.685068, 0.587301],
        'CTransPath':   [0.724566, 0.686569, 0.577025],
        'Hibou-L':      [0.729732, 0.685489, 0.575429],
        'Hibou-B':      [0.727391, 0.684032, 0.570080],
        'BiomedCLIP':   [0.733166, 0.667362, 0.605194],
        'Kaiko':        [0.707349, 0.680724, 0.554390],
        'Phikon':       [0.698691, 0.665523, 0.589755],
        'PLIP':         [0.698386, 0.651622, 0.567466]
    }

    # Create DataFrame
    df = pd.DataFrame(data)

    # Transform data for plotting (Melt to Long Format)
    # We want 'Model' on X-axis, 'Score' on Y-axis, grouped by 'Task Type'
    df_melted = df.melt(id_vars='Task Type', var_name='Model', value_name='AUROC')

    # 2. Plot Configuration
    # Set style
    sns.set_theme(style="white")
    plt.rcParams['font.family'] = 'sans-serif'
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6), dpi=150)

    # Define Colors based on the image
    # Morphology: Dark Purple/Indigo
    # Biomarker: Mauve/Rose
    # Prognosis: Dark Brown/Red
    custom_palette = ["#482759", "#A6537E", "#7E3339"]

    # Create Bar Plot
    # Note: The order of models on X-axis should match the input column order
    model_order = [k for k in data.keys() if k != 'Task Type']
    
    sns.barplot(
        data=df_melted,
        x='Model',
        y='AUROC',
        hue='Task Type',
        palette=custom_palette,
        ax=ax,
        edgecolor=None,
        width=0.75  # Adjust bar width to match image tightness
    )

    # 3. Styling and Layout
    
    # Title
    ax.set_title("Average AUROC scores across all tasks grouped by task type", fontsize=14, pad=10, color='black')

    # Axis Labels
    ax.set_ylabel("Average AUROC score", fontsize=12, color='black')
    ax.set_xlabel("Results", fontsize=14, color='black', labelpad=10)

    # Y-Axis Limits and Ticks
    # The chart starts at 0.50 and goes up to roughly 0.82
    ax.set_ylim(0.50, 0.82)
    
    # Grid
    ax.yaxis.grid(True, color='#d9d9d9', linestyle='-', linewidth=0.8)
    ax.set_axisbelow(True) # Ensure grid is behind bars

    # X-Axis Ticks Rotation
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right', fontsize=11)
    
    # Y-Axis Tick styling
    ax.tick_params(axis='y', labelsize=11, colors='#333333')
    
    # Legend
    # Located top right, no frame
    ax.legend(
        title=None, 
        loc='upper right', 
        frameon=False, 
        fontsize=11,
        handletextpad=0.5,
        borderaxespad=0.5
    )

    # Remove top and right spines for cleaner look
    sns.despine(left=False, bottom=False, right=False, top=False)
    # Actually, the image has a full box frame, so let's keep spines but make them subtle if needed.
    # Looking closely at the image, there is a box around the plot area.
    for spine in ax.spines.values():
        spine.set_edgecolor('#333333')
        spine.set_linewidth(0.8)

    # 4. Save Output
    plt.tight_layout()
    plt.savefig(output_filename, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    # Handle command line argument for output filename
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        output_file = "output.png"
    
    generate_chart(output_file)