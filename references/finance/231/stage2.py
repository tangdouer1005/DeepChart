import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [0.0223874056900658, 0.0702946067204216, 0.0420822556555316, 0.0454959889277351, -0.262215540392943, 0.0150944526389086, 0.0125508515437789, 0.0374863820936912, 0.0402313087561524]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Internal Growth Rate, IGR)')

    # Add titles and labels
    plt.title('tmus (Internal Growth Rate, IGR) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Internal Growth Rate, IGR)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 231.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
