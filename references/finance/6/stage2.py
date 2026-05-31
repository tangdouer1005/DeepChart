import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [-27.759656652360515, -27.73923892701185, -32.89327296248383, -32.18867924528302, -67.71966527196653, -58.05571187394485, -52.33689538807649, -51.50141003948111, -59.90693739424704]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label="“” (Graham's Net-Net Working Capital, NNWC)")

    # Add titles and labels
    plt.title("abbv “” (Graham's Net-Net Working Capital, NNWC) (2016-2024)")
    plt.xlabel("Fiscal Year")
    plt.ylabel("“” (Graham's Net-Net Working Capital, NNWC)")
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 6.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
