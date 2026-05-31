import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Source Data provided in the prompt
DATA_CSV = """
|   Compound | Vehicle          | Unnamed: 2       | Unnamed: 3     | Unnamed: 4     | Unnamed: 5     | Unnamed: 6     | Unnamed: 7     | Unnamed: 8       | Unnamed: 9     | Vehicle + 100 nM NT   | Unnamed: 11   | Unnamed: 12   | Unnamed: 13   | Unnamed: 14   | Unnamed: 15   | Unnamed: 16   | Unnamed: 17   | Unnamed: 18   | SBI-553 + 100 nM NT   | Unnamed: 20    | Unnamed: 21   | Unnamed: 22   | Unnamed: 23   | Unnamed: 24   | Unnamed: 25   | Unnamed: 26   | Unnamed: 27   | SR14 + 100 nM NT   | Unnamed: 29    | Unnamed: 30    | Unnamed: 31    | Unnamed: 32    | Unnamed: 33     | Unnamed: 34    | Unnamed: 35    | Unnamed: 36   |
|-----------:|:-----------------|:-----------------|:---------------|:---------------|:---------------|:---------------|:---------------|:-----------------|:---------------|:----------------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:----------------------|:---------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:--------------|:-------------------|:---------------|:---------------|:---------------|:---------------|:----------------|:---------------|:---------------|:--------------|
|   nan      | 3/14/24          | 3/14/24          | 3/14/24        | 3/7/24         | 3/7/24         | 3/7/24         | 3/1/24         | 3/1/24           | 3/1/24         | 3/14/24               | 3/14/24       | 3/14/24       | 3/7/24        | 3/7/24        | 3/7/24        | 3/1/24        | 3/1/24        | 3/1/24        | 3/14/24               | 3/14/24        | 3/14/24       | 3/7/24        | 3/7/24        | 3/7/24        | 3/1/24        | 3/1/24        | 3/1/24        | 3/14/24            | 3/14/24        | 3/14/24        | 3/7/24         | 3/7/24         | 3/7/24          | 3/1/24         | 3/1/24         | 3/1/24        |
|     3e-05  | nan              | nan              | nan            | nan            | nan            | nan            | nan            | nan              | nan            | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan                   | nan            | nan           | nan           | nan           | nan           | 0.02119359085 | 0.01637320149 | 0.02023077701 | nan                | nan            | nan            | nan            | nan            | nan             | nan            | nan            | nan           |
|     1e-05  | nan              | nan              | nan            | nan            | nan            | nan            | nan            | nan              | nan            | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan                   | nan            | nan           | nan           | nan           | nan           | 0.01441151359 | 0.01178053913 | 0.01439269509 | nan                | nan            | nan            | nan            | nan            | nan             | nan            | nan            | nan           |
|     3e-06  | nan              | nan              | nan            | nan            | nan            | nan            | nan            | nan              | nan            | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.01258935763         | 0.008555368902 | 0.01203682003 | 0.01711682945 | 0.01842259048 | 0.01570917792 | 0.01430966272 | 0.01178059389 | 0.01473860691 | nan                | nan            | nan            | nan            | nan            | nan             | nan            | nan            | nan           |
|     1e-06  | nan              | nan              | nan            | nan            | nan            | nan            | nan            | nan              | nan            | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.01676539395         | 0.01450527723  | 0.01475314373 | 0.01697721887 | 0.02129264848 | 0.01862289007 | 0.02154147357 | 0.01823194474 | 0.01811190366 | nan                | nan            | nan            | nan            | nan            | nan             | nan            | nan            | nan           |
|     3e-07  | nan              | nan              | nan            | nan            | nan            | nan            | nan            | nan              | nan            | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.01884159202         | 0.02390327732  | 0.02246163821 | 0.02293902704 | 0.02229114174 | 0.02524010685 | 0.02255137215 | 0.02234829541 | 0.02398801787 | nan                | nan            | nan            | nan            | nan            | nan             | nan            | nan            | nan           |
|     1e-07  | nan              | nan              | nan            | nan            | nan            | nan            | nan            | nan              | nan            | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.03919047338         | 0.03974712313  | 0.03754655226 | 0.0401703025  | 0.0419978675  | 0.03925382387 | 0.03850463243 | 0.04349016942 | 0.04302751414 | nan                | nan            | nan            | nan            | nan            | nan             | nan            | nan            | nan           |
|     3e-08  | nan              | nan              | nan            | nan            | nan            | nan            | nan            | nan              | nan            | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.06404988242         | 0.06324963523  | 0.06610901589 | 0.07057171844 | 0.07097637944 | 0.07825028342 | 0.06594699178 | 0.05787112409 | 0.06783697338 | nan                | nan            | nan            | nan            | nan            | nan             | nan            | nan            | nan           |
|     1e-08  | nan              | nan              | nan            | nan            | nan            | nan            | nan            | nan              | nan            | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.08578103809         | 0.09614613857  | 0.09169842672 | 0.09376560726 | 0.09570840738 | 0.09619016967 | nan           | nan           | nan           | nan                | nan            | nan            | nan            | nan            | nan             | nan            | nan            | nan           |
|     3e-09  | nan              | nan              | nan            | nan            | nan            | nan            | nan            | nan              | nan            | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.1102018222          | 0.1104853211   | 0.1149595649  | 0.121596881   | 0.1284429274  | 0.1290871563  | nan           | nan           | nan           | nan                | nan            | nan            | nan            | nan            | nan             | nan            | nan            | nan           |
|     1e-11  | nan              | nan              | nan            | nan            | nan            | nan            | nan            | nan              | nan            | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.1339420616          | 0.142010146    | 0.1354039776  | 0.164922789   | 0.150274487   | 0.1532477739  | 0.1366795391  | 0.1347867306  | 0.1406683575  | nan                | nan            | nan            | nan            | nan            | nan             | nan            | nan            | nan           |
|   nan      | nan              | nan              | nan            | nan            | nan            | nan            | nan            | nan              | nan            | nan                   | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan                   | nan            | nan           | nan           | nan           | nan           | nan           | nan           | nan           | nan                | nan            | nan            | nan            | nan            | nan             | nan            | nan            | nan           |
|     0.0001 | -0.0008491728718 | -0.002916211795  | 0.004534863263 | 0.005657592259 | 0.006805173487 | 0.009569019255 | 0.006066760546 | 0.004775600712   | 0.008797734246 | 0.1194109977          | 0.1290535929  | 0.1186961314  | 0.1376566982  | 0.1347141544  | 0.1281461876  | 0.1219813363  | 0.1252895321  | 0.1277766357  | nan                   | nan            | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.005117112663     | 0.003513865332 | 0.003596337517 | 0.008646407188 | 0.00607553643  | -0.005758271741 | 0.006064582203 | 0.007902507219 | 0.01439533803 |
|     1e-05  | -0.001442275816  | -0.002028703243  | 0.00271837475  | 0.004253376692 | 0.001735564995 | 0.007909710784 | 0.005487924334 | 0.006475036865   | 0.003647551894 | 0.110623542           | 0.1319055897  | 0.1250213764  | 0.1387346075  | 0.1362253884  | 0.1384659032  | 0.1202258355  | 0.137299355   | 0.1371003408  | nan                   | nan            | nan           | nan           | nan           | nan           | nan           | nan           | nan           | -0.003456312079    | 0.000189701874 | 0.001011319659 | 0.01006761242  | 0.007477599536 | 0.002618047979  | 0.01170104389  | 0.007518413311 | 0.00450336209 |
|     1e-06  | 0.0005555843281  | 0.001208992539   | 0.003317206151 | 0.003202422536 | 0.00412675862  | 0.006682852154 | 0.009523127057 | 0.008000100768   | 0.002571116114 | 0.1209763731          | 0.1292942381  | 0.1072243506  | 0.1419285588  | 0.1360628874  | 0.1368003684  | 0.1229967959  | 0.130138388   | 0.1419664623  | nan                   | nan            | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.00506454492      | 0.00793315351  | 0.00422180136  | 0.01702602353  | 0.01504633988  | 0.01482203694   | 0.01180296411  | 0.007536616478 | 0.00703143613 |
|     1e-07  | 4.935989406e-05  | 0.003433931786   | 0.003790273325 | 0.004130969783 | 0.005101740999 | 0.007289203324 | 0.001683107989 | 0.005019825825   | 0.007896421331 | 0.1193867196          | 0.1334084964  | 0.1191550893  | 0.1459409863  | 0.1476994092  | 0.1503471497  | 0.1258944284  | 0.1343706355  | 0.1443769899  | nan                   | nan            | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.03791972852      | 0.04079168104  | 0.03450512774  | 0.06369418531  | 0.06871179156  | 0.05303774676   | 0.04779704104  | 0.04753212101  | 0.0467325935  |
|     1e-08  | 0.005538850859   | 0.002471536629   | 0.002650488565 | 0.006677313831 | 0.001725929059 | 0.002207291763 | 0.005479181223 | -0.0007318698458 | 0.006334795286 | 0.1271592586          | 0.130858166   | 0.1190901839  | 0.1594274751  | 0.1507406696  | 0.14213415    | 0.1357566599  | 0.1275223469  | 0.1466622001  | nan                   | nan            | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.09154442282      | 0.09891574063  | 0.08628440817  | 0.1260692086   | 0.130782476    | 0.1347608151    | 0.09265232118  | 0.1014963201   | 0.09062408929 |
|     1e-09  | -0.0003906024442 | -0.0004475186928 | 0.003747866864 | 0.004609681469 | 0.003212843583 | 0.003670411808 | 0.004783154543 | 0.00653423483    | 0.00937675818  | 0.1274062354          | 0.1289364688  | 0.117809414   | 0.1469119685  | 0.1519432285  | 0.1389813501  | 0.1219528949  | 0.1331094678  | 0.140970965   | nan                   | nan            | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.1250668633       | 0.124412028    | 0.1200810717   | 0.1543541666   | 0.1529669176   | 0.1553174092    | 0.1281802597   | 0.1341751209   | 0.1321626147  |
|     1e-10  | 0.004663376404   | 0.0005647715365  | 0.00413657252  | 0.00709891683  | 0.003547132068 | 0.007392767441 | 0.008023464263 | 0.009009385732   | 0.008876937098 | 0.1344241305          | 0.1212174842  | 0.1246452375  | 0.1554283227  | 0.1528233262  | 0.1561819885  | 0.1375558299  | 0.1283940289  | 0.1361611229  | nan                   | nan            | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.13045903         | 0.136543986    | 0.1198942379   | 0.1589774976   | 0.1540357661   | 0.159839411     | 0.1341358605   | 0.1392689925   | 0.1310805223  |
|     1e-11  | 0.001260041302   | -0.0002385359186 | 0.007615982429 | 0.002744478456 | 0.002542230378 | 0.003701522731 | 0.001747509092 | 0.005329244761   | 0.003710548973 | 0.1338466487          | 0.1282491367  | 0.1211210533  | 0.1555945808  | 0.1548069977  | 0.1558006298  | 0.1351060829  | 0.1271116659  | 0.1471016088  | nan                   | nan            | nan           | nan           | nan           | nan           | nan           | nan           | nan           | 0.1351631158       | 0.1521128497   | 0.1266063381   | 0.1686627795   | 0.1662551277   | 0.1596970272    | 0.1247043877   | 0.1398863204   | 0.1416737646  |
"""

