import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

def generate_chart(output_filename):
    # 1. Source Data
    csv_data = """Date|E_solar [kWh]|E_fuel [kWh]|E_heat [kWh]|Fuel system efficiency (Gibbs) [%]|Heat system efficiency [%]|IPEC device efficiency (Gibbs) [%]|Fuel system efficiency (HHV) [%]|IPEC device efficiency (HHV) [%]
2020-08-19 00:00:00|154.791|10.4153|60.6679|5.47092|38.3446|20.3615|6.5829|24.5
2020-08-20 00:00:00|275.969|20.0619|107.334|5.94472|38.2694|21.9405|7.153|26.4
2020-08-21 00:00:00|224.841|15.9314|87.3055|5.79087|38.1847|21.4419|6.96788|25.8
2020-08-24 00:00:00|264.534|19.2475|101.679|5.94933|37.8166|22.0236|7.15854|26.5
2021-02-17 00:00:00|77.6414|5.58401|27.7777|5.87082|35.1403|21.7743|7.06408|26.2
2021-02-23 00:00:00|128.928|7.61501|43.6776|4.78073|32.9943|17.8682|5.75242|21.5
2021-02-24 00:00:00|156.83|9.67157|52.5228|5.00715|32.7189|18.6162|6.02487|22.4
2021-02-25 00:00:00|191.114|12.7748|65.2465|5.45997|33.5545|20.1953|6.56972|24.3
2021-02-26 00:00:00|54.2302|3.29407|17.5064|4.93685|31.5697|18.3669|5.94028|22.1
2021-03-01 00:00:00|210.299|12.8753|70.6659|4.99228|32.9691|18.5331|6.00697|22.3
2021-03-02 00:00:00|118.593|7.28012|37.5582|5.00232|31.0524|18.5331|6.01905|22.3
2021-03-05 00:00:00|4.20444|0.2585|1.33517|4.9503|30.766|18.6162|5.95645|22.4
2021-03-12 00:00:00|22.4122|1.67846|5.83005|6.12886|25.6151|22.6054|7.37457|27.2"""

    # Load Data
    df = pd.read_csv(io.StringIO(csv_data), sep="|")
    
    # Clean column names (remove whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Convert Date to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Create custom date labels: "19 Aug. 2020"
    # %b gives "Aug", we need to add the dot manually if it's not May
    def format_date(d):
        month_str = d.strftime("%b")
        if len(month_str) == 3 and month_str != "May":
            month_str += "."
        return d.strftime(f"%d {month_str} %Y")
    
    df['DateLabel'] = df['Date'].apply(format_date)

    # 2. Plotting Setup
    fig, ax1 = plt.subplots(figsize=(10, 7))
    
    # Define Colors (matching the image)
    color_solar = '#d9d9d9'  # Light Grey
    color_fuel_bar = '#f4cccc' # Light Red/Pink
    color_heat_bar = '#cfe2f3' # Light Blue
    
    color_heat_line = '#666666' # Dark Grey
    color_fuel_line = '#cc4125' # Red
    color_ipec_line = '#3d85c6' # Blue
    
    bar_edge_color = '#555555'
    bar_width = 0.35
    
    x = np.arange(len(df))

    # --- Left Axis: Bar Chart (Energy) ---
    # Solar (Input) - Left Bar
    ax1.bar(x - bar_width/2, df['E_solar [kWh]'], width=bar_width, 
            color=color_solar, edgecolor=bar_edge_color, linewidth=0.8, label='Solar (input)')
    
    # Fuel (Output) - Right Bar (Bottom)
    ax1.bar(x + bar_width/2, df['E_fuel [kWh]'], width=bar_width, 
            color=color_fuel_bar, edgecolor=bar_edge_color, linewidth=0.8, label='Fuel (output)')
    
    # Heat (Output) - Right Bar (Top, stacked on Fuel)
    ax1.bar(x + bar_width/2, df['E_heat [kWh]'], width=bar_width, bottom=df['E_fuel [kWh]'],
            color=color_heat_bar, edgecolor=bar_edge_color, linewidth=0.8, label='Heat (output)')

    # Axis 1 Styling
    ax1.set_ylabel('Energy (kWh)', fontsize=12, labelpad=10)
    ax1.set_ylim(0, 300)
    ax1.set_yticks(np.arange(0, 301, 100))
    ax1.set_xticks(x)
    ax1.set_xticklabels(df['DateLabel'], rotation=90, fontsize=10)
    ax1.set_xlabel('Date', fontsize=12, labelpad=10)
    
    # Remove top spine for aesthetic match
    ax1.spines['top'].set_visible(False)

    # --- Right Axis: Line Chart (Efficiency) ---
    ax2 = ax1.twinx()
    
    # Marker styles
    marker_size = 4
    
    # Heat system efficiency (Solid Grey, Square)
    ax2.plot(x, df['Heat system efficiency [%]'], color=color_heat_line, 
             marker='s', markersize=marker_size, linestyle='-', linewidth=1.5, label='Heat system efficiency')
    
    # Fuel system efficiency HHV (Solid Red, Triangle Up) -> "Enthalpy"
    ax2.plot(x, df['Fuel system efficiency (HHV) [%]'], color=color_fuel_line, 
             marker='^', markersize=marker_size, linestyle='-', linewidth=1.5, label='Fuel system efficiency')
    
    # Fuel system efficiency Gibbs (Dashed Red, Triangle Up) -> "Gibbs"
    ax2.plot(x, df['Fuel system efficiency (Gibbs) [%]'], color=color_fuel_line, 
             marker='^', markersize=marker_size, linestyle='--', linewidth=1.5)
    
    # IPEC device efficiency HHV (Solid Blue, Triangle Up) -> "Enthalpy"
    ax2.plot(x, df['IPEC device efficiency (HHV) [%]'], color=color_ipec_line, 
             marker='^', markersize=marker_size, linestyle='-', linewidth=1.5, label='IPEC device efficiency')
    
    # IPEC device efficiency Gibbs (Dashed Blue, Triangle Up) -> "Gibbs"
    ax2.plot(x, df['IPEC device efficiency (Gibbs) [%]'], color=color_ipec_line, 
             marker='^', markersize=marker_size, linestyle='--', linewidth=1.5)

    # Axis 2 Styling
    ax2.set_ylabel('Efficiency (%)', fontsize=12, rotation=270, labelpad=20)
    ax2.set_ylim(0, 40)
    ax2.set_yticks(np.arange(0, 41, 5))
    ax2.spines['top'].set_visible(False)

    # --- Legend ---
    # The chart has a custom legend layout at the top.
    # We will construct handles manually to match the visual order and style.
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D

    legend_elements = [
        # Column 1: Bars
        Patch(facecolor=color_solar, edgecolor=bar_edge_color, label='Solar (input)'),
        Patch(facecolor=color_fuel_bar, edgecolor=bar_edge_color, label='Fuel (output)'),
        Patch(facecolor=color_heat_bar, edgecolor=bar_edge_color, label='Heat (output)'),
        
        # Column 2: Lines
        Line2D([0], [0], color=color_heat_line, marker='s', markersize=5, label='Heat system efficiency'),
        Line2D([0], [0], color=color_fuel_line, marker='^', markersize=5, label='Fuel system efficiency'),
        Line2D([0], [0], color=color_ipec_line, marker='^', markersize=5, label='IPEC device efficiency'),
    ]

    # Place legend above the plot area
    ax1.legend(handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, 1.15), 
               ncol=2, frameon=False, fontsize=10, columnspacing=2)

    # --- Annotations ---
    # "a" label in top left
    ax1.text(-0.12, 1.1, 'a', transform=ax1.transAxes, fontsize=20, fontweight='bold', va='top')

    # Arrows and Text for Enthalpy/Gibbs
    # Based on visual inspection, arrows point to the IPEC lines (Blue) around March 2021
    
    # Index for annotation (around 2021-03-05, which is index 11)
    idx_anno = 11 
    
    # Enthalpy (Solid line)
    y_enthalpy = df.loc[idx_anno, 'IPEC device efficiency (HHV) [%]']
    ax2.annotate('Enthalpy', 
                 xy=(idx_anno, y_enthalpy), 
                 xytext=(idx_anno - 2.5, y_enthalpy + 5),
                 arrowprops=dict(arrowstyle='->', color='#274e13', lw=1.5, connectionstyle="arc3,rad=-0.2"),
                 fontsize=12, color='#222222')

    # Gibbs (Dashed line)
    y_gibbs = df.loc[idx_anno, 'IPEC device efficiency (Gibbs) [%]']
    ax2.annotate('Gibbs', 
                 xy=(idx_anno, y_gibbs), 
                 xytext=(idx_anno - 1.5, y_gibbs - 5),
                 arrowprops=dict(arrowstyle='->', color='#274e13', lw=1.5, connectionstyle="arc3,rad=0.2"),
                 fontsize=12, color='#222222')

    # Adjust layout to prevent clipping
    plt.tight_layout()
    plt.subplots_adjust(top=0.85) # Make room for legend

    # Save
    plt.savefig(output_filename, dpi=300)

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else 'output.png'
    generate_chart(output_file)