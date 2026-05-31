import sys
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm, colors
from matplotlib.gridspec import GridSpec

# -----------------------------------------------------------------------------
# 1. Source Data Embedding
# -----------------------------------------------------------------------------
csv_data = """| Fig. 3m                                   | Unnamed: 1                              | Unnamed: 2         | Unnamed: 3                               | Unnamed: 4         | Unnamed: 5         | Unnamed: 6         | Unnamed: 7         | Unnamed: 8        | Unnamed: 9         | Unnamed: 10        | Unnamed: 11        | Unnamed: 12       | Unnamed: 13        | Unnamed: 14        | Unnamed: 15        | Unnamed: 16        | Unnamed: 17        | Unnamed: 18       | Unnamed: 19        | Unnamed: 20       | Unnamed: 21        | Unnamed: 22        | Unnamed: 23        | Unnamed: 24        | Unnamed: 25       | Unnamed: 26        | Unnamed: 27        | Unnamed: 28        | Unnamed: 29        | Unnamed: 30       | Unnamed: 31        | Unnamed: 32        | Unnamed: 33        | Unnamed: 34       | Unnamed: 35        | Unnamed: 36       | Unnamed: 37        | Unnamed: 38       | Unnamed: 39        | Unnamed: 40        | Unnamed: 41        | Unnamed: 42       | Unnamed: 43        | Unnamed: 44       | Unnamed: 45       | Unnamed: 46        | Unnamed: 47        | Unnamed: 48       | Unnamed: 49       | Unnamed: 50        | Unnamed: 51        | Unnamed: 52        | Unnamed: 53        | Unnamed: 54       |
|:------------------------------------------|:----------------------------------------|:-------------------|:-----------------------------------------|:-------------------|:-------------------|:-------------------|:-------------------|:------------------|:-------------------|:-------------------|:-------------------|:------------------|:-------------------|:-------------------|:-------------------|:-------------------|:-------------------|:------------------|:-------------------|:------------------|:-------------------|:-------------------|:-------------------|:-------------------|:------------------|:-------------------|:-------------------|:-------------------|:-------------------|:------------------|:-------------------|:-------------------|:-------------------|:------------------|:-------------------|:------------------|:-------------------|:------------------|:-------------------|:-------------------|:-------------------|:------------------|:-------------------|:------------------|:------------------|:-------------------|:-------------------|:------------------|:------------------|:-------------------|:-------------------|:-------------------|:-------------------|:------------------|
| Relative viability (%)                    | nan                                     | nan                | nan                                      | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan               | nan                | nan                | nan               | nan               | nan                | nan                | nan                | nan                | nan               |
| nan                                       | NORMOXIA                                | nan                | nan                                      | HYPOXIA            | nan                | nan                | NORMOXIA           | nan               | nan                | HYPOXIA            | nan                | nan               | NORMOXIA           | nan                | nan                | HYPOXIA            | nan                | nan               | NORMOXIA           | nan               | nan                | HYPOXIA            | nan                | nan                | NORMOXIA          | nan                | nan                | HYPOXIA            | nan                | nan               | NORMOXIA           | nan                | nan                | HYPOXIA           | nan                | nan               | NORMOXIA           | nan               | nan                | HYPOXIA            | nan                | nan               | NORMOXIA           | nan               | nan               | HYPOXIA            | nan                | nan               | NORMOXIA          | nan                | nan                | HYPOXIA            | nan                | nan               |
| ML210                                     | F0Luc 1                                 | F0Luc 2            | F0Luc 3                                  | F0Luc 1            | F0Luc 2            | F0Luc 3            | LN71112-1          | LN71112-2         | LN71112-3          | LN71112 1          | LN71112 2          | LN71112 3         | LN71120 1          | LN71120 2          | LN71120 3          | LN71120 1          | LN71120 2          | LN71120 3         | LN71134 1          | LN71134 2         | LN71134 3          | LN71134 1          | LN71134 2          | LN71134 3          | LN81194 1         | LN81194 2          | LN81194 3          | LN81194 1          | LN81194 2          | LN81194 3         | LN81198 -1         | LN81198 -2         | LN81198 -3         | LN81198 1         | LN81198 2          | LN81198 3         | LN81205-1          | LN81205-2         | LN81205-3          | LN81205 1          | LN81205 2          | LN81205 3         | LN91315 1          | LN91315 2         | LN91315 3         | LN91315 1          | LN91315 2          | LN91315 3         | LN91358 1         | LN91358 2          | LN91358 3          | LN91358 1          | LN91358 2          | LN91358 3         |
| 0                                         | 103.62776025236593                      | 101.92429022082018 | 94.44794952681389                        | 99.01768172888016  | 100.55009823182712 | 100.43222003929274 | 95.39895165987187  | 101.5142690739662 | 103.08677926616191 | 107.44615384615385 | 104.12307692307691 | 88.43076923076923 | 109.05915230554263 | 94.66697717745693  | 96.27387051700047  | 100.07748934521503 | 101.47229755908563 | 98.45021309569935 | 100.53492762743865 | 97.51415984896161 | 101.95091252359975 | 101.15044247787611 | 95.30973451327434  | 103.53982300884957 | 100               | 101.82341650671785 | 107.58157389635316 | 104.66278101582013 | 100.04163197335554 | 95.2955870108243  | 102.20994475138122 | 101.47329650092081 | 96.31675874769797  | 97.26636999364273 | 104.32294977749524 | 98.41068022886205 | 101.72872340425532 | 98.73670212765958 | 99.53457446808511  | 103.40346534653465 | 103.96039603960396 | 92.63613861386138 | 106.62020905923345 | 98.46689895470382 | 94.91289198606272 | 101.81700194678783 | 100.84360804672293 | 97.33939000648931 | 98.57433808553972 | 101.42566191446029 | 100.00000000000001 | 101.80115273775213 | 100.72046109510086 | 97.47838616714697 |
| 2.5                                       | 91.32492113564669                       | 85.3627760252366   | 93.69085173501577                        | 105.50098231827113 | 109.98035363457763 | 116.11001964636543 | 75.13104251601631  | 72.51019219569015 | 64.47291788002329  | 97.84615384615385  | 102.46153846153848 | 86.95384615384614 | 54.70423847228692  | 46.949231485794144 | 40.03260363297625  | 88.10538550949245  | 91.35993800852384  | 95.07942657884541 | 63.62492133417245  | 69.00566393958465 | 63.53052234109504  | 106.06194690265488 | 109.91150442477876 | 90.00000000000001  | 56.62188099808061 | 58.54126679462572  | 48.368522072936656 | 93.42214820982514  | 92.17318900915902  | 73.06411323896752 | 66.48250460405157  | 66.11418047882135  | 53.95948434622467  | 86.01398601398601 | 92.87984742530196  | 87.3490146217419  | 47.87234042553192  | 58.24468085106383 | 47.87234042553192  | 75.18564356435643  | 86.13861386138613  | 76.29950495049503 | 57.2822299651568   | 61.46341463414634 | 56.86411149825785 | 95.97663854639845  | 94.02985074626866  | 84.29591174561973 | 54.37881873727089 | 53.9714867617108   | 54.582484725050925 | 90.99423631123918  | 97.91066282420749  | 93.37175792507205 |
| 5                                         | 79.77917981072555                       | 74.10094637223975  | 88.67507886435331                        | 100.43222003929274 | 110.80550098231828 | 108.44793713163065 | 67.61793826441468  | 51.19394292370413 | 49.446709376820024 | 100.43076923076924 | 89.72307692307693  | 87.32307692307693 | 43.87517466231952  | 45.132743362831874 | 39.40381928272007  | 81.13134444013949  | 92.40604416892678  | 89.73266175900814 | 58.14977973568283  | 51.82504719949655 | 50.503461296412844 | 86.81415929203541  | 88.00884955752213  | 94.38053097345133  | 52.68714011516315 | 43.76199616122841  | 43.66602687140115  | 80.30807660283097  | 73.81348875936717  | 66.44462947543714 | 46.77716390423572  | 48.43462246777164  | 44.383057090239404 | 71.13795295613477 | 75.33375715193897  | 76.85950413223142 | 49.06914893617022  | 49.66755319148936 | 46.675531914893625 | 72.21534653465345  | 66.64603960396039  | 72.21534653465345 | 51.01045296167247  | 53.10104529616724 | 42.02090592334495 | 84.10123296560677  | 84.87994808565868  | 75.53536664503571 | 49.08350305498982 | 44.806517311608964 | 31.568228105906318 | 87.7521613832853   | 89.69740634005763  | 92.29106628242073 |
| Normalized to B16-F0  (DMSO/control)      | nan                                     | nan                | nan                                      | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan               | nan                | nan                | nan               | nan               | nan                | nan                | nan                | nan                | nan               |
| nan                                       | nan                                     | nan                | nan                                      | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan               | nan                | nan                | nan               | nan               | nan                | nan                | nan                | nan                | nan               |
| nan                                       | nan                                     | nan                | nan                                      | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan               | nan                | nan                | nan               | nan               | nan                | nan                | nan                | nan                | nan               |
| ML-210 5 uM                               | B16-F0 - 21%O2                          | B16-F0 - 1%O2      | LN7 1112AR - 21%O2                       | LN7 1112AR- 1%O2   | LN7 1120BL - 21%O2 | LN7 1120BL - 1%O2  | LN7 1134BL - 21%O2 | LN7 1134BL- 1%O2  | LN8 1194BR - 21%O2 | LN8 1194BR - 1%O2  | LN8 1198AR - 21%O2 | LN8 1198AR - 1%O2 | LN8 1205BL - 21%O2 | LN8 1205BL - 1%O2  | LN9 1315BL - 21%O2 | LN9 1315BL- 1%O2   | LN9 1358IR - 21%O2 | LN9 1358IR - 1%O2 | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan               | nan                | nan                | nan               | nan               | nan                | nan                | nan                | nan                | nan               |
| n1                                        | 79.77917981072555                       | 100.43222003929274 | 67.61793826441468                        | 100.43076923076924 | 43.87517466231952  | 81.13134444013949  | 58.14977973568283  | 86.81415929203541 | 52.68714011516315  | 86.81415929203541  | 46.77716390423572  | 80.30807660283097 | 49.06914893617022  | 71.13795295613477  | 51.01045296167247  | 66.64603960396039  | 49.08350305498982  | 87.7521613832853  | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan               | nan                | nan                | nan               | nan               | nan                | nan                | nan                | nan                | nan               |
| n2                                        | 74.10094637223975                       | 110.80550098231828 | 51.19394292370413                        | 89.72307692307693  | 45.132743362831874 | 92.40604416892678  | 51.82504719949655  | 88.00884955752213 | 43.76199616122841  | 88.00884955752213  | 48.43462246777164  | 73.81348875936717 | 49.66755319148936  | 75.33375715193897  | 53.10104529616724  | 72.21534653465345  | 44.806517311608964 | 89.69740634005763 | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan               | nan                | nan                | nan               | nan               | nan                | nan                | nan                | nan                | nan               |
| n3                                        | 88.67507886435331                       | 108.44793713163065 | 49.446709376820024                       | 87.32307692307693  | 39.40381928272007  | 89.73266175900814  | 50.503461296412844 | 94.38053097345133 | 43.66602687140115  | 94.38053097345133  | 44.383057090239404 | 66.44462947543714 | 46.675531914893625 | 76.85950413223142  | 42.02090592334495  | 84.10123296560677  | 31.568228105906318 | 92.29106628242073 | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan               | nan                | nan                | nan               | nan               | nan                | nan                | nan                | nan                | nan               |
| nan                                       | nan                                     | nan                | nan                                      | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan               | nan                | nan                | nan               | nan               | nan                | nan                | nan                | nan                | nan               |
| nan                                       | nan                                     | nan                | nan                                      | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan               | nan                | nan                | nan               | nan               | nan                | nan                | nan                | nan                | nan               |
| nan                                       | nan                                     | nan                | nan                                      | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan               | nan                | nan                | nan               | nan               | nan                | nan                | nan                | nan                | nan               |
| nan                                       | nan                                     | nan                | nan                                      | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan               | nan                | nan                | nan               | nan               | nan                | nan                | nan                | nan                | nan               |
| Statistical test                          | nan                                     | nan                | nan                                      | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan               | nan                | nan                | nan               | nan               | nan                | nan                | nan                | nan                | nan               |
| Table Analyzed                            | Fig. 3m - ML-210 Reorganized 5 uM final | nan                | Šídák's multiple comparisons test        | Mean diff.         | 95.00% CI of diff. | Below threshold?   | Summary            | Adjusted P Value  | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan               | nan                | nan                | nan               | nan               | nan                | nan                | nan                | nan                | nan               |
| Data sets analyzed                        | A-R                                     | nan                | B16-F0 - 21%O2 vs. B16-F0 - 1%O2         | -25.71             | -39.80 to -11.62   | Yes                | ****               | 4.3779488301e-05  | A-B                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan               | nan                | nan                | nan               | nan               | nan                | nan                | nan                | nan                | nan               |
| Distribution assumption                   | Normal (Gaussian)                       | nan                | LN7 1112AR - 21%O2 vs. LN7 1112AR- 1%O2  | -36.41             | -50.49 to -22.32   | Yes                | ****               | 4.8904949e-08     | C-D                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan               | nan                | nan                | nan               | nan               | nan                | nan                | nan                | nan                | nan               |
| nan                                       | nan                                     | nan                | LN7 1120BL - 21%O2 vs. LN7 1120BL - 1%O2 | -44.95             | -59.04 to -30.86   | Yes                | ****               | 2.96147e-10       | E-F                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan               | nan                | nan                | nan               | nan               | nan                | nan                | nan                | nan                | nan               |
| ANOVA summary                             | nan                                     | nan                | LN7 1134BL - 21%O2 vs. LN7 1134BL- 1%O2  | -36.24             | -50.33 to -22.15   | Yes                | ****               | 5.4145029e-08     | G-H                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan               | nan                | nan                | nan               | nan               | nan                | nan                | nan                | nan                | nan               |
| F                                         | 38.45                                   | nan                | LN8 1194BR - 21%O2 vs. LN8 1194BR - 1%O2 | -43.03             | -57.12 to -28.94   | Yes                | ****               | 9.03365e-10       | I-J                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan               | nan                | nan                | nan               | nan               | nan                | nan                | nan                | nan                | nan               |
| P value                                   | <0.000000000000001                      | nan                | LN8 1198AR - 21%O2 vs. LN8 1198AR - 1%O2 | -26.99             | -41.08 to -12.90   | Yes                | ****               | 1.923302805e-05   | K-L                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan               | nan                | nan                | nan               | nan               | nan                | nan                | nan                | nan                | nan               |
| P value summary                           | ****                                    | nan                | LN8 1205BL - 21%O2 vs. LN8 1205BL - 1%O2 | -25.97             | -40.06 to -11.88   | Yes                | ****               | 3.6981560674e-05  | M-N                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan               | nan                | nan                | nan               | nan               | nan                | nan                | nan                | nan                | nan               |
| Significant diff. among means (P < 0.05)? | Yes                                     | nan                | LN9 1315BL - 21%O2 vs. LN9 1315BL- 1%O2  | -25.61             | -39.70 to -11.52   | Yes                | ****               | 4.6683616809e-05  | O-P                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan               | nan                | nan                | nan               | nan               | nan                | nan                | nan                | nan                | nan               |
| R squared                                 | 0.9478                                  | nan                | LN9 1358IR - 21%O2 vs. LN9 1358IR - 1%O2 | -48.09             | -62.18 to -34.01   | Yes                | ****               | 5.0104e-11        | Q-R                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan                | nan               | nan                | nan                | nan                | nan               | nan                | nan               | nan               | nan                | nan                | nan               | nan               | nan                | nan                | nan                | nan                | nan               |"""

