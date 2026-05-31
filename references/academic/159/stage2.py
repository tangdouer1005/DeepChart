import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ------------------------------------------------------------
# Handle output filename from command line
# ------------------------------------------------------------
if len(sys.argv) > 1:
    out_file = sys.argv[1]
else:
    out_file = "output.png"

# ------------------------------------------------------------
# Embed source data
# ------------------------------------------------------------
csv_data = """million$,Unnamed: 1,central estimate of SAF cost,low SAF cost,high SAF cost
central estimate of CORSIA offset cost,2027,823,458.6,2499.9
nan,2028,535.3,153.5,2296.2
nan,2029,277,-153.8,2115.3
nan,2030,60.5,-449.5,1986.5
nan,2031,-114.2,-733.8,1910
nan,2032,-334.8,-1006.6,1804
nan,2033,-535.3,-1237.2,1693.9
nan,2034,-735.8,-1481.9,1626.2
nan,2035,-936.3,-1715.2,1571.3
nan,nan,nan,nan,nan
low estimate of CORSIA offset cost,2027,1299.5,935.1,2976.5
nan,2028,1118.4,736.7,2879.4
nan,2029,977.7,546.9,2816
nan,2030,889.7,379.6,2815.7
nan,2031,854.5,235,2878.7
nan,2032,784.7,112.9,2923.5
nan,2033,715.2,13.3,2944.4
nan,2034,682.4,-63.7,3044.4
nan,2035,660.8,-118.1,3168.4
nan,nan,nan,nan,nan
high estimate of CORSIA offset cost,2027,279.2,-85.2,1956.2
nan,2028,-131.6,-513.4,1629.3
nan,2029,-525.6,-956.5,1312.6
nan,2030,-890.6,-1400.7,1035.3
nan,2031,-1226.8,-1846.4,797.4
nan,2032,-1621.8,-2293.7,516.9
nan,2033,-1974.2,-2676.1,255
nan,2034,-2369,-3115.1,-7
nan,2035,-2776.6,-3555.5,-269
"""

df = pd.read_csv(io.StringIO(csv_data))

# Clean and split data into three blocks based on the descriptive label
df['label'] = df['million$'].replace('nan', pd.NA)
df['label'] = df['label'].ffill()

# Drop rows with NaN in year column
df = df.dropna(subset=['Unnamed: 1'])

# Rename columns for convenience
df = df.rename(columns={
    'Unnamed: 1': 'year',
    'central estimate of SAF cost': 'central',
    'low SAF cost': 'low',
    'high SAF cost': 'high'
})

# Create separate DataFrames
central_offset = df[df['label'] == 'central estimate of CORSIA offset cost'].copy()
low_offset = df[df['label'] == 'low estimate of CORSIA offset cost'].copy()
high_offset = df[df['label'] == 'high estimate of CORSIA offset cost'].copy()

# Convert year to numeric
for d in (central_offset, low_offset, high_offset):
    d['year'] = pd.to_numeric(d['year'])

# ------------------------------------------------------------
# Plot styling
# ------------------------------------------------------------
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False
})

fig, ax = plt.subplots(figsize=(6.5, 4.5))

# Colors approximating the figure
color_high = "#d8d228"    # yellow line (High offset price)
color_low = "#23446b"     # dark blue line (Low offset price)
color_med = "#e46b7a"     # pink line (Medium offset price)

fill_low = "#e1edf7"      # light blue band
fill_med = "#ead6e6"      # light purple/pink band
fill_high = "#f5e4b3"     # light yellow band

# ------------------------------------------------------------
# Plot shaded regions (low/high SAF cost around each offset estimate)
# ------------------------------------------------------------
# Low offset price band
ax.fill_between(low_offset['year'], low_offset['low'], low_offset['high'],
                color=fill_low, alpha=1.0, zorder=1)

# Medium offset price band (central)
ax.fill_between(central_offset['year'], central_offset['low'], central_offset['high'],
                color=fill_med, alpha=0.9, zorder=2)

# High offset price band
ax.fill_between(high_offset['year'], high_offset['low'], high_offset['high'],
                color=fill_high, alpha=0.9, zorder=1)

# ------------------------------------------------------------
# Plot central lines
# ------------------------------------------------------------
ax.plot(low_offset['year'], low_offset['central'], color=color_low, linewidth=2.2,
        label="Low offset price", zorder=3)
ax.plot(central_offset['year'], central_offset['central'], color=color_med, linewidth=2.2,
        label="Medium offset price", zorder=3)
ax.plot(high_offset['year'], high_offset['central'], color=color_high, linewidth=2.2,
        label="High offset price", zorder=3)

# Zero line
ax.axhline(0, color="#777777", linestyle=(0, (3, 3)), linewidth=1)

# ------------------------------------------------------------
# Axes, limits, ticks
# ------------------------------------------------------------
ax.set_xlim(2027, 2035)
ax.set_xticks(np.arange(2027, 2036, 1))

ax.set_ylim(-4000, 6000)
ax.set_yticks(np.arange(-4000, 7000, 1000))

ax.set_ylabel("Net costs of max usage of SAF (million US$)", fontsize=11)

# ------------------------------------------------------------
# Legend and text annotations
# ------------------------------------------------------------
ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0.02, 0.08), fontsize=9)

# Scenario label
ax.text(2027.2, -2300, "US-S2", fontsize=11)

# Right-side billion labels (approximations from figure)
ax.text(2035.1, low_offset['central'].iloc[-1] + 150, "8.0 B",
        color=color_low, fontsize=10, ha="left")
ax.text(2035.1, central_offset['central'].iloc[-1] - 150, "-1.0 B",
        color=color_med, fontsize=10, ha="left")
ax.text(2035.1, high_offset['central'].iloc[-1] - 150, "-11.2 B",
        color=color_high, fontsize=10, ha="left")

# Panel letter
ax.text(0.0, 1.02, "c", transform=ax.transAxes, fontsize=14, fontweight="bold")

# Tight layout and save
plt.tight_layout()
fig.savefig(out_file, dpi=300, bbox_inches="tight")