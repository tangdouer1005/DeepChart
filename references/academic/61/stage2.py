import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# 1. Source Data embedded as a string
# The data is provided in Markdown table format. We will parse this raw string.
source_data = """
| Unnamed: 0       | GsS             | Unnamed: 2      | Unnamed: 3      | Unnamed: 4      | Unnamed: 5       | Unnamed: 6     | Unnamed: 7      | Unnamed: 8   | Unnamed: 9   | Unnamed: 10   |   Unnamed: 11 | Unnamed: 12        | Unnamed: 13     | Unnamed: 14    | Unnamed: 15     | Unnamed: 16    | Unnamed: 17   | Unnamed: 18   | Unnamed: 19   | Unnamed: 20   | Unnamed: 21   | Unnamed: 22   |
|:-----------------|:----------------|:----------------|:----------------|:----------------|:-----------------|:---------------|:----------------|:-------------|:-------------|:--------------|--------------:|:-------------------|:----------------|:---------------|:----------------|:---------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|
| Log [NT], M      | nan             | nan             | nan             | nan             | nan              | nan            | nan             | nan          | nan          | nan           |           nan | Log [SR142948A], M | nan             | nan            | nan             | nan            | nan           | nan           | nan           | nan           | nan           | nan           |
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
| Log [SBI-553], M | nan             | nan             | nan             | nan             | nan              | nan            | nan             | nan          | nan          | nan           |           nan | Log [PD149163], M  | nan             | nan            | nan             | nan            | nan           | nan           | nan           | nan           | nan           | nan           |
| nan              | 8-4-2022        | 8-4-2022        | 8-5-2022        | 8-5-2022        | 9-29-2022        | 9-29-2022      | 9-29-2022       | 10-7-2022    | 10-7-2022    | 10-7-2022     |           nan | nan                | 9-29-2022       | 9-29-2022      | 9-29-2022       | 10-7-2022      | 10-7-2022     | 10-7-2022     | 2-3-23        | 2-3-23        | 2-3-23        | nan           |
| 3e-05            | 0.07074993082   | 0.04435902911   | -0.001268423857 | -0.04771607     | -0.03709         | -0.0083        | -0.06821        | -0.01462     | -0.03691     | 0.069942      |           nan | 3e-05              | 0.004009819564  | 0.006419128466 | 0.02964973729   | 0.102284       | 0.056093      | 0.10236       | 0.041376      | 0.057526      | 0.049415      | nan           |
| 1e-05            | 0.04078562689   | 0.06102941176   | 0.02872443975   | -0.0320654912   | 0.026047         | -0.0087        | 0.014072        | -0.03147     | 0.045176     | 0.043729      |           nan | 1e-05              | 0.04244131405   | -0.0436899132  | 0.01981601892   | 0.051213       | 0.045067      | 0.064233      | 0.013293      | -0.00965      | 0.029999      | nan           |
| 3e-06            | 0.03143558121   | 0.03328879817   | -0.003381901875 | -0.001997801404 | -0.0225          | -0.02448       | -0.01605        | -0.05277     | -0.0113      | 0.061406      |           nan | 3e-06              | -0.04145339291  | -0.06872598044 | -0.03379406838  | 0.015924       | 0.001245      | 0.083739      | -0.05887      | -0.02026      | -0.01159      | nan           |
| 1e-06            | 0.06523676171   | 0.009559084914  | -0.02071559491  | -0.01830725549  | 0.013456         | -0.02839       | 0.018256        | 0.00106      | -0.03416     | 0.01652       |           nan | 1e-06              | -0.03318833245  | -0.06438868271 | -0.05074334146  | -0.01244       | 0.019514      | 0.082189      | -0.01965      | 0.029373      | -0.04266      | nan           |
| 3e-07            | -0.009287249219 | -0.02585086711  | -0.02147255787  | -0.05960437154  | -0.0107          | -0.04156       | 0.016981        | -0.05159     | -0.01138     | 0.004958      |           nan | 3e-07              | -0.01631398253  | -0.04338753825 | -0.006621125013 | 0.037513       | 0.016547      | 0.034339      | 0.059887      | -0.05411      | -0.0192       | nan           |
| 1e-07            | 0.01701551309   | -0.04912219665  | -0.03927702964  | -0.03846522676  | -0.01706         | -0.01681       | -0.02593        | 0.012357     | -0.00857     | 0.025348      |           nan | 1e-07              | -0.02976721284  | -0.04724854075 | -0.001788609741 | 0.005819       | -0.0203       | 0.01972       | -0.03852      | -0.03387      | -0.05347      | nan           |
| 1e-12            | 0               | 0               | 0               | 0               | 0                | 0              | 0               | 0            | 0            | 0             |           nan | 1e-12              | 0               | 0              | 0               | 0              | 0             | 0             | 0             | 0             | 0             | nan           |
"""

