import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

# 1. Source Data (Figure 3B)
# Embedded as a string to ensure the script is self-contained.
csv_data = """
|   Compound | Vehicle - Vehicle (Barr KO)   | Unnamed: 2     | Unnamed: 3     | Unnamed: 4     | Unnamed: 5      | Unnamed: 6     | Vehicle + 100 nM NT (β-arrestin1/2-null)   | Unnamed: 8    | Unnamed: 9    | Unnamed: 10   | Unnamed: 11   | Unnamed: 12   | SBI-553 + 100 nM NT (β-arrestin1/2-null)   | Unnamed: 14     | Unnamed: 15     | Unnamed: 16     | Unnamed: 17     | Unnamed: 18     | Vehicle - Vehicle (Parentals)   | Unnamed: 20    | Unnamed: 21    | Unnamed: 22    | Unnamed: 23    | Unnamed: 24    | Vehicle + 100 nM NT (Parentals)   | Unnamed: 26   | Unnamed: 27   | Unnamed: 28   | Unnamed: 29   | Unnamed: 30   | SBI-553 + 100 nM NT (Parentals)   | Unnamed: 32     | Unnamed: 33     | Unnamed: 34    | Unnamed: 35     | Unnamed: 36     |
|-----------:|:------------------------------|:---------------|:---------------|:---------------|:----------------|:---------------|:-------------------------------------------|:--------------|:--------------|:--------------|:--------------|:--------------|:-------------------------------------------|:----------------|:----------------|:----------------|:----------------|:----------------|:--------------------------------|:---------------|:---------------|:---------------|:---------------|:---------------|:----------------------------------|:--------------|:--------------|:--------------|:--------------|:--------------|:----------------------------------|:----------------|:----------------|:---------------|:----------------|:----------------|
|   nan      | 4/5/24                        | 4/5/24         | 3/21/24        | 3/21/24        | 3/20/24         | 3/20/24        | 4/5/24                                     | 4/5/24        | 3/21/24       | 3/21/24       | 3/20/24       | 3/20/24       | 4/5/24                                     | 4/5/24          | 3/21/24         | 3/21/24         | 3/20/24         | 3/20/24         | 4/5/24                          | 4/5/24         | 3/21/24        | 3/21/24        | 3/20/24        | 3/20/24        | 4/5/24                            | 4/5/24        | 3/21/24       | 3/21/24       | 3/20/24       | 3/20/24       | 4/5/24                            | 4/5/24          | 3/21/24         | 3/21/24        | 3/20/24         | 3/20/24         |
|     3e-06  | nan                           | nan            | nan            | nan            | nan             | nan            | nan                                        | nan           | nan           | nan           | nan           | nan           | -0.02861489896                             | -0.02534887022  | -0.02470798873  | -0.02293069454  | -0.01842958889  | -0.005885784002 | nan                             | nan            | nan            | nan            | nan            | nan            | nan                               | nan           | nan           | nan           | nan           | nan           | -0.02648540792                    | -0.03431096244  | -0.03134469387  | -0.0276378503  | -0.0198520841   | -0.01868319724  |
|     1e-06  | nan                           | nan            | nan            | nan            | nan             | nan            | nan                                        | nan           | nan           | nan           | nan           | nan           | -0.01720810583                             | -0.02277382307  | -0.0224886877   | -0.02130169224  | -0.001877246815 | -0.01686383811  | nan                             | nan            | nan            | nan            | nan            | nan            | nan                               | nan           | nan           | nan           | nan           | nan           | -0.02273463684                    | -0.0305364072   | -0.02746253747  | -0.02827190012 | -0.01939144376  | -0.01906813104  |
|     3e-07  | nan                           | nan            | nan            | nan            | nan             | nan            | nan                                        | nan           | nan           | nan           | nan           | nan           | -0.008754857984                            | -0.01869604892  | -0.02442366417  | -0.01455620321  | -0.02200375729  | -0.01186286174  | nan                             | nan            | nan            | nan            | nan            | nan            | nan                               | nan           | nan           | nan           | nan           | nan           | -0.01631486779                    | -0.02343409472  | -0.02170710833  | -0.02286571592 | -0.01967013291  | -0.01779204555  |
|     1e-07  | nan                           | nan            | nan            | nan            | nan             | nan            | nan                                        | nan           | nan           | nan           | nan           | nan           | -0.002557009086                            | -0.009217734112 | -0.001693144711 | -0.009353540879 | -0.01373197457  | 0.0001741767881 | nan                             | nan            | nan            | nan            | nan            | nan            | nan                               | nan           | nan           | nan           | nan           | nan           | 3.350256129e-05                   | -0.008737920738 | -0.003072724318 | -0.01490436994 | -0.008381411757 | -0.001659829496 |
|     3e-08  | nan                           | nan            | nan            | nan            | nan             | nan            | nan                                        | nan           | nan           | nan           | nan           | nan           | 0.01274290695                              | 0.009948265757  | 0.02143541528   | 0.01877877084   | 0.009836638368  | 0.007992366491  | nan                             | nan            | nan            | nan            | nan            | nan            | nan                               | nan           | nan           | nan           | nan           | nan           | 0.01161403799                     | 0.0132841525    | 0.01718808944   | 0.0199751414   | 0.01233298292   | 0.01171714308   |
|     1e-08  | nan                           | nan            | nan            | nan            | nan             | nan            | nan                                        | nan           | nan           | nan           | nan           | nan           | 0.03509492739                              | 0.05726017259   | 0.04770833857   | 0.04155319399   | 0.02691974711   | 0.01832493684   | nan                             | nan            | nan            | nan            | nan            | nan            | nan                               | nan           | nan           | nan           | nan           | nan           | 0.04403028961                     | 0.03298227147   | 0.03132594171   | 0.03174542459  | 0.02567187847   | 0.03468688622   |
|     3e-09  | nan                           | nan            | nan            | nan            | nan             | nan            | nan                                        | nan           | nan           | nan           | nan           | nan           | 0.06183100993                              | 0.05781920003   | 0.06527415838   | 0.06376379927   | 0.06132385753   | 0.05207189198   | nan                             | nan            | nan            | nan            | nan            | nan            | nan                               | nan           | nan           | nan           | nan           | nan           | 0.05038710885                     | 0.04244685272   | 0.05070531999   | 0.051574858    | 0.04547793995   | 0.05396636209   |
|     1e-11  | nan                           | nan            | nan            | nan            | nan             | nan            | nan                                        | nan           | nan           | nan           | nan           | nan           | 0.09027572259                              | 0.08817040097   | 0.08794183791   | 0.1071636582    | 0.09356712381   | 0.09780909901   | nan                             | nan            | nan            | nan            | nan            | nan            | nan                               | nan           | nan           | nan           | nan           | nan           | 0.06790302682                     | 0.05603475244   | 0.06585767193   | 0.06078379136  | 0.0712802248    | 0.07757727791   |
|   nan      | nan                           | nan            | nan            | nan            | nan             | nan            | nan                                        | nan           | nan           | nan           | nan           | nan           | nan                                        | nan             | nan             | nan             | nan             | nan             | nan                             | nan            | nan            | nan            | nan            | nan            | nan                               | nan           | nan           | nan           | nan           | nan           | nan                               | nan             | nan             | nan            | nan             | nan             |
|     0.0001 | -0.0292683692                 | -0.03240320878 | -0.02995225071 | -0.0307002276  | -0.01963164265  | -0.01605227019 | 0.09655177186                              | 0.08791824426 | 0.07007740211 | 0.08286376189 | 0.1085727747  | 0.07727154568 | nan                                        | nan             | nan             | nan             | nan             | nan             | -0.0351213984                   | -0.03475586978 | -0.03262092714 | -0.03465933828 | -0.02634052048 | -0.02620901985 | 0.07049728027                     | 0.06808558031 | 0.04844928431 | 0.06645440144 | 0.07506574481 | 0.06813289575 | nan                               | nan             | nan             | nan            | nan             | nan             |
|     1e-05  | -0.02925573644                | -0.03369631857 | -0.03870240819 | -0.03137772205 | -0.02921765704  | -0.01808909976 | 0.09948915499                              | 0.08946808055 | 0.06908475884 | 0.09310962907 | 0.08466025123 | 0.06905911923 | nan                                        | nan             | nan             | nan             | nan             | nan             | -0.03329906245                  | -0.03335228603 | -0.03933986393 | -0.02999804905 | -0.0212635972  | -0.02125639223 | 0.06739693708                     | 0.06452817402 | 0.059447888   | 0.06447327486 | 0.06148974018 | 0.0662075036  | nan                               | nan             | nan             | nan            | nan             | nan             |
|     1e-06  | -0.02636610662                | -0.03277680542 | -0.02674453102 | -0.03714323021 | -0.009626431832 | -0.01747546846 | 0.1033700933                               | 0.08738333331 | 0.06546181477 | 0.07470331066 | 0.0681856395  | 0.06998248357 | nan                                        | nan             | nan             | nan             | nan             | nan             | -0.03436850762                  | -0.03146256799 | -0.02739259146 | -0.03231151413 | -0.02733956052 | -0.02308767558 | 0.06221010036                     | 0.06081163623 | 0.05699329464 | 0.06424303233 | 0.0604790871  | 0.05758507954 | nan                               | nan             | nan             | nan            | nan             | nan             |
|     1e-07  | -0.03346920598                | -0.02961102328 | -0.02957906056 | -0.02314549232 | -0.03000217149  | -0.02500019122 | 0.1039269951                               | 0.09708987722 | 0.0689043321  | 0.0906168959  | 0.06591562849 | 0.07654111527 | nan                                        | nan             | nan             | nan             | nan             | nan             | -0.03153206597                  | -0.0331449245  | -0.03408475324 | -0.03263808218 | -0.02086492281 | -0.01810476818 | 0.06467955229                     | 0.06477156934 | 0.0598105424  | 0.07251424096 | 0.06810112223 | 0.06181018095 | nan                               | nan             | nan             | nan            | nan             | nan             |
|     1e-08  | -0.03004810109                | -0.03600095446 | -0.02396217223 | -0.03550574649 | -0.02177447572  | -0.02498297168 | 0.1049999181                               | 0.1014291847  | 0.0791682951  | 0.08227325874 | 0.09757746768 | 0.07890686513 | nan                                        | nan             | nan             | nan             | nan             | nan             | -0.03227721889                  | -0.03025240901 | -0.03159258881 | -0.03401669022 | -0.02113875842 | -0.02389464166 | 0.06624920928                     | 0.06138625023 | 0.06607723502 | 0.06423398517 | 0.06660145312 | 0.06116796897 | nan                               | nan             | nan             | nan            | nan             | nan             |
|     1e-09  | -0.02816762576                | -0.02123827019 | -0.03489026705 | -0.0323382531  | -0.02343084062  | -0.02152033409 | 0.09448202197                              | 0.09430806455 | 0.07963041078 | 0.09436301006 | 0.09129279194 | 0.08267269497 | nan                                        | nan             | nan             | nan             | nan             | nan             | -0.03058005566                  | -0.0322043504  | -0.03255815641 | -0.03358907524 | -0.0269761561  | -0.02696948936 | 0.06250991574                     | 0.06370951397 | 0.06134031518 | 0.06631263273 | 0.06377883585 | 0.0534727909  | nan                               | nan             | nan             | nan            | nan             | nan             |
|     1e-10  | -0.03374712                   | -0.03564675558 | -0.03241768536 | -0.03459523246 | -0.02532582362  | -0.0224316384  | 0.09462105654                              | 0.08885866496 | 0.07788886029 | 0.111140253   | 0.07946677049 | 0.07856413612 | nan                                        | nan             | nan             | nan             | nan             | nan             | -0.03557264006                  | -0.03511497793 | -0.03615156562 | -0.02887642809 | -0.02794511627 | -0.02489293123 | 0.06209511661                     | 0.05956464427 | 0.06288923056 | 0.07318791243 | 0.06912003938 | 0.05824835695 | nan                               | nan             | nan             | nan            | nan             | nan             |
|     1e-11  | -0.0301527272                 | -0.03374560111 | -0.03225891944 | -0.02384022167 | -0.01900973176  | -0.02580818287 | 0.09240278738                              | 0.08259450613 | 0.0884250945  | 0.1029884454  | 0.09041059681 | 0.08936627788 | nan                                        | nan             | nan             | nan             | nan             | nan             | -0.03426036729                  | -0.03364416379 | -0.0325945799  | -0.03226655919 | -0.02903513174 | -0.02730516504 | 0.05784055117                     | 0.06108335539 | 0.06758209641 | 0.07878642173 | 0.07990185908 | 0.07159174348 | nan                               | nan             | nan             | nan            | nan             | nan             |
"""

