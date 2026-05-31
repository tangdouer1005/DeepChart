import sys
import io
import pandas as pd
import json

def process_data(output_filename):
    # 1. Data Loading
    csv_data = """
Unnamed: 0|Observed diets|Red and processed meat (25%)|Red and processed meat (50%)|Dairy (25%)|Dairy (50%)
Vegetables and fruits|0.468|0.632|0.645|0.6035|0.6275
Whole-grain foods|0.236|0.192|0.184|0.166|0.156
Grain foods ratio|0.282|0.282|0.282|0.282|0.282
Protein foods|0.714|0.802|0.814|0.848|0.866
Plant-based protein foods|0.282|0.624|0.65|0.76|0.794
Beverages|0.788|0.788|0.788|0.546|0.516
Fatty acids ratio|0.514|0.568|0.608|0.634|0.75
Saturated fats|0.712|0.728|0.746|0.788|0.864
Free sugars|0.741|0.737|0.739|0.736|0.734
Sodium|0.51|0.534|0.555|0.534|0.552
"""

    # 2. Process Data
    df = pd.read_csv(io.StringIO(csv_data), sep="|")
    
    # Clean column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Rename the first column to 'Category'
    df.rename(columns={'Unnamed: 0': 'Category'}, inplace=True)
    
    # Clean category names (strip whitespace)
    df['Category'] = df['Category'].str.strip()
    
    # Convert values to percentages (0-100 scale)
    data_cols = df.columns[1:]
    df[data_cols] = df[data_cols] * 100

    # Save to JSON
    data_list = df.to_dict(orient='records')
    output_data = {
        "scr_data": data_list,
        "der_data": []
    }
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/163.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    process_data(output_file)
