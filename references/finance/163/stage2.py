import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [-0.0284082865367372, -0.0745189723745028, 0.0343398266625161, 0.1576946472019464, 0.0332656567234108, 0.2027999559062061, 0.1783664983664983, -0.1694347389077681, 0.2211600352826185]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Sustainable Growth Rate, SGR)')

    # Add titles and labels
    plt.title('mrk (Sustainable Growth Rate, SGR) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Sustainable Growth Rate, SGR)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 163.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
