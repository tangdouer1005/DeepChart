import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def generate_chart(output_filename):
    # 1. Source Data Loading
    # Using the raw markdown table provided in the prompt
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
    
    # Forward fill the first column to identify groups (handling the 'nan' in the first column)
    df['million$'] = df['million$'].str.strip()
    df['group'] = df['million$'].fillna(method='ffill')
    
    # Drop rows where Year (Unnamed: 1) is NaN (the separator rows)
    df = df.dropna(subset=['Unnamed: 1'])
    
    # Convert numeric columns
    cols_to_numeric = ['Unnamed: 1', 'central estimate of SAF cost', 'low SAF cost', 'high SAF cost']
    for col in cols_to_numeric:
        df[col] = pd.to_numeric(df[col])

    # 2. Plotting Setup
    fig, ax = plt.subplots(figsize=(8, 6))
    
    # Define styles based on the image
    # Mapping: 
    # "low estimate of CORSIA..." -> Corresponds to "Low offset price" (Blue)
    # "central estimate of CORSIA..." -> Corresponds to "Medium offset price" (Pink/Red)
    # "high estimate of CORSIA..." -> Corresponds to "High offset price" (Yellow)
    
    styles = {
        "high estimate of CORSIA offset cost": {
            "label": "High offset price",
            "color": "#EDD968", # Yellow
            "fill_color": "#F9F0C2",
            "zorder": 1,
            "text_offset": -200
        },
        "central estimate of CORSIA offset cost": {
            "label": "Medium offset price",
            "color": "#E67E83", # Pink/Red
            "fill_color": "#F2D4D7",
            "zorder": 2,
            "text_offset": 200
        },
        "low estimate of CORSIA offset cost": {
            "label": "Low offset price",
            "color": "#2B5576", # Dark Blue
            "fill_color": "#DCE6F1",
            "zorder": 3,
            "text_offset": 400
        }
    }

    # Add Zero Line (dotted grey)
    ax.axhline(y=0, color='grey', linestyle=':', linewidth=1.5, zorder=0)

    # Plotting Loop
    # We iterate in a specific order to match the visual layering if needed, 
    # though zorder handles it.
    
    for group_key, style in styles.items():
        subset = df[df['group'] == group_key]
        
        x = subset['Unnamed: 1']
        y = subset['central estimate of SAF cost']
        y_low = subset['low SAF cost']
        y_high = subset['high SAF cost']
        
        # Plot Fill (Confidence Interval)
        ax.fill_between(x, y_low, y_high, color=style['color'], alpha=0.2, zorder=style['zorder']-0.5, edgecolor=None)
        
        # Plot Line (Central Estimate)
        line, = ax.plot(x, y, color=style['color'], linewidth=3, label=style['label'], zorder=style['zorder'])
        
        # Calculate Cumulative Sum for the annotation (Billions)
        # The labels in the chart (5.3 B, -2.2 B, -10.9 B) match the sum of the central estimates.
        total_sum_billions = y.sum() / 1000.0
        label_text = f"{total_sum_billions:+.1f} B".replace("+", "") # Format: 5.3 B
        
        # Add Annotation at the end of the line (Year 2035)
        # Adjust y-position slightly for readability based on the chart
        last_x = x.iloc[-1]
        last_y = y.iloc[-1]
        
        # Manual adjustments to match the exact placement in the image
        text_y = last_y
        if "High" in style['label']: text_y = -2200 # Yellow label position
        if "Medium" in style['label']: text_y = -800 # Pink label position
        if "Low" in style['label']: text_y = 600    # Blue label position

        ax.text(last_x - 0.2, text_y, label_text, 
                color=style['color'], 
                fontsize=14, 
                ha='right', 
                va='center',
                zorder=10)

    # 3. Formatting
    
    # Axis Limits
    ax.set_xlim(2027, 2035)
    ax.set_ylim(-4000, 6000)
    
    # Axis Labels
    ax.set_ylabel("Net costs of max usage of SAF (million US$)", fontsize=14, color='black')
    
    # Ticks styling
    ax.tick_params(axis='both', which='major', direction='in', length=6, width=1, labelsize=12)
    ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
    
    # Y-axis formatting (comma separator)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, p: format(int(x), ',')))

    # Legend
    # Custom legend to match "China-S2" title inside
    handles, labels = ax.get_legend_handles_labels()
    # Reorder handles/labels to match image: High (Yellow), Low (Blue), Medium (Pink)
    # Note: The image legend order is High, Low, Medium.
    order_map = {"High offset price": 0, "Low offset price": 1, "Medium offset price": 2}
    
    # Sort handles and labels based on the desired order
    sorted_pairs = sorted(zip(handles, labels), key=lambda t: order_map.get(t[1], 99))
    sorted_handles, sorted_labels = zip(*sorted_pairs)

    legend = ax.legend(sorted_handles, sorted_labels, 
              title="China-S2", 
              loc='lower left', 
              frameon=False, 
              fontsize=14,
              title_fontsize=14,
              handlelength=1.0,
              borderpad=1)
    
    # Align legend title to the left
    legend._legend_box.align = "left"

    # Figure Title ("a")
    fig.text(0.02, 0.92, 'a', fontsize=20, fontweight='bold')

    # Layout adjustments
    plt.tight_layout()
    plt.subplots_adjust(left=0.15, top=0.92) # Make room for 'a' and y-label

    # 4. Save Output
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    generate_chart(output_file)