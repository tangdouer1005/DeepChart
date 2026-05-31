import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.9343785943459048, 0.7689014831785843, 0.9178860282768414, 1.833954999398388, 0.9296970992040172, 0.8865884851117224, 0.8110087293889428, 0.8081350729086723, 0.9256098129751412]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Quality of Income Ratio)')

    # Add titles and labels
    plt.title('pg (Quality of Income Ratio) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Quality of Income Ratio)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 219.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
