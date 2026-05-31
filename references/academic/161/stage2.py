import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.lines import Line2D

def generate_chart(output_filename):
    # 1. Source Data
    csv_data = """| million$                               |   Unnamed: 1 |   central estimate of SAF cost |   low SAF cost |   high SAF cost |
|:---------------------------------------|-------------:|-------------------------------:|---------------:|----------------:|
| central estimate of CORSIA offset cost |         2027 |                         -555.1 |         -555.1 |           351.8 |
| nan                                    |         2028 |                         -628.1 |         -668.4 |           134.2 |
| nan                                    |         2029 |                         -692.9 |         -791.4 |           -28.8 |
| nan                                    |         2030 |                         -757.6 |         -925.3 |          -139.5 |
| nan                                    |         2031 |                         -822.3 |        -1070.3 |          -216   |
| nan                                    |         2032 |                         -887.1 |        -1226.5 |          -322   |
| nan                                    |         2033 |                         -951.8 |        -1363   |          -432.1 |
| nan                                    |         2034 |                        -1016.6 |        -1536.2 |          -418.2 |
| nan                                    |         2035 |                        -1081.3 |        -1720.5 |          -344.7 |
| nan                                    |          nan |                          nan   |          nan   |           nan   |
| low estimate of CORSIA offset cost     |         2027 |                          -78.6 |          -78.6 |           828.4 |
| nan                                    |         2028 |                          -44.9 |          -85.2 |           717.4 |
| nan                                    |         2029 |                            7.8 |          -90.7 |           671.9 |
| nan                                    |         2030 |                           71.6 |          -96.1 |           689.7 |
| nan                                    |         2031 |                          146.4 |         -101.6 |           752.7 |
| nan                                    |         2032 |                          232.4 |         -107   |           797.5 |
| nan                                    |         2033 |                          298.7 |         -112.5 |           818.4 |
| nan                                    |         2034 |                          401.7 |         -118   |          1000.1 |
| nan                                    |         2035 |                          515.8 |         -123.4 |          1252.4 |
| nan                                    |          nan |                          nan   |          nan   |           nan   |
| high estimate of CORSIA offset cost    |         2027 |                        -1098.9 |        -1098.9 |          -192   |
| nan                                    |         2028 |                        -1295   |        -1335.3 |          -532.7 |
| nan                                    |         2029 |                        -1495.5 |        -1594   |          -831.4 |
| nan                                    |         2030 |                        -1708.8 |        -1876.5 |         -1090.7 |
| nan                                    |         2031 |                        -1934.9 |        -2182.9 |         -1328.6 |
| nan                                    |         2032 |                        -2174.1 |        -2513.6 |         -1609.1 |
| nan                                    |         2033 |                        -2390.7 |        -2801.9 |         -1871   |
| nan                                    |         2034 |                        -2649.7 |        -3169.4 |         -2051.3 |
| nan                                    |         2035 |                        -2921.6 |        -3560.8 |         -2185   |"""

    # 2. Data Processing
    # Read csv with '|' separator. 
    df = pd.read_csv(io.StringIO(csv_data), sep='|', skipinitialspace=True)
    
    # Clean column names
    df.columns = [c.strip() for c in df.columns]
    
    # Select relevant columns: 'million$', 'Unnamed: 1', 'central...', 'low...', 'high...'
    df = df.iloc[:, 1:6]
    df.columns = ['Scenario', 'Year', 'Central', 'Low', 'High']
    
    # Clean Scenario column: strip whitespace and replace 'nan' string with np.nan
    # This is crucial because the markdown table contains literal "nan" strings in the first column
    df['Scenario'] = df['Scenario'].astype(str).str.strip()
    df['Scenario'] = df['Scenario'].replace({'nan': np.nan, 'NaN': np.nan, '': np.nan})
    
    # Forward fill Scenario to propagate labels to rows with 'nan' scenario
    df['Scenario'] = df['Scenario'].ffill()
    
    # Clean Year column: coerce to numeric (handles '---' separator lines)
    df['Year'] = pd.to_numeric(df['Year'], errors='coerce')
    
    # Drop rows where Year is NaN (removes separator lines and empty spacer lines)
    df = df.dropna(subset=['Year'])
    df['Year'] = df['Year'].astype(int)
    
    # Convert numeric columns
    for col in ['Central', 'Low', 'High']:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    # 3. Plotting Setup
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Colors extracted/approximated from the image
    colors = {
        'high_offset': '#EBD66E',  # Yellow
        'low_offset': '#365C80',   # Dark Blue
        'med_offset': '#E68387'    # Red/Pink
    }
    
    # Configuration for each scenario
    scenario_config = {
        'high estimate of CORSIA offset cost': {
            'label': 'High offset price',
            'color': colors['high_offset'],
            'zorder': 1
        },
        'central estimate of CORSIA offset cost': {
            'label': 'Medium offset price',
            'color': colors['med_offset'],
            'zorder': 2
        },
        'low estimate of CORSIA offset cost': {
            'label': 'Low offset price',
            'color': colors['low_offset'],
            'zorder': 3
        }
    }

    # Add horizontal zero line
    ax.axhline(y=0, color='gray', linestyle=':', linewidth=1.5, zorder=0)

    # Plot each scenario
    unique_scenarios = df['Scenario'].unique()
    
    for sc in unique_scenarios:
        if sc not in scenario_config:
            continue
            
        config = scenario_config[sc]
        subset = df[df['Scenario'] == sc]
        
        if subset.empty:
            continue

        # Plot Confidence Interval (Fill)
        ax.fill_between(
            subset['Year'],
            subset['Low'],
            subset['High'],
            color=config['color'],
            alpha=0.3,
            edgecolor=None,
            zorder=config['zorder']
        )
        
        # Plot Central Line
        ax.plot(
            subset['Year'],
            subset['Central'],
            color=config['color'],
            linewidth=3,
            zorder=config['zorder'] + 10
        )
        
        # Calculate Cumulative Sum in Billions for annotation
        total_sum_billions = subset['Central'].sum() / 1000.0
        
        # Determine text position
        # We place text at Year 2035 with specific Y offsets to match the image
        if config['label'] == 'High offset price':
            text_y = -2500 
        elif config['label'] == 'Medium offset price':
            text_y = -600
        elif config['label'] == 'Low offset price':
            text_y = 1000
        else:
            text_y = 0
            
        ax.text(
            2035,
            text_y,
            f'{total_sum_billions:+.1f} B',
            color=config['color'],
            fontsize=12,
            ha='right',
            va='center',
            zorder=20
        )

    # 4. Styling
    ax.set_xlim(2027, 2035)
    ax.set_ylim(-4000, 6000)
    
    ax.set_ylabel('Net costs of max usage of SAF (million US$)', fontsize=12, color='black')
    
    # Tick styling
    ax.tick_params(axis='both', which='major', direction='in', length=5, labelsize=11)
    ax.yaxis.set_major_formatter(ticker.StrMethodFormatter('{x:,.0f}'))
    
    # Custom Legend
    # Order: High (Yellow), Low (Blue), Medium (Red)
    legend_elements = [
        Line2D([0], [0], color=colors['high_offset'], lw=3, label='High offset price'),
        Line2D([0], [0], color=colors['low_offset'], lw=3, label='Low offset price'),
        Line2D([0], [0], color=colors['med_offset'], lw=3, label='Medium offset price')
    ]
    
    leg = ax.legend(
        handles=legend_elements,
        title='US-S2 with subsidy',
        loc='upper left',
        bbox_to_anchor=(0.02, 0.95),
        frameon=False,
        fontsize=12,
        title_fontsize=12,
        handlelength=1.0
    )
    leg._legend_box.align = "left"

    # Add 'e' tag
    ax.text(
        -0.15, 1.02, 
        'e', 
        transform=ax.transAxes, 
        fontsize=20, 
        fontweight='bold', 
        va='bottom', 
        ha='right',
        color='black'
    )

    # Spines
    for spine in ax.spines.values():
        spine.set_color('black')
        spine.set_linewidth(0.8)

    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    generate_chart(output_file)