import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [177.0779238527346, 219.91979351687388, 191.6346127873369, 216.3364733979037, 228.4459516269163, 190.6763552791672, 170.96387144833457, 168.11030095074702, 167.02200759213878]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Defensive Interval Ratio, DIR)')

    # Add titles and labels
    plt.title('csco (Defensive Interval Ratio, DIR) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Defensive Interval Ratio, DIR)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 62.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
