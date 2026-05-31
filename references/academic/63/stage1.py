import sys
import io
import pandas as pd
import numpy as np
import json
import warnings

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

def process_data():
    # 1. Source Data (Figure 2C Gq)
    csv_data = """
|   Log [NT], M | 0 µM                | Unnamed: 2   | Unnamed: 3   | Unnamed: 4   | Unnamed: 5   | Unnamed: 6   | 1 µM      | Unnamed: 8   | Unnamed: 9   | Unnamed: 10   | Unnamed: 11   | Unnamed: 12   | 3 µM      | Unnamed: 14   | Unnamed: 15   | Unnamed: 16   | Unnamed: 17   | Unnamed: 18   | 10 µM     | Unnamed: 20   | Unnamed: 21   | Unnamed: 22   | Unnamed: 23   | Unnamed: 24   | 30 µM     | Unnamed: 26   | Unnamed: 27   | Unnamed: 28   | Unnamed: 29   | Unnamed: 30   |
|--------------:|:--------------------|:-------------|:-------------|:-------------|:-------------|:-------------|:----------|:-------------|:-------------|:--------------|:--------------|:--------------|:----------|:--------------|:--------------|:--------------|:--------------|:--------------|:----------|:--------------|:--------------|:--------------|:--------------|:--------------|:----------|:--------------|:--------------|:--------------|:--------------|:--------------|
|       nan     | 2022-09-29 00:00:00 | 9-29-2022    | 9-30-2022    | 9-30-2022    | 10-20-22     | 10-20-22     | 9-29-2022 | 9-29-2022    | 9-30-2022    | 9-30-2022     | 10-20-22      | 10-20-22      | 9-29-2022 | 9-29-2022     | 9-30-2022     | 9-30-2022     | 10-20-22      | 10-20-22      | 9-29-2022 | 9-29-2022     | 9-30-2022     | 9-30-2022     | 10-20-22      | 10-20-22      | 9-29-2022 | 9-29-2022     | 9-30-2022     | 9-30-2022     | 10-20-22      | 10-20-22      |
|         1e-05 | -0.31875            | -0.31636     | -0.28194     | -0.27913     | -0.30354736  | -0.30681852  | -0.15577  | -0.14897     | -0.10568     | -0.1098       | -0.25801      | -0.24023585   | -0.08267  | -0.06903      | -0.03529      | -0.03839      | -0.16693      | -0.15713096   | -0.00266  | -0.00864      | 0.015417      | 0.003493      | -0.05723      | -0.06330782   | 0.005226  | -0.00974      | 0.002996      | 0.032247      | -0.03033      | -0.02254235   |
|         1e-06 | -0.32254            | -0.31464     | -0.26736     | -0.27408     | -0.29769371  | -0.30410805  | -0.18082  | -0.1861      | -0.11885     | -0.1188       | -0.25976      | -0.26557425   | -0.08562  | -0.07424      | -0.05079      | -0.03249      | -0.17218      | -0.15901349   | 0.001009  | -0.01721      | 0.00824       | 0.032579      | -0.06013      | -0.05861463   | 0.008717  | -0.02238      | 0.037099      | -0.00106      | -0.01356      | -0.03370047   |
|         1e-07 | -0.33753            | -0.32178     | -0.28402     | -0.28163     | -0.30832869  | -0.30834301  | -0.17476  | -0.16928     | -0.12622     | -0.11248      | -0.25857      | -0.25861992   | -0.0812   | -0.06108      | -0.03184      | -0.03646      | -0.17514      | -0.16108356   | 0.015876  | -0.00739      | 0.021623      | 0.027191      | -0.06719      | -0.08202482   | 0.009194  | -0.00546      | 0.035348      | 0.011297      | -0.01598      | -0.03374237   |
|         1e-08 | -0.06722*           | -0.12007*    | -0.25006     | -0.25282     | -0.24566293  | -0.2214824   | -0.00356  | -0.00566     | -0.06509     | -0.06606      | -0.09856      | -0.12165324   | 0.017045  | 0.031883      | -0.00284      | -0.00934      | -0.05754      | -0.07172176   | 0.036412  | 0.018765      | 0.026237      | 0.034204      | -0.04157      | -0.03647502   | 0.021668  | -0.01445      | 0.022583      | 0.005766      | -0.00301      | -0.02075906   |
|         1e-09 | 0.01961*            | 0.041374*    | -0.14207     | -0.12111     | -0.01920335  | -0.013254    | 0.008171  | -0.01112     | -0.01821     | 0.008647      | -0.00155      | -0.0208003    | 0.006568  | 0.019405      | 0.050257      | 0.035472      | -0.02843      | -0.00845238   | 0.019551  | 0.000572      | 0.016662      | 0.026219      | -0.01509      | -0.01579574   | 0.000743  | -0.02787      | 0.044731      | -0.00268      | 0.001783      | -0.00935653   |
|         1e-10 | 0.014724            | 0.027173     | -0.00705     | 0.00852      | -0.00524545  | -0.00904603  | -0.01131  | -0.02103     | 0.025469     | 0.037488      | -0.00814      | -0.01858691   | -0.02637  | 0.001792      | 0.041488      | 0.050132      | -0.0201       | -0.004147     | -0.00115  | -0.01388      | 0.051546      | 0.065437      | -0.00705      | -0.02066939   | -0.01474  | -0.01876      | 0.051784      | 0.005034      | -0.01024      | -0.01627966   |
|         1e-11 | 0.006215            | 0.011279     | -0.00868     | 0.023732     | -0.01469926  | 0.006903366  | -0.01737  | -0.04154     | 0.002233     | 0.02203       | -0.01118      | -0.01623421   | -0.0325   | -0.0227       | 0.052718      | 0.025983      | -0.01104      | -0.00841572   | -0.01634  | -0.0236       | 0.055965      | 0.082599      | -0.0089       | -0.01569861   | -0.0268   | -0.02768      | 0.038036      | 0.020315      | 0.002334      | -0.00633934   |
|         1e-12 | -0.00371            | -0.01202     | -0.02449     | 0.009733     | -0.00787016  | -0.01005139  | -0.04273  | -0.04616     | 0.008922     | 0.002986      | -0.01038      | -0.02186704   | -0.03721  | -0.02849      | 0.036272      | 0.037963      | -0.00103      | 0.00099388    | -0.02295  | -0.01577      | 0.01792       | 0.042771      | -0.00667      | 0.004476628   | -0.02474  | -0.02614      | 0.0147        | 0.006906      | 0.000674      | -0.00557499   |
    """

    # 2. Data Parsing and Cleaning
    # Read markdown table
    df = pd.read_csv(io.StringIO(csv_data), sep="|", skipinitialspace=True)
    
    # Drop the first and last columns which are just markdown pipes
    df = df.iloc[:, 1:-1]
    
    # The first row in the data contains dates/metadata, remove it
    df = df.iloc[1:].reset_index(drop=True)
    
    # Clean data: remove asterisks and convert to float
    for col in df.columns:
        df[col] = df[col].astype(str).str.replace('*', '', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 3. Organize Data by Concentration Groups
    # X-axis: Log [NT], M. The values are linear (1e-5, etc), we need to log10 transform them.
    x_linear = df.iloc[:, 0].values
    x_log = np.log10(x_linear)

    # Define groups based on column structure
    groups = [
        {'label': '0 µM',  'cols_start': 1, 'cols_end': 7,   'color': '#00008B'}, # Dark Blue
        {'label': '1 µM',  'cols_start': 7, 'cols_end': 13,  'color': '#6A5ACD'}, # Slate Blue
        {'label': '3 µM',  'cols_start': 13, 'cols_end': 19, 'color': '#9370DB'}, # Medium Purple
        {'label': '10 µM', 'cols_start': 19, 'cols_end': 25, 'color': '#BA55D3'}, # Medium Orchid
        {'label': '30 µM', 'cols_start': 25, 'cols_end': 31, 'color': '#DDA0DD'}, # Plum
    ]
    
    scr_data = []
    der_data = []
    
    for group in groups:
        # Extract Y data for this group
        y_data_raw = df.iloc[:, group['cols_start']:group['cols_end']]
        
        # Calculate Mean and SEM (Standard Error of Mean)
        y_mean = y_data_raw.mean(axis=1).values
        y_sem = y_data_raw.sem(axis=1).values
        
        der_data.append({
            'label': group['label'],
            'color': group['color'],
            'x_log': x_log.tolist(),
            'y_mean': y_mean.tolist(),
            'y_sem': y_sem.tolist()
        })
        
        # Source Data extraction
        # We store the raw values for each x-point for this group
        group_raw_values = []
        for idx, x_val in enumerate(x_log):
            replicates = y_data_raw.iloc[idx].tolist()
            group_raw_values.append({
                "x_log": x_val,
                "replicates": replicates
            })
            
        scr_data.append({
            "label": group['label'],
            "data": group_raw_values
        })
        
    return {"scr_data": scr_data, "der_data": der_data}

def main():
    data = process_data()
    output_path = "bench/ground_truth_code/nature_1_output/63.json"
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    main()
