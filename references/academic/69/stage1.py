import sys
import io
import pandas as pd
import numpy as np
import json
import warnings

# Suppress warnings from curve_fit optimization
warnings.filterwarnings("ignore")

def get_source_data():
    """
    Returns the raw markdown data for Figure 3A Gs as a string.
    """
    return """
|   Compound | Vehicle          | Unnamed: 2      | Unnamed: 3     | Unnamed: 4      | Unnamed: 5     | Unnamed: 6     | Unnamed: 7      | Unnamed: 8     | Unnamed: 9     | Vehicle + 100 nM NT   | Unnamed: 11   | Unnamed: 12   | Unnamed: 13   | Unnamed: 14   | Unnamed: 15    | Unnamed: 16   | Unnamed: 17   | Unnamed: 18   | SBI-553 + 100 nM NT   | Unnamed: 20    | Unnamed: 21    | Unnamed: 22    | Unnamed: 23    | Unnamed: 24    | Unnamed: 25   | Unnamed: 26    | Unnamed: 27   | SR142948A + 100 nM NT   | Unnamed: 29      | Unnamed: 30    | Unnamed: 31    | Unnamed: 32    | Unnamed: 33     | Unnamed: 34    | Unnamed: 35    |
|-----------:|:-----------------|:----------------|:---------------|:----------------|:---------------|:---------------|:----------------|:---------------|:---------------|:----------------------|:--------------|:--------------|:--------------|:--------------|:---------------|:--------------|:--------------|:--------------|:----------------------|:---------------|:---------------|:---------------|:---------------|:---------------|:--------------|:---------------|:--------------|:------------------------|:-----------------|:---------------|:---------------|:---------------|:----------------|:---------------|:---------------|
|   nan      | 3/29/24          | 3/29/24         | 3/29/24        | 3/29/24 #2      | 3/29/24 #2     | 3/29/24 #2     | 3/15/24         | 3/15/24        | 3/15/24        | 3/29/24               | 3/29/24       | 3/29/24       | 3/29/24 #2    | 3/29/24 #2    | 3/29/24 #2     | 3/15/24       | 3/15/24       | 3/15/24       | 3/29/24               | 3/29/24        | 3/29/24        | 3/29/24 #2     | 3/29/24 #2     | 3/29/24 #2     | 3/15/24       | 3/15/24        | 3/15/24       | 3/29/24                 | 3/29/24          | 3/29/24        | 3/29/24 #2     | 3/29/24 #2     | 3/15/24         | 3/15/24        | 3/15/24        |
|     3e-06  | nan              | nan             | nan            | nan             | nan            | nan            | nan             | nan            | nan            | nan                   | nan           | nan           | nan           | nan           | nan            | nan           | nan           | nan           | 0.01782305729         | 0.01012637017  | 0.00713712928  | 0.01267898797  | 0.01216961215  | 0.01002840902  | 0.01413785703 | 0.01371052126  | 0.0105890128  | nan                     | nan              | nan            | nan            | nan            | nan             | nan            | nan            |
|     1e-06  | nan              | nan             | nan            | nan             | nan            | nan            | nan             | nan            | nan            | nan                   | nan           | nan           | nan           | nan           | nan            | nan           | nan           | nan           | 0.005978941557        | 0.003143604625 | 0.0106230526   | 0.009009466772 | 0.009945001887 | 0.01013454521  | 0.01632972938 | 0.01087384465  | 0.01619402804 | nan                     | nan              | nan            | nan            | nan            | nan             | nan            | nan            |
|     3e-07  | nan              | nan             | nan            | nan             | nan            | nan            | nan             | nan            | nan            | nan                   | nan           | nan           | nan           | nan           | nan            | nan           | nan           | nan           | 0.01081564042         | 0.008031513627 | 0.006731253879 | 0.01246403009  | 0.01085976001  | 0.007274472066 | 0.01844119731 | 0.01180679024  | 0.01234404025 | nan                     | nan              | nan            | nan            | nan            | nan             | nan            | nan            |
|     1e-07  | nan              | nan             | nan            | nan             | nan            | nan            | nan             | nan            | nan            | nan                   | nan           | nan           | nan           | nan           | nan            | nan           | nan           | nan           | 0.01291745386         | 0.006098165591 | 0.008708074186 | 0.005175648717 | 0.008984921526 | 0.01066476518  | 0.01220519074 | 0.01770826225  | 0.02099027125 | nan                     | nan              | nan            | nan            | nan            | nan             | nan            | nan            |
|     3e-08  | nan              | nan             | nan            | nan             | nan            | nan            | nan             | nan            | nan            | nan                   | nan           | nan           | nan           | nan           | nan            | nan           | nan           | nan           | 0.01782029884         | 0.0140151026   | 0.01375752408  | 0.01075616226  | 0.01301619622  | 0.0118279268   | 0.01917870351 | 0.01346276944  | 0.01332093541 | nan                     | nan              | nan            | nan            | nan            | nan             | nan            | nan            |
|     1e-08  | nan              | nan             | nan            | nan             | nan            | nan            | nan             | nan            | nan            | nan                   | nan           | nan           | nan           | nan           | nan            | nan           | nan           | nan           | 0.01722823324         | 0.0174147945   | 0.01131659648  | 0.01592035402  | 0.01860893942  | 0.02395376559  | 0.02058300747 | 0.01708625779  | 0.018618401   | nan                     | nan              | nan            | nan            | nan            | nan             | nan            | nan            |
|     3e-09  | nan              | nan             | nan            | nan             | nan            | nan            | nan             | nan            | nan            | nan                   | nan           | nan           | nan           | nan           | nan            | nan           | nan           | nan           | 0.01512356112         | 0.01826747932  | 0.01074827068  | 0.01622024569  | 0.01699309009  | 0.02182988338  | 0.02211863537 | 0.02465403395  | 0.02098953185 | nan                     | nan              | nan            | nan            | nan            | nan             | nan            | nan            |
|     1e-11  | nan              | nan             | nan            | nan             | nan            | nan            | nan             | nan            | nan            | nan                   | nan           | nan           | nan           | nan           | nan            | nan           | nan           | nan           | 0.0274269719          | 0.02240258022  | 0.02378129644  | 0.02790036312  | 0.02721289703  | 0.02885084134  | 0.02597844086 | 0.03318424486* | 0.0441027467* | nan                     | nan              | nan            | nan            | nan            | nan             | nan            | nan            |
|   nan      | nan              | nan             | nan            | nan             | nan            | nan            | nan             | nan            | nan            | nan                   | nan           | nan           | nan           | nan           | nan            | nan           | nan           | nan           | nan                   | nan            | nan            | nan            | nan            | nan            | nan           | nan            | nan           | nan                     | nan              | nan            | nan            | nan            | nan             | nan            | nan            |
|     0.0001 | -0.0004493137373 | 0.004511141087  | 0.003651527551 | 0.003090359289  | 0.009575045332 | 0.0123010559   | 0.003104587415  | 0.001586832647 | 0.007066910093 | 0.02676401902         | 0.02289305713 | 0.02627315553 | 0.03485382208 | 0.02257479772 | 0.01896705463  | 0.02120034573 | 0.02641059429 | 0.02070234279 | nan                   | nan            | nan            | nan            | nan            | nan            | nan           | nan            | nan           | 0.003448271116*         | 0.003665390982*  | -0.01911132103 | 0.004996006685 | 0.009817394134 | 0.007885845515  | 0.008911033292 | 0.004937921396 |
|     1e-05  | 0.004862973825   | 0.00240952901   | 0.003374556727 | 0.0002168443389 | 0.005288879499 | 0.009576309646 | -0.004470779314 | 0.002309825314 | 0.01392577602  | 0.02044883025         | 0.01604755612 | 0.01924543013 | 0.0278113061  | 0.02097050535 | 0.02113879241  | 0.0258153718  | 0.02961017377 | 0.02327729044 | nan                   | nan            | nan            | nan            | nan            | nan            | nan           | nan            | nan           | 0.003218097649*         | 0.0003066738639* | 0.00633507559  | 0.00535857501  | 0.003962762753 | 0.0008120535807 | 0.0044700819   | 0.005014008111 |
|     1e-06  | 0.002202279554   | -0.002818977152 | 0.002061010671 | 0.003096758514  | 0.002401635228 | 0.007597679736 | -0.004233618723 | 0.001919121262 | 0.001383206147 | 0.01818700751         | 0.02164242645 | 0.01914194822 | 0.02531468706 | 0.02405812217 | 0.02842259678  | 0.02452628227 | 0.02801969414 | 0.02503237023 | nan                   | nan            | nan            | nan            | nan            | nan            | nan           | nan            | nan           | -0.002420973232*        | -0.001379107869* | 0.001203608885 | 0.005544150247 | 0.005492513935 | 0.01136699095   | 0.00157098811  | 0.009024177592 |
|     1e-07  | 0.006599065763   | 0.008974962353  | 0.01112363925  | 0.006205329034  | 0.003679758112 | 0.004736789831 | 0.002315787925  | 0.007898909428 | 0.006386027288 | 0.02359088193         | 0.02174559209 | 0.01783310179 | 0.0202516924  | 0.02121109997 | 0.006232988403 | 0.02749616232 | 0.0259221161  | 0.02446413997 | nan                   | nan            | nan            | nan            | nan            | nan            | nan           | nan            | nan           | -0.001008772082*        | 0.002824345343*  | 0.002152121296 | 0.002107146277 | 0.006628341059 | 0.01084774235   | 0.008886777421 | 0.01114456795  |
|     1e-08  | 0.007376027833   | 0.005687289427  | 0.005391714591 | 0.004576224725  | 0.007996696908 | 0.007354574723 | 0.01173255296   | 0.001826328797 | 0.007120528203 | 0.02296431061         | 0.02085376973 | 0.01768353396 | 0.02460923839 | 0.02245760313 | 0.02332789823  | 0.0259120829  | 0.02089739707 | 0.0267384141  | nan                   | nan            | nan            | nan            | nan            | nan            | nan           | nan            | nan           | 0.008208507015*         | 0.008363154996*  | 0.002433485318 | 0.01970282519  | 0.01076531296  | 0.01496123424   | 0.01571676495  | 0.0226764638   |
|     1e-09  | 0.004915649534   | 0.003575398654  | 0.006134588343 | 0.007901301217  | 0.005143301734 | 0.002239363537 | 0.004935095151  | 0.006639409032 | 0.005738587377 | 0.02247336408         | 0.02553309492 | 0.02169798104 | 0.02230576623 | 0.02278506201 | 0.02089492611  | 0.02758134746 | 0.02271180397 | 0.0265249706  | nan                   | nan            | nan            | nan            | nan            | nan            | nan           | nan            | nan           | 0.01292399867*          | 0.01427069946*   | 0.01385545398  | 0.02515460344  | 0.01868298974  | 0.02576593374   | 0.02217217592  | 0.02676476053  |
|     1e-10  | 0.00599007524    | 0.003553640288  | 0.007886920783 | 0.003210648152  | 0.005730244506 | 0.002392450072 | 0.01047691574   | 0.003741760688 | 0.01118258988  | 0.03302162923         | 0.0274307433  | 0.02431183287 | 0.02417399922 | 0.02176581051 | 0.02089381733  | 0.03361145305 | 0.02635586782 | 0.01950924412 | nan                   | nan            | nan            | nan            | nan            | nan            | nan           | nan            | nan           | 0.01407423253*          | 0.01561449875*   | 0.02213542717  | 0.02580911677  | 0.01950692315  | 0.02802620223   | 0.02607141339  | 0.02423629486  |
|     1e-11  | 0.005105385096   | 0.00424522145   | 0.003978316064 | -0.001412032798 | 0.005324382595 | 0.005128141125 | 0.002862130073  | 0.003428229641 | 0.005579745162 | 0.02887453346         | 0.02571036478 | 0.02743225965 | 0.02322647055 | 0.0247114419  | 0.02143332573  | 0.0182717672  | 0.02908981634 | 0.02986021735 | nan                   | nan            | nan            | nan            | nan            | nan            | nan           | nan            | nan           | 0.01548569835*          | 0.01721837421*   | 0.01999774008  | 0.02019256046  | 0.02263137777  | 0.02330966278   | 0.03044419689  | 0.02852578425  |
"""

