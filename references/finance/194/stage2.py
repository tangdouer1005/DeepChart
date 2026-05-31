import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.138179642987912, 0.3256768644316293, 0.4605153782211139, 0.492595015761613, 0.2595377332219437, 0.2977626559439117, 0.4483162854844271, 0.1793361115102744, 0.9145807403309824]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='- (Return on Equity - DuPont Analysis, ROE)')

    # Add titles and labels
    plt.title('nvda - (Return on Equity - DuPont Analysis, ROE) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('- (Return on Equity - DuPont Analysis, ROE)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 194.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
