import sys
import io
import pandas as pd
import json

def get_source_data():
    """
    Returns the raw data provided in the prompt as a pandas DataFrame.
    """
    csv_data = """million$|Unnamed: 1|central estimate of SAF cost|low SAF cost|high SAF cost
central estimate of CORSIA offset cost|2027|343|-516.9|2100.1
nan|2028|121.4|-626.3|2003.8
nan|2029|-64.6|-746.6|1948.6
nan|2030|-214.9|-877.8|1934.7
nan|2031|-341.8|-1020.1|1953
nan|2032|-448.9|-1173.7|1953.6
nan|2033|-481.7|-1307.5|1945
nan|2034|-514.5|-1478|1978.7
nan|2035|-547.2|-1659.6|2025.4
nan|nan|nan|nan|nan
low estimate of CORSIA offset cost|2027|819.6|-40.4|2576.7
nan|2028|704.6|-43.1|2587
nan|2029|636|-45.9|2649.3
nan|2030|614.3|-48.6|2763.9
nan|2031|626.9|-51.4|2921.8
nan|2032|670.6|-54.2|3073.1
nan|2033|768.8|-56.9|3195.5
nan|2034|903.8|-59.7|3397
nan|2035|1049.9|-62.5|3622.5
nan|nan|nan|nan|nan
high estimate of CORSIA offset cost|2027|-200.7|-1060.7|1556.3
nan|2028|-545.5|-1293.2|1337
nan|2029|-867.3|-1549.2|1146
nan|2030|-1166.1|-1829|983.5
nan|2031|-1454.4|-2132.7|840.4
nan|2032|-1736|-2460.7|666.6
nan|2033|-1920.6|-2746.4|506.1
nan|2034|-2147.6|-3111.1|345.6
nan|2035|-2387.5|-3499.9|185.1"""

    # Read the pipe-separated data
    df = pd.read_csv(io.StringIO(csv_data), sep='|')
    
    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # The first column acts as a group header. We need to forward fill it.
    groups = []
    current_group = None
    
    # Iterate to fill the grouping column manually to be safe
    clean_rows = []
    
    for index, row in df.iterrows():
        # Check if the first column has a value (start of a new group)
        val = row['million$']
        if pd.notna(val) and str(val).strip() != 'nan':
            current_group = str(val).strip()
        
        # Check if the Year column is valid (contains data)
        year_val = row['Unnamed: 1']
        if pd.notna(year_val) and str(year_val).strip() != 'nan':
            # Create a clean row dictionary
            clean_rows.append({
                'Group': current_group,
                'Year': int(float(year_val)),
                'Central': float(row['central estimate of SAF cost']),
                'Low': float(row['low SAF cost']),
                'High': float(row['high SAF cost'])
            })
            
    return pd.DataFrame(clean_rows)

def save_data(output_filename):
    df = get_source_data()
    data_list = df.to_dict(orient='records')
    output_data = {
        "scr_data": data_list,
        "der_data": []
    }
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/162.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    save_data(output_file)
