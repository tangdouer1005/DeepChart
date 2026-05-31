import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.0358639028387823, 0.0740849745694848, 0.1052823158657162, 0.1020156442723539, 0.1207999352279167, 0.1024335179691807, 0.0295842014549834, -0.0181841275217511, 0.0681539914643531]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='- (Earnings Quality Spread)')

    # Add titles and labels
    plt.title('tsla - (Earnings Quality Spread) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('- (Earnings Quality Spread)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 247.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
