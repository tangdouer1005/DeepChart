import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [-14.99610288386594, -16.944084278768234, -20.3902027027027, -23.93000874890639, -31.487693710118503, -35.99721706864564, -42.0765595463138, -41.37756097560976, -45.61976047904192]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label="“” (Graham's Net-Net Working Capital, NNWC)")

    # Add titles and labels
    plt.title("hd “” (Graham's Net-Net Working Capital, NNWC) (2016-2024)")
    plt.xlabel("Fiscal Year")
    plt.ylabel("“” (Graham's Net-Net Working Capital, NNWC)")
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 108.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
