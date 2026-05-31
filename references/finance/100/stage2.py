import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [1.5171507636199737, 3.531434467351863, 0.1408525000962673, 0.9836181004657067, 0.7216140989011716, 0.5621847979513882, 0.0388548282260216, 0.3392217112413975, 0.4055428216912424]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Reinvestment Rate)')

    # Add titles and labels
    plt.title('goog (Reinvestment Rate) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Reinvestment Rate)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 100.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
