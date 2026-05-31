import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.2070849488896722, 0.2344139650872818, 0.2658523136955507, 0.2609656943156693, 0.2387329614937214, 0.2793461280964071, 0.3059205360414594, 0.2753610503282275, 0.302670501232539]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='- (Return on Equity - DuPont Analysis, ROE)')

    # Add titles and labels
    plt.title('cost - (Return on Equity - DuPont Analysis, ROE) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('- (Return on Equity - DuPont Analysis, ROE)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 45.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
