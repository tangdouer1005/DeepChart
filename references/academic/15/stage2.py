import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

def generate_chart(output_filename='output_chart_b.png'):
    # 1. Source Data
    csv_data = """Task,CONCH,Concat,Avg-Pred,Virchow2
CRC_DACHS_KRAS,0.534721,0.535258,0.549144,0.547883
STAD_Kiel_M_STATUS,0.544224,0.557744,0.537224,0.526274
BRCA_IEO_N_STATUS,0.575481,0.571745,0.574428,0.55847
Lung_CPTAC_KRAS,0.581757,0.599324,0.576014,0.522889
CRC_CPTAC_LEFT_RIGHT,0.613278,0.61947,0.613003,0.583832
CRC_CPTAC_N_STATUS,0.630026,0.611971,0.638095,0.615013
CRC_CPTAC_PIK3CA,0.617665,0.642105,0.645977,0.636782
CRC_DACHS_N_STATUS,0.648021,0.63771,0.649866,0.632989
STAD_Kiel_N_STATUS,0.631522,0.620105,0.654946,0.616924
BRCA_CPTAC_PIK3CA,0.675417,0.662003,0.661682,0.610655
CRC_CPTAC_KRAS,0.674286,0.67493,0.68668,0.613441
BRCA_CPTAC_ERBB2,0.688275,0.651617,0.657008,0.66186
CRC_DACHS_M_STATUS,0.675269,0.678237,0.692091,0.697332
CRC_DACHS_CIMP,0.671484,0.684641,0.686804,0.698943
STAD_Bern_N_STATUS,0.71867,0.594866,0.611224,0.598758
Total,0.708066,0.710943,0.7204,0.705072
CRC_DACHS_LEFT_RIGHT,0.707539,0.731377,0.744267,0.723064
CRC_DACHS_BRAF,0.708614,0.756712,0.75453,0.725489
Lung_CPTAC_EGFR,0.711846,0.761928,0.760948,0.701634
CRC_CPTAC_BRAF,0.708571,0.734359,0.76967,0.724835
Lung_CPTAC_STK11,0.727652,0.759091,0.774495,0.766667
Lung_CPTAC_TP53,0.781961,0.764064,0.771907,0.752157
STAD_Bern_isMSIH,0.738697,0.762577,0.763076,0.795687
STAD_Kiel_isMSIH,0.731109,0.743598,0.774264,0.813374
BRCA_CPTAC_PGR,0.800114,0.807714,0.826743,0.796057
CRC_DACHS_isMSIH,0.828881,0.826826,0.858945,0.862416
STAD_Kiel_EBV,0.87855,0.88245,0.880574,0.862767
BRCA_CPTAC_ESR1,0.820932,0.846125,0.868231,0.894659
CRC_CPTAC_isMSIH,0.916667,0.90607,0.920062,0.92284
Lung_CPTAC_CANCER_TYPE,0.99268,0.992732,0.98971,0.983386
"""
    
    # 2. Load and Prepare Data
    df = pd.read_csv(io.StringIO(csv_data))
    df = df[df['Task'] != 'Total'].copy().reset_index(drop=True)
    
    models = ['CONCH', 'Concat', 'Avg-Pred', 'Virchow2']
    
    # --- SCALING LOGIC START ---
    FIXED_STEP = 0.06
    
    # Calculate Max per row
    df['data_max'] = df[models].max(axis=1)
    
    axis_tops = []
    axis_bottoms = []
    
    for idx, row in df.iterrows():
        dmax = row['data_max']
        
        # Top (Outer Ring, 100%) = Max Value
        top = dmax
        
        # Bottom (Inner Ring, 20%) = Top - 4 * Step
        # This creates 4 intervals of 0.06
        bottom = top - (4 * FIXED_STEP)
        
        axis_tops.append(top)
        axis_bottoms.append(bottom)
        
    df['axis_top'] = axis_tops
    df['axis_bottom'] = axis_bottoms
    # --- SCALING LOGIC END ---

    # 3. Styles & Colors
    # Colors for Models
    colors = {
        'CONCH':    '#9e2a2b', # Dark Red
        'Concat':   '#6d9dc5', # Light Blue
        'Avg-Pred': '#1f4e79', # Dark Blue
        'Virchow2': '#d16045'  # Orange
    }
    
    # Colors for Categories (Backgrounds)
    cat_colors = {
        'Morphology': '#482C3F', # Dark Purple
        'Biomarkers': '#A95C76', # Pink/Mauve
        'Prognosis':  '#7D3C42'  # Brown
    }

    # Helper function for labels (kept from your code)
    def get_label_properties(raw_label):
        text = raw_label.replace('_', ' ')
        text = text.replace('Lung', 'LUAD')
        text = text.replace('LEFT RIGHT', 'sidedness')
        text = text.replace('CANCER TYPE', 'subtyping')
        text = text.replace('isMSIH', 'MSI')
        text = text.replace('N STATUS', 'N-status')
        text = text.replace('M STATUS', 'M-status')
        
        if "DACHS CRC sidedness" not in text and "CRC DACHS sidedness" in text:
            text = "DACHS CRC\nsidedness"
        elif "CPTAC CRC sidedness" not in text and "CRC CPTAC sidedness" in text:
            text = "CPTAC CRC\nsidedness"
        elif "NSCLC subtyping" not in text and "LUAD CPTAC subtyping" in text:
            text = "NSCLC\nsubtyping"
        else:
            words = text.split()
            if len(words) >= 3:
                text = " ".join(words[:-1]) + "\n" + words[-1]
            elif len(words) == 2:
                 text = words[0] + "\n" + words[1]

        if 'sidedness' in text or 'subtyping' in text:
            category = 'Morphology'
        elif 'N-status' in text or 'M-status' in text:
            category = 'Prognosis'
        else:
            category = 'Biomarkers'
            
        return text, cat_colors[category], category

    # 4. Plot Setup
    categories = list(df['Task'])
    N = len(categories)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += [angles[0]] # Close loop
    
    fig, ax = plt.subplots(figsize=(14, 14), subplot_kw=dict(polar=True))
    
    # Orient like Chart A (Clockwise from top/right) or keep Chart B?
    # To match Chart A style:
    ax.set_theta_offset(np.pi / 2) 
    ax.set_theta_direction(-1) # Clockwise
    
    ax.grid(False)
    ax.spines['polar'].set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])

    # 5. Draw Custom Grid (5 Rings)
    # Visual Radii: 0.2, 0.4, 0.6, 0.8, 1.0
    grid_radii = [0.2, 0.4, 0.6, 0.8, 1.0]
    
    def get_poly_coords(r):
        return [(angle, r) for angle in angles]

    # Draw from outside in
    reversed_radii = sorted(grid_radii, reverse=True)
    for i, r in enumerate(reversed_radii):
        poly_coords = get_poly_coords(r)
        # Alternating colors: White / Grey-ish
        c = '#FFFFFF' if i % 2 == 0 else '#F0F0F5'
        
        ax.fill([a for a, _ in poly_coords], [r]*len(poly_coords), color=c, zorder=-5+i)
        ax.plot([a for a, _ in poly_coords], [r]*len(poly_coords), color='#D0D0E0', lw=0.8, zorder=-5+i)

    # Center hole (fill white inside 0.2)
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
        
        # Linear map: Bottom -> 0.2, Top -> 1.0
        # The scale range is (Top - Bottom) = 4 * 0.06 = 0.24
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
        
        ax.plot(angles, values_mapped, color=colors[model], linewidth=2.5, label=model, zorder=10)
        ax.scatter(angles, values_mapped, color=colors[model], s=15, zorder=11)

    # 7. Labels & Axis Numbers
    for i, (angle, raw_label) in enumerate(zip(angles[:-1], categories)):
        # Category Label
        label_text, bg_color, _ = get_label_properties(raw_label)
        
        deg = np.degrees(angle)
        norm_angle = (np.degrees(np.pi/2) - deg) % 360
        ha = 'right' if 90 < norm_angle <= 270 else 'left'
            
        ax.text(angle, 1.08, label_text, 
                horizontalalignment=ha, verticalalignment='center',
                size=8, color='white', weight='bold',
                bbox=dict(boxstyle="square,pad=0.4", fc=bg_color, ec="none", alpha=0.9))

        # Axis Numbers
        # Top Label = Max Value
        dmax = df.loc[i, 'axis_top']
        # dmin = df.loc[i, 'axis_bottom'] # Optional inner label
        
        ax.text(angle, 1.02, f"{dmax:.2f}", color='#333333', fontsize=6, weight='bold',
                ha='center', va='center', rotation=np.degrees(angle)-90 if ha=='left' else np.degrees(angle)+90)
        
        # Optional: Show Min/Step at inner ring
        # ax.text(angle, 0.13, f"{dmin:.2f}", color='gray', fontsize=5, ha='center', va='center', rotation=...)

    # 8. Titles & Legends
    plt.title("Ensembles versus two best foundation models", size=18, y=1.10)
    plt.figtext(0.02, 0.95, "b", size=28, weight='bold')

    # Line Legend (Models)
    legend_lines = [Line2D([0], [0], color=colors[m], lw=3, label=m) for m in models]
    fig.legend(handles=legend_lines, loc='lower left', bbox_to_anchor=(0.02, 0.02), frameon=False, fontsize=10)
    
    # Category Legend (Manual text boxes to match style)
    cat_legend_items = list(cat_colors.items()) # [('Morphology', color), ...]
    start_x = 0.85
    start_y = 0.15
    for i, (cat, color) in enumerate(cat_legend_items):
        fig.text(start_x, start_y - (i * 0.04), cat, 
                 color='white', ha='center',
                 bbox=dict(facecolor=color, edgecolor='none', boxstyle='square,pad=0.4'),
                 fontsize=10)

    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output_chart_b.png"
    generate_chart(output_file)