import sys
import io
import pandas as pd
import json

def process_and_save_data(output_filename='bench/ground_truth_code/nature_2_output/80.json'):
    # 1. Source Data
    csv_data = """Site_type,Site_topography,N_stations,PM_size,N_samples,OP_DTT_m_mean,OP_DTT_m_SEM,PM_mass_mean,PM_mass_SEM
nan,nan,nan,nan,nan,nmol min-1 µg-1,nmol min-1 µg-1,µg m-3,µg m-3
Industrial,nan,6,PM10,696,0.07,0.01,20.22,1.78
Rural,nan,9,PM10,1252,0.07,0.01,15.52,1.0
Suburban,nan,3,PM10,695,0.09,0.02,20.73,6.58
Traffic,nan,4,PM10,1140,0.12,0.01,22.44,3.26
Urban,nan,20,PM10,4243,0.1,0.0,21.91,0.99
"Urban, Industrial, Suburban, Rural",Valley,9,PM10,2572,0.1,0.01,20.34,2.10"""

    # 2. Data Processing
    # Read CSV, skipping the unit row (row index 1)
    df = pd.read_csv(io.StringIO(csv_data), header=0)
    
    raw_df = df.copy()
    
    # Drop the unit row (index 0 in the dataframe after header load)
    df = df.drop(0)
    
    # Convert numeric columns to float
    numeric_cols = ['OP_DTT_m_mean', 'OP_DTT_m_SEM', 'PM_mass_mean', 'PM_mass_SEM']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col])

    # Define mapping for labels and colors based on the chart visual analysis
    
    plot_config = []
    
    for _, row in df.iterrows():
        site_type = row['Site_type']
        topography = row['Site_topography']
        
        label = ""
        color = ""
        text_offset = (0, 0) # (x, y) offset for text
        ha = 'center'
        va = 'center'
        
        if topography == 'Valley':
            label = '(V)'
            color = '#bdbdbd' # Grey
            text_offset = (-1.5, 0.003)
            ha = 'right'
            va = 'bottom'
        elif 'Industrial' in site_type and ',' not in site_type:
            label = 'I'
            color = '#ea8c9f' # Pinkish Red
            text_offset = (-0.5, -0.003)
            ha = 'right'
            va = 'top'
        elif 'Rural' in site_type and ',' not in site_type:
            label = 'R'
            color = '#d67fe2' # Orchid/Purple
            text_offset = (-0.5, -0.003)
            ha = 'right'
            va = 'top'
        elif 'Suburban' in site_type and ',' not in site_type:
            label = 'SU'
            color = '#6fa8dc' # Light Blue
            text_offset = (-1.0, 0.003)
            ha = 'right'
            va = 'bottom'
        elif 'Traffic' in site_type:
            label = 'T'
            color = '#cdae63' # Gold/Mustard
            text_offset = (0.8, 0.003)
            ha = 'left'
            va = 'bottom'
        elif 'Urban' in site_type and ',' not in site_type:
            label = 'U'
            color = '#7bc068' # Green
            text_offset = (0.8, 0.003)
            ha = 'left'
            va = 'bottom'
            
        plot_config.append({
            'x': row['PM_mass_mean'],
            'y': row['OP_DTT_m_mean'],
            'xerr': row['PM_mass_SEM'],
            'yerr': row['OP_DTT_m_SEM'],
            'label': label,
            'color': color,
            'text_offset': text_offset,
            'ha': ha,
            'va': va
        })

    return raw_df, plot_config

if __name__ == "__main__":
    raw_df, processed_data = process_and_save_data()
    
    final_output = {
        "scr_data": raw_df.to_dict(orient='records'),
        "der_data": processed_data
    }
    
    with open('bench/ground_truth_code/nature_1_output/80.json', 'w') as f:
        json.dump(final_output, f, indent=4)
