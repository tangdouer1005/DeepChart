import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def generate_chart(output_filename='output.png'):
    # ---------------------------------------------------------
    # 1. Data Preparation
    # ---------------------------------------------------------
    # The data is embedded directly from the provided source table.
    # We extract the numerical columns for "Parental" and "LN" (Lymph node).
    
    csv_data = """Parental,LN
0.9405664903089984,0.32166830172851885
1.0020154316232128,0.3065971299955544
1.0574180780677889,0.38985097865305635
0.98465942,0.3127913917149869
1.04898903,0.34022398910412494
1.10698891,0.4149112275779394
1.0057907649121947,0.33172340422096624
0.9572862232473632,0.5516546189292959
1.0370697519659795,0.31744212086969126
0.9901110640197729,0.43409434874755287
0.9657994848913162,0.4216916045495087
1.0440995063306664,0.4451561371567206
0.9264813777791925,0.28882262702890416
0.9554945029996652,0.4216717606818705
1.1180088762214924,0.4302036746779516
0.9421485840530326,0.34887427878694655
0.9878714805620564,0.6803316399338138
1.07005230930726,0.44816722877251564
1.0055519007557248,0.33674783
0.9326038381751974,0.32097013
1.062106775951418,0.40812685
1.1032391006172184,0.4483543718709108
0.8939311991643537,0.48793744034978476
1.003016907328868,0.453499387396596
1.0398765132984888,0.32510537462909633
0.9317790704041532,0.7637741640758461
1.0283641836165913,0.43536556238911184
1.0000041662624255,0.4024079380150075
1.00005172,0.3518128287936721
1.000051718465634,0.42933228029431986
nan,0.3527665999583561
nan,0.33568636466945223
nan,0.3516858970610669
nan,0.44391373089849534
nan,0.4454432251916396
nan,0.3592625732815101
nan,0.30620820244136754
nan,0.46474997779162325
nan,0.2677934167687582
nan,0.5357849810972981
nan,0.5127838632461413
nan,0.502396559075916
nan,0.4265378928818343
nan,0.4560260939976978
nan,0.441351382336324
nan,0.47635893884990743
nan,0.48272731515580847
nan,0.4496045713248384
nan,0.3775688947150515
nan,0.5652846266389681
nan,0.36890084560662906
nan,0.4544443094789942
nan,0.44146013555692687
nan,0.466024664785878
nan,0.3286913425500528
nan,0.3489360512429212
nan,0.30106599265181266
nan,0.3905464680379359
nan,0.34503789523367795
nan,0.3510093445430288
nan,0.2521139553293007
nan,0.4869817123608369
nan,0.28264140928813736
nan,0.3967565260831017
nan,0.4751328403142235
nan,0.45545327161219845
nan,0.3038158540455491
nan,0.4279212489385044
nan,0.33702002878965054
nan,0.7007039427613408
nan,0.4178179676122032
nan,0.5382826255257271
nan,0.40134002441438077
nan,0.6889071955165279
nan,0.3933389265165961
"""
    
    # Read data into DataFrame
    df = pd.read_csv(io.StringIO(csv_data))
    
    # Extract series and drop NaNs
    parental = df['Parental'].dropna()
    ln = df['LN'].dropna()
    
    # Calculate statistics
    mean_parental = parental.mean()
    std_parental = parental.std()
    
    mean_ln = ln.mean()
    std_ln = ln.std()
    
    # ---------------------------------------------------------
    # 2. Plotting Setup
    # ---------------------------------------------------------
    # Set figure size to match the portrait aspect ratio of the original image
    fig, ax = plt.subplots(figsize=(2.5, 4.5))
    
    # Define colors
    color_parental_bar = '#d9d9d9'  # Light grey
    color_parental_dot = 'black'
    color_ln_bar = '#98c992'        # Muted light green
    color_ln_dot = '#3a8e3a'        # Darker green for dots
    
    # ---------------------------------------------------------
    # 3. Draw Bars
    # ---------------------------------------------------------
    # Bar positions
    x_pos = [0, 1]
    means = [mean_parental, mean_ln]
    colors = [color_parental_bar, color_ln_bar]
    
    ax.bar(x_pos, means, color=colors, edgecolor='black', linewidth=0.8, width=0.6, zorder=1)
    
    # ---------------------------------------------------------
    # 4. Draw Error Bars
    # ---------------------------------------------------------
    # Using standard deviation as error bars
    ax.errorbar(x_pos, means, yerr=[std_parental, std_ln], fmt='none', 
                ecolor='black', capsize=6, elinewidth=1.5, markeredgewidth=1.5, zorder=3)
    
    # ---------------------------------------------------------
    # 5. Draw Individual Data Points (Swarm Plot)
    # ---------------------------------------------------------
    # Create a long-form DataFrame for seaborn plotting
    df_plot = pd.DataFrame({
        'Group': ['Parental'] * len(parental) + ['LN'] * len(ln),
        'Value': pd.concat([parental, ln], ignore_index=True)
    })
    
    # Define palette for the dots
    palette = {'Parental': color_parental_dot, 'LN': color_ln_dot}
    
    # Use swarmplot with hue and palette to control colors correctly
    # order=['Parental', 'LN'] ensures alignment with x=0 and x=1
    sns.swarmplot(x='Group', y='Value', hue='Group', data=df_plot, 
                  order=['Parental', 'LN'], palette=palette, 
                  size=4.5, ax=ax, zorder=2, legend=False)

    # ---------------------------------------------------------
    # 6. Statistical Annotation
    # ---------------------------------------------------------
    # Draw the line and text for P value
    line_y = 1.35
    
    # Draw the horizontal line
    ax.plot([0, 1], [line_y, line_y], color='black', linewidth=0.8)
    
    # Add text
    ax.text(0.5, line_y + 0.02, r'$P < 1 \times 10^{-15}$', ha='center', va='bottom', fontsize=11)

    # ---------------------------------------------------------
    # 7. Styling and Formatting
    # ---------------------------------------------------------
    # Axis Labels
    ax.set_ylabel('Relative GCLC levels', fontsize=12, labelpad=5)
    ax.set_xlabel('') # No x-label text
    
    # X Ticks
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Parental', 'LN'], rotation=45, ha='right', fontsize=12)
    
    # Y Ticks and Limits
    ax.set_ylim(0, 1.5)
    ax.set_yticks([0, 0.5, 1.0, 1.5])
    ax.tick_params(axis='y', labelsize=11)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Add Figure Label "f"
    ax.text(-0.3, 1.05, 'f', transform=ax.transAxes, fontsize=20, fontweight='bold', va='bottom', ha='right')

    # Adjust layout
    plt.tight_layout()
    
    # ---------------------------------------------------------
    # 8. Save Output
    # ---------------------------------------------------------
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = 'output.png'
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    generate_chart(output_file)