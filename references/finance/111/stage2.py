import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.0612023293827599, -0.0487130214756674, 0.0388614134893236, 0.0346478929525306, 0.0261170547514159, 0.0583951129826226, 0.0350764126676343, 0.1517539020670409, 0.0130720096976478]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Internal Growth Rate, IGR)')

    # Add titles and labels
    plt.title('jnj (Internal Growth Rate, IGR) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Internal Growth Rate, IGR)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 111.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
