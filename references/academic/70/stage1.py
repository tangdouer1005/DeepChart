import sys
import io
import numpy as np
import pandas as pd
import json

def get_data():
    """
    Returns the raw data for Figure 3A Gi1 as a string.
    """
    return """
|   Compound | Vehicle          | Unnamed: 2      | Unnamed: 3     | Unnamed: 4     | Unnamed: 5      | Unnamed: 6     | Unnamed: 7     | Unnamed: 8     | Unnamed: 9      | Vehicle + 100 nM NT   | Unnamed: 11   | Unnamed: 12   | Unnamed: 13   | Unnamed: 14   | Unnamed: 15   | Unnamed: 16   | Unnamed: 17   | Unnamed: 18   | SBI-553 + 100 nM NT   | Unnamed: 20   | Unnamed: 21   | Unnamed: 22   | Unnamed: 23   | Unnamed: 24   | Unnamed: 25   | Unnamed: 26   | Unnamed: 27          | SR142948A + 100 nM NT   | Unnamed: 29     | Unnamed: 30     | Unnamed: 31    | Unnamed: 32    | Unnamed: 33    | Unnamed: 34    | Unnamed: 35    | Unnamed: 36     |
|-----------:|:-----------------|:----------------|:---------------|:---------------|:----------------|:---------------|:---------------|:---------------|:----------------|:----------------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:----------------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:---------------------|:------------------------|:----------------|:----------------|:---------------|:---------------|:---------------|:---------------|:---------------|:----------------|
|   nan      | 3/14/24          | 3/14/24         | 3/14/24        | 3/7/24         | 3/7/24          | 3/7/24         | 3/1/24         | 3/1/24         | 3/1/24          | 3/14/24               | 3/14/24       | 3/14/24       | 3/7/24        | 3/7/24        | 3/7/24        | 3/1/24        | 3/1/24        | 3/1/24        | 3/14/24               | 3/14/24       | 3/14/24       | 3/7/24        | 3/7/24        | 3/7/24        | 3/1/24        | 3/1/24        | 3/1/24               | 3/14/24                 | 3/14/24         | 3/14/24         | 3/7/24         | 3/7/24         | 3/7/24         | 3/1/24         | 3/1/24         | 3/1/24          |
|     3e-05  | nan              | nan             | nan            | nan            | nan             | nan            | nan            | nan            | nan             | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan                   | nan           | nan           | nan           | nan           | nan           | 0.05940910011 | 0.04835571143 | 0.04968631966        | nan                     | nan             | nan             | nan            | nan            | nan            | nan            | nan            | nan             |
|     1e-05  | nan              | nan             | nan            | nan            | nan             | nan            | nan            | nan            | nan             | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan                   | nan           | nan           | nan           | nan           | nan           | 0.04200852799 | 0.04919381149 | 0.04709571688        | nan                     | nan             | nan             | nan            | nan            | nan            | nan            | nan            | nan             |
|     3e-06  | nan              | nan             | nan            | nan            | nan             | nan            | nan            | nan            | nan             | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.04721542789         | 0.04582151253 | 0.04534709956 | 0.04716972101 | 0.05933557087 | 0.05110333657 | 0.04513166429 | 0.04503873974 | 0.04583802348        | nan                     | nan             | nan             | nan            | nan            | nan            | nan            | nan            | nan             |
|     1e-06  | nan              | nan             | nan            | nan            | nan             | nan            | nan            | nan            | nan             | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.04485072705         | 0.04531686469 | 0.04370022059 | 0.05679628984 | 0.05286270082 | 0.0468382903  | 0.0467026791  | 0.04910479048 | 0.04561814096        | nan                     | nan             | nan             | nan            | nan            | nan            | nan            | nan            | nan             |
|     3e-07  | nan              | nan             | nan            | nan            | nan             | nan            | nan            | nan            | nan             | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.04202244191         | 0.04775041093 | 0.04679663476 | 0.04827861388 | 0.04754708271 | 0.0430833978  | 0.04839383463 | 0.04293536753 | 0.048678568480000003 | nan                     | nan             | nan             | nan            | nan            | nan            | nan            | nan            | nan             |
|     1e-07  | nan              | nan             | nan            | nan            | nan             | nan            | nan            | nan            | nan             | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.04850327466         | 0.05102454658 | 0.0533531262  | 0.04907400014 | 0.04939437165 | 0.0477982569  | 0.04090282151 | 0.04673524355 | 0.04446491453        | nan                     | nan             | nan             | nan            | nan            | nan            | nan            | nan            | nan             |
|     3e-08  | nan              | nan             | nan            | nan            | nan             | nan            | nan            | nan            | nan             | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.06025884347         | 0.05963051812 | 0.05550548748 | 0.05662037184 | 0.06160580703 | 0.06467138271 | 0.05822859202 | 0.0488551659  | 0.05694555764        | nan                     | nan             | nan             | nan            | nan            | nan            | nan            | nan            | nan             |
|     1e-08  | nan              | nan             | nan            | nan            | nan             | nan            | nan            | nan            | nan             | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.06902591057         | 0.07190598716 | 0.06771303856 | 0.06586410428 | 0.07498586467 | 0.07187508519 | nan           | nan           | nan                  | nan                     | nan             | nan             | nan            | nan            | nan            | nan            | nan            | nan             |
|     3e-09  | nan              | nan             | nan            | nan            | nan             | nan            | nan            | nan            | nan             | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.08505878531         | 0.0872567618  | 0.08409054528 | 0.07436501819 | 0.08470138138 | 0.08468449666 | nan           | nan           | nan                  | nan                     | nan             | nan             | nan            | nan            | nan            | nan            | nan            | nan             |
|     1e-11  | nan              | nan             | nan            | nan             | nan            | nan            | nan            | nan            | nan             | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.1061633104          | 0.1098992745  | 0.1024509615  | 0.1023431175  | 0.1025867304  | 0.1109825891  | 0.09681798113 | 0.1033426694  | 0.1013971667         | nan                     | nan             | nan             | nan            | nan            | nan            | nan            | nan            | nan             |
|   nan      | nan              | nan             | nan            | nan             | nan            | nan            | nan            | nan            | nan             | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan                  | nan                     | nan             | nan             | nan            | nan            | nan            | nan            | nan            | nan             |
|     0.0001 | -0.002202054028  | 0.002982846469  | 0.003305744747 | 0.00198729732  | 0.004592223117  | 0.005006006419 | 0.003369184796 | 0.002299374792 | -0.00189304168  | 0.1142498422          | 0.1091077052  | 0.1055389894  | 0.1051089289  | 0.09158554611 | 0.1009077815  | 0.09250549918 | 0.09894119655 | 0.09013634379 | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan                  | 0.002850065555          | -0.001128302888 | -0.002061776664 | 0.002989532247 | 0.002322408092 | 0.007001054028 | 0.004964425932 | 0.001991811188 | 0.008956029957  |
|     1e-05  | 7.971817887e-05  | 0.001645081782  | 0.002610728046 | 0.005058787383 | 0.007769971458  | 0.005663763636 | 0.00490269982  | 0.008244637168 | 0.0007798859362 | 0.1036476895          | 0.1068348258  | 0.1082771024  | 0.09788312319 | 0.09132404232 | 0.1044030597  | 0.1080674384  | 0.1042112563  | 0.1028465261  | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan                  | 0.002550277503          | 0.0001317375323 | -0.003876358931 | 0.00255033119  | 0.005489423803 | 0.004781430764 | 0.003662748059 | 0.003308933828 | 0.0001935486292 |
|     1e-06  | -0.0003030741624 | 0.0005829566638 | 0.002379529723 | 0.002463481408 | 0.003203121356  | 0.001951378786 | 0.001198261503 | 0.009168247089 | 0.004679974552  | 0.09320084744         | 0.1012456352  | 0.1035102486  | 0.1073259997  | 0.1086500218  | 0.1071066517  | 0.1004239895  | 0.09902268936 | 0.09902181937 | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan                  | 0.001629847913          | 0.001742851514  | 0.004883844699  | 0.007272678791 | 0.005520111523 | 0.005899369122 | 0.004486689736 | 0.001686434315 | 0.002794662334  |
|     1e-07  | -0.000932346276  | 0.002279511459  | 0.002267818424 | 0.01012433715  | 0.00138225444   | 0.003925480626 | 0.005202102373 | 0.001645057542 | 0.009649542574  | 0.1023973695          | 0.1022126597  | 0.0953554632  | 0.1081099028  | 0.09461861877 | 0.1073831628  | 0.105873692   | 0.09499147149 | 0.0926954775  | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan                  | 0.01993685005           | 0.01837762942   | 0.0150749496    | 0.02433376639  | 0.03135951632  | 0.03006307881  | 0.01499883398  | 0.01454803816  | 0.007974712733  |
|     1e-08  | 0.0009596372366  | 0.00184688247   | 0.001989479983 | 0.003559399295 | 0.007026542937  | 0.008410916095 | 0.005236295072 | 0.01147370826  | 0.002157077269  | 0.1062587441          | 0.1054426017  | 0.1044477701  | 0.09727282808 | 0.1065460897  | 0.1067034147  | 0.1000469404  | 0.09558999098 | 0.097411003   | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan                  | 0.05964041159           | 0.05576335157   | 0.05990687653   | 0.07883604646  | 0.08081620596  | 0.06660086674  | 0.04158657689  | 0.05417075422  | 0.04057244104   |
|     1e-09  | 0.002166236219   | 0.001879202318  | 0.001892500342 | 0.01029234836  | 0.001195049352  | 0.005555353932 | 0.004935095151 | 0.006639409032 | 0.005738587377 | 0.1127857676          | 0.1002396852  | 0.1068987424  | 0.08679365488 | 0.08927607562 | 0.09874228549 | 0.09325002409 | 0.08847846527 | 0.09310715451 | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan                  | 0.08306486394           | 0.08530945219   | 0.09698612104   | 0.1007506015   | 0.08086539784  | 0.111676542    | 0.07237840963  | 0.08462165662  | 0.06887929863   |
|     1e-10  | 0.00115836765    | 8.20691624e-05  | 0.001379123397 | 0.003159683066 | -0.000333235655 | 0.003960251276 | 0.006114651857 | 0.001571020634 | 0.003425091585  | 0.1010050687          | 0.1057956594  | 0.1023469211  | 0.09665855203 | 0.0955164436  | 0.104598675   | 0.09412634995 | 0.09381698386 | 0.09160574384 | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan                  | 0.102535988             | 0.1005502889    | 0.1097392812    | 0.104601464    | 0.0901670288   | 0.09931273047  | 0.09111034815  | 0.09808424166  | 0.08493820848   |
|     1e-11  | 0.002128805274   | 0.002123674037  | 0.002502525762 | 0.006905160232 | 0.004217772289  | 0.006008153319 | 0.004504195958 | 0.005014856972 | 0.003940224183  | 0.1159779127          | 0.1099366709  | 0.1115405943  | 0.1012336121  | 0.1018662848  | 0.1056038823  | 0.1011959522  | 0.09269329664 | 0.1077416993  | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan                  | 0.1036725183            | 0.1046121897    | 0.1034419086    | 0.1090603382   | 0.1008563335   | 0.1061044374   | 0.09062705347  | 0.1142558643   | 0.09150908826   |
"""

