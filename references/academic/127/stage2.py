import sys
import io
import json
import urllib.request
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Polygon, Patch
from matplotlib.collections import PatchCollection
import numpy as np

# -----------------------------------------------------------------------------
# 1. EMBEDDED SOURCE DATA
# -----------------------------------------------------------------------------
DATA_CSV = """
GHG emissions from food system (kton CO2eq) to produce pie charts of Figure 5,Unnamed: 1,Unnamed: 2,Unnamed: 3,Unnamed: 4,Unnamed: 5,Unnamed: 6,Unnamed: 7,Unnamed: 8,Unnamed: 9,Unnamed: 10
nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan
Figure5a,nan,nan,nan,nan,nan,Figure 5b,nan,nan,nan,nan
For pie charts in 2015,Landbased,Energy,Industry,Waste,nan,For pie charts in 2015,Landbased,Energy,Industry,Waste
Canada,201164.294,51689.479,6175.649,12193.085,nan,Canada,263117.801,85853.562,21392.628,13121.601
USA,601738.080,445115.361,26836.665,131828.315,nan,USA,578273.619,569021.760,233941.387,90267.061
Mexico,120226.551,37171.706,4013.252,33693.332,nan,Mexico,123821.157,56373.865,3137.997,54280.481
Central America,178432.110,8367.638,3598.965,18714.392,nan,Central America,145744.874,17116.907,9499.750,29794.832
Brazil,1474276.979,41389.487,2499.999,68187.007,nan,Brazil,1126107.603,84267.338,5387.973,111450.551
South America,1083260.373,60080.497,1762.967,45226.091,nan,South America,1040997.444,99131.498,4312.605,68735.659
North Africa,46651.876,31399.088,3683.796,29433.271,nan,North Africa,70503.202,65476.070,11529.255,51164.242
West Africa,734772.908,48327.365,747.604,40384.321,nan,West Africa,882311.531,39999.317,788.483,91129.102
East Africa,637616.461,3889.021,27.367,24404.194,nan,East Africa,635059.463,11976.521,156.844,52448.822
South Africa,1037727.823,28736.143,1958.759,24822.018,nan,South Africa,1140436.901,47069.926,2702.491,48543.007
OECD Europe,506415.852,376345.884,43278.047,135212.773,nan,OECD Europe,456173.452,335696.077,110149.281,83049.510
Central Europe,192861.896,116611.679,22161.509,31342.563,nan,Central Europe,136674.060,90707.672,33126.462,27606.399
Turkey,49054.091,18500.640,171.109,8451.183,nan,Turkey,61196.426,42494.015,6051.404,12212.789
Ukraine,170510.606,77082.207,15893.346,7395.620,nan,Ukraine,99204.425,25684.059,8706.805,11075.620
Central Asia,91615.093,35678.491,3843.458,8524.126,nan,Central Asia,101864.547,44231.658,4866.091,13331.452
Russia,461793.341,197935.876,30187.846,53413.813,nan,Russia,227540.827,146476.220,50973.592,68754.852
Middle East,62356.971,111865.735,5532.684,35802.596,nan,Middle East,70838.384,220067.095,23742.695,76231.767
India,944465.777,94002.558,14409.817,146370.530,nan,India,1105713.464,293459.209,21504.578,238476.233
Korea,49941.328,27463.763,1707.030,14931.015,nan,Korea,46890.757,51958.992,3986.427,17530.598
China,935242.290,573292.388,41073.883,202378.564,nan,China,973057.822,1106530.662,87783.357,339679.549
South-East Asia,578420.839,35097.646,392.350,48818.095,nan,South-East Asia,652160.938,130398.843,6100.406,86187.630
Indonesia,1753214.062,27077.214,4536.245,28818.235,nan,Indonesia,1572711.639,57578.501,8553.456,55399.190
Japan,69352.978,107601.025,3472.682,16698.800,nan,Japan,61923.867,102355.577,38039.725,7346.705
Oceania,179115.319,42758.678,1743.352,17268.612,nan,Oceania,171113.604,58416.043,14483.316,14530.635
nan,nan,nan,nan,nan,nan,nan,nan,nan,nan,nan
Food system emission shares in 1990 to produce map of Figure5a,nan,nan,nan,nan,nan,Food system emission shares in 2015 to produce map of Figure5b,nan,nan,nan,nan
country,1990,nan,nan,nan,nan,country,2015,nan,nan,nan
ABW,0.117343698,nan,nan,nan,nan,ABW,0.136907995,nan,nan,nan
AFG,0.785585221,nan,nan,nan,nan,AFG,0.636150027,nan,nan,nan
AGO,0.723135583,nan,nan,nan,nan,AGO,0.681969076,nan,nan,nan
AIA,-0.397118838,nan,nan,nan,nan,AIA,0.194691823,nan,nan,nan
ALB,0.410061696,nan,nan,nan,nan,ALB,0.602264048,nan,nan,nan
ANT,0.067183973,nan,nan,nan,nan,ANT,0.119156176,nan,nan,nan
ARE,0.087729251,nan,nan,nan,nan,ARE,0.092731596,nan,nan,nan
ARG,0.81231668,nan,nan,nan,nan,ARG,0.665247582,nan,nan,nan
ARM,0.188481726,nan,nan,nan,nan,ARM,0.419117828,nan,nan,nan
ASM,0.908327108,nan,nan,nan,nan,ASM,1.085516055,nan,nan,nan
ATG,0.33514895,nan,nan,nan,nan,ATG,0.194452679,nan,nan,nan
AUS,0.40344781,nan,nan,nan,nan,AUS,0.329642484,nan,nan,nan
AUT,0.323501718,nan,nan,nan,nan,AUT,0.263883801,nan,nan,nan
AZE,0.216471579,nan,nan,nan,nan,AZE,0.373172038,nan,nan,nan
BDI,0.880745567,nan,nan,nan,nan,BDI,1.070346831,nan,nan,nan
BEL,0.220089894,nan,nan,nan,nan,BEL,0.245436882,nan,nan,nan
BEN,0.931951673,nan,nan,nan,nan,BEN,0.695778762,nan,nan,nan
BFA,0.934986805,nan,nan,nan,nan,BFA,0.948279029,nan,nan,nan
BGD,0.897209294,nan,nan,nan,nan,BGD,0.682723904,nan,nan,nan
BGR,0.307192399,nan,nan,nan,nan,BGR,0.286651912,nan,nan,nan
BHR,0.105895026,nan,nan,nan,nan,BHR,0.099380163,nan,nan,nan
BHS,0.873093611,nan,nan,nan,nan,BHS,0.180673961,nan,nan,nan
BIH,0.179401168,nan,nan,nan,nan,BIH,0.163467194,nan,nan,nan
BLR,0.536570902,nan,nan,nan,nan,BLR,0.590678242,nan,nan,nan
BLZ,1.380094829,nan,nan,nan,nan,BLZ,1.075126965,nan,nan,nan
BMU,0.121031219,nan,nan,nan,nan,BMU,0.157268808,nan,nan,nan
BOL,0.891957596,nan,nan,nan,nan,BOL,0.83383841,nan,nan,nan
BRA,0.986054541,nan,nan,nan,nan,BRA,0.806860921,nan,nan,nan
BRB,0.257824935,nan,nan,nan,nan,BRB,0.132104271,nan,nan,nan
BRN,0.234855318,nan,nan,nan,nan,BRN,0.161727196,nan,nan,nan
BTN,-0.305340369,nan,nan,nan,nan,BTN,-0.72196524,nan,nan,nan
BWA,1.226779855,nan,nan,nan,nan,BWA,1.062830929,nan,nan,nan
CAF,0.647694982,nan,nan,nan,nan,CAF,0.722541908,nan,nan,nan
CAN,0.390282026,nan,nan,nan,nan,CAN,0.410520519,nan,nan,nan
CHE,0.226054948,nan,nan,nan,nan,CHE,0.260295723,nan,nan,nan
CHL,0.441057547,nan,nan,nan,nan,CHL,2.219958602,nan,nan,nan
CHN,0.461069491,nan,nan,nan,nan,CHN,0.189477874,nan,nan,nan
CIV,1.386224901,nan,nan,nan,nan,CIV,0.509962059,nan,nan,nan
CMR,0.90737961,nan,nan,nan,nan,CMR,0.843695984,nan,nan,nan
COD,0.962544571,nan,nan,nan,nan,COD,0.894515046,nan,nan,nan
COG,0.800924414,nan,nan,nan,nan,COG,0.781699275,nan,nan,nan
COK,2.423531132,nan,nan,nan,nan,COK,0.278361519,nan,nan,nan
COL,0.808260119,nan,nan,nan,nan,COL,0.577497141,nan,nan,nan
COM,0.80798406,nan,nan,nan,nan,COM,0.67533201,nan,nan,nan
CPV,-0.691598781,nan,nan,nan,nan,CPV,0.304209156,nan,nan,nan
CRI,0.821777461,nan,nan,nan,nan,CRI,6.660951783,nan,nan,nan
CUB,0.966256057,nan,nan,nan,nan,CUB,0.528785065,nan,nan,nan
CYM,0.168315591,nan,nan,nan,nan,CYM,0.144044273,nan,nan,nan
CYP,0.238983628,nan,nan,nan,nan,CYP,0.297466947,nan,nan,nan
CZE,0.177355677,nan,nan,nan,nan,CZE,0.202829483,nan,nan,nan
DEU,0.182229265,nan,nan,nan,nan,DEU,0.204702009,nan,nan,nan
DJI,0.428140655,nan,nan,nan,nan,DJI,0.52139949,nan,nan,nan
DMA,2.765729244,nan,nan,nan,nan,DMA,0.519870553,nan,nan,nan
DNK,0.35789038,nan,nan,nan,nan,DNK,0.425155457,nan,nan,nan
DOM,1.253589097,nan,nan,nan,nan,DOM,0.550162344,nan,nan,nan
DZA,0.185686091,nan,nan,nan,nan,DZA,0.213234612,nan,nan,nan
ECU,0.644002873,nan,nan,nan,nan,ECU,0.538207707,nan,nan,nan
EGY,0.281445794,nan,nan,nan,nan,EGY,0.236940064,nan,nan,nan
ERI,0.832357805,nan,nan,nan,nan,ERI,0.923839426,nan,nan,nan
ESH,0.763415737,nan,nan,nan,nan,ESH,0.688832754,nan,nan,nan
ESP,0.330131216,nan,nan,nan,nan,ESP,0.309429918,nan,nan,nan
EST,0.214307238,nan,nan,nan,nan,EST,0.267294924,nan,nan,nan
ETH,0.827620342,nan,nan,nan,nan,ETH,0.785545733,nan,nan,nan
FIN,0.490349021,nan,nan,nan,nan,FIN,0.329384654,nan,nan,nan
FJI,3.407270168,nan,nan,nan,nan,FJI,-5.569367416,nan,nan,nan
FLK,0.782043714,nan,nan,nan,nan,FLK,0.920616161,nan,nan,nan
FRA,0.31706303,nan,nan,nan,nan,FRA,0.458953629,nan,nan,nan
FRO,0.825227094,nan,nan,nan,nan,FRO,0.823878171,nan,nan,nan
FSM,0.999086934,nan,nan,nan,nan,FSM,7.789822496,nan,nan,nan
GAB,0.146141977,nan,nan,nan,nan,GAB,-0.043818772,nan,nan,nan
GBR,0.206798675,nan,nan,nan,nan,GBR,0.23070905,nan,nan,nan
GEO,0.220183978,nan,nan,nan,nan,GEO,0.384516007,nan,nan,nan
GHA,0.191482208,nan,nan,nan,nan,GHA,0.295187052,nan,nan,nan
GIB,0.120137251,nan,nan,nan,nan,GIB,0.10558965,nan,nan,nan
GIN,0.920913817,nan,nan,nan,nan,GIN,0.895551183,nan,nan,nan
GLP,0.234331305,nan,nan,nan,nan,GLP,0.214194563,nan,nan,nan
GMB,1.459957651,nan,nan,nan,nan,GMB,0.808024607,nan,nan,nan
GNB,0.926138112,nan,nan,nan,nan,GNB,0.874934181,nan,nan,nan
GNQ,0.978937882,nan,nan,nan,nan,GNQ,0.453280799,nan,nan,nan
GRC,0.267576387,nan,nan,nan,nan,GRC,0.24354323,nan,nan,nan
GRD,0.364993089,nan,nan,nan,nan,GRD,0.223956265,nan,nan,nan
GRL,0.633465287,nan,nan,nan,nan,GRL,0.316180219,nan,nan,nan
GTM,0.871958868,nan,nan,nan,nan,GTM,0.701459107,nan,nan,nan
GUF,0.03402232,nan,nan,nan,nan,GUF,0.118970887,nan,nan,nan
GUM,0.79150544,nan,nan,nan,nan,GUM,0.78539815,nan,nan,nan
GUY,1.07160753,nan,nan,nan,nan,GUY,0.990927325,nan,nan,nan
HKG,0.13079184,nan,nan,nan,nan,HKG,0.141646085,nan,nan,nan
HND,0.94772582,nan,nan,nan,nan,HND,0.782960882,nan,nan,nan
HRV,0.531105462,nan,nan,nan,nan,HRV,0.38190594,nan,nan,nan
HTI,0.686024383,nan,nan,nan,nan,HTI,0.476694059,nan,nan,nan
HUN,0.341476024,nan,nan,nan,nan,HUN,0.342904794,nan,nan,nan
IDN,1.233269272,nan,nan,nan,nan,IDN,0.560448047,nan,nan,nan
IND,0.588213384,nan,nan,nan,nan,IND,0.325065034,nan,nan,nan
IRL,0.512751623,nan,nan,nan,nan,IRL,0.475657238,nan,nan,nan
IRN,0.26126357,nan,nan,nan,nan,IRN,0.159698627,nan,nan,nan
IRQ,0.182043589,nan,nan,nan,nan,IRQ,0.148964417,nan,nan,nan
ISL,0.53921272,nan,nan,nan,nan,ISL,0.402991806,nan,nan,nan
ISR,0.186909166,nan,nan,nan,nan,ISR,0.18884053,nan,nan,nan
ITA,0.230530281,nan,nan,nan,nan,ITA,0.250347107,nan,nan,nan
JAM,0.248795033,nan,nan,nan,nan,JAM,0.228854926,nan,nan,nan
JOR,0.211660266,nan,nan,nan,nan,JOR,0.249355814,nan,nan,nan
JPN,0.16453513,nan,nan,nan,nan,JPN,0.155258028,nan,nan,nan
KAZ,0.195904613,nan,nan,nan,nan,KAZ,0.144793338,nan,nan,nan
KEN,0.875965446,nan,nan,nan,nan,KEN,1.042161749,nan,nan,nan
KGZ,0.312633266,nan,nan,nan,nan,KGZ,0.458429155,nan,nan,nan
KHM,0.942921902,nan,nan,nan,nan,KHM,0.805327295,nan,nan,nan
KIR,0.570044399,nan,nan,nan,nan,KIR,0.535740247,nan,nan,nan
KNA,0.816363235,nan,nan,nan,nan,KNA,0.215469006,nan,nan,nan
KOR,0.210792732,nan,nan,nan,nan,KOR,0.135107143,nan,nan,nan
KWT,0.118969116,nan,nan,nan,nan,KWT,0.131235236,nan,nan,nan
LAO,1.816973231,nan,nan,nan,nan,LAO,0.4932181,nan,nan,nan
LBN,0.247437609,nan,nan,nan,nan,LBN,0.193544884,nan,nan,nan
LBR,0.951183522,nan,nan,nan,nan,LBR,2.193354501,nan,nan,nan
LBY,0.120241964,nan,nan,nan,nan,LBY,0.138595714,nan,nan,nan
LCA,0.808581761,nan,nan,nan,nan,LCA,0.295992443,nan,nan,nan
LKA,0.717116748,nan,nan,nan,nan,LKA,0.452839831,nan,nan,nan
LSO,0.835160341,nan,nan,nan,nan,LSO,0.650493874,nan,nan,nan
LTU,0.360798,nan,nan,nan,nan,LTU,0.7816423,nan,nan,nan
LUX,0.126758674,nan,nan,nan,nan,LUX,0.186054096,nan,nan,nan
LVA,0.639325023,nan,nan,nan,nan,LVA,-23.02854328,nan,nan,nan
MAC,0.130960844,nan,nan,nan,nan,MAC,0.154444903,nan,nan,nan
MAR,0.60209814,nan,nan,nan,nan,MAR,0.461283005,nan,nan,nan
MDA,0.227243393,nan,nan,nan,nan,MDA,0.336451318,nan,nan,nan
MDG,0.985991395,nan,nan,nan,nan,MDG,0.794373455,nan,nan,nan
MDV,0.335208901,nan,nan,nan,nan,MDV,0.165231544,nan,nan,nan
MEX,0.396693023,nan,nan,nan,nan,MEX,0.300546968,nan,nan,nan
MHL,0.990871216,nan,nan,nan,nan,MHL,0.985555645,nan,nan,nan
MKD,0.230768599,nan,nan,nan,nan,MKD,0.234598063,nan,nan,nan
MLI,0.97413897,nan,nan,nan,nan,MLI,0.952687965,nan,nan,nan
MLT,0.118649481,nan,nan,nan,nan,MLT,0.236532694,nan,nan,nan
MMR,0.976702897,nan,nan,nan,nan,MMR,0.997303467,nan,nan,nan
MNG,0.720550187,nan,nan,nan,nan,MNG,0.666690833,nan,nan,nan
MNP,0.989106287,nan,nan,nan,nan,MNP,0.993815178,nan,nan,nan
MOZ,0.919724507,nan,nan,nan,nan,MOZ,0.727291149,nan,nan,nan
MRT,0.899066484,nan,nan,nan,nan,MRT,0.901515904,nan,nan,nan
MSR,0.828653437,nan,nan,nan,nan,MSR,0.373059134,nan,nan,nan
MTQ,0.209593414,nan,nan,nan,nan,MTQ,0.153001187,nan,nan,nan
MUS,0.371324032,nan,nan,nan,nan,MUS,0.193959095,nan,nan,nan
MWI,1.005147423,nan,nan,nan,nan,MWI,0.927865182,nan,nan,nan
MYS,0.449445257,nan,nan,nan,nan,MYS,0.652691494,nan,nan,nan
MYT,1.055965739,nan,nan,nan,nan,MYT,1.021290689,nan,nan,nan
NAM,0.892218783,nan,nan,nan,nan,NAM,0.830104307,nan,nan,nan
NCL,0.203304474,nan,nan,nan,nan,NCL,0.089775553,nan,nan,nan
NER,0.923203147,nan,nan,nan,nan,NER,0.90904682,nan,nan,nan
NGA,0.498723621,nan,nan,nan,nan,NGA,0.613977519,nan,nan,nan
NIC,0.943432681,nan,nan,nan,nan,NIC,0.886143182,nan,nan,nan
NIU,1.983615759,nan,nan,nan,nan,NIU,0.99982595,nan,nan,nan
NLD,0.306593782,nan,nan,nan,nan,NLD,0.273956566,nan,nan,nan
NOR,0.416692166,nan,nan,nan,nan,NOR,0.352888969,nan,nan,nan
NPL,1.123199698,nan,nan,nan,nan,NPL,0.800758141,nan,nan,nan
NRU,0.649844281,nan,nan,nan,nan,NRU,0.637519403,nan,nan,nan
NZL,1.067644806,nan,nan,nan,nan,NZL,0.835256383,nan,nan,nan
OMN,0.113345788,nan,nan,nan,nan,OMN,0.119681019,nan,nan,nan
PAK,0.693382567,nan,nan,nan,nan,PAK,0.59695735,nan,nan,nan
PAN,0.919060776,nan,nan,nan,nan,PAN,0.581322438,nan,nan,nan
PER,1.2842829,nan,nan,nan,nan,PER,0.729963787,nan,nan,nan
PHL,0.597314631,nan,nan,nan,nan,PHL,0.609081102,nan,nan,nan
PLW,0.088078524,nan,nan,nan,nan,PLW,0.114981255,nan,nan,nan
PNG,0.868403191,nan,nan,nan,nan,PNG,0.961809827,nan,nan,nan
POL,0.240814809,nan,nan,nan,nan,POL,0.270532949,nan,nan,nan
PRI,0.702363947,nan,nan,nan,nan,PRI,0.750723322,nan,nan,nan
PRK,0.18393714,nan,nan,nan,nan,PRK,0.449847069,nan,nan,nan
PRT,0.344620957,nan,nan,nan,nan,PRT,0.30876454,nan,nan,nan
PRY,1.055708139,nan,nan,nan,nan,PRY,1.004980983,nan,nan,nan
PYF,-0.121199422,nan,nan,nan,nan,PYF,0.263350262,nan,nan,nan
QAT,0.152777886,nan,nan,nan,nan,QAT,0.122309643,nan,nan,nan
REU,0.17315551,nan,nan,nan,nan,REU,0.167702813,nan,nan,nan
ROU,0.225959343,nan,nan,nan,nan,ROU,-0.660258315,nan,nan,nan
RUS,0.214389997,nan,nan,nan,nan,RUS,0.217661675,nan,nan,nan
RWA,0.448330786,nan,nan,nan,nan,RWA,1.064299753,nan,nan,nan
SAU,0.126468647,nan,nan,nan,nan,SAU,0.098012142,nan,nan,nan
SCG,0.180671479,nan,nan,nan,nan,SCG,0.275141305,nan,nan,nan
SDN,1.060346119,nan,nan,nan,nan,SDN,1.032242732,nan,nan,nan
SEN,0.882884233,nan,nan,nan,nan,SEN,0.81974287,nan,nan,nan
SGP,0.084321002,nan,nan,nan,nan,SGP,0.099656043,nan,nan,nan
SHN,0.302507824,nan,nan,nan,nan,SHN,0.157255292,nan,nan,nan
SLB,0.926828077,nan,nan,nan,nan,SLB,0.805886222,nan,nan,nan
SLE,0.887758004,nan,nan,nan,nan,SLE,0.491108151,nan,nan,nan
SLV,0.654226364,nan,nan,nan,nan,SLV,0.486177119,nan,nan,nan
SOM,0.976255654,nan,nan,nan,nan,SOM,0.978644821,nan,nan,nan
SPM,0.099212062,nan,nan,nan,nan,SPM,0.182974137,nan,nan,nan
STP,0.349259979,nan,nan,nan,nan,STP,0.274571256,nan,nan,nan
SUR,0.809135159,nan,nan,nan,nan,SUR,0.78788923,nan,nan,nan
SVK,0.249228213,nan,nan,nan,nan,SVK,0.260896365,nan,nan,nan
SVN,0.287891477,nan,nan,nan,nan,SVN,0.369011232,nan,nan,nan
SWE,0.897635098,nan,nan,nan,nan,SWE,0.891768099,nan,nan,nan
SWZ,0.75287526,nan,nan,nan,nan,SWZ,0.610946847,nan,nan,nan
SYC,0.180789146,nan,nan,nan,nan,SYC,0.119583445,nan,nan,nan
SYR,0.225967938,nan,nan,nan,nan,SYR,0.333870233,nan,nan,nan
TCA,-0.055711587,nan,nan,nan,nan,TCA,0.143430569,nan,nan,nan
TCD,0.934924091,nan,nan,nan,nan,TCD,0.956676846,nan,nan,nan
TGO,0.872277905,nan,nan,nan,nan,TGO,0.702762509,nan,nan,nan
THA,0.536552774,nan,nan,nan,nan,THA,0.367119545,nan,nan,nan
TJK,0.325532083,nan,nan,nan,nan,TJK,0.619843342,nan,nan,nan
TKL,0.999325791,nan,nan,nan,nan,TKL,0.99945123,nan,nan,nan
TKM,0.152734114,nan,nan,nan,nan,TKM,0.215551681,nan,nan,nan
TLS,1.312339752,nan,nan,nan,nan,TLS,0.680724054,nan,nan,nan
TON,0.602291974,nan,nan,nan,nan,TON,0.508734094,nan,nan,nan
TTO,0.271354318,nan,nan,nan,nan,TTO,0.238169281,nan,nan,nan
TUN,0.349080261,nan,nan,nan,nan,TUN,0.3158462,nan,nan,nan
TUR,0.375829083,nan,nan,nan,nan,TUR,0.269736977,nan,nan,nan
TUV,1.292121347,nan,nan,nan,nan,TUV,0.935601034,nan,nan,nan
TWN,0.212240595,nan,nan,nan,nan,TWN,0.103077825,nan,nan,nan
TZA,0.988399148,nan,nan,nan,nan,TZA,0.935612588,nan,nan,nan
UGA,0.876305948,nan,nan,nan,nan,UGA,0.829193117,nan,nan,nan
UKR,0.210647049,nan,nan,nan,nan,UKR,0.26793164,nan,nan,nan
URY,5.989513567,nan,nan,nan,nan,URY,1.073764057,nan,nan,nan
USA,0.208055693,nan,nan,nan,nan,USA,0.229300425,nan,nan,nan
UZB,0.239934554,nan,nan,nan,nan,UZB,0.390859301,nan,nan,nan
VCT,-5.016650659,nan,nan,nan,nan,VCT,0.280026521,nan,nan,nan
VEN,0.663059026,nan,nan,nan,nan,VEN,0.481147557,nan,nan,nan
VGB,0.483925606,nan,nan,nan,nan,VGB,0.170398609,nan,nan,nan
VIR,0.855522883,nan,nan,nan,nan,VIR,-4.292622358,nan,nan,nan
VNM,1.492383635,nan,nan,nan,nan,VNM,0.496878937,nan,nan,nan
VUT,0.78655561,nan,nan,nan,nan,VUT,0.876604073,nan,nan,nan
WLF,1.573028644,nan,nan,nan,nan,WLF,0.858455392,nan,nan,nan
WSM,-0.10583137,nan,nan,nan,nan,WSM,0.669900369,nan,nan,nan
YEM,0.482987834,nan,nan,nan,nan,YEM,0.444756592,nan,nan,nan
ZAF,0.189326031,nan,nan,nan,nan,ZAF,0.166054356,nan,nan,nan
ZMB,0.995042021,nan,nan,nan,nan,ZMB,1.043112474,nan,nan,nan
ZWE,0.755449467,nan,nan,nan,nan,ZWE,0.780384593,nan,nan,nan
"""

