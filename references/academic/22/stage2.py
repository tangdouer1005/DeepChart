import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats

def generate_chart(output_filename):
    # ---------------------------------------------------------
    # 1. Source Data Embedding
    # ---------------------------------------------------------
    # We reconstruct the CSV content based on the provided Markdown table.
    # We include the raw data points and the correlation stats.
    
    csv_content = """Model,Task Category,AUROC,k_WSIs,k_Patients,k_Sites
bioptimus,Morphology,0.7467894276890517,500,333,nan
ctranspath,Morphology,0.7245662906836026,32,13,25
hibou,Morphology,0.7273914889097874,nan,nan,nan
phikon,Morphology,0.6986905923455256,6,5.6,13
prov-gigapath,Morphology,0.7242330131938731,171,30,31
uni,Morphology,0.7351347723197759,100,nan,20
virchow-class,Morphology,0.7300469326931298,1488,120,17
hibou-l,Morphology,0.7297320720088225,1139,306,nan
virchow2-class,Morphology,0.762773096016989,3135,225,175
panakeia,Morphology,0.7306335682076608,6,nan,2
kaiko,Morphology,0.7073485188270819,29,11,25
dinosslpath,Morphology,0.764276572755652,37,nan,nan
bioptimus,Biomarker,0.7046859564606631,500,333,nan
ctranspath,Biomarker,0.6865689130621666,32,13,25
hibou,Biomarker,0.6840318931145523,nan,nan,nan
phikon,Biomarker,0.6655231079066909,6,5.6,13
prov-gigapath,Biomarker,0.7222276213474471,171,30,31
uni,Biomarker,0.7120236484959361,100,nan,20
virchow-class,Biomarker,0.6850684143619094,1488,120,17
hibou-l,Biomarker,0.6854885628643554,1139,306,nan
virchow2-class,Biomarker,0.732159659734404,3135,225,175
panakeia,Biomarker,0.706014841052465,6,nan,2
kaiko,Biomarker,0.6807236915312719,29,11,25
dinosslpath,Biomarker,0.7020635797745987,37,nan,nan
bioptimus,Prognosis,0.5857513036006027,500,333,nan
ctranspath,Prognosis,0.5770248615268212,32,13,25
hibou,Prognosis,0.5700799404528647,nan,nan,nan
phikon,Prognosis,0.5897553541124554,6,5.6,13
prov-gigapath,Prognosis,0.5871979448905298,171,30,31
uni,Prognosis,0.5721758498408054,100,nan,20
virchow-class,Prognosis,0.5873006733060928,1488,120,17
hibou-l,Prognosis,0.5754285617170372,1139,306,nan
virchow2-class,Prognosis,0.6065370877164761,3135,225,175
panakeia,Prognosis,0.5866993918324305,6,nan,2
kaiko,Prognosis,0.5543899668068984,29,11,25
dinosslpath,Prognosis,0.602773354053987,37,nan,nan
"""
    
    # ---------------------------------------------------------
    # 2. Data Processing
    # ---------------------------------------------------------
    df = pd.read_csv(io.StringIO(csv_content))
    
    # Filter for the categories present in the chart
    target_categories = ['Morphology', 'Biomarker', 'Prognosis']
    df = df[df['Task Category'].isin(target_categories)]
    
    # The X-axis is "Pretraining Dataset (k Anatomic Tissue Sites)"
    # We must drop rows where this value is NaN to plot them
    df_plot = df.dropna(subset=['k_Sites']).copy()
    
    # Ensure numeric types
    df_plot['k_Sites'] = pd.to_numeric(df_plot['k_Sites'])
    df_plot['AUROC'] = pd.to_numeric(df_plot['AUROC'])

    # ---------------------------------------------------------
    # 3. Visualization Setup
    # ---------------------------------------------------------
    # Set style
    sns.set_theme(style="whitegrid")
    plt.rcParams['font.family'] = 'sans-serif'
    
    # Create figure
    fig, ax = plt.subplots(figsize=(7, 6))
    
    # Define Colors (matching the image)
    # Morphology: Dark Purple, Biomarker: Rose/Pink, Prognosis: Brown/Red
    palette = {
        'Morphology': '#563668', 
        'Biomarker': '#BC6C93', 
        'Prognosis': '#8E4D56'
    }
    
    # Define Stats for Legend (Extracted from the "Correlation Statistics" table in source)
    # Morphology: r=0.744... -> 0.74, p=0.034... -> 0.034
    # Biomarker: r=0.606... -> 0.61, p=0.110... -> 0.11
    # Prognosis: r=0.579... -> 0.58, p=0.131... -> 0.13
    stats_labels = {
        'Morphology': r'Morphology ($r=0.74, P=0.034$)',
        'Biomarker': r'Biomarker ($r=0.61, P=0.11$)',
        'Prognosis': r'Prognosis ($r=0.58, P=0.13$)'
    }

    # ---------------------------------------------------------
    # 4. Plotting
    # ---------------------------------------------------------
    
    for category in target_categories:
        subset = df_plot[df_plot['Task Category'] == category]
        color = palette[category]
        
        # Calculate stats dynamically
        corr_df = subset[['k_Sites', 'AUROC']].dropna()
        if len(corr_df) > 1:
            r_val, p_val = stats.pearsonr(corr_df['k_Sites'], corr_df['AUROC'])
            
            # Format to match image style
            if category == 'Morphology':
                p_str = f"{p_val:.3f}" # 0.034
            else:
                p_str = f"{p_val:.2f}" # 0.11, 0.13
                
            label = f"{category} ($r={r_val:.2f}, P={p_str}$)"
        else:
            label = category
        
        # Plot Regression Line (ci=None removes the shaded confidence interval to match image)
        sns.regplot(
            data=subset,
            x='k_Sites',
            y='AUROC',
            color=color,
            label=label,
            ci=None,
            scatter_kws={'s': 80, 'alpha': 0.9, 'edgecolor': 'none'},
            line_kws={'linewidth': 2},
            ax=ax
        )

    # ---------------------------------------------------------
    # 5. Styling and Formatting
    # ---------------------------------------------------------
    
    # Axis Limits
    ax.set_xlim(-5, 185)
    ax.set_ylim(0.50, 0.85)
    
    # Axis Labels
    ax.set_xlabel("Pretraining dataset (k anatomic tissue sites)", fontsize=12, labelpad=10)
    ax.set_ylabel("Average downstream performance\nby task type (AUROC)", fontsize=12, labelpad=10)
    
    # Ticks
    ax.set_xticks(np.arange(0, 176, 25))
    ax.set_yticks(np.arange(0.50, 0.86, 0.05))
    
    # Legend
    # Positioned top right, no frame (or very light), matching font size
    ax.legend(loc='upper right', frameon=True, framealpha=0.8, fontsize=10, handletextpad=0.5)
    
    # Grid styling
    ax.grid(True, color='#E0E0E0', linestyle='-', linewidth=1)
    
    # Remove top and right spines for cleaner look
    sns.despine(left=False, bottom=False, right=False, top=False)
    # Actually, the image has a full box frame. Let's keep the spines but make them light gray?
    # The image shows a standard box. We will ensure the border is visible.
    for spine in ax.spines.values():
        spine.set_edgecolor('#D0D0D0')

    # ---------------------------------------------------------
    # 6. Save Output
    # ---------------------------------------------------------
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    # Handle command line argument for output filename
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        output_file = "output.png"
        
    generate_chart(output_file)