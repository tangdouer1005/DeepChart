import pandas as pd
import io
import json
import os

def process_data(output_filename='bench/ground_truth_code/nature_2_output/84.json'):
    # 1. Load Source Data
    csv_data = """
| Extended Figure 3 b)   | Unnamed: 1   | Unnamed: 2   | Unnamed: 3      | Unnamed: 4     | Unnamed: 5     |
|:-----------------------|:-------------|:-------------|:----------------|:---------------|:---------------|
| Type                   | PM_size      | Season       | OP_v_DTT_median | OP_v_DTT_Q1    | OP_v_DTT_Q3    |
| nan                    | nan          | nan          | nmol min-1 m-3  | nmol min-1 m-3 | nmol min-1 m-3 |
| Traffic                | PM10         | Cold         | 2.63            | 1.66           | 3.63           |
| Traffic                | PM10         | Warm         | 1.97            | 1.46           | 2.53           |
| Urban                  | PM10         | Cold         | 1.79            | 1.17           | 2.73           |
| Urban                  | PM10         | Warm         | 1.39            | 0.88           | 2.05           |
| Industrial             | PM10         | Cold         | 1.28            | 0.81           | 2.06           |
| Industrial             | PM10         | Warm         | 1.13            | 0.78           | 1.68           |
| Suburban               | PM10         | Cold         | 2.22            | 1.33           | 3.72           |
| Suburban               | PM10         | Warm         | 0.8             | 0.53           | 1.27           |
| Rural                  | PM10         | Cold         | 0.82            | 0.48           | 1.51           |
| Rural                  | PM10         | Warm         | 0.79            | 0.47           | 1.13           |
| Traffic                | PM2.5        | Cold         | 1.45            | 0.89           | 2.03           |
| Traffic                | PM2.5        | Warm         | 0.89            | 0.65           | 1.18           |
| Urban                  | PM2.5        | Cold         | 0.89            | 0.61           | 1.56           |
| Urban                  | PM2.5        | Warm         | 0.70            | 0.44           | 1.14           |
| Suburban               | PM2.5        | Cold         | 0.63            | 0.37           | 1.54           |
| Suburban               | PM2.5        | Warm         | 0.33            | 0.2            | 0.43           |
| Rural                  | PM2.5        | Cold         | 0.45            | 0.24           | 0.88           |
| Rural                  | PM2.5        | Warm         | 0.47            | 0.25           | 0.73           |
| Urban                  | PM1          | Cold         | 0.71            | 0.45           | 1.01           |
| Urban                  | PM1          | Warm         | 0.75            | 0.42           | 1.27           |
| Rural                  | PM1          | Cold         | 0.44            | 0.24           | 0.88           |
| Rural                  | PM1          | Warm         | 0.50            | 0.33           | 0.77           |
"""

    # Parse the markdown table
    df = pd.read_csv(io.StringIO(csv_data), sep="|", header=2, skipinitialspace=True)
    
    # Clean up column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Drop empty columns created by leading/trailing pipes
    df = df.dropna(axis=1, how='all')
    
    # Rename columns to be cleaner
    df = df.rename(columns={
        'Type': 'Type',
        'PM_size': 'PM_size',
        'Season': 'Season',
        'OP_v_DTT_median': 'Median',
        'OP_v_DTT_Q1': 'Q1',
        'OP_v_DTT_Q3': 'Q3'
    })

    df_raw = df.copy()

    # Drop the row containing units (where Type is NaN or 'nan')
    df = df[pd.to_numeric(df['Median'], errors='coerce').notna()]

    # Convert numeric columns
    cols_to_numeric = ['Median', 'Q1', 'Q3']
    for col in cols_to_numeric:
        df[col] = pd.to_numeric(df[col])

    # Clean string columns
    df['Type'] = df['Type'].str.strip()
    df['PM_size'] = df['PM_size'].str.strip()
    df['Season'] = df['Season'].str.strip()
    
    return df_raw, df

if __name__ == "__main__":
    raw_df, processed_df = process_data()
    
    final_output = {
        "scr_data": raw_df.to_dict(orient='records'),
        "der_data": processed_df.to_dict(orient='records')
    }
    
    output_filename = 'bench/ground_truth_code/nature_1_output/84.json'
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    with open(output_filename, 'w') as f:
        json.dump(final_output, f, indent=4)
    print(f"Data saved to {output_filename}")