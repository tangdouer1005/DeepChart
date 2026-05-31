import sys
import io
import json
import pandas as pd
import numpy as np

# 1. Source Data embedded as a string
SOURCE_DATA = """
|   Unnamed: 0 | Unnamed: 1                                                                                  |
|-------------:|:--------------------------------------------------------------------------------------------|
|          nan | Figure 5:                                                                                   |
|          nan | Data on water use for soybeans in Brazil are reported in this file (unit: cubic kilometers) |

# 2012
| UF   |       Total |    Domestic |       China |          EU |   Other countries | Biome          |
|:-----|------------:|------------:|------------:|------------:|------------------:|:---------------|
| RO   |  0.489138   | 0.162627    | 0           | 0.270817    |       0.0553949   | AMAZÔNIA       |
| AC   |  0          | 0           | 0           | 0           |       0           | AMAZÔNIA       |
| AM   |  0.00100049 | 0.00100049  | 0           | 0           |       0           | AMAZÔNIA       |
| RR   |  0.0212041  | 0.0211216   | 0           | 0           |       8.25081e-05 | AMAZÔNIA       |
| PA   |  0.460453   | 0.0463854   | 0.0832068   | 0.240372    |       0.0644473   | AMAZÔNIA       |
| AP   |  0          | 0           | 0           | 0           |       0           | AMAZÔNIA       |
| TO   |  0.00681717 | 0           | 0.000903865 | 0.0059133   |       0           | AMAZÔNIA       |
| MA   |  0.00121452 | 0           | 0.000570446 | 0.000186396 |       0.00025902  | AMAZÔNIA       |
| MT   |  8.35218    | 1.15457     | 2.58274     | 0.98045     |       0.900024    | AMAZÔNIA       |
| RO   |  0.185048   | 0           | 0           | 0.161486    |       0.0235618   | CERRADO        |
| PA   |  0.0195673  | 0           | 0.00758645  | 0.00694813  |       0.00469114  | CERRADO        |
| TO   |  2.57853    | 0.119757    | 0.558597    | 1.20598     |       0.474085    | CERRADO        |
| MA   |  2.90213    | 0.238213    | 0.720007    | 1.2529      |       0.574956    | CERRADO        |
| PI   |  2.59514    | 0.463114    | 0.226178    | 1.20184     |       0.251866    | CERRADO        |
| BA   |  5.44566    | 1.0393      | 1.3445      | 1.91414     |       0.921806    | CERRADO        |
| MG   |  4.80725    | 0.813701    | 2.53475     | 0.781597    |       0.479927    | CERRADO        |
| SP   |  1.22089    | 0.112457    | 0.626372    | 0.134307    |       0.237839    | CERRADO        |
| PR   |  0.372971   | 0           | 0.370254    | 0           |       0           | CERRADO        |
| MS   |  6.18903    | 1.9196      | 1.37792     | 1.4869      |       1.10989     | CERRADO        |
| MT   | 19.7381     | 3.47543     | 7.17141     | 4.50499     |       3.32551     | CERRADO        |
| GO   | 11.3169     | 4.49351     | 3.88629     | 1.57867     |       1.09906     | CERRADO        |
| DF   |  0.292076   | 0.22708     | 0.0447509   | 0.00489012  |       0.0152516   | CERRADO        |
| PI   |  0          | 0           | 0           | 0           |       0           | CAATINGA       |
| CE   |  0.00414158 | 0           | 0           | 0.00334586  |       0.000795645 | CAATINGA       |
| RN   |  0          | 0           | 0           | 0           |       0           | CAATINGA       |
| PB   |  0          | 0           | 0           | 0           |       0           | CAATINGA       |
| PE   |  0          | 0           | 0           | 0           |       0           | CAATINGA       |
| AL   |  0          | 0           | 0           | 0           |       0           | CAATINGA       |
| SE   |  0          | 0           | 0           | 0           |       0           | CAATINGA       |
| BA   |  0.012676   | 0           | 0           | 0.0084054   |       0.000578225 | CAATINGA       |
| MG   |  0.00134266 | 0           | 0           | 0.00024078  |       0.000213213 | CAATINGA       |
| RN   |  0          | 0           | 0           | 0           |       0           | MATA ATLÂNTICA |
| PB   |  0          | 0           | 0           | 0           |       0           | MATA ATLÂNTICA |
| PE   |  0          | 0           | 0           | 0           |       0           | MATA ATLÂNTICA |
| AL   |  0          | 0           | 0           | 0           |       0           | MATA ATLÂNTICA |
| SE   |  0          | 0           | 0           | 0           |       0           | MATA ATLÂNTICA |
| BA   |  0          | 0           | 0           | 0           |       0           | MATA ATLÂNTICA |
| MG   |  0.572842   | 0.303058    | 0.198936    | 0.00640423  |       0.0213916   | MATA ATLÂNTICA |
| ES   |  0          | 0           | 0           | 0           |       0           | MATA ATLÂNTICA |
| RJ   |  0          | 0           | 0           | 0           |       0           | MATA ATLÂNTICA |
| SP   |  2.00848    | 0.628002    | 0.978497    | 0.117234    |       0.0828354   | MATA ATLÂNTICA |
| PR   | 23.7797     | 8.19883     | 8.00448     | 4.36941     |       2.57902     | MATA ATLÂNTICA |
| SC   |  2.46684    | 0.834658    | 0.795146    | 0.331747    |       0.321397    | MATA ATLÂNTICA |
| RS   |  6.72967    | 3.37986     | 1.45936     | 1.08309     |       0.656413    | MATA ATLÂNTICA |
| MS   |  2.05315    | 0.663404    | 0.912557    | 0.184921    |       0.219525    | MATA ATLÂNTICA |
| GO   |  0.00198916 | 0           | 0.00197814  | 0           |       0           | MATA ATLÂNTICA |
| RS   | 10.9793     | 4.20276     | 2.65267     | 2.17404     |       1.48846     | PAMPA          |
| MS   |  0          | 0           | 0           | 0           |       0           | PANTANAL       |
| MT   |  0          | 0           | 0           | 0           |       0           | PANTANAL       |
| nan  |  0          | 0.000430101 | 3.30758     | 3.25883     |       1.83799     | nan            |
"""

