import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def generate_chart(output_filename):
    # ---------------------------------------------------------
    # 1. Data Preparation
    # ---------------------------------------------------------
    # Data extracted directly from the provided source table columns.
    # Mapping based on headers:
    # Col 1: Intranodal, WT, Vehicle
    # Col 2: Intranodal, WT, viFSP1
    # Col 3: Intranodal, FSP1 KO, Vehicle
    # Col 4: Intranodal, FSP1 KO, viFSP1
    # Col 5: Subcutaneous, WT, Vehicle
    # Col 6: Subcutaneous, WT, viFSP1
    # Col 7: Subcutaneous, FSP1 KO, Vehicle
    # Col 8: Subcutaneous, FSP1 KO, viFSP1

    raw_data = {
        ('Intranodal', 'WT', 'Vehicle'): [
            1.226013991989289, 0.9137241501300842, 1.2593749169413784, 
            1.3181705861405943, 0.46320361183478104, 1.1517888949997317, 
            0.667723847964141
        ],
        ('Intranodal', 'WT', 'viFSP1'): [
            0.26919108005571524, 0.4740587435691917, 0.03158430764694863, 
            0.1172567421392968, 0.030024832456880545, 0.28110033805784285, 
            0.5876161736753397, 0.18387347551958827, 0.5379202396120939, 
            0.52758427493463
        ],
        ('Intranodal', 'Fsp1 KO', 'Vehicle'): [
            0.7439762627007868, 0.8433562867119107, 0.03158430764694863, 
            0.03158430764694863, 0.03158430764694863, 0.03158430764694863, 
            0.03158430764694863, 0.03158430764694863, 0.03158430764694863
        ],
        ('Intranodal', 'Fsp1 KO', 'viFSP1'): [
            0.6323691635918379, 0.10994497491902819, 0.09440549555672946, 
            0.6810129454065946, 0.25673107068899403, 0.03158430764694863, 
            0.09960901024156425, 0.03656278413979891
        ],
        ('Subcutaneous', 'WT', 'Vehicle'): [
            0.47505561344221175, 0.6275176971758019, 0.8627640623994038, 
            1.07262093290512, 1.5483034001667353, 0.9886672051858337, 
            1.425071088724893
        ],
        ('Subcutaneous', 'WT', 'viFSP1'): [
            0.32442302364590364, 0.5469331491498078, 0.5017894606485539, 
            0.48018662260755507, 0.9407594871142966, 0.29633971719901214, 
            1.6253259886079303, 0.789999228515666
        ],
        ('Subcutaneous', 'Fsp1 KO', 'Vehicle'): [
            1.6476616455742605, 0.31997887263705566, 0.4379039919663494, 
            1.302964816119536, 0.5985279422324202, 1.058976968000909, 
            1.7172092256394702, 1.3238654757477606
        ],
        ('Subcutaneous', 'Fsp1 KO', 'viFSP1'): [
            1.5255694165371587, 1.1622329419433417, 0.6292029253664596, 
            0.806938325207822, 1.9126420748587845
        ]
    }

    # Convert to Long Format DataFrame
    rows = []
    for (loc, geno, treat), values in raw_data.items():
        for v in values:
            rows.append({
                'Location': loc,
                'Genotype': geno,
                'Treatment': treat,
                'Value': v,
                # Create a combined group for x-axis positioning
                'Group': f"{loc}\n{geno}" 
            })
    
    df = pd.DataFrame(rows)

    # Define order for plotting
    # We want: Intranodal WT, Intranodal KO, Subcutaneous WT, Subcutaneous KO
    group_order = [
        ('Intranodal', 'WT'), 
        ('Intranodal', 'Fsp1 KO'), 
        ('Subcutaneous', 'WT'), 
        ('Subcutaneous', 'Fsp1 KO')
    ]
    
    # Create a mapping to ensure correct x-axis order
    df['SortOrder'] = df.apply(lambda x: group_order.index((x['Location'], x['Genotype'])), axis=1)
    df = df.sort_values('SortOrder')

    # ---------------------------------------------------------
    # 2. Plotting Setup
    # ---------------------------------------------------------
    
    # Colors based on image
    # Vehicle: Grey/Black
    # viFSP1: Teal/Blue
    palette = {'Vehicle': '#999999', 'viFSP1': '#6daebf'}
    
    fig, ax = plt.subplots(figsize=(5, 6))
    
    # Boxplot
    # We use a dummy x-variable constructed from Location and Genotype
    x_col = 'SortOrder'
    
    sns.boxplot(
        data=df, 
        x=x_col, 
        y='Value', 
        hue='Treatment', 
        palette=palette,
        width=0.6,
        dodge=True,
        ax=ax,
        linewidth=1.2,
        fliersize=0 # Hide outliers as we will overlay strip plot
    )

    # Stripplot (Individual points)
    sns.stripplot(
        data=df, 
        x=x_col, 
        y='Value', 
        hue='Treatment', 
        palette=palette,
        dodge=True,
        edgecolor='black',
        linewidth=1,
        size=8,
        alpha=0.7,
        ax=ax,
        jitter=True
    )

    # ---------------------------------------------------------
    # 3. Styling and Annotations
    # ---------------------------------------------------------

    # Remove default legend and create a custom one later if needed, 
    # but Seaborn's default is okay, just need to position it.
    handles, labels = ax.get_legend_handles_labels()
    # We only want the first two handles (Boxplot handles), not the stripplot duplicates
    ax.legend(handles[:2], labels[:2], frameon=False, loc='upper left', bbox_to_anchor=(-0.05, 1.15), handletextpad=0.2)

    # Axis Labels
    ax.set_ylabel("End-point tumour volume\n(compared with vehicle)", fontsize=12)
    ax.set_xlabel("")
    
    # Custom X-axis ticks
    # Positions are 0, 1, 2, 3
    ax.set_xticks([0, 1, 2, 3])
    
    # Styled labels: "WT", "Fsp1 KO"
    # Note: "Fsp1" should be italicized. Matplotlib supports mathtext.
    labels = [r"WT", r"$\it{Fsp1}$ KO", r"WT", r"$\it{Fsp1}$ KO"]
    ax.set_xticklabels(labels, fontsize=11)

    # Add "Intranodal" and "Subcutaneous" labels below
    # We use text annotations relative to axes coordinates or data coordinates
    trans = ax.get_xaxis_transform()
    ax.text(0.5, -0.12, "Intranodal", ha="center", va="top", transform=trans, fontsize=11)
    ax.text(2.5, -0.12, "Subcutaneous", ha="center", va="top", transform=trans, fontsize=11)

    # Add lines
    # Dashed line at y=1
    ax.axhline(y=1.0, color='gray', linestyle='--', linewidth=1.5, zorder=0)
    # Dotted line at y=0
    ax.axhline(y=0.0, color='black', linestyle=':', linewidth=1.5, zorder=0)
    # Vertical dotted line separating groups (between 1 and 2)
    ax.axvline(x=1.5, color='black', linestyle=':', linewidth=1.5, zorder=0)

    # Remove top and right spines
    sns.despine()

    # Set Y-axis limits to accommodate p-values
    ax.set_ylim(-0.2, 2.6)
    ax.set_yticks([0, 0.5, 1.0, 1.5, 2.0, 2.5])

    # Title "i"
    ax.text(-0.15, 1.15, "i", transform=ax.transAxes, fontsize=20, fontweight='bold', va='top', ha='right')

    # ---------------------------------------------------------
    # 4. Statistical Significance Annotations
    # ---------------------------------------------------------
    
    # Helper function to draw significance lines
    def draw_sig(x1, x2, y, text, h=0.05):
        ax.plot([x1, x1, x2, x2], [y, y+h, y+h, y], lw=1, c='k')
        ax.text((x1+x2)*.5, y+h, text, ha='center', va='bottom', color='k', fontsize=10)

    # Calculate approximate x-positions of the bars
    # Box width is 0.6. Dodge is True.
    # Center of group is integer i.
    # Left bar (Vehicle) center: i - 0.15
    # Right bar (viFSP1) center: i + 0.15
    
    # Group 0: IN WT
    x_in_wt_veh = 0 - 0.15
    x_in_wt_vi = 0 + 0.15
    
    # Group 1: IN KO
    x_in_ko_veh = 1 - 0.15
    x_in_ko_vi = 1 + 0.15
    
    # Group 2: SubQ WT
    x_sq_wt_veh = 2 - 0.15
    x_sq_wt_vi = 2 + 0.15
    
    # Group 3: SubQ KO
    x_sq_ko_veh = 3 - 0.15
    x_sq_ko_vi = 3 + 0.15

    # P-values from source data
    
    # 1. IN: WT Vehicle vs WT viFSP1 (P = 0.0001)
    draw_sig(x_in_wt_veh, x_in_wt_vi, 1.5, "P = 0.0001")
    
    # 2. IN: WT Vehicle vs KO Vehicle (P = 2.1 x 10^-5)
    # This spans across groups. Needs to be higher.
    draw_sig(x_in_wt_veh, x_in_ko_veh, 1.9, r"$P = 2.1 \times 10^{-5}$")
    
    # 3. IN: WT viFSP1 vs KO Vehicle (P = 0.9015)
    # This is tricky, it connects the inner bars.
    draw_sig(x_in_wt_vi, x_in_ko_veh, 2.25, "P = 0.9015")
    
    # 4. IN: KO Vehicle vs KO viFSP1 (P = 0.997)
    draw_sig(x_in_ko_veh, x_in_ko_vi, 1.25, "P = 0.997")

    # 5. SubQ: WT Vehicle vs WT viFSP1 (P = 0.623)
    draw_sig(x_sq_wt_veh, x_sq_wt_vi, 1.7, "P = 0.623")
    
    # 6. SubQ: WT Vehicle vs KO Vehicle (P = 0.9993)
    draw_sig(x_sq_wt_veh, x_sq_ko_veh, 2.2, "P = 0.9993")
    
    # 7. SubQ: WT viFSP1 vs KO Vehicle (P = 0.4516)
    draw_sig(x_sq_wt_vi, x_sq_ko_veh, 2.5, "P = 0.4516")
    
    # 8. SubQ: KO Vehicle vs KO viFSP1 (P = 0.9653)
    draw_sig(x_sq_ko_veh, x_sq_ko_vi, 2.0, "P = 0.9653")

    # Adjust layout to prevent clipping
    plt.tight_layout()
    
    # Save
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    generate_chart(output_file)