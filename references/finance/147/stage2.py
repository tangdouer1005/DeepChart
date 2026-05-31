import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.0243246336996336, 0.081991800819918, 0.0157613284548269, 0.0024031351671103, 0.0258834765998089, 0.0217815390229183, 0.0331182176377417, 0.019341644902183, 0.0421080537728241]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='- (Earnings Quality Spread)')

    # Add titles and labels
    plt.title('ma - (Earnings Quality Spread) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('- (Earnings Quality Spread)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 147.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
