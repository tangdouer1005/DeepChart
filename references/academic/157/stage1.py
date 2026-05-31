import sys
import io
import pandas as pd
import json

def compile_data(output_filename):
    # 1. Source Data Loading
    csv_data = """million$|Unnamed: 1|central estimate of SAF cost|low SAF cost|high SAF cost
central estimate of CORSIA offset cost|2027|641.1|357.2|1947.5
nan|2028|453.3|164.1|1905.5
nan|2029|257.2|-51.4|1859
nan|2030|61.3|-285.3|1815.9
nan|2031|-125.5|-533.5|1784.8
nan|2032|-397.3|-791.8|1677.8
nan|2033|-695.4|-1073.1|1585.9
nan|2034|-1026.5|-1342.4|1433.8
nan|2035|-1398.6|-1607.1|1246.9
nan|nan|nan|nan|nan
low estimate of CORSIA offset cost|2027|1012.4|728.5|2318.8
nan|2028|913.1|623.8|2365.3
nan|2029|816.2|507.7|2418
nan|2030|730.8|384.2|2485.4
nan|2031|666.1|258|2576.4
nan|2032|528.4|133.9|2603.5
nan|2033|395|17.3|2676.3
nan|2034|227.1|-88.8|2687.4
nan|2035|32.2|-176.3|2677.6
nan|nan|nan|nan|nan
high estimate of CORSIA offset cost|2027|217.5|-66.4|1523.9
nan|2028|-72.5|-361.7|1379.8
nan|2029|-383.2|-691.8|1218.6
nan|2030|-706.7|-1053.3|1047.9
nan|2031|-1034.6|-1442.6|875.7
nan|2032|-1461.6|-1856.1|613.5
nan|2033|-1950|-2327.7|331.2
nan|2034|-2470.1|-2786|-9.8
nan|2035|-3047.2|-3255.7|-401.7"""

    # Read data
    df = pd.read_csv(io.StringIO(csv_data), sep="|")
    
    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Forward fill the first column to identify groups
    # We rename 'million$' to 'Group' and 'Unnamed: 1' to 'Year' for clarity
    df = df.rename(columns={'million$': 'Group', 'Unnamed: 1': 'Year'})
    
    df['Group'] = df['Group'].str.strip()
    df['Group'] = df['Group'].ffill()
    
    # Drop rows where Year is NaN (the separator rows)
    df = df.dropna(subset=['Year'])
    
    # Convert numeric columns
    cols_to_numeric = ['Year', 'central estimate of SAF cost', 'low SAF cost', 'high SAF cost']
    for col in cols_to_numeric:
        df[col] = pd.to_numeric(df[col])

    # Save to JSON
    output_data = {
        "scr_data": df.to_dict(orient='records'),
        "der_data": []
    }
    
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/157.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compile_data(output_file)
