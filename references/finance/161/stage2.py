import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [116.87268326446308, 120.4706378294807, 115.77397039290368, 130.856190504121, 106.16036796791316, 94.51238341311868, 88.85682525103635, 106.3145857944624, 112.3112705943573]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Cash Conversion Cycle, CCC)')

    # Add titles and labels
    plt.title('mrk (Cash Conversion Cycle, CCC) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Cash Conversion Cycle, CCC)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 161.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
