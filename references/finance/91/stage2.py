import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2022, 2023, 2024]
    values = [0.1411439047543133, 0.0745990785582146, 0.1983896471646807, 0.238023049159283, 0.2780684056372145]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Internal Growth Rate, IGR)')

    # Add titles and labels
    plt.title('goog (Internal Growth Rate, IGR) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Internal Growth Rate, IGR)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 91.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
