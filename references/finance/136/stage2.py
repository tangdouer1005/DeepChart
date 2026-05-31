import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [4.649557327560693, 6.81961169606914, 7.965724545034139, 2.337597399891662, 3.595585524321401, 3.416390802540932, 1.825178993222908, 2.020441444401302, 1.9705676948043795]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Cash Burn Runway) -  (Zero Revenue Scenario)')

    # Add titles and labels
    plt.title('lly (Cash Burn Runway) -  (Zero Revenue Scenario) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Cash Burn Runway) -  (Zero Revenue Scenario)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 136.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