# -----------------------------------------------------------------------------
# 2. Data Processing
# -----------------------------------------------------------------------------

def parse_data(csv_string):
    # Read the markdown table
    # Use header=None to treat all lines as data initially
    # dtype=str to ensure we read everything as text first to avoid conversion errors during read
    df = pd.read_csv(io.StringIO(csv_string), sep="|", header=None, dtype=str)
    
    # Drop the first and last columns which are empty due to leading/trailing pipes
    # Check if column 0 is all NaN or empty strings, same for last
    if df.iloc[:, 0].isna().all() or (df.iloc[:, 0].str.strip() == '').all():
        df = df.iloc[:, 1:]
    if df.iloc[:, -1].isna().all() or (df.iloc[:, -1].str.strip() == '').all():
        df = df.iloc[:, :-1]
        
    # Reset columns to range index for easier handling
    df.columns = range(df.shape[1])
    
    # Find the row index for the data "0", "2.5", "5"
    # Column 0 should contain these values
    # We look for the row where column 0 is exactly "0" (string)
    col0 = df[0].str.strip()
    
    try:
        # Find the first row where the first column is '0'
        start_idx = col0[col0 == '0'].index[0]
    except IndexError:
        raise ValueError("Could not find the data row starting with '0'")
        
    # Extract the 3 rows of data (0, 2.5, 5)
    heatmap_rows = df.iloc[start_idx : start_idx + 3, :].copy()
    
    # Set index (Concentration)
    heatmap_rows.set_index(0, inplace=True)
    heatmap_rows.index = [0.0, 2.5, 5.0]
    
    # The remaining columns are the data points.
    # Convert to float
    data_cols = heatmap_rows.astype(float)
    
    # Calculate means
    # Structure: 3 cols Normoxia, 3 cols Hypoxia per cell line.
    # Total 9 cell lines.
    
    cell_lines_map = [
        ("B16-F0", 0),
        ("LN7-1112AR", 6),
        ("LN7-1120BL", 12),
        ("LN7-1134BL", 18),
        ("LN8-1194BR", 24),
        ("LN8-1198AR", 30),
        ("LN8-1205BL", 36),
        ("LN9-1315BL", 42),
        ("LN9-1358IR", 48)
    ]
    
    processed_data = {}
    
    for name, start_col in cell_lines_map:
        # Columns are 0-indexed relative to data_cols
        # Normoxia: start_col to start_col+3
        norm_vals = data_cols.iloc[:, start_col:start_col+3].mean(axis=1).values
        # Hypoxia: start_col+3 to start_col+6
        hyp_vals = data_cols.iloc[:, start_col+3:start_col+6].mean(axis=1).values
        
        processed_data[name] = {
            '21': norm_vals,
            '1': hyp_vals
        }

    # --- Extract P-values ---
    p_values = {}
    
    # Find "Statistical test" row
    stat_rows = df[df[0].str.contains("Statistical test", na=False)]
    if not stat_rows.empty:
        stat_start_idx = stat_rows.index[0]
        stat_df = df.iloc[stat_start_idx:, :]
        
        comp_map = {
            "B16-F0": "B16-F0",
            "LN7 1112AR": "LN7-1112AR",
            "LN7 1120BL": "LN7-1120BL",
            "LN7 1134BL": "LN7-1134BL",
            "LN8 1194BR": "LN8-1194BR",
            "LN8 1198AR": "LN8-1198AR",
            "LN8 1205BL": "LN8-1205BL",
            "LN9 1315BL": "LN9-1315BL",
            "LN9 1358IR": "LN9-1358IR"
        }
        
        for idx, row in stat_df.iterrows():
            comp_str = str(row[3])
            p_val_str = str(row[8])
            
            if "vs." in comp_str:
                for key, display_name in comp_map.items():
                    if key in comp_str:
                        try:
                            p_val = float(p_val_str.strip())
                            p_values[display_name] = p_val
                        except ValueError:
                            pass
                        break
    
    return processed_data, p_values

