import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [-0.0105648753203924, 0.0516676163057238, 0.015092860791985, 0.0888093676120957, 0.005091937765205, 0.1080421343097455, 0.0289889986348671, 0.0035711219847197, 0.0700987246303122]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='- (Return on Equity - DuPont Analysis, ROE)')

    # Add titles and labels
    plt.title('crm - (Return on Equity - DuPont Analysis, ROE) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('- (Return on Equity - DuPont Analysis, ROE)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 53.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
