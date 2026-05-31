import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [1.6149572819595055, 1.4906117035569937, 1.7992305835787656, 1.94535423757296, 2.216035867988388, 1.8278962214319, 1.955126073541424, 2.0040386798259284, 2.1972135155377086]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Altman Z-Score)')

    # Add titles and labels
    plt.title('tmo (Altman Z-Score) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Altman Z-Score)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 228.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
