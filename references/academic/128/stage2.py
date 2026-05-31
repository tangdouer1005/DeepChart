import sys
import io
import json
import urllib.request
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Polygon, Patch
from matplotlib.collections import PatchCollection
import numpy as np

# -----------------------------------------------------------------------------
# 1. EMBEDDED SOURCE DATA (Figure 5b 2015 Data)
# -----------------------------------------------------------------------------
# Using the data provided in f5.md for "For pie charts in 2015" (Right side, Figure 5b)
# Also including the "Food system emission shares in 2015 to produce map of Figure5b"
DATA_CSV = """
Region,Landbased,Energy,Industry,Waste
Canada,263117.800559682,85853.56248650354,21392.628282042213,13121.601308323592
USA,578273.618626597,569021.7596366757,233941.3869466632,90267.06097166253
Mexico,123821.15739878573,56373.86529224699,3137.9970232539595,54280.48080223983
Central America,145744.8740588209,17116.907028649934,9499.749694817201,29794.832077837185
Brazil,1126107.602728838,84267.3379955557,5387.972591648913,111450.55145851424
South America,1040997.4442110347,99131.4978726647,4312.605045305646,68735.65860769653
North Africa,70503.20216485241,65476.070051200375,11529.255202664974,51164.24230102904
West Africa,882311.5311946706,39999.31738968485,788.4832677664941,91129.10233626203
East Africa,635059.4629609243,11976.521425874413,156.84352955049746,52448.82238713576
South Africa,1140436.9010001156,47069.926263619134,2702.4905559815734,48543.00653076366
OECD Europe,456173.45157901844,335696.0767792153,110149.28064615338,83049.50981214276
Central Europe,136674.0599739677,90707.67183729023,33126.461952266465,27606.399442276404
Turkey,61196.42596266215,42494.01501356687,6051.403500421071,12212.7886486763
Ukraine,99204.42544616526,25684.05947557344,8706.804804933736,11075.61966941027
Central Asia,101864.54712701317,44231.65837906641,4866.0907748485115,13331.451515006916
Russia,227540.82677725152,146476.22004911758,50973.59154664338,68754.85195559333
Middle East,70838.38421722686,220067.09499011116,23742.69464034251,76231.7670298695
India,1105713.4637834476,293459.2094615187,21504.578097133537,238476.2333420156
Korea,46890.756661472944,51958.9920244375,3986.427111623156,17530.598127401183
China,973057.8218986995,1106530.6621784645,87783.3569152072,339679.54870286403
South-East Asia,652160.9375746754,130398.84302099035,6100.4057979545905,86187.62981422983
Indonesia,1572711.6393244064,57578.50078771228,8553.456192912474,55399.18961279844
Japan,61923.86691767493,102355.57710518816,38039.7251730613,7346.704714077717
Oceania,171113.60362442656,58416.0425204705,14483.316454119653,14530.63545059957
"""

