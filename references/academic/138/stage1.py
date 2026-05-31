import sys
import io
import json
import pandas as pd
import numpy as np

def process_data():
    # 1. Load Data
    # Using the provided source data exactly as a string buffer
    csv_data = """
UF|Total|Domestic|China|EU|Other countries|Biome
RO|1.7028|0.714085|0|0.546341|0.214683|AMAZÔNIA
AC|0|0|0|0|0|AMAZÔNIA
AM|0.0122237|0.0122236|0|0|0|AMAZÔNIA
RR|0.218045|0.218045|0|0|0|AMAZÔNIA
PA|2.36176|0|0.359321|0.477212|0.50947|AMAZÔNIA
AP|0.0885287|0|0|0|0|AMAZÔNIA
TO|0.133839|0.0358671|0.0221865|0.00423591|0.00800975|AMAZÔNIA
MA|0.701576|0.250605|0.0567376|0.0185344|0.018738|AMAZÔNIA
MT|17.9337|0.801797|3.71661|1.68935|4.2973|AMAZÔNIA
RO|0.268529|0|0.000890181|0.188907|0.0758579|CERRADO
PA|0.0281624|0|0|0|0|CERRADO
TO|5.87683|0.750694|2.405|0.368623|0.875614|CERRADO
MA|4.66546|0.0746332|2.54759|0.462159|0.51833|CERRADO
PI|4.6205|0.625936|1.09801|0.18551|0.316376|CERRADO
BA|9.16888|1.41234|3.39683|1.97755|0.914535|CERRADO
MG|7.46717|1.2042|3.0454|0.336829|1.47383|CERRADO
SP|2.31141|0.426538|1.35377|0.0449633|0.37721|CERRADO
PR|0.222688|0.076108|0.136252|2.69587e-09|0.00823693|CERRADO
MS|11.5686|2.52942|5.72548|1.32195|1.52692|CERRADO
MT|23.8678|3.99933|8.19591|2.19776|5.91568|CERRADO
GO|14.882|4.52926|6.42301|1.03616|2.05772|CERRADO
DF|0.385592|0.217271|0.148304|0.000229712|0.0151448|CERRADO
PI|0|0|0|0|0|CAATINGA
CE|0.0021375|0|0.00213535|0|0|CAATINGA
RN|0|0|0|0|0|CAATINGA
PB|0|0|0|0|0|CAATINGA
PE|0|0|0|0|0|CAATINGA
AL|0|0|0|0|0|CAATINGA
SE|0|0|0|0|0|CAATINGA
BA|0.0508217|0.0415239|0.0092731|-1.33004e-07|0|CAATINGA
MG|0.00712854|0|0.000410985|0|0.000307625|CAATINGA
RN|0|0|0|0|0|MATA ATLÂNTICA
PB|0|0|0|0|0|MATA ATLÂNTICA
PE|0|0|0|0|0|MATA ATLÂNTICA
AL|0.00342842|0|0.00342191|0|0|MATA ATLÂNTICA
SE|0|0|0|0|0|MATA ATLÂNTICA
BA|0|0|0|0|0|MATA ATLÂNTICA
MG|1.40751|0.495722|0.498626|0.0387838|0.194424|MATA ATLÂNTICA
ES|0|0|0|0|0|MATA ATLÂNTICA
RJ|0|0|0|0|0|MATA ATLÂNTICA
SP|4.19579|0.936257|2.13859|0.299379|0.423268|MATA ATLÂNTICA
PR|31.4401|7.33527|16.782|2.83486|3.29996|MATA ATLÂNTICA
SC|3.80972|0.751658|2.37845|0.208518|0.323453|MATA ATLÂNTICA
RS|8.18601|3.60894|3.51158|0.184026|0.489045|MATA ATLÂNTICA
MS|3.03427|0.746492|1.32953|0.456528|0.308773|MATA ATLÂNTICA
GO|0.0068595|0.0066709|0|0|0|MATA ATLÂNTICA
RS|17.5383|3.79974|10.8462|0.680015|1.52441|PAMPA
MS|0|0|0|0|0|PANTANAL
MT|0|0|0|0|0|PANTANAL
nan|0|0.000359487|9.92086|8.27656|7.98418|nan
"""
    
    # Read CSV
    df = pd.read_csv(io.StringIO(csv_data), sep='|')
    
    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Clean string columns and handle 'nan' to 'NA' conversion
    df['UF'] = df['UF'].astype(str).str.strip().replace('nan', 'NA')
    df['Biome'] = df['Biome'].astype(str).str.strip().replace('nan', 'NA')
    
    # Define the specific order of Biomes as seen in the chart (Clockwise)
    biome_order = ['AMAZÔNIA', 'PANTANAL', 'CERRADO', 'CAATINGA', 'PAMPA', 'MATA ATLÂNTICA', 'NA']
    
    # Sort dataframe by Biome then UF
    df['Biome'] = pd.Categorical(df['Biome'], categories=biome_order, ordered=True)
    df = df.sort_values(['Biome', 'UF']).reset_index(drop=True)
    
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
    with open("bench/ground_truth_code/nature_1_output/138.json", 'w') as f:
        json.dump(data_to_save, f, indent=4)
