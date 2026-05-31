import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import numpy as np

def generate_chart(output_filename='output.png'):
    # 1. Load Data
    csv_data = """Station,PM_size,Site_type,N_samples,OP_AA_m_mean,OP_AA_m_SD,PM_mass_mean,PM_mass_SD
nan,nan,nan,nan,nmol min-1 µg-1,nmol min-1 µg-1,µg m-3,µg m-3
BERN,PM10,Traffic,738,0.2,0.04,19.42,10.22
BERN,PM2.5,Traffic,644,0.11,0.03,12.61,7.52
ZURICH,PM10,Urban,204,0.12,0.05,18.38,12.57
ZURICH,PM2.5,Urban,90,0.08,0.04,10.8,6.97
BCN,PM1,Urban,94,0.05,0.03,14.71,4.91
BCN,PM10,Urban,270,0.07,0.03,23.31,8.94
BCN,PM2.5,Urban,197,0.05,0.03,17.48,6.32
MRS-lcp,PM1,Urban,262,0.08,0.07,13.65,13.48
MRS-lcp,PM10,Urban,271,0.06,0.04,18.69,8.2
PARIS-lcpp,PM10,Urban,184,0.08,0.04,19.4,9.26
PARIS-lcpp,PM2.5,Urban,69,0.06,0.04,12.51,7.26
PARIS-lh,PM10,Urban,386,0.07,0.04,20.74,13.22
PARIS-lh,PM2.5,Urban,807,0.07,0.04,10.32,6.06
ATH,PM10,Urban,147,0.06,0.05,31.99,14.89
ATH,PM2.5,Urban,152,0.08,0.05,24.7,16.61
KRAK,PM1,Urban,63,0.04,0.02,19.73,17.28
KRAK,PM10,Urban,63,0.05,0.01,28.69,18.9
BASEL,PM10,Suburban,90,0.09,0.05,13.97,9.26
BASEL,PM2.5,Suburban,90,0.06,0.05,10.6,7.76
MGD,PM10,Rural,240,0.1,0.06,16.7,10.6
MGD,PM2.5,Rural,153,0.09,0.07,10.61,7.2
PAYRN,PM10,Rural,103,0.06,0.03,13.49,8.31
PAYRN,PM2.5,Rural,102,0.04,0.03,9.68,6.73
MSY,PM1,Rural,93,0.04,0.04,9.35,4.39
MSY,PM10,Rural,106,0.04,0.03,12.82,6.24
MSY,PM2.5,Rural,107,0.05,0.06,9.62,4.68
OPE,PM10,Rural,200,0.05,0.06,9.54,6.54
OPE,PM2.5,Rural,102,0.03,0.02,9,7.23"""

    # Read CSV, skipping the unit row (row index 1 in 0-based, or just filter after)
    df = pd.read_csv(io.StringIO(csv_data))
    
    # Remove the unit row (where Station is NaN)
    df = df.dropna(subset=['Station'])
    
    # Convert numeric columns
    numeric_cols = ['N_samples', 'OP_AA_m_mean', 'OP_AA_m_SD', 'PM_mass_mean', 'PM_mass_SD']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col])

    # 2. Setup Plotting Parameters
    
    # Define Colors (matching the image)
    colors = {
        'PM1': '#4e79a7',   # Blueish
        'PM2.5': '#d38d5f', # Orange/Brownish
        'PM10': '#6a9f58'   # Greenish
    }
    
    # Define Order
    site_type_order = ['Traffic', 'Urban', 'Suburban', 'Rural']
    site_type_labels = {'Traffic': 'T', 'Urban': 'U', 'Suburban': 'SU', 'Rural': 'R'}
    pm_order = ['PM1', 'PM2.5', 'PM10']
    
    # Create Figure and Dual Axes
    fig, ax1 = plt.subplots(figsize=(14, 5))
    ax2 = ax1.twinx()
    
    # Layout settings
    bar_width = 0.8
    group_gap = 0.5      # Gap between stations
    type_gap = 1.5       # Gap between site types
    current_x = 0
    
    # Store x-ticks and labels if needed (though image doesn't show bottom labels)
    # We need to track positions for vertical dividers
    type_boundaries = []
    type_centers = []
    
    # 3. Plotting Loop
    
    # Iterate through Site Types
    for i, site_type in enumerate(site_type_order):
        # Filter data for this site type
        site_data = df[df['Site_type'] == site_type]
        
        # Get unique stations in this site type, preserving order of appearance
        stations = site_data['Station'].unique()
        
        start_x_for_type = current_x
        
        for station in stations:
            station_data = site_data[site_data['Station'] == station]
            
            # Sort by PM size
            # Create a categorical type for sorting
            station_data = station_data.copy()
            station_data['PM_size'] = pd.Categorical(station_data['PM_size'], categories=pm_order, ordered=True)
            station_data = station_data.sort_values('PM_size')
            
            # Plot Bars and Scatters
            for _, row in station_data.iterrows():
                pm_size = row['PM_size']
                color = colors[pm_size]
                
                # Bar Plot (Left Axis)
                # Error bars: capsize=3, ecolor='gray'
                ax1.bar(current_x, row['OP_AA_m_mean'], 
                        width=bar_width, 
                        color=color, 
                        yerr=row['OP_AA_m_SD'], 
                        capsize=3, 
                        error_kw={'ecolor': 'gray', 'elinewidth': 1.5},
                        edgecolor='none',
                        zorder=2)
                
                # Scatter Plot (Right Axis)
                # Circle marker, facecolor matches bar, black edge
                ax2.scatter(current_x, row['PM_mass_mean'], 
                            s=80, 
                            facecolors=color, 
                            edgecolors='black', 
                            linewidth=1.2,
                            zorder=3)
                
                current_x += 1 # Move to next bar slot
            
            current_x += group_gap # Gap between stations
            
        # Calculate center for the Site Type Label
        end_x_for_type = current_x - group_gap # Remove last gap
        center_x = (start_x_for_type + end_x_for_type) / 2 - 0.5 # Adjust for 0-indexing width
        type_centers.append((center_x, site_type_labels[site_type]))
        
        # Record boundary for vertical line
        type_boundaries.append(current_x - (group_gap/2) + (type_gap/2) - 0.5) # Approximate midpoint
        
        current_x += type_gap # Gap between site types

    # 4. Styling and Formatting
    
    # Axis Limits
    ax1.set_ylim(0, 0.25)
    ax2.set_ylim(0, 50)
    
    # Axis Labels
    # Using LaTeX formatting for superscripts/subscripts
    ax1.set_ylabel(r'$OP^{AA}_m$ (nmolAA min$^{-1}$ $\mu$g$^{-1}$)', fontsize=12)
    ax2.set_ylabel(r'PM ($\mu$g m$^{-3}$)', fontsize=12)
    
    # Remove X-axis ticks and labels (as per image)
    ax1.set_xticks([])
    ax2.set_xticks([])
    
    # Add Grid (Horizontal dashed lines on primary axis)
    ax1.grid(axis='y', linestyle='--', linewidth=1, alpha=0.7, zorder=0)
    
    # Add Vertical Dividers
    # We plot lines between the types. The last boundary is not needed.
    for boundary in type_boundaries[:-1]:
        ax1.axvline(x=boundary, color='gray', linewidth=2, linestyle='-', zorder=1)
        
    # Add Site Type Labels (T, U, SU, R) at the top
    for center_x, label in type_centers:
        # Position slightly above the plot area
        ax1.text(center_x, 0.26, label, ha='center', va='bottom', fontsize=12, fontweight='bold', transform=ax1.transData)

    # Add "a)" label
    ax1.text(0.02, 0.92, 'a)', transform=ax1.transAxes, fontsize=14, fontweight='bold')

    # 5. Legend
    # Create custom legend handles
    legend_elements = [
        mpatches.Patch(color=colors['PM1'], label='PM1'),
        mpatches.Patch(color=colors['PM2.5'], label='PM2.5'),
        mpatches.Patch(color=colors['PM10'], label='PM10'),
        mlines.Line2D([], [], color='white', marker='o', markeredgecolor='black', 
                      markerfacecolor='white', markersize=8, label='PM mass\nconcentration', linewidth=0)
    ]
    
    # Add legend to the plot
    # Locating it roughly where it is in the image (upper right)
    ax1.legend(handles=legend_elements, loc='upper right', frameon=True, fontsize=11, borderpad=0.6)

    # Adjust layout to make room for top labels
    plt.subplots_adjust(top=0.85, bottom=0.1, left=0.08, right=0.92)
    
    # Save
    plt.savefig(output_filename, dpi=300)
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)