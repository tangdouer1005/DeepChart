import sys
import math
import io

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge

# ------------------------------------------------------------
# Handle command-line argument
# ------------------------------------------------------------
if len(sys.argv) > 1:
    out_file = sys.argv[1]
else:
    out_file = "output.png"

# ------------------------------------------------------------
# Embed source data (2012) as CSV text
# ------------------------------------------------------------
csv_data = """UF,Total,Domestic,China,EU,Other_countries,Biome
RO,104544,35817.7,0,57250,11407.5,AMAZÔNIA
AC,0,0,0,0,0,AMAZÔNIA
AM,220,220,0,0,0,AMAZÔNIA
RR,5000,4980.36,0,0,19.6429,AMAZÔNIA
PA,114236,13023.4,21351.7,56283.6,15902,AMAZÔNIA
AP,0,0,0,0,0,AMAZÔNIA
TO,1200,0,159.104,1040.9,0,AMAZÔNIA
MA,230,0,108.028,35.2987,49.0519,AMAZÔNIA
MT,2119394,291382,657731,248767,227804,AMAZÔNIA
RO,41600,0,0,36303.1,5296.85,CERRADO
PA,5450,0,2113.03,1936.16,1307.19,CERRADO
TO,417263,20300,90331.5,194297,77197,CERRADO
MA,555948,41510.9,138095,241907,112746,CERRADO
PI,444856,82862.4,38389,202655,42853.4,CERRADO
BA,1109707,226868,270394,382775,185891,CERRADO
MG,923495,147609,485775,155029,94509,CERRADO
SP,210101,18904.3,109001,22801.2,40341.7,CERRADO
PR,67710,0,67224.5,0,0,CERRADO
MS,1344063,414899,301225,321885,242245,CERRADO
MT,4861296,829534,1767640,1130350,817372,CERRADO
GO,2669474,1067810,907128,374156,257666,CERRADO
DF,55050,42799.7,8434.56,921.681,2874.59,CERRADO
PI,0,0,0,0,0,CAATINGA
CE,1145,0,0,925.012,219.968,CAATINGA
RN,0,0,0,0,0,CAATINGA
PB,0,0,0,0,0,CAATINGA
PE,0,0,0,0,0,CAATINGA
AL,0,0,0,0,0,CAATINGA
SE,0,0,0,0,0,CAATINGA
BA,2920,0,0,1952.15,134.126,CAATINGA
MG,356,0,0,63.8419,56.5327,CAATINGA
RN,0,0,0,0,0,MATA ATLÂNTICA
PB,0,0,0,0,0,MATA ATLÂNTICA
PE,0,0,0,0,0,MATA ATLÂNTICA
AL,0,0,0,0,0,MATA ATLÂNTICA
SE,0,0,0,0,0,MATA ATLÂNTICA
BA,0,0,0,0,0,MATA ATLÂNTICA
MG,104570,55294.7,35852.3,1252.17,3800.04,MATA ATLÂNTICA
ES,0,0,0,0,0,MATA ATLÂNTICA
RJ,0,0,0,0,0,MATA ATLÂNTICA
SP,352547,106095,175838,20391.3,14687.8,MATA ATLÂNTICA
PR,4389095,1514110,1478420,806281,472127,MATA ATLÂNTICA
SC,452349,152374,144839,61724.7,59489.9,MATA ATLÂNTICA
RS,1554512,763246,342919,255955,156319,MATA ATLÂNTICA
MS,470073,151631,209782,42153.7,49993,MATA ATLÂNTICA
GO,420,0,417.675,0,0,MATA ATLÂNTICA
RS,2714735,1034250,659237,539522,364054,PAMPA
MS,0,0,0,0,0,PANTANAL
MT,0,0,0,0,0,PANTANAL
"""

df = pd.read_csv(io.StringIO(csv_data))

# Drop rows with zero Total (no bar to show)
df = df[df["Total"] > 0].copy()

# ------------------------------------------------------------
# Parameters and helpers for circular stacked bars
# ------------------------------------------------------------
# Order biomes as in figure (approx.)
biome_order = ["AMAZÔNIA", "PANTANAL", "CERRADO", "CAATINGA", "PAMPA", "MATA ATLÂNTICA"]

# Color mapping for stacked components (Domestic, China, EU, Other)
colors = {
    "Domestic": "#f4a259",        # orange
    "China": "#4f6d7a",           # teal/blue
    "EU": "#a4c5c6",              # light blue
    "Other_countries": "#e07a5f"  # reddish
}

stack_cols = ["Domestic", "China", "EU", "Other_countries"]

# Normalize heights to millions of hectares for easier scaling
scale = 1e6
df["Total_million"] = df["Total"] / scale
for c in stack_cols:
    df[c + "_million"] = df[c] / scale

# Assign angle positions
# Biome blocks separated by gaps; each state within biome gets equal slice
biome_width = 50  # degrees allocated to each biome block (Increased to use more circle)
gap_width = 8     # gap between biome blocks

angles = []
labels = []
biomes_for_tick = []
current_angle = 0

