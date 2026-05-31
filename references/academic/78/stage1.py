import sys
import io
import pandas as pd
import numpy as np
import json

# 1. Source Data embedded as a string
csv_data = """
| Station            | PM_size      | Site_type    | Site_topography | Country      | Date_start          | Date_end            | N_samples    | OP_DTT_v_mean  | OP_DTT_v_SD    | PM_mass_mean  | PM_mass_SD    |
| ATH                | PM10         | Urban        | Other           | GR           | 2022-06-23 00:00:00 | 2023-12-06 00:00:00 | 147          | 2.44           | 1.24           | 31.99         | 14.89         |
| PASSY              | PM10         | Suburban     | Valley          | FR           | 2013-11-14 00:00:00 | 2018-03-02 00:00:00 | 437          | 3.19           | 2.25           | 29.19         | 18.4          |
| KRAK               | PM10         | Urban        | Other           | PL           | 2018-01-23 00:00:00 | 2018-09-27 00:00:00 | 63           | 2.04           | 1.26           | 28.69         | 18.9          |
| STG-cle            | PM10         | Traffic      | Other           | FR           | 2013-04-11 00:00:00 | 2020-01-03 00:00:00 | 147          | 2.65           | 2.09           | 27.87         | 14.58         |
| RBX                | PM10         | Traffic      | Other           | FR           | 2013-01-20 00:00:00 | 2014-05-26 00:00:00 | 159          | 2.71           | 1.71           | 27.8          | 15.26         |
| GSY                | PM10         | Industrial   | Coastal         | FR           | 2018-01-01 00:00:00 | 2020-06-29 00:00:00 | 133          | 1.63           | 1.54           | 27.05         | 14.6          |
| LENS               | PM10         | Urban        | Other           | FR           | 2011-03-09 00:00:00 | 2012-03-06 00:00:00 | 116          | 1.74           | 1.46           | 25.86         | 14.74         |
| ROUEN              | PM10         | Urban        | Other           | FR           | 2013-01-02 00:00:00 | 2014-03-30 00:00:00 | 135          | 2.26           | 1.19           | 25.39         | 13.88         |
| NOGENT             | PM10         | Urban        | Other           | FR           | 2013-01-02 00:00:00 | 2018-05-22 00:00:00 | 199          | 2.24           | 1.83           | 24.88         | 13.72         |
| CHAM               | PM10         | Urban        | Valley          | FR           | 2013-11-02 00:00:00 | 2014-10-31 00:00:00 | 98           | 2.33           | 1.56           | 23.47         | 12.72         |
| BCN                | PM10         | Urban        | Coastal         | ES           | 2018-01-03 00:00:00 | 2023-12-02 00:00:00 | 270          | 2.48           | 1.15           | 23.31         | 8.94          |
| NICE               | PM10         | Urban        | Coastal         | FR           | 2014-07-11 00:00:00 | 2018-07-06 00:00:00 | 110          | 2.24           | 0.8            | 22.88         | 7.72          |
| FSM                | PM10         | Industrial   | Coastal         | FR           | 2018-02-13 00:00:00 | 2018-09-23 00:00:00 | 29           | 1.1            | 0.7            | 21.89         | 7.84          |
| PARIS-lh           | PM10         | Urban        | Other           | FR           | 2022-04-07 00:00:00 | 2023-09-26 00:00:00 | 386          | 1.79           | 1.06           | 20.74         | 13.22         |
| PDB                | PM10         | Industrial   | Coastal         | FR           | 2014-06-01 00:00:00 | 2018-11-10 00:00:00 | 139          | 1.63           | 0.87           | 20.74         | 7.05          |
| CALAIS             | PM10         | Industrial   | Coastal         | FR           | 2021-02-01 00:00:00 | 2021-06-20 00:00:00 | 139          | 1.67           | 1.13           | 20.5          | 9.21          |
| TAL                | PM10         | Urban        | Other           | FR           | 2012-03-01 00:00:00 | 2019-11-03 00:00:00 | 235          | 1.64           | 1.25           | 20.05         | 10.98         |
| BERN               | PM10         | Traffic      | Other           | CH           | 2013-01-01 00:00:00 | 2020-12-31 00:00:00 | 738          | 2.69           | 1.45           | 19.42         | 10.22         |
| PARIS-lcpp         | PM10         | Urban        | Other           | FR           | 2020-04-21 00:00:00 | 2021-09-22 00:00:00 | 184          | 2.29           | 1.51           | 19.4          | 9.26          |
| LYON               | PM10         | Urban        | Other           | FR           | 2019-01-02 00:00:00 | 2019-12-31 00:00:00 | 122          | 1.64           | 1.33           | 19.32         | 12.19         |
| GRE-fr             | PM10         | Urban        | Valley          | FR           | 2013-01-02 00:00:00 | 2022-05-12 00:00:00 | 1351         | 1.62           | 1.33           | 18.9          | 10.23         |
| MRS-lcp            | PM10         | Urban        | Coastal         | FR           | 2015-01-11 00:00:00 | 2024-02-29 00:00:00 | 271          | 1.78           | 0.97           | 18.62         | 8.09          |
| ARREST             | PM10         | Rural        | Other           | FR           | 2021-02-01 00:00:00 | 2021-06-20 00:00:00 | 140          | 0.91           | 0.67           | 18.58         | 8.89          |
| MARNAZ             | PM10         | Rural        | Valley          | FR           | 2013-11-02 00:00:00 | 2014-10-31 00:00:00 | 93           | 1.77           | 1.18           | 18.49         | 12.28         |
| AIX                | PM10         | Urban        | Other           | FR           | 2013-08-02 00:00:00 | 2014-07-13 00:00:00 | 59           | 1.96           | 1.29           | 18.39         | 10.21         |
| ZURICH             | PM10         | Urban        | Other           | CH           | 2011-05-24 00:00:00 | 2019-05-29 00:00:00 | 204          | 2.4            | 2.1            | 18.38         | 12.57         |
| GRE-cb             | PM10         | Urban        | Valley          | FR           | 2017-02-28 00:00:00 | 2021-07-10 00:00:00 | 247          | 1.59           | 1.06           | 18.08         | 9.39          |
| COURMAY            | PM10         | Rural        | Valley          | IT           | 2023-08-12 00:00:00 | 2024-01-09 00:00:00 | 67           | 1              | 0.83           | 17.58         | 12.9          |
| DIEPPE             | PM10         | Rural        | Coastal         | FR           | 2021-02-11 00:00:00 | 2021-06-29 00:00:00 | 137          | 0.72           | 0.63           | 16.72         | 8.3           |
| MGD                | PM10         | Rural        | Valley          | CH           | 2013-01-04 00:00:00 | 2019-05-29 00:00:00 | 240          | 1.61           | 1.42           | 16.7          | 10.6          |
| RDAM               | PM10         | Urban        | Other           | NL           | 2023-07-26 00:00:00 | 2024-02-18 00:00:00 | 56           | 1.89           | 0.71           | 16.21         | 4.17          |
| PLOURZ             | PM10         | Rural        | Other           | FR           | 2023-03-10 00:00:00 | 2024-05-20 00:00:00 | 171          | 0.88           | 0.53           | 15.73         | 8.13          |
| KANAL              | PM10         | Industrial   | Valley          | SI           | 2020-11-12 00:00:00 | 2021-11-16 00:00:00 | 120          | 1.52           | 1.62           | 15.62         | 11.65         |
| LHV                | PM10         | Industrial   | Coastal         | FR           | 2021-02-01 00:00:00 | 2021-06-16 00:00:00 | 136          | 1.06           | 0.57           | 15.33         | 7.37          |
| BOSSONS            | PM10         | Traffic      | Other           | FR           | 2023-08-12 00:00:00 | 2024-01-09 00:00:00 | 96           | 1.51           | 0.66           | 14.67         | 7.19          |
| VIF                | PM10         | Suburban     | Other           | FR           | 2017-02-28 00:00:00 | 2021-07-10 00:00:00 | 253          | 1.12           | 0.8            | 14.32         | 9.34          |
| BASEL              | PM10         | Suburban     | Other           | CH           | 2018-06-03 00:00:00 | 2019-05-29 00:00:00 | 90           | 0.79           | 0.55           | 13.97         | 9.26          |
| PAYRN              | PM10         | Rural        | Other           | CH           | 2013-01-01 00:00:00 | 2019-05-29 00:00:00 | 103          | 0.92           | 0.73           | 13.49         | 8.31          |
| MSY                | PM10         | Rural        | Other           | ES           | 2018-01-11 00:00:00 | 2019-03-27 00:00:00 | 106          | 0.55           | 0.38           | 12.82         | 6.24          |
| OPE                | PM10         | Rural        | Other           | FR           | 2017-06-13 00:00:00 | 2020-12-29 00:00:00 | 200          | 0.6            | 0.4            | 9.54          | 6.54          |
| SRJV               | PM2.5        | Urban        | Valley          | BA           | 2022-08-20 00:00:00 | 2023-03-01 00:00:00 | 103          | 1.75           | 1.5            | 32.69         | 22.95         |
| ATH                | PM2.5        | Urban        | Coastal         | GR           | 2022-01-07 00:00:00 | 2023-12-06 00:00:00 | 152          | 1.92           | 1.2            | 24.7          | 16.61         |
| BCN                | PM2.5        | Urban        | Coastal         | ES           | 2018-01-03 00:00:00 | 2023-02-28 00:00:00 | 197          | 1.2            | 0.59           | 17.48         | 6.32          |
| BDP                | PM2.5        | Urban        | Other           | HU           | 2017-10-18 00:00:00 | 2018-08-01 00:00:00 | 61           | 1.8            | 1.23           | 15.03         | 8.69          |
| BERN               | PM2.5        | Traffic      | Other           | CH           | 2013-01-01 00:00:00 | 2020-12-29 00:00:00 | 644          | 1.27           | 0.74           | 12.61         | 7.52          |
| PARIS-lcpp         | PM2.5        | Urban        | Other           | FR           | 2020-11-07 00:00:00 | 2021-09-22 00:00:00 | 69           | 1.02           | 0.84           | 12.51         | 7.26          |
| LILLE              | PM2.5        | Urban        | Other           | FR           | 2023-04-03 00:00:00 | 2024-04-01 00:00:00 | 121          | 0.86           | 0.49           | 11.19         | 6.82          |
| ZURICH             | PM2.5        | Urban        | Other           | CH           | 2018-06-03 00:00:00 | 2019-05-29 00:00:00 | 90           | 0.83           | 0.56           | 10.8          | 6.97          |
| MGD                | PM2.5        | Rural        | Valley          | CH           | 2014-01-03 00:00:00 | 2019-05-29 00:00:00 | 153          | 0.88           | 0.86           | 10.61         | 7.2           |
| BASEL              | PM2.5        | Suburban     | Other           | CH           | 2018-06-03 00:00:00 | 2019-05-29 00:00:00 | 90           | 0.62           | 0.57           | 10.6          | 7.76          |
| PARIS-lh           | PM2.5        | Urban        | Other           | FR           | 2020-06-24 00:00:00 | 2023-09-26 00:00:00 | 806          | 0.8            | 0.55           | 10.48         | 6.27          |
| PAYRN              | PM2.5        | Rural        | Other           | CH           | 2013-01-01 00:00:00 | 2019-05-29 00:00:00 | 102          | 0.61           | 0.48           | 9.68          | 6.73          |
| MSY                | PM2.5        | Rural        | Other           | ES           | 2018-01-11 00:00:00 | 2019-03-31 00:00:00 | 107          | 0.44           | 0.3            | 9.62          | 4.68          |
| OPE                | PM2.5        | Rural        | Other           | FR           | 2014-01-01 00:00:00 | 2015-12-28 00:00:00 | 102          | 0.5            | 0.54           | 8.79          | 7.16          |
| BCN                | PM1          | Urban        | Coastal         | ES           | 2018-01-03 00:00:00 | 2019-03-15 00:00:00 | 94           | 0.87           | 0.41           | 14.71         | 4.91          |
| MRS-lcp            | PM1          | Urban        | Coastal         | FR           | 2022-12-10 00:00:00 | 2024-07-26 00:00:00 | 262          | 0.87           | 0.76           | 13.65         | 13.48         |
| KRAK               | PM1          | Urban        | Other           | PL           | 2018-01-23 00:00:00 | 2018-09-27 00:00:00 | 63           | 1.03           | 0.85           | 19.73         | 17.28         |
| MSY                | PM1          | Rural        | Other           | ES           | 2018-01-11 00:00:00 | 2019-03-31 00:00:00 | 94           | 0.35           | 0.2            | 9.35          | 4.39          |
"""

