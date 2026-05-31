import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [3.353487853577838, 3.886255931183732, 4.954804529742273, 5.401418353858988, 4.641245226884335, 3.375519985942825, 3.4470721068718, 2.5152879899112253, 4.966406235220475]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Altman Z-Score)')

    # Add titles and labels
    plt.title('nvda (Altman Z-Score) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Altman Z-Score)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 198.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