records = []
for biome in biome_order:
    sub = df[df["Biome"] == biome].copy()
    if sub.empty:
        continue
    n_states = len(sub)
    state_width = biome_width / n_states
    start_block = current_angle
    for i, row in sub.reset_index(drop=True).iterrows():
        angle = start_block + i * state_width + state_width / 2.0
        records.append((angle, row))
    # center biome label
    biome_center = start_block + biome_width / 2.0
    biomes_for_tick.append((biome_center, biome))
    current_angle += biome_width + gap_width

# ------------------------------------------------------------
# Create figure / polar axes
# ------------------------------------------------------------
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.edgecolor": "none"
})

fig = plt.figure(figsize=(10, 10), dpi=300) # Increased figure size
ax = plt.subplot(111, polar=True)
ax.set_theta_direction(-1)            # clockwise
ax.set_theta_zero_location("E")       # zero at east (to mimic original)

# Background style
ax.set_facecolor("#f8f8f8")
fig.patch.set_facecolor("white")

# Radius limits
inner_radius = 2.0 # Increased inner radius for better label spacing
max_height = max(df["Total_million"]) if len(df) else 1
outer_radius = inner_radius + max_height * 1.2
ax.set_rlim(0, outer_radius + 1.0) # Increased limit for outer labels

# Remove default grid and ticks
ax.set_axis_off()

# ------------------------------------------------------------
# Draw stacked bar wedges
# ------------------------------------------------------------
bar_width_rad = math.radians(biome_width / max(df["Biome"].value_counts().max(), 1))

for angle_deg, row in records:
    theta = math.radians(angle_deg)

    # heights in millions
    heights = [row[c + "_million"] for c in stack_cols]
    r_base = inner_radius

    for h, col_name in zip(heights, stack_cols):
        if h <= 0:
            continue
        r_top = r_base + h
        # Recalculate width for each wedge based on state count in its biome
        # Find the biome for this row to get correct width
        this_biome = row["Biome"]
        n_states_in_biome = len(df[df["Biome"] == this_biome])
        width_deg = biome_width / n_states_in_biome
        
        # Draw wedge
        wedge = Wedge(
            (0, 0),
            r_top,
            angle_deg - width_deg / 2.0 + 0.5, # Add small padding
            angle_deg + width_deg / 2.0 - 0.5,
            width=h,
            transform=ax.transData._b,  # use polar transform
            facecolor=colors[col_name],
            edgecolor="none"
        )
        ax.add_patch(wedge)
        r_base = r_top

    # state label
    label_radius = inner_radius - 0.2
    ax.text(
        theta,
        label_radius,
        row["UF"],
        ha="center",
        va="center",
        fontsize=8, # Slightly larger font
        rotation=angle_deg - 90,
        rotation_mode="anchor",
        color="#333333"
    )

# ------------------------------------------------------------
# Biome labels on outer circle
# ------------------------------------------------------------
for angle_deg, biome in biomes_for_tick:
    theta = math.radians(angle_deg)
    # Place label outside the max data range
    label_r = outer_radius + 0.2
    ax.text(
        theta,
        label_r,
        biome.replace("AMAZÔNIA", "Amazônia"),
        ha="center",
        va="center",
        fontsize=10, # Larger font for groups
        fontweight='bold',
        rotation=angle_deg - 90, # Keep rotation or set to 0? 
                                 # Usually easier to read if rotated along the circle or horizontal
                                 # Let's keep rotation aligned with radius but readable
        rotation_mode="anchor",
        color="#222222"
    )

# ------------------------------------------------------------
# Manual radial grid rings and labels (0, 1.5, 3, 4.5 million ha approx.)
# ------------------------------------------------------------
ring_values = [0, 1.5, 3, 4.5]
for rv in ring_values:
    r = inner_radius + rv
    circle = plt.Circle((0, 0), r, transform=ax.transData._b,
                        fill=False, color="#dcdcdc",
                        ls=(0, (3, 6)), lw=0.5, zorder=0)
    ax.add_artist(circle)
    if rv > 0:
        ax.text(
            math.radians(90),
            r,
            f"{rv:g}",
            ha="center",
            va="center",
            fontsize=7,
            color="#999999"
        )

# ------------------------------------------------------------
# Title
# ------------------------------------------------------------
fig.text(0.08, 0.86, "2012", fontsize=16, fontweight="normal", ha="left", va="center")

# ------------------------------------------------------------
# Legend for export destinations
# ------------------------------------------------------------
legend_handles = [
    plt.Line2D([0], [0], color=colors["Domestic"], lw=4),
    plt.Line2D([0], [0], color=colors["China"], lw=4),
    plt.Line2D([0], [0], color=colors["EU"], lw=4),
    plt.Line2D([0], [0], color=colors["Other_countries"], lw=4),
]
fig.legend(
    legend_handles,
    ["Domestic", "China", "EU", "Other"],
    loc="lower center",
    bbox_to_anchor=(0.5, 0.05),
    ncol=4,
    fontsize=7,
    frameon=False
)

# ------------------------------------------------------------
# Save figure (no plt.show())
# ------------------------------------------------------------
plt.savefig(out_file, dpi=300, bbox_inches="tight")