# -----------------------------------------------------------------------------
# 2. DATA PROCESSING
# -----------------------------------------------------------------------------

def get_data():
    # Read the raw CSV string
    df_raw = pd.read_csv(io.StringIO(DATA_CSV), header=None)
    
    # --- Extract Pie Chart Data ---
    pie_start_idx = 3
    pie_end_idx = 28
    
    df_pie_left = df_raw.iloc[pie_start_idx+1:pie_end_idx, 0:5].copy()
    df_pie_left.columns = ["Region", "Landbased", "Energy", "Industry", "Waste"]
    
    df_pie_right = df_raw.iloc[pie_start_idx+1:pie_end_idx, 6:11].copy()
    df_pie_right.columns = ["Region", "Landbased", "Energy", "Industry", "Waste"]
    
    df_pie = pd.concat([df_pie_left, df_pie_right], ignore_index=True)
    df_pie = df_pie.dropna(subset=['Region'])
    
    cols = ["Landbased", "Energy", "Industry", "Waste"]
    for c in cols:
        df_pie[c] = pd.to_numeric(df_pie[c])
        
    df_pie['Total'] = df_pie[cols].sum(axis=1)
    for c in cols:
        df_pie[c + '_pct'] = (df_pie[c] / df_pie['Total']) * 100

    # --- Extract Map Data ---
    map_start_idx = 30
    df_map = df_raw.iloc[map_start_idx+1:, 0:2].copy()
    df_map.columns = ["iso_a3", "share_1990"]
    df_map = df_map.dropna(subset=['iso_a3'])
    df_map['share_1990'] = pd.to_numeric(df_map['share_1990'])
    
    return df_pie, df_map

