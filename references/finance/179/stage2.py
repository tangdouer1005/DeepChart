import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [9442976001.40411, 11237306947.928162, 1030827743.0498447, 23077021571.140816, 27656360894.486763, 42550733657.28109, 53033567566.53447, 50665151566.99623, 63454512364.19975]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Economic Value Added, EVA) -')

    # Add titles and labels
    plt.title('msft (Economic Value Added, EVA) - (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Economic Value Added, EVA) -')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 179.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
