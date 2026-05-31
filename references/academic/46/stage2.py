import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def parse_data():
    """
    Parses the provided Markdown table data into a structured format.
    Returns a dictionary organized by Temperature -> Current Density -> Stats.
    """
    raw_data = """
| 20°C                     | Unnamed: 1           | Unnamed: 2          |   Unnamed: 3 | Unnamed: 4           | Unnamed: 5          |   Unnamed: 6 | Unnamed: 7           | Unnamed: 8          |
|:-------------------------|:---------------------|:--------------------|-------------:|:---------------------|:--------------------|-------------:|:---------------------|:--------------------|
| nan                      | Replicat 1           | nan                 |          nan | Replicat 2           | nan                 |          nan | Replicat 3           | nan                 |
| Current Density (mA/cm2) | H2 FE                | C2H4 FE             |          nan | H2 FE                | C2H4 FE             |          nan | H2 FE                | C2H4 FE             |
| 50                       | 0.08537673569365246  | 0.26467052796869767 |          nan | 0.08167807532660352  | 0.2715174916982006  |          nan | 0.1008398877664833   | 0.3242463201791644  |
| 100                      | 0.07734861766689143  | 0.3370705791505792  |          nan | 0.08067045341041623  | 0.33778392153834275 |          nan | 0.07897327818291043  | 0.355462815661441   |
| 200                      | 0.05609432556306102  | 0.4211414008803768  |          nan | 0.059522533193569725 | 0.3936044482199397  |          nan | 0.05728876894563645  | 0.4251558575951811  |
| 300                      | 0.05274345437591877  | 0.4662604576930008  |          nan | 0.06734880141006057  | 0.4448016063016449  |          nan | 0.055999498493840186 | 0.4534645146343346  |
| 400                      | 0.058479502876713205 | 0.4930699667928025  |          nan | 0.06384438141239715  | 0.47177009807707154 |          nan | 0.05412386492696144  | 0.46792855046721754 |
| 500                      | 0.060372065031340474 | 0.5067397327978994  |          nan | 0.07440862950235112  | 0.494182593250444   |          nan | 0.05403572835935277  | 0.4914513491389296  |
| 600                      | 0.08930380834692322  | 0.5199876438335006  |          nan | 0.07612401476448684  | 0.5303411846474632  |          nan | 0.05502586864229536  | 0.5201310989265581  |
| 700                      | 0.10344494402208719  | 0.5339828116898161  |          nan | 0.08016057244077929  | 0.540143772823053   |          nan | 0.05873204426173124  | 0.5322631951722693  |
| 800                      | 0.101163419381741    | 0.5465617885551007  |          nan | 0.08226838394918916  | 0.5547238396787396  |          nan | 0.07356489789783285  | 0.5444405745617421  |
| nan                      | nan                  | nan                 |          nan | nan                  | nan                 |          nan | nan                  | nan                 |
| 35°C                     | nan                  | nan                 |          nan | nan                  | nan                 |          nan | nan                  | nan                 |
| nan                      | Replicat 1           | nan                 |          nan | Replicat 2           | nan                 |          nan | Replicat 3           | nan                 |
| Current Density (mA/cm2) | H2 FE                | C2H4 FE             |          nan | H2 FE                | C2H4 FE             |          nan | H2 FE                | C2H4 FE             |
| 50                       | 0.045759793687734474 | 0.3007363245553067  |          nan | 0.04285428149567634  | 0.2957992122943856  |          nan | 0.03203752092552121  | 0.30451679666383497 |
| 100                      | 0.04202066657706356  | 0.4470212886451978  |          nan | 0.0482930118384704   | 0.43512950807012124 |          nan | 0.04770422071877059  | 0.42162313692176995 |
| 200                      | 0.04856413902073766  | 0.46404273174247684 |          nan | 0.05198357885679493  | 0.45624928565912426 |          nan | 0.04732282166013344  | 0.4508900918989882  |
| 300                      | 0.0547168825732173   | 0.5161030366995306  |          nan | 0.049919774932073974 | 0.5061493551625608  |          nan | 0.048255782434338174 | 0.49766827811671427 |
| 400                      | 0.05692524269876567  | 0.5427476510412644  |          nan | 0.04836585197698996  | 0.5344012665070661  |          nan | 0.05056177981963668  | 0.532264553247355   |
| 500                      | 0.06132465217620189  | 0.5424596185033593  |          nan | 0.05503072465153     | 0.5535539114989575  |          nan | 0.05084929603307084  | 0.5424838674801141  |
| 600                      | 0.06841217750634926  | 0.547847401343733   |          nan | 0.059550859914105116 | 0.5509955981156845  |          nan | 0.0693285693971932   | 0.5474283574021159  |
| 700                      | 0.07215625055235173  | 0.546927528877023   |          nan | 0.0660972228394665   | 0.5497058570435664  |          nan | 0.06892342021402553  | 0.5375206292819081  |
| 800                      | 0.08957425827327294  | 0.5272588301541945  |          nan | 0.07774167284077546  | 0.5426517877828404  |          nan | 0.08747387409843203  | 0.5225119623136921  |
| nan                      | nan                  | nan                 |          nan | nan                  | nan                 |          nan | nan                  | nan                 |
| 50°C                     | nan                  | nan                 |          nan | nan                  | nan                 |          nan | nan                  | nan                 |
| nan                      | Replicat 1           | nan                 |          nan | Replicat 2           | nan                 |          nan | Replicat 3           | nan                 |
| Current Density (mA/cm2) | H2 FE                | C2H4 FE             |          nan | H2 FE                | C2H4 FE             |          nan | H2 FE                | C2H4 FE             |
| 50                       | 0.025105567743076117 | 0.360388395500296   |          nan | 0.024428963789716616 | 0.36906946739773994 |          nan | 0.049077257329864364 | 0.3884275851417098  |
| 100                      | 0.035417842909410566 | 0.4756591757407264  |          nan | 0.025936484878780763 | 0.46362115993513014 |          nan | 0.04901089187032432  | 0.45621230983087496 |
| 200                      | 0.041019114672419574 | 0.5467736504749401  |          nan | 0.03048278863556476  | 0.5557290498622802  |          nan | 0.05281861011143449  | 0.5327903930805468  |
| 300                      | 0.05219940148944549  | 0.5495089968337323  |          nan | 0.042064190807981426 | 0.5567659518967574  |          nan | 0.06838407560105621  | 0.5469182794038149  |
| 400                      | 0.08649328059475557  | 0.5439740263083378  |          nan | 0.051445640944913426 | 0.5524246608489716  |          nan | 0.08446663862959414  | 0.5525811491234844  |
| 500                      | 0.11141411765319736  | 0.5360420315597085  |          nan | 0.07201914922496049  | 0.5443333364223749  |          nan | 0.12712635602193603  | 0.521707443045795   |
| 600                      | 0.24505131193822877  | 0.45377168550123986 |          nan | 0.18856675207750645  | 0.46761231154700916 |          nan | 0.19752296418354415  | 0.5115029423121477  |
| 700                      | 0.2849113113375841   | 0.40461638148193096 |          nan | 0.22701164872227916  | 0.4402729359501929  |          nan | 0.2603469573856352   | 0.478414178701058   |
| 800                      | 0.462160562220723    | 0.2615366308852678  |          nan | 0.32130378613219124  | 0.3846849537930857  |          nan | 0.401623021930255    | 0.343008583674415   |
    """
    
    # Read as a list of lines to handle the jagged structure manually
    lines = [line.strip() for line in raw_data.strip().split('\n')]
    
    # Helper to clean a line into a list of values
    def clean_line(l):
        # Remove leading/trailing pipes and split
        parts = l.strip('|').split('|')
        return [p.strip() for p in parts]

    data_blocks = {}
    current_temp = None
    
    # Indices for columns based on the table structure
    # Col 0: Current Density
    # Rep 1: H2 (1), C2H4 (2)
    # Rep 2: H2 (4), C2H4 (5)
    # Rep 3: H2 (7), C2H4 (8)
    
    # Iterate and find blocks
    i = 0
    while i < len(lines):
        row = clean_line(lines[i])
        
        # Detect Temperature Header
        if len(row) > 0 and "20°C" in row[0]:
            current_temp = "20°C"
            i += 3 # Skip header rows (Replicat row, Unit row)
        elif len(row) > 0 and "35°C" in row[0]:
            current_temp = "35°C"
            i += 3
        elif len(row) > 0 and "50°C" in row[0]:
            current_temp = "50°C"
            i += 3
        
        # Process Data Rows
        if current_temp and i < len(lines):
            row = clean_line(lines[i])
            # Check if it's a data row (starts with a number)
            if row[0].replace('.', '', 1).isdigit():
                cd = int(row[0])
                
                # Extract values, handling potential empty strings
                try:
                    h2_vals = [float(row[1]), float(row[4]), float(row[7])]
                    c2h4_vals = [float(row[2]), float(row[5]), float(row[8])]
                    
                    # Convert to Percentage (Data is 0.08 -> 8%)
                    h2_vals = [x * 100 for x in h2_vals]
                    c2h4_vals = [x * 100 for x in c2h4_vals]
                    
                    if current_temp not in data_blocks:
                        data_blocks[current_temp] = {'CD': [], 'H2_mean': [], 'H2_std': [], 'C2H4_mean': [], 'C2H4_std': []}
                    
                    data_blocks[current_temp]['CD'].append(cd)
                    data_blocks[current_temp]['H2_mean'].append(np.mean(h2_vals))
                    data_blocks[current_temp]['H2_std'].append(np.std(h2_vals))
                    data_blocks[current_temp]['C2H4_mean'].append(np.mean(c2h4_vals))
                    data_blocks[current_temp]['C2H4_std'].append(np.std(c2h4_vals))
                    
                except (ValueError, IndexError):
                    pass # Skip malformed rows
        i += 1
        
    return data_blocks

