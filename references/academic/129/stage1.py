import sys
import io
import pandas as pd
import json
import os

def compute_data(output_filename):
    csv_data = """\
|   Unnamed: 0 | Unnamed: 1                                                                         |
|-------------:|:-----------------------------------------------------------------------------------|
|          nan | Figure 4:                                                                          |
|          nan | Data on land use for soybeans in Brazil are reported in this file (unit: hectares) |
| UF   |   Total |         Domestic |       China |               EU |   Other_countries | Biome          |
| RO   |   24443 |  24443           |      0      |      0           |       0           | AMAZÔNIA       |
| AC   |       0 |      0           |      0      |      0           |       0           | AMAZÔNIA       |
| AM   |    2306 |   2300           |      0      |      0           |       0           | AMAZÔNIA       |
| RR   |   12000 |  12000           |      0      |      0           |       0           | AMAZÔNIA       |
| PA   |   33569 |      0           |      0      |   9883.44        |     706.923       | AMAZÔNIA       |
| AP   |       0 |      0           |      0      |      0           |       0           | AMAZÔNIA       |
| TO   |     770 |      0           |      0      |    400           |       0           | AMAZÔNIA       |
| MA   |       0 |      0           |      0      |      0           |       0           | AMAZÔNIA       |
| MT   |  739637 |      0           |  12383.7    |  39923.2         |   31156.7         | AMAZÔNIA       |
| RO   |   32000 |  32000           |      0      |      0           |       0           | CERRADO        |
| PA   |    1650 |      0           |      0      |      0           |       0           | CERRADO        |
| TO   |  253496 |      0           |  13234.1    | 110071           |    1672.52        | CERRADO        |
| MA   |  340403 |  34823.4         |  32304.6    |  88251.1         |   85365.5         | CERRADO        |
| PI   |  159281 |  78509.1         |    275.173  |  43959.1         |       0           | CERRADO        |
| BA   |  821000 | 211106           |      0      | 372659           |   96905.2         | CERRADO        |
| MG   |  950966 | 207090           |  46848.5    | 561802           |   86352.6         | CERRADO        |
| SP   |  231909 | 131597           |  16812.3    |  51190.7         |   23181.3         | CERRADO        |
| PR   |   55000 |  42590           |  12385.2    |      0           |       0           | CERRADO        |
| MS   | 1318891 | 365389           |  17253      | 346641           |  106072           | CERRADO        |
| MT   | 4540291 | 805247           | 221864      |      1.06649e+06 |  437541           | CERRADO        |
| GO   | 2588954 | 778464           | 160175      |      1.23922e+06 |  215061           | CERRADO        |
| DF   |   50383 |  20342.1         |    694.108  |  17208.7         |   11437.6         | CERRADO        |
| PI   |       0 |      0           |      0      |      0           |       0           | CAATINGA       |
| CE   |     350 |      0           |     67.2402 |    282.76        |       0           | CAATINGA       |
| RN   |       0 |      0           |      0      |      0           |       0           | CAATINGA       |
| PB   |       0 |      0           |      0      |      0           |       0           | CAATINGA       |
| PE   |       0 |      0           |      0      |      0           |       0           | CAATINGA       |
| AL   |     171 |      0           |     19.2115 |    138.155       |       0           | CAATINGA       |
| SE   |       0 |      0           |      0      |      0           |       0           | CAATINGA       |
| BA   |     270 |      0           |      0      |     24.5164      |       0           | CAATINGA       |
| MG   |      41 |      0           |      0      |      0           |       0           | CAATINGA       |
| RN   |       0 |      0           |      0      |      0           |       0           | MATA ATLÂNTICA |
| PB   |       0 |      0           |      0      |      0           |       0           | MATA ATLÂNTICA |
| PE   |       0 |      0           |      0      |      0           |       0           | MATA ATLÂNTICA |
| AL   |      30 |      0           |      0      |     24.2366      |       0           | MATA ATLÂNTICA |
| SE   |       0 |      0           |      0      |      0           |       0           | MATA ATLÂNTICA |
| BA   |       0 |      0           |      0      |      0           |       0           | MATA ATLÂNTICA |
| MG   |  145416 |  35739.6         |  13139.4    |  71533.8         |   17831.5         | MATA ATLÂNTICA |
| ES   |       0 |      0           |      0      |      0           |       0           | MATA ATLÂNTICA |
| RJ   |       0 |      0           |      0      |      0           |       0           | MATA ATLÂNTICA |
| SP   |  547971 | 197746           |  66327.3    | 165683           |   86614.9         | MATA ATLÂNTICA |
| PR   | 3956021 |      1.38135e+06 | 709033      |      1.14325e+06 |  669558           | MATA ATLÂNTICA |
| SC   |  314469 | 139741           |  41986      |  52740.3         |   67362.3         | MATA ATLÂNTICA |
| RS   | 1536638 | 544845           | 357305      | 191569           |  390989           | MATA ATLÂNTICA |
| MS   |  493115 | 173247           |  56374.5    | 150083           |   66407.6         | MATA ATLÂNTICA |
| GO   |    3000 |   2000           |    431.876  |      0           |     568.124       | MATA ATLÂNTICA |
| RS   | 2447699 | 646075           | 504690      | 410547           |  830028           | PAMPA          |
| MS   |       0 |      0           |      0      |      0           |       0           | PANTANAL       |
| MT   |       0 |      0           |      0      |      0           |       0           | PANTANAL       |
| nan  |       0 |    106.087       | 747449      |      2.69633e+06 |       1.07016e+06 | nan            |
"""

    # Read the raw text, skipping the first few lines of metadata manually
    lines = csv_data.strip().split('\n')
    
    # Find the header line (starts with | UF)
    header_idx = 0
    for i, line in enumerate(lines):
        if '| UF' in line:
            header_idx = i
            break
            
    # Extract relevant lines
    data_lines = lines[header_idx:]
    data_str = '\n'.join(data_lines)
    
    # Read into pandas
    df = pd.read_csv(io.StringIO(data_str), sep='|', skipinitialspace=True)
    
    # Clean column names
    df.columns = [c.strip() for c in df.columns]
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Clean string columns
    df['UF'] = df['UF'].astype(str).str.strip()
    df['Biome'] = df['Biome'].astype(str).str.strip()
    
    # Handle the last row (NA/nan)
    df.loc[df['Biome'] == 'nan', 'Biome'] = 'NA'
    df.loc[df['UF'] == 'nan', 'UF'] = 'NA'
    
    # Convert numeric columns
    numeric_cols = ['Total', 'Domestic', 'China', 'EU', 'Other_countries']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        # Convert to Millions
        df[col] = df[col] / 1_000_000
        
    biome_order = ['AMAZÔNIA', 'PANTANAL', 'CERRADO', 'CAATINGA', 'PAMPA', 'MATA ATLÂNTICA', 'NA']
    
    # Sort Data
    df['Biome'] = pd.Categorical(df['Biome'], categories=biome_order, ordered=True)
    df = df.sort_values(by=['Biome', 'UF'])
    
    data_to_save = {
        "scr_data": df.to_dict(orient='records'),
        "der_data": {
            "biome_order": biome_order
        }
    }
    
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    with open(output_filename, 'w') as f:
        json.dump(data_to_save, f, indent=4)
        
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/129.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compute_data(output_file)
