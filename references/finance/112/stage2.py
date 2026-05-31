import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [78.81760526183926, 79.36426505308447, 78.6713808315999, 73.74595395013083, 64.02464032919895, 69.00115203807024, 79.7604791136988, 81.28233134549106, 93.90955244424048]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Cash Conversion Cycle, CCC)')

    # Add titles and labels
    plt.title('jnj (Cash Conversion Cycle, CCC) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Cash Conversion Cycle, CCC)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 112.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
