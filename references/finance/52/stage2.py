import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
    values = [225.63684823629023, 149.17925065151655, 112.43368955501232, 150.83612414254966, 37.26970055115291, -71.9492349706463, -67.04543111887563, -76.89192077060474]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Cash Conversion Cycle, CCC)')

    # Add titles and labels
    plt.title('crm (Cash Conversion Cycle, CCC) (2016-2023)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Cash Conversion Cycle, CCC)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 52.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
