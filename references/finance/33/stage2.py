import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.2821368616202789, 0.0951915023103793, 0.263606019495229, 0.2528361023988069, 0.2693419805166358, 0.1636275877660635, 0.0718671795007202, 0.1572265394475029, 0.2547376130104782]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Return on Invested Capital, ROIC)')

    # Add titles and labels
    plt.title('amzn (Return on Invested Capital, ROIC) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Return on Invested Capital, ROIC)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 33.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
