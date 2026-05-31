import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [-44.71245826411838, -40.01142475916049, -33.540444708681385, -33.71332565750246, -43.30739609642, -34.295608701878635, -24.28725383025208, -31.15182786640692, -34.60099064391855]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label="“” (Graham's Net-Net Working Capital, NNWC)")

    # Add titles and labels
    plt.title("cvx “” (Graham's Net-Net Working Capital, NNWC) (2016-2024)")
    plt.xlabel("Fiscal Year")
    plt.ylabel("“” (Graham's Net-Net Working Capital, NNWC)")
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 76.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
