import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

def generate_chart(output_filename='output.png'):
    # 1. Source Data (Embedded exactly as provided)
    csv_data = """| Unnamed: 0       | GsS             | Unnamed: 2      | Unnamed: 3      | Unnamed: 4      | Unnamed: 5       | Unnamed: 6     | Unnamed: 7      | Unnamed: 8   | Unnamed: 9   | Unnamed: 10   |   Unnamed: 11 | Unnamed: 12        | Unnamed: 13     | Unnamed: 14    | Unnamed: 15     | Unnamed: 16    | Unnamed: 17   | Unnamed: 18   | Unnamed: 19   | Unnamed: 20   | Unnamed: 21   | Unnamed: 22   |
|:-----------------|:----------------|:----------------|:----------------|:----------------|:-----------------|:---------------|:----------------|:-------------|:-------------|:--------------|--------------:|:-------------------|:----------------|:---------------|:----------------|:---------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|
| Log [NT], M      | nan             | nan             | nan             | nan             | nan              | nan            | nan             | nan          | nan          | nan           |           nan | Log [SR142948A], M | nan             | nan            | nan             | nan            | nan           | nan           | nan           | nan           | nan           | nan           |
| nan              | 8-4-2022        | 8-4-2022        | 8-5-2022        | 8-5-2022        | 9-29-2022        | 9-29-2022      | 9-29-2022       | 10-7-2022    | 10-7-2022    | 10-7-2022     |           nan | nan                | 8-4-2022        | 8-4-2022       | 8-5-2022        | 8-5-2022       | 9-29-2022     | 9-29-2022     | 9-29-2022     | 10-7-2022     | 10-7-2022     | 10-7-2022     |
| 1e-05            | -0.1512820513   | -0.0701632464   | -0.03521        | 0.007501        | -0.01744798828   | -0.02741454427 | -0.006572963594 | 0.064873     | 0.034575     | 0.075671      |           nan | 0.0001             | -0.004539442039 | -0.01295724847 | -0.1495348412   | -0.08964964102 | -0.07944      | 0.004145      | 0.070974      | 0.042298      | -0.0007       | 0.007781      |
| 1e-06            | -0.09535423926  | 1.666083537e-05 | -0.0591         | 0.055851        | 0.0004212288537  | -0.04798644971 | -0.01655069907  | 0.032379     | 0.038412     | 0.052439      |           nan | 1e-05              | -0.02935682738  | 0.02165618449  | -0.1025542436   | -0.1385250984  | -0.06961      | -0.00506      | 0.094154      | 0.043259      | 0.028621      | 0.06358       |
| 1e-07            | -0.162305296    | -0.0381571866   | -0.07706        | 0.008714        | -0.003282477324  | -0.04148428892 | -0.04520309915  | 0.061803     | 0.003118     | 0.041369      |           nan | 1e-06              | -0.05512777024  | -0.04992673993 | -0.009389658055 | -0.0926203817  | -0.04568      | -0.0084       | 0.054258      | -0.03134      | -0.03041      | 0.015901      |
| 1e-08            | -0.1164007092   | -0.001062954105 | -0.08801        | 0.029205        | 0.002057602462   | 0.03401026784  | -0.07446676423  | 0.045788     | 0.031123     | 0.080397      |           nan | 1e-07              | -0.01757388198  | -0.05805804524 | -0.02005338575  | -0.08555300205 | -0.01935      | 0.020722      | 0.064203      | -0.0266       | -0.03166      | -0.0048       |
| 1e-09            | -0.2309142654   | -0.00206348647  | -0.01635        | -0.00835        | -0.01127328163   | 0.03395398074  | -0.02890324891  | 0.042724     | 0.045733     | 0.040897      |           nan | 1e-08              | -0.01937361419  | -0.1085507246  | 0.003742582303  | -0.03890371597 | -0.04267      | -0.03728      | 0.038776      | 0.0171        | -0.07515      | -0.00336      |
| 1e-10            | -0.05742092457  | -0.04591442486  | -0.01661        | 0.037552        | -0.0002540132439 | 0.01573024041  | -0.0552574848   | 0.040963     | 0.032142     | 0.025043      |           nan | 1e-09              | -0.07126113004  | -0.0167001675  | -0.02335124742  | -0.05426952878 | -0.00125      | -0.04511      | -0.0455       | -0.01562      | -0.00759      | 0.006663      |
| 1e-11            | -0.1012919897   | 0.01198498188   | -0.03516        | 0.036617        | -0.01257538602   | 0.02904405383  | -0.03754393383  | 0.010101     | 0.002281     | 0.018151      |           nan | 1e-10              | -0.09554117407  | -0.11          | 0.008910659111  | -0.01673826039 | -0.04467      | -0.03839      | -0.01571      | -0.01345      | -0.05956      | -0.00538      |
| 1e-12            | 0               | 0               | 0               | 0               | 0                | 0              | 0               | 0            | 0            | 0             |           nan | 1e-12              | 0               | 0              | 0               | 0              | 0             | 0             | 0             | 0             | 0             | 0             |
| nan              | nan             | nan             | nan             | nan             | nan              | nan            | nan             | nan          | nan          | nan           |           nan | nan                | nan             | nan            | nan             | nan            | nan           | nan           | nan           | nan           | nan           | nan           |
| nan              | nan             | nan             | nan             | nan             | nan              | nan            | nan             | nan          | nan          | nan           |           nan | nan                | nan             | nan            | nan             | nan            | nan           | nan           | nan           | nan           | nan           | nan           |
| Log [SBI-553], M | nan             | nan             | nan             | nan             | nan              | nan            | nan             | nan          | nan          | nan           |           nan | Log [PD149163], M  | nan             | nan            | nan             | nan            | nan           | nan           | nan           | nan           | nan           | nan           |
| nan              | 8-4-2022        | 8-4-2022        | 8-5-2022        | 8-5-2022        | 9-29-2022        | 9-29-2022      | 9-29-2022       | 10-7-2022    | 10-7-2022    | 10-7-2022     |           nan | nan                | 9-29-2022       | 9-29-2022      | 9-29-2022       | 10-7-2022      | 10-7-2022     | 10-7-2022     | 2-3-23        | 2-3-23        | 2-3-23        | nan           |
| 3e-05            | 0.07074993082   | 0.04435902911   | -0.001268423857 | -0.04771607     | -0.03709         | -0.0083        | -0.06821        | -0.01462     | -0.03691     | 0.069942      |           nan | 3e-05              | 0.004009819564  | 0.006419128466 | 0.02964973729   | 0.102284       | 0.056093      | 0.10236       | 0.041376      | 0.057526      | 0.049415      | nan           |
| 1e-05            | 0.04078562689   | 0.06102941176   | 0.02872443975   | -0.0320654912   | 0.026047         | -0.0087        | 0.014072        | -0.03147     | 0.045176     | 0.043729      |           nan | 1e-05              | 0.04244131405   | -0.0436899132  | 0.01981601892   | 0.051213       | 0.045067      | 0.064233      | 0.013293      | -0.00965      | 0.029999      | nan           |
| 3e-06            | 0.03143558121   | 0.03328879817   | -0.003381901875 | -0.001997801404 | -0.0225          | -0.02448       | -0.01605        | -0.05277     | -0.0113      | 0.061406      |           nan | 3e-06              | -0.04145339291  | -0.06872598044 | -0.03379406838  | 0.015924       | 0.001245      | 0.083739      | -0.05887      | -0.02026      | -0.01159      | nan           |
| 1e-06            | 0.06523676171   | 0.009559084914  | -0.02071559491  | -0.01830725549  | 0.013456         | -0.02839       | 0.018256        | 0.00106      | -0.03416     | 0.01652       |           nan | 1e-06              | -0.03318833245  | -0.06438868271 | -0.05074334146  | -0.01244       | 0.019514      | 0.082189      | -0.01965      | 0.029373      | -0.04266      | nan           |
| 3e-07            | -0.009287249219 | -0.02585086711  | -0.02147255787  | -0.05960437154  | -0.0107          | -0.04156       | 0.016981        | -0.05159     | -0.01138     | 0.004958      |           nan | 3e-07              | -0.01631398253  | -0.04338753825 | -0.006621125013 | 0.037513       | 0.016547      | 0.034339      | 0.059887      | -0.05411      | -0.0192       | nan           |
| 1e-07            | 0.01701551309   | -0.04912219665  | -0.03927702964  | -0.03846522676  | -0.01706         | -0.01681       | -0.02593        | 0.012357     | -0.00857     | 0.025348      |           nan | 1e-07              | -0.02976721284  | -0.04724854075 | -0.001788609741 | 0.005819       | -0.0203       | 0.01972       | -0.03852      | -0.03387      | -0.05347      | nan           |
| 1e-12            | 0               | 0               | 0               | 0               | 0                | 0              | 0               | 0            | 0            | 0             |           nan | 1e-12              | 0               | 0              | 0               | 0              | 0             | 0             | 0             | 0             | 0             | nan           |"""

    # 2. Data Parsing
    # Read the markdown table. Handle the pipe separators.
    df = pd.read_csv(io.StringIO(csv_data), sep='|', header=0, skipinitialspace=True)
    
    # Clean up column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Drop the first and last columns if they are empty (common in markdown parsing)
    if df.iloc[:, 0].isna().all() or df.columns[0] == '':
        df = df.iloc[:, 1:]
    if df.iloc[:, -1].isna().all() or df.columns[-1] == '':
        df = df.iloc[:, :-1]

    # Helper function to extract a dataset block
    def extract_block(df, start_row, end_row, conc_col_idx, data_col_start, data_col_end):
        # Slice the dataframe
        block = df.iloc[start_row:end_row].copy()
        
        # Extract concentration
        conc_str = block.iloc[:, conc_col_idx]
        # Convert to numeric, coercing errors
        conc = pd.to_numeric(conc_str, errors='coerce')
        
        # Extract data values
        data_vals = block.iloc[:, data_col_start:data_col_end]
        # Convert all to numeric
        data_vals = data_vals.apply(pd.to_numeric, errors='coerce')
        
        # Calculate Mean and SEM (Standard Error of Mean)
        mean = data_vals.mean(axis=1)
        sem = data_vals.sem(axis=1)
        
        # Create result dataframe
        result = pd.DataFrame({
            'Concentration': conc,
            'Mean': mean,
            'SEM': sem
        })
        
        # Drop rows where Concentration is NaN
        result = result.dropna(subset=['Concentration'])
        
        # Calculate Log Concentration
        # Handle 0 or negative values just in case, though concentrations are usually > 0
        result = result[result['Concentration'] > 0]
        result['LogConc'] = np.log10(result['Concentration'])
        
        # Sort by LogConc ascending for plotting lines
        result = result.sort_values('LogConc')
        
        return result

    # Define blocks based on visual inspection of the table structure
    # Block 1: NT (Top Left). Rows 2-10 approx. Conc Col 0. Data Cols 1-11.
    # Block 2: SR (Top Right). Rows 2-10 approx. Conc Col 12. Data Cols 13-23.
    # Block 3: SBI (Bottom Left). Rows 14-21 approx. Conc Col 0. Data Cols 1-11.
    # Block 4: PD (Bottom Right). Rows 14-21 approx. Conc Col 12. Data Cols 13-23.

    # Note: Indices in pandas are 0-based.
    # The header is row 0 in the CSV string, but pandas consumes it.
    # So "Log [NT]" is actually the header or index.
    # Let's rely on row indices.
    
    # Extract Block 1 (NT)
    # Rows 2 to 10 (inclusive of data). 
    # Note: Row 0 is "nan | 8-4-2022...", Row 1 is "1e-05..." in the dataframe index if header=0 took the first line.
    # Let's inspect the dataframe structure logic:
    # The provided string has a header line.
    # Row 0 in DF: "nan | 8-4-2022..."
    # Row 1 in DF: "1e-05 | -0.15..."
    
    ds1 = extract_block(df, 1, 10, 0, 1, 11)
    ds2 = extract_block(df, 1, 10, 12, 13, 23)
    ds3 = extract_block(df, 13, 21, 0, 1, 11)
    ds4 = extract_block(df, 13, 21, 12, 13, 23)

    # 3. Plotting
    fig, ax = plt.subplots(figsize=(4, 3.5)) # Small scientific figure size

    # Styling constants matching the image
    colors = ['#00008B', '#2E8B57', '#9400D3', '#FF8C00'] # Blue, Green, Purple, Orange
    # Adjust colors to match image better
    colors = [
        '#000099', # Deep Blue
        '#45a070', # Sea Green / Teal
        '#b030b0', # Magenta/Purple
        '#f59e30'  # Orange
    ]
    
    datasets = [ds1, ds2, ds3, ds4]
    
    for i, data in enumerate(datasets):
        x = data['LogConc']
        y = data['Mean']
        err = data['SEM']
        color = colors[i]
        
        # Plot Error Bars and Markers
        ax.errorbar(x, y, yerr=err, fmt='o', color=color, 
                    ecolor=color, elinewidth=1.5, capsize=3, 
                    markersize=7, markeredgewidth=0, zorder=5)
        
        # Plot Smooth Line (Spline)
        # Only smooth if we have enough points
        if len(x) > 3:
            try:
                # Create a smooth curve
                x_new = np.linspace(x.min(), x.max(), 200)
                # k=2 (quadratic) or k=3 (cubic). k=2 is often safer for noisy dose-response without a model fit
                spl = make_interp_spline(x, y, k=2) 
                y_smooth = spl(x_new)
                ax.plot(x_new, y_smooth, color=color, linewidth=2, zorder=4)
            except:
                # Fallback to straight lines
                ax.plot(x, y, color=color, linewidth=2, zorder=4)
        else:
            ax.plot(x, y, color=color, linewidth=2, zorder=4)

    # 4. Chart Styling
    
    # Axes Limits and Ticks
    # X-Axis: Log scale labels -12 to -4
    ax.set_xlim(-12.5, -3.5)
    ax.set_xticks([-12, -10, -8, -6, -4])
    ax.set_xticklabels(['$-12$', '$-10$', '$-8$', '$-6$', '$-4$'], fontsize=12)
    
    # Y-Axis: 
    # The image goes 0 to 0.6. The data is much smaller/negative (GsS data vs Gi1 image).
    # To be faithful to the data, we let it scale, but we ensure the style matches.
    # If we force 0-0.6, the data will look like flat lines.
    # We will allow autoscaling but ensure the zero line is visible.
    ylim = ax.get_ylim()
    # Ensure 0 is included and there's some headroom
    ax.set_ylim(min(ylim[0], -0.05), max(ylim[1], 0.05))
    
    # Add dashed zero line
    ax.axhline(0, color='black', linestyle='--', linewidth=0.8, zorder=1)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Tick styling
    ax.tick_params(axis='both', which='both', direction='in', length=4, width=1, labelsize=12)
    
    # Add Label "Gi1" (or GsS based on data, but image says Gi1)
    # Using Gi1 to match the visual request.
    ax.text(0.05, 0.95, 'G$_{i1}$', transform=ax.transAxes, fontsize=14, verticalalignment='top')
    
    # Adjust layout
    plt.tight_layout()
    
    # Save output
    plt.savefig(output_filename, dpi=300)

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)