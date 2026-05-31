import sys
import io
import json
import pandas as pd
import numpy as np

# 1. Source Data (Embedded exactly as provided)
csv_data = """
| UF   |   Total |         Domestic |            China |               EU |   Other_countries | Biome          |
|:-----|--------:|-----------------:|-----------------:|-----------------:|------------------:|:---------------|
| RO   |  338642 | 150386           |      0           | 104896           |   41127.9         | AMAZÔNIA       |
| AC   |    3280 |   3279.86        |      0           |      0           |       0           | AMAZÔNIA       |
| AM   |    2700 |   2699.97        |      0           |      0           |       0           | AMAZÔNIA       |
| RR   |   49800 |  49800           |      0           |      0           |       0           | AMAZÔNIA       |
| PA   |  634831 |      0           |  85888.5         | 126133           |  140613           | AMAZÔNIA       |
| AP   |   20300 |      0           |      0           |      0           |       0           | AMAZÔNIA       |
| TO   |   24274 |   6425.91        |   4051.05        |    764.353       |    1463.07        | AMAZÔNIA       |
| MA   |  137374 |  49119.9         |  11034.4         |   3487.91        |    3623.39        | AMAZÔNIA       |
| MT   | 4228843 | 186657           | 883894           | 398242           |       1.01623e+06 | AMAZÔNIA       |
| RO   |   54000 |      0           |    179.011       |  37988.4         |   15254.7         | CERRADO        |
| PA   |    8436 |      0           |      0           |      0           |       0           | CERRADO       |
| TO   |  943325 | 119698           | 383314           |  59737.4         |  140541           | CERRADO        |
| MA   |  823526 |  13323           | 449035           |  81298.9         |   91124.4         | CERRADO        |
| PI   |  757978 | 105178           | 182462           |  29943.5         |   52557.6         | CERRADO        |
| BA   | 1614550 | 251491           | 597877           | 345972           |  160695           | CERRADO        |
| MG   | 1427871 | 227638           | 584290           |  63274.4         |  280472           | CERRADO        |
| SP   |  414415 |  73593.3         | 245878           |   7796.82        |   68113.9         | CERRADO        |
| PR   |   41100 |  14176.4         |  25019.9         |      0           |    1514.64        | CERRADO        |
| MS   | 2416981 | 543300           |      1.18335e+06 | 276129           |  317171           | CERRADO        |
| MT   | 5760806 | 968009           |      2.00269e+06 | 528306           |       1.4266e+06  | CERRADO        |
| GO   | 3576103 |      1.10374e+06 |      1.538e+06   | 245174           |  489912           | CERRADO        |
| DF   |   74500 |  41978.8         |  28653.7         |     44.4968      |    2926.13        | CERRADO        |
| PI   |       0 |      0           |      0           |      0           |       0           | CAATINGA       |
| CE   |     450 |      0           |    449.547       |      0           |       0           | CAATINGA       |
| RN   |       0 |      0           |      0           |      0           |       0           | CAATINGA       |
| PB   |       0 |      0           |      0           |      0           |       0           | CAATINGA       |
| PE   |       0 |      0           |      0           |      0           |       0           | CAATINGA       |
| AL   |       0 |      0           |      0           |      0           |       0           | CAATINGA       |
| SE   |       0 |      0           |      0           |      0           |       0           | CAATINGA       |
| BA   |    7925 |   6470.26        |   1449.99        |      0           |       0           | CAATINGA       |
| MG   |    1390 |      0           |     89.8935      |      0           |      57.6345      | CAATINGA       |
| RN   |       0 |      0           |      0           |      0           |       0           | MATA ATLÂNTICA |
| PB   |       0 |      0           |      0           |      0           |       0           | MATA ATLÂNTICA |
| PE   |       0 |      0           |      0           |      0           |       0           | MATA ATLÂNTICA |
| AL   |    1224 |      0           |   1221.64        |      0           |       0           | MATA ATLÂNTICA |
| SE   |       0 |      0           |      0           |      0           |       0           | MATA ATLÂNTICA |
| BA   |       0 |      0           |      0           |      0           |       0           | MATA ATLÂNTICA |
| MG   |  266441 |  88147.7         |  96966.3         |   7324.07        |   38202.8         | MATA ATLÂNTICA |
| ES   |       0 |      0           |      0           |      0           |       0           | MATA ATLÂNTICA |
| RJ   |       0 |      0           |      0           |      0           |       0           | MATA ATLÂNTICA |
| SP   |  718550 | 155578           | 368910           |  50870.3         |   74352.9         | MATA ATLÂNTICA |
| PR   | 5493743 |      1.27815e+06 |      2.9639e+06  | 482759           |  567806           | MATA ATLÂNTICA |
| SC   |  664795 | 129116           | 412226           |  38743           |   59429.4         | MATA ATLÂNTICA |
| RS   | 1864870 | 813182           | 818890           |  38723           |  106262           | MATA ATLÂNTICA |
| MS   |  704541 | 170630           | 310075           | 107695           |   71153.8         | MATA ATLÂNTICA |
| GO   |    1597 |   1551.34        |      0           |      0           |       0           | MATA ATLÂNTICA |
| RS   | 4131501 | 907101           |      2.56704e+06 | 150768           |  342051           | PAMPA          |
| MS   |       0 |      0           |      0           |      0           |       0           | PANTANAL       |
| MT   |       0 |      0           |      0           |      0           |       0           | PANTANAL       |
| nan  |       0 |     74.5038      |      2.05422e+06 |      1.71344e+06 |       1.65472e+06 | nan            |
"""

def process_data(csv_text):
    # Read CSV from string, handling the markdown pipe format
    df = pd.read_csv(io.StringIO(csv_text), sep='|', skipinitialspace=True)
    
    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Drop the first and last columns which are empty due to markdown pipes
    df = df.iloc[:, 1:-1]
    
    # Remove the separator line used in markdown table
    df = df[df['UF'].astype(str).str.strip() != ':-----']
    
    # Handle the "NA" row (last row in source)
    # The source has 'nan' for UF and Biome in the last row.
    df['UF'] = df['UF'].astype(str).str.strip()
    df['Biome'] = df['Biome'].astype(str).str.strip()
    
    # Replace string 'nan' with actual NA logic for the chart
    df.loc[df['UF'] == 'nan', 'UF'] = 'NA'
    df.loc[df['Biome'] == 'nan', 'Biome'] = 'NA'
    
    # Convert numeric columns
    numeric_cols = ['Total', 'Domestic', 'China', 'EU', 'Other_countries']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
    # Scale to Millions (as per chart axis 1.5, 3, 4.5, 6)
    # create new columns
    for col in numeric_cols:
        df[col + '_million'] = df[col] / 1_000_000
        
    return df

if __name__ == "__main__":
    df_clean = process_data(csv_data)
    
    # scr_data: original columns
    scr_cols = ['UF', 'Total', 'Domestic', 'China', 'EU', 'Other_countries', 'Biome']
    scr_data = df_clean[scr_cols].to_dict(orient='records')
    
    # der_data: million columns
    numeric_cols = ['Total', 'Domestic', 'China', 'EU', 'Other_countries']
    der_cols = [c + '_million' for c in numeric_cols]
    der_data = df_clean[der_cols + ['UF', 'Biome']].to_dict(orient='records')
    
    final_data = {
        "scr_data": scr_data,
        "der_data": der_data
    }
    
    with open("bench/ground_truth_code/nature_1_output/133.json", 'w') as f:
        json.dump(final_data, f, indent=4)
