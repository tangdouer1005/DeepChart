import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2022, 2023, 2024]
    values = [8, 8, 4, 7, 8]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='F-Score (Piotroski F-Score)')

    # Add titles and labels
    plt.title('meta F-Score (Piotroski F-Score) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('F-Score (Piotroski F-Score)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 158.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
