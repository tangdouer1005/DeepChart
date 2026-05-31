import sys
import io
import pandas as pd
import json
from scipy import stats # Import stats for Pearson correlation
import numpy as np

def compile_data(output_filename):
    # 1. Load Source Data
    nsf_csv = """unit|fund_norm|gdp_norm
Alachua, Florida|0.393397|0.0154887
Alameda, California|0.0109455|0.209677
Albany, New York|0.352985|0.0403226
Albemarle, Virginia|0.0429196|0.00595238
Allegheny, Pennsylvania|0.2474|0.134601
Barnstable, Massachusetts|0.210292|0.0104647
Benton, Arkansas|0.267752|0.0197773
Bexar, Texas|0.0109484|0.143721
Boulder, Colorado|0.19847|0.031298
Brazos, Texas|0.327723|0.0112327
Centre, Pennsylvania|0.0233701|0.0114247
Champaign, Illinois|0.344173|0.0113287
Cleveland, Oklahoma|0.0109484|0.015841
Coconino, Arizona|0.205369|0.00854455
Cook, Illinois|0.563428|0.71611
Cumberland, Maine|0.103504|0.0259217
Cuyahoga, Ohio|0.0393818|0.169931
Davidson, Tennessee|1|0.0869816
DeKalb, Georgia|0.0765153|0.0200653
Delaware, Pennsylvania|0.0108724|0.0560676
Douglas, Kansas|0.12569|0.00729647
Douglas, Nebraska|0.103833|0.0393625
Douglas, Nevada|0.00990158|0.0062404
Durham, North Carolina|0.0525111|0.046563
El Paso, Texas|0.158379|0.0321621
Erie, New York|0.213113|0.0383065
Fayette, Kentucky|0.0545489|0.031682
Fulton, Georgia|0.791746|0.220142
Hampshire, Massachusetts|0.0106141|0.00604839
Harris, Texas|0.14536|0.689708
Hennepin, Minnesota|0.185887|0.275058
Hillsborough, Florida|0.162688|0.131816
Houghton, Michigan|0.125677|0.000576037
Jackson, Missouri|0.0729075|0.102247
King, Washington|0.723896|0.460253
Knox, Tennessee|0.0273401|0.031394
Leon, Florida|0.0747808|0.015361
Los Angeles, California|0.331466|0.756624
Lubbock, Texas|0.0109398|0.0120968
Maricopa, Arizona|0.253546|0.324021
McLennan, Texas|2.05443e-05|0.0165131
Mecklenburg, North Carolina|0.245564|0.157354
Miami-Dade, Florida|0.0491464|0.149674
Middlesex, Massachusetts|0.305412|0.262289
Middlesex, New Jersey|0.413311|0.114247
Milwaukee, Wisconsin|0.103835|0.0817972
Missoula, Montana|0.0109481|0.00604839
Monongalia, West Virginia|0|0.00451229
Monroe, New York|0.158474|0.0341782
Montgomery, Ohio|0.0288705|0.0404186
New Haven, Connecticut|0.0382679|0.0534754
New York, New York|0.454125|1
Norfolk, Virginia|0.298713|0.0408026
Orange, California|0.870387|0.315476
Orange, Florida|0.134761|0.0999424
Phelps, Missouri|0.219031|0.000288018
Philadelphia, Pennsylvania|0.0950925|0.490783
Pickens, South Carolina|0.28414|0.00614439
Pima, Arizona|0.109744|0.0449309
Prince George's, Maryland|0.311065|0.0549155
Richland, South Carolina|0.0109462|0.0219854
Riley, Kansas|0.0109484|0.00528034
Salt Lake, Utah|0.147199|0.105511
San Diego, California|0.0126967|0.271025
Santa Barbara, California|0.0109484|0.0508833
Santa Clara, California|0.127786|0.404378
Santa Cruz, California|0.165685|0.0169931
Sedgwick, Kansas|0.117249|0.0324501
Socorro, New Mexico|0.0109483|0
St. Joseph, Indiana|2.05443e-05|0.015841
Story, Iowa|0.74758|0.00768049
Suffolk, Massachusetts|0.717179|0.309044
Suffolk, New York|0.275852|0.0947581
Tarrant, Texas|0.256798|0.203533
Tippecanoe, Indiana|0.42949|0.015169
Tompkins, New York|0.152897|0.00796851
Travis, Texas|0.371719|0.210061
Tuscaloosa, Alabama|0.0382679|0.0116167
Wake, North Carolina|0.231472|0.140553
Waller, Texas|0.0317551|0.00441628
Washington, D.C.|0.368165|0.133545
Washoe, Nevada|0.0106243|0.0235215
Washtenaw, Michigan|0.634831|0.0331221
Wayne, Michigan|2.0435e-05|0.188364
Worcester, Massachusetts|2.0435e-05|0.0961022"""

    nsfc_csv = """unit|fund_norm|gdp_norm
Beijing|1|0.930411
Changchun|0.00175961|0.121839
Changsha|0.150526|0.277033
Chengdu|0.13405|0.425905
Chongqing|0.0220751|0.606356
Dalian|0.0153566|0.151893
Fuzhou|0.00972582|0.21731
Guangzhou|0.258502|0.606991
Guilin|0.080302|0.0178722
Guiyang|0.0188118|0.0708199
Hangzhou|0.527562|0.381016
Harbin|0.123972|0.103911
Hefei|0.0505487|0.217775
Huzhou|0.0147167|0.0457042
Jiaozuo|0.00127971|0.035815
Jinan|0.0278338|0.218706
Kunming|0.0166363|0.137496
Lanzhou|0.0156765|0.0378925
Linfen|0|0
Nanchang|0.0287296|0.113409
Nanjing|0.300285|0.344284
Shanghai|0.348722|1
Shenyang|0.00550277|0.137332
Shenzhen|0.0976741|0.697261
Suzhou|0.0633458|0.486745
Tianjin|0.0467095|0.344954
Wuhan|0.52785|0.404281
Xi'an|0.0852289|0.215366
Xiamen|0.0108776|0.12433
Xiangtan|0.0143968|0.0220337
Xuzhou|0.00127971|0.155981
Yiyang|0.013437|0.00930233
Zhengzhou|0.08926|0.277471"""

    # Load dataframes
    df_nsf = pd.read_csv(io.StringIO(nsf_csv), sep='|')
    df_nsfc = pd.read_csv(io.StringIO(nsfc_csv), sep='|')

    # 2. Calculate Statistics for Legend
    def calculate_stats(df):
        # Ensure data types are numeric before calculation
        df['gdp_norm'] = pd.to_numeric(df['gdp_norm'], errors='coerce')
        df['fund_norm'] = pd.to_numeric(df['fund_norm'], errors='coerce')
        
        # Drop rows with NaN values that resulted from coercion
        df = df.dropna(subset=['gdp_norm', 'fund_norm'])
        
        r, p = stats.pearsonr(df['gdp_norm'], df['fund_norm'])
        return r, p

    r_nsf, p_nsf = calculate_stats(df_nsf)
    r_nsfc, p_nsfc = calculate_stats(df_nsfc)

    # 3. Add Median Lines
    # Calculate medians of the combined dataset
    combined_gdp = pd.concat([df_nsf['gdp_norm'], df_nsfc['gdp_norm']])
    combined_fund = pd.concat([df_nsf['fund_norm'], df_nsfc['fund_norm']])

    median_gdp = combined_gdp.median()
    median_fund = combined_fund.median()

    # 4. Annotations (Labels)
    # Define mapping for NSF labels (Full State Name -> Abbreviation)
    # Only mapping the specific points seen in the chart
    nsf_labels_map = {
        "Davidson, Tennessee": "Davidson, TN",
        "Orange, California": "Orange, CA",
        "Fulton, Georgia": "Fulton, GA",
        "Suffolk, Massachusetts": "Suffolk, MA",
        "King, Washington": "King, WA",
        "Story, Iowa": "Story, IA",
        "Washtenaw, Michigan": "Washtenaw, MI",
        "Cook, Illinois": "Cook, IL",
        "New York, New York": "New York, NY",
        "Los Angeles, California": "Los Angeles, CA",
        "Harris, Texas": "Harris, TX"
    }

    nsfc_labels_list = [
        "Beijing", "Hangzhou", "Wuhan", "Guangzhou", 
        "Shanghai", "Shenzhen", "Chongqing"
    ]

    # Prepare scr_data
    scr_data = []
    for record in df_nsf.to_dict(orient='records'):
        record['source'] = 'NSF'
        scr_data.append(record)
    for record in df_nsfc.to_dict(orient='records'):
        record['source'] = 'NSFC'
        scr_data.append(record)

    # Prepare der_data
    der_data = [
        {'metric': 'r_nsf', 'value': r_nsf},
        {'metric': 'p_nsf', 'value': p_nsf},
        {'metric': 'r_nsfc', 'value': r_nsfc},
        {'metric': 'p_nsfc', 'value': p_nsfc},
        {'metric': 'median_gdp', 'value': median_gdp},
        {'metric': 'median_fund', 'value': median_fund},
        {'type': 'nsf_labels_map', 'value': nsf_labels_map},
        {'type': 'nsfc_labels_list', 'value': nsfc_labels_list}
    ]

    # Final output structure
    final_output = {
        'scr_data': scr_data,
        'der_data': der_data
    }

    # Save to JSON
    with open(output_filename, 'w') as f:
        json.dump(final_output, f, indent=4)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_2_output/178.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compile_data(output_file)
