import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [33504000000, 40901000000, 49468000000, 58056000000, 68423000000, 85134000000, 100239000000, 105140000000, 133009000000]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)')

    # Add titles and labels
    plt.title('msft (Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 174.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
