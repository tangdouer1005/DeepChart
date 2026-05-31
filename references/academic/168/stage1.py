import sys
import io
import pandas as pd
import json
import numpy as np

def process_data(output_filename):
    # 1. Source Data Loading
    csv_data = """Country|Plate waste amount|sd
Brazil|46.7486|12.487
Canada|nan|nan
China|87.2099|18.7216
Croatia|nan|nan
Denmark|106.572|0
Ethiopia|35.2404|0
Finland|48.337|21.5668
France|72.1517|16.4234
Germany|nan|nan
Hungary|nan|nan
India|43.5447|0
Indonesia|39.8112|9.40734
Iran|nan|nan
Italy|55.445|34.3162
Japan|21.9694|27.4253
Jordan|73.6009|0
Latvia|86.3343|16.0132
Malaysia|8.92205|3.64655
Philippines|17.0031|15.3442
Portugal|84.9073|37.5819
Russia|42.9844|47.3762
South Africa|105.772|26.4915
Spain|75.6494|53.1506
Sweden|32.8335|10.9777
Switzerland|16.0593|6.52803
Thailand|31.2178|26.9765
Turkey|64.4366|21.9458
UK|55.5429|4.695
USA|133.085|80.0026"""

    # Read the data
    df = pd.read_csv(io.StringIO(csv_data), sep='|')

    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]

    # Convert numeric columns to float, coercing errors (like 'nan') to NaN
    df['Plate waste amount'] = pd.to_numeric(df['Plate waste amount'], errors='coerce')
    df['sd'] = pd.to_numeric(df['sd'], errors='coerce')

    # Drop rows with NaN values (as they are not plotted in the reference image)
    df = df.dropna(subset=['Plate waste amount'])

    # Sort by 'Plate waste amount' in descending order
    df = df.sort_values(by='Plate waste amount', ascending=False)

    # Reset index for clean plotting
    df = df.reset_index(drop=True)

    # Save to JSON
    data_list = df.to_dict(orient='records')
    output_data = {
        "scr_data": [],
        "der_data": data_list
    }
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)

if __name__ == "__main__":
    output_file = "168.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    process_data(output_file)
