import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [3.612121212121212, 9.703296703296704, 17.966329966329965, 2.73985401459854, 32.90186210367388, 1.6805555555555556, 3.1134289439374188, 4.0501942037645655, 7.540134645261522]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Cash Burn Runway) -  (Zero Revenue Scenario)')

    # Add titles and labels
    plt.title('nvda (Cash Burn Runway) -  (Zero Revenue Scenario) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Cash Burn Runway) -  (Zero Revenue Scenario)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 196.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