def parse_data(data_str):
    """
    Parses the complex markdown table structure into 4 separate dataframes.
    Structure:
    - Top Left: NT
    - Top Right: SR142948A
    - Bottom Left: SBI-553
    - Bottom Right: PD149163
    """
    # Read the markdown table as a CSV with pipe separator
    # skipinitialspace=True handles the spaces after pipes
    df = pd.read_csv(io.StringIO(data_str), sep='|', skipinitialspace=True, header=None)
    
    # Clean up: Remove the first and last columns if they are empty (common in markdown tables)
    # The first column is often empty because lines start with |
    if df.iloc[:, 0].astype(str).str.strip().eq('').all() or df.iloc[:, 0].isna().all():
        df = df.iloc[:, 1:]
    # The last column might be empty if lines end with |
    if df.iloc[:, -1].astype(str).str.strip().eq('').all() or df.iloc[:, -1].isna().all():
        df = df.iloc[:, :-1]
        
    # Reset columns to integer index for easier slicing
    df.columns = range(df.shape[1])

    # Helper to process a sub-block
    def process_block(sub_df):
        # Row 0 is the header (e.g., "Log [NT], M"), Row 1 is dates, Row 2+ is data
        # We need to find the data rows.
        # The first column is Concentration. The rest are replicates.
        
        # Extract concentration (X) and values (Y)
        # Filter out rows where concentration is NaN or string 'nan'
        clean_df = sub_df.iloc[2:].copy() # Skip header and date row
        
        # Convert to numeric, coercing errors to NaN
        clean_df = clean_df.apply(pd.to_numeric, errors='coerce')
        
        # Drop rows where X (col 0) is NaN
        clean_df = clean_df.dropna(subset=[clean_df.columns[0]])
        
        x = clean_df.iloc[:, 0].values
        y_data = clean_df.iloc[:, 1:].values
        
        # Calculate Mean and SEM
        # Note: Some columns might be NaN (missing replicates), so use nanmean/nanstd
        y_mean = np.nanmean(y_data, axis=1)
        y_sem = np.nanstd(y_data, axis=1, ddof=1) / np.sqrt(np.sum(~np.isnan(y_data), axis=1))
        
        # Log transform X (Concentration is in Molar)
        # Handle 0 or very small numbers if necessary, but data looks like 1e-5, etc.
        x_log = np.log10(x)
        
        return x_log, y_mean, y_sem

    # Define block coordinates based on the provided table structure
    # The table has two main horizontal sections separated by empty rows.
    
    # Find the row index for the second block headers
    # Look for "Log [SBI-553]" in the first column
    split_idx = df[df[0].astype(str).str.contains("SBI-553", na=False)].index[0]
    
    # Block 1: NT (Top Left)
    # Rows: 1 (header) to split_idx-1. Cols: 0 to 10
    # Note: In the raw df, Row 0 is the markdown header line "Unnamed...", Row 1 is "Log [NT]..."
    # Let's slice strictly.
    
    # Top Left (NT)
    # Cols 0 (Conc) and 1-10 (Data)
    df_nt = df.iloc[1:split_idx-2, 0:11] 
    nt_data = process_block(df_nt)
    
    # Top Right (SR142948A)
    # Cols 12 (Conc) and 13-22 (Data)
    df_sr = df.iloc[1:split_idx-2, 12:23]
    sr_data = process_block(df_sr)
    
    # Bottom Left (SBI-553)
    # Rows split_idx to end. Cols 0 to 10
    df_sbi = df.iloc[split_idx:, 0:11]
    sbi_data = process_block(df_sbi)
    
    # Bottom Right (PD149163)
    # Rows split_idx to end. Cols 12 to 22
    df_pd = df.iloc[split_idx:, 12:23]
    pd_data = process_block(df_pd)
    
    return {
        "NT": nt_data,
        "SR": sr_data,
        "SBI": sbi_data,
        "PD": pd_data
    }

