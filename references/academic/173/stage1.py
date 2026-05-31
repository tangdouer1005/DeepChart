import sys
import io
import pandas as pd
import json

def compile_data(output_filename):
    # 1. Source Data
    csv_data = """Stage|value
primary school|0.766
primary school|0.635
primary school|0.62
primary school|0.5928
primary school|0.559
primary school|0.55
preschool|0.534
primary school|0.53
preschool|0.501
secondary school|0.5
primary school|0.4846
primary school|0.4816
primary school|0.47
primary school|0.47
primary school|0.462
university|0.4517
university|0.4517
primary school|0.446
preschool|0.446
primary school|0.441429
primary school|0.4376
primary school|0.4365
preschool|0.4365
preschool|0.435
secondary school|0.4346
secondary school|0.433
preschool|0.43
primary school|0.423333
preschool|0.418
secondary school|0.41
primary school|0.403667
primary school|0.398
university|0.3961
university|0.3961
primary school|0.386
primary school|0.383333
primary school|0.382
preschool|0.382
primary school|0.368
preschool|0.3668
university|0.3647
university|0.3647
secondary school|0.364
primary school|0.3602
primary school|0.36
preschool|0.357
university|0.3538
primary school|0.3495
preschool|0.3495
primary school|0.349
primary school|0.348167
preschool|0.348167
secondary school|0.34
primary school|0.34
preschool|0.34
primary school|0.328
primary school|0.319
primary school|0.318
secondary school|0.3138
primary school|0.3015
primary school|0.3
university|0.2986
university|0.2971
preschool|0.2968
primary school|0.293333
preschool|0.293333
primary school|0.291
primary school|0.29
preschool|0.29
preschool|0.29
preschool|0.2876
preschool|0.2874
primary school|0.286
university|0.28
primary school|0.28
primary school|0.28
primary school|0.28
preschool|0.28
secondary school|0.2766
secondary school|0.2763
secondary school|0.272143
secondary school|0.27
preschool|0.27
primary school|0.2675
secondary school|0.265842
secondary school|0.261667
secondary school|0.261
university|0.258
secondary school|0.257
primary school|0.252
primary school|0.246084
preschool|0.2448
preschool|0.2442
primary school|0.243
preschool|0.240919
secondary school|0.2349
preschool|0.233
secondary school|0.2328
secondary school|0.2328
preschool|0.23
secondary school|0.2288
university|0.2284
secondary school|0.221667
primary school|0.22
preschool|0.22
preschool|0.213
university|0.2128
secondary school|0.21015
primary school|0.21015
primary school|0.209
university|0.207
secondary school|0.206
primary school|0.205
secondary school|0.198429
preschool|0.1954
university|0.187
university|0.1847
primary school|0.182
preschool|0.1814
secondary school|0.18
secondary school|0.18
primary school|0.175583
secondary school|0.173438
secondary school|0.173438
primary school|0.173438
university|0.1734
preschool|0.172
preschool|0.1715
university|0.169096
university|0.169
university|0.169
preschool|0.1657
university|0.1653
secondary school|0.164
preschool|0.164
university|0.158
university|0.157997
university|0.1561
university|0.1509
university|0.149712
university|0.148515
university|0.1468
university|0.1465
university|0.145
preschool|0.142
university|0.1413
university|0.1325
university|0.13
preschool|0.13
primary school|0.129771
university|0.1286
university|0.12001
primary school|0.12
university|0.118479
university|0.118
primary school|0.114
university|0.1123
university|0.1123
university|0.111871
university|0.1101
university|0.107
university|0.107
university|0.107
university|0.107
university|0.107
secondary school|0.107
secondary school|0.107
primary school|0.107
primary school|0.106
primary school|0.103
university|0.1025
university|0.1015
secondary school|0.1
secondary school|0.1
secondary school|0.099
secondary school|0.099
primary school|0.099
secondary school|0.095
secondary school|0.095
primary school|0.095
university|0.0912545
university|0.087
university|0.0868
secondary school|0.086
secondary school|0.086
primary school|0.086
university|0.0845
primary school|0.079
university|0.0776
primary school|0.0759
preschool|0.0759
university|0.0708
primary school|0.07
university|0.0642
primary school|0.0618762
primary school|0.06
primary school|0.0562852
secondary school|0.054
university|0.0472
primary school|0.045
primary school|0.0423892
primary school|0.0373832
primary school|0.0183028
secondary school|0.017
primary school|0.0145396
primary school|0.0139616
primary school|0.0132548
primary school|0.0121581
primary school|0.0104167
primary school|0.00917431
primary school|0.00813008
primary school|0.002849
primary school|0.00167504
primary school|0.00146843
primary school|0.00142653"""

    df = pd.read_csv(io.StringIO(csv_data), sep="|")
    
    # 2. Data Preprocessing
    # Convert values to percentages (0-1 range to 0-100 range)
    df['value'] = df['value'] * 100
    
    # Normalize stage names (capitalize first letter)
    df['Stage'] = df['Stage'].str.capitalize()
    
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
    output_file = "bench/ground_truth_code/nature_2_output/173.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compile_data(output_file)
