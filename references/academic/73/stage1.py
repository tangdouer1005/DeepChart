import sys
import io
import pandas as pd
import numpy as np
import json

# 1. Source Data (Figure 3B)
# Embedded as a string to ensure the script is self-contained.
csv_data = """
|   Compound | Vehicle - Vehicle (Barr KO)   | Unnamed: 2     | Unnamed: 3     | Unnamed: 4     | Unnamed: 5      | Unnamed: 6     | Vehicle + 100 nM NT (β-arrestin1/2-null)   | Unnamed: 8    | Unnamed: 9    | Unnamed: 10   | Unnamed: 11   | Unnamed: 12   | SBI-553 + 100 nM NT (β-arrestin1/2-null)   | Unnamed: 14     | Unnamed: 15     | Unnamed: 16     | Unnamed: 17     | Unnamed: 18     | Vehicle - Vehicle (Parentals)   | Unnamed: 20    | Unnamed: 21    | Unnamed: 22    | Unnamed: 23    | Unnamed: 24    | Vehicle + 100 nM NT (Parentals)   | Unnamed: 26   | Unnamed: 27   | Unnamed: 28   | Unnamed: 29   | Unnamed: 30   | SBI-553 + 100 nM NT (Parentals)   | Unnamed: 32     | Unnamed: 33     | Unnamed: 34    | Unnamed: 35     | Unnamed: 36     |
|-----------:|:------------------------------|:---------------|:---------------|:---------------|:----------------|:---------------|:-------------------------------------------|:--------------|:--------------|:--------------|:--------------|:--------------|:-------------------------------------------|:----------------|:----------------|:----------------|:----------------|:----------------|:--------------------------------|:---------------|:---------------|:---------------|:---------------|:---------------|:----------------------------------|:--------------|:--------------|:--------------|:--------------|:--------------|:----------------------------------|:----------------|:----------------|:---------------|:----------------|:----------------|
|   nan      | 4/5/24                        | 4/5/24         | 3/21/24        | 3/21/24        | 3/20/24         | 3/20/24        | 4/5/24                                     | 4/5/24        | 3/21/24       | 3/21/24       | 3/20/24       | 3/20/24       | 4/5/24                                     | 4/5/24          | 3/21/24         | 3/21/24         | 3/20/24         | 3/20/24         | 4/5/24                          | 4/5/24         | 3/21/24        | 3/21/24        | 3/20/24        | 3/20/24        | 4/5/24                            | 4/5/24        | 3/21/24       | 3/21/24       | 3/20/24       | 3/20/24       | 4/5/24                            | 4/5/24          | 3/21/24         | 3/21/24        | 3/20/24         | 3/20/24         |
|     3e-06  | nan                           | nan            | nan            | nan            | nan             | nan            | nan                                        | nan           | nan           | nan           | nan           | nan           | -0.02861489896                             | -0.02534887022  | -0.02470798873  | -0.02293069454  | -0.01842958889  | -0.005885784002 | nan                             | nan            | nan            | nan            | nan            | nan            | nan                               | nan           | nan           | nan           | nan           | nan           | -0.02648540792                    | -0.03431096244  | -0.03134469387  | -0.0276378503  | -0.0198520841   | -0.01868319724  |
|     1e-06  | nan                           | nan            | nan            | nan            | nan             | nan            | nan                                        | nan           | nan           | nan           | nan           | nan           | -0.01720810583                             | -0.02277382307  | -0.0224886877   | -0.02130169224  | -0.001877246815 | -0.01686383811  | nan                             | nan            | nan            | nan            | nan            | nan            | nan                               | nan           | nan           | nan           | nan           | nan           | -0.02273463684                    | -0.0305364072   | -0.02746253747  | -0.02827190012 | -0.01939144376  | -0.01906813104  |
|     3e-07  | nan                           | nan            | nan            | nan            | nan             | nan            | nan                                        | nan           | nan           | nan           | nan           | nan           | -0.008754857984                            | -0.01869604892  | -0.02442366417  | -0.01455620321  | -0.02200375729  | -0.01186286174  | nan                             | nan            | nan            | nan            | nan            | nan            | nan                               | nan           | nan           | nan           | nan           | nan           | -0.01631486779                    | -0.02343409472  | -0.02170710833  | -0.02286571592 | -0.01967013291  | -0.01779204555  |
|     1e-07  | nan                           | nan            | nan            | nan            | nan             | nan            | nan                                        | nan           | nan           | nan           | nan           | nan           | -0.002557009086                            | -0.009217734112 | -0.001693144711 | -0.009353540879 | -0.01373197457  | 0.0001741767881 | nan                             | nan            | nan            | nan            | nan            | nan            | nan                               | nan           | nan           | nan           | nan           | nan           | 3.350256129e-05                   | -0.008737920738 | -0.003072724318 | -0.01490436994 | -0.008381411757 | -0.001659829496 |
|     3e-08  | nan                           | nan            | nan            | nan            | nan             | nan            | nan                                        | nan           | nan           | nan           | nan           | nan           | 0.01274290695                              | 0.009948265757  | 0.02143541528   | 0.01877877084   | 0.009836638368  | 0.007992366491  | nan                             | nan            | nan            | nan            | nan            | nan            | nan                               | nan           | nan           | nan           | nan           | nan           | 0.01161403799                     | 0.0132841525    | 0.01718808944   | 0.0199751414   | 0.01233298292   | 0.01171714308   |
|     1e-08  | nan                           | nan            | nan            | nan            | nan             | nan            | nan                                        | nan           | nan           | nan           | nan           | nan           | 0.03509492739                              | 0.05726017259   | 0.04770833857   | 0.04155319399   | 0.02691974711   | 0.01832493684   | nan                             | nan            | nan            | nan            | nan            | nan            | nan                               | nan           | nan           | nan           | nan           | nan           | 0.04403028961                     | 0.03298227147   | 0.03132594171   | 0.03174542459  | 0.02567187847   | 0.03468688622   |
|     3e-09  | nan                           | nan            | nan            | nan            | nan             | nan            | nan                                        | nan           | nan           | nan           | nan           | nan           | 0.06183100993                              | 0.05781920003   | 0.06527415838   | 0.06376379927   | 0.06132385753   | 0.05207189198   | nan                             | nan            | nan            | nan            | nan            | nan            | nan                               | nan           | nan           | nan           | nan           | nan           | 0.05038710885                     | 0.04244685272   | 0.05070531999   | 0.051574858    | 0.04547793995   | 0.05396636209   |
|     1e-11  | nan                           | nan            | nan            | nan            | nan             | nan            | nan                                        | nan           | nan           | nan           | nan           | nan           | 0.09027572259                              | 0.08817040097   | 0.08794183791   | 0.1071636582    | 0.09356712381   | 0.09780909901   | nan                             | nan            | nan            | nan            | nan            | nan            | nan                               | nan           | nan           | nan           | nan           | nan           | 0.06790302682                     | 0.05603475244   | 0.06585767193   | 0.06078379136  | 0.0712802248    | 0.07757727791   |
|   nan      | nan                           | nan            | nan            | nan            | nan             | nan            | nan                                        | nan           | nan           | nan           | nan           | nan           | nan                                        | nan             | nan             | nan             | nan             | nan             | nan                             | nan            | nan            | nan            | nan            | nan            | nan                               | nan           | nan           | nan           | nan           | nan           | nan                               | nan             | nan             | nan            | nan             | nan             |
|     0.0001 | -0.0292683692                 | -0.03240320878 | -0.02995225071 | -0.0307002276  | -0.01963164265  | -0.01605227019 | 0.09655177186                              | 0.08791824426 | 0.07007740211 | 0.08286376189 | 0.1085727747  | 0.07727154568 | nan                                        | nan             | nan             | nan             | nan             | nan             | -0.0351213984                   | -0.03475586978 | -0.03262092714 | -0.03465933828 | -0.02634052048 | -0.02620901985 | 0.07049728027                     | 0.06808558031 | 0.04844928431 | 0.06645440144 | 0.07506574481 | 0.06813289575 | nan                               | nan             | nan             | nan            | nan             | nan             |
|     1e-05  | -0.02925573644                | -0.03369631857 | -0.03870240819 | -0.03137772205 | -0.02921765704  | -0.01808909976 | 0.09948915499                              | 0.08946808055 | 0.06908475884 | 0.09310962907 | 0.08466025123 | 0.06905911923 | nan                                        | nan             | nan             | nan             | nan             | nan             | -0.03329906245                  | -0.03335228603 | -0.03933986393 | -0.02999804905 | -0.0212635972  | -0.02125639223 | 0.06739693708                     | 0.06452817402 | 0.059447888   | 0.06447327486 | 0.06148974018 | 0.0662075036  | nan                               | nan             | nan             | nan            | nan             | nan             |
|     1e-06  | -0.02636610662                | -0.03277680542 | -0.02674453102 | -0.03714323021 | -0.009626431832 | -0.01747546846 | 0.1033700933                               | 0.08738333331 | 0.06546181477 | 0.07470331066 | 0.0681856395  | 0.06998248357 | nan                                        | nan             | nan             | nan             | nan             | nan             | -0.03436850762                  | -0.03146256799 | -0.02739259146 | -0.03231151413 | -0.02733956052 | -0.02308767558 | 0.06221010036                     | 0.06081163623 | 0.05699329464 | 0.06424303233 | 0.0604790871  | 0.05758507954 | nan                               | nan             | nan             | nan            | nan             | nan             |
|     1e-07  | -0.03346920598                | -0.02961102328 | -0.02957906056 | -0.02314549232 | -0.03000217149  | -0.02500019122 | 0.1039269951                               | 0.09708987722 | 0.0689043321  | 0.0906168959  | 0.06591562849 | 0.07654111527 | nan                                        | nan             | nan             | nan             | nan             | nan             | -0.03153206597                  | -0.0331449245  | -0.03408475324 | -0.03263808218 | -0.02086492281 | -0.01810476818 | 0.06467955229                     | 0.06477156934 | 0.0598105424  | 0.07251424096 | 0.06810112223 | 0.06181018095 | nan                               | nan             | nan             | nan            | nan             | nan             |
|     1e-08  | -0.03004810109                | -0.03600095446 | -0.02396217223 | -0.03550574649 | -0.02177447572  | -0.02498297168 | 0.1049999181                               | 0.1014291847  | 0.0791682951  | 0.08227325874 | 0.09757746768 | 0.07890686513 | nan                                        | nan             | nan             | nan             | nan             | nan             | -0.03227721889                  | -0.03025240901 | -0.03159258881 | -0.03401669022 | -0.02113875842 | -0.02389464166 | 0.06624920928                     | 0.06138625023 | 0.06607723502 | 0.06423398517 | 0.06660145312 | 0.06116796897 | nan                               | nan             | nan             | nan            | nan             | nan             |
|     1e-09  | -0.02816762576                | -0.02123827019 | -0.03489026705 | -0.0323382531  | -0.02343084062  | -0.02152033409 | 0.09448202197                              | 0.09430806455 | 0.07963041078 | 0.09436301006 | 0.09129279194 | 0.08267269497 | nan                                        | nan             | nan             | nan             | nan             | nan             | -0.03058005566                  | -0.0322043504  | -0.03255815641 | -0.03358907524 | -0.0269761561  | -0.02696948936 | 0.06250991574                     | 0.06370951397 | 0.06134031518 | 0.06631263273 | 0.06377883585 | 0.0534727909  | nan                               | nan             | nan             | nan            | nan             | nan             |
|     1e-10  | -0.03374712                   | -0.03564675558 | -0.03241768536 | -0.03459523246 | -0.02532582362  | -0.0224316384  | 0.09462105654                              | 0.08885866496 | 0.07788886029 | 0.111140253   | 0.07946677049 | 0.07856413612 | nan                                        | nan             | nan             | nan             | nan             | nan             | -0.03557264006                  | -0.03511497793 | -0.03615156562 | -0.02887642809 | -0.02794511627 | -0.02489293123 | 0.06209511661                     | 0.05956464427 | 0.06288923056 | 0.07318791243 | 0.06912003938 | 0.05824835695 | nan                               | nan             | nan             | nan            | nan             | nan             |
|     1e-11  | -0.0301527272                 | -0.03374560111 | -0.03225891944 | -0.02384022167 | -0.01900973176  | -0.02580818287 | 0.09240278738                              | 0.08259450613 | 0.0884250945  | 0.1029884454  | 0.09041059681 | 0.08936627788 | nan                                        | nan             | nan             | nan             | nan             | nan             | -0.03426036729                  | -0.03364416379 | -0.0325945799  | -0.03226655919 | -0.02903513174 | -0.02730516504 | 0.05784055117                     | 0.06108335539 | 0.06758209641 | 0.07878642173 | 0.07990185908 | 0.07159174348 | nan                               | nan             | nan             | nan            | nan             | nan             |
"""

