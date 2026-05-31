import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.0405262605409566, -0.1872038562650635, 0.0859160912940166, 0.950271800315224, 0.8502394374734801, 0.3412809148610199, 0.2760201742320036, 0.1093377276313271, 0.4734497676654383]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Sustainable Growth Rate, SGR)')

    # Add titles and labels
    plt.title('lly (Sustainable Growth Rate, SGR) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Sustainable Growth Rate, SGR)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 133.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
