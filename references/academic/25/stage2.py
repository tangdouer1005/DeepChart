import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

def generate_chart(output_filename='output.png'):
    # 1. Source Data
    # Using the exact markdown table provided in the prompt.
    csv_data = """
| Figure 3D: Average AUROC across 29 tasks for models trained with reduced numbers of patients.   | Unnamed: 1               | Unnamed: 2         |
|:------------------------------------------------------------------------------------------------|:-------------------------|:-------------------|
| nan                                                                                             | nan                      | nan                |
| Model                                                                                           | Downstream Training Size | Average AUROC      |
| 300 patients                                                                                    | bioptimus                | 0.6517158688410827 |
| 150 patients                                                                                    | bioptimus                | 0.5802264312220263 |
| 75 patients                                                                                     | bioptimus                | 0.5470019924276457 |
| 300 patients                                                                                    | conch                    | 0.672942774817434  |
| 150 patients                                                                                    | conch                    | 0.6154008166562007 |
| 75 patients                                                                                     | conch                    | 0.5791498585558393 |
| 300 patients                                                                                    | ctranspath               | 0.6291062922684837 |
| 150 patients                                                                                    | ctranspath               | 0.5710509089724938 |
| 75 patients                                                                                     | ctranspath               | 0.5410367286336112 |
| 300 patients                                                                                    | hibou                    | 0.6379063476106139 |
| 150 patients                                                                                    | hibou                    | 0.5727761195225896 |
| 75 patients                                                                                     | hibou                    | 0.5562067331721074 |
| 300 patients                                                                                    | hibou-l                  | 0.6239549871461666 |
| 150 patients                                                                                    | hibou-l                  | 0.5751085656062501 |
| 75 patients                                                                                     | hibou-l                  | 0.5389014636946619 |
| 300 patients                                                                                    | kaiko                    | 0.6250757455645438 |
| 150 patients                                                                                    | kaiko                    | 0.5800004052945474 |
| 75 patients                                                                                     | kaiko                    | 0.5453298651189457 |
| 300 patients                                                                                    | madeleine                | 0.6574321767991897 |
| 150 patients                                                                                    | madeleine                | 0.6124805203499889 |
| 75 patients                                                                                     | madeleine                | 0.5741346994196119 |
| 300 patients                                                                                    | phikon                   | 0.6057894992309325 |
| 150 patients                                                                                    | phikon                   | 0.5667616625139058 |
| 75 patients                                                                                     | phikon                   | 0.5298242015784663 |
| 300 patients                                                                                    | prism                    | 0.6553326870672026 |
| 150 patients                                                                                    | prism                    | 0.6137751964755708 |
| 75 patients                                                                                     | prism                    | 0.5809407507499376 |
| 300 patients                                                                                    | prov-gigapath            | 0.6540952461683367 |
| 150 patients                                                                                    | prov-gigapath            | 0.595442596902233  |
| 75 patients                                                                                     | prov-gigapath            | 0.5452248273062075 |
| 300 patients                                                                                    | prov-gigapath-slide      | 0.6505149933403137 |
| 150 patients                                                                                    | prov-gigapath-slide      | 0.592498956404845  |
| 75 patients                                                                                     | prov-gigapath-slide      | 0.5471431795435153 |
| 300 patients                                                                                    | uni                      | 0.661658662534097  |
| 150 patients                                                                                    | uni                      | 0.6027280013559551 |
| 75 patients                                                                                     | uni                      | 0.5646607760944191 |
| 300 patients                                                                                    | virchow-class            | 0.6319207545553032 |
| 150 patients                                                                                    | virchow-class            | 0.5653361780348889 |
| 75 patients                                                                                     | virchow-class            | 0.543204342469331  |
| 300 patients                                                                                    | virchow2-class           | 0.6760624066310988 |
| 150 patients                                                                                    | virchow2-class           | 0.6175003942804516 |
| 75 patients                                                                                     | virchow2-class           | 0.5673908442334521 |
| 300 patients                                                                                    | panakeia                 | 0.6421712650668627 |
| 150 patients                                                                                    | panakeia                 | 0.5803004315333413 |
| 75 patients                                                                                     | panakeia                 | 0.5503337091394822 |
| 300 patients                                                                                    | chief                    | 0.6140413449683532 |
| 150 patients                                                                                    | chief                    | 0.5547604174224477 |
| 75 patients                                                                                     | chief                    | 0.5348862707760792 |
| 300 patients                                                                                    | dinosslpath              | 0.6450345007008265 |
| 150 patients                                                                                    | dinosslpath              | 0.5917099194542511 |
| 75 patients                                                                                     | dinosslpath              | 0.554353187518743  |
| 300 patients                                                                                    | biomedclip               | 0.6114886974757219 |
| 150 patients                                                                                    | biomedclip               | 0.5592247241978702 |
| 75 patients                                                                                     | biomedclip               | 0.5518145094797684 |
| 300 patients                                                                                    | plip                     | 0.5968990567399465 |
| 150 patients                                                                                    | plip                     | 0.5499106728461921 |
| 75 patients                                                                                     | plip                     | 0.5356388554287601 |
"""

    # 2. Data Processing
    # Read the markdown table. Skip the first few header/separator lines.
    # The data starts effectively at line 5 (0-indexed) based on the string above.
    df = pd.read_csv(io.StringIO(csv_data), sep='|', skiprows=4, header=None)
    
    # Clean up columns (Markdown tables often have empty first/last columns due to pipes)
    df = df.iloc[:, 1:-1] # Drop first and last empty columns
    df.columns = ['Size', 'Model_ID', 'AUROC']
    
    # Strip whitespace
    df['Size'] = df['Size'].str.strip()
    df['Model_ID'] = df['Model_ID'].str.strip()
    
    # Filter out any remaining header rows or nan rows if they slipped through
    df = df[df['Size'] != 'Model'] # Remove the repeated header row if present
    df = df.dropna()
    df['AUROC'] = pd.to_numeric(df['AUROC'])

    # Map Model IDs to the Display Names shown in the chart image
    # This mapping is derived by comparing the raw data IDs to the X-axis labels in the image.
    name_mapping = {
        'virchow2-class': 'Virchow2',
        'conch': 'CONCH',
        'uni': 'UNI',
        'madeleine': 'MADELEINE',
        'prism': 'PRISM',
        'prov-gigapath': 'ProvGigaPath-T', # T for Tile/Token (Standard)
        'bioptimus': 'H-optimus-O',
        'prov-gigapath-slide': 'ProvGigaPath-S', # S for Slide
        'dinosslpath': 'DinoSSLPath',
        'panakeia': 'Panakeia*',
        'hibou': 'Hibou-B',
        'virchow-class': 'Virchow',
        'ctranspath': 'CTransPath',
        'kaiko': 'Kaiko',
        'hibou-l': 'Hibou-L',
        'chief': 'CHIEF',
        'biomedclip': 'BiomedCLIP',
        'phikon': 'Phikon',
        'plip': 'PLIP'
    }
    
    df['Display_Name'] = df['Model_ID'].map(name_mapping)
    
    # Verify we didn't miss any mappings
    if df['Display_Name'].isnull().any():
        missing = df[df['Display_Name'].isnull()]['Model_ID'].unique()
        print(f"Warning: Missing mappings for: {missing}")

    # Determine Order: Sort by the AUROC of the '300 patients' group descending
    pivot_df = df.pivot(index='Display_Name', columns='Size', values='AUROC')
    # Sort by '300 patients' column
    sorted_indices = pivot_df.sort_values(by='300 patients', ascending=False).index.tolist()

    # 3. Plotting
    # Set style
    sns.set_theme(style="white")
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
    
    fig, ax = plt.subplots(figsize=(10, 6))

    # Define Colors based on the image (Dark Purple, Medium Purple, Light Pinkish-Purple)
    # 300 patients -> Dark
    # 150 patients -> Medium
    # 75 patients -> Light
    palette = {
        '300 patients': '#281E38', # Dark purple/black
        '150 patients': '#6F4C75', # Medium purple
        '75 patients': '#DCCCE0'   # Light lavender/pink
    }
    
    # Ensure the hue order matches the legend in the image
    hue_order = ['300 patients', '150 patients', '75 patients']

    # Create the Bar Plot
    sns.barplot(
        data=df,
        x='Display_Name',
        y='AUROC',
        hue='Size',
        order=sorted_indices,
        hue_order=hue_order,
        palette=palette,
        ax=ax,
        edgecolor=None,
        width=0.8 # Adjust bar width to be tighter
    )

    # 4. Styling and Layout
    
    # Y-Axis
    ax.set_ylim(0.51, 0.69)
    ax.set_ylabel("Average of 29 tasks (AUROC)", fontsize=12, color='black')
    ax.tick_params(axis='y', labelsize=10, color='black')
    
    # Grid lines (Horizontal only, behind bars)
    ax.yaxis.grid(True, color='#D3D3D3', linestyle='-', linewidth=0.8, zorder=0)
    ax.set_axisbelow(True) # Puts grid behind bars

    # X-Axis
    ax.set_xlabel("") # No label for X-axis
    ax.set_xticklabels(sorted_indices, rotation=45, ha='right', fontsize=10, color='black')
    
    # Title
    ax.set_title("Reduced training set for downstream tasks (no. of patients)", fontsize=12, loc='center', pad=10)

    # Legend
    # Remove the legend title ("Size") and position it top right
    ax.legend(title=None, loc='upper right', frameon=False, fontsize=10, handletextpad=0.5)

    # Add the 'd' label in the top left corner
    # Using figure coordinates or axes coordinates to place it outside/corner
    ax.text(-0.1, 1.05, 'd', transform=ax.transAxes, fontsize=24, fontweight='bold', va='top', ha='left')

    # Remove top and right spines
    sns.despine(top=False, right=False, left=False, bottom=False)
    # The image has a box around it, so we keep spines but maybe color them
    for spine in ax.spines.values():
        spine.set_edgecolor('black')
        spine.set_linewidth(0.5)

    # Adjust layout to prevent clipping of rotated labels
    plt.tight_layout()

    # Save
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)