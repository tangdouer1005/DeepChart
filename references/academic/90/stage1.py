import pandas as pd
import io
import json
import os
import numpy as np

def process_data(output_filename='bench/ground_truth_code/nature_2_output/90.json'):
    # 1. Source Data
    csv_data = """| Fig. 1g             | Unnamed: 1         | Unnamed: 2         | Unnamed: 3         | Unnamed: 4         | Unnamed: 5         | Unnamed: 6         | Unnamed: 7         | Unnamed: 8         | Unnamed: 9         |   Unnamed: 10 | Unnamed: 11                               | Unnamed: 12        | Unnamed: 13                         | Unnamed: 14   | Unnamed: 15        | Unnamed: 16      | Unnamed: 17   | Unnamed: 18       | Unnamed: 19   | Unnamed: 20   |
|:--------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|--------------:|:------------------------------------------|:-------------------|:------------------------------------|:--------------|:-------------------|:-----------------|:--------------|:------------------|:--------------|:--------------|
| FSP1 protein levels | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |           nan | nan                                       | nan                | nan                                 | nan           | nan                | nan              | nan           | nan               | nan           | nan           |
| B16-F0              | LN1 18IL           | LN7 1112AR         | LN7 1120BL         | LN7 1134BL         | LN8 1194BR         | LN8 1198AR         | LN8 1205BL         | LN9 1315BL         | LN9 1358IR         |           nan | Table Analyzed                            | Fig. 1g            | Dunnett's multiple comparisons test | Mean diff.    | 95.00% CI of diff. | Below threshold? | Summary       | Adjusted P Value  | A-?           | nan           |
| 0.8709716083391996  | 1.549737091580455  | 2.850802126911562  | 4.285395632319021  | 3.1159567335299294 | 2.7555710244555778 | 3.1989135425398    | 1.1099025962411833 | 1.6594961664147203 | 2.720926327731109  |           nan | Data sets analyzed                        | A-J                | B16-F0 vs. LN1 18IL                 | -0.3754       | -0.7842 to 0.03352 | No               | ns            | 0.091610521392838 | B             | LN1 18IL      |
| 1.163636166577947   | 1.8401402380371499 | 2.831017458797632  | 3.8618899449324937 | 2.4972600558469304 | 2.6959670511319116 | 3.1224259486974386 | 1.3041709489940583 | 2.2613087425334126 | 1.7118141094963655 |           nan | Distribution assumption                   | Normal (Gaussian)  | B16-F0 vs. LN7 1112AR               | -1.661        | -2.262 to -1.059   | Yes              | ****          | 3.2727e-11        | C             | LN7 1112AR    |
| 0.9655449807231169  | 1.6521837208879588 | 2.937364610340302  | 5.009290288466751  | 2.8062076929116637 | 2.7880997823966487 | 1.5357605307222275 | 1.794586399282931  | 2.413476981833502  | 2.641496941582993  |           nan | nan                                       | nan                | B16-F0 vs. LN7 1120BL               | -2.377        | -2.979 to -1.775   | Yes              | ****          | 4e-15             | D             | LN7 1120BL    |
| 0.8597330379618892  | 1.2542451674858575 | 2.1770580978498817 | 2.2671921259682297 | 2.3771580806350006 | 2.9460697874311013 | 2.27619231605305   | 1.8198042685089366 | 1.263143683138213  | 4.853379099245915  |           nan | ANOVA summary                             | nan                | B16-F0 vs. LN7 1134BL               | -1.85         | -2.452 to -1.248   | Yes              | ****          | 2.9e-13           | E             | LN7 1134BL    |
| 1.176093947359024   | 1.3388246029929656 | 2.1268461939871033 | 2.5310387071115925 | 2.516819306046498  | 2.6825772530485756 | 2.3681003175586777 | 1.6813632372345209 | 2.6985598402872495 | 2.6282460361245796 |           nan | F                                         | 30.2               | B16-F0 vs. LN8 1194BR               | -1.68         | -2.221 to -1.139   | Yes              | ****          | 1.81e-13          | F             | LN8 1194BR    |
| 0.9649672859886522  | 1.2457475092264052 | 2.3192470705407002 | 2.9477890320349607 | 2.8337094105335874 | 2.6625537164540276 | 2.577699599539925  | 1.6071165932144746 | 2.2963958768441155 | 3.047416468169401  |           nan | P value                                   | <0.000000000000001 | B16-F0 vs. LN8 1198AR               | -1.771        | -2.312 to -1.230   | Yes              | ****          | 1.7e-14           | G             | LN8 1198AR    |
| 0.8904168718543946  | 1.462742400084962  | 4.047197358133228  | 4.813490147713096  | 3.663191672688194  | 2.0714761978996012 | 2.2386721533780003 | 1.7509587691265476 | nan                | nan                |           nan | P value summary                           | ****               | B16-F0 vs. LN8 1205BL               | -0.8136       | -1.355 to -0.2727  | Yes              | ***           | 0.000454712621187 | H             | LN8 1205BL    |
| 1.0725268751993908  | 1.5541405295450688 | 2.0097585016774935 | 2.0512039066750813 | 2.6744810776251273 | 2.0925956049722227 | 2.353859329808663  | 1.5222738827015716 | nan                | nan                |           nan | Significant diff. among means (P < 0.05)? | Yes                | B16-F0 vs. LN9 1315BL               | -1.099        | -1.807 to -0.3904  | Yes              | ***           | 0.000273075453655 | I             | LN9 1315BL    |
| 1.0380790144390275  | 1.5530468086723124 | 2.647457713277039  | 2.6243034434553247 | 3.168788574091623  | 2.1163458596200266 | 2.473936441317873  | 1.8334214971755416 | nan                | nan                |           nan | R squared                                 | 0.685              | B16-F0 vs. LN9 1358IR               | -1.934        | -2.642 to -1.226   | Yes              | ****          | 4.998e-11         | J             | LN9 1358IR    |
| 1.1453606777036145  | 1.7943759076129866 | nan                | nan                | nan                | 4.105397133510845  | 5.2015137457526155 | 2.5129551901243325 | nan                | nan                |           nan | nan                                       | nan                | nan                                 | nan           | nan                | nan              | nan           | nan               | nan           | nan           |
| 0.8833249802905037  | 1.679568758448755  | nan                | nan                | nan                | 2.4192618935795838 | 2.5844047422525778 | 3.04541240900302   | nan                | nan                |           nan | nan                                       | nan                | nan                                 | nan           | nan                | nan              | nan           | nan               | nan           | nan           |
| 0.9714125397543188  | 1.6679331203191494 | nan                | nan                | nan                | 2.824200471110591  | 3.3221986518454028 | 1.783632147964823  | nan                | nan                |           nan | nan                                       | nan                | nan                                 | nan           | nan                | nan              | nan           | nan               | nan           | nan           |
| 0.9924852259159755  | 1.6918266116105038 | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |           nan | nan                                       | nan                | nan                                 | nan           | nan                | nan              | nan           | nan               | nan           | nan           |
| 0.9177934727647518  | 1.8423120308000593 | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |           nan | nan                                       | nan                | nan                                 | nan           | nan                | nan              | nan           | nan               | nan           | nan           |
| 1.089823273581349   | 1.6683607060951646 | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |           nan | nan                                       | nan                | nan                                 | nan           | nan                | nan              | nan           | nan               | nan           | nan           |
| 0.9572414622115825  | 1.368419886609368  | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |           nan | nan                                       | nan                | nan                                 | nan           | nan                | nan              | nan           | nan               | nan           | nan           |
| 0.989919438617107   | 1.7096584994119155 | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |           nan | nan                                       | nan                | nan                                 | nan           | nan                | nan              | nan           | nan               | nan           | nan           |
| 1.0536712551188123  | 1.3301776296894665 | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |           nan | nan                                       | nan                | nan                                 | nan           | nan                | nan              | nan           | nan               | nan           | nan           |
| 1.2325350499581258  | 1.12561397270971   | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |           nan | nan                                       | nan                | nan                                 | nan           | nan                | nan              | nan           | nan               | nan           | nan           |
| 0.8528342210715382  | 0.916013041939194  | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |           nan | nan                                       | nan                | nan                                 | nan           | nan                | nan              | nan           | nan               | nan           | nan           |
| 0.9148067493803628  | 1.327349359914708  | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |           nan | nan                                       | nan                | nan                                 | nan           | nan                | nan              | nan           | nan               | nan           | nan           |
| 1.2699145962304776  | 0.9279254121332988 | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |           nan | nan                                       | nan                | nan                                 | nan           | nan                | nan              | nan           | nan               | nan           | nan           |
| 0.8468665013964249  | 0.8369649327189256 | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |           nan | nan                                       | nan                | nan                                 | nan           | nan                | nan              | nan           | nan               | nan           | nan           |
| 0.883764678672027   | 0.6954857454040407 | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |           nan | nan                                       | nan                | nan                                 | nan           | nan                | nan              | nan           | nan               | nan           | nan           |
| 1.224122315643644   | 1.1440898791454082 | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |           nan | nan                                       | nan                | nan                                 | nan           | nan                | nan              | nan           | nan               | nan           | nan           |
| 0.77936863332052    | 0.9518361526174307 | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |           nan | nan                                       | nan                | nan                                 | nan           | nan                | nan              | nan           | nan               | nan           | nan           |
| 0.9970336321197293  | 1.0673735989212343 | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |           nan | nan                                       | nan                | nan                                 | nan           | nan                | nan              | nan           | nan               | nan           | nan           |
| 1.0000001351314967  | 1.2423290473908908 | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |           nan | nan                                       | nan                | nan                                 | nan           | nan                | nan              | nan           | nan               | nan           | nan           |
| 1.000215886511742   | 1.1042231802244027 | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |           nan | nan                                       | nan                | nan                                 | nan           | nan                | nan              | nan           | nan               | nan           | nan           |
| 1.0000899043170295  | 1.7229104069894439 | nan                | nan                | nan                | nan                | nan                | nan                | nan                | nan                |           nan | nan                                       | nan                | nan                                 | nan           | nan                | nan              | nan           | nan               | nan           | nan           |"""

    # 2. Data Processing
    # Read raw data
    df_raw = pd.read_csv(io.StringIO(csv_data), sep="|", header=None, skipinitialspace=True)
    
    # Drop columns that are completely empty (often first/last due to markdown pipes)
    df_raw = df_raw.dropna(axis=1, how='all')
    
    # Reset column indices to be sequential 0..N
    df_raw.columns = range(df_raw.shape[1])
    
    # Find the header row (contains "B16-F0")
    header_row_idx = None
    for idx, row in df_raw.iterrows():
        # Convert row to string list to search
        row_vals = [str(x).strip() for x in row.values]
        if "B16-F0" in row_vals:
            header_row_idx = idx
            break
            
    if header_row_idx is None:
        raise ValueError("Could not find header row containing 'B16-F0'")
        
    # Extract headers
    headers = [str(x).strip() for x in df_raw.iloc[header_row_idx].values]
    
    # The first 10 columns are the data groups
    group_names = headers[:10]
    
    # Data rows are below the header
    df_data = df_raw.iloc[header_row_idx+1:].copy()
    
    # Extract Data into dict
    group_data = {}
    for i, group in enumerate(group_names):
        # Extract data for this group
        # Column index i corresponds to the group in df_data
        series = pd.to_numeric(df_data.iloc[:, i], errors='coerce').dropna().tolist()
        group_data[group] = series

    # Extract P-values
    try:
        comp_col_idx = next(i for i, h in enumerate(headers) if "Dunnett" in h or "comparisons test" in h)
        pval_col_idx = next(i for i, h in enumerate(headers) if "Adjusted P Value" in h)
    except StopIteration:
        # Fallback indices based on table structure if names don't match exactly
        comp_col_idx = 13
        pval_col_idx = 18

    p_value_map = {}
    for idx, row in df_data.iterrows():
        try:
            comp_str = str(row.iloc[comp_col_idx])
            pval_val = row.iloc[pval_col_idx]
            
            if "B16-F0 vs." in comp_str:
                target = comp_str.replace("B16-F0 vs.", "").strip()
                # Clean target name to match group names (handle potential spaces)
                
                # Check for "nan" string
                if str(pval_val).lower() == 'nan':
                    continue
                    
                p = float(pval_val)
                p_value_map[target] = p
        except (ValueError, TypeError, IndexError):
            continue
            
    output_data = {
        'group_data': group_data,
        'p_values': p_value_map
    }

    return csv_data, output_data

if __name__ == "__main__":
    raw_csv_str, processed_derived_data = process_data()
    
    final_output = {
        "scr_data": raw_csv_str,
        "der_data": processed_derived_data
    }
    
    output_filename = 'bench/ground_truth_code/nature_1_output/90.json'
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    with open(output_filename, 'w') as f:
        json.dump(final_output, f, indent=4)
        
    print(f"Data saved to {output_filename}")