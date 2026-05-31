import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [-1402402672.247263, -3033108641.312682, 1531504171.9342604, 1874878698.9262304, -316306140.201262, 6110371219.108006, 9761468827.53588, -5927901032.292218, 10550729022.873192]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Economic Value Added, EVA) -')

    # Add titles and labels
    plt.title('mrk (Economic Value Added, EVA) - (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Economic Value Added, EVA) -')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 169.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
