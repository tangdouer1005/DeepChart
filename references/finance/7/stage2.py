import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.0182628473591889, 0.0679548526135076, 0.1189506523843919, 0.0733092202307583, 0.1082443257676902, 0.0756326280571132, 0.0918712806745778, 0.1314438643443162, 0.1076658564059998]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='- (Earnings Quality Spread)')

    # Add titles and labels
    plt.title('abbv - (Earnings Quality Spread) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('- (Earnings Quality Spread)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 7.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