def plot_chart(data, output_path):
    # Setup
    fig, ax = plt.subplots(figsize=(14, 6))
    
    # Constants
    temps = ["20°C", "35°C", "50°C"]
    current_densities = data["20°C"]['CD'] # Assuming all temps have same CDs
    x = np.arange(len(current_densities))
    width = 0.22
    
    # Styling
    # Colors extracted from image
    color_h2 = '#aebcd6'   # Light blue/grey
    color_c2h4 = '#6c85b5' # Medium blue
    
    # Hatching patterns
    hatches = {
        "20°C": "",
        "35°C": "////",
        "50°C": "xxxx"
    }
    
    # Plotting Loop
    for i, temp in enumerate(temps):
        offset = (i - 1) * width
        
        h2_means = data[temp]['H2_mean']
        h2_stds = data[temp]['H2_std']
        c2h4_means = data[temp]['C2H4_mean']
        c2h4_stds = data[temp]['C2H4_std']
        
        # H2 Bars (Bottom)
        ax.bar(x + offset, h2_means, width, 
               label=f"H2 {temp}", 
               color=color_h2, 
               edgecolor='white', linewidth=0.5,
               hatch=hatches[temp],
               yerr=h2_stds, capsize=3, error_kw={'elinewidth':1, 'alpha':0.8})
        
        # C2H4 Bars (Stacked on H2)
        ax.bar(x + offset, c2h4_means, width, 
               bottom=h2_means,
               label=f"C2H4 {temp}", 
               color=color_c2h4, 
               edgecolor='white', linewidth=0.5,
               hatch=hatches[temp],
               yerr=c2h4_stds, capsize=3, error_kw={'elinewidth':1, 'alpha':0.8})

    # Axis Configuration
    ax.set_ylabel('FE (%)', fontsize=12)
    ax.set_xlabel('Current density (mA cm$^{-2}$)', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(current_densities, fontsize=10)
    ax.set_ylim(0, 120)
    
    # Grid
    ax.yaxis.grid(True, linestyle='--', which='major', color='grey', alpha=0.5)
    ax.set_axisbelow(True)
    
    # Tag "e"
    ax.text(-0.08, 1.02, 'e', transform=ax.transAxes, fontsize=20, fontweight='bold', va='top', ha='right')

    # Custom Legend Construction
    # Row 1: Colors (Chemicals)
    # Note: The source data only provided H2 and C2H4, so we only plot those.
    # To faithfully represent the provided data, we only show legends for what is plotted.
    legend_handles_color = [
        mpatches.Patch(facecolor=color_h2, label='H$_2$'),
        mpatches.Patch(facecolor=color_c2h4, label='C$_2$H$_4$'),
        # Placeholders for missing data if we wanted to match the image exactly, 
        # but we must stick to source data.
        # mpatches.Patch(facecolor='#5b6e96', label='Acetate'),
        # mpatches.Patch(facecolor='#e6c2b5', label='Ethanol'),
        # mpatches.Patch(facecolor='#b56b5b', label='n-propanol'),
    ]
    
    # Row 2: Patterns (Temperatures)
    legend_handles_pattern = [
        mpatches.Patch(facecolor='#aebcd6', hatch='', label='20 °C', edgecolor='white'), # Using H2 color as base for legend
        mpatches.Patch(facecolor='#aebcd6', hatch='////', label='35 °C', edgecolor='white'),
        mpatches.Patch(facecolor='#aebcd6', hatch='xxxx', label='50 °C', edgecolor='white'),
    ]
    
    # Combine legends
    # We create two legends. One for colors, one for patterns.
    
    # Legend 1: Chemicals (Top Left)
    leg1 = ax.legend(handles=legend_handles_color, loc='upper left', 
                     bbox_to_anchor=(0, 1.02), ncol=5, frameon=False, fontsize=10)
    ax.add_artist(leg1)
    
    # Legend 2: Temperatures (Below Legend 1)
    leg2 = ax.legend(handles=legend_handles_pattern, loc='upper left', 
                     bbox_to_anchor=(0, 0.97), ncol=3, frameon=False, fontsize=10)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save
    plt.savefig(output_path, dpi=300)

if __name__ == "__main__":
    output_filename = "output.png"
    if len(sys.argv) > 1:
        output_filename = sys.argv[1]
        
    data = parse_data()
    plot_chart(data, output_filename)