import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.1325662831415708, 0.1348703397957469, 0.0089324967027696, 0.2397035686453263, 0.417318881242801, 1.2341728280961184, -6.639511201629328, -1.8787643287351847, 1.242917050219904]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Sustainable Growth Rate, SGR)')

    # Add titles and labels
    plt.title('orcl (Sustainable Growth Rate, SGR) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Sustainable Growth Rate, SGR)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 203.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
