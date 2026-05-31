import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

def generate_chart(output_filename='output_fixed_step.png'):
    # 1. Load Source Data
    csv_data = """Task|CONCH|Virchow2|ProvGigaPath|DinoSSLPath
KIEL_STAD_M_STATUS|0.544224|0.526274|0.534376|0.506792
DACHS_CRC_KRAS|0.534721|0.547883|0.5362|0.533338
IEO_BRCA_N_STATUS|0.575481|0.55847|0.549081|0.573873
CPTAC_LUAD_KRAS|0.581757|0.522889|0.552111|0.540034
CPTAC_CRC_Sidedness|0.613278|0.583832|0.571655|0.60289
CPTAC_CRC_N_STATUS|0.630026|0.615013|0.616402|0.594841
CPTAC_CRC_PIK3CA|0.617665|0.636782|0.619964|0.602783
DACHS_CRC_N_STATUS|0.648021|0.632989|0.622209|0.62096
KIEL_STAD_N_STATUS|0.631522|0.616924|0.657943|0.632616
CPTAC_CRC_KRAS|0.674286|0.613441|0.628008|0.637022
CPTAC_BRCA_PIK3CA|0.675417|0.610655|0.626444|0.633569
CPTAC_BRCA_ERBB2|0.688275|0.66186|0.562938|0.620216
DACHS_CRC_M_STATUS|0.675269|0.697332|0.63174|0.662344
DACHS_CRC_CIMP|0.671484|0.698943|0.692594|0.65021
BERN_STAD_N_STATUS|0.71867|0.598758|0.498635|0.627987
BERN_STAD_LAUREN|0.720555|0.729027|0.644662|0.705261
DACHS_CRC_Sidedness|0.707539|0.723064|0.706909|0.736509
DACHS_CRC_BRAF|0.708614|0.725489|0.741302|0.649243
CPTAC_CRC_BRAF|0.708571|0.724835|0.763956|0.753407
CPTAC_LUAD_STK11|0.727652|0.766667|0.748611|0.737374
CPTAC_LUAD_EGFR|0.711846|0.701634|0.769281|0.718056
CPTAC_LUAD_TP53|0.781961|0.752157|0.732478|0.719857
BERN_STAD_MSI|0.738697|0.795687|0.790903|0.685307
KIEL_STAD_LAUREN|0.795917|0.794557|0.711356|0.806003
CPTAC_BRCA_PGR|0.800114|0.796057|0.779371|0.806571
KIEL_STAD_MSI|0.731109|0.813374|0.778738|0.677917
DACHS_CRC_MSI|0.828881|0.862416|0.816061|0.833579
KIEL_STAD_EBV|0.87855|0.862767|0.877741|0.837932
CPTAC_BRCA_ESR1|0.820932|0.894659|0.817351|0.852485
CPTAC_CRC_MSI|0.916667|0.92284|0.888272|0.850309
NSCLC_Subtyping|0.99268|0.983386|0.986583|0.97072"""

    df = pd.read_csv(io.StringIO(csv_data), sep='|')
    models = ['CONCH', 'Virchow2', 'ProvGigaPath', 'DinoSSLPath']

    # 2. Logic to determine Scale per Axis
    
    # RULE: Fixed Step = 0.06
    # Outer Edge (Top) = Max Value
    # Inner Edge (Bottom, 5th ring) = Top - (4 * Step)
    
    FIXED_STEP = 0.06
    
    df['data_max'] = df[models].max(axis=1)
    
    axis_tops = []
    axis_bottoms = []
    
    for idx, row in df.iterrows():
        dmax = row['data_max']
        
        # Determine Top (Visual Radius 1.0)
        top = dmax
        
        # Determine Bottom (Visual Radius 0.2)
        # We have 5 rings: 1.0, 0.8, 0.6, 0.4, 0.2
        # The gap is 4 steps.
        bottom = top - (4 * FIXED_STEP)
        
        axis_tops.append(top)
        axis_bottoms.append(bottom)
        
    df['axis_top'] = axis_tops
    df['axis_bottom'] = axis_bottoms 

    # 3. Colors
    colors = {
        'CONCH': '#8B2323',        
        'Virchow2': '#D67A5C',     
        'ProvGigaPath': '#6CA6CD', 
        'DinoSSLPath': '#27408B'   
    }
    cat_colors = {
        'Morphology': '#4B0082',   
        'Biomarkers': '#B05075',   
        'Prognosis': '#8B3A3A'     
    }

    def get_category(task_name):
        task_upper = task_name.upper()
        if 'N_STATUS' in task_upper or 'M_STATUS' in task_upper:
            return 'Prognosis'
        if 'SUBTYPING' in task_upper or 'SIDEDNESS' in task_upper or 'LAUREN' in task_upper:
            return 'Morphology'
        return 'Biomarkers'

    def format_label(task_name):
        name = task_name.replace('_', ' ')
        parts = name.split(' ')
        if len(parts) > 2:
            return f"{' '.join(parts[:2])}\n{' '.join(parts[2:])}"
        elif len(parts) == 2 and len(name) > 10:
             return f"{parts[0]}\n{parts[1]}"
        return name

    # 4. Plot Setup
    categories = list(df['Task'])
    N = len(categories)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += [angles[0]] # Close loop
    
    fig, ax = plt.subplots(figsize=(14, 14), subplot_kw=dict(polar=True))
    ax.set_theta_offset(np.pi / 2) 
    ax.set_theta_direction(-1) 
    ax.grid(False)
    ax.spines['polar'].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])

    # 5. Draw Custom Grid (5 Rings)
    grid_radii = [0.2, 0.4, 0.6, 0.8, 1.0]
    
    def get_poly_coords(r):
        return [(angle, r) for angle in angles]

    # Draw from outside in
    reversed_radii = sorted(grid_radii, reverse=True)
    for i, r in enumerate(reversed_radii):
        poly_coords = get_poly_coords(r)
        c = '#FFFFFF' if i % 2 == 0 else '#F0F0F5'
        
        # Here we correctly unpack because poly_coords is [(angle, r), ...]
        ax.fill([a for a, _ in poly_coords], [r]*len(poly_coords), color=c, zorder=-5+i)
        ax.plot([a for a, _ in poly_coords], [r]*len(poly_coords), color='#D0D0E0', lw=0.8, zorder=-5+i)

    # Center hole (fill white inside 0.2)
    # FIX: angles is just [0.0, 0.2, ...], so we use it directly instead of iterating [a for a,_ in angles]
    ax.fill(angles, [0.2]*len(angles), color='white', zorder=0)

    # Axis Lines
    for angle in angles[:-1]:
        ax.plot([angle, angle], [0.2, 1.0], color='#E0E0E0', linewidth=0.8, zorder=1)

    # 6. Plot Data
    def normalize_value(val, row_idx):
        top = df.loc[row_idx, 'axis_top']
        bottom = df.loc[row_idx, 'axis_bottom'] 
        
        # Clamp logic: If value < bottom, clamp to visual bottom (0.2)
        if val <= bottom:
            return 0.2
        
        # Linear map
        # Value=Bottom -> r=0.2
        # Value=Top    -> r=1.0
        # Denom = Top - Bottom = 4 * 0.06 = 0.24
        
        ratio = (val - bottom) / (top - bottom)
        r = 0.2 + (0.8 * ratio)
        return r

    for model in models:
        values_mapped = []
        for i in range(len(df)):
            val = df.loc[i, model]
            r = normalize_value(val, i)
            values_mapped.append(r)
        
        values_mapped += [values_mapped[0]]
        
        ax.plot(angles, values_mapped, color=colors[model], linewidth=2, label=model, zorder=10)
        ax.scatter(angles, values_mapped, color=colors[model], s=15, zorder=11)

    # 7. Labels
    for i, (angle, task_name) in enumerate(zip(angles[:-1], categories)):
        # Category Box
        cat = get_category(task_name)
        label_text = format_label(task_name)
        
        deg = np.degrees(angle)
        norm_angle = (np.degrees(np.pi/2) - deg) % 360
        ha = 'right' if 90 < norm_angle <= 270 else 'left'
            
        ax.text(angle, 1.08, label_text, 
                horizontalalignment=ha, verticalalignment='center',
                size=8, color='white', weight='bold',
                bbox=dict(boxstyle="square,pad=0.4", fc=cat_colors[cat], ec="none", alpha=0.9))

        # Axis Numbers
        # Top Label = Max Value
        dmax = df.loc[i, 'axis_top']
        dmin_visible = df.loc[i, 'axis_bottom']
        
        # Outer Label (Max)
        ax.text(angle, 1.02, f"{dmax:.2f}", color='#333333', fontsize=6, weight='bold',
                ha='center', va='center', rotation=np.degrees(angle)-90 if ha=='left' else np.degrees(angle)+90)
        
        # Inner Label (Min visible) - Optional, helps verify step logic
        ax.text(angle, 0.13, f"{dmin_visible:.2f}", color='#777777', fontsize=5, 
                ha='center', va='center', rotation=np.degrees(angle)-90 if ha=='left' else np.degrees(angle)+90)

    # Title & Legend
    plt.title("Four best foundation models (Fixed Step=0.06)", size=16, y=1.10)
    plt.figtext(0.02, 0.95, "a", size=24, weight='bold')

    legend_lines = [Line2D([0], [0], color=colors[m], lw=2, label=m) for m in models]
    fig.legend(handles=legend_lines, loc='lower left', bbox_to_anchor=(0.02, 0.02), frameon=False)
    
    legend_cats = [Patch(facecolor=c, label=k) for k, c in cat_colors.items()]
    fig.legend(handles=legend_cats, loc='lower right', bbox_to_anchor=(0.98, 0.02), frameon=False)

    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        generate_chart(sys.argv[1])
    else:
        generate_chart()