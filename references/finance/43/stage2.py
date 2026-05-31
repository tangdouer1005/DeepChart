import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.2445703808287204, 0.2726571364303687, 0.3011522905115193, 0.3721073375082542, 0.3818751130822868, 0.3455974552451687, 0.3752626944934977]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Return on Invested Capital, ROIC)')

    # Add titles and labels
    plt.title('cost (Return on Invested Capital, ROIC) (2018-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Return on Invested Capital, ROIC)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 43.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