def sigmoid(x, Top, Bottom, LogIC50, HillSlope):
    return Bottom + (Top - Bottom) / (1 + 10**((LogIC50 - x) * HillSlope))

def main():
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"

    # 1. Load Data
    # Skip row 1 (dates) which is index 1 in 0-based indexing after header
    df = pd.read_csv(io.StringIO(DATA_CSV), sep="|", header=0, skiprows=[2])
    
    # Clean column names
    df.columns = [c.strip() for c in df.columns]
    
    # Remove empty columns from markdown parsing
    df = df.loc[:, ~df.columns.str.contains('^Unnamed: 0$')]
    df = df.dropna(axis=1, how='all')

    # 2. Data Cleaning & Aggregation
    # The 'Compound' column contains the concentration.
    # Clean asterisks if any and convert to numeric
    df['Compound'] = df['Compound'].astype(str).str.replace('*', '', regex=False)
    df['Compound'] = pd.to_numeric(df['Compound'], errors='coerce')
    df = df.dropna(subset=['Compound'])

    # Define column groups based on the table structure
    # Note: The first column is 'Compound'.
    # Vehicle: Columns 1 to 9
    # Vehicle + 100 nM NT: Columns 10 to 18
    # SBI-553 + 100 nM NT: Columns 19 to 27
    # SR14 + 100 nM NT: Columns 28 to 36
    
    # Get column names by index to be safe
    cols = df.columns
    vehicle_cols = cols[1:10]
    vehicle_nt_cols = cols[10:19]
    sbi_cols = cols[19:28]
    sr14_cols = cols[28:37]

    # Helper to process a group
    def process_group(columns):
        # Melt to long format: Compound, Value
        sub = df[['Compound'] + list(columns)]
        sub = sub.melt(id_vars='Compound', value_vars=columns, value_name='Value')
        
        # Clean values (remove asterisks, convert to float)
        sub['Value'] = sub['Value'].astype(str).str.replace('*', '', regex=False)
        sub['Value'] = pd.to_numeric(sub['Value'], errors='coerce')
        sub = sub.dropna(subset=['Value'])
        
        # Group by Compound and calculate Mean, SEM
        grouped = sub.groupby('Compound')['Value'].agg(['mean', 'sem', 'count']).reset_index()
        grouped['LogConc'] = np.log10(grouped['Compound'])
        return grouped.sort_values('LogConc')

    df_vehicle = process_group(vehicle_cols)
    df_vehicle_nt = process_group(vehicle_nt_cols)
    df_sbi = process_group(sbi_cols)
    df_sr14 = process_group(sr14_cols)

    # 3. Plotting
    fig, ax = plt.subplots(figsize=(5, 4))

    # Colors
    color_vehicle = '#808080'  # Grey
    color_vehicle_nt = '#0000CD' # MediumBlue
    color_sbi = '#B030B0'      # Purple/Magenta
    color_sr14 = '#FF8C00'     # DarkOrange

    # Plot Vehicle (Grey) - Flat line
    ax.errorbar(df_vehicle['LogConc'], df_vehicle['mean'], yerr=df_vehicle['sem'], 
                fmt='o', color=color_vehicle, capsize=0, markersize=8, label='Vehicle')
    # Plot mean line for Vehicle
    mean_vehicle = df_vehicle['mean'].mean()
    ax.axhline(mean_vehicle, color=color_vehicle, linestyle='-', linewidth=2, zorder=1)

    # Plot Vehicle + NT (Blue) - Flat line
    ax.errorbar(df_vehicle_nt['LogConc'], df_vehicle_nt['mean'], yerr=df_vehicle_nt['sem'], 
                fmt='o', color=color_vehicle_nt, capsize=0, markersize=8, label='Vehicle + 100 nM NT')
    # Plot mean line for Vehicle + NT
    mean_vehicle_nt = df_vehicle_nt['mean'].mean()
    ax.axhline(mean_vehicle_nt, color=color_vehicle_nt, linestyle='-', linewidth=2, zorder=1)

    # Fit and Plot SBI (Purple)
    if len(df_sbi) > 4:
        try:
            # Initial guess: Top=High, Bottom=Low, LogIC50=-8, Slope=1
            p0 = [df_sbi['mean'].max(), df_sbi['mean'].min(), -8, 1]
            popt, _ = curve_fit(sigmoid, df_sbi['LogConc'], df_sbi['mean'], p0=p0, maxfev=5000)
            
            x_fit = np.linspace(df_sbi['LogConc'].min(), df_sbi['LogConc'].max(), 100)
            y_fit = sigmoid(x_fit, *popt)
            ax.plot(x_fit, y_fit, color=color_sbi, linewidth=2, zorder=2)
        except:
            pass
    ax.errorbar(df_sbi['LogConc'], df_sbi['mean'], yerr=df_sbi['sem'], 
                fmt='o', color=color_sbi, capsize=0, markersize=8, label='SBI-553 + 100 nM NT')

    # Fit and Plot SR14 (Orange)
    if len(df_sr14) > 4:
        try:
            # Initial guess
            p0 = [df_sr14['mean'].max(), df_sr14['mean'].min(), -7, 1]
            popt, _ = curve_fit(sigmoid, df_sr14['LogConc'], df_sr14['mean'], p0=p0, maxfev=5000)
            
            x_fit = np.linspace(df_sr14['LogConc'].min(), df_sr14['LogConc'].max(), 100)
            y_fit = sigmoid(x_fit, *popt)
            ax.plot(x_fit, y_fit, color=color_sr14, linewidth=2, zorder=2)
        except:
            pass
    ax.errorbar(df_sr14['LogConc'], df_sr14['mean'], yerr=df_sr14['sem'], 
                fmt='o', color=color_sr14, capsize=0, markersize=8, label='SR14 + 100 nM NT')

    # 4. Formatting
    ax.set_ylabel('Mini G$_q$ recruitment\n($\Delta$ Net BRET)', fontsize=12)
    # ax.set_xlabel('Log[Compound] (M)', fontsize=12) # X-label not explicitly shown in crop, but ticks are
    
    # Axis limits and ticks
    ax.set_xlim(-12, -3.5)
    ax.set_xticks([-12, -10, -8, -6, -4])
    ax.set_ylim(-0.02, 0.20)
    ax.set_yticks([0.00, 0.05, 0.10, 0.15, 0.20])
    
    # Dotted zero line
    ax.axhline(0, color='black', linestyle=':', linewidth=1.5, zorder=0)

    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Tick parameters
    ax.tick_params(axis='both', which='major', labelsize=12, direction='in', length=6)

    # Title "a"
    ax.text(-0.15, 1.0, 'a', transform=ax.transAxes, fontsize=16, fontweight='bold', va='top', ha='right')

    # Save
    plt.tight_layout()
    plt.savefig(output_file, dpi=300)

if __name__ == "__main__":
    main()