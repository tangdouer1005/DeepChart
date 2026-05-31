
import sys
import io
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 1. Embed Source Data
# The provided markdown table is converted into a string for parsing.
source_data = """
| service_type            |   county_fip |   fairness_index |   ratio_of_HighAging_CBG |
|:------------------------|-------------:|-----------------:|-------------------------:|
| Health Care Services    |         1003 |     -0.037037    |              0.0319149   |
| Health Care Services    |         1015 |     -0.777778    |              0.010989    |
| Health Care Services    |         1073 |      0.777778    |              0.0019305   |
| Health Care Services    |         1077 |      0.111111    |              0.0136986   |
| Health Care Services    |         1089 |      0.777778    |              0.0052356   |
| Health Care Services    |         1097 |      1           |              0.00743494  |
| Health Care Services    |         1101 |     -0.777778    |              0.00502513  |
| Health Care Services    |         4003 |     -0.555556    |              0.00980392  |
| Health Care Services    |         4005 |     -0.333333    |              0.0204082   |
| Health Care Services    |         4007 |      0.111111    |              0.0444444   |
| Health Care Services    |         4012 |     -0.111111    |              0.272727    |
| Health Care Services    |         4013 |      0.228003    |              0.0690619   |
| Health Care Services    |         4015 |     -0.52381     |              0.059322    |
| Health Care Services    |         4019 |     -0.0784314   |              0.0539683   |
| Health Care Services    |         4021 |      0.125       |              0.080402    |
| Health Care Services    |         4025 |      0.0505051   |              0.0964912   |
| Health Care Services    |         4027 |     -0.383838    |              0.15493     |
| Health Care Services    |         5005 |      1           |              0.0333333   |
| Health Care Services    |         5007 |     -1           |              0.00724638  |
| Health Care Services    |         5023 |      0.777778    |              0.0454545   |
| Health Care Services    |         5049 |      0.333333    |              0.0833333   |
| Health Care Services    |         5051 |      0.037037    |              0.0428571   |
| Health Care Services    |         5107 |      0.555556    |              0.0416667   |
| Health Care Services    |         5125 |      0           |              0.0327869   |
| Health Care Services    |         5135 |      1           |              0.111111    |
| Health Care Services    |         5141 |     -0.777778    |              0.0769231   |
| Health Care Services    |         6005 |      0.777778    |              0.0357143   |
| Health Care Services    |         6007 |      0.111111    |              0.00512821  |
| Health Care Services    |         6013 |      0.62963     |              0.0141287   |
| Health Care Services    |         6019 |      0.888889    |              0.00339559  |
| Health Care Services    |         6025 |     -0.555556    |              0.0208333   |
| Health Care Services    |         6029 |     -0.244444    |              0.0109649   |
| Health Care Services    |         6037 |      0.111111    |              0.00171206  |
| Health Care Services    |         6039 |      0.555556    |              0.0125      |
| Health Care Services    |         6041 |     -1           |              0.00571429  |
| Health Care Services    |         6043 |     -0.555556    |              0.0588235   |
| Health Care Services    |         6045 |     -0.333333    |              0.0126582   |
| Health Care Services    |         6053 |     -0.111111    |              0.00858369  |
| Health Care Services    |         6055 |     -0.333333    |              0.0283019   |
| Health Care Services    |         6059 |      0.213675    |              0.0213933   |
| Health Care Services    |         6061 |     -0.222222    |              0.056338    |
| Health Care Services    |         6063 |     -1           |              0.0909091   |
| Health Care Services    |         6065 |      0.126984    |              0.0543689   |
| Health Care Services    |         6067 |     -0.333333    |              0.00328947  |
| Health Care Services    |         6071 |     -0.2         |              0.00457875  |
| Health Care Services    |         6073 |      0.0849673   |              0.00947075  |
| Health Care Services    |         6075 |     -0.777778    |              0.00172117  |
| Health Care Services    |         6077 |      0.185185    |              0.00759494  |
| Health Care Services    |         6079 |     -0.592593    |              0.0368098   |
| Health Care Services    |         6081 |     -1           |              0.00215983  |
| Health Care Services    |         6083 |     -0.244444    |              0.0159744   |
| Health Care Services    |         6085 |      0.481481    |              0.0027907   |
| Health Care Services    |         6087 |     -1           |              0.00510204  |
| Health Care Services    |         6095 |     -0.688889    |              0.0175439   |
| Health Care Services    |         6097 |     -0.530864    |              0.0232558   |
| Health Care Services    |         6101 |      0.777778    |              0.016129    |
| Health Care Services    |         6107 |      1           |              0.0037037   |
| Health Care Services    |         6109 |     -0.111111    |              0.0208333   |
| Health Care Services    |         6111 |     -0.333333    |              0.00697674  |
| Health Care Services    |         6113 |     -0.777778    |              0.00819672  |
| Health Care Services    |         8001 |      0.888889    |              0.00769231  |
| Health Care Services    |         8005 |     -0.148148    |              0.0147059   |
| Health Care Services    |         8014 |     -0.222222    |              0.0434783   |
| Health Care Services    |         8031 |      0.388889    |              0.00831601  |
| Health Care Services    |         8035 |      1           |              0.00645161  |
| Health Care Services    |         8041 |      0.555556    |              0.00273973  |
| Health Care Services    |         8043 |      0.777778    |              0.0277778   |
| Health Care Services    |         8123 |     -0.777778    |              0.00571429  |
| Health Care Services    |         9001 |     -0.222222    |              0.00611621  |
| Health Care Services    |         9003 |     -0.111111    |              0.0029985   |
| Health Care Services    |         9007 |     -0.555556    |              0.0168067   |
| Health Care Services    |         9009 |     -0.0277778   |              0.0127389   |
| Health Care Services    |         9011 |      0.444444    |              0.0106383   |
| Health Care Services    |        10003 |     -0.777778    |              0.00271739  |
| Health Care Services    |        10005 |     -0.196581    |              0.0970149   |
| Health Care Services    |        12001 |     -0.111111    |              0.00645161  |
| Health Care Services    |        12009 |      0.00653595  |              0.0534591   |
| Health Care Services    |        12011 |      0.301587    |              0.0446809   |
| Health Care Services    |        12015 |     -0.141762    |              0.268519    |
| Health Care Services    |        12017 |     -0.296296    |              0.136364    |
| Health Care Services    |        12019 |     -1           |              0.0123457   |
| Health Care Services    |        12021 |      0.543434    |              0.284974    |
| Health Care Services    |        12027 |      0.111111    |              0.0769231   |
| Health Care Services    |        12031 |      0.185185    |              0.00612245  |
| Health Care Services    |        12035 |     -0.0793651   |              0.134615    |
| Health Care Services    |        12049 |      1           |              0.05        |
| Health Care Services    |        12053 |      0.0740741   |              0.11215     |
| Health Care Services    |        12055 |     -0.2         |              0.189873    |
| Health Care Services    |        12057 |      0.414141    |              0.0249716   |
| Health Care Services    |        12061 |      0.0899471   |              0.225806    |
| Health Care Services    |        12069 |      0.218107    |              0.182432    |
| Health Care Services    |        12071 |      0.0410628   |              0.178988    |
| Health Care Services    |        12073 |      1           |              0.0112994   |
| Health Care Services    |        12081 |     -0.111111    |              0.163462    |
| Health Care Services    |        12083 |      0.17284     |              0.102857    |
| Health Care Services    |        12085 |      0.320988    |              0.191489    |
| Health Care Services    |        12086 |      0.412698    |              0.00878294  |
| Health Care Services    |        12087 |     -0.722222    |              0.0526316   |
| Health Care Services    |        12089 |      0.555556    |              0.075       |
| Health Care Services    |        12091 |     -0.222222    |              0.017094    |
| Health Care Services    |        12093 |     -0.333333    |              0.0357143   |
| Health Care Services    |        12095 |      0.259259    |              0.008       |
| Health Care Services    |        12097 |      0.333333    |              0.0394737   |
| Health Care Services    |        12099 |      0.404393    |              0.194131    |
| Health Care Services    |        12101 |      0.301587    |              0.0909091   |
| Health Care Services    |        12103 |      0.199161    |              0.073509    |
| Health Care Services    |        12105 |     -0.285714    |              0.0422961   |
| Health Care Services    |        12107 |      0.222222    |              0.0327869   |
| Health Care Services    |        12109 |      0.333333    |              0.0243902   |
| Health Care Services    |        12111 |     -0.333333    |              0.134752    |
| Health Care Services    |        12115 |     -0.157407    |              0.285714    |
| Health Care Services    |        12119 |      0.925926    |              0.292683    |
| Health Care Services    |        12121 |     -0.111111    |              0.0384615   |
| Health Care Services    |        12123 |     -0.111111    |              0.05        |
| Health Care Services    |        12127 |     -0.238095    |              0.0484429   |
| Health Care Services    |        13015 |      1           |              0.0204082   |
| Health Care Services    |        13051 |     -0.851852    |              0.0146341   |
| Health Care Services    |        13067 |      1           |              0.00285714  |
| Health Care Services    |        13073 |      1           |              0.0181818   |
| Health Care Services    |        13085 |     -0.777778    |              0.1         |
| Health Care Services    |        13089 |      0.333333    |              0.0025641   |
| Health Care Services    |        13095 |     -0.777778    |              0.0144928   |
| Health Care Services    |        13121 |      0.777778    |              0.00367647  |
| Health Care Services    |        13127 |     -0.555556    |              0.0181818   |
| Health Care Services    |        13133 |      1           |              0.210526    |
| Health Care Services    |        13227 |     -0.333333    |              0.0588235   |
| Health Care Services    |        13241 |     -1           |              0.0769231   |
| Health Care Services    |        17001 |     -0.333333    |              0.0163934   |
| Health Care Services    |        17011 |      1           |              0.027027    |
| Health Care Services    |        17031 |      0.466667    |              0.00500877  |
| Health Care Services    |        17043 |      0.444444    |              0.00648298  |
| Health Care Services    |        17089 |     -1           |              0.00364964  |
| Health Care Services    |        17097 |     -0.111111    |              0.00497512  |
| Health Care Services    |        17115 |      0.777778    |              0.010101    |
| Health Care Services    |        17167 |      0.555556    |              0.00555556  |
| Health Care Services    |        17177 |      0.555556    |              0.0204082   |
| Health Care Services    |        17197 |     -0.666667    |              0.00508906  |
| Health Care Services    |        17201 |      0.62963     |              0.0114068   |
| Health Care Services    |        34003 |     -0.444444    |              0.00252845  |
| Health Care Services    |        34005 |     -0.444444    |              0.0143369   |
| Health Care Services    |        34007 |      0           |              0.0052356   |
| Health Care Services    |        34009 |     -0.277778    |              0.0879121   |
| Health Care Services    |        34013 |      0.259259    |              0.00447094  |
| Health Care Services    |        34015 |     -0.333333    |              0.0052356   |
| Health Care Services    |        34017 |      0.666667    |              0.00449438  |
| Health Care Services    |        34023 |     -0.606838    |              0.0248566   |
| Health Care Services    |        34025 |      0.209877    |              0.0191898   |
| Health Care Services    |        34027 |      0.111111    |              0.00338983  |
| Health Care Services    |        34029 |     -0.137037    |              0.15873     |
| Health Care Services    |        34031 |      0.333333    |              0.00547945  |
| Health Care Services    |        34035 |      0.111111    |              0.00552486  |
| Health Care Services    |        34041 |     -0.777778    |              0.0126582   |
| Health Care Services    |        36001 |     -0.111111    |              0.00425532  |
| Health Care Services    |        36005 |     -0.206349    |              0.00606586  |
| Health Care Services    |        36007 |      0.333333    |              0.0147059   |
| Health Care Services    |        36015 |     -0.555556    |              0.0114943   |
| Health Care Services    |        36025 |     -0.333333    |              0.0181818   |
| Health Care Services    |        36029 |      0.333333    |              0.0012837   |
| Health Care Services    |        36041 |      1           |              0.125       |
| Health Care Services    |        36043 |      0.111111    |              0.016129    |
| Health Care Services    |        36047 |      0.407407    |              0.0028777   |
| Health Care Services    |        36055 |      0.444444    |              0.00328407  |
| Health Care Services    |        36059 |      0.5         |              0.00349956  |
| Health Care Services    |        36061 |      0.377778    |              0.00854701  |
| Health Care Services    |        36065 |     -0.333333    |              0.00534759  |
| Health Care Services    |        36067 |      0.166667    |              0.0105263   |
| Health Care Services    |        36071 |     -0.111111    |              0.00362319  |
| Health Care Services    |        36075 |     -0.555556    |              0.0121951   |
| Health Care Services    |        36081 |      0.382716    |              0.00515464  |
| Health Care Services    |        36083 |      0.777778    |              0.008       |
| Health Care Services    |        36085 |      0.777778    |              0.00295858  |
| Health Care Services    |        36091 |      0.777778    |              0.0143885   |
| Health Care Services    |        36103 |     -0.0877193   |              0.019019    |
| Health Care Services    |        36113 |     -1           |              0.0212766   |
| Health Care Services    |        36119 |     -0.733333    |              0.00710227  |
| Health Care Services    |        42003 |     -0.277778    |              0.00363636  |
| Health Care Services    |        42011 |      0.333333    |              0.00377358  |
| Health Care Services    |        42017 |     -0.407407    |              0.00787402  |
| Health Care Services    |        42019 |      0.555556    |              0.00833333  |
| Health Care Services    |        42021 |      0.111111    |              0.0222222   |
| Health Care Services    |        42029 |      0.62963     |              0.0113208   |
| Health Care Services    |        42041 |     -0.333333    |              0.00662252  |
| Health Care Services    |        42045 |     -0.222222    |              0.00457666  |
| Health Care Services    |        42053 |     -0.333333    |              0.375       |
| Health Care Services    |        42055 |      0.111111    |              0.011236    |
| Health Care Services    |        42067 |      1           |              0.0526316   |
| Health Care Services    |        42071 |      0.277778    |              0.0122699   |
| Health Care Services    |        42075 |      1           |              0.0117647   |
| Health Care Services    |        42077 |      0.222222    |              0.00813008  |
| Health Care Services    |        42081 |      0.777778    |              0.00884956  |
| Health Care Services    |        42085 |      0.555556    |              0.00900901  |
| Health Care Services    |        42091 |      0.481481    |              0.0107143   |
| Health Care Services    |        42095 |      1           |              0.00990099  |
| Health Care Services    |        42101 |     -0.0555556   |              0.00598802  |
| Health Care Services    |        42103 |      0.555556    |              0.0232558   |
| Health Care Services    |        42133 |     -0.555556    |              0.00310559  |
| Health Care Services    |        48007 |      0.925926    |              0.157895    |
| Health Care Services    |        48029 |      0.111111    |              0.00184502  |
| Health Care Services    |        48061 |     -0.111111    |              0.0133333   |
| Health Care Services    |        48085 |      0           |              0.00422833  |
| Health Care Services    |        48089 |      1           |              0.0555556   |
| Health Care Services    |        48113 |      0.833333    |              0.00239664  |
| Health Care Services    |        48121 |     -0.333333    |              0.0132275   |
| Health Care Services    |        48141 |      0.222222    |              0.00779727  |
| Health Care Services    |        48149 |      0.111111    |              0.04        |
| Health Care Services    |        48201 |     -0.466667    |              0.00233209  |
| Health Care Services    |        48215 |     -0.511111    |              0.0147493   |
| Health Care Services    |        48221 |     -0.555556    |              0.0333333   |
| Health Care Services    |        48225 |      1           |              0.047619    |
| Health Care Services    |        48245 |      0.777778    |              0.00483092  |
| Health Care Services    |        48265 |     -1           |              0.0606061   |
| Health Care Services    |        48299 |      1           |              0.166667    |
| Health Care Services    |        48309 |      0.222222    |              0.0121212   |
| Health Care Services    |        48339 |     -0.555556    |              0.00537634  |
| Health Care Services    |        48343 |     -0.555556    |              0.0714286   |
| Health Care Services    |        48375 |      1           |              0.0103093   |
| Health Care Services    |        48403 |     -1           |              0.1         |
| Health Care Services    |        48439 |      0.333333    |              0.000849618 |
| Health Care Services    |        48451 |      0.333333    |              0.0103093   |
| Health Care Services    |        48453 |     -1           |              0.00172414  |
| Health Care Services    |        48465 |      1           |              0.0294118   |
| Health Care Services    |        48479 |     -0.555556    |              0.0070922   |
| Health Care Services    |        48491 |     -0.45679     |              0.037037    |
| Health Care Services    |        15001 |      0.555556    |              0.0243902   |
| Health Care Services    |        15003 |      0.111111    |              0.00676819  |
| Health Care Services    |        15007 |     -0.777778    |              0.0178571   |
| Health Care Services    |        18005 |      0.777778    |              0.0169492   |
| Health Care Services    |        18035 |      0.555556    |              0.00990099  |
| Health Care Services    |        18081 |      1           |              0.0135135   |
| Health Care Services    |        18097 |      0.555556    |              0.00474684  |
| Health Care Services    |        18157 |      0.111111    |              0.00980392  |
| Health Care Services    |        18163 |     -0.444444    |              0.0125786   |
| Health Care Services    |        19025 |     -0.333333    |              0.0909091   |
| Health Care Services    |        19059 |      0.333333    |              0.0666667   |
| Health Care Services    |        19099 |      1           |              0.0285714   |
| Health Care Services    |        19139 |     -0.111111    |              0.0294118   |
| Health Care Services    |        19155 |     -0.333333    |              0.0107527   |
| Health Care Services    |        19163 |      0.111111    |              0.00806452  |
| Health Care Services    |        20091 |      0.888889    |              0.00534759  |
| Health Care Services    |        20177 |      0.333333    |              0.0148148   |
| Health Care Services    |        21067 |     -1           |              0.00961538  |
| Health Care Services    |        21111 |      0.777778    |              0.00173913  |
| Health Care Services    |        21217 |      0.777778    |              0.047619    |
| Health Care Services    |        22051 |      1           |              0.00302115  |
| Health Care Services    |        22127 |     -0.111111    |              0.0625      |
| Health Care Services    |        23003 |      0.333333    |              0.0125      |
| Health Care Services    |        23005 |      0.111111    |              0.00469484  |
| Health Care Services    |        23013 |      0.333333    |              0.0243902   |
| Health Care Services    |        23031 |      0.015873    |              0.05        |
| Health Care Services    |        24003 |      0.185185    |              0.00961538  |
| Health Care Services    |        24005 |      0.587302    |              0.0132325   |
| Health Care Services    |        24009 |      0.777778    |              0.0222222   |
| Health Care Services    |        24013 |      1           |              0.00943396  |
| Health Care Services    |        24021 |      0.222222    |              0.0105263   |
| Health Care Services    |        24029 |      1           |              0.05        |
| Health Care Services    |        24031 |      0.259259    |              0.019544    |
| Health Care Services    |        24033 |      1           |              0.00191205  |
| Health Care Services    |        24041 |     -0.333333    |              0.0714286   |
| Health Care Services    |        24045 |      1           |              0.0140845   |
| Health Care Services    |        24047 |     -0.259259    |              0.0625      |
| Health Care Services    |        24510 |      0.444444    |              0.00918836  |
| Health Care Services    |        25001 |     -0.0111111   |              0.102041    |
| Health Care Services    |        25003 |     -0.555556    |              0.020979    |
| Health Care Services    |        25005 |      0.666667    |              0.00512821  |
| Health Care Services    |        25009 |      0.222222    |              0.003663    |
| Health Care Services    |        25013 |      0.777778    |              0.00296736  |
| Health Care Services    |        25017 |      1           |              0.000882613 |
| Health Care Services    |        25021 |      0.407407    |              0.00632911  |
| Health Care Services    |        25023 |     -0.333333    |              0.00277778  |
| Health Care Services    |        25025 |     -0.037037    |              0.00464396  |
| Health Care Services    |        25027 |      1           |              0.00178571  |
| Health Care Services    |        26019 |      1           |              0.0714286   |
| Health Care Services    |        26021 |     -0.777778    |              0.0208333   |
| Health Care Services    |        26033 |     -0.111111    |              0.027027    |
| Health Care Services    |        26049 |      1           |              0.00268097  |
| Health Care Services    |        26081 |      0.111111    |              0.00514139  |
| Health Care Services    |        26089 |      0.333333    |              0.0588235   |
| Health Care Services    |        26093 |      0.777778    |              0.00884956  |
| Health Care Services    |        26099 |      0.666667    |              0.00318979  |
| Health Care Services    |        26121 |      0.666667    |              0.0144928   |
| Health Care Services    |        26125 |     -0.111111    |              0.00642398  |
| Health Care Services    |        26139 |     -0.111111    |              0.0193548   |
| Health Care Services    |        26163 |      0.244444    |              0.00274424  |
| Health Care Services    |        27021 |     -0.333333    |              0.0357143   |
| Health Care Services    |        27053 |      0.84127     |              0.00719424  |
| Health Care Services    |        27091 |      0.555556    |              0.047619    |
| Health Care Services    |        27099 |      0.777778    |              0.0294118   |
| Health Care Services    |        27109 |      0.444444    |              0.018018    |
| Health Care Services    |        28035 |      0.777778    |              0.0188679   |
| Health Care Services    |        28067 |      0.333333    |              0.0192308   |
| Health Care Services    |        28141 |      1           |              0.0588235   |
| Health Care Services    |        29015 |     -1           |              0.0625      |
| Health Care Services    |        29019 |      0.555556    |              0.0114943   |
| Health Care Services    |        29031 |      1           |              0.0178571   |
| Health Care Services    |        29077 |      1           |              0.00598802  |
| Health Care Services    |        29095 |      0.481481    |              0.00547445  |
| Health Care Services    |        29141 |      0.777778    |              0.0588235   |
| Health Care Services    |        29189 |      0.5         |              0.00578035  |
| Health Care Services    |        29209 |      0.111111    |              0.0416667   |
| Health Care Services    |        29213 |      0.333333    |              0.0294118   |
| Health Care Services    |        30013 |      0.555556    |              0.0138889   |
| Health Care Services    |        30053 |     -0.333333    |              0.0588235   |
| Health Care Services    |        30081 |      0.111111    |              0.0322581   |
| Health Care Services    |        30111 |      0.333333    |              0.00892857  |
| Health Care Services    |        31055 |      0.555556    |              0.00603622  |
| Health Care Services    |        32003 |      0.339181    |              0.0293663   |
| Health Care Services    |        32031 |     -0.444444    |              0.00641026  |
| Health Care Services    |        33003 |      0.333333    |              0.025       |
| Health Care Services    |        33009 |      1           |              0.0142857   |
| Health Care Services    |        33011 |      0.555556    |              0.0037037   |
| Health Care Services    |        33013 |      0.555556    |              0.00990099  |
| Health Care Services    |        33015 |      0           |              0.010989    |
| Health Care Services    |        35045 |      1           |              0.0103093   |
| Health Care Services    |        35049 |      0.111111    |              0.0196078   |
| Health Care Services    |        35053 |     -0.555556    |              0.0833333   |
| Health Care Services    |        35055 |     -0.777778    |              0.0454545   |
| Health Care Services    |        37019 |      0.259259    |              0.133333    |
| Health Care Services    |        37031 |      0.333333    |              0.0138889   |
| Health Care Services    |        37037 |      0.111111    |              0.0285714   |
| Health Care Services    |        37063 |      0.555556    |              0.00653595  |
| Health Care Services    |        37071 |      1           |              0.00578035  |
| Health Care Services    |        37089 |      0.644444    |              0.0694444   |
| Health Care Services    |        37119 |      0.111111    |              0.0036036   |
| Health Care Services    |        37125 |      0.851852    |              0.0526316   |
| Health Care Services    |        37131 |      0.333333    |              0.0454545   |
| Health Care Services    |        37161 |      0.777778    |              0.0192308   |
| Health Care Services    |        37175 |     -1           |              0.04        |
| Health Care Services    |        38051 |      1           |              0.333333    |
| Health Care Services    |        39021 |      0.333333    |              0.0294118   |
| Health Care Services    |        39023 |      0.222222    |              0.0147059   |
| Health Care Services    |        39025 |     -0.111111    |              0.00847458  |
| Health Care Services    |        39035 |     -6.16791e-18 |              0.00516351  |
| Health Care Services    |        39037 |      0.555556    |              0.0192308   |
| Health Care Services    |        39041 |      0.777778    |              0.0113636   |
| Health Care Services    |        39043 |     -0.62963     |              0.0428571   |
| Health Care Services    |        39049 |     -0.111111    |              0.00225479  |
| Health Care Services    |        39061 |      0.111111    |              0.00143472  |
| Health Care Services    |        39081 |      1           |              0.0149254   |
| Health Care Services    |        39085 |      0.555556    |              0.00645161  |
| Health Care Services    |        39099 |      0.277778    |              0.0185185   |
| Health Care Services    |        39113 |     -0.333333    |              0.0047619   |
| Health Care Services    |        39119 |      0.333333    |              0.0133333   |
| Health Care Services    |        39121 |      0.333333    |              0.0833333   |
| Health Care Services    |        39123 |     -0.555556    |              0.0465116   |
| Health Care Services    |        39131 |      1           |              0.0454545   |
| Health Care Services    |        39153 |     -0.259259    |              0.00663717  |
| Health Care Services    |        39165 |      1           |              0.00925926  |
| Health Care Services    |        39169 |      1           |              0.0120482   |
| Health Care Services    |        40115 |     -0.777778    |              0.0344828   |
| Health Care Services    |        41005 |      0.111111    |              0.00460829  |
| Health Care Services    |        41011 |      0           |              0.03125     |
| Health Care Services    |        41015 |      0.111111    |              0.176471    |
| Health Care Services    |        41017 |     -0.703704    |              0.0352941   |
| Health Care Services    |        41019 |      0.222222    |              0.0235294   |
| Health Care Services    |        41029 |      0.037037    |              0.023622    |
| Health Care Services    |        41033 |     -0.777778    |              0.0185185   |
| Health Care Services    |        41039 |      0.277778    |              0.0155039   |
| Health Care Services    |        41047 |     -0.666667    |              0.0104167   |
| Health Care Services    |        41051 |      0.777778    |              0.00191939  |
| Health Care Services    |        41057 |     -0.111111    |              0.0344828   |
| Health Care Services    |        41059 |     -0.111111    |              0.015625    |
| Health Care Services    |        41067 |      0.422222    |              0.0165017   |
| Health Care Services    |        44001 |      0.333333    |              0.0263158   |
| Health Care Services    |        44007 |      0.777778    |              0.00601202  |
| Health Care Services    |        44009 |     -0.822222    |              0.0531915   |
| Health Care Services    |        45001 |      0.777778    |              0.047619    |
| Health Care Services    |        45013 |     -0.22807     |              0.169643    |
| Health Care Services    |        45019 |     -1           |              0.0170213   |
| Health Care Services    |        45029 |      0.333333    |              0.0322581   |
| Health Care Services    |        45043 |     -0.111111    |              0.0217391   |
| Health Care Services    |        45051 |      0.722222    |              0.0268456   |
| Health Care Services    |        45055 |     -0.333333    |              0.0232558   |
| Health Care Services    |        45065 |      1           |              0.25        |
| Health Care Services    |        45073 |     -0.777778    |              0.0576923   |
| Health Care Services    |        45079 |      1           |              0.00408163  |
| Health Care Services    |        46081 |      1           |              0.0588235   |
| Health Care Services    |        47035 |      0.111111    |              0.09375     |
| Health Care Services    |        47065 |      0.111111    |              0.00404858  |
| Health Care Services    |        47105 |     -0.722222    |              0.129032    |
| Health Care Services    |        47155 |      1           |              0.0227273   |
| Health Care Services    |        47157 |      0.555556    |              0.00318471  |
| Health Care Services    |        47163 |      0           |              0.018018    |
| Health Care Services    |        49043 |     -0.333333    |              0.0277778   |
| Health Care Services    |        49049 |     -0.777778    |              0.00289855  |
| Health Care Services    |        49053 |     -0.111111    |              0.0175439   |
| Health Care Services    |        51003 |      0.333333    |              0.0151515   |
| Health Care Services    |        51013 |      0.555556    |              0.0110497   |
| Health Care Services    |        51019 |      0.111111    |              0.0208333   |
| Health Care Services    |        51087 |     -0.62963     |              0.0175439   |
| Health Care Services    |        51095 |     -0.333333    |              0.0740741   |
| Health Care Services    |        51103 |      0.333333    |              0.230769    |
| Health Care Services    |        51107 |      1           |              0.0122699   |
| Health Care Services    |        51125 |     -0.333333    |              0.0833333   |
| Health Care Services    |        51133 |     -0.444444    |              0.153846    |
| Health Care Services    |        51135 |      0.333333    |              0.125       |
| Health Care Services    |        51153 |      0.740741    |              0.026087    |
| Health Care Services    |        51161 |     -0.333333    |              0.0185185   |
| Health Care Services    |        51510 |      0.333333    |              0.0188679   |
| Health Care Services    |        51710 |     -0.555556    |              0.00529101  |
| Health Care Services    |        51760 |     -0.111111    |              0.00621118  |
| Health Care Services    |        51775 |      1           |              0.05        |
| Health Care Services    |        51810 |     -0.111111    |              0.00662252  |
| Health Care Services    |        53005 |      0.333333    |              0.00729927  |
| Health Care Services    |        53009 |      0.185185    |              0.0545455   |
| Health Care Services    |        53011 |     -0.777778    |              0.00357143  |
| Health Care Services    |        53015 |      1           |              0.0224719   |
| Health Care Services    |        53027 |     -0.111111    |              0.016129    |
| Health Care Services    |        53031 |      0.481481    |              0.111111    |
| Health Care Services    |        53033 |      0.111111    |              0.00281294  |
| Health Care Services    |        53041 |     -0.777778    |              0.0322581   |
| Health Care Services    |        53045 |     -0.333333    |              0.0408163   |
| Health Care Services    |        53053 |      0.62963     |              0.00535714  |
| Health Care Services    |        53061 |      0.333333    |              0.00199601  |
| Health Care Services    |        53063 |      0.666667    |              0.00621118  |
| Health Care Services    |        53067 |      0.333333    |              0.0186335   |
| Health Care Services    |        53071 |      0.777778    |              0.0232558   |
| Health Care Services    |        53073 |      1           |              0.00980392  |
| Health Care Services    |        53077 |      0.333333    |              0.00671141  |
| Health Care Services    |        54063 |     -0.555556    |              0.0833333   |
| Health Care Services    |        54069 |      0.777778    |              0.0208333   |
| Health Care Services    |        54083 |      0.111111    |              0.037037    |
| Health Care Services    |        54109 |     -0.111111    |              0.0526316   |
| Health Care Services    |        55025 |      0.777778    |              0.00322581  |
| Health Care Services    |        55027 |      0.333333    |              0.0149254   |
| Health Care Services    |        55047 |      0.777778    |              0.05        |
| Health Care Services    |        55071 |      1           |              0.0133333   |
| Health Care Services    |        55079 |      0           |              0.00232829  |
| Health Care Services    |        55087 |      1           |              0.00763359  |
| Health Care Services    |        55089 |      1           |              0.0163934   |
| Health Care Services    |        55131 |      1           |              0.0120482   |
| Health Care Services    |        55133 |      0.333333    |              0.00334448  |
| Health Care Services    |        72057 |      1           |              0.030303    |
| Health Care Services    |        72079 |     -0.555556    |              0.0555556   |
| Health Care Services    |        72097 |     -1           |              0.0142857   |
| Health Care Services    |        72113 |      0.111111    |              0.0149254   |
| Health Care Services    |        72127 |      0.444444    |              0.00542005  |
| Health Care Services    |        72145 |     -0.444444    |              0.0526316   |
| Grocery and Food Supply |         1003 |     -0.333333    |              0.0319149   |
| Grocery and Food Supply |         1073 |      1           |              0.0019305   |
| Grocery and Food Supply |         1077 |     -0.111111    |              0.0136986   |
| Grocery and Food Supply |         1089 |      0.333333    |              0.0052356   |
| Grocery and Food Supply |         1097 |     -0.222222    |              0.00743494  |
| Grocery and Food Supply |         1101 |     -1           |              0.00502513  |
| Grocery and Food Supply |         4003 |     -0.333333    |              0.00980392  |
| Grocery and Food Supply |         4005 |     -0.555556    |              0.0204082   |
| Grocery and Food Supply |         4007 |     -0.111111    |              0.0444444   |
| Grocery and Food Supply |         4012 |      0.333333    |              0.272727    |
| Grocery and Food Supply |         4013 |      0.0695257   |              0.0682635   |
| Grocery and Food Supply |         4015 |     -0.492063    |              0.059322    |
| Grocery and Food Supply |         4019 |     -0.529412    |              0.0539683   |
| Grocery and Food Supply |         4021 |      0.0972222   |              0.080402    |
| Grocery and Food Supply |         4025 |     -0.010101    |              0.0964912   |
| Grocery and Food Supply |         4027 |     -0.232323    |              0.15493     |
| Grocery and Food Supply |         5005 |      0.333333    |              0.0333333   |
| Grocery and Food Supply |         5007 |     -0.555556    |              0.00724638  |
| Grocery and Food Supply |         5023 |      0.333333    |              0.0454545   |
| Grocery and Food Supply |         5049 |      1           |              0.0833333   |
| Grocery and Food Supply |         5051 |     -0.555556    |              0.0428571   |
| Grocery and Food Supply |         5107 |     -0.111111    |              0.0416667   |
| Grocery and Food Supply |         5125 |     -1           |              0.0327869   |
| Grocery and Food Supply |         5135 |      0.555556    |              0.111111    |
| Grocery and Food Supply |         5141 |     -0.111111    |              0.0769231   |
| Grocery and Food Supply |         6005 |      1           |              0.0357143   |
| Grocery and Food Supply |         6007 |     -0.111111    |              0.00512821  |
| Grocery and Food Supply |         6009 |     -1           |              0.0333333   |
| Grocery and Food Supply |         6013 |     -0.753086    |              0.0141287   |
| Grocery and Food Supply |         6019 |      0.222222    |              0.00339559  |
| Grocery and Food Supply |         6025 |     -0.777778    |              0.0208333   |
| Grocery and Food Supply |         6029 |     -0.377778    |              0.0109649   |
| Grocery and Food Supply |         6037 |     -0.252525    |              0.00171206  |
| Grocery and Food Supply |         6039 |      0.555556    |              0.0125      |
| Grocery and Food Supply |         6041 |     -0.555556    |              0.00571429  |
| Grocery and Food Supply |         6043 |     -0.555556    |              0.0588235   |
| Grocery and Food Supply |         6045 |     -0.111111    |              0.0126582   |
| Grocery and Food Supply |         6053 |     -0.777778    |              0.00858369  |
| Grocery and Food Supply |         6055 |     -1           |              0.0188679   |
| Grocery and Food Supply |         6059 |      0.031339    |              0.0213933   |
| Grocery and Food Supply |         6061 |      0.299145    |              0.0610329   |
| Grocery and Food Supply |         6063 |     -1           |              0.0909091   |
| Grocery and Food Supply |         6065 |      0.143434    |              0.0533981   |
| Grocery and Food Supply |         6067 |     -0.555556    |              0.00328947  |
| Grocery and Food Supply |         6071 |     -0.244444    |              0.00457875  |
| Grocery and Food Supply |         6073 |     -0.0123457   |              0.0100279   |
| Grocery and Food Supply |         6075 |      0.111111    |              0.00172117  |
| Grocery and Food Supply |         6077 |     -0.407407    |              0.00759494  |
| Grocery and Food Supply |         6079 |     -0.555556    |              0.0368098   |
| Grocery and Food Supply |         6081 |     -1           |              0.00215983  |
| Grocery and Food Supply |         6083 |      0.466667    |              0.0159744   |
| Grocery and Food Supply |         6085 |     -0.333333    |              0.00186047  |
| Grocery and Food Supply |         6087 |     -1           |              0.00510204  |
| Grocery and Food Supply |         6095 |     -0.111111    |              0.0175439   |
| Grocery and Food Supply |         6097 |     -0.802469    |              0.0232558   |
| Grocery and Food Supply |         6101 |      1           |              0.016129    |
| Grocery and Food Supply |         6109 |      1           |              0.0208333   |
| Grocery and Food Supply |         6111 |     -0.111111    |              0.00697674  |
| Grocery and Food Supply |         6113 |     -0.555556    |              0.00819672  |
| Grocery and Food Supply |         8001 |      1           |              0.00384615  |
| Grocery and Food Supply |         8005 |     -0.296296    |              0.0147059   |
| Grocery and Food Supply |         8014 |      1           |              0.0434783   |
| Grocery and Food Supply |         8031 |      0.222222    |              0.00831601  |
| Grocery and Food Supply |         8035 |      0.555556    |              0.00645161  |
| Grocery and Food Supply |         8041 |      1           |              0.00273973  |
| Grocery and Food Supply |         8043 |      0.555556    |              0.0277778   |
| Grocery and Food Supply |         8123 |      0.111111    |              0.00571429  |
| Grocery and Food Supply |         9001 |      0           |              0.00611621  |
| Grocery and Food Supply |         9003 |     -0.333333    |              0.0029985   |
| Grocery and Food Supply |         9007 |      0           |              0.0168067   |
| Grocery and Food Supply |         9009 |     -0.333333    |              0.0111465   |
| Grocery and Food Supply |         9011 |     -0.111111    |              0.0106383   |
| Grocery and Food Supply |        10003 |     -1           |              0.00271739  |
| Grocery and Food Supply |        10005 |      0.288889    |              0.11194     |
| Grocery and Food Supply |        12001 |      0.555556    |              0.00645161  |
| Grocery and Food Supply |        12009 |      0.137255    |              0.0534591   |
| Grocery and Food Supply |        12011 |      0.243386    |              0.0446809   |
| Grocery and Food Supply |        12015 |      0.48659     |              0.268519    |
| Grocery and Food Supply |        12017 |     -2.15877e-17 |              0.136364    |
| Grocery and Food Supply |        12019 |     -1           |              0.0123457   |
| Grocery and Food Supply |        12021 |      0.377778    |              0.284974    |
| Grocery and Food Supply |        12027 |      0.222222    |              0.0769231   |
| Grocery and Food Supply |        12031 |     -0.185185    |              0.00612245  |
| Grocery and Food Supply |        12035 |      0.206349    |              0.134615    |
| Grocery and Food Supply |        12049 |      1           |              0.05        |
| Grocery and Food Supply |        12053 |      0.462963    |              0.11215     |
| Grocery and Food Supply |        12055 |     -0.318519    |              0.189873    |
| Grocery and Food Supply |        12057 |      0.343434    |              0.0249716   |
| Grocery and Food Supply |        12061 |     -0.111111    |              0.225806    |
| Grocery and Food Supply |        12069 |      0.176955    |              0.182432    |
| Grocery and Food Supply |        12071 |      0.173238    |              0.180934    |
| Grocery and Food Supply |        12073 |      0.777778    |              0.0112994   |
| Grocery and Food Supply |        12081 |     -0.0261438   |              0.163462    |
| Grocery and Food Supply |        12083 |      0.0493827   |              0.102857    |
| Grocery and Food Supply |        12085 |      0.308642    |              0.191489    |
| Grocery and Food Supply |        12086 |      0.244444    |              0.00941029  |
| Grocery and Food Supply |        12087 |     -0.644444    |              0.0657895   |
| Grocery and Food Supply |        12089 |      0.037037    |              0.075       |
| Grocery and Food Supply |        12091 |      0.777778    |              0.025641    |
| Grocery and Food Supply |        12093 |     -0.111111    |              0.0357143   |
| Grocery and Food Supply |        12095 |     -0.185185    |              0.008       |
| Grocery and Food Supply |        12097 |      0.407407    |              0.0394737   |
| Grocery and Food Supply |        12099 |      0.234568    |              0.193002    |
| Grocery and Food Supply |        12101 |      0.531746    |              0.0909091   |
| Grocery and Food Supply |        12103 |      0.169811    |              0.073509    |
| Grocery and Food Supply |        12105 |     -0.380952    |              0.0422961   |
| Grocery and Food Supply |        12107 |     -0.444444    |              0.0327869   |
| Grocery and Food Supply |        12109 |      0.444444    |              0.0243902   |
| Grocery and Food Supply |        12111 |     -0.309942    |              0.134752    |
| Grocery and Food Supply |        12115 |      0.231481    |              0.285714    |
| Grocery and Food Supply |        12119 |      0.777778    |              0.292683    |
| Grocery and Food Supply |        12121 |     -0.555556    |              0.0384615   |
| Grocery and Food Supply |        12123 |      0.111111    |              0.05        |
| Grocery and Food Supply |        12127 |     -0.015873    |              0.0484429   |
| Grocery and Food Supply |        13015 |      1           |              0.0204082   |
| Grocery and Food Supply |        13051 |     -1           |              0.0146341   |
| Grocery and Food Supply |        13067 |     -1           |              0.00285714  |
| Grocery and Food Supply |        13073 |      0.555556    |              0.0181818   |
| Grocery and Food Supply |        13085 |     -1           |              0.1         |
| Grocery and Food Supply |        13089 |     -0.777778    |              0.0025641   |
| Grocery and Food Supply |        13095 |     -1           |              0.0144928   |
| Grocery and Food Supply |        13121 |      1           |              0.00367647  |
| Grocery and Food Supply |        13127 |      0.111111    |              0.0181818   |
| Grocery and Food Supply |        13133 |     -0.5         |              0.210526    |
| Grocery and Food Supply |        13227 |     -0.333333    |              0.0588235   |
| Grocery and Food Supply |        13241 |     -1           |              0.0769231   |
| Grocery and Food Supply |        17001 |     -0.777778    |              0.0163934   |
| Grocery and Food Supply |        17011 |      0.111111    |              0.027027    |
| Grocery and Food Supply |        17031 |      0.0444444   |              0.00500877  |
| Grocery and Food Supply |        17043 |      0.333333    |              0.00648298  |
| Grocery and Food Supply |        17089 |     -1           |              0.00364964  |
| Grocery and Food Supply |        17097 |     -0.666667    |              0.00497512  |
| Grocery and Food Supply |        17115 |     -0.555556    |              0.010101    |
| Grocery and Food Supply |        17167 |      0.333333    |              0.00555556  |
| Grocery and Food Supply |        17177 |      0.777778    |              0.0204082   |
| Grocery and Food Supply |        17197 |      0           |              0.00508906  |
| Grocery and Food Supply |        17201 |      0.259259    |              0.0114068   |
| Grocery and Food Supply |        34003 |      0.777778    |              0.00252845  |
| Grocery and Food Supply |        34005 |     -0.277778    |              0.0143369   |
| Grocery and Food Supply |        34007 |      0           |              0.0052356   |
| Grocery and Food Supply |        34009 |      0.0555556   |              0.0879121   |
| Grocery and Food Supply |        34013 |      0.333333    |              0.00447094  |
| Grocery and Food Supply |        34015 |      0.777778    |              0.0052356   |
| Grocery and Food Supply |        34017 |      0.777778    |              0.00449438  |
| Grocery and Food Supply |        34023 |     -0.846154    |              0.0248566   |
| Grocery and Food Supply |        34025 |     -0.037037    |              0.0191898   |
| Grocery and Food Supply |        34027 |      0.111111    |              0.00338983  |
| Grocery and Food Supply |        34029 |     -0.173042    |              0.161376    |
| Grocery and Food Supply |        34031 |      0.222222    |              0.00547945  |
| Grocery and Food Supply |        34035 |     -1           |              0.00552486  |
| Grocery and Food Supply |        34041 |     -0.555556    |              0.0126582   |
| Grocery and Food Supply |        36001 |     -0.333333    |              0.00425532  |
| Grocery and Food Supply |        36005 |     -0.583333    |              0.00693241  |
| Grocery and Food Supply |        36007 |     -0.185185    |              0.0147059   |
| Grocery and Food Supply |        36015 |      0.111111    |              0.0114943   |
| Grocery and Food Supply |        36025 |     -0.777778    |              0.0181818   |
| Grocery and Food Supply |        36029 |      0.333333    |              0.0012837   |
| Grocery and Food Supply |        36041 |      1           |              0.125       |
| Grocery and Food Supply |        36043 |      0.333333    |              0.016129    |
| Grocery and Food Supply |        36047 |      0.422222    |              0.00239808  |
| Grocery and Food Supply |        36055 |     -0.444444    |              0.00328407  |
| Grocery and Food Supply |        36059 |      0.111111    |              0.00349956  |
| Grocery and Food Supply |        36061 |     -0.222222    |              0.00854701  |
| Grocery and Food Supply |        36065 |     -0.555556    |              0.00534759  |
| Grocery and Food Supply |        36067 |      0.5         |              0.0105263   |
| Grocery and Food Supply |        36071 |     -1           |              0.00362319  |
| Grocery and Food Supply |        36075 |     -1           |              0.0121951   |
| Grocery and Food Supply |        36081 |     -0.622222    |              0.00572738  |
| Grocery and Food Supply |        36083 |     -0.555556    |              0.008       |
| Grocery and Food Supply |        36085 |      0.333333    |              0.00295858  |
| Grocery and Food Supply |        36091 |     -0.444444    |              0.0143885   |
| Grocery and Food Supply |        36103 |     -0.239766    |              0.019019    |
| Grocery and Food Supply |        36113 |     -1           |              0.0212766   |
| Grocery and Food Supply |        36119 |     -0.377778    |              0.00710227  |
| Grocery and Food Supply |        42003 |     -0.0222222   |              0.00454545  |
| Grocery and Food Supply |        42011 |     -0.111111    |              0.00377358  |
| Grocery and Food Supply |        42017 |     -0.185185    |              0.00787402  |
| Grocery and Food Supply |        42019 |     -1           |              0.00833333  |
| Grocery and Food Supply |        42021 |      0.185185    |              0.0222222   |
| Grocery and Food Supply |        42029 |      0.111111    |              0.0113208   |
| Grocery and Food Supply |        42041 |     -0.777778    |              0.00662252  |
| Grocery and Food Supply |        42045 |     -1           |              0.00457666  |
| Grocery and Food Supply |        42053 |      1           |              0.375       |
| Grocery and Food Supply |        42055 |     -0.333333    |              0.011236    |
| Grocery and Food Supply |        42067 |     -0.111111    |              0.0526316   |
| Grocery and Food Supply |        42071 |      0           |              0.0122699   |
| Grocery and Food Supply |        42075 |     -0.777778    |              0.0117647   |
| Grocery and Food Supply |        42077 |      0.888889    |              0.00813008  |
| Grocery and Food Supply |        42081 |      0.333333    |              0.00884956  |
| Grocery and Food Supply |        42085 |     -0.111111    |              0.00900901  |
| Grocery and Food Supply |        42091 |     -0.111111    |              0.0107143   |
| Grocery and Food Supply |        42095 |      0.222222    |              0.00990099  |
| Grocery and Food Supply |        42101 |     -0.0833333   |              0.00598802  |
| Grocery and Food Supply |        42103 |      0.555556    |              0.0232558   |
| Grocery and Food Supply |        42133 |     -0.333333    |              0.00310559  |
| Grocery and Food Supply |        48007 |      0.703704    |              0.157895    |
| Grocery and Food Supply |        48029 |      0.333333    |              0.00184502  |
| Grocery and Food Supply |        48061 |     -0.185185    |              0.0133333   |
| Grocery and Food Supply |        48085 |     -0.111111    |              0.00422833  |
| Grocery and Food Supply |        48089 |      0.333333    |              0.0555556   |
| Grocery and Food Supply |        48113 |      0.5         |              0.00239664  |
| Grocery and Food Supply |        48121 |      0.377778    |              0.0132275   |
| Grocery and Food Supply |        48141 |     -0.222222    |              0.00779727  |
| Grocery and Food Supply |        48149 |      0.333333    |              0.04        |
| Grocery and Food Supply |        48201 |      0.0666667   |              0.00233209  |
| Grocery and Food Supply |        48215 |     -0.377778    |              0.0147493   |
| Grocery and Food Supply |        48221 |     -0.555556    |              0.0333333   |
| Grocery and Food Supply |        48225 |      1           |              0.047619    |
| Grocery and Food Supply |        48245 |      0.111111    |              0.00483092  |
| Grocery and Food Supply |        48265 |     -1           |              0.0606061   |
| Grocery and Food Supply |        48299 |      0.333333    |              0.166667    |
| Grocery and Food Supply |        48309 |      0.333333    |              0.0121212   |
| Grocery and Food Supply |        48339 |     -0.777778    |              0.00537634  |
| Grocery and Food Supply |        48343 |      1           |              0.0714286   |
| Grocery and Food Supply |        48375 |      1           |              0.0103093   |
| Grocery and Food Supply |        48403 |     -1           |              0.1         |
| Grocery and Food Supply |        48439 |      0.111111    |              0.000849618 |
| Grocery and Food Supply |        48451 |     -0.555556    |              0.0103093   |
| Grocery and Food Supply |        48453 |     -0.777778    |              0.00172414  |
| Grocery and Food Supply |        48465 |     -0.111111    |              0.0294118   |
| Grocery and Food Supply |        48479 |     -0.777778    |              0.0070922   |
| Grocery and Food Supply |        48491 |     -0.604938    |              0.037037    |
| Grocery and Food Supply |        15001 |      0.259259    |              0.0243902   |
| Grocery and Food Supply |        15003 |      0.388889    |              0.00676819  |
| Grocery and Food Supply |        15007 |      0.333333    |              0.0178571   |
| Grocery and Food Supply |        15009 |     -1           |              0.00970874  |
| Grocery and Food Supply |        18005 |      0.111111    |              0.0169492   |
| Grocery and Food Supply |        18035 |      1           |              0.00990099  |
| Grocery and Food Supply |        18081 |      1           |              0.0135135   |
| Grocery and Food Supply |        18097 |      0.555556    |              0.00474684  |
| Grocery and Food Supply |        18157 |      1           |              0.00980392  |
| Grocery and Food Supply |        18163 |      0.222222    |              0.0125786   |
| Grocery and Food Supply |        19025 |      1           |              0.0909091   |
| Grocery and Food Supply |        19059 |      0.555556    |              0.0666667   |
| Grocery and Food Supply |        19099 |      0.777778    |              0.0285714   |
| Grocery and Food Supply |        19139 |     -0.555556    |              0.0294118   |
| Grocery and Food Supply |        19155 |      0.111111    |              0.0107527   |
| Grocery and Food Supply |        19163 |      1           |              0.00806452  |
| Grocery and Food Supply |        20091 |      0.333333    |              0.00534759  |
| Grocery and Food Supply |        20177 |      1           |              0.0148148   |
| Grocery and Food Supply |        21067 |      0.111111    |              0.00961538  |
| Grocery and Food Supply |        21111 |     -0.333333    |              0.00173913  |
| Grocery and Food Supply |        21217 |      0.777778    |              0.047619    |
| Grocery and Food Supply |        22051 |      0.111111    |              0.00302115  |
| Grocery and Food Supply |        22071 |      1           |              0.00201207  |
| Grocery and Food Supply |        22127 |     -0.333333    |              0.0625      |
| Grocery and Food Supply |        23003 |      0.111111    |              0.0125      |
| Grocery and Food Supply |        23005 |      0.333333    |              0.00469484  |
| Grocery and Food Supply |        23013 |      1           |              0.0243902   |
| Grocery and Food Supply |        23031 |      0.047619    |              0.05        |
| Grocery and Food Supply |        24003 |     -0.037037    |              0.00961538  |
| Grocery and Food Supply |        24005 |      0.365079    |              0.0132325   |
| Grocery and Food Supply |        24009 |      0.333333    |              0.0222222   |
| Grocery and Food Supply |        24013 |      1           |              0.00943396  |
| Grocery and Food Supply |        24021 |     -1           |              0.00526316  |
| Grocery and Food Supply |        24029 |      1           |              0.05        |
| Grocery and Food Supply |        24031 |      0.373737    |              0.0179153   |
| Grocery and Food Supply |        24033 |      0.777778    |              0.00191205  |
| Grocery and Food Supply |        24041 |      0           |              0.0714286   |
| Grocery and Food Supply |        24045 |      1           |              0.0140845   |
| Grocery and Food Supply |        24047 |      0.62963     |              0.0625      |
| Grocery and Food Supply |        24510 |     -0.333333    |              0.00918836  |
| Grocery and Food Supply |        25001 |      0.177778    |              0.102041    |
| Grocery and Food Supply |        25003 |     -0.185185    |              0.020979    |
| Grocery and Food Supply |        25005 |      0.777778    |              0.00512821  |
| Grocery and Food Supply |        25009 |      0.333333    |              0.003663    |
| Grocery and Food Supply |        25013 |      0.333333    |              0.00296736  |
| Grocery and Food Supply |        25017 |      1           |              0.000882613 |
| Grocery and Food Supply |        25021 |     -0.037037    |              0.00632911  |
| Grocery and Food Supply |        25023 |     -0.777778    |              0.00277778  |
| Grocery and Food Supply |        25025 |      0           |              0.00309598  |
| Grocery and Food Supply |        25027 |      1           |              0.00178571  |
| Grocery and Food Supply |        26019 |      1           |              0.0714286   |
| Grocery and Food Supply |        26021 |     -0.555556    |              0.0208333   |
| Grocery and Food Supply |        26033 |     -0.333333    |              0.027027    |
| Grocery and Food Supply |        26049 |      1           |              0.00268097  |
| Grocery and Food Supply |        26081 |     -0.111111    |              0.00514139  |
| Grocery and Food Supply |        26089 |      1           |              0.0588235   |
| Grocery and Food Supply |        26093 |      1           |              0.00884956  |
| Grocery and Food Supply |        26099 |      0.888889    |              0.00318979  |
| Grocery and Food Supply |        26121 |      0.333333    |              0.0144928   |
| Grocery and Food Supply |        26125 |     -0.185185    |              0.00642398  |
| Grocery and Food Supply |        26139 |      0.037037    |              0.0193548   |
| Grocery and Food Supply |        26163 |     -0.244444    |              0.00274424  |
| Grocery and Food Supply |        27021 |      1           |              0.0357143   |
| Grocery and Food Supply |        27053 |      0.148148    |              0.0061665   |
| Grocery and Food Supply |        27091 |      0.333333    |              0.047619    |
| Grocery and Food Supply |        27099 |      1           |              0.0294118   |
| Grocery and Food Supply |        27109 |      0.222222    |              0.018018    |
| Grocery and Food Supply |        28035 |      0.111111    |              0.0188679   |
| Grocery and Food Supply |        28067 |      0.111111    |              0.0192308   |
| Grocery and Food Supply |        28141 |      0.333333    |              0.0588235   |
| Grocery and Food Supply |        29015 |     -1           |              0.0625      |
| Grocery and Food Supply |        29019 |      1           |              0.0114943   |
| Grocery and Food Supply |        29031 |      1           |              0.0178571   |
| Grocery and Food Supply |        29077 |     -0.777778    |              0.00598802  |
| Grocery and Food Supply |        29095 |     -0.111111    |              0.00547445  |
| Grocery and Food Supply |        29141 |     -0.333333    |              0.0588235   |
| Grocery and Food Supply |        29189 |      0.333333    |              0.00578035  |
| Grocery and Food Supply |        29209 |     -0.777778    |              0.0416667   |
| Grocery and Food Supply |        29213 |      0.333333    |              0.0294118   |
| Grocery and Food Supply |        30013 |     -0.333333    |              0.0138889   |
| Grocery and Food Supply |        30053 |     -0.333333    |              0.0588235   |
| Grocery and Food Supply |        30081 |      0.333333    |              0.0322581   |
| Grocery and Food Supply |        30111 |     -0.777778    |              0.00892857  |
| Grocery and Food Supply |        31055 |     -0.111111    |              0.00402414  |
| Grocery and Food Supply |        32003 |     -0.05        |              0.0309119   |
| Grocery and Food Supply |        32031 |     -0.222222    |              0.00641026  |
| Grocery and Food Supply |        33003 |      0.111111    |              0.025       |
| Grocery and Food Supply |        33009 |      0.111111    |              0.0285714   |
| Grocery and Food Supply |        33011 |     -0.777778    |              0.0037037   |
| Grocery and Food Supply |        33013 |     -0.777778    |              0.00990099  |
| Grocery and Food Supply |        33015 |      0           |              0.010989    |
| Grocery and Food Supply |        35045 |     -0.111111    |              0.0103093   |
| Grocery and Food Supply |        35049 |      0.555556    |              0.0196078   |
| Grocery and Food Supply |        35053 |     -0.333333    |              0.0833333   |
| Grocery and Food Supply |        35055 |     -0.222222    |              0.0909091   |
| Grocery and Food Supply |        37001 |     -0.777778    |              0.00884956  |
| Grocery and Food Supply |        37019 |      0.00854701  |              0.144444    |
| Grocery and Food Supply |        37031 |      0.111111    |              0.0138889   |
| Grocery and Food Supply |        37037 |      0.111111    |              0.0285714   |
| Grocery and Food Supply |        37063 |     -0.333333    |              0.00653595  |
| Grocery and Food Supply |        37071 |     -0.555556    |              0.00578035  |
| Grocery and Food Supply |        37089 |      0.377778    |              0.0694444   |
| Grocery and Food Supply |        37119 |     -0.333333    |              0.0036036   |
| Grocery and Food Supply |        37125 |      0.851852    |              0.0526316   |
| Grocery and Food Supply |        37131 |     -0.111111    |              0.0454545   |
| Grocery and Food Supply |        37161 |      0.555556    |              0.0192308   |
| Grocery and Food Supply |        37175 |     -1           |              0.04        |
| Grocery and Food Supply |        38051 |      1           |              0.333333    |
| Grocery and Food Supply |        39021 |      0.333333    |              0.0294118   |
| Grocery and Food Supply |        39023 |     -0.111111    |              0.0147059   |
| Grocery and Food Supply |        39025 |      0.777778    |              0.00847458  |
| Grocery and Food Supply |        39035 |      0.185185    |              0.00516351  |
| Grocery and Food Supply |        39037 |      1           |              0.0192308   |
| Grocery and Food Supply |        39041 |      1           |              0.0113636   |
| Grocery and Food Supply |        39043 |     -0.333333    |              0.0428571   |
| Grocery and Food Supply |        39049 |      0.666667    |              0.00225479  |
| Grocery and Food Supply |        39061 |     -1           |              0.00143472  |
| Grocery and Food Supply |        39081 |      0.333333    |              0.0149254   |
| Grocery and Food Supply |        39085 |      1           |              0.00645161  |
| Grocery and Food Supply |        39099 |      0.111111    |              0.0185185   |
| Grocery and Food Supply |        39113 |     -0.333333    |              0.0047619   |
| Grocery and Food Supply |        39119 |      0.111111    |              0.0133333   |
| Grocery and Food Supply |        39121 |     -0.111111    |              0.0833333   |
| Grocery and Food Supply |        39123 |      0.222222    |              0.0465116   |
| Grocery and Food Supply |        39131 |      1           |              0.0454545   |
| Grocery and Food Supply |        39153 |     -0.185185    |              0.00663717  |
| Grocery and Food Supply |        39165 |     -0.555556    |              0.00925926  |
| Grocery and Food Supply |        39169 |      0.777778    |              0.0120482   |
| Grocery and Food Supply |        41005 |      0.333333    |              0.00460829  |
| Grocery and Food Supply |        41011 |     -0.111111    |              0.03125     |
| Grocery and Food Supply |        41015 |      0.333333    |              0.176471    |
| Grocery and Food Supply |        41017 |     -0.925926    |              0.0352941   |
| Grocery and Food Supply |        41019 |     -0.111111    |              0.0235294   |
| Grocery and Food Supply |        41029 |     -0.037037    |              0.023622    |
| Grocery and Food Supply |        41033 |     -1           |              0.0185185   |
| Grocery and Food Supply |        41039 |      0.666667    |              0.0155039   |
| Grocery and Food Supply |        41047 |     -0.222222    |              0.0104167   |
| Grocery and Food Supply |        41051 |      0.777778    |              0.00191939  |
| Grocery and Food Supply |        41057 |     -1           |              0.0344828   |
| Grocery and Food Supply |        41059 |      0.333333    |              0.015625    |
| Grocery and Food Supply |        41067 |      0.0666667   |              0.0165017   |
| Grocery and Food Supply |        44001 |      1           |              0.0263158   |
| Grocery and Food Supply |        44007 |      0.407407    |              0.00601202  |
| Grocery and Food Supply |        44009 |     -0.333333    |              0.0425532   |
| Grocery and Food Supply |        45001 |      1           |              0.047619    |
| Grocery and Food Supply |        45013 |      0.0877193   |              0.169643    |
| Grocery and Food Supply |        45019 |     -0.288889    |              0.0212766   |
| Grocery and Food Supply |        45029 |     -0.333333    |              0.0322581   |
| Grocery and Food Supply |        45043 |      0.555556    |              0.0217391   |
| Grocery and Food Supply |        45051 |      0.5         |              0.0268456   |
| Grocery and Food Supply |        45055 |     -0.777778    |              0.0232558   |
| Grocery and Food Supply |        45065 |     -0.222222    |              0.25        |
| Grocery and Food Supply |        45073 |     -0.62963     |              0.0576923   |
| Grocery and Food Supply |        46081 |     -0.555556    |              0.0588235   |
| Grocery and Food Supply |        47035 |      0.111111    |              0.09375     |
| Grocery and Food Supply |        47065 |     -0.111111    |              0.00404858  |
| Grocery and Food Supply |        47105 |     -0.444444    |              0.129032    |
| Grocery and Food Supply |        47155 |      1           |              0.0227273   |
| Grocery and Food Supply |        47157 |      1           |              0.00318471  |
| Grocery and Food Supply |        47163 |     -0.555556    |              0.018018    |
| Grocery and Food Supply |        49043 |     -0.333333    |              0.0277778   |
| Grocery and Food Supply |        49049 |     -1           |              0.00289855  |
| Grocery and Food Supply |        49053 |     -0.777778    |              0.0175439   |
| Grocery and Food Supply |        50025 |      0.555556    |              0.0208333   |
| Grocery and Food Supply |        51003 |      0.111111    |              0.0151515   |
| Grocery and Food Supply |        51013 |      0.333333    |              0.0110497   |
| Grocery and Food Supply |        51019 |     -0.555556    |              0.0208333   |
| Grocery and Food Supply |        51087 |     -0.185185    |              0.0175439   |
| Grocery and Food Supply |        51095 |      0.111111    |              0.0740741   |
| Grocery and Food Supply |        51103 |      1           |              0.230769    |
| Grocery and Food Supply |        51107 |      0.888889    |              0.0122699   |
| Grocery and Food Supply |        51125 |      1           |              0.0833333   |
| Grocery and Food Supply |        51133 |      0.555556    |              0.153846    |
| Grocery and Food Supply |        51135 |     -0.111111    |              0.125       |
| Grocery and Food Supply |        51153 |      0.222222    |              0.026087    |
| Grocery and Food Supply |        51161 |     -0.777778    |              0.0185185   |
| Grocery and Food Supply |        51510 |      1           |              0.0188679   |
| Grocery and Food Supply |        51710 |     -0.777778    |              0.00529101  |
| Grocery and Food Supply |        51760 |      0.111111    |              0.00621118  |
| Grocery and Food Supply |        51775 |      0.555556    |              0.05        |
| Grocery and Food Supply |        51810 |     -0.888889    |              0.00662252  |
| Grocery and Food Supply |        53005 |      1           |              0.00729927  |
| Grocery and Food Supply |        53009 |      0.407407    |              0.0545455   |
| Grocery and Food Supply |        53011 |     -0.111111    |              0.00357143  |
| Grocery and Food Supply |        53015 |      0.111111    |              0.0224719   |
| Grocery and Food Supply |        53027 |     -0.333333    |              0.016129    |
| Grocery and Food Supply |        53031 |      0.259259    |              0.111111    |
| Grocery and Food Supply |        53033 |      0.0555556   |              0.00281294  |
| Grocery and Food Supply |        53041 |     -0.444444    |              0.0322581   |
| Grocery and Food Supply |        53045 |     -0.444444    |              0.0408163   |
| Grocery and Food Supply |        53053 |      0.481481    |              0.00535714  |
| Grocery and Food Supply |        53061 |      0.777778    |              0.00199601  |
| Grocery and Food Supply |        53063 |      0.444444    |              0.00621118  |
| Grocery and Food Supply |        53067 |      0.407407    |              0.0186335   |
| Grocery and Food Supply |        53071 |      0.777778    |              0.0232558   |
| Grocery and Food Supply |        53073 |     -0.111111    |              0.00980392  |
| Grocery and Food Supply |        53077 |      0.333333    |              0.00671141  |
| Grocery and Food Supply |        54063 |      0.555556    |              0.0833333   |
| Grocery and Food Supply |        54069 |      0.777778    |              0.0208333   |
| Grocery and Food Supply |        54083 |      0.111111    |              0.037037    |
| Grocery and Food Supply |        54109 |      0.111111    |              0.0526316   |
| Grocery and Food Supply |        55025 |      0.333333    |              0.00322581  |
| Grocery and Food Supply |        55027 |      1           |              0.0149254   |
| Grocery and Food Supply |        55047 |      0.777778    |              0.05        |
| Grocery and Food Supply |        55071 |      1           |              0.0133333   |
| Grocery and Food Supply |        55079 |      0.111111    |              0.00232829  |
| Grocery and Food Supply |        55087 |      0.555556    |              0.00763359  |
| Grocery and Food Supply |        55089 |      1           |              0.0163934   |
| Grocery and Food Supply |        55131 |     -0.333333    |              0.0120482   |
| Grocery and Food Supply |        55133 |      0.333333    |              0.00334448  |
| Grocery and Food Supply |        72005 |     -1           |              0.0222222   |
| Grocery and Food Supply |        72031 |     -0.555556    |              0.008       |
| Grocery and Food Supply |        72033 |     -0.777778    |              0.0344828   |
| Grocery and Food Supply |        72057 |      1           |              0.030303    |
| Grocery and Food Supply |        72079 |     -0.111111    |              0.0555556   |
| Grocery and Food Supply |        72097 |     -0.111111    |              0.0142857   |
| Grocery and Food Supply |        72113 |      1           |              0.00746269  |
| Grocery and Food Supply |        72127 |     -0.666667    |              0.00542005  |
| Grocery and Food Supply |        72145 |      1           |              0.0263158   |
| Housing and Real Estate |         1003 |      0.407407    |              0.0319149   |
| Housing and Real Estate |         1015 |     -0.333333    |              0.010989    |
| Housing and Real Estate |         1073 |     -0.555556    |              0.0019305   |
| Housing and Real Estate |         1077 |     -0.111111    |              0.0136986   |
| Housing and Real Estate |         1089 |      1           |              0.0052356   |
| Housing and Real Estate |         1097 |      0.333333    |              0.00371747  |
| Housing and Real Estate |         1101 |     -0.777778    |              0.00502513  |
| Housing and Real Estate |         4003 |     -0.111111    |              0.00980392  |
| Housing and Real Estate |         4005 |     -0.333333    |              0.0204082   |
| Housing and Real Estate |         4007 |      0.555556    |              0.0444444   |
| Housing and Real Estate |         4012 |      0.777778    |              0.272727    |
| Housing and Real Estate |         4013 |      0.231856    |              0.0690619   |
| Housing and Real Estate |         4015 |     -0.333333    |              0.059322    |
| Housing and Real Estate |         4019 |     -0.496732    |              0.0539683   |
| Housing and Real Estate |         4021 |      0.263889    |              0.080402    |
| Housing and Real Estate |         4025 |      0.111111    |              0.0964912   |
| Housing and Real Estate |         4027 |     -0.212121    |              0.15493     |
| Housing and Real Estate |         5005 |      1           |              0.0333333   |
| Housing and Real Estate |         5007 |     -0.777778    |              0.00724638  |
| Housing and Real Estate |         5023 |      1           |              0.0454545   |
| Housing and Real Estate |         5049 |      1           |              0.0833333   |
| Housing and Real Estate |         5051 |     -0.037037    |              0.0428571   |
| Housing and Real Estate |         5107 |     -0.555556    |              0.0416667   |
| Housing and Real Estate |         5125 |     -0.555556    |              0.0327869   |
| Housing and Real Estate |         5135 |      0.555556    |              0.111111    |
| Housing and Real Estate |         5141 |     -1           |              0.0769231   |
| Housing and Real Estate |         6005 |      0.555556    |              0.0357143   |
| Housing and Real Estate |         6007 |     -0.333333    |              0.0102564   |
| Housing and Real Estate |         6009 |      0.777778    |              0.0333333   |
| Housing and Real Estate |         6013 |      0.0888889   |              0.0156986   |
| Housing and Real Estate |         6019 |      0.888889    |              0.00339559  |
| Housing and Real Estate |         6025 |     -0.555556    |              0.0208333   |
| Housing and Real Estate |         6029 |     -0.0666667   |              0.0109649   |
| Housing and Real Estate |         6037 |     -0.030303    |              0.00171206  |
| Housing and Real Estate |         6039 |      0.111111    |              0.0125      |
| Housing and Real Estate |         6041 |     -1           |              0.00571429  |
| Housing and Real Estate |         6043 |      1           |              0.0588235   |
| Housing and Real Estate |         6045 |      0.111111    |              0.0126582   |
| Housing and Real Estate |         6053 |      0.111111    |              0.00858369  |
| Housing and Real Estate |         6055 |     -0.777778    |              0.0283019   |
| Housing and Real Estate |         6059 |      0.242165    |              0.0213933   |
| Housing and Real Estate |         6061 |     -0.025641    |              0.0610329   |
| Housing and Real Estate |         6063 |      0.111111    |              0.0909091   |
| Housing and Real Estate |         6065 |      0.232323    |              0.0533981   |
| Housing and Real Estate |         6067 |     -0.111111    |              0.00328947  |
| Housing and Real Estate |         6071 |     -0.511111    |              0.00457875  |
| Housing and Real Estate |         6073 |      0.308642    |              0.0100279   |
| Housing and Real Estate |         6075 |      1           |              0.00172117  |
| Housing and Real Estate |         6077 |      0.481481    |              0.00759494  |
| Housing and Real Estate |         6079 |     -0.185185    |              0.0368098   |
| Housing and Real Estate |         6081 |     -0.333333    |              0.00215983  |
| Housing and Real Estate |         6083 |      0.244444    |              0.0159744   |
| Housing and Real Estate |         6085 |     -0.925926    |              0.0027907   |
| Housing and Real Estate |         6087 |     -1           |              0.00510204  |
| Housing and Real Estate |         6095 |     -0.0666667   |              0.0175439   |
| Housing and Real Estate |         6097 |     -0.407407    |              0.0232558   |
| Housing and Real Estate |         6101 |      1           |              0.016129    |
| Housing and Real Estate |         6107 |     -0.555556    |              0.0037037   |
| Housing and Real Estate |         6109 |      1           |              0.0208333   |
| Housing and Real Estate |         6111 |     -0.111111    |              0.00697674  |
| Housing and Real Estate |         6113 |     -0.111111    |              0.00819672  |
| Housing and Real Estate |         8001 |      1           |              0.00384615  |
| Housing and Real Estate |         8005 |      0.037037    |              0.0147059   |
| Housing and Real Estate |         8014 |     -0.777778    |              0.0434783   |
| Housing and Real Estate |         8031 |      0.5         |              0.00831601  |
| Housing and Real Estate |         8035 |      0.777778    |              0.00645161  |
| Housing and Real Estate |         8041 |     -0.333333    |              0.00273973  |
| Housing and Real Estate |         8043 |     -0.333333    |              0.0277778   |
| Housing and Real Estate |         8123 |     -0.777778    |              0.00571429  |
| Housing and Real Estate |         9001 |      0.555556    |              0.00611621  |
| Housing and Real Estate |         9003 |      0.222222    |              0.0029985   |
| Housing and Real Estate |         9007 |     -0.444444    |              0.0168067   |
| Housing and Real Estate |         9009 |     -0.138889    |              0.0127389   |
| Housing and Real Estate |         9011 |      0.333333    |              0.0106383   |
| Housing and Real Estate |        10003 |     -0.777778    |              0.00271739  |
| Housing and Real Estate |        10005 |      0.333333    |              0.134328    |
| Housing and Real Estate |        12001 |      0.777778    |              0.00645161  |
| Housing and Real Estate |        12009 |     -0.00653595  |              0.0534591   |
| Housing and Real Estate |        12011 |      0.195767    |              0.0446809   |
| Housing and Real Estate |        12015 |     -0.356322    |              0.268519    |
| Housing and Real Estate |        12017 |      0.037037    |              0.136364    |
| Housing and Real Estate |        12019 |     -0.777778    |              0.0123457   |
| Housing and Real Estate |        12021 |      0.519192    |              0.284974    |
| Housing and Real Estate |        12027 |      0.222222    |              0.0769231   |
| Housing and Real Estate |        12031 |     -0.703704    |              0.00612245  |
| Housing and Real Estate |        12035 |      0.555556    |              0.134615    |
| Housing and Real Estate |        12049 |      1           |              0.05        |
| Housing and Real Estate |        12053 |      0.314815    |              0.11215     |
| Housing and Real Estate |        12055 |     -0.0138889   |              0.202532    |
| Housing and Real Estate |        12057 |      0.151515    |              0.0249716   |
| Housing and Real Estate |        12061 |     -0.0899471   |              0.225806    |
| Housing and Real Estate |        12069 |      0.176955    |              0.182432    |
| Housing and Real Estate |        12071 |      0.142174    |              0.180934    |
| Housing and Real Estate |        12073 |      0.777778    |              0.0112994   |
| Housing and Real Estate |        12081 |     -0.0130719   |              0.163462    |
| Housing and Real Estate |        12083 |      0.246914    |              0.102857    |
| Housing and Real Estate |        12085 |      0.320988    |              0.191489    |
| Housing and Real Estate |        12086 |      0.688889    |              0.00941029  |
| Housing and Real Estate |        12087 |     -0.644444    |              0.0657895   |
| Housing and Real Estate |        12089 |      0.777778    |              0.075       |
| Housing and Real Estate |        12091 |      0.777778    |              0.025641    |
| Housing and Real Estate |        12093 |      1           |              0.0357143   |
| Housing and Real Estate |        12095 |     -0.037037    |              0.008       |
| Housing and Real Estate |        12097 |      0.259259    |              0.0394737   |
| Housing and Real Estate |        12099 |      0.333333    |              0.194131    |
| Housing and Real Estate |        12101 |      0.492063    |              0.0909091   |
| Housing and Real Estate |        12103 |      0.136268    |              0.073509    |
| Housing and Real Estate |        12105 |     -0.333333    |              0.0422961   |
| Housing and Real Estate |        12107 |      0           |              0.0327869   |
| Housing and Real Estate |        12109 |      0.333333    |              0.0243902   |
| Housing and Real Estate |        12111 |     -0.0877193   |              0.134752    |
| Housing and Real Estate |        12115 |     -0.0987654   |              0.285714    |
| Housing and Real Estate |        12119 |      0.685185    |              0.292683    |
| Housing and Real Estate |        12121 |     -0.555556    |              0.0384615   |
| Housing and Real Estate |        12123 |     -0.111111    |              0.05        |
| Housing and Real Estate |        12127 |     -0.174603    |              0.0484429   |
| Housing and Real Estate |        13015 |      1           |              0.0204082   |
| Housing and Real Estate |        13051 |     -1           |              0.0146341   |
| Housing and Real Estate |        13067 |     -0.777778    |              0.00285714  |
| Housing and Real Estate |        13073 |      0.333333    |              0.0181818   |
| Housing and Real Estate |        13085 |     -0.777778    |              0.1         |
| Housing and Real Estate |        13089 |      0.777778    |              0.0025641   |
| Housing and Real Estate |        13121 |      0.888889    |              0.00367647  |
| Housing and Real Estate |        13127 |     -0.777778    |              0.0181818   |
| Housing and Real Estate |        13133 |      0.777778    |              0.210526    |
| Housing and Real Estate |        13227 |     -0.777778    |              0.0588235   |
| Housing and Real Estate |        13241 |      1           |              0.0769231   |
| Housing and Real Estate |        17001 |     -0.333333    |              0.0163934   |
| Housing and Real Estate |        17011 |      1           |              0.027027    |
| Housing and Real Estate |        17031 |     -0.0222222   |              0.00500877  |
| Housing and Real Estate |        17043 |      0.277778    |              0.00648298  |
| Housing and Real Estate |        17089 |     -1           |              0.00364964  |
| Housing and Real Estate |        17097 |      0.444444    |              0.00497512  |
| Housing and Real Estate |        17115 |      0.333333    |              0.010101    |
| Housing and Real Estate |        17167 |      1           |              0.00555556  |
| Housing and Real Estate |        17177 |      1           |              0.0204082   |
| Housing and Real Estate |        17197 |     -0.222222    |              0.00508906  |
| Housing and Real Estate |        17201 |     -0.259259    |              0.0114068   |
| Housing and Real Estate |        34003 |     -0.444444    |              0.00252845  |
| Housing and Real Estate |        34005 |     -0.277778    |              0.0143369   |
| Housing and Real Estate |        34007 |      0.222222    |              0.0052356   |
| Housing and Real Estate |        34009 |     -0.209877    |              0.0989011   |
| Housing and Real Estate |        34013 |      0.333333    |              0.00447094  |
| Housing and Real Estate |        34015 |      0.555556    |              0.0052356   |
| Housing and Real Estate |        34017 |      0.444444    |              0.00449438  |
| Housing and Real Estate |        34023 |     -0.880342    |              0.0248566   |
| Housing and Real Estate |        34025 |      0.580247    |              0.0191898   |
| Housing and Real Estate |        34027 |     -0.333333    |              0.00338983  |
| Housing and Real Estate |        34029 |     -0.204301    |              0.164021    |
| Housing and Real Estate |        34031 |      0.333333    |              0.00547945  |
| Housing and Real Estate |        34035 |     -0.333333    |              0.00552486  |
| Housing and Real Estate |        34041 |     -0.777778    |              0.0126582   |
| Housing and Real Estate |        36001 |     -0.111111    |              0.00425532  |
| Housing and Real Estate |        36005 |      0.0555556   |              0.00693241  |
| Housing and Real Estate |        36007 |      0.111111    |              0.0147059   |
| Housing and Real Estate |        36015 |      0.333333    |              0.0114943   |
| Housing and Real Estate |        36025 |      0.111111    |              0.0181818   |
| Housing and Real Estate |        36029 |      1           |              0.0012837   |
| Housing and Real Estate |        36041 |      1           |              0.125       |
| Housing and Real Estate |        36043 |      1           |              0.016129    |
| Housing and Real Estate |        36047 |      0.511111    |              0.00239808  |
| Housing and Real Estate |        36055 |     -0.777778    |              0.00164204  |
| Housing and Real Estate |        36059 |      0.555556    |              0.00349956  |
| Housing and Real Estate |        36061 |     -0.288889    |              0.00854701  |
| Housing and Real Estate |        36065 |     -0.111111    |              0.00534759  |
| Housing and Real Estate |        36067 |     -0.166667    |              0.0105263   |
| Housing and Real Estate |        36071 |     -0.777778    |              0.00362319  |
| Housing and Real Estate |        36075 |     -0.111111    |              0.0121951   |
| Housing and Real Estate |        36081 |     -0.0555556   |              0.0045819   |
| Housing and Real Estate |        36083 |      0.333333    |              0.008       |
| Housing and Real Estate |        36085 |      1           |              0.00295858  |
| Housing and Real Estate |        36091 |      0.666667    |              0.0143885   |
| Housing and Real Estate |        36103 |     -0.204678    |              0.019019    |
| Housing and Real Estate |        36113 |     -0.777778    |              0.0212766   |
| Housing and Real Estate |        36119 |      0.0666667   |              0.00710227  |
| Housing and Real Estate |        42003 |     -0.0222222   |              0.00454545  |
| Housing and Real Estate |        42011 |     -0.111111    |              0.00377358  |
| Housing and Real Estate |        42017 |      0.111111    |              0.00787402  |
| Housing and Real Estate |        42019 |     -0.555556    |              0.00833333  |
| Housing and Real Estate |        42021 |      0.111111    |              0.0222222   |
| Housing and Real Estate |        42029 |      0.185185    |              0.0113208   |
| Housing and Real Estate |        42041 |     -0.333333    |              0.00662252  |
| Housing and Real Estate |        42045 |     -0.888889    |              0.00457666  |
| Housing and Real Estate |        42053 |      1           |              0.375       |
| Housing and Real Estate |        42055 |      0.111111    |              0.011236    |
| Housing and Real Estate |        42067 |      1           |              0.0526316   |
| Housing and Real Estate |        42071 |      0.0555556   |              0.0122699   |
| Housing and Real Estate |        42075 |     -0.555556    |              0.0117647   |
| Housing and Real Estate |        42077 |      0.333333    |              0.00813008  |
| Housing and Real Estate |        42081 |      0.111111    |              0.00884956  |
| Housing and Real Estate |        42085 |      0.111111    |              0.00900901  |
| Housing and Real Estate |        42091 |      0.0740741   |              0.0107143   |
| Housing and Real Estate |        42095 |      0.888889    |              0.00990099  |
| Housing and Real Estate |        42101 |     -0.194444    |              0.00598802  |
| Housing and Real Estate |        42103 |      1           |              0.0232558   |
| Housing and Real Estate |        42133 |      0.333333    |              0.00310559  |
| Housing and Real Estate |        48007 |      0.703704    |              0.157895    |
| Housing and Real Estate |        48029 |      0.888889    |              0.00184502  |
| Housing and Real Estate |        48061 |     -0.037037    |              0.0133333   |
| Housing and Real Estate |        48085 |     -0.333333    |              0.00422833  |
| Housing and Real Estate |        48089 |      1           |              0.0555556   |
| Housing and Real Estate |        48113 |      0.5         |              0.00239664  |
| Housing and Real Estate |        48121 |      0.288889    |              0.0132275   |
| Housing and Real Estate |        48141 |      0.222222    |              0.00779727  |
| Housing and Real Estate |        48149 |      0.777778    |              0.04        |
| Housing and Real Estate |        48201 |      0.511111    |              0.00233209  |
| Housing and Real Estate |        48215 |     -0.333333    |              0.0147493   |
| Housing and Real Estate |        48221 |     -0.111111    |              0.0333333   |
| Housing and Real Estate |        48225 |      0.555556    |              0.047619    |
| Housing and Real Estate |        48245 |      0.333333    |              0.00483092  |
| Housing and Real Estate |        48265 |     -0.555556    |              0.0606061   |
| Housing and Real Estate |        48299 |      1           |              0.166667    |
| Housing and Real Estate |        48309 |      0.333333    |              0.0121212   |
| Housing and Real Estate |        48339 |     -0.333333    |              0.00537634  |
| Housing and Real Estate |        48343 |      0.555556    |              0.0714286   |
| Housing and Real Estate |        48375 |      1           |              0.0103093   |
| Housing and Real Estate |        48403 |     -1           |              0.1         |
| Housing and Real Estate |        48439 |      0.555556    |              0.000849618 |
| Housing and Real Estate |        48451 |     -0.333333    |              0.0103093   |
| Housing and Real Estate |        48453 |     -0.777778    |              0.00172414  |
| Housing and Real Estate |        48465 |     -0.333333    |              0.0294118   |
| Housing and Real Estate |        48479 |     -0.333333    |              0.0070922   |
| Housing and Real Estate |        48491 |     -0.432099    |              0.037037    |
| Housing and Real Estate |        15001 |      0.777778    |              0.0243902   |
| Housing and Real Estate |        15003 |      0.444444    |              0.00676819  |
| Housing and Real Estate |        15007 |      0.777778    |              0.0178571   |
| Housing and Real Estate |        15009 |     -0.111111    |              0.00970874  |
| Housing and Real Estate |        18005 |      1           |              0.0169492   |
| Housing and Real Estate |        18035 |      1           |              0.00990099  |
| Housing and Real Estate |        18081 |      0.555556    |              0.0135135   |
| Housing and Real Estate |        18097 |      0.481481    |              0.00474684  |
| Housing and Real Estate |        18157 |     -0.111111    |              0.00980392  |
| Housing and Real Estate |        18163 |     -0.333333    |              0.0125786   |
| Housing and Real Estate |        19025 |      1           |              0.0909091   |
| Housing and Real Estate |        19059 |      0.777778    |              0.0666667   |
| Housing and Real Estate |        19099 |      0.555556    |              0.0285714   |
| Housing and Real Estate |        19139 |     -0.333333    |              0.0294118   |
| Housing and Real Estate |        19155 |      0.333333    |              0.0107527   |
| Housing and Real Estate |        19163 |      0.555556    |              0.00806452  |
| Housing and Real Estate |        20091 |      0.222222    |              0.00534759  |
| Housing and Real Estate |        20177 |      0.666667    |              0.0148148   |
| Housing and Real Estate |        21067 |     -0.777778    |              0.00961538  |
| Housing and Real Estate |        21111 |     -0.777778    |              0.00173913  |
| Housing and Real Estate |        21217 |      0.555556    |              0.047619    |
| Housing and Real Estate |        22051 |     -0.555556    |              0.00302115  |
| Housing and Real Estate |        22071 |      0.555556    |              0.00201207  |
| Housing and Real Estate |        22127 |      0.111111    |              0.0625      |
| Housing and Real Estate |        23003 |      0.333333    |              0.0125      |
| Housing and Real Estate |        23005 |     -0.555556    |              0.00469484  |
| Housing and Real Estate |        23013 |      0.111111    |              0.0243902   |
| Housing and Real Estate |        23031 |      0.365079    |              0.05        |
| Housing and Real Estate |        24003 |      0.259259    |              0.00961538  |
| Housing and Real Estate |        24005 |     -0.015873    |              0.0132325   |
| Housing and Real Estate |        24009 |      1           |              0.0222222   |
| Housing and Real Estate |        24013 |      0.777778    |              0.00943396  |
| Housing and Real Estate |        24021 |     -0.777778    |              0.0105263   |
| Housing and Real Estate |        24029 |      0.777778    |              0.05        |
| Housing and Real Estate |        24031 |      0.296296    |              0.019544    |
| Housing and Real Estate |        24033 |      1           |              0.00191205  |
| Housing and Real Estate |        24041 |     -0.111111    |              0.0714286   |
| Housing and Real Estate |        24045 |      1           |              0.0140845   |
| Housing and Real Estate |        24047 |      0.407407    |              0.0625      |
| Housing and Real Estate |        24510 |     -0.148148    |              0.00918836  |
| Housing and Real Estate |        25001 |      0.133333    |              0.102041    |
| Housing and Real Estate |        25003 |     -0.333333    |              0.020979    |
| Housing and Real Estate |        25005 |      0.666667    |              0.00512821  |
| Housing and Real Estate |        25009 |      0.111111    |              0.003663    |
| Housing and Real Estate |        25013 |     -0.111111    |              0.00296736  |
| Housing and Real Estate |        25017 |      0.777778    |              0.000882613 |
| Housing and Real Estate |        25021 |      0.333333    |              0.00632911  |
| Housing and Real Estate |        25023 |     -0.555556    |              0.00277778  |
| Housing and Real Estate |        25025 |     -0.259259    |              0.00464396  |
| Housing and Real Estate |        25027 |      1           |              0.00178571  |
| Housing and Real Estate |        26019 |      1           |              0.0714286   |
| Housing and Real Estate |        26021 |     -0.333333    |              0.0208333   |
| Housing and Real Estate |        26033 |     -0.333333    |              0.027027    |
| Housing and Real Estate |        26049 |      0.555556    |              0.00268097  |
| Housing and Real Estate |        26081 |      0           |              0.00514139  |
| Housing and Real Estate |        26089 |      1           |              0.0588235   |
| Housing and Real Estate |        26093 |      0.555556    |              0.00884956  |
| Housing and Real Estate |        26099 |      0.555556    |              0.00318979  |
| Housing and Real Estate |        26121 |     -0.222222    |              0.0144928   |
| Housing and Real Estate |        26125 |      0.037037    |              0.00642398  |
| Housing and Real Estate |        26139 |      0.111111    |              0.0193548   |
| Housing and Real Estate |        26163 |      0.244444    |              0.00274424  |
| Housing and Real Estate |        27021 |      1           |              0.0357143   |
| Housing and Real Estate |        27053 |      0.52381     |              0.00719424  |
| Housing and Real Estate |        27091 |      0.333333    |              0.047619    |
| Housing and Real Estate |        27099 |      1           |              0.0294118   |
| Housing and Real Estate |        27109 |      0.222222    |              0.018018    |
| Housing and Real Estate |        28035 |      0.777778    |              0.0188679   |
| Housing and Real Estate |        28067 |      0.333333    |              0.0192308   |
| Housing and Real Estate |        28141 |      1           |              0.0588235   |
| Housing and Real Estate |        29015 |     -1           |              0.0625      |
| Housing and Real Estate |        29019 |     -0.111111    |              0.0114943   |
| Housing and Real Estate |        29031 |      0.555556    |              0.0178571   |
| Housing and Real Estate |        29077 |      1           |              0.00598802  |
| Housing and Real Estate |        29095 |      0.333333    |              0.00547445  |
| Housing and Real Estate |        29141 |      1           |              0.0588235   |
| Housing and Real Estate |        29189 |      0.444444    |              0.00578035  |
| Housing and Real Estate |        29209 |      0.777778    |              0.0416667   |
| Housing and Real Estate |        29213 |      0.333333    |              0.0294118   |
| Housing and Real Estate |        30013 |      0.777778    |              0.0138889   |
| Housing and Real Estate |        30053 |      1           |              0.0588235   |
| Housing and Real Estate |        30081 |      0.555556    |              0.0322581   |
| Housing and Real Estate |        30111 |      0.111111    |              0.00892857  |
| Housing and Real Estate |        31055 |      0.185185    |              0.00603622  |
| Housing and Real Estate |        32003 |      0.0582011   |              0.0324575   |
| Housing and Real Estate |        32031 |     -0.111111    |              0.00641026  |
| Housing and Real Estate |        33003 |     -0.333333    |              0.025       |
| Housing and Real Estate |        33009 |      0.111111    |              0.0142857   |
| Housing and Real Estate |        33011 |     -0.111111    |              0.0037037   |
| Housing and Real Estate |        33013 |     -0.333333    |              0.00990099  |
| Housing and Real Estate |        33015 |      0.666667    |              0.010989    |
| Housing and Real Estate |        35045 |      1           |              0.0103093   |
| Housing and Real Estate |        35049 |      0.333333    |              0.0196078   |
| Housing and Real Estate |        35053 |      1           |              0.0833333   |
| Housing and Real Estate |        35055 |      0.111111    |              0.0909091   |
| Housing and Real Estate |        37019 |      0.425926    |              0.133333    |
| Housing and Real Estate |        37031 |      0.111111    |              0.0138889   |
| Housing and Real Estate |        37037 |      0.333333    |              0.0285714   |
| Housing and Real Estate |        37063 |     -0.777778    |              0.00653595  |
| Housing and Real Estate |        37071 |      0.777778    |              0.00578035  |
| Housing and Real Estate |        37089 |      0.0666667   |              0.0694444   |
| Housing and Real Estate |        37119 |      0           |              0.0036036   |
| Housing and Real Estate |        37125 |      0.62963     |              0.0526316   |
| Housing and Real Estate |        37131 |      0.777778    |              0.0454545   |
| Housing and Real Estate |        37161 |      0.111111    |              0.0192308   |
| Housing and Real Estate |        37175 |     -0.777778    |              0.04        |
| Housing and Real Estate |        38051 |      1           |              0.333333    |
| Housing and Real Estate |        39021 |      0.111111    |              0.0294118   |
| Housing and Real Estate |        39023 |      0.111111    |              0.0147059   |
| Housing and Real Estate |        39025 |      1           |              0.00847458  |
| Housing and Real Estate |        39035 |      0.222222    |              0.00516351  |
| Housing and Real Estate |        39037 |      1           |              0.0192308   |
| Housing and Real Estate |        39041 |      1           |              0.0113636   |
| Housing and Real Estate |        39043 |     -0.555556    |              0.0428571   |
| Housing and Real Estate |        39049 |      1           |              0.00225479  |
| Housing and Real Estate |        39061 |      0.777778    |              0.00143472  |
| Housing and Real Estate |        39081 |      0.555556    |              0.0149254   |
| Housing and Real Estate |        39085 |     -0.555556    |              0.00645161  |
| Housing and Real Estate |        39099 |     -0.444444    |              0.0185185   |
| Housing and Real Estate |        39113 |      0.111111    |              0.0047619   |
| Housing and Real Estate |        39119 |      0.111111    |              0.0133333   |
| Housing and Real Estate |        39121 |      1           |              0.0833333   |
| Housing and Real Estate |        39123 |      0.333333    |              0.0465116   |
| Housing and Real Estate |        39131 |      1           |              0.0454545   |
| Housing and Real Estate |        39153 |      0.333333    |              0.00663717  |
| Housing and Real Estate |        39165 |     -0.777778    |              0.00925926  |
| Housing and Real Estate |        39169 |      0.555556    |              0.0120482   |
| Housing and Real Estate |        41005 |     -0.555556    |              0.00460829  |
| Housing and Real Estate |        41011 |      0           |              0.03125     |
| Housing and Real Estate |        41015 |      0.333333    |              0.176471    |
| Housing and Real Estate |        41017 |     -0.62963     |              0.0352941   |
| Housing and Real Estate |        41019 |      0.555556    |              0.0117647   |
| Housing and Real Estate |        41029 |      0.185185    |              0.023622    |
| Housing and Real Estate |        41033 |     -0.777778    |              0.0185185   |
| Housing and Real Estate |        41039 |     -0.333333    |              0.0155039   |
| Housing and Real Estate |        41047 |     -0.777778    |              0.0104167   |
| Housing and Real Estate |        41051 |     -0.555556    |              0.00191939  |
| Housing and Real Estate |        41057 |      1           |              0.0344828   |
| Housing and Real Estate |        41059 |     -0.111111    |              0.015625    |
| Housing and Real Estate |        41067 |      0.244444    |              0.0165017   |
| Housing and Real Estate |        44001 |     -1           |              0.0263158   |
| Housing and Real Estate |        44007 |     -0.407407    |              0.00601202  |
| Housing and Real Estate |        44009 |     -0.666667    |              0.0425532   |
| Housing and Real Estate |        45001 |      0.777778    |              0.047619    |
| Housing and Real Estate |        45013 |     -0.157895    |              0.169643    |
| Housing and Real Estate |        45019 |     -0.688889    |              0.0212766   |
| Housing and Real Estate |        45029 |      0.555556    |              0.0322581   |
| Housing and Real Estate |        45043 |     -0.333333    |              0.0217391   |
| Housing and Real Estate |        45051 |      0.5         |              0.0268456   |
| Housing and Real Estate |        45055 |      0.111111    |              0.0232558   |
| Housing and Real Estate |        45065 |      1           |              0.25        |
| Housing and Real Estate |        45073 |     -0.333333    |              0.0576923   |
| Housing and Real Estate |        45079 |     -0.111111    |              0.00408163  |
| Housing and Real Estate |        46081 |      0.777778    |              0.0588235   |
| Housing and Real Estate |        47035 |      0.111111    |              0.09375     |
| Housing and Real Estate |        47065 |      0.777778    |              0.00404858  |
| Housing and Real Estate |        47105 |     -0.222222    |              0.129032    |
| Housing and Real Estate |        47155 |      1           |              0.0227273   |
| Housing and Real Estate |        47157 |     -0.111111    |              0.00318471  |
| Housing and Real Estate |        47163 |      0.444444    |              0.018018    |
| Housing and Real Estate |        49043 |     -0.111111    |              0.0277778   |
| Housing and Real Estate |        49049 |     -1           |              0.00289855  |
| Housing and Real Estate |        49053 |     -0.555556    |              0.0175439   |
| Housing and Real Estate |        51003 |      0.555556    |              0.0151515   |
| Housing and Real Estate |        51013 |      0.333333    |              0.0110497   |
| Housing and Real Estate |        51019 |      0.555556    |              0.0208333   |
| Housing and Real Estate |        51087 |      0.037037    |              0.0175439   |
| Housing and Real Estate |        51095 |      0           |              0.0740741   |
| Housing and Real Estate |        51103 |      1           |              0.230769    |
| Housing and Real Estate |        51107 |      1           |              0.0122699   |
| Housing and Real Estate |        51125 |      1           |              0.0833333   |
| Housing and Real Estate |        51133 |      0.333333    |              0.153846    |
| Housing and Real Estate |        51135 |      0.333333    |              0.125       |
| Housing and Real Estate |        51153 |      0.259259    |              0.026087    |
| Housing and Real Estate |        51161 |     -0.333333    |              0.0185185   |
| Housing and Real Estate |        51510 |      0.888889    |              0.0188679   |
| Housing and Real Estate |        51710 |     -1           |              0.00529101  |
| Housing and Real Estate |        51760 |      0.777778    |              0.00621118  |
| Housing and Real Estate |        51775 |      1           |              0.05        |
| Housing and Real Estate |        51810 |     -0.888889    |              0.00662252  |
| Housing and Real Estate |        53005 |      0.333333    |              0.00729927  |
| Housing and Real Estate |        53009 |      1           |              0.0545455   |
| Housing and Real Estate |        53011 |      0.333333    |              0.00357143  |
| Housing and Real Estate |        53015 |      1           |              0.0224719   |
| Housing and Real Estate |        53027 |     -0.111111    |              0.016129    |
| Housing and Real Estate |        53031 |      1           |              0.111111    |
| Housing and Real Estate |        53033 |     -0.0555556   |              0.00281294  |
| Housing and Real Estate |        53041 |      0.333333    |              0.0322581   |
| Housing and Real Estate |        53045 |     -0.333333    |              0.0612245   |
| Housing and Real Estate |        53053 |      0.851852    |              0.00535714  |
| Housing and Real Estate |        53061 |     -0.333333    |              0.00199601  |
| Housing and Real Estate |        53063 |     -0.111111    |              0.00621118  |
| Housing and Real Estate |        53067 |      0.185185    |              0.0186335   |
| Housing and Real Estate |        53071 |      1           |              0.0232558   |
| Housing and Real Estate |        53073 |      0.555556    |              0.00980392  |
| Housing and Real Estate |        53077 |      1           |              0.00671141  |
| Housing and Real Estate |        54063 |      1           |              0.0833333   |
| Housing and Real Estate |        54069 |      0.555556    |              0.0208333   |
| Housing and Real Estate |        54083 |      0.555556    |              0.037037    |
| Housing and Real Estate |        54109 |      1           |              0.0526316   |
| Housing and Real Estate |        55025 |      0.333333    |              0.00322581  |
| Housing and Real Estate |        55027 |      0.333333    |              0.0149254   |
| Housing and Real Estate |        55047 |      0.777778    |              0.05        |
| Housing and Real Estate |        55071 |      0.555556    |              0.0133333   |
| Housing and Real Estate |        55079 |      0.222222    |              0.00232829  |
| Housing and Real Estate |        55087 |      0.777778    |              0.00763359  |
| Housing and Real Estate |        55089 |      1           |              0.0163934   |
| Housing and Real Estate |        55131 |      0.111111    |              0.0120482   |
| Housing and Real Estate |        55133 |      0.333333    |              0.00334448  |
| Housing and Real Estate |        72003 |      1           |              0.0344828   |
| Housing and Real Estate |        72005 |      1           |              0.0222222   |
| Housing and Real Estate |        72031 |     -0.111111    |              0.008       |
| Housing and Real Estate |        72033 |      0.111111    |              0.0344828   |
| Housing and Real Estate |        72079 |     -0.111111    |              0.0555556   |
| Housing and Real Estate |        72097 |      0.111111    |              0.0142857   |
| Housing and Real Estate |        72113 |      0           |              0.0149254   |
| Housing and Real Estate |        72127 |     -0.777778    |              0.00271003  |
| Housing and Real Estate |        72145 |     -0.555556    |              0.0263158   |
"""
# 2. Parse and Clean Data
try:
    # 读取数据，使用 | 作为分隔符
    df = pd.read_csv(io.StringIO(source_data), sep="|", skipinitialspace=True)
    
    # 清理列名（去除首尾空格）
    df.columns = [c.strip() for c in df.columns]
    
    # 删除由 markdown 表格首尾 | 产生的空列
    df = df.dropna(axis=1, how='all')

    # 【关键修复】：过滤掉 Markdown 的分割行（即包含 ----- 的那一行）
    # 通常这一行在读取后位于 index 0，特征是内容全是 - 或 :
    df = df[~df['service_type'].str.contains('---', na=False)]

    # 【关键修复】：强制将数值列转换为数字类型
    # 之前因为分割行的存在，这些列被认为是字符串，导致了 conjugate 错误
    numeric_cols = ['fairness_index', 'ratio_of_HighAging_CBG']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
        
    # 删除转换后可能出现的空值行
    df = df.dropna(subset=numeric_cols)

