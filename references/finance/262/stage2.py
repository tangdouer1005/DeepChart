import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]
    values = [396.7760193863512, 314.24185480135907, 317.19204948679914, 347.94444381748, 335.1593880507362, 309.93589310181767, 361.7787100878196, 339.25471363680265]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Cash Conversion Cycle, CCC)')

    # Add titles and labels
    plt.title('v (Cash Conversion Cycle, CCC) (2016-2023)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Cash Conversion Cycle, CCC)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 262.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
