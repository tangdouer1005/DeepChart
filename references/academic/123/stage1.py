import json
import sys
import os

def compute_data(output_filename):
    # Source Data
    # Mapped directly from the provided Markdown table.
    data = {
        "Globe": {
            "Energy": [
                ("Transport", 834432),
                ("Processing", 496434),
                ("Packaging", 956519),
                ("Retail", 313028),
                ("Consumption", 456845),
                ("Production", 729419)
            ],
            "Industry": [
                ("Packaging", 20982.2),
                ("Processing", 576.842),
                ("Production", 286377),
                ("Retail", 402981)
            ],
            "Waste": [
                ("End of Life", 1.61649e+06),
                ("Processing", 124474)
            ],
            "Land based": [
                ("Production", 6.04419e+06),
                ("LULUC", 5.66302e+06)
            ]
        },
        "Industrialized": {
            "Energy": [
                ("Transport", 481391),
                ("Processing", 225195),
                ("Packaging", 276552),
                ("Retail", 211656),
                ("Consumption", 127937),
                ("Production", 286551)
            ],
            "Industry": [
                ("Packaging", 10467.4),
                ("Processing", 235.675),
                ("Production", 128630),
                ("Retail", 385620)
            ],
            "Waste": [
                ("End of Life", 458636),
                ("Processing", 37152.5)
            ],
            "Land based": [
                ("Production", 1.62167e+06),
                ("LULUC", 681299)
            ]
        },
        "Developing": {
            "Energy": [
                ("Transport", 353041),
                ("Processing", 271239),
                ("Packaging", 679967),
                ("Retail", 101372),
                ("Consumption", 328908),
                ("Production", 442868)
            ],
            "Industry": [
                ("Packaging", 10514.8),
                ("Processing", 341.167),
                ("Production", 157747),
                ("Retail", 17360.2)
            ],
            "Waste": [
                ("End of Life", 1.15785e+06),
                ("Processing", 87321.7)
            ],
            "Land based": [
                ("Production", 4.42252e+06),
                ("LULUC", 4.98172e+06)
            ]
        }
    }
    
    categories = ["Energy", "Industry", "Waste", "Land based"]
    regions = ["Globe", "Industrialized", "Developing"]

    data_to_save = {
        "scr_data": {
            "data": data,
            "categories": categories,
            "regions": regions
        },
        "der_data": {}
    }
    
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    
    with open(output_filename, 'w') as f:
        json.dump(data_to_save, f, indent=4)
        
    print(f"Data saved to {output_filename}")

if __name__ == "__main__":
    output_file = "bench/ground_truth_code/nature_1_output/123.json"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    compute_data(output_file)
