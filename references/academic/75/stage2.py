import sys
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as lines
from scipy import stats

def generate_chart(output_filename='output.png'):
    # 1. Source Data (Embedded exactly as provided)
    csv_data = """|
Unnamed: 0   | Unnamed: 1   | Unnamed: 2   | Unnamed: 3   |   Unnamed: 4 |   Unnamed: 5 |   Unnamed: 6 |   Unnamed: 7 |   Unnamed: 8 |   Unnamed: 9 |   Unnamed: 10 |   Unnamed: 11 |   Unnamed: 12 | Unnamed: 13   | Unnamed: 14   | Unnamed: 15   | Unnamed: 16   | Unnamed: 17   | Unnamed: 18   | Unnamed: 19   | Unnamed: 20   | Unnamed: 21   | Unnamed: 22   | Unnamed: 23   | Unnamed: 24         | Unnamed: 25         | Unnamed: 26         | Unnamed: 27         | Unnamed: 28         | Unnamed: 29         | Unnamed: 30         | Unnamed: 31         | Unnamed: 32         | Unnamed: 33         | Unnamed: 34         | Unnamed: 35         | Unnamed: 36         | Unnamed: 37         |
|:-------------|:-------------|:-------------|:-------------|-------------:|-------------:|-------------:|-------------:|-------------:|-------------:|--------------:|--------------:|--------------:|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|:--------------------|
| nan          | NTSR1        | nan          | nan          |    nan       |    nan       |    nan       |    nan       |    nan       |    nan       |     nan       |     nan       |     nan       | No NTSR1      | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 |
| nan          | nan          | nan          | nan          |    nan       |    nan       |    nan       |    nan       |    nan       |    nan       |     nan       |     nan       |     nan       | 3/6/2024      | 3/6/2024      | 3/6/2024      | 3/7/2024      | 3/7/2024      | 3/7/2024      | 3/8/2024      | 3/8/2024      | 3/8/2024      | 6-8-23        | 6-8-23        | 2024-01-25 00:00:00 | 2024-01-25 00:00:00 | 2024-01-25 00:00:00 | 2024-01-26 00:00:00 | 2023-06-29 00:00:00 | 2023-06-29 00:00:00 | 2023-06-29 00:00:00 | 2023-11-22 00:00:00 | 2023-11-22 00:00:00 | 2023-11-22 00:00:00 | 2023-03-17 00:00:00 | 2023-03-17 00:00:00 | 2023-03-23 00:00:00 | 2023-03-23 00:00:00 |
| G15          | -0.09861     | 0.023013*    | 0.015358*    |     -0.1157  |     -0.13439 |     -0.1263  |     -0.119   |     -0.12425 |     -0.12537 |     nan       |     nan       |     nan       | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.03635143578 | 0.02834705032 | 0.0239758348        | 0.02936297897       | 0.03280815393       | 0.02272429095       | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 |
| Gi1          | -0.06814     | -0.06494     | -0.05948     |     -0.12041 |     -0.09415 |     -0.08036 |     -0.10172 |     -0.10296 |     -0.09427 |     nan       |     nan       |     nan       | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | -0.05627221819      | -0.003265948046     | 0.012646862         | 0.02237109425       | 0.03457729744       | 0.003834766583      | -0.01269434146      |
| Gi2          | -0.06814     | -0.06494     | -0.05948     |     -0.12041 |     -0.09415 |     -0.08036 |     -0.10172 |     -0.10296 |     -0.09427 |     nan       |     nan       |     nan       | 0.026585829   | -0.00090738   | 0.007091      | -0.00817      | -0.03506      | -0.04762      | 0.0306        | 0.023158      | -0.00673827   | nan           | nan           | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 |
| GoA          | -0.10739     | -0.13261     | -0.10043     |     -0.12215 |     -0.13214 |     -0.14922 |     -0.08009 |     -0.10627 |     -0.10338 |     nan       |     nan       |     nan       | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan                 | nan                 | nan                 | nan                 | 0.046413            | 0.040247            | 0.050125            | -0.01948815829      | -0.009848719921     | -0.0003642223716    | nan                 | nan                 | nan                 | nan                 |
| GoB          | -0.10066     | -0.12493     | -0.10246     |     -0.11339 |     -0.15058 |     -0.13409 |     -0.17886 |     -0.19844 |     -0.17703 |      -0.14779 |      -0.18754 |      -0.17204 | -0.0059671    | -0.0809716    | -0.05614      | -0.05503      | -0.05067      | -0.04166      | -0.07838      | -0.06805      | -0.02149      | nan           | nan           | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 |
| Gg           | -0.05587     | -0.03747     | -0.02696     |     -0.06502 |     -0.06803 |     -0.05858 |     -0.04931 |     -0.03871 |     -0.04315 |      -0.04863 |      -0.07383 |      -0.04347 | 0.028911      | 0.011637      | 0.021725      | 0.033632      | 0.02368       | 0.011402      | 0.0698347     | 0.0629408     | 0.02384818    | nan           | nan           | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 |
| G12          | -0.10272     | -0.14475     | -0.10265     |     -0.12409 |     -0.14208 |     -0.15277 |     -0.20006 |     -0.23637 |     -0.2368  |     nan       |     nan       |     nan       | -0.05611      | -0.00916      | -0.01579454   | -0.01273      | -0.01917      | -0.04146      | -0.01826      | -0.00963      | -0.0203       | nan           | nan           | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | 0.02153082363       | 0.02811099579       | 0.04487437074       | nan                 | nan                 | nan                 | nan                 |
| G13          | -0.18362     | -0.18632     | -0.15875     |     -0.27634 |     -0.24043 |     -0.24637 |     -0.28347 |     -0.29985 |     -0.26862 |     nan       |     nan       |     nan       | -0.04172175   | -0.02928817   | -0.05098181   | -0.01676      | -0.0028       | -0.04314      | -0.07779      | -0.05963      | -0.05236      | nan           | nan           | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 | nan                 |
"""

    # 2. Data Processing
    # Manual parsing to avoid pandas ParserError with markdown tables
    data_lines = csv_data.strip().split('\n')
    
    # Filter out separator lines (start with |: or |-)
    data_lines = [l for l in data_lines if not l.strip().startswith('|:')]
    
    # Process header to count columns (though we might not need names)
    # The first line is header
    header_line = data_lines[0]
    # Split by |
    headers = [h.strip() for h in header_line.split('|')]
    # Remove empty first/last if they exist (markdown side pipes)
    if headers[0] == '': headers.pop(0)
    if headers[-1] == '': headers.pop(-1)
    
    # Process data rows
    rows = []
    for line in data_lines[1:]:
        vals = [v.strip() for v in line.split('|')]
        # Remove empty first/last
        if vals[0] == '': vals.pop(0)
        if vals[-1] == '': vals.pop(-1)
        rows.append(vals)
        
    df = pd.DataFrame(rows)
    
    # Extract relevant rows (Protein names start at index 2 in the provided data)
    # Row 0 is "nan | NTSR1..."
    # Row 1 is Dates
    # Row 2 is Data (G15...)
    data_rows = df.iloc[2:].copy()
    
    # Define groups
    proteins = ['G15', 'Gi1', 'Gi2', 'GoA', 'GoB', 'Gg', 'G12', 'G13']
    
    # Containers for plotting data
    plot_data = []
    
    for _, row in data_rows.iterrows():
        protein_name = row.iloc[0].strip()
        if protein_name not in proteins:
            continue
            
        # Extract raw values
        ntsr1_raw = row.iloc[1:13].values
        no_ntsr1_raw = row.iloc[13:].values
        
        def clean_and_convert(val_list):
            cleaned = []
            for v in val_list:
                s = str(v).strip()
                if s == 'nan' or s == '':
                    continue
                if '*' in s:
                    continue 
                try:
                    # The Y-axis is (-Delta Net BRET), so we invert the sign of the raw data
                    val = -1 * float(s)
                    cleaned.append(val)
                except ValueError:
                    continue
            return cleaned

        vals_ntsr1 = clean_and_convert(ntsr1_raw)
        vals_no_ntsr1 = clean_and_convert(no_ntsr1_raw)
        
        plot_data.append({
            'protein': protein_name,
            'ntsr1': vals_ntsr1,
            'no_ntsr1': vals_no_ntsr1
        })

    # 3. Plotting Setup
    fig, ax = plt.subplots(figsize=(10, 5.5))
    
    # Styling constants
    bar_width = 0.35
    color_ntsr1 = '#9932CC' # Dark Orchid / Purple
    color_no_ntsr1_edge = '#9932CC'
    color_no_ntsr1_face = 'white'
    
    indices = np.arange(len(proteins))
    
    # Helper to calculate stars
    def get_star(v1, v2):
        if not v1 or not v2 or len(v1) < 2 or len(v2) < 2:
            return ""
        _, p = stats.ttest_ind(v1, v2)
        if p < 0.001: return '***'
        if p < 0.01: return '**'
        if p < 0.05: return '*'
        return ""

    # 4. Draw Bars and Scatters
    for i, item in enumerate(plot_data):
        # NTSR1 Data
        v1 = item['ntsr1']
        mean1 = np.mean(v1) if v1 else 0
        sem1 = np.std(v1, ddof=1) / np.sqrt(len(v1)) if len(v1) > 1 else 0
        
        # No NTSR1 Data
        v2 = item['no_ntsr1']
        mean2 = np.mean(v2) if v2 else 0
        sem2 = np.std(v2, ddof=1) / np.sqrt(len(v2)) if len(v2) > 1 else 0
        
        # Bar 1 (With NTSR1)
        ax.bar(indices[i] - bar_width/2, mean1, bar_width, 
               color=color_ntsr1, label='Cells with NTSR1' if i == 0 else "")
        
        # Error Bar 1
        ax.errorbar(indices[i] - bar_width/2, mean1, yerr=sem1, 
                    fmt='none', ecolor='black', capsize=3, elinewidth=1)
        
        # Scatter 1 (Jittered)
        jitter1 = np.random.uniform(-0.05, 0.05, size=len(v1))
        ax.scatter(np.full(len(v1), indices[i] - bar_width/2) + jitter1, v1, 
                   color='white', edgecolor='gray', s=20, linewidth=0.8, zorder=3)

        # Bar 2 (Without NTSR1)
        ax.bar(indices[i] + bar_width/2, mean2, bar_width, 
               color=color_no_ntsr1_face, edgecolor=color_no_ntsr1_edge, linewidth=1.5,
               label='Cell without NTSR1' if i == 0 else "")
        
        # Error Bar 2
        ax.errorbar(indices[i] + bar_width/2, mean2, yerr=sem2, 
                    fmt='none', ecolor=color_no_ntsr1_edge, capsize=3, elinewidth=1)
        
        # Scatter 2
        jitter2 = np.random.uniform(-0.05, 0.05, size=len(v2))
        ax.scatter(np.full(len(v2), indices[i] + bar_width/2) + jitter2, v2, 
                   color='white', edgecolor=color_no_ntsr1_edge, s=20, linewidth=0.8, zorder=3)

        # Significance Stars
        star_symbol = get_star(v1, v2)
        
        if star_symbol:
            # Find max Y to place the bracket above
            max_y = max(max(v1) if v1 else 0, max(v2) if v2 else 0)
            # Add some padding
            bracket_y = max_y + 0.03
            if bracket_y < 0.05: bracket_y = 0.05
            
            # Specific adjustments for visual match
            if item['protein'] in ['G12', 'G13']:
                bracket_y += 0.02
                
            x1 = indices[i] - bar_width/2
            x2 = indices[i] + bar_width/2
            
            # Draw bracket line
            ax.plot([x1, x1, x2, x2], [bracket_y - 0.01, bracket_y, bracket_y, bracket_y - 0.01], color='black', linewidth=0.8)
            # Draw star
            ax.text((x1 + x2)/2, bracket_y - 0.005, star_symbol, ha='center', va='bottom', fontsize=14, fontweight='bold')

    # 5. Formatting
    ax.set_ylabel('Max SBI-553-induced\nG protein Activation\n(-$\Delta$ Net BRET)', fontsize=12, fontweight='bold')
    ax.set_xticks(indices)
    ax.set_xticklabels(proteins, fontsize=12, fontweight='bold')
    
    # Add horizontal line at y=0
    ax.axhline(0, color='black', linewidth=1)
    
    # Y-axis ticks styling
    ax.tick_params(axis='y', direction='in', length=4)
    ax.tick_params(axis='x', direction='out', length=4)
    
    # Set Y limit to match image
    ax.set_ylim(-0.08, 0.32)

    # Legend
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=color_ntsr1, label='Cells with NTSR1'),
        Patch(facecolor='white', edgecolor=color_no_ntsr1_edge, linewidth=1.5, label='Cell without NTSR1')
    ]
    ax.legend(handles=legend_elements, loc='upper right', frameon=False, ncol=2, fontsize=11, handlelength=1.2)

    # 6. Family Grouping (X-axis annotations)
    families = [
        ('Gq', 0, 0),
        ('Gi/o', 1, 5),
        ('G12/13', 6, 7)
    ]
    
    trans = ax.get_xaxis_transform()
    
    for name, start, end in families:
        line_y = -0.12
        x_start = indices[start] - 0.3
        x_end = indices[end] + 0.3
        line = lines.Line2D([x_start, x_end], [line_y, line_y], transform=trans, color='black', linewidth=1.5, clip_on=False)
        ax.add_artist(line)
        ax.text((x_start + x_end)/2, line_y - 0.05, name, transform=trans, ha='center', va='top', fontsize=12, fontweight='bold')

    ax.text(indices[0] - 1.0, -0.15, 'Family', transform=trans, ha='right', va='top', fontsize=12, fontweight='bold')
    fig.text(0.02, 0.95, 'e', fontsize=24, fontweight='bold')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)