def process_data(csv_str):
    # Read CSV, handling the pipe separator and whitespace
    df = pd.read_csv(io.StringIO(csv_str), sep="|", header=0, skipinitialspace=True)
    
    # Remove the first row (dates) and any completely empty rows
    df = df.iloc[1:].copy()
    
    # Clean column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Convert Compound to numeric, coerce errors to NaN
    df['Compound'] = pd.to_numeric(df['Compound'], errors='coerce')
    
    # Drop rows where Compound is NaN
    df = df.dropna(subset=['Compound'])
    
    # Calculate log10 of Compound
    df['LogCompound'] = np.log10(df['Compound'])
    
    # Convert all other columns to numeric
    for col in df.columns:
        if col not in ['Compound', 'LogCompound']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    return df

def generate_json_data(df):
    # Colors
    color_veh = '#808080' # Gray
    color_nt_veh = '#00008B' # Dark Blue
    color_nt_sbi = '#BA55D3' # Medium Orchid / Purple
    
    # Groups configuration
    groups_config = [
        # Parentals (+) - Filled Circles, Solid Lines
        {
            'name': 'Vehicle (Parentals)',
            'cols': range(20, 26),
            'color': color_veh,
            'marker': 'o',
            'linestyle': '-',
            'fill': True
        },
        {
            'name': '100 nM NT + vehicle (Parentals)',
            'cols': range(26, 32),
            'color': color_nt_veh,
            'marker': 'o',
            'linestyle': '-',
            'fill': True
        },
        {
            'name': '100 nM NT + SBI-553 (Parentals)',
            'cols': range(32, 38),
            'color': color_nt_sbi,
            'marker': 'o',
            'linestyle': '-',
            'fill': True
        },
        # Null (-) - Open Circles, Dashed Lines
        {
            'name': 'Vehicle (Null)',
            'cols': range(2, 8),
            'color': color_veh,
            'marker': 'o',
            'linestyle': '--',
            'fill': False
        },
        {
            'name': '100 nM NT + vehicle (Null)',
            'cols': range(8, 14),
            'color': color_nt_veh,
            'marker': 'o',
            'linestyle': '--',
            'fill': False
        },
        {
            'name': '100 nM NT + SBI-553 (Null)',
            'cols': range(14, 20),
            'color': color_nt_sbi,
            'marker': 'o',
            'linestyle': '--',
            'fill': False
        }
    ]
    
    output_data = {}
    
    for g in groups_config:
        # Select columns by index
        cols = df.iloc[:, list(g['cols'])]
        
        # Calculate Mean and SEM
        mean = cols.mean(axis=1)
        sem = cols.sem(axis=1)
        x = df['LogCompound']
        
        output_data[g['name']] = {
            'x': x.tolist(),
            'y': mean.tolist(),
            'yerr': sem.tolist(),
            'color': g['color'],
            'marker': g['marker'],
            'linestyle': g['linestyle'],
            'fill': g['fill']
        }
    
    return output_data

if __name__ == "__main__":
    df = process_data(csv_data)
    der_data = generate_json_data(df)
    
    final_output = {
        "scr_data": df.to_dict(orient='records'),
        "der_data": der_data
    }
    
    with open('bench/ground_truth_code/nature_1_output/73.json', 'w') as f:
        json.dump(final_output, f, indent=4)
