import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [6.974752431082166, 6.448266737232072, 5.159235668789809, 6.006207324643079, 4.600657236748106, 4.749779994133177, 6.930615587606352, 2.0909299304653475, 5.9052361663384]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Cash Burn Runway) -  (Zero Revenue Scenario)')

    # Add titles and labels
    plt.title('mrk (Cash Burn Runway) -  (Zero Revenue Scenario) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Cash Burn Runway) -  (Zero Revenue Scenario)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 166.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
