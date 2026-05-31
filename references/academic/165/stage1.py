import sys
import io
import pandas as pd
import json

def process_data(output_filename):
    # 1. Source Data
    csv_data = """Scenario|Nutrient|Mean difference from observed (%)|95% CI
Red and processed meat (25%)|Free sugars|-0.588834|(-0·56, -0·62)
Red and processed meat (50%)|Free sugars|-0.867064|(-0·83, -0·91)
Dairy (25%)|Free sugars|0.211354|(0·2, 0·22)
Dairy (50%)|Free sugars|0.640388|(0·61, 0·67)
Red and processed meat (25%)|Saturated fat|-0.838248|(-0·8, -0·88)
Red and processed meat (50%)|Saturated fat|-4.70775|(-4·5, -4·92)
Dairy (25%)|Saturated fat|-13.4857|(-12·88, -14·09)
Dairy (50%)|Saturated fat|-33.3778|(-31·89, -34·87)
Red and processed meat (25%)|Sodium|-1.51633|(-1·45, -1·58)
Red and processed meat (50%)|Sodium|-3.18769|(-3·05, -3·33)
Dairy (25%)|Sodium|-1.4256|(-1·36, -1·49)
Dairy (50%)|Sodium|-2.9479|(-2·82, -3·08)
"""
    
    # Load data
    df = pd.read_csv(io.StringIO(csv_data), sep="|")
    
    # Clean data: Remove NaNs if any
    df = df.dropna(how='all')
    
    # Clean CI column: replace middle dot with decimal point
    df['95% CI'] = df['95% CI'].str.replace('·', '.')

    # Add P-values based on the image content (Visual Replication)
    p_values = {
        ('Free sugars', 'Red and processed meat (25%)'): 'P < 0.0001',
        ('Free sugars', 'Red and processed meat (50%)'): 'P < 0.0001',
        ('Free sugars', 'Dairy (25%)'): 'P = 0.08',
        ('Free sugars', 'Dairy (50%)'): 'P = 0.008',
        ('Saturated fat', 'Red and processed meat (25%)'): 'P < 0.0001',
        ('Saturated fat', 'Red and processed meat (50%)'): 'P < 0.0001',
        ('Saturated fat', 'Dairy (25%)'): 'P < 0.0001',
        ('Saturated fat', 'Dairy (50%)'): 'P < 0.0001',
        ('Sodium', 'Red and processed meat (25%)'): 'P < 0.0001',
        ('Sodium', 'Red and processed meat (50%)'): 'P < 0.0001',
        ('Sodium', 'Dairy (25%)'): 'P < 0.0001',
        ('Sodium', 'Dairy (50%)'): 'P < 0.0001',
    }

    # Add p_value column
    df['P-value'] = df.apply(lambda row: p_values.get((row['Nutrient'], row['Scenario']), ""), axis=1)

    # Save to JSON
    data_list = df.to_dict(orient='records')
    output_data = {
        "scr_data": [],
        "der_data": data_list
    }
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/165.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    process_data(output_file)