import sys
import matplotlib.pyplot as plt

def generate_chart(output_path):
    # Hardcoded data
    years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    values = [-0.0571894110074026, 0.0072391718877689, 0.0417869815447439, -0.040673836133174, -0.110496156229952, 0.0362796172082416, 0.1497887711994122, 0.0626594512223683, 0.0374176043412337]

    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(years, values, marker='o', linestyle='-', color='b', label='(Sustainable Growth Rate, SGR)')

    # Add titles and labels
    plt.title('cvx (Sustainable Growth Rate, SGR) (2016-2024)')
    plt.xlabel("Fiscal Year")
    plt.ylabel('(Sustainable Growth Rate, SGR)')
    plt.grid(True, axis='y')
    plt.legend()

    # Save the plot to the specified output path
    plt.savefig(output_path)
    print(f"Chart saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python 75.py <output_path>")
        sys.exit(1)
    
    output_path = sys.argv[1]
    generate_chart(output_path)
