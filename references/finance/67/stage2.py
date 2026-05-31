import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [10.42249032551787, 15.763042746549983, 11.382100010616838, 15.22185037244953, 15.999548379812577, 12.052545155993432, 9.198484028153764, 11.617827084927312, 9.174377224199288]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Cash Burn Runway) -  (Zero Revenue Scenario)')

    # Add titles and labels
    plt.title('csco (Cash Burn Runway) -  (Zero Revenue Scenario) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Cash Burn Runway) -  (Zero Revenue Scenario)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 67.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
