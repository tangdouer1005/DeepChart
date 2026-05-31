import sys
import io
import pandas as pd
import json
import numpy as np

def compile_data(output_filename):
    # 1. Source Data
    csv_data = """
Unnamed: 0|Unnamed: 1|central estimate of country/region|low|high|Unnamed: 5|Unnamed: 6|Unnamed: 7|Percentile value of cities on map|Unnamed: 9|Unnamed: 10|Unnamed: 11|Unnamed: 12|Unnamed: 13|Unnamed: 14|Unnamed: 15|Unnamed: 16|Unnamed: 17|Unnamed: 18|Unnamed: 19
China|S1|0.154|0.114|0.254|nan|nan|Percentile (%)|China-S1|China-S2|China-S3|EU27-S1|EU27-S2|EU27-S3|United States-S1|United States-S2|United States-S3|India-S1|India-S2|India-S3
nan|S2|0.294|0.199|0.394|nan|nan|10|0.026|0.049|0.073|0.007|0.013|0.02|0.006|0.011|0.017|0.021|0.04|0.06
nan|S3|0.439|0.297|0.588|nan|nan|25|0.04|0.077|0.115|0.021|0.04|0.06|0.018|0.035|0.053|0.042|0.08|0.12
nan|nan|nan|nan|nan|nan|nan|50|0.076|0.144|0.216|0.056|0.109|0.162|0.064|0.127|0.189|0.094|0.179|0.268
EU27|S1|0.067|0.05|0.113|nan|nan|75|0.235|0.449|0.67|0.139|0.269|0.401|0.211|0.418|0.624|0.223|0.427|0.637
nan|S2|0.13|0.087|0.176|nan|nan|90|0.397|0.757|1.13|0.328|0.636|0.95|0.592|1.17|1.747|0.726|1.393|2.079
nan|S3|0.194|0.13|0.263|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan
nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan
United States|S1|0.044|0.033|0.075|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan
nan|S2|0.087|0.057|0.119|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan
nan|S3|0.13|0.085|0.178|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan
nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan
India|S1|0.376|0.278|0.623|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan
nan|S2|0.721|0.486|0.97|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan
nan|S3|1.076|0.725|1.448|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan|nan
"""

    # Read CSV
    df = pd.read_csv(io.StringIO(csv_data), sep="|")
    
    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]

    # --- Process Bar Chart Data (Left side of table) ---
    # Extract relevant columns
    bar_cols = ['Unnamed: 0', 'Unnamed: 1', 'central estimate of country/region', 'low', 'high']
    df_bars = df[bar_cols].copy()
    df_bars.columns = ['Region', 'Scenario', 'Central', 'Low', 'High']

    # Clean Region before filling
    df_bars['Region'] = df_bars['Region'].astype(str).str.strip()
    df_bars['Region'] = df_bars['Region'].replace({'nan': np.nan, 'NaN': np.nan})

    # Forward fill the Region column
    df_bars['Region'] = df_bars['Region'].ffill()

    # Drop rows where Scenario or Central estimate is NaN (spacer rows)
    df_bars = df_bars.dropna(subset=['Scenario', 'Central'])
    
    # Clean Scenario and Central (remove NaN string if any)
    df_bars = df_bars[df_bars['Scenario'].astype(str).str.strip() != 'nan']

    # Create a composite label for the X-axis
    df_bars['Scenario'] = df_bars['Scenario'].astype(str).str.strip()
    df_bars['Label'] = df_bars['Region'] + '-' + df_bars['Scenario']
    
    # Fix US label to match chart image (United States -> US)
    df_bars['Label'] = df_bars['Label'].str.replace('United States', 'US')
    
    # Ensure numeric types
    for col in ['Central', 'Low', 'High']:
        df_bars[col] = pd.to_numeric(df_bars[col], errors='coerce')

    # --- Process Scatter/Percentile Data (Right side of table) ---
    # The scatter data is in columns 8 to 19 (indices). 
    # The headers for these columns are actually in the first row of data (index 0) in the raw CSV read.
    # The values (10%, 25%, etc.) are in rows 1 to 5.
    
    # Extract the specific block for percentiles
    # Columns 8 through 19 correspond to the regions (China-S1 ... India-S3)
    scatter_data = df.iloc[1:6, 8:20].copy()
    
    # Get column names from the first row of the dataframe (which contains the labels like China-S1)
    scatter_cols = df.iloc[0, 8:20].values
    scatter_data.columns = [str(c).strip() for c in scatter_cols]
    
    # Convert to numeric
    scatter_data = scatter_data.apply(pd.to_numeric)
    
    # Prepare final list of dicts
    final_data = []
    
    for _, row in df_bars.iterrows():
        region = row['Region']
        scenario = row['Scenario']
        label = row['Label']
        
        item = {
            'Region': region,
            'Scenario': scenario,
            'Label': label,
            'Central': row['Central'],
            'Low': row['Low'],
            'High': row['High']
        }
        
        # Look up scatter points
        # Construct key for scatter lookup based on raw CSV header format
        # The CSV header for scatter used "United States", so we need to be careful matching.
        # df_bars['Region'] has "United States" because we only replaced in 'Label'.
        scatter_key = f"{region}-{scenario}"
        
        points = []
        if scatter_key in scatter_data.columns:
            points = scatter_data[scatter_key].dropna().tolist()
            
        item['Percentiles'] = points
        final_data.append(item)
    
    output_data = {
        "scr_data": final_data,
        "der_data": []
    }
    
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/155.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compile_data(output_file)
