import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [7147510579.710144, -2464469056.3748016, 7860221797.038353, 12015668498.42271, 14535078644.815102, 42990467138.007805, 38061792507.85105, 46389507888.16687, 64444633685.26479]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Economic Value Added, EVA) -')

    # Add titles and labels
    plt.title('goog (Economic Value Added, EVA) - (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Economic Value Added, EVA) -')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 98.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
