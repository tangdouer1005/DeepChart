import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [13803000000, 15436000000, 16817000000, 17759000000, 18212000000, 20844000000, 25946000000, 27069000000, 25114000000]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)')

    # Add titles and labels
    plt.title('hd (Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 107.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
