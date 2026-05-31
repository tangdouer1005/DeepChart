import sys
import io
import pandas as pd
import numpy as np
from scipy import stats
import json
import os

def process_data(output_filename):
    # ---------------------------------------------------------
    # 1. Data Preparation
    # ---------------------------------------------------------
    
    raw_data = """
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
    
    parts = raw_data.split("Correlation Statistics")
    
    # --- Process Main Data ---
    main_data_str = parts[0].strip()
    
    lines = [l for l in main_data_str.split('\n') if "|" in l]
    # Find the line with "Model"
    header_idx = next(i for i, l in enumerate(lines) if "Model" in l)
    
    data_rows = []
    headers = [h.strip() for h in lines[header_idx].split('|') if h.strip()]
    
    for line in lines[header_idx+1:]:
        if "nan" in line and "Model" not in line:
            vals = [v.strip() for v in line.split('|') if v.strip()]
            if not vals or all(v == 'nan' for v in vals):
                continue
        
        vals = [v.strip() for v in line.split('|')]
        vals = [v for v in vals if v != '']
        
        if len(vals) == len(headers):
            data_rows.append(vals)
            
    df = pd.DataFrame(data_rows, columns=headers)
    
    # Convert numeric columns
    numeric_cols = [
        'Average Downstream Performance (AUROC)', 
        'Pretraining Dataset (k WSIs)', 
        'Pretraining Dataset (k Patients)', 
        'Pretraining Dataset (k Anatomic Tissue Sites)'
    ]
    
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Filter for target categories
    target_categories = ['Morphology', 'Biomarker', 'Prognosis']
    plot_df = df[df['Task Category'].isin(target_categories)].copy()
    plot_df = plot_df.dropna(subset=['Pretraining Dataset (k Patients)'])

    # Calculate statistics (derived data)
    stats_list = []
    for category in target_categories:
        subset = plot_df[plot_df['Task Category'] == category]
        corr_df = subset[['Pretraining Dataset (k Patients)', 'Average Downstream Performance (AUROC)']].dropna()
        
        if len(corr_df) > 1:
            r_val, p_val = stats.pearsonr(corr_df['Pretraining Dataset (k Patients)'], corr_df['Average Downstream Performance (AUROC)'])
        else:
            r_val, p_val = None, None # JSON uses null for None
        
        stats_list.append({
            "category": category,
            "r": r_val,
            "p": p_val
        })

    # Prepare output data structure
    output_data = {
        "scr_data": {
            "plot_data": plot_df.to_dict(orient='records')
        },
        "der_data": {
            "stats_data": stats_list
        }
    }
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
        
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    # Default output path
    output_file = "bench/ground_truth_code/nature_2_output/21.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    process_data(output_file)
