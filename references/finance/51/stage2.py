import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2023, 2024]
    values = [-0.0040275568247199, 0.021749492110641, 0.0066499096538635, -0.0066849573104563, 0.0350518901346226]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Internal Growth Rate, IGR)')

    # Add titles and labels
    plt.title('crm (Internal Growth Rate, IGR) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Internal Growth Rate, IGR)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 51.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