MAP_DATA_CSV = """
country,2015
ABW,0.136907995
AFG,0.636150027
AGO,0.681969076
AIA,0.194691823
ALB,0.602264048
ANT,0.119156176
ARE,0.092731596
ARG,0.665247582
ARM,0.419117828
ASM,1.085516055
ATG,0.194452679
AUS,0.329642484
AUT,0.263883801
AZE,0.373172038
BDI,1.070346831
BEL,0.245436882
BEN,0.695778762
BFA,0.948279029
BGD,0.682723904
BGR,0.286651912
BHR,0.099380163
BHS,0.180673961
BIH,0.163467194
BLR,0.590678242
BLZ,1.075126965
BMU,0.157268808
BOL,0.83383841
BRA,0.806860921
BRB,0.132104271
BRN,0.161727196
BTN,-0.72196524
BWA,1.062830929
CAF,0.722541908
CAN,0.410520519
CHE,0.260295723
CHL,2.219958602
CHN,0.189477874
CIV,0.509962059
CMR,0.843695984
COD,0.894515046
COG,0.781699275
COK,0.278361519
COL,0.577497141
COM,0.67533201
CPV,0.304209156
CRI,6.660951783
CUB,0.528785065
CYM,0.144044273
CYP,0.297466947
CZE,0.202829483
DEU,0.204702009
DJI,0.52139949
DMA,0.519870553
DNK,0.425155457
DOM,0.550162344
DZA,0.213234612
ECU,0.538207707
EGY,0.236940064
ERI,0.923839426
ESH,0.688832754
ESP,0.309429918
EST,0.267294924
ETH,0.785545733
FIN,0.329384654
FJI,-5.569367416
FLK,0.920616161
FRA,0.458953629
FRO,0.823878171
FSM,7.789822496
GAB,-0.043818772
GBR,0.23070905
GEO,0.384516007
GHA,0.295187052
GIB,0.10558965
GIN,0.895551183
GLP,0.214194563
GMB,0.808024607
GNB,0.874934181
GNQ,0.453280799
GRC,0.24354323
GRD,0.223956265
GRL,0.316180219
GTM,0.701459107
GUF,0.118970887
GUM,0.78539815
GUY,0.990927325
HKG,0.141646085
HND,0.782960882
HRV,0.38190594
HTI,0.476694059
HUN,0.342904794
IDN,0.560448047
IND,0.325065034
IRL,0.475657238
IRN,0.159698627
IRQ,0.148964417
ISL,0.402991806
ISR,0.18884053
ITA,0.250347107
JAM,0.228854926
JOR,0.249355814
JPN,0.155258028
KAZ,0.144793338
KEN,1.042161749
KGZ,0.458429155
KHM,0.805327295
KIR,0.535740247
KNA,0.215469006
KOR,0.135107143
KWT,0.131235236
LAO,0.4932181
LBN,0.193544884
LBR,2.193354501
LBY,0.138595714
LCA,0.295992443
LKA,0.452839831
LSO,0.650493874
LTU,0.7816423
LUX,0.186054096
LVA,-23.02854328
MAC,0.154444903
MAR,0.461283005
MDA,0.336451318
MDG,0.794373455
MDV,0.165231544
MEX,0.300546968
MHL,0.985555645
MKD,0.234598063
MLI,0.952687965
MLT,0.236532694
MMR,0.997303467
MNG,0.666690833
MNP,0.993815178
MOZ,0.727291149
MRT,0.901515904
MSR,0.373059134
MTQ,0.153001187
MUS,0.193959095
MWI,0.927865182
MYS,0.652691494
MYT,1.021290689
NAM,0.830104307
NCL,0.089775553
NER,0.90904682
NGA,0.613977519
NIC,0.886143182
NIU,0.99982595
NLD,0.273956566
NOR,0.352888969
NPL,0.800758141
NRU,0.637519403
NZL,0.835256383
OMN,0.119681019
PAK,0.59695735
PAN,0.581322438
PER,0.729963787
PHL,0.609081102
PLW,0.114981255
PNG,0.961809827
POL,0.270532949
PRI,0.750723322
PRK,0.449847069
PRT,0.30876454
PRY,1.004980983
PYF,0.263350262
QAT,0.122309643
REU,0.167702813
ROU,-0.660258315
RUS,0.217661675
RWA,1.064299753
SAU,0.098012142
SCG,0.275141305
SDN,1.032242732
SEN,0.81974287
SGP,0.099656043
SHN,0.157255292
SLB,0.805886222
SLE,0.491108151
SLV,0.486177119
SOM,0.978644821
SPM,0.182974137
STP,0.274571256
SUR,0.78788923
SVK,0.260896365
SVN,0.369011232
SWE,0.891768099
SWZ,0.610946847
SYC,0.119583445
SYR,0.333870233
TCA,0.143430569
TCD,0.956676846
TGO,0.702762509
THA,0.367119545
TJK,0.619843342
TKL,0.99945123
TKM,0.215551681
TLS,0.680724054
TON,0.508734094
TTO,0.238169281
TUN,0.3158462
TUR,0.269736977
TUV,0.935601034
TWN,0.103077825
TZA,0.935612588
UGA,0.829193117
UKR,0.26793164
URY,1.073764057
USA,0.229300425
UZB,0.390859301
VCT,0.280026521
VEN,0.481147557
VGB,0.170398609
VIR,-4.292622358
VNM,0.496878937
VUT,0.876604073
WLF,0.858455392
WSM,0.669900369
YEM,0.444756592
ZAF,0.166054356
ZMB,1.043112474
ZWE,0.780384593
"""

