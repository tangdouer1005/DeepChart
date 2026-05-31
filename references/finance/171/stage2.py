import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.0546147235749069, 0.0669657318425883, 0.0157337613523232, 0.1028377542230652, 0.1100647873121857, 0.164042596088638, 0.1852792524087524, 0.1565028122925022, 0.1677135337101296]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Internal Growth Rate, IGR)')

    # Add titles and labels
    plt.title('msft (Internal Growth Rate, IGR) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Internal Growth Rate, IGR)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 171.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
