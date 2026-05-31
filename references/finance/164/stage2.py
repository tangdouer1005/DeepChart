import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.0924920957010051, 0.064334085778781, 0.2038108032832544, 0.3742016423357664, 0.2759253474933625, 0.4109856537692319, 0.344971784971785, 0.0087349830086631, 0.4080625551290914]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='- (Return on Equity - DuPont Analysis, ROE)')

    # Add titles and labels
    plt.title('mrk - (Return on Equity - DuPont Analysis, ROE) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('- (Return on Equity - DuPont Analysis, ROE)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 164.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