# -----------------------------------------------------------------------------
# 3. Plotting
# -----------------------------------------------------------------------------

def format_p_value(p):
    # Format as scientific notation: 4.4 x 10^-5
    s = "{:.1e}".format(p)
    base, exponent = s.split('e')
    exponent = int(exponent)
    return r"$P = {} \times 10^{{{}}}$".format(base, exponent)

def create_chart(data, p_values, output_path):
    # Setup layout
    # 1 row, 2 columns (Left for B16-F0, Right for others) + Colorbar
    # Width ratios: 1 (B16) : 8 (Others) : 0.5 (Cbar)
    
    fig = plt.figure(figsize=(12, 5))
    gs = GridSpec(1, 3, width_ratios=[1.2, 9, 0.4], wspace=0.1)
    
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1])
    cbar_ax = fig.add_subplot(gs[2])
    
    # Prepare data matrices
    # Rows: 0, 2.5, 5 (3 rows)
    # Cols: 2 per cell line
    
    cell_lines_order = [
        "B16-F0", "LN7-1112AR", "LN7-1120BL", "LN7-1134BL", 
        "LN8-1194BR", "LN8-1198AR", "LN8-1205BL", "LN9-1315BL", "LN9-1358IR"
    ]
    
    # Left Plot Data (B16-F0)
    left_matrix = np.array([
        data["B16-F0"]['21'],
        data["B16-F0"]['1']
    ]).T # Transpose to get (3 rows, 2 cols)
    
    # Right Plot Data (Others)
    right_list = []
    for name in cell_lines_order[1:]:
        right_list.append(data[name]['21'])
        right_list.append(data[name]['1'])
    
    right_matrix = np.array(right_list).T # Transpose to get (3 rows, 16 cols)
    
    # Plotting settings
    cmap = plt.cm.viridis
    norm = colors.Normalize(vmin=40, vmax=100)
    
    # --- Plot Left Heatmap ---
    im1 = ax1.imshow(left_matrix, cmap=cmap, norm=norm, aspect='auto')
    
    # --- Plot Right Heatmap ---
    im2 = ax2.imshow(right_matrix, cmap=cmap, norm=norm, aspect='auto')
    
    # --- Styling Axes ---
    
    # Y-Axis (Shared, but only labels on left)
    yticks = [0, 1, 2]
    yticklabels = ['0', '2.5', '5']
    
    ax1.set_yticks(yticks)
    ax1.set_yticklabels(yticklabels, fontsize=12)
    ax1.set_ylabel(r"ML-210 ($\mu$M)", fontsize=14)
    
    ax2.set_yticks(yticks)
    ax2.set_yticklabels([]) # Hide labels
    
    # X-Axis (Inner: 21 1)
    # Left
    ax1.set_xticks([0, 1])
    ax1.set_xticklabels(['21', '1'], fontsize=12)
    
    # Right
    right_xticks = np.arange(16)
    right_xticklabels = ['21', '1'] * 8
    ax2.set_xticks(right_xticks)
    ax2.set_xticklabels(right_xticklabels, fontsize=12)
    
    # X-Axis Labels (Outer: Cell Lines)
    # We use text annotations or a secondary axis. Text is easier for positioning.
    
    # Left Label
    ax1.text(0.5, 3.2, "B16-F0", rotation=45, ha='right', va='top', fontsize=12, transform=ax1.transData)
    
    # Right Labels
    for i, name in enumerate(cell_lines_order[1:]):
        # Center of the pair (indices 0,1 -> 0.5; 2,3 -> 2.5)
        x_pos = i * 2 + 0.5
        ax2.text(x_pos, 3.2, name, rotation=45, ha='right', va='top', fontsize=12, transform=ax2.transData)

    # Add common X label
    # We can place it relative to the figure or one of the axes
    # The label is "% O2" placed at the end of the x-axis ticks
    ax2.text(16, 2.8, "% O$_2$", ha='center', va='top', fontsize=12)

    # --- Grid Lines (Borders) ---
    # Draw black borders around every cell
    
    def draw_borders(ax, shape):
        rows, cols = shape
        # Horizontal lines
        for r in range(rows + 1):
            ax.hlines(r - 0.5, -0.5, cols - 0.5, color='black', linewidth=1)
        # Vertical lines
        for c in range(cols + 1):
            ax.vlines(c - 0.5, -0.5, rows - 0.5, color='black', linewidth=1)
            
    draw_borders(ax1, left_matrix.shape)
    draw_borders(ax2, right_matrix.shape)
    
    # --- P-Value Annotations ---
    # Drawn above the columns.
    # Structure: Line up, Line across, Line down, Text above.
    
    def add_p_annotation(ax, x_start, x_end, p_val_text):
        y_base = -0.5 # Top of the heatmap cells
        h_line = 0.5  # Height of the bracket legs
        y_top = y_base - h_line
        
        # Draw bracket
        ax.plot([x_start, x_start, x_end, x_end], [y_base, y_top, y_top, y_base], color='black', linewidth=1, clip_on=False)
        
        # Add text
        ax.text((x_start + x_end)/2, y_top - 0.1, p_val_text, ha='center', va='bottom', rotation=90, fontsize=11)

    # Left P-value
    if "B16-F0" in p_values:
        p_text = format_p_value(p_values["B16-F0"])
        add_p_annotation(ax1, 0, 1, p_text)
        
    # Right P-values
    for i, name in enumerate(cell_lines_order[1:]):
        if name in p_values:
            p_text = format_p_value(p_values[name])
            x_start = i * 2
            x_end = i * 2 + 1
            add_p_annotation(ax2, x_start, x_end, p_text)

    # --- Colorbar ---
    cbar = plt.colorbar(im2, cax=cbar_ax)
    cbar.set_label("Relative viability (%)", fontsize=12)
    cbar.set_ticks([40, 60, 80, 100])
    cbar.ax.tick_params(labelsize=12)
    
    # --- Final Adjustments ---
    # Remove spines (outer box) since we drew our own grid
    for ax in [ax1, ax2]:
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        # Remove ticks marks but keep labels
        ax.tick_params(axis='both', which='both', length=0)
        
    # Add lines under the "21 1" labels to group them (like in the image)
    # Left
    ax1.plot([0, 1], [2.7, 2.7], color='black', linewidth=1, clip_on=False)
    # Right
    for i in range(8):
        start = i * 2
        end = i * 2 + 1
        ax2.plot([start, end], [2.7, 2.7], color='black', linewidth=1, clip_on=False)

    # Adjust margins to fit the rotated labels and p-values
    plt.subplots_adjust(top=0.75, bottom=0.25, left=0.1, right=0.9)

    # Save
    plt.savefig(output_path, dpi=300, bbox_inches='tight')

# -----------------------------------------------------------------------------
# 4. Main Execution
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
        
    data, p_vals = parse_data(csv_data)
    create_chart(data, p_vals, output_file)