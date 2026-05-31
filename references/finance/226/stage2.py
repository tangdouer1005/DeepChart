import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.0942794856549971, 0.0947770396764375, 0.110870016415404, 0.1290931000157175, 0.1986538281761241, 0.2051792828685259, 0.1639711693857569, 0.1321751016943547, 0.1315420633519866]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='- (Return on Equity - DuPont Analysis, ROE)')

    # Add titles and labels
    plt.title('tmo - (Return on Equity - DuPont Analysis, ROE) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('- (Return on Equity - DuPont Analysis, ROE)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 226.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
