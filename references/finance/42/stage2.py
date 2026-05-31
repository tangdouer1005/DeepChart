import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [14.692386589828503, 17.46777783114783, 20.564130244500205, 24.4680196801968, 31.283581071866905, 25.19416449548412, 20.724763986293183, 24.91512793796119, 18.79876248123736]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Defensive Interval Ratio, DIR)')

    # Add titles and labels
    plt.title('cost (Defensive Interval Ratio, DIR) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Defensive Interval Ratio, DIR)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 42.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