def load_and_clean_data():
    # Read the data, skipping the initial metadata lines
    # We look for the header line starting with "| UF"
    lines = SOURCE_DATA.strip().split('\n')
    start_idx = 0
    for i, line in enumerate(lines):
        if "| UF" in line:
            start_idx = i
            break
    
    data_str = '\n'.join(lines[start_idx:])
    
    # Use pandas to parse the markdown table
    df = pd.read_csv(io.StringIO(data_str), sep='|', skipinitialspace=True)
    
    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Drop the first and last columns which are empty due to markdown pipes
    df = df.iloc[:, 1:-1]

    # Remove the markdown separator line if it exists
    df = df[df['UF'].astype(str).str.strip() != ':-----']
    
    # Handle the last row (NA group)
    # The last row has nan in UF and nan in Biome. We want to label it NA.
    # Identify it by index or by checking for nan in Biome
    mask_na_biome = df['Biome'].astype(str).str.strip() == 'nan'
    df.loc[mask_na_biome, 'Biome'] = 'NA'
    df.loc[mask_na_biome, 'UF'] = 'NA'
    
    # Convert numeric columns to float
    numeric_cols = ['Total', 'Domestic', 'China', 'EU', 'Other countries']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    # Clean string columns
    df['UF'] = df['UF'].astype(str).str.strip()
    df['Biome'] = df['Biome'].astype(str).str.strip()

    # Define the order of Biomes as they appear clockwise in the chart
    biome_order = [
        'AMAZÔNIA', 
        'PANTANAL', 
        'CERRADO', 
        'CAATINGA', 
        'PAMPA', 
        'MATA ATLÂNTICA', 
        'NA'
    ]
    
    # Sort data: Custom Biome order, then Alphabetical UF
    df['Biome'] = pd.Categorical(df['Biome'], categories=biome_order, ordered=True)
    df = df.sort_values(['Biome', 'UF'])
    
    return df, biome_order

if __name__ == "__main__":
    df_clean, biome_order = load_and_clean_data()
    # Save to JSON
    data_to_save = {
        "scr_data": df_clean.to_dict(orient='records'),
        "der_data": {
            "biome_order": biome_order
        }
    }
    with open("bench/ground_truth_code/nature_1_output/136.json", 'w') as f:
        json.dump(data_to_save, f, indent=4)
