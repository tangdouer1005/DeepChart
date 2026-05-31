import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from scipy import stats

# -----------------------------------------------------------------------------
# 1. Source Data Embedding
# -----------------------------------------------------------------------------
SOURCE_DATA = """
| Figure 3A: Data points for vision model pretraining diversity correlations.   | Unnamed: 1    | Unnamed: 2                             | Unnamed: 3                   | Unnamed: 4                       | Unnamed: 5                                    |
|:------------------------------------------------------------------------------|:--------------|:---------------------------------------|:-----------------------------|:---------------------------------|:----------------------------------------------|
| nan                                                                           | nan           | nan                                    | nan                          | nan                              | nan                                           |
| Model                                                                         | Task Category | Average Downstream Performance (AUROC) | Pretraining Dataset (k WSIs) | Pretraining Dataset (k Patients) | Pretraining Dataset (k Anatomic Tissue Sites) |
| bioptimus                                                                     | Morphology    | 0.7467894276890517                     | 500                          | 333                              | nan                                           |
| ctranspath                                                                    | Morphology    | 0.7245662906836026                     | 32                           | 13                               | 25                                            |
| hibou                                                                         | Morphology    | 0.7273914889097874                     | nan                          | nan                              | nan                                           |
| phikon                                                                        | Morphology    | 0.6986905923455256                     | 6                            | 5.6                              | 13                                            |
| prov-gigapath                                                                 | Morphology    | 0.7242330131938731                     | 171                          | 30                               | 31                                            |
| uni                                                                           | Morphology    | 0.7351347723197759                     | 100                          | nan                              | 20                                            |
| virchow-class                                                                 | Morphology    | 0.7300469326931298                     | 1488                         | 120                              | 17                                            |
| hibou-l                                                                       | Morphology    | 0.7297320720088225                     | 1139                         | 306                              | nan                                           |
| virchow2-class                                                                | Morphology    | 0.762773096016989                      | 3135                         | 225                              | 175                                           |
| panakeia                                                                      | Morphology    | 0.7306335682076608                     | 6                            | nan                              | 2                                             |
| kaiko                                                                         | Morphology    | 0.7073485188270819                     | 29                           | 11                               | 25                                            |
| dinosslpath                                                                   | Morphology    | 0.764276572755652                      | 37                           | nan                              | nan                                           |
| bioptimus                                                                     | Biomarker     | 0.7046859564606631                     | 500                          | 333                              | nan                                           |
| ctranspath                                                                    | Biomarker     | 0.6865689130621666                     | 32                           | 13                               | 25                                            |
| hibou                                                                         | Biomarker     | 0.6840318931145523                     | nan                          | nan                              | nan                                           |
| phikon                                                                        | Biomarker     | 0.6655231079066909                     | 6                            | 5.6                              | 13                                            |
| prov-gigapath                                                                 | Biomarker     | 0.7222276213474471                     | 171                          | 30                               | 31                                            |
| uni                                                                           | Biomarker     | 0.7120236484959361                     | 100                          | nan                              | 20                                            |
| virchow-class                                                                 | Biomarker     | 0.6850684143619094                     | 1488                         | 120                              | 17                                            |
| hibou-l                                                                       | Biomarker     | 0.6854885628643554                     | 1139                         | 306                              | nan                                           |
| virchow2-class                                                                | Biomarker     | 0.732159659734404                      | 3135                         | 225                              | 175                                           |
| panakeia                                                                      | Biomarker     | 0.706014841052465                      | 6                            | nan                              | 2                                             |
| kaiko                                                                         | Biomarker     | 0.6807236915312719                     | 29                           | 11                               | 25                                            |
| dinosslpath                                                                   | Biomarker     | 0.7020635797745987                     | 37                           | nan                              | nan                                           |
| bioptimus                                                                     | Prognosis     | 0.5857513036006027                     | 500                          | 333                              | nan                                           |
| ctranspath                                                                    | Prognosis     | 0.5770248615268212                     | 32                           | 13                               | 25                                            |
| hibou                                                                         | Prognosis     | 0.5700799404528647                     | nan                          | nan                              | nan                                           |
| phikon                                                                        | Prognosis     | 0.5897553541124554                     | 6                            | 5.6                              | 13                                            |
| prov-gigapath                                                                 | Prognosis     | 0.5871979448905298                     | 171                          | 30                               | 31                                            |
| uni                                                                           | Prognosis     | 0.5721758498408054                     | 100                          | nan                              | 20                                            |
| virchow-class                                                                 | Prognosis     | 0.5873006733060928                     | 1488                         | 120                              | 17                                            |
| hibou-l                                                                       | Prognosis     | 0.5754285617170372                     | 1139                         | 306                              | nan                                           |
| virchow2-class                                                                | Prognosis     | 0.6065370877164761                     | 3135                         | 225                              | 175                                           |
| panakeia                                                                      | Prognosis     | 0.5866993918324305                     | 6                            | nan                              | 2                                             |
| kaiko                                                                         | Prognosis     | 0.5543899668068984                     | 29                           | 11                               | 25                                            |
| dinosslpath                                                                   | Prognosis     | 0.602773354053987                      | 37                           | nan                              | nan                                           |
| bioptimus                                                                     | BRCA          | 0.6646577126903751                     | 500                          | 333                              | nan                                           |
| ctranspath                                                                    | BRCA          | 0.6901946923437127                     | 32                           | 13                               | 25                                            |
| hibou                                                                         | BRCA          | 0.6745796280204613                     | nan                          | nan                              | nan                                           |
| phikon                                                                        | BRCA          | 0.6333019990370683                     | 6                            | 5.6                              | 13                                            |
| prov-gigapath                                                                 | BRCA          | 0.66703719221213                       | 171                          | 30                               | 31                                            |
| uni                                                                           | BRCA          | 0.6884572772690907                     | 100                          | nan                              | 20                                            |
| virchow-class                                                                 | BRCA          | 0.6589119444462541                     | 1488                         | 120                              | 17                                            |
| hibou-l                                                                       | BRCA          | 0.6803628143251778                     | 1139                         | 306                              | nan                                           |
| virchow2-class                                                                | BRCA          | 0.7043400914608242                     | 3135                         | 225                              | 175                                           |
| panakeia                                                                      | BRCA          | 0.7080816433172487                     | 6                            | nan                              | 2                                             |
| kaiko                                                                         | BRCA          | 0.685518762408426                      | 29                           | 11                               | 25                                            |
| dinosslpath                                                                   | BRCA          | 0.6973429041114697                     | 37                           | nan                              | nan                                           |
| bioptimus                                                                     | LUNG          | 0.7393242904896622                     | 500                          | 333                              | nan                                           |
| ctranspath                                                                    | LUNG          | 0.7101566922966756                     | 32                           | 13                               | 25                                            |
| hibou                                                                         | LUNG          | 0.7160297092067347                     | nan                          | nan                              | nan                                           |
| phikon                                                                        | LUNG          | 0.7086469364758765                     | 6                            | 5.6                              | 13                                            |
| prov-gigapath                                                                 | LUNG          | 0.7578128341867243                     | 171                          | 30                               | 31                                            |
| uni                                                                           | LUNG          | 0.7582049929810751                     | 100                          | nan                              | 20                                            |
| virchow-class                                                                 | LUNG          | 0.7174955993098335                     | 1488                         | 120                              | 17                                            |
| hibou-l                                                                       | LUNG          | 0.7132175072231954                     | 1139                         | 306                              | nan                                           |
| virchow2-class                                                                | LUNG          | 0.7453463548176368                     | 3135                         | 225                              | 175                                           |
| panakeia                                                                      | LUNG          | 0.7136461434822977                     | 6                            | nan                              | 2                                             |
| kaiko                                                                         | LUNG          | 0.7311053739265448                     | 29                           | 11                               | 25                                            |
| dinosslpath                                                                   | LUNG          | 0.7372080501195374                     | 37                           | nan                              | nan                                           |
| bioptimus                                                                     | STAD          | 0.6825321397625634                     | 500                          | 333                              | nan                                           |
| ctranspath                                                                    | STAD          | 0.6727500426566878                     | 32                           | 13                               | 25                                            |
| hibou                                                                         | STAD          | 0.6749535218276297                     | nan                          | nan                              | nan                                           |
| phikon                                                                        | STAD          | 0.6650650873334706                     | 6                            | 5.6                              | 13                                            |
| prov-gigapath                                                                 | STAD          | 0.6867942247149665                     | 171                          | 30                               | 31                                            |
| uni                                                                           | STAD          | 0.6769115022211536                     | 100                          | nan                              | 20                                            |
| virchow-class                                                                 | STAD          | 0.6845577051089727                     | 1488                         | 120                              | 17                                            |
| hibou-l                                                                       | STAD          | 0.6762860623850082                     | 1139                         | 306                              | nan                                           |
| virchow2-class                                                                | STAD          | 0.7171710064688561                     | 3135                         | 225                              | 175                                           |
| panakeia                                                                      | STAD          | 0.6830453013043695                     | 6                            | nan                              | 2                                             |
| kaiko                                                                         | STAD          | 0.6679383667204072                     | 29                           | 11                               | 25                                            |
| dinosslpath                                                                   | STAD          | 0.6849769746019573                     | 37                           | nan                              | nan                                           |
| bioptimus                                                                     | CRC           | 0.6725440232616449                     | 500                          | 333                              | nan                                           |
| ctranspath                                                                    | CRC           | 0.6402351975254987                     | 32                           | 13                               | 25                                            |
| hibou                                                                         | CRC           | 0.6362652412414206                     | nan                          | nan                              | nan                                           |
| phikon                                                                        | CRC           | 0.6335703165007269                     | 6                            | 5.6                              | 13                                            |
| prov-gigapath                                                                 | CRC           | 0.6796362735454282                     | 171                          | 30                               | 31                                            |
| uni                                                                           | CRC           | 0.6585192894528652                     | 100                          | nan                              | 20                                            |
| virchow-class                                                                 | CRC           | 0.6476261453717196                     | 1488                         | 120                              | 17                                            |
| hibou-l                                                                       | CRC           | 0.6402117599741689                     | 1139                         | 306                              | nan                                           |
| virchow2-class                                                                | CRC           | 0.6911429496854462                     | 3135                         | 225                              | 175                                           |
| panakeia                                                                      | CRC           | 0.6616418630330357                     | 6                            | nan                              | 2                                             |
| kaiko                                                                         | CRC           | 0.609584221956904                      | 29                           | 11                               | 25                                            |
| dinosslpath                                                                   | CRC           | 0.671341060761758                      | 37                           | nan                              | nan                                           |
| bioptimus                                                                     | All           | 0.6846206269807122                     | 500                          | 333                              | nan                                           |
| ctranspath                                                                    | All           | 0.6679617687834495                     | 32                           | 13                               | 25                                            |
| hibou                                                                         | All           | 0.6652942902224349                     | nan                          | nan                              | nan                                           |
| phikon                                                                        | All           | 0.6537638545400627                     | 6                            | 5.6                              | 13                                            |
| prov-gigapath                                                                 | All           | 0.692060499542083                      | 171                          | 30                               | 31                                            |
| uni                                                                           | All           | 0.6841727139324936                     | 100                          | nan                              | 20                                            |
| virchow-class                                                                 | All           | 0.6702464274027281                     | 1488                         | 120                              | 17                                            |
| hibou-l                                                                       | All           | 0.6677723544027784                     | 1139                         | 306                              | nan                                           |
| virchow2-class                                                                | All           | 0.7087309235178695                     | 3135                         | 225                              | 175                                           |
| panakeia                                                                      | All           | 0.6830434052858759                     | 6                            | nan                              | 2                                             |
| kaiko                                                                         | All           | 0.6564910484154151                     | 29                           | 11                               | 25                                            |
| dinosslpath                                                                   | All           | 0.6896775599314047                     | 37                           | nan                              | nan                                           |
| nan                                                                           | nan           | nan                                    | nan                          | nan                              | nan                                           |
| nan                                                                           | nan           | nan                                    | nan                          | nan                              | nan                                           |
| Correlation Statistics                                                        | nan           | nan                                    | nan                          | nan                              | nan                                           |
| Correlation Attribute                                                         | Task Category | Pearson r                              | p-value                      | nan                              | nan                                           |
| Pretraining Dataset (k WSIs)                                                  | Morphology    | 0.4859917715943717                     | 0.1296143207884952           | nan                              | nan                                           |
| Pretraining Dataset (k WSIs)                                                  | Biomarker     | 0.4081639994488918                     | 0.2126835810954361           | nan                              | nan                                           |
| Pretraining Dataset (k WSIs)                                                  | Prognosis     | 0.4619022277545125                     | 0.1526384346830376           | nan                              | nan                                           |
| Pretraining Dataset (k WSIs)                                                  | BRCA          | 0.1765554318490269                     | 0.6035453610752683           | nan                              | nan                                           |
| Pretraining Dataset (k WSIs)                                                  | LUNG          | 0.1131317083348493                     | 0.7405010877450119           | nan                              | nan                                           |
| Pretraining Dataset (k WSIs)                                                  | STAD          | 0.8116245228740286                     | 0.002418708048634998         | nan                              | nan                                           |
| Pretraining Dataset (k WSIs)                                                  | CRC           | 0.4191571896468188                     | 0.1994134196676589           | nan                              | nan                                           |
| Pretraining Dataset (k WSIs)                                                  | All           | 0.4871475397521298                     | 0.1285690551314311           | nan                              | nan                                           |
| Pretraining Dataset (k Patients)                                              | Morphology    | 0.7252874859979224                     | 0.04173739156908165          | nan                              | nan                                           |
| Pretraining Dataset (k Patients)                                              | Biomarker     | 0.3454421572318546                     | 0.4019784691794736           | nan                              | nan                                           |
| Pretraining Dataset (k Patients)                                              | Prognosis     | 0.2946265763094684                     | 0.4787114151864745           | nan                              | nan                                           |
| Pretraining Dataset (k Patients)                                              | BRCA          | 0.2232233918032454                     | 0.5951519594960489           | nan                              | nan                                           |
| Pretraining Dataset (k Patients)                                              | LUNG          | 0.1459031917620603                     | 0.7302891577166752           | nan                              | nan                                           |
| Pretraining Dataset (k Patients)                                              | STAD          | 0.4288723182625986                     | 0.2890273881734001           | nan                              | nan                                           |
| Pretraining Dataset (k Patients)                                              | CRC           | 0.4484403385172616                     | 0.2650996317135804           | nan                              | nan                                           |
| Pretraining Dataset (k Patients)                                              | All           | 0.4356237501809864                     | 0.2806569395588059           | nan                              | nan                                           |
| Pretraining Dataset (k Anatomic Tissue Sites)                                 | Morphology    | 0.7443450229025076                     | 0.0341734912075763           | nan                              | nan                                           |
| Pretraining Dataset (k Anatomic Tissue Sites)                                 | Biomarker     | 0.6064670049508223                     | 0.1109335350797595           | nan                              | nan                                           |
| Pretraining Dataset (k Anatomic Tissue Sites)                                 | Prognosis     | 0.5798363630222992                     | 0.1319117723315713           | nan                              | nan                                           |
| Pretraining Dataset (k Anatomic Tissue Sites)                                 | BRCA          | 0.3753378844635153                     | 0.3595443119614016           | nan                              | nan                                           |
| Pretraining Dataset (k Anatomic Tissue Sites)                                 | LUNG          | 0.3692306773102758                     | 0.3680411234622192           | nan                              | nan                                           |
| Pretraining Dataset (k Anatomic Tissue Sites)                                 | STAD          | 0.8641442002931352                     | 0.005647287507666749         | nan                              | nan                                           |
| Pretraining Dataset (k Anatomic Tissue Sites)                                 | CRC           | 0.5866780506706342                     | 0.1263270212792962           | nan                              | nan                                           |
| Pretraining Dataset (k Anatomic Tissue Sites)                                 | All           | 0.689489994353303                      | 0.05849789308106676          | nan                              | nan                                           |
"""

