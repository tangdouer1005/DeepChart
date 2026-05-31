import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [-0.0237373003734053, -0.0232142311336614, -0.0255906728280199, -0.0283585293305939, -0.0364838433312319, -0.0247035983345339, -0.0265815846310745, -0.0257477017856283, -0.0342623575606907]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Sloan Ratio / Accruals Ratio)')

    # Add titles and labels
    plt.title('unh (Sloan Ratio / Accruals Ratio) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Sloan Ratio / Accruals Ratio)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 252.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
