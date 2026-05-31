import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [3.0526871300524268, 3.1896163880554886, 1.6268470046943753, 1.717667488279519, 2.9338503032316, 3.426986027047693, 2.975324036947145, 1.2312542902327732, 0.8637785820157824]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Reinvestment Rate)')

    # Add titles and labels
    plt.title('tmus (Reinvestment Rate) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Reinvestment Rate)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 240.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