def parse_data(data_str):
    """
    Parses the markdown table string into a structured DataFrame.
    """
    # Read CSV from string, handling the markdown pipe separators
    df = pd.read_csv(io.StringIO(data_str), sep="|", skipinitialspace=True)
    
    # Clean column names (remove whitespace and empty columns)
    df.columns = [c.strip() for c in df.columns]
    df = df.dropna(axis=1, how='all') # Drop empty columns from markdown formatting
    df = df.loc[:, ~df.columns.str.contains('^Unnamed: 0')] # Drop index-like column if exists
    
    # The first row in the data contains dates, which we don't need. 
    # The 'Compound' column has 'nan' in that row.
    df['Compound'] = pd.to_numeric(df['Compound'], errors='coerce')
    df = df.dropna(subset=['Compound'])
    
    # Helper to get data for a group
    def get_group_stats(df, start_col_idx, end_col_idx, name):
        # Select columns by index (inclusive of start, exclusive of end)
        # Note: df.iloc[:, 0] is Compound.
        subset = df.iloc[:, start_col_idx:end_col_idx]
        
        # Convert to numeric, forcing errors to NaN
        subset = subset.apply(pd.to_numeric, errors='coerce')
        
        # Calculate Mean and SEM row-wise
        means = subset.mean(axis=1)
        sems = subset.sem(axis=1)
        
        # Collect raw values
        raw_values = subset.values.tolist()
        
        result = pd.DataFrame({
            'Compound': df['Compound'],
            'Mean': means,
            'SEM': sems,
            'Group': name,
            'Raw': raw_values
        })
        # Drop rows where Mean is NaN (e.g. if that group wasn't measured for that concentration)
        return result.dropna(subset=['Mean'])

    # Indices based on the provided table structure (Compound is index 0)
    # Vehicle: 1 to 10 (9 cols)
    # Vehicle + NT: 10 to 19 (9 cols)
    # SBI: 19 to 28 (9 cols)
    # SR14: 28 to 37 (9 cols)
    
    vehicle = get_group_stats(df, 1, 10, 'Vehicle')
    vehicle_nt = get_group_stats(df, 10, 19, 'Vehicle + 100 nM NT')
    sbi = get_group_stats(df, 19, 28, 'SBI-553 + 100 nM NT')
    sr14 = get_group_stats(df, 28, 37, 'SR142948A + 100 nM NT')
    
    return [vehicle, vehicle_nt, sbi, sr14]

def main():
    # Load and parse data
    data_str = get_data()
    results = parse_data(data_str)
    
    scr_data = []
    der_data = []
    
    for df_res in results:
        if df_res.empty:
            continue
            
        label = df_res['Group'].iloc[0]
        
        # Derived Data
        # We include LogConc for convenience as x_log, similar to previous tasks
        compounds = df_res['Compound'].tolist()
        x_log = np.log10(compounds).tolist()
        
        der_data.append({
            "label": label,
            "x": compounds,
            "x_log": x_log,
            "y": df_res['Mean'].tolist(),
            "yerr": df_res['SEM'].tolist()
        })
        
        # Source Data
        group_raw = []
        raw_vals = df_res['Raw'].tolist()
        for i, conc in enumerate(compounds):
            group_raw.append({
                "concentration": conc,
                "x_log": x_log[i],
                "replicates": raw_vals[i]
            })
        
        scr_data.append({
            "label": label,
            "data": group_raw
        })
        
    data = {"scr_data": scr_data, "der_data": der_data}

    output_path = "bench/ground_truth_code/nature_1_output/70.json"
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    main()
