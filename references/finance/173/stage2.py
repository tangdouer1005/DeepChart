import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.1253682272488164, 0.1889868482107611, 0.0499252153282789, 0.2748367991007738, 0.2641841239337545, 0.3438446052894441, 0.3539558551842608, 0.2820060896275133, 0.2796081735833158]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Sustainable Growth Rate, SGR)')

    # Add titles and labels
    plt.title('msft (Sustainable Growth Rate, SGR) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Sustainable Growth Rate, SGR)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 173.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
