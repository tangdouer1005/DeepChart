import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.2196297522451757, 0.0435765359899508, 0.4862893211779591, 0.6633033964295174, 1.341312106740742, 1.953863697347039, 2.6988990799856625, 2.657622222087664, 2.5898226699172686]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Altman Z-Score)')

    # Add titles and labels
    plt.title('tsla (Altman Z-Score) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Altman Z-Score)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 248.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
