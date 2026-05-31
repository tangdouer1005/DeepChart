import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.1331083634235496, 0.1799244167405453, 0.1833446355503545, 0.1893023141894938, 0.1899488953362313, 0.2022169976688141, 0.2137821416002205, 0.2153277937839195, 0.1808483789551966]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Return on Invested Capital, ROIC)')

    # Add titles and labels
    plt.title('unh (Return on Invested Capital, ROIC) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Return on Invested Capital, ROIC)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 251.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
