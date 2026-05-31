import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import numpy as np

def get_data():
    """
    Returns the dataframe parsed from the provided source data.
    Note: Based on the visual evidence in the chart (ranges and outliers),
    Column 1 corresponds to the X-axis (Gclc) and Column 2 to the Y-axis (Fsp1),
    despite the markdown headers suggesting the reverse or being ambiguous.
    """
    csv_data = """
| ED Fig. 1r            | Unnamed: 1             |
|:----------------------|:-----------------------|
| 2log[Fsp1] expression | 2Log [Gclc] expression |
| 5.614709844           | 8.694183743            |
| 5.722466024           | 8.129283017            |
| 5.730639956           | 8.233140296            |
| 5.902073579           | 8.784634846            |
| 5.902073579           | 8.479780264            |
| 6.38024459            | 8.647458426            |
| 5.916476644           | 8.653919873            |
| 5.746850183           | 8.508190931            |
| 7.483009577           | 7.40599236             |
| 7.721099189           | 6.798309782            |
| 7.654636029           | 7.207502459            |
| 5.951867504           | 7.594697827            |
| 7.997179481           | 7.296457407            |
| 7.24697806            | 7.314696526            |
| 6.437960088           | 7.76420813             |
| 6.343407822           | 7.665335917            |
| 6.563768278           | 8.41869595             |
| 7.663913842           | 8.163901214            |
| 5.956521363           | 8.822411496            |
| 6.037821465           | 9.109047078            |
| 6.074676686           | 9.191799501            |
| 6.920055055           | 10.00982862            |
| 6.223036338           | 8.671010241            |
| 5.902073579           | 7.957682486            |
| 5.145677455           | 7.975561406            |
| 5.669593751           | 8.685449638            |
| 5.189824559           | 7.947198584            |
| 5.786596362           | 8.484218708            |
| 5.666756592           | 7.854245054            |
| 5.569855608           | 8.236014192            |
| 5.560714954           | 8.158862106            |
| 5.652486495           | 7.64096791             |
| 5.523561956           | 7.217230716            |
| 5.842978832           | 7.993221467            |
| 7.147713722           | 7.005624549            |
| 6.263034406           | 7.64385619             |
| 6.875288598           | 7.529040056            |
| 7.054197294           | 7.499845887            |
| 6.770829046           | 6.50779464             |
| 6.388878339           | 6.680886921            |
| 7.306517445           | 7.435461914            |
| 6.404290064           | 7.894817763            |
| 7.203592714           | 7.161887682            |
| 5.925999419           | 7.610286657            |
| 6.137503524           | 7.991521846            |
| 5.997744026           | 7.351380981            |
| 6.055282436           | 7.698357406            |
| 6.002252452           | 6.175923742            |
| 5.794415866           | 7.40599236             |
| 6.307428525           | 8.400879436            |
| 6.493455201           | 8.404290064            |
| 5.465974465           | 8.294620749            |
| 5.575917361           | 8.303780748            |
| 5.375039431           | 8.102238194            |
| 5.510961919           | 8.167418146            |
| 6.171927354           | 8.332707934            |
| 4.892391026           | 7.902073579            |
| 5.593951284           | 7.250772132            |
| 6.62058641            | 6.849248703            |
| 5.224966365           | 6.803485376            |
| 7.438791853           | 6.770829046            |
| 6                     | 7.766197597            |
| 6.963474124           | 7.585713709            |
| 7.184875343           | 8.20994068             |
| 7.516487981           | 6.996614715            |
| 5.773468928           | 8.518849829            |
| 6.298291731           | 7.963474124            |
| 6.400879436           | 7.642412773            |
| 7.5360529             | 7.780047576            |
| 7.330020516           | 8.461479447            |
| 6.563768278           | 7.526694846            |
| 7.053111336           | 8.005624549            |
| 6.246027981           | 7.215290306            |
| 6.783980414           | 7.807998839            |
| 6.366322214           | 7.827183896            |
| 6.729280846           | 8.745170091            |
| 6.860466259           | 8.962317655            |
| 6.73470962            | 7.754887502            |
| 7.107478647           | 7.728600811            |
| 7.031218731           | 8.733354341            |
| 6.059614856           | 7.432959407            |
| 8.232181058           | 7.896635141            |
| 5.741466986           | 8.118422024            |
| 5.491853096           | 8.332707934            |
| 8.034523875           | 8.677719642            |
| 5.539158811           | 6.758889433            |
| 7.945443836           | 5.708739041            |
    """
    # Read markdown table, skipping the first two header rows to handle data manually
    # Using regex separator to handle markdown pipes
    df = pd.read_csv(io.StringIO(csv_data), sep=r'\s*\|\s*', engine='python', skiprows=4, header=None)
    
    # Clean up: Drop the first and last columns which are likely NaN due to leading/trailing pipes
    df = df.dropna(axis=1, how='all')
    
    # Assign columns based on visual analysis of the chart:
    # Column 1 (index 1 in raw) -> X-axis (Gclc)
    # Column 2 (index 2 in raw) -> Y-axis (Fsp1)
    df.columns = ['Gclc', 'Fsp1']
    
    return df

def create_chart(output_filename):
    # Load data
    df = get_data()
    
    # Set up the plot style
    sns.set_style("ticks")
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
    
    # Create figure
    fig, ax = plt.subplots(figsize=(5, 4.5))
    
    # Calculate statistics for annotation
    r_value, p_value = stats.pearsonr(df['Gclc'], df['Fsp1'])
    
    # Plot Scatter and Regression Line
    # Scatter: Blueish purple, semi-transparent
    # Line: Red, solid, no confidence interval shading (ci=None)
    sns.regplot(
        data=df, 
        x='Gclc', 
        y='Fsp1', 
        ax=ax,
        color='#7385E0', # Matches the blue/purple scatter color
        scatter_kws={'s': 50, 'alpha': 0.8, 'edgecolor': 'none'},
        line_kws={'color': '#E34A33', 'linewidth': 2.5}, # Matches the red fit line
        ci=None
    )
    
    # Axis Labels
    ax.set_xlabel("Log2 Gclc expression", fontsize=14, fontweight='bold', color='black')
    ax.set_ylabel("Log2 Fsp1 (AIFM2) expression", fontsize=14, fontweight='bold', color='black')
    
    # Axis Ticks
    ax.set_xticks(range(4, 10))
    ax.set_yticks(range(5, 12))
    ax.tick_params(axis='both', which='major', labelsize=12, width=1.5, length=5, colors='black')
    
    # Set Limits to match image
    ax.set_xlim(4, 9.2)
    ax.set_ylim(5, 11)
    
    # Title
    ax.set_title("Tumor Melanoma (Metastatic)", fontsize=14, fontweight='bold', pad=15)
    
    # Statistical Annotation (Top Left inside plot)
    stats_text = f"r-value={r_value:.3f}\nP={p_value:.3f}"
    ax.text(0.05, 0.95, stats_text, transform=ax.transAxes, 
            fontsize=12, fontweight='bold', verticalalignment='top')
    
    # Figure Label "q" (Top Left outside plot)
    # We place this relative to the figure or axes. 
    # In the image, it's to the left of the Y-axis label.
    fig.text(0.02, 0.90, "q", fontsize=20, fontweight='bold')
    
    # Remove top and right spines
    sns.despine()
    
    # Make axis lines thicker/blacker
    for spine in ax.spines.values():
        spine.set_edgecolor('black')
        spine.set_linewidth(1.5)

    # Adjust layout
    plt.tight_layout()
    
    # Save
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    create_chart(output_file)