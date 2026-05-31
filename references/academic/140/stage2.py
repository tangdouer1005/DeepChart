import sys
import io
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def generate_chart(output_filename='output.png'):
    # Source Data
    csv_data = """
| Protein conversion from feed to animal food in China and Brazil protein supply to the Chinese's diet   | Unnamed: 1                                                                                       |       Unnamed: 2 |       Unnamed: 3 |       Unnamed: 4 |       Unnamed: 5 |       Unnamed: 6 |       Unnamed: 7 |       Unnamed: 8 |       Unnamed: 9 |      Unnamed: 10 |      Unnamed: 11 |      Unnamed: 12 |      Unnamed: 13 |      Unnamed: 14 |      Unnamed: 15 |      Unnamed: 16 |      Unnamed: 17 |      Unnamed: 18 |
|:-------------------------------------------------------------------------------------------------------|:-------------------------------------------------------------------------------------------------|-----------------:|-----------------:|-----------------:|-----------------:|-----------------:|-----------------:|-----------------:|-----------------:|-----------------:|-----------------:|-----------------:|-----------------:|-----------------:|-----------------:|-----------------:|-----------------:|-----------------:|
| unit: protein                                                                                          | nan                                                                                              |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |
| nan                                                                                                    | nan                                                                                              |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |
| nan                                                                                                    | nan                                                                                              |   2004           |   2005           |   2006           |   2007           |   2008           |   2009           |   2010           |   2011           |   2012           |   2013           |   2014           |   2015           |   2016           |   2017           |   2018           |   2019           |   2020           |
| Animal proteins from livestock and aquaculture intensively farmed and fed within China                 | Bovine Meat                                                                                      | 116448           | 130727           | 154537           | 190479           | 229452           | 262134           | 321026           | 342833           | 354985           | 395428           | 404133           | 437579           | 432522           | 390502           | 433939           | 519452           | 671737           |
| nan                                                                                                    | Butter, Ghee                                                                                     |     93.4682      |     87.9395      |     80.7548      |    134.122       |    163.14        |    149.581       |    209.762       |    305.631       |    369.082       |    424.095       |    540.21        |    489.742       |    519.786       |    463.263       |    608.843       |    610.548       |    769.771       |
| nan                                                                                                    | Cream                                                                                            |      2.97998     |      5.53863     |      2.50017     |      8.46501     |     15.1787      |     20.3608      |     39.7133      |     79.6142      |    125.605       |      0           |    362.948       |    624.307       |    932.939       |   1319.53        |   1413.77        |   2033.2         |   2559.26        |
| nan                                                                                                    | Eggs                                                                                             |      2.10792e+06 |      2.23611e+06 |      2.23082e+06 |      2.16841e+06 |      2.44559e+06 |      2.51604e+06 |      2.63286e+06 |      2.69984e+06 |      2.76336e+06 |      2.79006e+06 |      2.8089e+06  |      2.92713e+06 |      3.07557e+06 |      2.9808e+06  |      3.00279e+06 |      3.19466e+06 |      3.35378e+06 |
| nan                                                                                                    | Fats, Animals, Raw                                                                               |    916.922       |    819.956       |   1407.74        |   2110.01        |   2054.12        |   1929.75        |   3146.97        |   3307.26        |   2484.82        |   2570.52        |   2684.77        |   3162.32        |   2696.99        |   2705.78        |   2822.12        |   3082.21        |   3142.52        |
| nan                                                                                                    | Meat, Other                                                                                      |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |
| nan                                                                                                    | Milk - Excluding Butter                                                                          | 109282           | 111909           | 114232           | 205433           | 251866           | 214098           | 321304           | 448205           | 506548           | 552066           | 658548           | 539222           | 543064           | 483576           | 572842           | 709217           | 774458           |
| nan                                                                                                    | Mutton & Goat Meat                                                                               |  84461.6         |  98902           | 133630           | 144605           | 147623           | 140325           | 163631           | 176019           | 210099           | 255013           | 288432           | 344531           | 371334           | 376205           | 389122           | 433218           | 465187           |
| nan                                                                                                    | Offals, Edible                                                                                   | 106224           | 105219           | 169035           | 253254           | 259863           | 256375           | 295234           | 343970           | 375598           | 396952           | 417644           | 426294           | 481003           | 464953           | 449960           | 413486           | 449723           |
| nan                                                                                                    | Pigmeat                                                                                          | 735424           | 750317           |      1.22013e+06 |      1.72649e+06 |      1.78578e+06 |      1.84562e+06 |      2.81413e+06 |      3.08592e+06 |      3.37002e+06 |      3.60431e+06 |      3.92609e+06 |      4.1012e+06  |      4.27359e+06 |      4.15259e+06 |      4.10718e+06 |      3.92201e+06 |      3.23748e+06 |
| nan                                                                                                    | Poultry Meat                                                                                     |      1.00072e+06 |      1.08863e+06 |      1.13438e+06 |      1.11692e+06 |      1.26369e+06 |      1.3835e+06  |      2.01241e+06 |      2.06576e+06 |      2.12639e+06 |      2.17504e+06 |      2.09199e+06 |      2.07189e+06 |      2.20133e+06 |      2.09221e+06 |      2.29888e+06 |      2.49983e+06 |      2.82719e+06 |
| nan                                                                                                    | nan                                                                                              |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |
| nan                                                                                                    | Aquatic Animals, Others                                                                          |   6859.15        |   6800.7         |   7022.48        |  10666.5         |  12929.2         |  16212.1         |  45112           |  37409.6         |  38983.3         |  39444.7         |  38409.5         |  41157           |  46364           |  48817           |  49731.8         |  63233.2         |  67451.2         |
| nan                                                                                                    | Cephalopods                                                                                      |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |
| nan                                                                                                    | Crustaceans                                                                                      | 147183           | 151676           | 155593           | 184695           | 190707           | 230321           | 254643           | 265639           | 292547           | 310814           | 347290           | 376249           | 396348           | 425888           | 493859           | 606018           | 638961           |
| nan                                                                                                    | Demersal Fish                                                                                    |  23337.5         |  24364.9         |  25472.7         |  27577.8         |  31923.8         |  33574.3         |  17260.5         |  18278.9         |  19383.7         |  19542.3         |  19865           |  21656.4         |  23464.6         |  25260           |  25217.9         |  28625.2         |  31810.3         |
| nan                                                                                                    | Fish, Body Oil                                                                                   |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |
| nan                                                                                                    | Freshwater Fish                                                                                  |      1.18861e+06 |      1.28899e+06 |      1.41433e+06 |      1.48642e+06 |      1.55572e+06 |      1.65828e+06 |      1.72533e+06 |      1.80764e+06 |      1.8434e+06  |      1.97508e+06 |      2.06457e+06 |      2.1459e+06  |      2.23508e+06 |      2.25466e+06 |      2.25307e+06 |      2.18795e+06 |      2.22307e+06 |
| nan                                                                                                    | Marine Fish, Other                                                                               |   3830.07        |   3569.69        |   2804.29        |   3085.98        |   4778.6         |   8701.86        |   4239.97        |   5297.82        |   4487.2         |   5709.57        |   7413.83        |   8888.99        |  11844.3         |  12384.4         |  11543.2         |  13755.6         |  15993.3         |
| nan                                                                                                    | Molluscs, Other                                                                                  |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |      0           |
| nan                                                                                                    | Pelagic Fish                                                                                     |   1495.55        |   1728.63        |   1643.82        |   1729.09        |   2117.46        |   1534.55        |    816.103       |    556.65        |    604.615       |    544.695       |    765.036       |   1034.52        |    434.886       |    616.567       |    588.29        |    530.249       |    520.818       |
| nan                                                                                                    | nan                                                                                              |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |
| nan                                                                                                    | Total animal food                                                                                |      1.42261e+07 |      1.4791e+07  |      1.53504e+07 |      1.60642e+07 |      1.69052e+07 |      1.74956e+07 |      2.07835e+07 |      2.0825e+07  |      2.12629e+07 |      2.17786e+07 |      2.25388e+07 |      2.27761e+07 |      2.33249e+07 |      2.33663e+07 |      2.36365e+07 |      2.41356e+07 |      2.37371e+07 |
| nan                                                                                                    | Total animal food                                             (intensive farming + acquaculture) |      5.63281e+06 |      5.99985e+06 |      6.76513e+06 |      7.52203e+06 |      8.18428e+06 |      8.56884e+06 |      1.06114e+07 |      1.13011e+07 |      1.19094e+07 |      1.2523e+07  |      1.30776e+07 |      1.3447e+07  |      1.40961e+07 |      1.37129e+07 |      1.40936e+07 |      1.45977e+07 |      1.47638e+07 |
| nan                                                                                                    | Total feed                                                                                       |      2.62354e+07 |      2.84349e+07 |      2.89785e+07 |      2.9839e+07  |      3.21302e+07 |      3.49477e+07 |      4.04937e+07 |      4.10089e+07 |      4.57656e+07 |      4.37183e+07 |      4.55764e+07 |      5.24634e+07 |      5.19704e+07 |      5.79228e+07 |      5.85285e+07 |      5.73791e+07 |      6.48526e+07 |
| nan                                                                                                    | nan                                                                                              |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |
| nan                                                                                                    | PER (protein efficiency ratio)                                                                   |      0.214702    |      0.211003    |      0.233454    |      0.252087    |      0.254722    |      0.24519     |      0.262051    |      0.275576    |      0.260225    |      0.286448    |      0.286939    |      0.256312    |      0.271233    |      0.236745    |      0.240798    |      0.254408    |      0.227652    |
| nan                                                                                                    | nan                                                                                              |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |    nan           |
| nan                                                                                                    | Soybean from Brazil to China                                                                     |      2.15769e+06 |      2.72217e+06 |      4.09963e+06 |      3.82731e+06 |      4.49326e+06 |      6.05794e+06 |      6.02379e+06 |      8.40924e+06 |      8.57994e+06 |      1.22675e+07 |      1.24644e+07 |      1.55524e+07 |      1.46582e+07 |      2.0449e+07  |      2.62001e+07 |      2.20359e+07 |      2.44349e+07 |
| nan                                                                                                    | Tot protein (converted to food) from Brazil to China                                             | 465671           | 576672           | 958516           | 966658           |      1.15234e+06 |      1.49994e+06 |      1.59375e+06 |      2.34197e+06 |      2.26413e+06 |      3.5376e+06  |      3.60462e+06 |      4.04271e+06 |      4.0763e+06  |      4.93425e+06 |      6.44131e+06 |      5.80095e+06 |      5.86864e+06 |
    """
    
    # Manual Parsing to handle markdown table structure robustly
    lines = [line for line in csv_data.split('\n') if line.strip()]
    
    # Find header row (containing years)
    header_idx = -1
    for i, line in enumerate(lines):
        if '2004' in line and '2020' in line:
            header_idx = i
            break
    
    if header_idx == -1:
        raise ValueError("Could not find header row with years")

    # Parse header to map years to column indices
    header_parts = lines[header_idx].split('|')
    # Note: split('|') on "| a | b |" gives ['', ' a ', ' b ', '']
    
    year_map = {}
    for idx, part in enumerate(header_parts):
        p = part.strip()
        if p.isdigit():
            y = int(p)
            if 2004 <= y <= 2020:
                year_map[y] = idx
    
    years = sorted(year_map.keys())
    col_indices = [year_map[y] for y in years]
    
    def get_row_values(label_pattern):
        for line in lines:
            if label_pattern in line:
                parts = line.split('|')
                vals = []
                for idx in col_indices:
                    if idx < len(parts):
                        val_str = parts[idx].strip()
                        try:
                            vals.append(float(val_str))
                        except ValueError:
                            vals.append(np.nan)
                    else:
                        vals.append(np.nan)
                return np.array(vals)
        return np.zeros(len(years))

    # Extract Data
    # Units in table are "protein" (likely tonnes). Chart is 10^6 tonnes.
    feed_total = get_row_values("Total feed") / 1e6
    food_animal = get_row_values("Total animal food") / 1e6
    brazil_soy_feed = get_row_values("Soybean from Brazil to China") / 1e6
    brazil_soy_food = get_row_values("Tot protein (converted to food) from Brazil to China") / 1e6

    # Plotting
    fig, ax = plt.subplots(figsize=(12, 8))
    
    x = np.arange(len(years))
    width = 0.35
    
    c_orange = '#E69F00'
    c_blue = '#0072B2'
    
    # Left Bar: Feed
    # 1. Total Feed (Solid Orange)
    ax.bar(x - width/2 - 0.02, feed_total, width=width, color=c_orange, label='_nolegend_')
    
    # 2. Brazil Soy (Overlay at bottom)
    # Texture: Orange background with white diagonal stripes (mimicking "CHN soybean feed supply")
    ax.bar(x - width/2 - 0.02, brazil_soy_feed, width=width, 
           color=c_orange, edgecolor='white', hatch='//', linewidth=0)
    # Red border for Brazil part
    ax.bar(x - width/2 - 0.02, brazil_soy_feed, width=width, 
           color='none', edgecolor='red', linewidth=1.5)

    # Right Bar: Food
    # 1. Animal Food (Hatched Blue)
    # Note: "Total Food" (Solid Blue) data is missing, so we only plot the Animal Food part.
    ax.bar(x + width/2 + 0.02, food_animal, width=width, 
           color=c_blue, edgecolor='white', hatch='//', label='_nolegend_')
    
    # 2. Brazil Converted (Overlay at bottom)
    # Red border
    ax.bar(x + width/2 + 0.02, brazil_soy_food, width=width, 
           color='none', edgecolor='red', linewidth=1.5)

    # Formatting
    ax.set_xticks(x)
    ax.set_xticklabels(years)
    ax.set_ylabel('Protein supply quantity ($10^6$ t $yr^{-1}$)', fontsize=12)
    ax.set_ylim(0, 70)
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Titles above bars
    ax.text(0, 68, "Feed protein supply", fontsize=12)
    ax.text(len(years)/2, 68, "Food protein supply", fontsize=12)
    
    # Legend
    patches = []
    # Column 1
    patches.append(mpatches.Patch(facecolor=c_orange, hatch='//', edgecolor='red', label='BRA soybean to CHN'))
    patches.append(mpatches.Patch(facecolor=c_orange, hatch='//', edgecolor='white', label='CHN soybean feed supply'))
    patches.append(mpatches.Patch(facecolor=c_orange, label='CHN total feed supply'))
    patches.append(mpatches.Patch(facecolor='none', edgecolor='red', linewidth=1.5, label='BRA contribution to CHN protein supply'))
    
    # Column 2
    patches.append(mpatches.Patch(facecolor=c_blue, hatch='//', edgecolor='red', label='BRA soybean (converted into animal food) to CHN'))
    patches.append(mpatches.Patch(facecolor=c_blue, hatch='//', edgecolor='white', label='CHN animal food supply'))
    patches.append(mpatches.Patch(facecolor=c_blue, label='CHN total food supply'))
    
    ax.legend(handles=patches, loc='upper left', ncol=2, frameon=False, fontsize=9)
    
    plt.tight_layout()
    plt.savefig(output_filename)

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)