import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import matplotlib.transforms as transforms
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def get_data():
    """
    Returns the dataframe constructed from the provided source data.
    """
    csv_data = """sample|C1|C2|C3|K21|K22|K23|K101|K102|K103|K501|K502|K503
label|0|0|0|1|1|1|2|2|2|3|3|3
Pyruvate|0.223058|0.210762|0.149665|0.379206|0.293885|0.464718|0.442063|0.254092|0.40376|0.614279|0.562326|0.429538
Citrate|0.258809|0.309936|0.356968|0.30788|0.325941|0.289485|0.296881|0.274078|0.282906|0.279333|0.314928|0.289988
Glutamate|0.367758|0.344181|0.376461|0.347516|0.379106|0.342397|0.314315|0.281335|0.302929|0.284958|0.332328|0.30411
Succinate|0.382252|0.328351|0.398149|0.360708|0.386626|0.357401|0.335758|0.298984|0.327873|0.297441|0.350486|0.323474
Fumarate|0.097648|0.104257|0.106706|0.0843699|0.0890736|0.0680718|0.0878835|0.0631375|0.0819516|0.0646776|0.0777998|0.0697304
Malate|0.0979276|0.11186|0.113111|0.0915563|0.0970604|0.069992|0.0949667|0.0724992|0.0904031|0.0690075|0.0817405|0.0725173
Aspartic acid|0.140544|0.158885|0.161802|0.132497|0.130524|0.105984|0.137745|0.0969118|0.124096|0.10052|0.12154|0.103243"""
    
    # Read CSV with pipe separator
    df = pd.read_csv(io.StringIO(csv_data), sep='|')
    
    # Set 'sample' as index
    df.set_index('sample', inplace=True)
    
    return df

def confidence_ellipse(x, y, ax, n_std=2.0, facecolor='none', **kwargs):
    """
    Create a plot of the covariance confidence ellipse of *x* and *y*.
    """
    if x.size != y.size:
        raise ValueError("x and y must be the same size")

    cov = np.cov(x, y)
    pearson = cov[0, 1]/np.sqrt(cov[0, 0] * cov[1, 1])
    
    # Using a special case to obtain the eigenvalues of this
    # 2d symmetric matrix
    ell_radius_x = np.sqrt(1 + pearson)
    ell_radius_y = np.sqrt(1 - pearson)
    
    ellipse = Ellipse((0, 0), width=ell_radius_x * 2, height=ell_radius_y * 2,
                      facecolor=facecolor, **kwargs)

    # Calculating the standard deviation of x from
    # the squareroot of the variance and multiplying
    # with the given number of standard deviations.
    scale_x = np.sqrt(cov[0, 0]) * n_std
    mean_x = np.mean(x)

    # calculating the standard deviation of y ...
    scale_y = np.sqrt(cov[1, 1]) * n_std
    mean_y = np.mean(y)

    transf = transforms.Affine2D() \
        .rotate_deg(45) \
        .scale(scale_x, scale_y) \
        .translate(mean_x, mean_y)

    ellipse.set_transform(transf + ax.transData)
    return ax.add_patch(ellipse)

def main():
    # 1. Handle Output Filename
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]

    # 2. Process Data
    df_raw = get_data()
    
    # Extract labels (first row)
    labels = df_raw.loc['label'].astype(int)
    
    # Extract features (metabolites), transpose so rows=samples, cols=features
    features = df_raw.drop('label').T.astype(float)
    
    # Standardize the data (Z-score normalization)
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)
    
    # 3. Perform PCA
    pca = PCA(n_components=2)
    principal_components = pca.fit_transform(features_scaled)
    
    # Create a DataFrame for plotting
    pca_df = pd.DataFrame(data=principal_components, columns=['PC1', 'PC2'])
    pca_df['label'] = labels.values
    
    # Note: PCA sign is arbitrary. To match the visual orientation of the provided image:
    # PC1 needs to be inverted (based on visual comparison of data points)
    # PC2 needs to be inverted
    pca_df['PC1'] = pca_df['PC1'] * -1
    pca_df['PC2'] = pca_df['PC2'] * -1

    # 4. Plotting
    fig, ax = plt.subplots(figsize=(6, 5))
    
    # Define styling based on the image
    # Groups: 0=Control, 1=2uM, 2=10uM, 3=50uM
    groups = [
        {'label': 0, 'name': 'Control', 'color': '#6495ED'},         # Cornflower Blue
        {'label': 1, 'name': '2 µM ketamine', 'color': '#77DD77'},   # Pastel Green
        {'label': 2, 'name': '10 µM ketamine', 'color': '#BA55D3'},  # Medium Orchid
        {'label': 3, 'name': '50 µM ketamine', 'color': '#EB5757'}   # Salmon Red
    ]
    
    # Plot points and ellipses
    for group in groups:
        subset = pca_df[pca_df['label'] == group['label']]
        
        # Draw Ellipse (Confidence Interval)
        # Using n_std=2.0 approximates the 95% confidence region often used in such plots
        confidence_ellipse(subset['PC1'], subset['PC2'], ax, n_std=2.5, 
                           facecolor=group['color'], alpha=0.3, edgecolor='none')
        
        # Draw Scatter Points
        ax.scatter(subset['PC1'], subset['PC2'], c=group['color'], s=80, 
                   label=group['name'], zorder=10, edgecolors='none')

    # 5. Styling Details
    
    # Axis Labels
    ax.set_xlabel('PC1 (72.36%)', fontsize=14, fontname='Arial')
    ax.set_ylabel('PC2 (12.52%)', fontsize=14, fontname='Arial')
    
    # Axis Ticks
    ax.tick_params(axis='both', which='major', labelsize=14, direction='in')
    
    # Set Limits to match image roughly
    ax.set_xlim(-6, 8)
    ax.set_ylim(-4, 3)
    
    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Legend
    # The image has a 2-column legend
    handles, labels = ax.get_legend_handles_labels()
    # Reorder handles to match image layout: 
    # Col 1: Control, 2uM. Col 2: 10uM, 50uM.
    # Current order is 0, 1, 2, 3. 
    # We want: 0 (Control), 2 (10uM) -- wait, image is:
    # Left Col: Control, 2uM
    # Right Col: 10uM, 50uM
    # Matplotlib fills columns first. So order should be: Control, 2uM, 10uM, 50uM
    # With ncol=2, it goes:
    # Item 0   Item 2
    # Item 1   Item 3
    # So we need list: [Control, 2uM, 10uM, 50uM] -> [0, 1, 2, 3]
    # If we pass this to legend(ncol=2), it plots:
    # Control   10uM
    # 2uM       50uM
    # This matches the visual exactly.
    
    leg = ax.legend(handles, labels, loc='upper right', ncol=2, frameon=False, 
                    fontsize=12, handletextpad=0.1, columnspacing=1.0)
    
    # Add the figure label 'h'
    # Placed in figure coordinates to be outside the axes
    fig.text(0.02, 0.92, 'h', fontsize=20, fontweight='bold', fontname='Arial')

    plt.tight_layout()
    
    # Save
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_file}")

if __name__ == "__main__":
    main()