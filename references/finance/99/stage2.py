import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [1.2068318821165438, 1.1208110476535824, 1.3121529582318991, 1.1849082847952708, 1.1857759327033377, 1.0054522516592617, 1.0359840121380934, 1.0572221240869086, 0.981190437036515]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Quality of Income Ratio)')

    # Add titles and labels
    plt.title('goog (Quality of Income Ratio) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Quality of Income Ratio)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 99.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
