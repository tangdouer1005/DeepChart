import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.4380441815433644, 0.9251850800462575, 0.8410973751548196, -2.162236522680179, -0.8650936877200964, 0.8102507887829582, -1.1001895055319706, 0.5260186674762015, 0.5199799282950175]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Reinvestment Rate)')

    # Add titles and labels
    plt.title('orcl (Reinvestment Rate) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Reinvestment Rate)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 210.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
