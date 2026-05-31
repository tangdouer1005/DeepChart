import sys
import io
import pandas as pd
import json
import numpy as np

def compile_data(output_filename):
    # 1. Load Source Data
    csv_data = """Type|Food waste reduction approaches (operational strategies)|Frequency in literatures|Percentage
Canteen management|Reduce the size of the plate, provide appropriate portion sizes|19|0.141791
nan|Plan and assess menus regularly|13|0.0970149
nan|Improve sensory quality|11|0.0820896
nan|Go trayless|8|0.0597015
nan|Supervise children's meals|6|0.0447761
nan|Extend lunchtime|6|0.0447761
nan|Improve canteen atmosphere|5|0.0373134
nan|Taste test|5|0.0373134
nan|Survey student feedback|4|0.0298507
nan|Monitor food waste|4|0.0298507
nan|Allow sharing and saving of leftovers|3|0.0223881
nan|Optimize food production plan|3|0.0223881
Food education|Comprehensive food education|14|0.104478
nan|Poster information|13|0.0970149
nan|Train canteen staff|10|0.0746269
nan|Course teaching|6|0.0447761
nan|Train teacher|3|0.0223881
nan|Educational text messages|1|0.00746269"""

    df = pd.read_csv(io.StringIO(csv_data), sep='|')

    # 2. Data Preprocessing
    # Fill forward the 'Type' column to handle nan values
    df['Type'] = df['Type'].ffill()
    
    # Create Short Labels map based on the visual chart
    label_map = {
        "Reduce the size of the plate, provide appropriate portion sizes": "Reduce portions",
        "Plan and assess menus regularly": "Assess menu",
        "Improve sensory quality": "Improve\nsensory\nquality",
        "Go trayless": "Trayless",
        "Supervise children's meals": "Supervise\nchildren's\nmeals",
        "Extend lunchtime": "Extend\nlunchtime",
        "Improve canteen atmosphere": "Improve canteen\natmosphere",
        "Taste test": "Taste test",
        "Survey student feedback": "Survey feedback",
        "Monitor food waste": "Monitor food waste",
        "Allow sharing and saving of leftovers": "Share and pack",
        "Optimize food production plan": "Optimize\nproduction plan",
        "Comprehensive food education": "Comprehensive\nfood education",
        "Poster information": "Poster\ninformation",
        "Train canteen staff": "Train canteen staff",
        "Course teaching": "Course teaching",
        "Train teacher": "Train teacher",
        "Educational text messages": "Text messages"
    }
    df['ShortLabel'] = df['Food waste reduction approaches (operational strategies)'].map(label_map)

    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Ensure numeric columns are actually numeric
    df['Frequency in literatures'] = pd.to_numeric(df['Frequency in literatures'], errors='coerce')
    df['Percentage'] = pd.to_numeric(df['Percentage'], errors='coerce')

    # Prepare data for outer ring
    df['pct_display'] = df['Percentage'] * 100
    
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
    output_file = "bench/ground_truth_code/nature_2_output/175.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compile_data(output_file)
