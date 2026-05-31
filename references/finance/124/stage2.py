import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [-0.0255999458440987, -0.066885126108948, -0.0139440834073589, -0.0182904178729576, -0.0241482752465784, -0.0314230663363611, -0.0157762255700978, -0.0092929971753488, 0.0385973407582269]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Sloan Ratio / Accruals Ratio)')

    # Add titles and labels
    plt.title('ko (Sloan Ratio / Accruals Ratio) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Sloan Ratio / Accruals Ratio)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 124.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
