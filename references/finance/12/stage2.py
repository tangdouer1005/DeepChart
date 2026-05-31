import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [111.02459107512902, 87.89444221760236, 87.24053940726195, 83.291106540028, 84.99078843363034, 71.33669448985013, 72.92296167644572, 93.08734151869892, 96.50555177520138]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Cash Conversion Cycle, CCC)')

    # Add titles and labels
    plt.title('abt (Cash Conversion Cycle, CCC) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Cash Conversion Cycle, CCC)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 12.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
