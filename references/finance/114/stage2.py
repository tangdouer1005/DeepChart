import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.2239154957050199, 0.0178795367852134, 0.241491936814696, 0.257723767071883, 0.2279515388230207, 0.2186079101712973, 0.1805332587807077, 0.2150572298378512, 0.2329888126878679]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Return on Invested Capital, ROIC)')

    # Add titles and labels
    plt.title('jnj (Return on Invested Capital, ROIC) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Return on Invested Capital, ROIC)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 114.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
