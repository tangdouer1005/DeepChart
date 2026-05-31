import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [-0.1642197746279023, -0.1611376277622699, 0.0701532175481268, 0.2912535632282351, -0.2720071389438035, -0.2367802386973345, 0.0324195470663024, -0.0347974956786396, 0.1306088256344503]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Reinvestment Rate)')

    # Add titles and labels
    plt.title('v (Reinvestment Rate) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Reinvestment Rate)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 270.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