def plot_chart(data, output_path):
    # Setup figure
    fig, ax = plt.subplots(figsize=(4, 3.5))
    
    # Styling constants based on image analysis
    # Colors: 
    # NT (Top Left) -> Dark Blue (Control/Reference)
    # SR (Top Right) -> Purple
    # SBI (Bottom Left) -> Orange
    # PD (Bottom Right) -> Green
    
    colors = {
        "NT": "#00008B",   # Dark Blue
        "SBI": "#FFA500",  # Orange
        "PD": "#3CB371",   # Medium Sea Green
        "SR": "#9400D3"    # Dark Violet/Purple
    }
    
    # Plotting order to match visual layering (Orange seems on top, then Green, etc.)
    # We iterate through the dictionary
    
    # Common style
    marker_size = 8
    cap_size = 3
    line_width = 1.5
    
    # Plot NT (Blue)
    x, y, err = data["NT"]
    ax.errorbar(x, y, yerr=err, fmt='o', color=colors["NT"], 
                markersize=marker_size, capsize=cap_size, elinewidth=line_width, 
                linestyle='-', linewidth=line_width, label='NT')

    # Plot SR (Purple)
    x, y, err = data["SR"]
    ax.errorbar(x, y, yerr=err, fmt='o', color=colors["SR"], 
                markersize=marker_size, capsize=cap_size, elinewidth=line_width, 
                linestyle='-', linewidth=line_width, label='SR142948A')

    # Plot PD (Green)
    x, y, err = data["PD"]
    # PD has a square marker in some contexts, but looks like circle in this specific crop. 
    # We will stick to circle to match the general style, or maybe square if distinct.
    # Looking closely at the crop, the green points look like circles or slightly rounded squares.
    # Let's use circles for consistency with the "flat" look.
    ax.errorbar(x, y, yerr=err, fmt='o', color=colors["PD"], 
                markersize=marker_size, capsize=cap_size, elinewidth=line_width, 
                linestyle='-', linewidth=line_width, label='PD149163')

    # Plot SBI (Orange)
    x, y, err = data["SBI"]
    ax.errorbar(x, y, yerr=err, fmt='o', color=colors["SBI"], 
                markersize=marker_size, capsize=cap_size, elinewidth=line_width, 
                linestyle='-', linewidth=line_width, label='SBI-553')

    # Axis configuration
    ax.set_xlim(-13, -3)
    ax.set_ylim(-0.1, 0.6)
    
    # Ticks
    ax.set_xticks([-12, -10, -8, -6, -4])
    ax.set_yticks([0.0, 0.2, 0.4, 0.6])
    
    # Tick styling
    ax.tick_params(axis='both', which='major', labelsize=14, direction='in', length=4)
    
    # Dashed line at y=0
    ax.axhline(y=0, color='black', linestyle='--', linewidth=0.8, zorder=0)
    
    # Title inside plot
    # "GsS" with subscript s
    ax.text(-12.5, 0.55, r'G$_{\rm s}$S', fontsize=16, ha='left', va='center')
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_path}")

def main():
    # Handle command line argument for output filename
    output_filename = "output.png"
    if len(sys.argv) > 1:
        output_filename = sys.argv[1]
        
    # Parse data
    parsed_data = parse_data(source_data)
    
    # Generate plot
    plot_chart(parsed_data, output_filename)

if __name__ == "__main__":
    main()