# -----------------------------------------------------------------------------
# 2. DATA PROCESSING
# -----------------------------------------------------------------------------

def get_data():
    # Read the Pie Chart Data
    df_pie = pd.read_csv(io.StringIO(DATA_CSV))
    df_pie = df_pie.dropna(subset=['Region'])
    
    cols = ["Landbased", "Energy", "Industry", "Waste"]
    for c in cols:
        df_pie[c] = pd.to_numeric(df_pie[c])
        
    df_pie['Total'] = df_pie[cols].sum(axis=1)
    for c in cols:
        df_pie[c + '_pct'] = (df_pie[c] / df_pie['Total']) * 100

    # Read the Map Data
    df_map = pd.read_csv(io.StringIO(MAP_DATA_CSV))
    df_map.columns = ["iso_a3", "share"]
    df_map['share'] = pd.to_numeric(df_map['share'])
    
    return df_pie, df_map

def get_world_geojson():
    # URL for a lightweight world geojson
    url = "https://raw.githubusercontent.com/python-visualization/folium/main/examples/data/world-countries.json"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
        return data
    except Exception as e:
        print(f"Warning: Could not download map data: {e}")
        return None

# -----------------------------------------------------------------------------
# 3. PLOTTING
# -----------------------------------------------------------------------------

def plot_chart(output_filename="output.png"):
    df_pie, df_map = get_data()
    
    # --- Setup Colors ---
    # Pie Colors (using same colors as 127 for consistency)
    c_land = '#5f804d'  # Green
    c_energy = '#c48257' # Brown/Orange
    c_industry = '#949698' # Grey
    c_waste = '#e8d67d' # Yellow
    pie_colors = [c_land, c_energy, c_industry, c_waste]
    
    # Map Colors (Discrete Bins)
    bounds = [-10, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 100]
    map_colors_hex = [
        '#c68642', # <10%
        '#e8d278', # 10-15
        '#fcf4c5', # 15-20
        '#a8d6e2', # 20-30
        '#8abf68', # 30-40
        '#5f9e56', # 40-50
        '#3b6e38'  # >50%
    ]
    cmap = mcolors.ListedColormap(map_colors_hex)
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    
    # Create a dict for fast lookup: iso_a3 -> value
    map_data_dict = dict(zip(df_map['iso_a3'], df_map['share']))

    # --- Figure Layout ---
    fig = plt.figure(figsize=(18, 12), facecolor='white')
    
    # 1. Draw Map (Center)
    ax_map = fig.add_axes([0.20, 0.25, 0.60, 0.50])
    ax_map.set_aspect('equal')
    ax_map.axis('off')
    
    geo_data = get_world_geojson()
    
    if geo_data:
        patches = []
        facecolors = []
        
        for feature in geo_data['features']:
            iso_code = feature['id']
            if iso_code == 'ATA': # Skip Antarctica
                continue
                
            val = map_data_dict.get(iso_code, None)
            if val is not None:
                c = cmap(norm(val))
            else:
                c = '#f0f0f0' # Default grey
            
            geom_type = feature['geometry']['type']
            coords = feature['geometry']['coordinates']
            
            if geom_type == 'Polygon':
                polys = [coords]
            elif geom_type == 'MultiPolygon':
                polys = coords
            else:
                continue
                
            for poly_coords in polys:
                exterior = poly_coords[0]
                polygon = Polygon(exterior, closed=True)
                patches.append(polygon)
                facecolors.append(c)
        
        p = PatchCollection(patches, facecolors=facecolors, edgecolor='black', linewidth=0.3)
        ax_map.add_collection(p)
        ax_map.set_xlim(-180, 180)
        ax_map.set_ylim(-60, 85)
    else:
        # Fallback if offline
        ax_map.text(0.5, 0.5, "Map Data Unavailable (Offline)", ha='center', va='center', fontsize=14)
        ax_map.set_xlim(0, 1)
        ax_map.set_ylim(0, 1)
    
    # 2. Add Map Legend
    legend_labels = ['<10%', '10–15%', '15–20%', '20–30%', '30–40%', '40–50%', '>50%']
    patches = [Patch(color=c, label=l) for c, l in zip(map_colors_hex, legend_labels)]
    
    leg = ax_map.legend(handles=patches, loc='lower left', 
                        bbox_to_anchor=(-0.1, 0.05), 
                        title="GHG shares\nfrom food system",
                        frameon=False, fontsize=10, title_fontsize=11)
    leg._legend_box.align = "left"
    ax_map.text(-0.05, 0.0, "2015", transform=ax_map.transAxes, fontsize=11, ha='left')

    # 3. Add Pie Legend
    pie_patches = [
        Patch(color=c_land, label='Land based'),
        Patch(color=c_energy, label='Energy'),
        Patch(color=c_industry, label='Industry'),
        Patch(color=c_waste, label='Waste')
    ]
    fig.legend(handles=pie_patches, loc='lower right', bbox_to_anchor=(0.8, 0.22), 
               ncol=4, frameon=False, fontsize=11, handlelength=1.0, handleheight=1.0)

    # --- Plot Pie Charts ---
    name_map = {
        "Canada": "Canada", "OECD Europe": "OECD Europe", "Central Europe": "Central Europe",
        "Russia": "Russia", "Ukraine": "Ukraine", "Central Asia": "Central Asia",
        "Middle East": "Middle East", "Turkey": "Turkey", "China": "China",
        "USA": "United States", "Mexico": "Mexico", "Central America": "Central America",
        "Brazil": "Brazil", "South America": "South America", "South Africa": "South Africa",
        "West Africa": "West Africa", "East Africa": "East Africa", "North Africa": "North Africa",
        "India": "India", "Oceania": "Oceania", "Japan": "Japan",
        "Indonesia": "Indonesia", "South-East Asia": "Southeast Asia", "Korea": "Korea"
    }
    
    top_row = ["Canada", "OECD Europe", "Central Europe", "Russia", "Ukraine", "Central Asia", "Middle East", "Turkey", "China"]
    right_col = ["Indonesia", "South-East Asia", "Korea"]
    bottom_row = ["Japan", "Oceania", "India", "North Africa", "East Africa", "West Africa", "South Africa", "South America", "Brazil"]
    left_col = ["Central America", "Mexico", "USA"]
    
    def add_pie(region_key, x, y, size=0.08):
        row = df_pie[df_pie['Region'] == region_key]
        if row.empty:
            return
        
        vals = row.iloc[0][["Landbased", "Energy", "Industry", "Waste"]].values
        pcts = row.iloc[0][["Landbased_pct", "Energy_pct", "Industry_pct", "Waste_pct"]].values
        
        ax = fig.add_axes([x, y, size, size])
        wedges, texts = ax.pie(vals, colors=pie_colors, startangle=90, counterclock=False)
        
        for i, p in enumerate(pcts):
            if p >= 1.5:
                ang = (wedges[i].theta2 - wedges[i].theta1)/2. + wedges[i].theta1
                y_off = np.sin(np.deg2rad(ang))
                x_off = np.cos(np.deg2rad(ang))
                r = 0.7
                txt_color = 'white'
                ax.text(x_off*r, y_off*r, f"{int(round(p))}%", ha='center', va='center', 
                        color=txt_color, fontsize=9, fontweight='bold')
        
        display_name = name_map.get(region_key, region_key)
        ax.set_title(display_name, fontsize=11, pad=2)

    # Coordinates
    start_x, end_x = 0.05, 0.90
    y_top = 0.82
    x_step = (end_x - start_x) / (len(top_row) - 1)
    for i, region in enumerate(top_row):
        add_pie(region, start_x + i*x_step, y_top)

    start_x, end_x = 0.90, 0.05
    y_bot = 0.05
    x_step = (end_x - start_x) / (len(bottom_row) - 1)
    for i, region in enumerate(bottom_row):
        add_pie(region, start_x + i*x_step, y_bot)

    x_right = 0.88
    right_y_positions = [0.63, 0.45, 0.27]
    for i, region in enumerate(right_col):
        add_pie(region, x_right, right_y_positions[i])

    x_left = 0.05
    left_y_positions = [0.63, 0.45, 0.27]
    for i, region in enumerate(reversed(left_col)):
        add_pie(region, x_left, left_y_positions[i])

    fig.text(0.02, 0.95, 'b', fontsize=24, fontweight='bold')

    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    try:
        plot_chart(output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
