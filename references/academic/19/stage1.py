import sys
import pandas as pd
import json

def compute_data(output_path):
    # 1. Source Data
    summary_data = {
        'Model': ['CONCH', 'Virchow2', 'ProvGigaPath', 'DinoSSLPath', 'H-optimus-0', 'UNI', 'Panakeia*', 'Virchow', 'CTransPath', 'Hibou-L', 'BiomedCLIP', 'Kaiko', 'Phikon', 'PLIP'],
        'Above 0.7': [17, 16, 15, 13, 14, 13, 12, 11, 9, 14, 10, 11, 10, 7],
        '0.6 - 0.7': [10, 9, 9, 13, 6, 10, 12, 8, 12, 4, 13, 9, 10, 12],
        'Below 0.6': [4, 6, 7, 5, 11, 8, 7, 12, 10, 13, 8, 11, 11, 12]
    }
    df_summary = pd.DataFrame(summary_data)

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

    MODEL_LABELS = {
        'ProvGigaPath': 'Giga-\nPath',
        'DinoSSLPath': 'Dino-\nSSLPath',
        'H-optimus-0': 'H-opti-\nmus-0',
        'Panakeia*': 'Pana-\nkeia*',
        'CTransPath': 'CTrans-\nPath',
        'BiomedCLIP': 'Biomed-\nCLIP',
    }

    output_data = {
        "scr_data": {
            "summary_data": summary_data,
            "breakdown_data": breakdown_data
        },
        "der_data": {
            "order": order,
            "summary": df_summary.to_dict(orient='records'),
            "breakdown": df_breakdown.to_dict(orient='records'),
            "model_labels": MODEL_LABELS
        }
    }

    with open(output_path, "w") as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_2_output/19.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compute_data(output_file)
