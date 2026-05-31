import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.1396131340570229, 0.143860344217885, 0.1730148138772629, 0.1586064759979097, 0.0091273800365296, 0.1126481073360953, 0.0529229889802611, -0.0383514462004077, 0.0263820982801433]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Sloan Ratio / Accruals Ratio)')

    # Add titles and labels
    plt.title('nflx (Sloan Ratio / Accruals Ratio) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Sloan Ratio / Accruals Ratio)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 183.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
