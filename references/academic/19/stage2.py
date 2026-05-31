import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import numpy as np
from scipy import stats

# -----------------------------------------------------------------------------
# 1. Data Loading
# ---------------------------------------------------------

# Summary Data
summary_data = {
    'Model': ['CONCH', 'Virchow2', 'ProvGigaPath', 'DinoSSLPath', 'H-optimus-0', 'UNI', 'Panakeia*', 'Virchow', 'CTransPath', 'Hibou-L', 'BiomedCLIP', 'Kaiko', 'Phikon', 'PLIP'],
    'Above 0.7': [17, 16, 15, 13, 14, 13, 12, 11, 9, 14, 10, 11, 10, 7],
    '0.6 - 0.7': [10, 9, 9, 13, 6, 10, 12, 8, 12, 4, 13, 9, 10, 12],
    'Below 0.6': [4, 6, 7, 5, 11, 8, 7, 12, 10, 13, 8, 11, 11, 12]
}
df_summary = pd.DataFrame(summary_data)

# Breakdown Data
breakdown_data = {
    'Model': ['BiomedCLIP', 'CONCH', 'CTransPath', 'DinoSSLPath', 'H-optimus-0', 'Hibou-L', 'Kaiko', 'PLIP', 'Panakeia*', 'Phikon', 'ProvGigaPath', 'UNI', 'Virchow', 'Virchow2'],
    "('Above 0.7', 'Morphology')": [2, 4, 2, 4, 2, 3, 1, 2, 3, 2, 3, 2, 2, 4],
    "('Above 0.7', 'Biomarker')":  [8, 12, 7, 9, 12, 11, 10, 5, 9, 8, 12, 11, 9, 12],
    "('Above 0.7', 'Prognosis')":  [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    "('0.6 - 0.7', 'Morphology')": [2, 1, 2, 1, 3, 1, 3, 2, 1, 2, 1, 3, 2, 0],
    "('0.6 - 0.7', 'Biomarker')":  [6, 5, 8, 8, 2, 2, 5, 9, 8, 5, 4, 5, 4, 5],
    "('0.6 - 0.7', 'Prognosis')":  [5, 4, 2, 4, 1, 1, 1, 1, 3, 3, 4, 2, 2, 4],
    "('Below 0.6', 'Morphology')": [1, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1],
    "('Below 0.6', 'Biomarker')":  [5, 2, 4, 2, 5, 6, 4, 5, 2, 6, 3, 3, 6, 2],
    "('Below 0.6', 'Prognosis')":  [2, 2, 5, 3, 6, 6, 6, 6, 4, 4, 3, 5, 5, 3]
}
df_breakdown = pd.DataFrame(breakdown_data)

# Ensure the order matches the summary table (which matches the image order)
order = df_summary['Model'].tolist()
df_breakdown = df_breakdown.set_index('Model').reindex(order).reset_index()

# ---------------------------------------------------------
# 2. Configuration & Styling
# ---------------------------------------------------------

# Colors based on the image
COLORS = {
    'Above 0.7': '#331052',   # Dark Indigo/Purple
    '0.6 - 0.7': '#7A4B85',   # Medium Purple
    'Below 0.6': '#D8BFD8'    # Thistle/Light Lavender
}

# Hatch patterns for task types
HATCHES = {
    'Morphology': '++',   # Checkered/Grid
    'Biomarker': 'oo',    # Circles
    'Prognosis': '//'     # Diagonal
}

# Manual label mapping for center text to match image line breaks
MODEL_LABELS = {
    'ProvGigaPath': 'Giga-\nPath',
    'DinoSSLPath': 'Dino-\nSSLPath',
    'H-optimus-0': 'H-opti-\nmus-0',
    'Panakeia*': 'Pana-\nkeia*',
    'CTransPath': 'CTrans-\nPath',
    'BiomedCLIP': 'Biomed-\nCLIP',
}

# Groups and Subgroups order
GROUPS = ['Above 0.7', '0.6 - 0.7', 'Below 0.6']
SUBGROUPS = ['Morphology', 'Biomarker', 'Prognosis']

# ---------------------------------------------------------
# 3. Plotting Logic
# ---------------------------------------------------------

def create_chart(output_filename='output.png'):
    # Setup grid: 3 rows, 5 columns
    fig, axes = plt.subplots(3, 5, figsize=(18, 11))
    axes = axes.flatten()

    # Iterate through models
    for i, model_name in enumerate(order):
        ax = axes[i]
        
        # Get data for this model
        row_summary = df_summary[df_summary['Model'] == model_name].iloc[0]
        row_breakdown = df_breakdown[df_breakdown['Model'] == model_name].iloc[0]

        # Prepare data lists
        outer_sizes = []
        outer_colors = []
        outer_labels = []
        
        inner_sizes = []
        inner_colors = []
        inner_hatches = []
        inner_labels = []

        # Build data in specific order: >0.7, 0.6-0.7, <0.6
        for group in GROUPS:
            # Outer Ring Data
            val = row_summary[group]
            outer_sizes.append(val)
            outer_colors.append(COLORS[group])
            outer_labels.append(str(val) if val > 0 else "")

            # Inner Ring Data
            for subgroup in SUBGROUPS:
                col_name = f"('{group}', '{subgroup}')"
                sub_val = row_breakdown[col_name]
                inner_sizes.append(sub_val)
                inner_colors.append(COLORS[group]) # Same base color
                inner_hatches.append(HATCHES[subgroup])
                inner_labels.append(str(sub_val) if sub_val > 0 else "")

        # --- Plotting ---
        
        # Start angle: 90 degrees (12 o'clock), Clockwise
        start_angle = 90
        
        # 1. Outer Ring (Solid)
        wedges_out, texts_out = ax.pie(
            outer_sizes, 
            radius=1.2, 
            colors=outer_colors, 
            startangle=start_angle,
            counterclock=False,
            wedgeprops=dict(width=0.3, edgecolor='white', linewidth=1.5)
        )

        # Label placement for Outer Ring
        for w, label in zip(wedges_out, outer_labels):
            if label == "": continue
            ang = (w.theta2 - w.theta1)/2. + w.theta1
            y = np.sin(np.deg2rad(ang)) * 1.05
            x = np.cos(np.deg2rad(ang)) * 1.05
            
            # Text color logic
            c = w.get_facecolor()
            brightness = (c[0]*299 + c[1]*587 + c[2]*114) / 1000
            txt_color = 'white' if brightness < 0.6 else 'black'
            
            ax.text(x, y, label, ha='center', va='center', 
                    fontsize=11, fontweight='normal', color=txt_color)

        # 2. Inner Ring (Hatched)
        wedges_in, texts_in = ax.pie(
            inner_sizes,
            radius=0.9,
            colors=inner_colors,
            startangle=start_angle,
            counterclock=False,
            wedgeprops=dict(width=0.3, edgecolor='white', linewidth=0.5)
        )

        # Apply hatches manually
        for w, hatch in zip(wedges_in, inner_hatches):
            w.set_hatch(hatch * 3) # Increase density
            w.set_edgecolor('white') # White hatch lines

        # Label placement for Inner Ring
        for w, label in zip(wedges_in, inner_labels):
            if label == "": continue
            ang = (w.theta2 - w.theta1)/2. + w.theta1
            r_lbl = 0.75
            y = np.sin(np.deg2rad(ang)) * r_lbl
            x = np.cos(np.deg2rad(ang)) * r_lbl
            
            c = w.get_facecolor()
            brightness = (c[0]*299 + c[1]*587 + c[2]*114) / 1000
            txt_color = 'white' if brightness < 0.6 else 'black'
            
            # Skip label if slice is too small
            if (w.theta2 - w.theta1) < 5:
                continue 

            ax.text(x, y, label, ha='center', va='center', 
                    fontsize=9, color=txt_color)

        # 3. Center Text (Model Name)
        display_name = MODEL_LABELS.get(model_name, model_name)
        ax.text(0, 0, display_name, ha='center', va='center', fontsize=11, fontweight='normal')

        ax.set_aspect('equal')

    # ---------------------------------------------------------
    # 4. Legend (Last Subplot)
    # ---------------------------------------------------------
    
    ax_leg = axes[14]
    ax_leg.axis('off')
    
    # AUROC Group (Circles)
    auroc_handles = []
    auroc_labels = ['>0.7', '0.6–0.7', '<0.6']
    for g, l in zip(GROUPS, auroc_labels):
        patch = mpatches.Circle((0,0), radius=1, facecolor=COLORS[g])
        auroc_handles.append(patch)

    # Task Types (Rectangles with Hatch)
    task_handles = []
    task_labels = ['Morphology', 'Biomarker', 'Prognosis']
    legend_base_color = COLORS['Above 0.7'] 
    
    for t in task_labels:
        patch = mpatches.Patch(
            facecolor=legend_base_color, 
            edgecolor='white', 
            hatch=HATCHES[t]*3, 
            label=t
        )
        task_handles.append(patch)

    # 1. AUROC Legend
    leg1 = ax_leg.legend(
        auroc_handles, auroc_labels, 
        title="AUROC group",
        loc='upper left', 
        bbox_to_anchor=(0.1, 0.9),
        frameon=False,
        handletextpad=0.5,
        labelspacing=0.8
    )
    leg1._legend_box.align = "left"
    leg1.get_title().set_fontweight('bold')

    # 2. Task Legend
    ax_leg.add_artist(leg1)
    
    leg2 = ax_leg.legend(
        task_handles, task_labels, 
        title="Task types",
        loc='upper left', 
        bbox_to_anchor=(0.1, 0.45),
        frameon=False,
        handletextpad=0.5,
        labelspacing=0.8
    )
    leg2._legend_box.align = "left"
    leg2.get_title().set_fontweight('bold')

    # ---------------------------------------------------------
    # 5. Final Touches
    # ---------------------------------------------------------
    
    fig.text(0.02, 0.95, 'f', fontsize=24, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    create_chart(output_file)