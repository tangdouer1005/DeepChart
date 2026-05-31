import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [-0.072860738581904, 0.0103331525642341, -0.0141367955198523, -0.042110810658201, -0.0388459086744948, -0.0535644477226627, -0.0679156068063967, -0.0488854947257887, -0.0526993122725315]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Sloan Ratio / Accruals Ratio)')

    # Add titles and labels
    plt.title('tmus (Sloan Ratio / Accruals Ratio) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Sloan Ratio / Accruals Ratio)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 233.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
