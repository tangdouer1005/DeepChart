import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [3.5675573083091456, 4.989704113241103, 0.9073418700849712, 0.5083245763149598, 2.3154979053803126, 3.6649097206016688, 1.387328543435663, 1.7865673411575853, 1.0589680475300542]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.bar(years, values, color='b', label='(Reinvestment Rate)')

    # Add titles and labels
    plt.title('amzn (Reinvestment Rate) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Reinvestment Rate)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 40.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
