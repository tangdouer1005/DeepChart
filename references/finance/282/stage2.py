import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [46.213249973465686, 47.0241288063651, 39.36967357158409, 45.178364776766045, 43.769048466027634, 56.60488061644892, 77.86409261101997, 87.47092021665128, 81.27355262938299]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Defensive Interval Ratio, DIR)')

    # Add titles and labels
    plt.title('xom (Defensive Interval Ratio, DIR) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Defensive Interval Ratio, DIR)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 282.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
