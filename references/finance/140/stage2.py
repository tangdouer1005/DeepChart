import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.9037053596378471, 0.9653607467638514, 0.7235945931786032, 0.6687776548672566, 0.7615499080225433, 0.7658481530704808, 0.6962007901098685, 0.3443148782745684, 0.4576376743148072]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Quality of Income Ratio)')

    # Add titles and labels
    plt.title('lly (Quality of Income Ratio) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Quality of Income Ratio)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 140.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
