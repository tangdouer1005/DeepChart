import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [10.011098898963311, 9.408196605168513, 10.380436106959516, 11.419210720784433, 16.49973071339519, 15.37932598406765, 10.38919475138823, 10.967400456921688]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Defensive Interval Ratio, DIR)')

    # Add titles and labels
    plt.title('wmt (Defensive Interval Ratio, DIR) (2017-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Defensive Interval Ratio, DIR)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 272.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
