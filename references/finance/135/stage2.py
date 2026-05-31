import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [-8.742136936527762, -13.41320484438078, -12.04420766068763, -23.89219718315743, -24.40523108123648, -22.22904976967513, -21.76414623724718, -30.351030240765915, -35.06806524795395]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label="“” (Graham's Net-Net Working Capital, NNWC)")

    # Add titles and labels
    plt.title("lly “” (Graham's Net-Net Working Capital, NNWC) (2016-2024)")
    plt.xlabel("Fiscal Year")
    plt.ylabel("“” (Graham's Net-Net Working Capital, NNWC)")
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 135.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