except Exception as e:
    print(f"Error parsing data: {e}")
    sys.exit(1)

# 3. Filter and Transform Data for the Chart
# Filter for "Grocery and Food Supply" (matching "GFS" title in image)
gfs_df = df[df['service_type'].str.strip() == 'Grocery and Food Supply'].copy()

# X-axis transformation
gfs_df['percentage_high_ageing'] = gfs_df['ratio_of_HighAging_CBG'] * 100
# 4. Plotting
def create_chart(output_path):
    # Set style for cleaner look matching the publication style
    sns.set_context("paper")
    sns.set_style("ticks")
    
    # Figure setup
    # Aspect ratio looks roughly 4:5 based on the image provided
    fig, ax = plt.subplots(figsize=(4, 5.5))
    
    # Color selection: Desaturated purple based on visual inspection
    # Points have white edges, line is solid.
    color_base = '#A696C6' # Approximate hex for the lavender/purple
    
    # Create the Regression Plot
    sns.regplot(
        data=gfs_df,
        x='percentage_high_ageing',
        y='fairness_index',
        color=color_base,
        scatter_kws={
            's': 60,                # Marker size
            'alpha': 1.0,           # Opacity
            'edgecolor': 'white',   # White border around points
            'linewidths': 0.8        # Width of the border
        },
        line_kws={
            'linewidth': 4,         # Thick regression line
            'alpha': 0.9,
            'color': '#9E8CC2'      # Slightly darker for the line itself
        },
        ax=ax,
        truncate=False              # Let line extend to edges
    )
    
    # Configure Axes Limits to match image
    # Y-axis: -1.0 to 1.0 (with a bit of padding shown in image)
    ax.set_ylim(-1.1, 1.1)
    
    # X-axis: 0 to roughly 40 based on data distribution, ticks at 0, 10, 20, 30
    # The max value in data is around 37.5
    ax.set_xlim(-1, 39)
    
    # Ticks configuration
    ax.set_yticks([-1.0, -0.5, 0, 0.5, 1.0])
    ax.set_xticks([0, 10, 20, 30])
    
    ax.tick_params(axis='both', which='major', labelsize=14, length=6, width=0.8, direction='out')
    
    # Labels and Title
    ax.set_title("GFS", fontsize=18, pad=10, color='black')
    
    # Y-axis Label: Delta F bar (Using LaTeX math mode)
    ax.set_ylabel(r"$\Delta \bar{F}$", fontsize=18, labelpad=5)
    
    # X-axis Label
    ax.set_xlabel("Percentage of high-ageing\nCBGs", fontsize=16, labelpad=5)
    
    # Add the 'd' tag in the top left corner (outside the axes)
    # Coordinate system: figure fraction or relative to axes
    # (0, 1) is top left of axis. We shift it up and left.
    ax.text(-0.25, 1.05, 'd', transform=ax.transAxes, 
            fontsize=24, fontweight='bold', va='bottom', ha='right')

    # Remove top and right spines if desired, though the image shows a box.
    # The image implies a box plot style, so we keep the box but ensure it's simple.
    sns.despine(ax=ax, top=False, right=False)
    
    # Layout adjustments
    plt.tight_layout()
    
    # Save the file
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_path}")

# 5. Execution Logic
if __name__ == "__main__":
    output_filename = "output.png"
    if len(sys.argv) > 1:
        output_filename = sys.argv[1]
    
    create_chart(output_filename)
