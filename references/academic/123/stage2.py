import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import sys

def main():
    # 1. Handle Output Filename
    output_file = sys.argv[1] if len(sys.argv) > 1 else 'output.png'

    # 2. Source Data
    # Mapped directly from the provided Markdown table.
    # Structure: Region -> Category -> List of (Subcategory, Value)
    # Order is critical for visual alignment (Clockwise: Energy, Industry, Waste, Landbased)
    # Inner Order is critical to match the visual slices.
    
    data = {
        "Globe": {
            "Energy": [
                ("Transport", 834432),
                ("Processing", 496434),
                ("Packaging", 956519),
                ("Retail", 313028),
                ("Consumption", 456845),
                ("Production", 729419)
            ],
            "Industry": [
                ("Packaging", 20982.2),
                ("Processing", 576.842),
                ("Production", 286377),
                ("Retail", 402981)
            ],
            "Waste": [
                ("End of Life", 1.61649e+06),
                ("Processing", 124474)
            ],
            "Land based": [
                ("Production", 6.04419e+06),
                ("LULUC", 5.66302e+06)
            ]
        },
        "Industrialized": {
            "Energy": [
                ("Transport", 481391),
                ("Processing", 225195),
                ("Packaging", 276552),
                ("Retail", 211656),
                ("Consumption", 127937),
                ("Production", 286551)
            ],
            "Industry": [
                ("Packaging", 10467.4),
                ("Processing", 235.675),
                ("Production", 128630),
                ("Retail", 385620)
            ],
            "Waste": [
                ("End of Life", 458636),
                ("Processing", 37152.5)
            ],
            "Land based": [
                ("Production", 1.62167e+06),
                ("LULUC", 681299)
            ]
        },
        "Developing": {
            "Energy": [
                ("Transport", 353041),
                ("Processing", 271239),
                ("Packaging", 679967),
                ("Retail", 101372),
                ("Consumption", 328908),
                ("Production", 442868)
            ],
            "Industry": [
                ("Packaging", 10514.8),
                ("Processing", 341.167),
                ("Production", 157747),
                ("Retail", 17360.2)
            ],
            "Waste": [
                ("End of Life", 1.15785e+06),
                ("Processing", 87321.7)
            ],
            "Land based": [
                ("Production", 4.42252e+06),
                ("LULUC", 4.98172e+06)
            ]
        }
    }

    # 3. Color Palette Definition
    # Hex codes approximated from the provided image
    colors_outer = {
        "Land based": "#95B766",  # Olive Green
        "Energy": "#CC7A3D",      # Rust Orange
        "Industry": "#A6AAB0",    # Grey
        "Waste": "#EBC05C"        # Mustard Yellow
    }

    colors_inner = {
        "LULUC": "#758C47",       # Dark Olive
        "Production": "#95B766",  # Green (Matches Land based outer)
        "Transport": "#1A3B5C",   # Dark Blue
        "Processing": "#46719E",  # Medium Blue
        "Packaging": "#6C9BC2",   # Light Blue
        "Retail": "#8FBBD9",      # Lighter Blue
        "Consumption": "#BBD6EB", # Pale Blue
        "End of Life": "#B0B0B0"  # Grey
    }

    # 4. Plotting Setup
    fig, axes = plt.subplots(1, 3, figsize=(14, 7))
    plt.subplots_adjust(left=0.05, right=0.95, top=0.85, bottom=0.35, wspace=0.1)

    regions = ["Globe", "Industrialized", "Developing"]

    for ax, region in zip(axes, regions):
        reg_data = data[region]
        
        # Flatten data for plotting
        outer_values = []
        outer_colors = []
        inner_values = []
        inner_colors = []
        
        # Iterate in specific order: Energy, Industry, Waste, Land based
        # This matches the clockwise visual starting from top-right
        categories = ["Energy", "Industry", "Waste", "Land based"]
        
        for cat in categories:
            subcats = reg_data[cat]
            
            # Outer Ring Data
            cat_total = sum(val for _, val in subcats)
            outer_values.append(cat_total)
            outer_colors.append(colors_outer[cat])
            
            # Inner Ring Data
            for sub_label, sub_val in subcats:
                inner_values.append(sub_val)
                inner_colors.append(colors_inner.get(sub_label, "#000000")) # Fallback black

        # Calculate Total for Center Text (in Gt CO2e)
        # 1 kton = 10^3 tonnes. 1 Gt = 10^9 tonnes. 
        # So 1 Gt = 1,000,000 kton.
        total_emissions_kton = sum(outer_values)
        total_emissions_gt = total_emissions_kton / 1e6
        
        # Plot Outer Ring
        # startangle=90 and counterclock=False makes it go Clockwise from 12 o'clock
        wedges_outer, _ = ax.pie(outer_values, radius=1.2, colors=outer_colors, 
                                 startangle=90, counterclock=False,
                                 wedgeprops=dict(width=0.35, edgecolor='none'))
        
        # Plot Inner Ring
        wedges_inner, _ = ax.pie(inner_values, radius=0.85, colors=inner_colors, 
                                 startangle=90, counterclock=False,
                                 wedgeprops=dict(width=0.45, edgecolor='none'))
        
        # Center Text
        # Formatting to match image (Globe=18, Ind=4.9, Dev=13)
        if region == "Globe":
            val_str = "18"
        elif region == "Industrialized":
            val_str = "4.9"
        else:
            val_str = "13"
            
        ax.text(0, 0, f"{val_str}\nGt CO$_2$e", ha='center', va='center', fontsize=12)
        
        # Title
        ax.set_title(region, fontsize=16, pad=20)

    # 5. Custom Legend Construction
    # The legend is outside the plots, aligned at the bottom
    
    # Helper to create legend handles
    def create_handle(color, label):
        return mpatches.Patch(color=color, label=label)

    # Outer Circle Legend Items
    outer_legend_items = [
        ("Land based", colors_outer["Land based"]),
        ("Energy", colors_outer["Energy"]),
        ("Industry", colors_outer["Industry"]),
        ("Waste", colors_outer["Waste"])
    ]
    
    # Inner Circle Legend Items
    # Split into two rows as per image
    inner_legend_row1 = [
        ("LULUC", colors_inner["LULUC"]),
        ("Production", colors_inner["Production"]),
        ("Transport", colors_inner["Transport"]),
        ("Processing", colors_inner["Processing"])
    ]
    inner_legend_row2 = [
        ("Packaging", colors_inner["Packaging"]),
        ("Retail", colors_inner["Retail"]),
        ("Consumption", colors_inner["Consumption"]),
        ("End of life", colors_inner["End of Life"])
    ]

    # Add text and patches manually to figure to ensure exact layout
    # Coordinates are relative to figure (0,0 is bottom-left, 1,1 is top-right)
    
    # Row 1: Outer circle
    fig.text(0.05, 0.22, "Outer circle:", fontsize=14, va='center')
    
    x_start = 0.22
    x_spacing = 0.18
    for i, (label, color) in enumerate(outer_legend_items):
        fig.patches.append(mpatches.Rectangle((x_start + i*x_spacing, 0.21), 0.015, 0.02, 
                                              transform=fig.transFigure, color=color, linewidth=0))
        fig.text(x_start + i*x_spacing + 0.025, 0.22, label, fontsize=14, va='center')

    # Row 2: Inner circle (Top half)
    fig.text(0.05, 0.12, "Inner circle:", fontsize=14, va='center')
    
    for i, (label, color) in enumerate(inner_legend_row1):
        fig.patches.append(mpatches.Rectangle((x_start + i*x_spacing, 0.11), 0.015, 0.02, 
                                              transform=fig.transFigure, color=color, linewidth=0))
        fig.text(x_start + i*x_spacing + 0.025, 0.12, label, fontsize=14, va='center')

    # Row 3: Inner circle (Bottom half)
    for i, (label, color) in enumerate(inner_legend_row2):
        fig.patches.append(mpatches.Rectangle((x_start + i*x_spacing, 0.06), 0.015, 0.02, 
                                              transform=fig.transFigure, color=color, linewidth=0))
        fig.text(x_start + i*x_spacing + 0.025, 0.07, label, fontsize=14, va='center')

    # Save output
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_file}")

if __name__ == "__main__":
    main()