import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [8.26468714057128, 6.852032555196057, 6.379922916297005, 4.04438747282325, 4.834067907880158, 4.38022491379083, 3.097551335325865, 3.2408635998043285, 3.4070346259751405]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Altman Z-Score)')

    # Add titles and labels
    plt.title('meta (Altman Z-Score) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Altman Z-Score)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 157.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
