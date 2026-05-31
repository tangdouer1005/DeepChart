import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.7614932034895516, 0.8580626757406578, 0.7899587247366923, 0.8369133993352157, 0.8728675270731345, 0.8262450146472311, 0.7573884143944538, 0.776815842394083, 0.8229110146500271]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Quality of Income Ratio)')

    # Add titles and labels
    plt.title('jnj (Quality of Income Ratio) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Quality of Income Ratio)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 120.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
