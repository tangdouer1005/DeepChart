import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.0905106850800439, 0.0916084661594111, 0.0994910539218577, 0.0455209636016586, 0.0922879971206014, 0.0422554468026926, 0.0713511919511301, 0.0815357684489045]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='- (Earnings Quality Spread)')

    # Add titles and labels
    plt.title('wmt - (Earnings Quality Spread) (2017-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('- (Earnings Quality Spread)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 277.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
