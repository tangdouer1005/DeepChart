import sys
import io
import pandas as pd
import json

def process_data(output_filename):
    # 1. Source Data
    csv_data = """Country,On track to meet goals,Not on track to meet goals,No data
Germany,33,33,34
France,19,40,41
United Kingdom,29,38,33
Italy,28,40,32
Spain,29,35,36
Poland,30,40,30
Netherlands,25,36,39
Belgium,24,37,39
Sweden,34,31,35
Greece,28,34,38
Portugal,26,38,36
Austria,33,30,37
Czech Republic,27,34,39
Denmark,33,31,36
Ireland,20,38,42
Finland,32,31,37
Hungary,27,33,40
Slovakia,25,35,40
Bulgaria,28,33,39
Croatia,29,34,37
Lithuania,28,31,41
Slovenia,31,31,38
Latvia,28,30,42
Estonia,33,26,41
Cyprus,26,31,43
Luxembourg,23,32,45
Malta,26,29,45
Romania,33,30,37
"""

    # 2. Data Processing
    df = pd.read_csv(io.StringIO(csv_data))

    # Convert to long format for easier plotting of stacked bars
    df_melted = df.melt(id_vars=['Country'], var_name='Status', value_name='Percentage')

    # Save to JSON
    data_list = df_melted.to_dict(orient='records')
    output_data = {
        "scr_data": data_list,
        "der_data": []
    }
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/164.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    process_data(output_file)
