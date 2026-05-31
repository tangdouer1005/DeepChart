import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.1466161480381355, 0.1212078235675596, 0.135276880454518, 0.0884305855268118, 0.0979467290916925, 0.0120072142110074, 0.0564175592842548, 0.0711436786939987, 0.0613876137553354]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='- (Earnings Quality Spread)')

    # Add titles and labels
    plt.title('crm - (Earnings Quality Spread) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('- (Earnings Quality Spread)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 56.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