# -----------------------------------------------------------------------------
# 2. Data Processing
# -----------------------------------------------------------------------------
def parse_markdown_lines(lines):
    """
    Parses a list of strings representing a Markdown table into a DataFrame.
    Handles leading/trailing pipes and whitespace robustly.
    """
    headers = None
    rows = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Split by pipe
        parts = line.split('|')
        
        # Remove empty start/end if present (common in markdown | a | b |)
        if len(parts) > 0 and parts[0].strip() == '':
            parts.pop(0)
        if len(parts) > 0 and parts[-1].strip() == '':
            parts.pop(-1)
            
        clean_parts = [p.strip() for p in parts]
        
        # Detect separator line (e.g. :---)
        if not clean_parts:
            continue
        # If all non-empty parts consist only of separator chars
        if all(all(c in '-: ' for c in p) for p in clean_parts if p):
            continue
            
        if headers is None:
            headers = clean_parts
        else:
            # Align lengths
            if len(clean_parts) < len(headers):
                clean_parts += [np.nan] * (len(headers) - len(clean_parts))
            elif len(clean_parts) > len(headers):
                clean_parts = clean_parts[:len(headers)]
            rows.append(clean_parts)
            
    return pd.DataFrame(rows, columns=headers)

def load_and_parse_data(source_text):
    lines = source_text.strip().split('\n')
    
    # Locate sections
    data_header_idx = -1
    stats_header_idx = -1
    
    for i, line in enumerate(lines):
        if "| Model" in line and "Task Category" in line:
            data_header_idx = i
        if "| Correlation Attribute" in line and "Pearson r" in line:
            stats_header_idx = i
            
    if data_header_idx == -1 or stats_header_idx == -1:
        raise ValueError("Could not find headers in source text.")
        
    # Extract lines for Data Points
    # Read from data_header_idx until we hit "Correlation Statistics" or the stats header
    data_lines = []
    for i in range(data_header_idx, len(lines)):
        line = lines[i]
        if "Correlation Statistics" in line or i >= stats_header_idx:
            break
        data_lines.append(line)
        
    # Extract lines for Statistics
    stats_lines = []
    for i in range(stats_header_idx, len(lines)):
        stats_lines.append(lines[i])
    
    df_points = parse_markdown_lines(data_lines)
    df_stats = parse_markdown_lines(stats_lines)
    
    # Convert numeric columns in df_points
    numeric_cols_points = [
        'Average Downstream Performance (AUROC)', 
        'Pretraining Dataset (k WSIs)', 
        'Pretraining Dataset (k Patients)',
        'Pretraining Dataset (k Anatomic Tissue Sites)'
    ]
    for col in numeric_cols_points:
        if col in df_points.columns:
            df_points[col] = pd.to_numeric(df_points[col], errors='coerce')

    # Convert numeric columns in df_stats
    numeric_cols_stats = ['Pearson r', 'p-value']
    for col in numeric_cols_stats:
        if col in df_stats.columns:
            df_stats[col] = pd.to_numeric(df_stats[col], errors='coerce')
            
    # Clean up stats df (remove extra 'nan' columns if any)
    target_cols = ['Correlation Attribute', 'Task Category', 'Pearson r', 'p-value']
    existing_cols = [c for c in target_cols if c in df_stats.columns]
    df_stats = df_stats[existing_cols]

    return df_points, df_stats

