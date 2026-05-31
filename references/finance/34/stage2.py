import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [12396000000, 16917000000, 28185000000, 38386000000, 51021000000, 74397000000, 44783000000, 89390000000, 123714000000]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)')

    # Add titles and labels
    plt.title('amzn (Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Earnings Before Interest, Taxes, Depreciation, and Amortization, EBITDA)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 34.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
