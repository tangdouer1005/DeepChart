import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.221790616027692, 0.188613622049744, 0.2002590295609977, 0.5621677343020484, 0.1327959138068086, 0.1838355874045878, 0.2067749461163351, 0.1549026679437163, 0.1269399846341908]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Return on Invested Capital, ROIC)')

    # Add titles and labels
    plt.title('abbv (Return on Invested Capital, ROIC) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Return on Invested Capital, ROIC)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 3.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
