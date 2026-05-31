import sys
import io
import json
import pandas as pd
import numpy as np

# 1. Load Source Data
# We embed the data directly as a string to ensure the script is self-contained.
csv_data = """
UF|Total|Domestic|China|EU|Other countries|Biome
RO|0.889164|0.42801|0.152716|0.215917|0.091916|AMAZÔNIA
AC|0|0|0|0|0|AMAZÔNIA
AM|0|0|0|0|0|AMAZÔNIA
RR|0.105008|0.104795|0|0|0.000212607|AMAZÔNIA
PA|1.58271|0.0950292|0.551001|0.671685|0.14383|AMAZÔNIA
AP|0.067138|0|0|0.0379322|0|AMAZÔNIA
TO|0.0931787|0.027217|0.0393144|0.0264442|0|AMAZÔNIA
MA|0.266676|0.12271|0.0477404|0.00390637|0.0190575|AMAZÔNIA
MT|14.2444|0.858222|3.70748|2.21389|2.14395|AMAZÔNIA
RO|0.244054|0|0.0721874|0.135157|0.0366261|CERRADO
PA|0.0550185|0|0.00530147|0.00568574|0.00133762|CERRADO
TO|4.86451|1.20177|1.74741|1.52155|0.214859|CERRADO
MA|3.73388|0.600306|1.73935|0.897921|0.467115|CERRADO
PI|2.81416|1.38696|0.750725|0.283503|0.16784|CERRADO
BA|6.57289|2.51835|1.64725|1.44533|0.808875|CERRADO
MG|6.37774|1.47775|2.59487|0.972055|1.09499|CERRADO
SP|1.91952|0.185938|1.38244|0.0428669|0.256277|CERRADO
PR|0.379938|0|0.304605|0.000296198|0.0714852|CERRADO
MS|7.97434|2.35714|1.62995|1.69072|1.5285|CERRADO
MT|22.1982|6.47418|6.80724|3.41044|3.90981|CERRADO
GO|13.709|7.50225|3.57765|1.0861|1.25681|CERRADO
DF|0.351429|0.130677|0.167283|0.0163992|0.0368531|CERRADO
PI|0|0|0|0|0|CAATINGA
CE|0|0|0|0|0|CAATINGA
RN|0|0|0|0|0|CAATINGA
PB|0|0|0|0|0|CAATINGA
PE|0|0|0|0|0|CAATINGA
AL|0|0|0|0|0|CAATINGA
SE|0|0|0|0|0|CAATINGA
BA|0.0179572|0.0170261|0.000910982|0|0|CAATINGA
MG|0.00514199|0|0.00316291|0|0.00111873|CAATINGA
RN|0|0|0|0|0|MATA ATLÂNTICA
PB|0|0|0|0|0|MATA ATLÂNTICA
PE|0|0|0|0|0|MATA ATLÂNTICA
AL|0.000953549|0|0|0.000953517|0|MATA ATLÂNTICA
SE|0|0|0|0|0|MATA ATLÂNTICA
BA|0|0|0|0|0|MATA ATLÂNTICA
MG|1.14379|0.249163|0.554815|0.0754145|0.231935|MATA ATLÂNTICA
ES|0|0|0|0|0|MATA ATLÂNTICA
RJ|0|0|0|0|0|MATA ATLÂNTICA
SP|3.4042|0.820036|2.14107|0.0351306|0.276878|MATA ATLÂNTICA
PR|32.9761|11.1358|14.3749|2.768|3.9394|MATA ATLÂNTICA
SC|3.86536|0.787649|1.53009|0.467788|0.558936|MATA ATLÂNTICA
RS|9.01536|3.7042|3.15373|0.685776|1.05507|MATA ATLÂNTICA
MS|2.93363|0.920377|0.998459|0.337178|0.455984|MATA ATLÂNTICA
GO|0.00526863|0.000424816|0.000489741|0.00367306|0.000655903|MATA ATLÂNTICA
RS|18.3157|4.14094|8.8696|2.14767|2.72434|PAMPA
MS|0.000380705|0|0|0|0|PANTANAL
MT|0|0|0|0|0|PANTANAL
NA|0|0.000405953|7.38215|1.13064|3.28723|NA
"""

def process_data():
    # 2. Data Processing
    df = pd.read_csv(io.StringIO(csv_data), sep='|')
    
    # Clean up whitespace in string columns
    df['UF'] = df['UF'].astype(str).str.strip().replace('nan', 'NA')
    df['Biome'] = df['Biome'].astype(str).str.strip().replace('nan', 'NA')
    
    # Define the specific order of Biomes as seen in the chart (Clockwise starting from top-right)
    # Visual analysis: Amazônia -> Pantanal -> Cerrado -> Caatinga -> Pampa -> Mata Atlântica -> NA
    biome_order = [
        'AMAZÔNIA', 
        'PANTANAL', 
        'CERRADO', 
        'CAATINGA', 
        'PAMPA', 
        'MATA ATLÂNTICA', 
        'NA'
    ]
    
    # Create a categorical type for sorting
    df['Biome'] = pd.Categorical(df['Biome'], categories=biome_order, ordered=True)
    
    # Sort by Biome, then by UF (alphabetical)
    df = df.sort_values(by=['Biome', 'UF'])
    
    # Reset index for easier iteration
    df = df.reset_index(drop=True)

    return df, biome_order

if __name__ == "__main__":
    df_clean, biome_order = process_data()
    # Save to JSON
    data_to_save = {
        "scr_data": df_clean.to_dict(orient='records'),
        "der_data": {
            "biome_order": biome_order
        }
    }
    with open("bench/ground_truth_code/nature_1_output/137.json", 'w') as f:
        json.dump(data_to_save, f, indent=4)