def clean_value(val):
    """Cleans string values by removing asterisks and converting to float."""
    if pd.isna(val):
        return np.nan
    if isinstance(val, str):
        val = val.replace('*', '').strip()
        if val == 'nan' or val == '':
            return np.nan
    try:
        return float(val)
    except ValueError:
        return np.nan

def process_data():
    # Read the markdown table
    csv_data = get_source_data()
    df = pd.read_csv(io.StringIO(csv_data), sep='|', skipinitialspace=True)
    
    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Drop the first and last columns if they are empty (common in markdown tables)
    if df.columns[0] == '' or df.columns[0] == 'Unnamed: 0':
        df = df.iloc[:, 1:]
    if df.columns[-1] == '' or (str(df.columns[-1]).startswith('Unnamed:') and df.iloc[:, -1].isna().all()):
        df = df.iloc[:, :-1]
        
    # Drop the first row (dates)
    df = df.iloc[1:].reset_index(drop=True)
    
    # Clean the 'Compound' column (Concentration)
    df['Compound'] = df['Compound'].apply(clean_value)
    
    # Drop rows where Compound is NaN
    df = df.dropna(subset=['Compound'])
    
    # Calculate Log Concentration
    # Note: 0.0001 is 1e-4 -> -4. 1e-11 -> -11.
    df['LogConc'] = np.log10(df['Compound'])
    
    # Define groups based on column headers
    # Vehicle: Columns 1 to 9 (indices 1 to 10 exclusive)
    # Vehicle + NT: Columns 10 to 18 (indices 10 to 19 exclusive)
    # SBI-553: Columns 19 to 27 (indices 19 to 28 exclusive)
    # SR142948A: Columns 28 to 36 (indices 28 to 37 exclusive)
    
    groups = {
        'Vehicle': {
            'cols': list(range(1, 10)),
            'color': '#808080', # Grey
            'label': 'Vehicle'
        },
        'Vehicle + NT': {
            'cols': list(range(10, 19)),
            'color': '#00008B', # Dark Blue
            'label': 'Vehicle + 100 nM NT'
        },
        'SBI-553': {
            'cols': list(range(19, 28)),
            'color': '#B030B0', # Magenta/Purple
            'label': 'SBI-553 + 100 nM NT'
        },
        'SR142948A': {
            'cols': list(range(28, 36)),
            'color': '#F58025', # Orange
            'label': 'SR142948A + 100 nM NT'
        }
    }
    
    scr_data = []
    der_data = []
    
    for name, info in groups.items():
        # Extract columns for this group
        group_df = df.iloc[:, info['cols']].copy()
        
        # Clean values in these columns
        for col in group_df.columns:
            group_df[col] = group_df[col].apply(clean_value)
            
        # Calculate Mean and SEM
        means = group_df.mean(axis=1)
        sems = group_df.sem(axis=1)
        
        # Store data, filtering out NaNs in the y-values
        mask = ~np.isnan(means)
        der_data.append({
            'label': info['label'],
            'color': info['color'],
            'x': df.loc[mask, 'LogConc'].values.tolist(),
            'y': means[mask].values.tolist(),
            'yerr': sems[mask].values.tolist(),
        })
        
        # Source Data
        group_raw = []
        for idx in df.index:
             replicates = group_df.loc[idx].values.tolist()
             # Skip if all are NaN (no data for this concentration)
             if np.isnan(replicates).all():
                 continue
                 
             group_raw.append({
                 "x_log": df.loc[idx, 'LogConc'],
                 "replicates": replicates
             })
             
        scr_data.append({
            "label": info['label'],
            "data": group_raw
        })
        
    return {"scr_data": scr_data, "der_data": der_data}

def main():
    data = process_data()
    output_path = "bench/ground_truth_code/nature_1_output/69.json"
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Data saved to {output_path}")

if __name__ == "__main__":
    main()
