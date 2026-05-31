import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [9656176960.561531, -6384414352.40197, 10544120623.367966, 11197362257.61773, 9879202288.294842, 10546971196.16227, 7926324928.973602, 10343990134.112335, 10656792527.116917]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Economic Value Added, EVA) -')

    # Add titles and labels
    plt.title('jnj (Economic Value Added, EVA) - (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Economic Value Added, EVA) -')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 119.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