# -----------------------------------------------------------------------------
# 3. Visualization
# -----------------------------------------------------------------------------
def generate_plot(df_points, df_stats, output_filename):
    # Filter for the specific categories shown in the chart
    target_categories = ['Morphology', 'Biomarker', 'Prognosis']
    
    # Filter Data Points
    plot_data = df_points[df_points['Task Category'].isin(target_categories)].copy()
    
    # Filter Stats for the specific attribute plotted (k WSIs)
    stats_attr = "Pretraining Dataset (k WSIs)"
    plot_stats = df_stats[
        (df_stats['Correlation Attribute'] == stats_attr) & 
        (df_stats['Task Category'].isin(target_categories))
    ].set_index('Task Category')

    # Define Colors
    palette = {
        'Morphology': '#5D3A75',  # Dark Purple
        'Biomarker': '#B86B87',   # Rose/Pink
        'Prognosis': '#8C464F'    # Brown/Red
    }

    # Setup Figure
    fig, ax = plt.subplots(figsize=(7, 6))
    
    # Plotting Loop
    for category in target_categories:
        subset = plot_data[plot_data['Task Category'] == category]
        color = palette[category]
        
        # Calculate stats dynamically
        corr_df = subset[['Pretraining Dataset (k WSIs)', 'Average Downstream Performance (AUROC)']].dropna()
        
        if len(corr_df) > 1:
            r_val, p_val = stats.pearsonr(corr_df['Pretraining Dataset (k WSIs)'], corr_df['Average Downstream Performance (AUROC)'])
            label_text = f"{category} ($r$ = {r_val:.2f}, $P$ = {p_val:.2f})"
        else:
            label_text = category
        
        # Plot Regression Line and Scatter
        sns.regplot(
            data=subset,
            x='Pretraining Dataset (k WSIs)',
            y='Average Downstream Performance (AUROC)',
            color=color,
            ci=None,
            label=label_text,
            scatter_kws={'s': 80, 'alpha': 0.85, 'edgecolor': 'none'},
            line_kws={'linewidth': 2},
            ax=ax
        )

    # Styling
    ax.set_facecolor('white')
    ax.grid(True, color='#E0E0E0', linestyle='-', linewidth=1)
    
    # Axis Labels
    ax.set_xlabel("Pretraining dataset (k WSIs)", fontsize=12, color='black')
    ax.set_ylabel("Average downstream performance\nby task type (AUROC)", fontsize=12, color='black')
    
    # Axis Limits
    ax.set_xlim(-150, 3300)
    ax.set_ylim(0.50, 0.85)
    
    # Ticks styling
    ax.tick_params(axis='both', which='major', labelsize=10, color='#888888')
    
    # Legend
    legend = ax.legend(loc='upper right', frameon=False, fontsize=10, handletextpad=0.1)
    
    # Add the "a" tag
    ax.text(-0.15, 1.0, 'a', transform=ax.transAxes, 
            fontsize=24, fontweight='bold', va='top', ha='right')

    # Add border (spines)
    for spine in ax.spines.values():
        spine.set_edgecolor('#CCCCCC')
        spine.set_linewidth(1.5)

    plt.tight_layout()
    
    # Save
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

# -----------------------------------------------------------------------------
# 4. Main Execution
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]

    try:
        df_points, df_stats = load_and_parse_data(SOURCE_DATA)
        generate_plot(df_points, df_stats, output_file)
    except Exception as e:
        print(f"Error generating chart: {e}")
        sys.exit(1)