def get_world_geojson():
    # URL for a lightweight world geojson
    url = "https://raw.githubusercontent.com/python-visualization/folium/main/examples/data/world-countries.json"
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = json.loads(response.read().decode())
        return data
    except Exception as e:
        print(f"Warning: Could not download map data: {e}")
        return None

# -----------------------------------------------------------------------------
# 3. PLOTTING
# -----------------------------------------------------------------------------

def plot_chart(output_filename="output.png"):
    df_pie, df_map = get_data()
    
    # --- Setup Colors ---
    # Pie Colors
    c_land = '#5f804d'  # Green
    c_energy = '#c48257' # Brown/Orange
    c_industry = '#949698' # Grey
    c_waste = '#e8d67d' # Yellow
    pie_colors = [c_land, c_energy, c_industry, c_waste]
    
    # Map Colors (Discrete Bins)
    bounds = [-10, 0.10, 0.15, 0.20, 0.30, 0.40, 0.50, 100]
    map_colors_hex = [
        '#c68642', # <10%
        '#e8d278', # 10-15
        '#fcf4c5', # 15-20
        '#a8d6e2', # 20-30
        '#8abf68', # 30-40
        '#5f9e56', # 40-50
        '#3b6e38'  # >50%
    ]
    cmap = mcolors.ListedColormap(map_colors_hex)
    norm = mcolors.BoundaryNorm(bounds, cmap.N)
    
    # Create a dict for fast lookup: iso_a3 -> value
    map_data_dict = dict(zip(df_map['iso_a3'], df_map['share_1990']))

    # --- Figure Layout ---
    fig = plt.figure(figsize=(18, 12), facecolor='white')
    
    # 1. Draw Map (Center)
    ax_map = fig.add_axes([0.20, 0.25, 0.60, 0.50])
    ax_map.set_aspect('equal')
    ax_map.axis('off')
    
    geo_data = get_world_geojson()
    
    if geo_data:
        patches = []
        facecolors = []
        
        for feature in geo_data['features']:
            iso_code = feature['id']
            if iso_code == 'ATA': # Skip Antarctica
                continue
                
            val = map_data_dict.get(iso_code, None)
            if val is not None:
                c = cmap(norm(val))
            else:
                c = '#f0f0f0' # Default grey
            
            geom_type = feature['geometry']['type']
            coords = feature['geometry']['coordinates']
            
            if geom_type == 'Polygon':
                polys = [coords]
            elif geom_type == 'MultiPolygon':
                polys = coords
            else:
                continue
                
            for poly_coords in polys:
                exterior = poly_coords[0]
                polygon = Polygon(exterior, closed=True)
                patches.append(polygon)
                facecolors.append(c)
        
        p = PatchCollection(patches, facecolors=facecolors, edgecolor='black', linewidth=0.3)
        ax_map.add_collection(p)
        ax_map.set_xlim(-180, 180)
        ax_map.set_ylim(-60, 85)
    else:
        # Fallback if offline
        ax_map.text(0.5, 0.5, "Map Data Unavailable (Offline)", ha='center', va='center', fontsize=14)
        ax_map.set_xlim(0, 1)
        ax_map.set_ylim(0, 1)
    
    # 2. Add Map Legend
    legend_labels = ['<10%', '10–15%', '15–20%', '20–30%', '30–40%', '40–50%', '>50%']
    patches = [Patch(color=c, label=l) for c, l in zip(map_colors_hex, legend_labels)]
    
    leg = ax_map.legend(handles=patches, loc='lower left', 
                        bbox_to_anchor=(-0.1, 0.05), 
                        title="GHG shares\nfrom food system",
                        frameon=False, fontsize=10, title_fontsize=11)
    leg._legend_box.align = "left"
    ax_map.text(-0.05, 0.0, "1990", transform=ax_map.transAxes, fontsize=11, ha='left')

    # 3. Add Pie Legend
    pie_patches = [
        Patch(color=c_land, label='Land based'),
        Patch(color=c_energy, label='Energy'),
        Patch(color=c_industry, label='Industry'),
        Patch(color=c_waste, label='Waste')
    ]
    fig.legend(handles=pie_patches, loc='lower right', bbox_to_anchor=(0.8, 0.22), 
               ncol=4, frameon=False, fontsize=11, handlelength=1.0, handleheight=1.0)

    # --- Plot Pie Charts ---
    name_map = {
        "Canada": "Canada", "OECD Europe": "OECD Europe", "Central Europe": "Central Europe",
        "Russia": "Russia", "Ukraine": "Ukraine", "Central Asia": "Central Asia",
        "Middle East": "Middle East", "Turkey": "Turkey", "China": "China",
        "USA": "United States", "Mexico": "Mexico", "Central America": "Central America",
        "Brazil": "Brazil", "South America": "South America", "South Africa": "South Africa",
        "West Africa": "West Africa", "East Africa": "East Africa", "North Africa": "North Africa",
        "India": "India", "Oceania": "Oceania", "Japan": "Japan",
        "Indonesia": "Indonesia", "South-East Asia": "Southeast Asia", "Korea": "Korea"
    }
    
    top_row = ["Canada", "OECD Europe", "Central Europe", "Russia", "Ukraine", "Central Asia", "Middle East", "Turkey", "China"]
    right_col = ["Indonesia", "South-East Asia", "Korea"]
    bottom_row = ["Japan", "Oceania", "India", "North Africa", "East Africa", "West Africa", "South Africa", "South America", "Brazil"]
    left_col = ["Central America", "Mexico", "USA"]
    
    def add_pie(region_key, x, y, size=0.08):
        row = df_pie[df_pie['Region'] == region_key]
        if row.empty:
            return
        
        vals = row.iloc[0][["Landbased", "Energy", "Industry", "Waste"]].values
        pcts = row.iloc[0][["Landbased_pct", "Energy_pct", "Industry_pct", "Waste_pct"]].values
        
        ax = fig.add_axes([x, y, size, size])
        wedges, texts = ax.pie(vals, colors=pie_colors, startangle=90, counterclock=False)
        
        for i, p in enumerate(pcts):
            if p >= 1.5:
                ang = (wedges[i].theta2 - wedges[i].theta1)/2. + wedges[i].theta1
                y_off = np.sin(np.deg2rad(ang))
                x_off = np.cos(np.deg2rad(ang))
                r = 0.7
                txt_color = 'white'
                ax.text(x_off*r, y_off*r, f"{int(round(p))}%", ha='center', va='center', 
                        color=txt_color, fontsize=9, fontweight='bold')
        
        display_name = name_map.get(region_key, region_key)
        ax.set_title(display_name, fontsize=11, pad=2)

    # Coordinates
    start_x, end_x = 0.05, 0.90
    y_top = 0.82
    x_step = (end_x - start_x) / (len(top_row) - 1)
    for i, region in enumerate(top_row):
        add_pie(region, start_x + i*x_step, y_top)

    start_x, end_x = 0.90, 0.05
    y_bot = 0.05
    x_step = (end_x - start_x) / (len(bottom_row) - 1)
    for i, region in enumerate(bottom_row):
        add_pie(region, start_x + i*x_step, y_bot)

    x_right = 0.88
    right_y_positions = [0.63, 0.45, 0.27]
    for i, region in enumerate(right_col):
        add_pie(region, x_right, right_y_positions[i])

    x_left = 0.05
    left_y_positions = [0.63, 0.45, 0.27]
    for i, region in enumerate(reversed(left_col)):
        add_pie(region, x_left, left_y_positions[i])

    fig.text(0.02, 0.95, 'a', fontsize=24, fontweight='bold')

    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Chart saved to {output_filename}")

if __name__ == "__main__":
    output_file = "output.png"
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
    
    try:
        plot_chart(output_file)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)