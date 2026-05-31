import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.0770003200797619, 0.0006972285166463, 0.0431647851247509, -0.0324460930175681, 0.1284019995425882, 0.0646336702381468, -0.0176491545397242, 0.0298234722205953, -0.0312412309419137]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='- (Earnings Quality Spread)')

    # Add titles and labels
    plt.title('nvda - (Earnings Quality Spread) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('- (Earnings Quality Spread)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 197.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
