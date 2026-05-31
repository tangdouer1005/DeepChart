import sys
import io
import pandas as pd
import json

def compile_data(output_filename):
    # 1. Source Data
    csv_data = """
| Country      | Stage   |      value |
|:-------------|:--------|-----------:|
| Portugal     | HIC     | 0.766      |
| Portugal     | HIC     | 0.635      |
| USA          | HIC     | 0.62       |
| USA          | HIC     | 0.5928     |
| USA          | HIC     | 0.559      |
| USA          | HIC     | 0.55       |
| USA          | HIC     | 0.534      |
| USA          | HIC     | 0.53       |
| USA          | HIC     | 0.501      |
| USA          | HIC     | 0.5        |
| USA          | HIC     | 0.4846     |
| USA          | HIC     | 0.4816     |
| Italy        | HIC     | 0.47       |
| USA          | HIC     | 0.47       |
| Portugal     | HIC     | 0.462      |
| South Africa | UMIC    | 0.4517     |
| South Africa | UMIC    | 0.4517     |
| USA          | HIC     | 0.446      |
| USA          | HIC     | 0.446      |
| USA          | HIC     | 0.441429   |
| Spain        | HIC     | 0.4376     |
| USA          | HIC     | 0.4365     |
| USA          | HIC     | 0.4365     |
| USA          | HIC     | 0.435      |
| Latvia       | HIC     | 0.4346     |
| USA          | HIC     | 0.433      |
| USA          | HIC     | 0.43       |
| China        | UMIC    | 0.423333   |
| USA          | HIC     | 0.418      |
| Italy        | HIC     | 0.41       |
| USA          | HIC     | 0.403667   |
| Portugal     | HIC     | 0.398      |
| South Africa | UMIC    | 0.3961     |
| South Africa | UMIC    | 0.3961     |
| Portugal     | HIC     | 0.386      |
| USA          | HIC     | 0.383333   |
| USA          | HIC     | 0.382      |
| USA          | HIC     | 0.382      |
| Portugal     | HIC     | 0.368      |
| Brazil       | UMIC    | 0.3668     |
| South Africa | UMIC    | 0.3647     |
| South Africa | UMIC    | 0.3647     |
| USA          | HIC     | 0.364      |
| Latvia       | HIC     | 0.3602     |
| USA          | HIC     | 0.36       |
| USA          | HIC     | 0.357      |
| UK           | HIC     | 0.3538     |
| USA          | HIC     | 0.3495     |
| USA          | HIC     | 0.3495     |
| USA          | HIC     | 0.349      |
| USA          | HIC     | 0.348167   |
| USA          | HIC     | 0.348167   |
| USA          | HIC     | 0.34       |
| Spain        | HIC     | 0.34       |
| Brazil       | UMIC    | 0.34       |
| USA          | HIC     | 0.328      |
| France       | HIC     | 0.319      |
| USA          | HIC     | 0.318      |
| Latvia       | HIC     | 0.3138     |
| USA          | HIC     | 0.3015     |
| USA          | HIC     | 0.3        |
| UK           | HIC     | 0.2986     |
| UK           | HIC     | 0.2971     |
| Brazil       | UMIC    | 0.2968     |
| USA          | HIC     | 0.293333   |
| USA          | HIC     | 0.293333   |
| USA          | HIC     | 0.291      |
| Denmark      | HIC     | 0.29       |
| USA          | HIC     | 0.29       |
| Thailand     | UMIC    | 0.29       |
| Brazil       | UMIC    | 0.2876     |
| Brazil       | UMIC    | 0.2874     |
| Italy        | HIC     | 0.286      |
| USA          | HIC     | 0.28       |
| Spain        | HIC     | 0.28       |
| Italy        | HIC     | 0.28       |
| Italy        | HIC     | 0.28       |
| Canada       | HIC     | 0.28       |
| Latvia       | HIC     | 0.2766     |
| Latvia       | HIC     | 0.2763     |
| USA          | HIC     | 0.272143   |
| USA          | HIC     | 0.27       |
| USA          | HIC     | 0.27       |
| Portugal     | HIC     | 0.2675     |
| Hungary      | HIC     | 0.265842   |
| China        | UMIC    | 0.261667   |
| USA          | HIC     | 0.261      |
| Portugal     | HIC     | 0.258      |
| USA          | HIC     | 0.257      |
| USA          | HIC     | 0.252      |
| Portugal     | HIC     | 0.246084   |
| Brazil       | UMIC    | 0.2448     |
| Brazil       | UMIC    | 0.2442     |
| USA          | HIC     | 0.243      |
| USA          | HIC     | 0.240919   |
| Latvia       | HIC     | 0.2349     |
| Spain        | HIC     | 0.233      |
| Latvia       | HIC     | 0.2328     |
| Latvia       | HIC     | 0.2328     |
| USA          | HIC     | 0.23       |
| Latvia       | HIC     | 0.2288     |
| UK           | HIC     | 0.2284     |
| China        | UMIC    | 0.221667   |
| Spain        | HIC     | 0.22       |
| USA          | HIC     | 0.22       |
| Brazil       | UMIC    | 0.213      |
| Portugal     | HIC     | 0.2128     |
| USA          | HIC     | 0.21015    |
| USA          | HIC     | 0.21015    |
| USA          | HIC     | 0.209      |
| USA          | HIC     | 0.207      |
| USA          | HIC     | 0.206      |
| Japan        | HIC     | 0.205      |
| USA          | HIC     | 0.198429   |
| Brazil       | UMIC    | 0.1954     |
| Iran         | LMIC    | 0.187      |
| UK           | HIC     | 0.1847     |
| USA          | HIC     | 0.182      |
| Brazil       | UMIC    | 0.1814     |
| China        | UMIC    | 0.18       |
| China        | UMIC    | 0.18       |
| Croatia      | UMIC    | 0.175583   |
| UK           | HIC     | 0.173438   |
| UK           | HIC     | 0.173438   |
| UK           | HIC     | 0.173438   |
| Iran         | LMIC    | 0.1734     |
| Thailand     | UMIC    | 0.172      |
| Brazil       | UMIC    | 0.1715     |
| Finland      | HIC     | 0.169096   |
| South Africa | UMIC    | 0.169      |
| South Africa | UMIC    | 0.169      |
| Brazil       | UMIC    | 0.1657     |
| USA          | HIC     | 0.1653     |
| USA          | HIC     | 0.164      |
| Brazil       | UMIC    | 0.164      |
| USA          | HIC     | 0.158      |
| USA          | HIC     | 0.157997   |
| Iran         | LMIC    | 0.1561     |
| Iran         | LMIC    | 0.1509     |
| USA          | HIC     | 0.149712   |
| USA          | HIC     | 0.148515   |
| Iran         | LMIC    | 0.1468     |
| Iran         | LMIC    | 0.1465     |
| Germany      | HIC     | 0.145      |
| Brazil       | UMIC    | 0.142      |
| Iran         | LMIC    | 0.1413     |
| China        | UMIC    | 0.1325     |
| Italy        | HIC     | 0.13       |
| Jordan       | UMIC    | 0.13       |
| Japan        | HIC     | 0.129771   |
| Portugal     | HIC     | 0.1286     |
| Portugal     | HIC     | 0.12001    |
| USA          | HIC     | 0.12       |
| USA          | HIC     | 0.118479   |
| Portugal     | HIC     | 0.118      |
| Japan        | HIC     | 0.114      |
| China        | UMIC    | 0.1123     |
| China        | UMIC    | 0.1123     |
| USA          | HIC     | 0.111871   |
| Portugal     | HIC     | 0.1101     |
| Portugal     | HIC     | 0.107      |
| Sweden       | HIC     | 0.107      |
| Sweden       | HIC     | 0.107      |
| Sweden       | HIC     | 0.107      |
| USA          | HIC     | 0.107      |
| Turkey       | UMIC    | 0.107      |
| Turkey       | UMIC    | 0.107      |
| Turkey       | UMIC    | 0.107      |
| Japan        | HIC     | 0.106      |
| Thailand     | UMIC    | 0.103      |
| Portugal     | HIC     | 0.1025     |
| China        | UMIC    | 0.1015     |
| China        | UMIC    | 0.1        |
| China        | UMIC    | 0.1        |
| Sweden       | HIC     | 0.099      |
| Sweden       | HIC     | 0.099      |
| Sweden       | HIC     | 0.099      |
| Sweden       | HIC     | 0.095      |
| Sweden       | HIC     | 0.095      |
| Sweden       | HIC     | 0.095      |
| Portugal     | HIC     | 0.0912545  |
| Ethiopia     | LIC     | 0.087      |
| Brazil       | UMIC    | 0.0868     |
| Sweden       | HIC     | 0.086      |
| Sweden       | HIC     | 0.086      |
| Sweden       | HIC     | 0.086      |
| Portugal     | HIC     | 0.0845     |
| Thailand     | UMIC    | 0.079      |
| Portugal     | HIC     | 0.0776     |
| Sweden       | HIC     | 0.0759     |
| Sweden       | HIC     | 0.0759     |
| Portugal     | HIC     | 0.0708     |
| Japan        | HIC     | 0.07       |
| Portugal     | HIC     | 0.0642     |
| Japan        | HIC     | 0.0618762  |
| Japan        | HIC     | 0.06       |
| Japan        | HIC     | 0.0562852  |
| Philippines  | LMIC    | 0.054      |
| Portugal     | HIC     | 0.0472     |
| Japan        | HIC     | 0.045      |
| Japan        | HIC     | 0.0423892  |
| Japan        | HIC     | 0.0373832  |
| Japan        | HIC     | 0.0183028  |
| Philippines  | LMIC    | 0.017      |
| Japan        | HIC     | 0.0145396  |
| Japan        | HIC     | 0.0139616  |
| Japan        | HIC     | 0.0132548  |
| Japan        | HIC     | 0.0121581  |
| Japan        | HIC     | 0.0104167  |
| Japan        | HIC     | 0.00917431 |
| Japan        | HIC     | 0.00813008 |
| Japan        | HIC     | 0.002849   |
| Japan        | HIC     | 0.00167504 |
| Japan        | HIC     | 0.00146843 |
| Japan        | HIC     | 0.00142653 |
    """

    # 2. Data Processing
    # Read the markdown table format
    # Filter out the separator line (lines containing '---')
    filtered_data = "\n".join([line for line in csv_data.split('\n') if '---' not in line])
    
    df = pd.read_csv(io.StringIO(filtered_data), sep="|", skipinitialspace=True)
    
    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Drop empty columns resulting from leading/trailing pipes
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Clean data values
    df['Stage'] = df['Stage'].str.strip()
    df['Country'] = df['Country'].str.strip()
    df['value'] = pd.to_numeric(df['value'], errors='coerce')
    
    # Convert value to percentage (0.766 -> 76.6) to match the chart's Y-axis
    df['value'] = df['value'] * 100

    # Save to JSON
    data = df.to_dict(orient='records')
    output_data = {
        "scr_data": data,
        "der_data": []
    }
    with open(output_filename, 'w') as f:
        json.dump(output_data, f, indent=4)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_2_output/171.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compile_data(output_file)
