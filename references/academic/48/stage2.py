import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

def generate_chart(output_filename):
    # 1. Source Data Loading
    # Using the exact data provided in the prompt
    csv_data = """
GO term|piggybac_abs_log10_q_value|human_abs_log10_q_value|sum_abs_log10_q_value|piggybac_marker_size_binned_q|human_marker_size_binned_q|total_marker_size_binned_q
synaptic membrane|10.9683220431953|27.1999010137671|38.1682230569625|40|80|80
postsynapse|13.5690029560099|11.9859107281264|25.5549136841363|40|40|80
neuron differentiation|15.4613873832848|8.00296758756651|23.4643549708513|40|20|80
biological adhesion|8.67189690613437|14.2766853763774|22.9485822825118|20|40|80
neuron to neuron synapse|13.985186921544|7.62842695455214|21.6136138760962|40|20|80
glutamatergic synapse|10.2438761964056|10.0243580040108|20.2682342004164|40|40|80
gated channel activity|1.38980943250208|16.9962913940332|18.3861008265352|10|40|40
regulation of membrane potential|5.61355344651853|12.4308863597106|18.0444398062292|20|40|40
ion channel complex|3.46667759619904|14.3980727256377|17.8647503218367|20|40|40
synapse organization|10.342692521706|6.89491987055633|17.2376123922624|40|20|40
trans-synaptic signaling|3.53762865997199|13.6838452055278|17.2214738654998|20|40|40
modulation of chemical synaptic transmission|6.7627162380012|9.66651296264769|16.4292292006489|20|20|40
cell morphogenesis|11.4391738590977|4.6716762136979|16.1108500727957|40|20|40
regulation of ion transmembrane transport|5.40342991222435|8.93170096109507|14.3351308733194|20|20|40
cell part morphogenesis|10.5347125889337|3.60180433795327|14.136516926887|40|20|40
regulation of nervous system development|8.83646274468904|5.17551645632876|14.0119792010178|20|20|40
central nervous system development|8.83646274468904|4.61984120461526|13.4563039493043|20|20|40
somatodendritic compartment|8.83646274468904|4.32490960269357|13.1613723473826|20|20|40
glutamate receptor activity|3.76126695799075|8.72002068201322|12.481287640004|20|20|40
regulation of synapse structure or activity|6.42566939091866|5.79263196486851|12.2183013557872|20|20|40
"""
    
    # Parse data
    df = pd.read_csv(io.StringIO(csv_data), sep="|")
    
    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Clean string data (remove whitespace)
    df['GO term'] = df['GO term'].str.strip()

    # 2. Data Preparation & Formatting
    # Map raw data labels to the specific formatting seen in the image
    # (Capitalization, abbreviations like "Reg.", spelling adjustments)
    def format_label(label):
        label = label.capitalize() # Start with sentence case
        
        # Specific replacements based on visual inspection of the target chart
        replacements = {
            "Regulation of": "Reg. of",
            "Modulation of": "Mod. of",
            "Neuron to neuron": "Neuron-to-neuron",
            "Trans-synaptic signaling": "Transsynaptic signalling" # Note spelling change in chart
        }
        
        for old, new in replacements.items():
            if label.startswith(old) or old in label:
                label = label.replace(old, new)
        
        return label

    df['display_label'] = df['GO term'].apply(format_label)
    
    # Reverse dataframe to plot top-to-bottom (matplotlib plots index 0 at bottom by default)
    df = df.iloc[::-1].reset_index(drop=True)

    # 3. Plot Configuration
    # Colors extracted to match the image
    color_piggy = '#8c5e4d'   # Brown
    color_somatic = '#da7cb8' # Pink/Magenta
    color_total = '#866bb1'   # Purple

    # Marker size scaling factor
    # The data has 10, 20, 40, 80. In scatter(s=...), s is area. 
    # Visually, 80 needs to be quite large.
    size_factor = 6.5

    fig, ax = plt.subplots(figsize=(7, 8)) # Portrait aspect ratio

    # 4. Plotting
    
    # Create horizontal lines for each row
    # We use a range for y positions
    y_range = range(len(df))
    
    # Draw the horizontal lines (behind the dots)
    # The lines start from a bit left of 0 (visual aesthetic) to the max value
    ax.hlines(y=y_range, xmin=0, xmax=df['sum_abs_log10_q_value'], 
              color='black', linewidth=0.8, zorder=1)

    # Plot "Total" dots (Purple) - Largest, usually furthest right
    ax.scatter(df['sum_abs_log10_q_value'], y_range, 
               s=df['total_marker_size_binned_q'] * size_factor, 
               color=color_total, label='Total', zorder=2, edgecolors='none')

    # Plot "Somatic mutations" dots (Pink)
    ax.scatter(df['human_abs_log10_q_value'], y_range, 
               s=df['human_marker_size_binned_q'] * size_factor, 
               color=color_somatic, label='Somatic mutations', zorder=3, edgecolors='white', linewidth=0.5)

    # Plot "PiggyBac" dots (Brown)
    ax.scatter(df['piggybac_abs_log10_q_value'], y_range, 
               s=df['piggybac_marker_size_binned_q'] * size_factor, 
               color=color_piggy, label='PiggyBac', zorder=4, edgecolors='white', linewidth=0.5)

    # 5. Styling
    
    # Y-axis
    ax.set_yticks(y_range)
    ax.set_yticklabels(df['display_label'])
    ax.tick_params(axis='y', length=0, labelsize=11) # Hide y ticks, keep labels
    
    # X-axis
    ax.set_xlabel(r'$-log_{10}[q \text{ value}]$', fontsize=12)
    ax.set_xlim(-2, 42) # Match the range 0-40 with some padding
    ax.set_xticks([0, 10, 20, 30, 40])
    ax.tick_params(axis='x', labelsize=11)
    
    # Grid
    ax.grid(axis='x', linestyle='-', alpha=1.0, color='black', linewidth=0.5)
    # Ensure grid is behind plot elements
    ax.set_axisbelow(False) 
    # Actually, in the image, grid lines seem to go through everything or are behind. 
    # Standard is behind.
    ax.grid(False) # Turn off default grid to draw specific vertical lines if needed
    # Draw vertical grid lines manually to match the "behind" look exactly
    for x in [0, 10, 20, 30, 40]:
        ax.axvline(x, color='black', linewidth=0.5, zorder=0)

    # Spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False) # The vertical line at 0 handles the visual left edge
    ax.spines['bottom'].set_visible(True)

    # 6. Legend
    # The legend in the image is at the top: "b  PiggyBac  Somatic mutations  Total"
    # We will construct this manually to match the layout.
    
    # Create custom legend handles
    legend_y = 1.02
    
    # "b" label
    fig.text(0.02, legend_y, "b", fontsize=16, fontweight='bold', va='center')
    
    # Custom markers for legend
    # PiggyBac
    fig.text(0.15, legend_y, "PiggyBac", fontsize=11, style='italic', va='center')
    ax.scatter([], [], s=80, color=color_piggy, label='PiggyBac') # Dummy for spacing if using standard legend, but we use text/dots manually
    
    # Draw legend dots manually in figure coordinates to ensure exact placement
    # Note: Figure coordinates (0,0) to (1,1).
    # Adjusting positions based on trial/visual estimation.
    
    # Dot for PiggyBac
    fig.add_artist(plt.Circle((0.13, legend_y), 0.012, color=color_piggy, transform=fig.transFigure, clip_on=False))
    
    # Dot for Somatic
    fig.add_artist(plt.Circle((0.38, legend_y), 0.012, color=color_somatic, transform=fig.transFigure, clip_on=False))
    fig.text(0.40, legend_y, "Somatic mutations", fontsize=11, va='center')
    
    # Dot for Total
    fig.add_artist(plt.Circle((0.76, legend_y), 0.012, color=color_total, transform=fig.transFigure, clip_on=False))
    fig.text(0.78, legend_y, "Total", fontsize=11, va='center')

    # Adjust layout to make room for labels
    plt.tight_layout()
    plt.subplots_adjust(top=0.93, left=0.45) # Leave space for long Y labels and top legend

    # Save
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    generate_chart(output_file)