def process_data(csv_str):
    # Read CSV, handling the pipe separator and whitespace
    df = pd.read_csv(io.StringIO(csv_str), sep="|", header=0, skipinitialspace=True)
    
    # Remove the first row (dates) and any completely empty rows
    df = df.iloc[1:].copy()
    
    # Clean column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Convert Compound to numeric, coerce errors to NaN
    df['Compound'] = pd.to_numeric(df['Compound'], errors='coerce')
    
    # Drop rows where Compound is NaN
    df = df.dropna(subset=['Compound'])
    
    # Calculate log10 of Compound
    df['LogCompound'] = np.log10(df['Compound'])
    
    # Convert all other columns to numeric
    for col in df.columns:
        if col not in ['Compound', 'LogCompound']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    return df

def plot_chart(df, output_path):
    fig, ax = plt.subplots(figsize=(6, 5))
    
    # Define the groups based on column indices
    # Note: Indices are 0-based. 
    # Compound is 0.
    # Null/Vehicle: 1-6 (6 cols)
    # Null/NT+Veh: 7-12 (6 cols)
    # Null/NT+SBI: 13-18 (6 cols)
    # Parent/Vehicle: 19-24 (6 cols)
    # Parent/NT+Veh: 25-30 (6 cols)
    # Parent/NT+SBI: 31-36 (6 cols)
    
    # Colors
    color_veh = '#808080' # Gray
    color_nt_veh = '#00008B' # Dark Blue
    color_nt_sbi = '#BA55D3' # Medium Orchid / Purple
    
    # Groups configuration
    groups = [
        # Parentals (+) - Filled Circles, Solid Lines
        {
            'label': 'Vehicle (Parentals)',
            'cols': range(19, 25),
            'color': color_veh,
            'marker': 'o',
            'linestyle': '-',
            'fill': True
        },
        {
            'label': '100 nM NT + vehicle (Parentals)',
            'cols': range(25, 31),
            'color': color_nt_veh,
            'marker': 'o',
            'linestyle': '-',
            'fill': True
        },
        {
            'label': '100 nM NT + SBI-553 (Parentals)',
            'cols': range(31, 37),
            'color': color_nt_sbi,
            'marker': 'o',
            'linestyle': '-',
            'fill': True
        },
        # Null (-) - Open Circles, Dashed Lines
        {
            'label': 'Vehicle (Null)',
            'cols': range(1, 7),
            'color': color_veh,
            'marker': 'o',
            'linestyle': '--',
            'fill': False
        },
        {
            'label': '100 nM NT + vehicle (Null)',
            'cols': range(7, 13),
            'color': color_nt_veh,
            'marker': 'o',
            'linestyle': '--',
            'fill': False
        },
        {
            'label': '100 nM NT + SBI-553 (Null)',
            'cols': range(13, 19),
            'color': color_nt_sbi,
            'marker': 'o',
            'linestyle': '--',
            'fill': False
        }
    ]
    
    # Plot each group
    for g in groups:
        # Select columns by index
        cols = df.iloc[:, list(g['cols'])]
        
        # Calculate Mean and SEM
        mean = cols.mean(axis=1)
        sem = cols.sem(axis=1)
        x = df['LogCompound']
        
        # Marker face color
        mfc = g['color'] if g['fill'] else 'white'
        
        # Plot errorbar
        ax.errorbar(
            x, mean, yerr=sem,
            fmt=g['marker'],
            color=g['color'],
            markerfacecolor=mfc,
            markeredgecolor=g['color'],
            markeredgewidth=1.5,
            linestyle=g['linestyle'],
            linewidth=1.5,
            capsize=4,
            markersize=8,
            label=g['label']
        )

    # Axis styling
    ax.set_xlabel('log[Compound] (M)', fontsize=12)
    ax.set_ylabel('Mini G$_q$ recruitment\n($\Delta$ Net BRET)', fontsize=12)
    
    # Ticks
    ax.set_xticks([-12, -10, -8, -6, -4])
    ax.set_xlim(-11.5, -3.5)
    
    # Y-axis ticks and limits
    ax.set_yticks([0, 0.03, 0.06, 0.09, 0.12, 0.15])
    ax.set_ylim(-0.02, 0.15)
    
    # Horizontal dotted line at 0
    ax.axhline(0, color='black', linestyle=':', linewidth=1.5)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Tick parameters (ticks facing out)
    ax.tick_params(direction='out', length=6, width=1)
    
    # Custom Legend Construction to match the image
    # The image has a matrix-style legend.
    # Columns: + (Filled), - (Open), Label
    # Rows: Vehicle, NT+Veh, NT+SBI
    
    # Create custom handles
    legend_handles = []
    
    # Header
    # We can't easily put headers in a standard legend, so we will construct handles that look like the rows
    
    # Row 1: Vehicle
    h_veh_fill = mlines.Line2D([], [], color=color_veh, marker='o', linestyle='-', 
                               markerfacecolor=color_veh, markersize=8, label='_nolegend_')
    h_veh_open = mlines.Line2D([], [], color=color_veh, marker='o', linestyle='--', 
                               markerfacecolor='white', markeredgewidth=1.5, markersize=8, label='_nolegend_')
    
    # Row 2: NT + Veh
    h_nt_fill = mlines.Line2D([], [], color=color_nt_veh, marker='o', linestyle='-', 
                              markerfacecolor=color_nt_veh, markersize=8, label='_nolegend_')
    h_nt_open = mlines.Line2D([], [], color=color_nt_veh, marker='o', linestyle='--', 
                              markerfacecolor='white', markeredgewidth=1.5, markersize=8, label='_nolegend_')
    
    # Row 3: NT + SBI
    h_sbi_fill = mlines.Line2D([], [], color=color_nt_sbi, marker='o', linestyle='-', 
                               markerfacecolor=color_nt_sbi, markersize=8, label='_nolegend_')
    h_sbi_open = mlines.Line2D([], [], color=color_nt_sbi, marker='o', linestyle='--', 
                               markerfacecolor='white', markeredgewidth=1.5, markersize=8, label='_nolegend_')

    # To replicate the exact look of the legend in the image (floating text and markers),
    # we will manually place the legend elements on the axes.
    
    # Legend position (upper right)
    lx, ly = 0.55, 0.95
    dy = 0.08
    dx_mark = 0.1
    
    # Headers
    ax.text(lx, ly, "+", transform=ax.transAxes, ha='center', va='center', fontsize=10)
    ax.text(lx + dx_mark, ly, "–", transform=ax.transAxes, ha='center', va='center', fontsize=10) # En dash
    ax.text(lx + dx_mark*2.5, ly, r"$\beta$-arrestin 1/2", transform=ax.transAxes, ha='center', va='center', fontsize=10)
    
    # Row 1: Vehicle
    y1 = ly - dy
    ax.add_line(mlines.Line2D([lx], [y1], transform=ax.transAxes, color=color_veh, marker='o', 
                              markerfacecolor=color_veh, markersize=8, linestyle='-'))
    ax.add_line(mlines.Line2D([lx + dx_mark], [y1], transform=ax.transAxes, color=color_veh, marker='o', 
                              markerfacecolor='white', markeredgewidth=1.5, markersize=8, linestyle='--'))
    ax.text(lx + dx_mark*1.5, y1, "Vehicle", transform=ax.transAxes, ha='left', va='center', fontsize=10)
    
    # Row 2: NT + Veh
    y2 = ly - 2*dy
    ax.add_line(mlines.Line2D([lx], [y2], transform=ax.transAxes, color=color_nt_veh, marker='o', 
                              markerfacecolor=color_nt_veh, markersize=8, linestyle='-'))
    ax.add_line(mlines.Line2D([lx + dx_mark], [y2], transform=ax.transAxes, color=color_nt_veh, marker='o', 
                              markerfacecolor='white', markeredgewidth=1.5, markersize=8, linestyle='--'))
    ax.text(lx + dx_mark*1.5, y2, "100 nM NT + vehicle", transform=ax.transAxes, ha='left', va='center', fontsize=10)
    
    # Row 3: NT + SBI
    y3 = ly - 3*dy
    ax.add_line(mlines.Line2D([lx], [y3], transform=ax.transAxes, color=color_nt_sbi, marker='o', 
                              markerfacecolor=color_nt_sbi, markersize=8, linestyle='-'))
    ax.add_line(mlines.Line2D([lx + dx_mark], [y3], transform=ax.transAxes, color=color_nt_sbi, marker='o', 
                              markerfacecolor='white', markeredgewidth=1.5, markersize=8, linestyle='--'))
    ax.text(lx + dx_mark*1.5, y3, "100 nM NT + SBI-553", transform=ax.transAxes, ha='left', va='center', fontsize=10)
    
    # Add lines behind markers in legend (short segments)
    # The add_line above adds a point. To add the line segment visible in the legend:
    line_len = 0.04
    for y_pos, col in zip([y1, y2, y3], [color_veh, color_nt_veh, color_nt_sbi]):
        # Solid line behind filled marker
        ax.add_line(mlines.Line2D([lx - line_len/2, lx + line_len/2], [y_pos, y_pos], 
                                  transform=ax.transAxes, color=col, linestyle='-', linewidth=1.5, zorder=0))
        # Dashed line behind open marker
        ax.add_line(mlines.Line2D([lx + dx_mark - line_len/2, lx + dx_mark + line_len/2], [y_pos, y_pos], 
                                  transform=ax.transAxes, color=col, linestyle='--', linewidth=1.5, zorder=0))

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    
    try:
        df_clean = process_data(csv_data)
        plot_chart(df_clean, output_file)
        print(f"Chart successfully saved to {output_file}")
    except Exception as e:
        print(f"An error occurred: {e}")