import sys
import io
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np # 确保导入numpy

def generate_chart(output_filename):
    # 1. Source Data (保持不变)
    csv_data = """
| Task               |    CONCH |   Virchow2 |   BiomedCLIP |   DinoSSLPath |   Phikon |   Virchow |   ProvGigaPath |   Panakeia* |   H-optimus-0 |   CTransPath |   Hibou-L |      UNI |   Hibou-B |     PLIP |    Kaiko |
|:-------------------|---------:|-----------:|-------------:|--------------:|---------:|----------:|---------------:|------------:|--------------:|-------------:|----------:|---------:|----------:|---------:|---------:|
| BERN STAD N STATUS | 0.71867  |   0.598758 |     0.622676 |      0.627987 | 0.574063 |  0.60613  |       0.498635 |    0.564809 |      0.570485 |     0.56206  |  0.583819 | 0.573323 |  0.560453 | 0.587603 | 0.583129 |
| KIEL STAD N STATUS | 0.631522 |   0.616924 |     0.631596 |      0.632616 | 0.614332 |  0.598649 |       0.657943 |    0.608062 |      0.577523 |     0.630989 |  0.5934   | 0.629206 |  0.632883 | 0.625878 | 0.608752 |
| KIEL STAD M STATUS | 0.544224 |   0.526274 |     0.492196 |      0.506792 | 0.591025 |  0.51302  |       0.534376 |    0.525071 |      0.537186 |     0.510906 |  0.53073  | 0.504209 |  0.465878 | 0.479537 | 0.515843 |
| IEO BRCA N STATUS  | 0.575481 |   0.55847  |     0.592211 |      0.573873 | 0.564433 |  0.573822 |       0.549081 |    0.562549 |      0.54941  |     0.568043 |  0.558692 | 0.557326 |  0.565293 | 0.595723 | 0.558933 |
| CPTAC CRC N STATUS | 0.630026 |   0.615013 |     0.640146 |      0.594841 | 0.559854 |  0.568056 |       0.616402 |    0.574471 |      0.588294 |     0.572024 |  0.573611 | 0.526455 |  0.541865 | 0.54914  | 0.51918  |
| DACHS CRC N STATUS | 0.648021 |   0.632989 |     0.625073 |      0.62096  | 0.609028 |  0.594649 |       0.622209 |    0.6141   |      0.597321 |     0.594246 |  0.573889 | 0.585531 |  0.595719 | 0.571071 | 0.531017 |
| DACHS CRC M STATUS | 0.675269 |   0.697332 |     0.632462 |      0.662344 | 0.615553 |  0.65678  |       0.63174  |    0.657834 |      0.680039 |     0.600907 |  0.613861 | 0.629181 |  0.628469 | 0.563312 | 0.563876 |
| Average            | 0.631888 |   0.606537 |     0.605194 |      0.602773 | 0.589755 |  0.587301 |       0.587198 |    0.586699 |      0.585751 |     0.577025 |  0.575429 | 0.572176 |  0.57008  | 0.567466 | 0.55439  |
"""

    # 2. Data Processing
    # Read markdown table
    df = pd.read_csv(io.StringIO(csv_data), sep="|", skipinitialspace=True)
    
    # Clean column names (remove whitespace and empty columns from markdown pipes)
    df.columns = [c.strip() for c in df.columns]
    df = df.drop(columns=[c for c in df.columns if c == '' or 'Unnamed' in c])

    # 【新增关键步骤 1】过滤掉 Markdown 的分隔行
    # 这一行在 'Task' 列中通常包含 '---' 符号
    # 我们保留不包含 '---' 的行
    df = df[~df['Task'].str.contains('---', na=False)]
    
    # Set index
    df['Task'] = df['Task'].str.strip()
    df = df.set_index('Task')

    # 【新增关键步骤 2】将数据转换为浮点数类型
    # 过滤掉脏行后，剩下的都是数字字符串，需要转成真正的数字才能计算
    df = df.astype(float)
    
    # Rename rows to match the specific casing and format in the target image
    # Source: "BERN STAD N STATUS" -> Target: "Bern STAD N-status"
    rename_map = {
        'BERN STAD N STATUS': 'Bern STAD N-status',
        'KIEL STAD N STATUS': 'Kiel STAD N-status',
        'KIEL STAD M STATUS': 'Kiel STAD M-status',
        'IEO BRCA N STATUS': 'IEO BRCA N-status',
        'CPTAC CRC N STATUS': 'CPTAC CRC N-status',
        'DACHS CRC N STATUS': 'DACHS CRC N-status',
        'DACHS CRC M STATUS': 'DACHS CRC M-status',
        'Average': 'Average'
    }
    df = df.rename(index=rename_map)

    # Reorder rows to match the target image exactly (Top to Bottom)
    desired_order = [
        'DACHS CRC M-status',
        'Kiel STAD N-status',
        'DACHS CRC N-status',
        'Bern STAD N-status',
        'CPTAC CRC N-status',
        'IEO BRCA N-status',
        'Kiel STAD M-status',
        'Average'
    ]
    df = df.reindex(desired_order)
 
    # 3. Color Normalization Logic (后面的代码不需要修改)
    # The chart uses row-wise normalization for the color scale. 
    # ...
    df_norm = df.apply(lambda x: (x - x.min()) / (x.max() - x.min()), axis=1)
    
    # ... (剩余的绘图代码保持不变) ...
    
    # Set up the figure
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans']
    
    fig, ax = plt.subplots(figsize=(12, 6.5))

    # Define custom purple colormap to match the image
    cmap = mcolors.LinearSegmentedColormap.from_list("custom_purple", ["#dcd0d9", "#4a2e55"])

    # Create Heatmap
    sns.heatmap(
        data=df_norm,
        annot=df,
        fmt=".2f",
        cmap=cmap,
        cbar=False, 
        linewidths=1,
        linecolor='white',
        ax=ax,
        annot_kws={"size": 11}
    )

    # 5. Styling
    ax.set_title("Prognosis tasks", fontsize=22, pad=15, color='black')
    ax.text(-0.18, 1.05, "e", transform=ax.transAxes, fontsize=28, fontweight='bold', va='bottom', ha='left')
    ax.set_xlabel("")
    plt.xticks(rotation=55, ha='right', rotation_mode='anchor', fontsize=11)
    ax.set_ylabel("")
    plt.yticks(rotation=0, fontsize=11)
    plt.tight_layout()
    plt.subplots_adjust(top=0.88, left=0.20, bottom=0.20)

    # 6. Save Output
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    generate_chart(output_file)