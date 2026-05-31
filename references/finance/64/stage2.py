import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [-0.0240910541431762, -0.0339364536525231, -0.1136285529878207, -0.0407596198996016, -0.0437278739241925, -0.0505640759033012, -0.0147677011368205, -0.074269608994455, -0.0049499480697412]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Sloan Ratio / Accruals Ratio)')

    # Add titles and labels
    plt.title('csco (Sloan Ratio / Accruals Ratio) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Sloan Ratio / Accruals Ratio)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 64.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
