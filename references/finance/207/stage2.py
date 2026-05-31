import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [1.943674663866236, 1.72907077313593, 1.5994861461274528, 1.1870277166848076, 1.0154339698158927, 0.7893534459001637, 0.4174577380821586, 0.3917210510860927, 0.4734661089691617]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Altman Z-Score)')

    # Add titles and labels
    plt.title('orcl (Altman Z-Score) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Altman Z-Score)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 207.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
