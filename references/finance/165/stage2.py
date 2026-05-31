import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [-8.774668101901687, -10.384643377001456, -11.153415453527437, -11.981782945736434, -15.120031483667848, -14.645784081954297, -10.77104642014162, -14.476639183352964, -12.5745769382133]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label="“” (Graham's Net-Net Working Capital, NNWC)")

    # Add titles and labels
    plt.title("mrk “” (Graham's Net-Net Working Capital, NNWC) (2016-2024)")
    plt.xlabel("Fiscal Year")
    plt.ylabel("“” (Graham's Net-Net Working Capital, NNWC)")
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 165.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
