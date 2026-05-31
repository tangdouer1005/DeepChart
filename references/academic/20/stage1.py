import sys
import pandas as pd
import numpy as np
from scipy import stats
import json

def parse_markdown_lines(lines):
    headers = None
    rows = []
    
    for line in lines:
        line = line.strip()
        if not line: continue
        parts = line.split('|')
        if len(parts) > 0 and parts[0].strip() == '': parts.pop(0)
        if len(parts) > 0 and parts[-1].strip() == '': parts.pop(-1)
        clean_parts = [p.strip() for p in parts]
        if not clean_parts: continue
        if all(all(c in '-: ' for c in p) for p in clean_parts if p): continue
            
        if headers is None:
            headers = clean_parts
        else:
            if len(clean_parts) < len(headers):
                clean_parts += [np.nan] * (len(headers) - len(clean_parts))
            elif len(clean_parts) > len(headers):
                clean_parts = clean_parts[:len(headers)]
            rows.append(clean_parts)
    return pd.DataFrame(rows, columns=headers)

def load_and_parse_data(source_text):
    lines = source_text.strip().split('\n')
    data_header_idx = -1
    stats_header_idx = -1
    for i, line in enumerate(lines):
        if "| Model" in line and "Task Category" in line: data_header_idx = i
        if "| Correlation Attribute" in line and "Pearson r" in line: stats_header_idx = i
            
    data_lines = []
    for i in range(data_header_idx, len(lines)):
        line = lines[i]
        if "Correlation Statistics" in line or (stats_header_idx != -1 and i >= stats_header_idx): break
        data_lines.append(line)
        
    df_points = parse_markdown_lines(data_lines)
    
    numeric_cols = [
        'Average Downstream Performance (AUROC)', 
        'Pretraining Dataset (k WSIs)', 
        'Pretraining Dataset (k Patients)',
        'Pretraining Dataset (k Anatomic Tissue Sites)'
    ]
    for col in numeric_cols:
        if col in df_points.columns:
            df_points[col] = pd.to_numeric(df_points[col], errors='coerce')
            
    return df_points

def compute_data(output_path):
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
| Correlation Statistics                                                        | nan           | nan                                    | nan                          | nan                              | nan                                           |
| Correlation Attribute                                                         | Task Category | Pearson r                              | p-value                      | nan                              | nan                                           |
| Pretraining Dataset (k WSIs)                                                  | Morphology    | 0.4859917715943717                     | 0.1296143207884952           | nan                              | nan                                           |
"""
    
    df_points = load_and_parse_data(SOURCE_DATA)
    
    target_categories = ['Morphology', 'Biomarker', 'Prognosis']
    plot_data = df_points[df_points['Task Category'].isin(target_categories)].copy()
    
    # Calculate stats
    stats_results = {}
    for category in target_categories:
        subset = plot_data[plot_data['Task Category'] == category]
        corr_df = subset[['Pretraining Dataset (k WSIs)', 'Average Downstream Performance (AUROC)']].dropna()
        
        if len(corr_df) > 1:
            r_val, p_val = stats.pearsonr(corr_df['Pretraining Dataset (k WSIs)'], corr_df['Average Downstream Performance (AUROC)'])
            stats_results[category] = {'r': r_val, 'p': p_val}
        else:
            stats_results[category] = {'r': None, 'p': None}

    output_data = {
        "scr_data": {
            "points": plot_data.to_dict(orient='records')
        },
        "der_data": {
            "stats": stats_results
        }
    }

    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_2_output/20.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compute_data(output_file)
