import sys
import numpy as np
import matplotlib.pyplot as plt

def generate_chart(output_filename):
    # 1. Source Data
    # Extracted faithfully from the provided Markdown table.
    # Column: Fig. 1l (Parental)
    data_parental = [
        0.8299296674003414, 1.0355057637490246, 1.134564568850634, 
        1.067366156351031, 1.0214732863448737, 0.9111623735995769, 
        0.7882105310868032, 0.9514894525471388, 1.2603002786479676, 
        1.151744305174724, 0.8150691363293474, 1.033186952433866, 
        1.0000178133667066, 1.0001977922468785, 1.000081804170821
    ]

    # Column: Unnamed: 1 (Lymph node late generations -> LN)
    data_ln = [
        0.8025826043362723, 0.5586761586545418, 0.981485217508094, 
        0.6828174503771713, 0.8991676521394686, 0.8518380020755709, 
        2.222764945615544, 1.625153697906596, 2.496864417961382, 
        1.1651481165731932, 1.54030017361637, 1.1177187016815318, 
        0.37278141648377583, 0.21125251548675206, 0.2840339839626573, 
        0.4938553059954519, 0.9079694495974822, 0.6916331033068995, 
        0.6090772699389065, 0.5130045874571015, 0.618016249272412, 
        0.555341273528883, 0.9781711654635805, 0.45367395258469567, 
        0.5369301638703191, 0.589444402175406, 0.43573465345652695, 
        0.5996181837280969, 0.8639109240152595, 1.2218269477581314, 
        0.13994083686105493, 0.10597787396603812, 0.18815322961925368, 
        0.2869213153964222, 0.8911277607591113, 0.40339876934736785, 
        0.5357799907267852, 0.7520433000113403, 0.8726564170965828, 
        0.20897275168862095, 1.2240086468234774, 0.3036788001925242, 
        0.5369725529955741, 0.735953968614233, 0.5482852964188359, 
        0.5125056222512814, 1.0522782074088821, 0.5448505274112878
    ]

    # P-value from table
    p_value = 0.0016

    # 2. Calculations
    # Calculate Mean and Standard Deviation for error bars
    mean_parental = np.mean(data_parental)
    std_parental = np.std(data_parental, ddof=1) # Sample standard deviation

    mean_ln = np.mean(data_ln)
    std_ln = np.std(data_ln, ddof=1)

    # 3. Plotting Setup
    # Set figure size to match the portrait aspect ratio of the original image
    fig, ax = plt.subplots(figsize=(2.5, 4.5))
    
    # Set global font properties to match scientific publication style
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']
    plt.rcParams['font.size'] = 12

    # Define Colors
    color_parental_bar = '#d9d9d9'  # Light gray
    color_parental_dot = '#000000'  # Black
    color_ln_bar = '#90c088'        # Muted light green
    color_ln_dot = '#3a7d2e'        # Darker green for dots
    color_edge = '#404040'          # Dark gray/black for bar edges

    bar_width = 0.6
    cap_size = 6

    # 4. Draw Bars
    # Parental Bar
    ax.bar(0, mean_parental, yerr=std_parental, width=bar_width, 
           color=color_parental_bar, edgecolor=color_edge, 
           capsize=cap_size, error_kw={'elinewidth': 1, 'capthick': 1, 'ecolor': '#404040'}, zorder=1)

    # LN Bar
    ax.bar(1, mean_ln, yerr=std_ln, width=bar_width, 
           color=color_ln_bar, edgecolor=color_edge, 
           capsize=cap_size, error_kw={'elinewidth': 1, 'capthick': 1, 'ecolor': '#404040'}, zorder=1)

    # 5. Draw Scatter Points (Jitter)
    # Create random jitter for x-axis to spread points within the bar
    np.random.seed(42) # For reproducibility
    jitter_width = 0.2
    
    x_parental = np.random.normal(0, 0.08, size=len(data_parental))
    # Clamp jitter to stay within reasonable bounds
    x_parental = np.clip(x_parental, -jitter_width, jitter_width)
    
    x_ln = np.random.normal(1, 0.08, size=len(data_ln))
    x_ln = np.clip(x_ln, 1-jitter_width, 1+jitter_width)

    ax.scatter(x_parental, data_parental, color=color_parental_dot, s=25, zorder=2, alpha=0.9, edgecolors='none')
    ax.scatter(x_ln, data_ln, color=color_ln_dot, s=25, zorder=2, alpha=0.9, edgecolors='none')

    # 6. Statistical Annotation
    # Draw the line and P-value text
    # Find max y to position the line
    max_y = max(max(data_parental), max(data_ln))
    line_y = 2.75  # Position slightly above the highest data point (approx 2.5)
    text_y = line_y + 0.05

    ax.plot([0, 1], [line_y, line_y], color='black', linewidth=1)
    ax.text(0.5, text_y, f'$P = {p_value}$', ha='center', va='bottom', fontsize=12)

    # 7. Axis Formatting
    # Y-Axis
    ax.set_ylabel('Relative ACSL4 levels', fontsize=13, labelpad=5)
    ax.set_ylim(0, 3.0)
    ax.set_yticks([0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0])
    
    # X-Axis
    ax.set_xticks([0, 1])
    ax.set_xticklabels(['Parental', 'LN'], rotation=45, ha='right', fontsize=12)

    # Spines (Remove top and right)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_linewidth(0.8)
    ax.spines['bottom'].set_linewidth(0.8)

    # 8. Figure Label "l"
    # Place bold 'l' in the top left corner, outside the axes
    # Using figure coordinates or axes coordinates with negative offset
    ax.text(-0.3, 1.05, 'l', transform=ax.transAxes, fontsize=24, fontweight='bold', va='bottom', ha='right')

    # Adjust layout to prevent clipping
    plt.tight_layout()

    # Save
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    # Handle command line argument for output filename
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    else:
        output_file = "output.png"
    
    generate_chart(output_file)