def load_data():
    # Read CSV, handling the markdown pipe format
    df = pd.read_csv(io.StringIO(csv_data), sep='|', skipinitialspace=True)
    
    # Clean column names (remove whitespace)
    df.columns = df.columns.str.strip()
    
    # Drop the first row (units) and any empty columns from markdown pipes
    df = df.iloc[1:].copy()
    df = df.dropna(axis=1, how='all')
    
    # Raw copy
    df_raw = df.copy()
    
    # Convert numeric columns
    numeric_cols = ['N_samples', 'OP_DTT_v_mean', 'OP_DTT_v_SD', 'PM_mass_mean', 'PM_mass_SD']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col])
        
    # Strip strings
    str_cols = ['Station', 'PM_size', 'Site_type', 'Site_topography', 'Country']
    for col in str_cols:
        df[col] = df[col].str.strip()
        
    return df_raw, df

def get_manual_order():
    # Order derived visually from the provided chart image
    order_pm10 = [
        'BERN', 'BOSSONS', 'RBX', 'STG-cle', # Traffic
        'CHAM', 'GRE-cb', 'GRE-fr', 'ZURICH', 'BCN', 'AIX', 'LENS', 'LYON', 'MRS-lcp', 'NICE', 'NOGENT', 'PARIS-lcpp', 'PARIS-lh', 'ROUEN', 'TAL', 'ATH', 'RDAM', 'KRAK', # Urban
        'KANAL', 'CALAIS', 'FSM', 'GSY', 'LHV', 'PDB', # Industrial
        'PASSY', 'BASEL', 'VIF', # Suburban
        'MGD', 'MARNAZ', 'COURMAY', 'PAYRN', 'MSY', 'ARREST', 'DIEPPE', 'OPE', 'PLOURZ' # Rural
    ]
    
    order_pm25 = [
        'BERN', # Traffic
        'SRJV', 'ZURICH', 'BCN', 'LILLE', 'PARIS-lcpp', 'PARIS-lh', 'ATH', 'BDP', # Urban
        'BASEL', # Suburban
        'MGD', 'PAYRN', 'MSY', 'OPE' # Rural
    ]
    
    order_pm1 = [
        'BCN', 'MRS-lcp', 'KRAK', # Urban
        'MSY' # Rural
    ]
    
    return {'PM10': order_pm10, 'PM2.5': order_pm25, 'PM1': order_pm1}

