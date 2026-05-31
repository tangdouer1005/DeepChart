import sys
import io
import pandas as pd
import json
import numpy as np

def process_data(output_filename):
    # 1. Load Source Data
    csv_data = """
| Country      |   Plate waste rate |        sd |
|:-------------|-------------------:|----------:|
| Brazil       |          0.147553  |   7.84035 |
| Canada       |          0.361057  |   0       |
| China        |          0.241117  |   0       |
| Croatia      |          0.155559  |   0       |
| Denmark      |          0.258459  |   8.91632 |
| Ethiopia     |          0.116182  |   0       |
| Finland      |          0.221753  |   0       |
| France       |          0.283855  |   0       |
| Germany      |          0.18335   |   0       |
| Hungary      |          0.277409  |   0       |
| India        |        nan         | nan       |
| Indonesia    |        nan         | nan       |
| Iran         |          0.201225  |   1.66657 |
| Italy        |          0.322202  |  11.8637  |
| Japan        |          0.0401832 |   5.1598  |
| Jordan       |          0.168129  |   0       |
| Latvia       |          0.319073  |   7.07593 |
| Malaysia     |        nan         | nan       |
| Philippines  |          0.0366431 |   2.6163  |
| Portugal     |          0.290535  |  19.6385  |
| Russia       |        nan         | nan       |
| South Africa |          0.463137  |  11.3842  |
| Spain        |          0.242257  |   9.88582 |
| Sweden       |          0.0834352 |   1.04935 |
| Switzerland  |        nan         | nan       |
| Thailand     |          0.124509  |   9.46044 |
| Turkey       |          0.136616  |   0       |
| UK           |          0.208682  |   7.1671  |
| USA          |          0.287659  |  12.9019  |
"""
    
    # Parse the markdown table
    df = pd.read_csv(io.StringIO(csv_data), sep='|', engine='python')
    
    # Clean column names
    df.columns = [c.strip() for c in df.columns]
    
    # Drop empty columns
    df = df.dropna(axis=1, how='all')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Clean string data
    df['Country'] = df['Country'].astype(str).str.strip()
    
    # Convert numeric columns
    df['Plate waste rate'] = pd.to_numeric(df['Plate waste rate'], errors='coerce')
    df['sd'] = pd.to_numeric(df['sd'], errors='coerce')
    
    # Drop rows where 'Plate waste rate' is NaN
    df = df.dropna(subset=['Plate waste rate'])
    
    # Convert rate to percentage
    df['rate_pct'] = df['Plate waste rate'] * 100
    
    # Sort descending by rate
    df = df.sort_values('rate_pct', ascending=False).reset_index(drop=True)

    # Save to JSON
    data_list = df.to_dict(orient='records')
    output_data = {
        "scr_data": [],
        "der_data": data_list
    }
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)

if __name__ == "__main__":
    output_file = "169.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    process_data(output_file)
