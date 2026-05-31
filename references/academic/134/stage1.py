import sys
import io
import json
import pandas as pd
import numpy as np

def get_source_data():
    """
    Returns the pandas DataFrame created from the provided source data.
    """
    data_str = """\
| UF   |        Total |    Domestic |       China |           EU |   Other countries | Biome          |
|:-----|-------------:|------------:|------------:|-------------:|------------------:|:---------------|
| RO   |  0.114415    | 0.114415    | 0           |  0           |        0          | AMAZÔNIA       |
| AC   |  0           | 0           | 0           |  0           |        0          | AMAZÔNIA       |
| AM   |  0.00962643  | 0.00960139  | 0           |  0           |        0          | AMAZÔNIA       |
| RR   |  0.0512527   | 0.0512527   | 0           |  0           |        0          | AMAZÔNIA       |
| PA   |  0.125305    | 0           | 0           |  0.0366658   |        0.00290931 | AMAZÔNIA       |
| AP   |  0           | 0           | 0           |  0           |        0          | AMAZÔNIA       |
| TO   |  0.00400667  | 0           | 0           |  0.00202471  |        0          | AMAZÔNIA       |
| MA   |  0           | 0           | 0           |  0           |        0          | AMAZÔNIA       |
| MT   |  2.97692     | 0           | 0.0500429   |  0.160889    |        0.125164   | AMAZÔNIA       |
| RO   |  0.141925    | 0.141925    | 0           |  0           |        0          | CERRADO        |
| PA   |  0.00498554  | 0           | 0           |  0           |        0          | CERRADO        |
| TO   |  1.43321     | 0           | 0.0741484   |  0.624675    |        0.00936783 | CERRADO        |
| MA   |  1.64168     | 0.163763    | 0.15678     |  0.43545     |        0.409197   | CERRADO        |
| PI   |  0.880661    | 0.437205    | 0.00150225  |  0.238742    |        0          | CERRADO        |
| BA   |  4.60401     | 1.1847      | 0           |  2.09371     |        0.5447     | CERRADO        |
| MG   |  4.56039     | 1.02729     | 0.230682    |  2.64935     |        0.421712   | CERRADO        |
| SP   |  1.31924     | 0.739402    | 0.0980305   |  0.294762    |        0.133971   | CERRADO        |
| PR   |  0.313118    | 0.243411    | 0.0695648   |  0           |        0          | CERRADO        |
| MS   |  6.03992     | 1.64629     | 0.0797918   |  1.58092     |        0.484488   | CERRADO        |
| MT   | 18.6892      | 3.33661     | 0.894709    |  4.40742     |        1.8195     | CERRADO        |
| GO   | 10.3227      | 3.03384     | 0.637851    |  5.02027     |        0.856332   | CERRADO        |
| DF   |  0.225615    | 0.0910918   | 0.00310821  |  0.0770602   |        0.0512176  | CERRADO        |
| PI   |  0           | 0           | 0           |  0           |        0          | CAATINGA       |
| CE   |  0.00149772  | 0           | 0.000287734 |  0.00120999  |        0          | CAATINGA       |
| RN   |  0           | 0           | 0           |  0           |        0          | CAATINGA       |
| PB   |  0           | 0           | 0           |  0           |        0          | CAATINGA       |
| PE   |  0           | 0           | 0           |  0           |        0          | CAATINGA       |
| AL   |  0.000538864 | 0           | 5.94989e-05 |  0.000435362 |        0          | CAATINGA       |
| SE   |  0           | 0           | 0           |  0           |        0          | CAATINGA       |
| BA   |  0.00171117  | 0           | 0           |  0.000155377 |        0          | CAATINGA       |
| MG   |  0.000212819 | 0           | 0           |  0           |        0          | CAATINGA       |
| RN   |  0           | 0           | 0           |  0           |        0          | MATA ATLÂNTICA |
| PB   |  0           | 0           | 0           |  0           |        0          | MATA ATLÂNTICA |
| PE   |  0           | 0           | 0           |  0           |        0          | MATA ATLÂNTICA |
| AL   |  0.000111864 | 0           | 0           |  9.03731e-05 |        0          | MATA ATLÂNTICA |
| SE   |  0           | 0           | 0           |  0           |        0          | MATA ATLÂNTICA |
| BA   |  0           | 0           | 0           |  0           |        0          | MATA ATLÂNTICA |
| MG   |  0.755314    | 0.185852    | 0.068604    |  0.373973    |        0.0916257  | MATA ATLÂNTICA |
| ES   |  0           | 0           | 0           |  0           |        0          | MATA ATLÂNTICA |
| RJ   |  0           | 0           | 0           |  0           |        0          | MATA ATLÂNTICA |
| SP   |  3.081       | 1.11031     | 0.37609     |  0.927829    |        0.485674   | MATA ATLÂNTICA |
| PR   | 21.1121      | 7.3909      | 3.78398     |  6.06268     |        3.59111    | MATA ATLÂNTICA |
| SC   |  1.73768     | 0.790946    | 0.229827    |  0.271224    |        0.370402   | MATA ATLÂNTICA |
| RS   |  6.42229     | 2.29844     | 1.49619     |  0.784473    |        1.62655    | MATA ATLÂNTICA |
| MS   |  2.30378     | 0.805498    | 0.259331    |  0.706551    |        0.310066   | MATA ATLÂNTICA |
| GO   |  0.0130812   | 0.00868897  | 0.0018969   |  0           |        0.00249533 | MATA ATLÂNTICA |
| RS   |  9.63679     | 2.52987     | 1.97878     |  1.61103     |        3.28818    | PAMPA          |
| MS   |  0           | 0           | 0           |  0           |        0          | PANTANAL       |
| MT   |  0           | 0           | 0           |  0           |        0          | PANTANAL       |
| nan  |  0           | 0.000487474 | 3.43685     | 12.3897      |        4.91744    | nan            |
    """
    
    # Process the markdown table string
    lines = data_str.strip().split('\n')
    # Filter out separator lines (e.g., |---|)
    lines = [line for line in lines if '---' not in line]
    
    # Create a clean CSV string
    csv_str = '\n'.join(lines)
    
    # Read into pandas
    df = pd.read_csv(io.StringIO(csv_str), sep='|', skipinitialspace=True)
    
    # Clean column names (remove whitespace and empty columns from markdown pipes)
    df.columns = [c.strip() for c in df.columns]
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Clean string columns
    df['UF'] = df['UF'].str.strip()
    df['Biome'] = df['Biome'].str.strip()
    
    # Handle the last row (NA)
    # The source data has 'nan' in the first column for the last row
    # We identify it by the index or by checking for NaN in UF/Biome
    mask_na = df['UF'].astype(str) == 'nan'
    df.loc[mask_na, 'UF'] = 'NA'
    df.loc[mask_na, 'Biome'] = 'NA'
    
    return df

if __name__ == "__main__":
    df_clean = get_source_data()
    # Save to JSON
    
    data_to_save = {
        "scr_data": df_clean.to_dict(orient='records'),
        "der_data": {}
    }
    
    with open("bench/ground_truth_code/nature_1_output/134.json", 'w') as f:
        json.dump(data_to_save, f, indent=4)
