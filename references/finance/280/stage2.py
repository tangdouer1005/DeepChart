import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.9643466082085008, 0.9151004327326744, 0.8504060058219702, 0.800348597686579, 1.0704451038575669, 0.6606830601092896, 0.9275810410225352, 0.9192332432780136]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Quality of Income Ratio)')

    # Add titles and labels
    plt.title('wmt (Quality of Income Ratio) (2017-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Quality of Income Ratio)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 280.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
