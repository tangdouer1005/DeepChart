import pandas as pd
import io
import json
import os

def process_data(output_filename='bench/ground_truth_code/nature_2_output/83.json'):
    # 1. Source Data Loading
    csv_data = """
| Extended Figure 3 a)   | Unnamed: 1   | Unnamed: 2   | Unnamed: 3     | Unnamed: 4     | Unnamed: 5     |
|:-----------------------|:-------------|:-------------|:---------------|:---------------|:---------------|
| Type                   | PM_size      | Season       | OP_v_AA_median | OP_v_AA_Q1     | OP_v_AA_Q3     |
| nan                    | nan          | nan          | nmol min-1 m-3 | nmol min-1 m-3 | nmol min-1 m-3 |
| Traffic                | PM10         | Cold         | 3.55           | 2.27           | 5.18           |
| Traffic                | PM10         | Warm         | 2.45           | 1.69           | 3.25           |
| Urban                  | PM10         | Cold         | 1.68           | 1.04           | 2.77           |
| Urban                  | PM10         | Warm         | 0.77           | 0.46           | 1.14           |
| Industrial             | PM10         | Cold         | 1.34           | 0.76           | 2.43           |
| Industrial             | PM10         | Warm         | 0.49           | 0.33           | 0.74           |
| Suburban               | PM10         | Cold         | 3.41           | 1.69           | 5.91           |
| Suburban               | PM10         | Warm         | 0.42           | 0.3            | 0.59           |
| Rural                  | PM10         | Cold         | 0.78           | 0.37           | 1.85           |
| Rural                  | PM10         | Warm         | 0.34           | 0.18           | 0.54           |
| Traffic                | PM2.5        | Cold         | 1.63           | 1.11           | 2.21           |
| Traffic                | PM2.5        | Warm         | 0.9            | 0.7            | 1.19           |
| Urban                  | PM2.5        | Cold         | 1.01           | 0.65           | 1.69           |
| Urban                  | PM2.5        | Warm         | 0.46           | 0.32           | 0.73           |
| Suburban               | PM2.5        | Cold         | 0.86           | 0.44           | 1.44           |
| Suburban               | PM2.5        | Warm         | 0.24           | 0.18           | 0.32           |
| Rural                  | PM2.5        | Cold         | 0.46           | 0.24           | 0.83           |
| Rural                  | PM2.5        | Warm         | 0.21           | 0.1            | 0.3            |
| Urban                  | PM1          | Cold         | 0.84           | 0.54           | 1.46           |
| Urban                  | PM1          | Warm         | 0.35           | 0.23           | 0.5            |
| Rural                  | PM1          | Cold         | 0.52           | 0.29           | 1.02           |
| Rural                  | PM1          | Warm         | 0.23           | 0.13           | 0.34           |
"""
    # Strip leading/trailing whitespace from the data string
    csv_data = csv_data.strip()

    # Parse the markdown table
    # header=2 corresponds to the line starting with "| Type | PM_size ..."
    df = pd.read_csv(io.StringIO(csv_data), sep="|", header=2, skipinitialspace=True)

    # Clean column names: remove whitespace
    df.columns = [c.strip() for c in df.columns]
    
    # Keep only relevant columns
    target_cols = ['Type', 'PM_size', 'Season', 'OP_v_AA_median', 'OP_v_AA_Q1', 'OP_v_AA_Q3']
    # Filter columns that match target_cols
    df = df[[c for c in df.columns if c in target_cols]]

    df_raw = df.copy()

    # Clean string data: strip whitespace from all string columns
    # This is crucial to handle " nan " vs "nan"
    for col in ['Type', 'PM_size', 'Season']:
        df[col] = df[col].astype(str).str.strip()

    # Filter out the unit row. The unit row has Type="nan"
    df = df[df['Type'] != 'nan']
    
    # Convert numeric columns, coercing errors to NaN (handles any remaining non-numeric text)
    numeric_cols = ['OP_v_AA_median', 'OP_v_AA_Q1', 'OP_v_AA_Q3']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop any rows that failed numeric conversion (safety check)
    df = df.dropna(subset=numeric_cols)

    return df_raw, df

if __name__ == "__main__":
    raw_df, processed_df = process_data()
    
    final_output = {
        "scr_data": raw_df.to_dict(orient='records'),
        "der_data": processed_df.to_dict(orient='records')
    }
    
    output_filename = 'bench/ground_truth_code/nature_1_output/83.json'
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    with open(output_filename, 'w') as f:
        json.dump(final_output, f, indent=4)
    print(f"Data saved to {output_filename}")