import json

def save_data(output_filename):
    # ---------------------------------------------------------
    # 1. Data Preparation
    # ---------------------------------------------------------
    # Data extracted directly from the provided source table columns.
    # Mapping based on headers:
    # Col 1: Intranodal, WT, Vehicle
    # Col 2: Intranodal, WT, viFSP1
    # Col 3: Intranodal, FSP1 KO, Vehicle
    # Col 4: Intranodal, FSP1 KO, viFSP1
    # Col 5: Subcutaneous, WT, Vehicle
    # Col 6: Subcutaneous, WT, viFSP1
    # Col 7: Subcutaneous, FSP1 KO, Vehicle
    # Col 8: Subcutaneous, FSP1 KO, viFSP1

    raw_data = {
        ('Intranodal', 'WT', 'Vehicle'): [
            1.226013991989289, 0.9137241501300842, 1.2593749169413784, 
            1.3181705861405943, 0.46320361183478104, 1.1517888949997317, 
            0.667723847964141
        ],
        ('Intranodal', 'WT', 'viFSP1'): [
            0.26919108005571524, 0.4740587435691917, 0.03158430764694863, 
            0.1172567421392968, 0.030024832456880545, 0.28110033805784285, 
            0.5876161736753397, 0.18387347551958827, 0.5379202396120939, 
            0.52758427493463
        ],
        ('Intranodal', 'Fsp1 KO', 'Vehicle'): [
            0.7439762627007868, 0.8433562867119107, 0.03158430764694863, 
            0.03158430764694863, 0.03158430764694863, 0.03158430764694863, 
            0.03158430764694863, 0.03158430764694863, 0.03158430764694863
        ],
        ('Intranodal', 'Fsp1 KO', 'viFSP1'): [
            0.6323691635918379, 0.10994497491902819, 0.09440549555672946, 
            0.6810129454065946, 0.25673107068899403, 0.03158430764694863, 
            0.09960901024156425, 0.03656278413979891
        ],
        ('Subcutaneous', 'WT', 'Vehicle'): [
            0.47505561344221175, 0.6275176971758019, 0.8627640623994038, 
            1.07262093290512, 1.5483034001667353, 0.9886672051858337, 
            1.425071088724893
        ],
        ('Subcutaneous', 'WT', 'viFSP1'): [
            0.32442302364590364, 0.5469331491498078, 0.5017894606485539, 
            0.48018662260755507, 0.9407594871142966, 0.29633971719901214, 
            1.6253259886079303, 0.789999228515666
        ],
        ('Subcutaneous', 'Fsp1 KO', 'Vehicle'): [
            1.6476616455742605, 0.31997887263705566, 0.4379039919663494, 
            1.302964816119536, 0.5985279422324202, 1.058976968000909, 
            1.7172092256394702, 1.3238654757477606
        ],
        ('Subcutaneous', 'Fsp1 KO', 'viFSP1'): [
            1.5255694165371587, 1.1622329419433417, 0.6292029253664596, 
            0.806938325207822, 1.9126420748587845
        ]
    }

    # Convert to Long Format List of Dicts
    rows = []
    for (loc, geno, treat), values in raw_data.items():
        for v in values:
            rows.append({
                'Location': loc,
                'Genotype': geno,
                'Treatment': treat,
                'Value': v,
                # Create a combined group for x-axis positioning
                'Group': f"{loc}\n{geno}" 
            })
    
    with open(output_filename, 'w') as f:
        json.dump({"scr_data": rows, "der_data": {}}, f, indent=4)

if __name__ == "__main__":
    output_file = 'bench/ground_truth_code/nature_1_output/112.json'
    save_data(output_file)
