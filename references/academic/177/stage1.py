import sys
import io
import pandas as pd
import json
import numpy as np

def compile_data(output_filename):
    # 1. Source Data Embedding
    csv_data = """left|right|NSF|NSFC
p_public health|t_machine learning|4|0
p_environmental conditions|t_machine learning|10|0
p_quality of life|t_machine learning|6|0
p_quality of life|t_internet of things|4|0
p_environmental conditions|t_internet of things|20|1
s_social sciences|p_environmental conditions|1|0
s_social sciences|p_equity|2|0
s_social sciences|p_gas emissions|3|0
p_environmental conditions|t_cloud computing|1|1
p_equity|t_cloud computing|4|0
p_gas emissions|t_cloud computing|3|1
p_environmental conditions|t_reinforcement learning|4|0
p_equity|t_reinforcement learning|4|0
p_gas emissions|t_reinforcement learning|9|0
p_resilience|t_machine learning|11|0
p_emergency response|t_machine learning|7|0
p_resilience|t_big data|6|5
p_emergency response|t_big data|7|8
s_urban systems|p_public safety|2|0
p_public safety|t_deep learning|2|0
p_public safety|t_cloud computing|1|0
p_equity|t_deep learning|2|0
p_environmental conditions|t_deep learning|1|6
p_resilience|t_wireless communication|2|0
p_equity|t_wireless communication|1|0
p_emergency response|t_wireless communication|1|0
p_resilience|t_cloud computing|2|0
p_emergency response|t_cloud computing|1|1
p_climate change|t_internet of things|4|0
p_climate change|t_big data|1|1
s_behavioral sciences|p_equity|2|0
p_equity|t_machine learning|8|0
s_mechanism|p_energy consumption|1|1
s_mechanism|p_quality of life|1|0
p_energy consumption|t_machine learning|7|0
s_control theory|p_quality of life|1|0
s_control theory|p_environmental conditions|1|0
s_control theory|p_digital divide|1|0
s_control theory|p_quality of services|1|0
s_control theory|p_traffic management|1|3
s_control theory|p_equity|1|0
p_digital divide|t_machine learning|1|0
p_quality of services|t_machine learning|3|0
p_traffic management|t_machine learning|10|0
p_quality of life|t_reinforcement learning|1|0
p_digital divide|t_reinforcement learning|1|0
p_quality of services|t_reinforcement learning|1|0
p_traffic management|t_reinforcement learning|6|0
p_gas emissions|t_self-driving|3|0
p_public health|t_deep learning|1|0
p_quality of services|t_self-driving|1|0
p_equity|t_self-driving|3|0
p_resilience|t_deep learning|5|0
p_climate change|t_deep learning|1|2
p_emergency response|t_deep learning|4|0
p_equity|t_big data|6|3
p_equity|t_internet of things|10|0
s_urban systems|p_resilience|4|0
s_human mobility|p_resilience|2|0
s_social sciences|p_information security|1|0
p_information security|t_internet of things|3|0
p_public safety|t_big data|2|2
p_information security|t_big data|2|2
p_public safety|t_unmanned aerial vehicle|1|0
p_information security|t_unmanned aerial vehicle|1|0
p_equity|t_unmanned aerial vehicle|1|0
p_traffic management|t_cloud computing|2|0
p_climate change|t_machine learning|3|0
p_quality of life|t_deep learning|2|0
p_quality of life|t_wireless communication|1|0
p_public health|t_internet of things|10|0
s_urban systems|p_equity|2|0
p_gas emissions|t_deep learning|3|0
p_gas emissions|t_machine learning|3|0
s_urban systems|p_traffic management|5|0
p_traffic management|t_self-driving|4|1
s_complexity sciences|p_energy consumption|2|0
s_complexity sciences|p_demand response|1|0
p_demand response|t_machine learning|3|0
p_resilience|t_virtual reality|1|0
p_climate change|t_virtual reality|1|0
p_equity|t_virtual reality|2|0
p_traffic management|t_deep learning|5|3
p_public health|t_digital twin|2|0
p_equity|t_digital twin|3|0
p_environmental conditions|t_digital twin|2|0
p_public health|t_big data|1|2
p_environmental conditions|t_big data|3|6
p_environmental conditions|t_wireless communication|3|1
p_quality of services|t_big data|1|4
p_resilience|t_internet of things|5|2
p_energy consumption|t_internet of things|1|0
p_digital divide|t_internet of things|5|0
p_energy consumption|t_cloud computing|3|0
p_digital divide|t_cloud computing|3|0
p_resilience|t_digital twin|2|0
p_climate change|t_digital twin|1|0
p_emergency response|t_digital twin|4|0
s_social sciences|p_quality of life|1|0
s_social sciences|p_covid-19 pandemic|1|0
p_quality of life|t_virtual reality|1|0
p_covid-19 pandemic|t_virtual reality|1|0
p_equity|t_explainable artificial intelligence|1|0
s_social sciences|p_traffic management|1|0
p_traffic management|t_internet of things|2|2
s_mechanism|p_covid-19 pandemic|1|0
p_covid-19 pandemic|t_wireless communication|2|0
s_complexity sciences|p_digital divide|1|0
s_urban morphology|p_digital divide|1|0
s_complexity sciences|p_environmental conditions|6|1
s_complexity sciences|p_resilience|1|0
s_complexity sciences|p_information security|1|0
p_information security|t_deep learning|1|0
s_urban systems|p_information security|2|0
s_urban systems|p_public health|2|0
s_human mobility|p_traffic management|0|13
p_traffic management|t_big data|0|29
p_sustainable development|t_big data|0|12
s_mechanism|p_resilience|0|3
s_mechanism|p_environmental conditions|0|3
p_sustainable development|t_deep learning|0|3
s_urban morphology|p_sustainable development|0|2
s_mechanism|p_sustainable development|0|2
p_sustainable development|t_machine learning|0|4
p_policy making|t_big data|0|4
s_human mobility|p_equity|0|1
s_mechanism|p_emergency response|0|5
s_urban morphology|p_traffic management|0|2
s_mechanism|p_gas emissions|0|5
p_gas emissions|t_big data|0|5
s_human mobility|p_public health|0|1
p_sustainable development|t_internet of things|0|1
s_human mobility|p_environmental conditions|0|1
s_human mobility|p_gas emissions|0|2
p_gas emissions|t_internet of things|0|1
s_mechanism|p_traffic management|0|3
s_complexity sciences|p_traffic management|0|8
p_quality of life|t_big data|0|1
s_complexity sciences|p_emergency response|0|6
s_mechanism|p_policy making|0|1
s_mechanism|p_quality of services|0|1
s_behavioral sciences|p_gas emissions|0|1
s_complexity sciences|p_rapid urbanization|0|1
p_rapid urbanization|t_big data|0|2
s_urban morphology|p_emergency response|0|1
s_urban morphology|p_energy consumption|0|1
p_energy consumption|t_deep learning|0|2
p_energy consumption|t_self-driving|0|1
s_mechanism|p_climate change|0|1
s_complexity sciences|p_sustainable development|0|1"""

    # 2. Data Processing
    # Load data
    df_raw = pd.read_csv(io.StringIO(csv_data), sep="|")

    # Create scr_data from the raw DataFrame
    scr_data = df_raw.to_dict(orient='records')

    # Clean whitespace for further processing
    df = df_raw.copy()
    df.columns = df.columns.str.strip()
    df['left'] = df['left'].str.strip()
    df['right'] = df['right'].str.strip()

    # Calculate metrics
    df['Total'] = df['NSF'] + df['NSFC']
    # Handle cases where Total is 0 to avoid division by zero
    df['Ratio'] = df.apply(lambda row: row['NSF'] / row['Total'] if row['Total'] != 0 else 0, axis=1)

    # Label Mapping to match the chart image exactly
    label_map = {
        's_human mobility': 'Human mobility',
        's_complexity sciences': 'Complexity sciences',
        's_urban morphology': 'Urban morphology',
        's_mechanism': 'Mechanism',
        's_control theory': 'Control theory',
        's_urban systems': 'Urban systems',
        's_social sciences': 'Social sciences',
        's_behavioral sciences': 'Behavioral sciences',
        
        'p_traffic management': 'Traffic management',
        'p_rapid urbanization': 'Rapid urbanization',
        'p_policy making': 'Policy-making',
        'p_sustainable development': 'Sustainable development',
        'p_emergency response': 'Emergency response',
        'p_environmental conditions': 'Environmental conditions',
        'p_gas emissions': 'Gas emissions',
        'p_quality of services': 'Quality of services',
        'p_resilience': 'Resilience',
        'p_demand response': 'Demand response',
        'p_energy consumption': 'Energy consumption',
        'p_public safety': 'Public safety',
        'p_information security': 'Information security',
        'p_equity': 'Equity',
        'p_climate change': 'Climate change',
        'p_public health': 'Public health',
        'p_digital divide': 'Digital divide',
        'p_quality of life': 'Quality of life',
        'p_covid-19 pandemic': 'COVID-19 pandemic',
        
        't_big data': 'Big data',
        't_self-driving': 'Self-driving',
        't_reinforcement learning': 'Reinforcement learning',
        't_deep learning': 'Deep learning',
        't_machine learning': 'Machine learning',
        't_cloud computing': 'Cloud computing',
        't_digital twin': 'Digital twin',
        't_internet of things': 'Internet of Things',
        't_wireless communication': 'Wireless communication',
        't_unmanned aerial vehicle': 'Unmanned aerial vehicle',
        't_explainable artificial intelligence': 'Explainable AI',
        't_virtual reality': 'Virtual reality'
    }

    # Apply mapping
    df['left_label'] = df['left'].map(label_map)
    df['right_label'] = df['right'].map(label_map)

    # Split into two stages
    # Stage 1: Science (s_) to Problems (p_)
    df_stage1 = df[df['left'].str.startswith('s_')].copy()
    # Stage 2: Problems (p_) to Technology (t_)
    df_stage2 = df[df['right'].str.startswith('t_')].copy()

    # Define explicit order based on the chart image
    order_left = [
        'Human mobility', 'Complexity sciences', 'Urban morphology', 'Mechanism',
        'Control theory', 'Urban systems', 'Social sciences', 'Behavioral sciences'
    ]

    order_mid = [
        'Traffic management', 'Rapid urbanization', 'Policy-making', 'Sustainable development',
        'Emergency response', 'Environmental conditions', 'Gas emissions', 'Quality of services',
        'Resilience', 'Demand response', 'Energy consumption', 'Public safety',
        'Information security', 'Equity', 'Climate change', 'Public health',
        'Digital divide', 'Quality of life', 'COVID-19 pandemic'
    ]

    order_right = [
        'Big data', 'Self-driving', 'Reinforcement learning', 'Deep learning',
        'Machine learning', 'Cloud computing', 'Digital twin', 'Internet of Things',
        'Wireless communication', 'Unmanned aerial vehicle', 'Explainable AI', 'Virtual reality'
    ]
    
    # Calculate node sizes (heights)
    # For middle nodes, height is max(input_sum, output_sum)
    node_sizes = {}

    # Left nodes (only outputs)
    left_sums = df_stage1.groupby('left_label')['Total'].sum()
    for node in order_left:
        node_sizes[node] = left_sums.get(node, 0)

    # Right nodes (only inputs)
    right_sums = df_stage2.groupby('right_label')['Total'].sum()
    for node in order_right:
        node_sizes[node] = right_sums.get(node, 0)

    # Middle nodes (inputs from left, outputs to right)
    mid_inputs = df_stage1.groupby('right_label')['Total'].sum()
    mid_outputs = df_stage2.groupby('left_label')['Total'].sum()

    for node in order_mid:
        inp = mid_inputs.get(node, 0)
        out = mid_outputs.get(node, 0)
        node_sizes[node] = max(inp, out)

    # Convert node_sizes values to standard Python int to avoid TypeError during JSON serialization
    node_sizes_serializable = {k: int(v) for k, v in node_sizes.items()}

    # Prepare derived data for JSON export
    der_data = []

    # Add processed links from df_stage1
    for record in df_stage1.to_dict(orient='records'):
        record['type'] = 'link_stage1'
        der_data.append(record)
    
    # Add processed links from df_stage2
    for record in df_stage2.to_dict(orient='records'):
        record['type'] = 'link_stage2'
        der_data.append(record)

    # Add node sizes
    for node, size in node_sizes_serializable.items():
        der_data.append({'type': 'node_size', 'node': node, 'size': size})

    # Add order lists
    der_data.append({'type': 'order', 'category': 'left', 'values': order_left})
    der_data.append({'type': 'order', 'category': 'mid', 'values': order_mid})
    der_data.append({'type': 'order', 'category': 'right', 'values': order_right})

    # Final output structure
    final_output = {
        'scr_data': scr_data,
        'der_data': der_data
    }

    # Save to JSON
    with open(output_filename, 'w') as f:
        json.dump(final_output, f, indent=4)
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_2_output/177.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compile_data(output_file)