def get_tags():
    # Asterisks derived visually from the provided chart image
    # Key: (Station, PM_size) - string key "Station_PMSize" for JSON
    tags = {
        'BERN_PM10': '***', 'BOSSONS_PM10': '*', 'RBX_PM10': '**', 'STG-cle_PM10': '**',
        'CHAM_PM10': '*', 'GRE-cb_PM10': '*', 'GRE-fr_PM10': '****', 'ZURICH_PM10': '**',
        'BCN_PM10': '**', 'AIX_PM10': '*', 'LENS_PM10': '**', 'LYON_PM10': '**',
        'MRS-lcp_PM10': '**', 'NICE_PM10': '**', 'NOGENT_PM10': '**', 'PARIS-lcpp_PM10': '**',
        'PARIS-lh_PM10': '**', 'ROUEN_PM10': '**', 'TAL_PM10': '**', 'ATH_PM10': '**',
        'RDAM_PM10': '*', 'KANAL_PM10': '**', 'CALAIS_PM10': '**', 'GSY_PM10': '**',
        'LHV_PM10': '**', 'PDB_PM10': '**', 'PASSY_PM10': '***', 'BASEL_PM10': '*',
        'VIF_PM10': '**', 'MGD_PM10': '**', 'MARNAZ_PM10': '*', 'PAYRN_PM10': '**',
        'MSY_PM10': '**', 'ARREST_PM10': '**', 'DIEPPE_PM10': '**', 'OPE_PM10': '**',
        'PLOURZ_PM10': '**',
        
        'BERN_PM2.5': '***', 'SRJV_PM2.5': '**', 'ZURICH_PM2.5': '*', 'BCN_PM2.5': '*',
        'LILLE_PM2.5': '**', 'PARIS-lcpp_PM2.5': '*', 'PARIS-lh_PM2.5': '****', 'ATH_PM2.5': '*',
        'BDP_PM2.5': '*', 'BASEL_PM2.5': '*', 'MGD_PM2.5': '**', 'PAYRN_PM2.5': '**',
        'MSY_PM2.5': '**', 'OPE_PM2.5': '**',
        
        'BCN_PM1': '*', 'MRS-lcp_PM1': '**', 'KRAK_PM1': '*', 'MSY_PM1': '*'
    }
    return tags

def process_and_save():
    df_raw, df = load_data()
    orders = get_manual_order()
    tags = get_tags()
    
    pm_sizes = ['PM10', 'PM2.5', 'PM1']
    
    output = {}
    
    for pm_size in pm_sizes:
        sub_df = df[df['PM_size'] == pm_size].copy()
        
        # Sort based on manual order
        sub_df['Station'] = pd.Categorical(sub_df['Station'], categories=orders[pm_size], ordered=True)
        sub_df = sub_df.sort_values('Station')
        
        # Add tag column
        sub_df['tag'] = sub_df['Station'].apply(lambda x: tags.get(f"{x}_{pm_size}", ''))
        
        # Convert to list of dicts
        output[pm_size] = sub_df.to_dict(orient='records')
    
    return df_raw, output

if __name__ == "__main__":
    df_raw, processed_data = process_and_save()
    
    final_output = {
        "scr_data": df_raw.to_dict(orient='records'),
        "der_data": processed_data
    }
    
    with open('bench/ground_truth_code/nature_1_output/78.json', 'w') as f:
        json.dump(final_output, f, indent=4)
