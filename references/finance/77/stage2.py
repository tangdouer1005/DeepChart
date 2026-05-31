import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [15.641857862339116, 11.132613723978412, 22.247271283984915, 12.540341848924829, 12.563517305893358, 2.0356111645813284, 6.214254328148344, 19.905882352941177, 14.07576543850545]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Cash Burn Runway) -  (Zero Revenue Scenario)')

    # Add titles and labels
    plt.title('cvx (Cash Burn Runway) -  (Zero Revenue Scenario) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Cash Burn Runway) -  (Zero Revenue Scenario)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 77.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
