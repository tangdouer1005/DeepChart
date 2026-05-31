import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.1578676115879611, 0.1608282329416772, 0.2426229584502731, 0.2640788301220306, 0.2420862503672333, 0.2811041632879178, 0.367570412310678, 0.4040071263492115, 0.4280222803015777]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Return on Invested Capital, ROIC)')

    # Add titles and labels
    plt.title('v (Return on Invested Capital, ROIC) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Return on Invested Capital, ROIC)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 264.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
