import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [185.2906238196892, 105.8474105742663, 77.42944184758403, 113.06377249173772, 262.7970347302146, 150.30500559934077, 103.6496377347331, 82.67551944653057, 82.8051404860176]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Defensive Interval Ratio, DIR)')

    # Add titles and labels
    plt.title('tsla (Defensive Interval Ratio, DIR) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Defensive Interval Ratio, DIR)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 241.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
