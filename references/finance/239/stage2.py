import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [-968160034.3790288, -869025877.8867445, 294620142.9665556, 370628861.6119919, -3230940934.8441925, -7155940734.109221, -8762909821.996185, -3309376420.5836887, -102427922.78412056]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Economic Value Added, EVA) -')

    # Add titles and labels
    plt.title('tmus (Economic Value Added, EVA) - (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Economic Value Added, EVA) -')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 239.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
