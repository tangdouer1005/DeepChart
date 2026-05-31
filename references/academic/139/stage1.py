import sys
import io
import json
import pandas as pd
import numpy as np

def process_data():
    # ---------------------------------------------------------
    # 1. Data Preparation
    # ---------------------------------------------------------
    
    # A. The Provided Source Data (Land use for soybeans - Solid Bars)
    # Using io.StringIO to load the provided markdown table data
    csv_data = """Category,2013,2014,2015,2016,2017,2018,2019,2020
Brazil/Domestic,8.12523,8.87591,8.80051,9.78178,8.97895,5.43421,9.32629,7.4605
China,11.0896,11.6053,13.3816,13.3039,15.8891,19.9617,16.7378,17.8011
EU28,4.97095,5.29244,4.75845,4.78287,3.91805,3.7941,4.03213,4.89951
Other countries,3.76588,4.53771,5.26896,5.4739,5.22136,5.65329,5.85281,7.04959"""
    
    df_land_use = pd.read_csv(io.StringIO(csv_data))
    df_land_use.set_index('Category', inplace=True)
    
    # B. Estimated Data for "Deforestation Exposure" (Hatched Bars)
    deforestation_data = {
        'Brazil/Domestic': [0.18, 0.16, 0.20, 0.25, 0.21, 0.16, 0.15, 0.12],
        'China':           [0.26, 0.26, 0.40, 0.35, 0.53, 0.45, 0.40, 0.33],
        'EU28':            [0.18, 0.18, 0.22, 0.12, 0.12, 0.08, 0.10, 0.08],
        'Other countries': [0.12, 0.12, 0.18, 0.10, 0.15, 0.11, 0.10, 0.10]
    }
    df_deforestation = pd.DataFrame(deforestation_data, index=df_land_use.columns).T

    # C. Explicit Data for "Soy Appropriation" (Markers)
    appropriation_data = {
        'Brazil/Domestic': [23.9, 25.8, 26.3, 28.8, 30.8, 18.9, 30.1, 23.9],
        'China':           [32.8, 32.8, 41.0, 38.8, 54.0, 67.7, 52.6, 57.1],
        'EU28':            [14.4, 15.2, 15.9, 15.3, 17.0, 18.4, 18.7, 24.2],
        'Other countries': [10.6, 12.9, 14.2, 13.5, 12.9, 12.9, 12.9, 16.7]
    }
    
    # Combine all data into a single structure for JSON serialization
    # The JSON should contain years, categories, and values for each type of data.
    # We can restructure this into a more flat format suitable for JSON.

    # Example:
    # [
    #   {'Year': 2013, 'Category': 'Brazil/Domestic', 'LandUse': 8.12523, 'Deforestation': 0.18, 'Appropriation': 23.9},
    #   {'Year': 2013, 'Category': 'China', 'LandUse': 11.0896, 'Deforestation': 0.26, 'Appropriation': 32.8},
    #   ...
    # ]

    years = df_land_use.columns.astype(int)
    categories = df_land_use.index.tolist()

    all_data = []
    for year_idx, year in enumerate(years):
        for category in categories:
            row_data = {
                'Year': int(year),
                'Category': category,
                'LandUse': df_land_use.loc[category, str(year)],
                'Deforestation': df_deforestation.loc[category, str(year)],
                'Appropriation': appropriation_data[category][year_idx]
            }
            all_data.append(row_data)

    return pd.DataFrame(all_data)

if __name__ == "__main__":
    df_processed = process_data()
    # Save to JSON
    data_to_save = {
        "scr_data": df_processed.to_dict(orient='records'),
        "der_data": {}
    }
    with open("bench/ground_truth_code/nature_1_output/139.json", 'w') as f:
        json.dump(data_to_save, f, indent=4)
