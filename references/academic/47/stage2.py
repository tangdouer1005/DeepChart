import sys
import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.path import Path

# ---------------------------------------------------------
# 1. Data Embedding
# ---------------------------------------------------------
source_data_md = """
| mouse_ensembl_gene | chromosome | mouse_symbol | position_Mb | clipped_abs_log10_q | marker_size_binned_q | p_value | q_value | transposon_donor_chr_H | transposon_donor_position_H_Mb | transposon_donor_chr_S | transposon_donor_position_S_Mb |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| ENSMUSG00000013663 | chr19 | Pten | 32.792 | 10 | 40 | 1.20758474311848e-47 | 2.071370109871128e-43 | 5 | 60 | 10 | 5 |
| ENSMUSG00000008575 | chr4 | Nfib | 82.498 | 10 | 40 | 1.108626390162786e-30 | 9.50813423523114e-27 | 5 | 60 | 10 | 5 |
| ENSMUSG00000058589 | chr10 | Anks1b | 90.423 | 10 | 40 | 7.43584404142083e-26 | 4.251567761416383e-22 | 5 | 60 | 10 | 5 |
| ENSMUSG00000063887 | chr3 | Nlgn1 | 25.879 | 10 | 40 | 8.894130140551156e-17 | 3.81402535752185e-13 | 5 | 60 | 10 | 5 |
| ENSMUSG00000038774 | chr10 | Ascc3 | 50.722 | 10 | 40 | 3.019122438068021e-16 | 8.631167863363461e-13 | 5 | 60 | 10 | 5 |
| ENSMUSG00000060843 | chr10 | Ctnna3 | 64.217 | 10 | 40 | 3.019122438068021e-16 | 8.631167863363461e-13 | 5 | 60 | 10 | 5 |
| ENSMUSG00000006586 | chr4 | Runx1t1 | 13.819 | 10 | 40 | 7.211911033593624e-16 | 1.767227285131878e-12 | 5 | 60 | 10 | 5 |
| ENSMUSG00000030067 | chr6 | Foxp1 | 99.223 | 10 | 40 | 1.813065192656477e-15 | 3.887438406204567e-12 | 5 | 60 | 10 | 5 |
| ENSMUSG00000063531 | chr5 | Sema3e | 14.141 | 10 | 40 | 1.951607893369725e-14 | 3.69640788561885e-11 | 5 | 60 | 10 | 5 |
| ENSMUSG00000028926 | chr5 | Cdk14 | 5.112 | 10 | 40 | 2.15496291355381e-14 | 3.69640788561885e-11 | 5 | 60 | 10 | 5 |
| ENSMUSG00000040118 | chr5 | Cacna2d1 | 16.155 | 10 | 40 | 5.854147248725938e-14 | 8.368015646449667e-11 | 5 | 60 | 10 | 5 |
| ENSMUSG00000055320 | chr7 | Tead1 | 112.793 | 10 | 40 | 5.854147248725938e-14 | 8.368015646449667e-11 | 5 | 60 | 10 | 5 |
| ENSMUSG00000035864 | chr10 | Syt1 | 108.754 | 10 | 40 | 6.87276779182222e-14 | 9.068352764086656e-11 | 5 | 60 | 10 | 5 |
| ENSMUSG00000039419 | chr6 | Cntnap2 | 46.182 | 9.274408875165069 | 20 | 4.338894325050555e-13 | 5.316075311256582e-10 | 5 | 60 | 10 | 5 |
| ENSMUSG00000045083 | chr4 | Lingo2 | 36.329 | 9.04339231236095 | 20 | 7.913322385737158e-13 | 9.049147925503295e-10 | 5 | 60 | 10 | 5 |
| ENSMUSG00000029212 | chr5 | Gabrb1 | 71.904 | 8.933544328602789 | 20 | 1.348163370912178e-12 | 1.165348097243393e-09 | 5 | 60 | 10 | 5 |
| ENSMUSG00000024109 | chr17 | Nrxn1 | 90.563 | 8.933544328602789 | 20 | 1.348163370912178e-12 | 1.165348097243393e-09 | 5 | 60 | 10 | 5 |
| ENSMUSG00000058571 | chr14 | Gpc6 | 117.451 | 8.933544328602789 | 20 | 1.562584168168719e-12 | 1.165348097243393e-09 | 5 | 60 | 10 | 5 |
| ENSMUSG00000038822 | chr10 | Hace1 | 45.645 | 8.933544328602789 | 20 | 1.562584168168719e-12 | 1.165348097243393e-09 | 5 | 60 | 10 | 5 |
| ENSMUSG00000019889 | chr10 | Ptprk | 28.336 | 8.933544328602789 | 20 | 1.562584168168719e-12 | 1.165348097243393e-09 | 5 | 60 | 10 | 5 |
| ENSMUSG00000029026 | chr4 | Trp73 | 154.098 | 8.933544328602789 | 20 | 1.562584168168719e-12 | 1.165348097243393e-09 | 5 | 60 | 10 | 5 |
| ENSMUSG00000038872 | chr8 | Zfhx3 | 108.452 | 8.933544328602789 | 20 | 1.562584168168719e-12 | 1.165348097243393e-09 | 5 | 60 | 10 | 5 |
| ENSMUSG00000028519 | chr4 | Dab1 | 104.182 | 8.933544328602789 | 20 | 1.562584168168719e-12 | 1.165348097243393e-09 | 5 | 60 | 10 | 5 |
| ENSMUSG00000059049 | chr4 | Frem1 | 82.975 | 7.79275398796945 | 20 | 2.254847454070844e-11 | 1.611558265819883e-08 | 5 | 60 | 10 | 5 |
| ENSMUSG00000022883 | chr16 | Robo1 | 72.677 | 7.755322292393169 | 20 | 2.867448663175697e-11 | 1.756619532837598e-08 | 5 | 60 | 10 | 5 |
| ENSMUSG00000047129 | chr10 | 1700113H08Rik | 87.144 | 7.755322292393169 | 20 | 2.867448663175697e-11 | 1.756619532837598e-08 | 5 | 60 | 10 | 5 |
| ENSMUSG00000024867 | chr19 | Pip5k1b | 24.425 | 7.755322292393169 | 20 | 2.867448663175697e-11 | 1.756619532837598e-08 | 5 | 60 | 10 | 5 |
| ENSMUSG00000029088 | chr5 | Kcnip4 | 48.957 | 7.755322292393169 | 20 | 2.867448663175697e-11 | 1.756619532837598e-08 | 5 | 60 | 10 | 5 |
| ENSMUSG00000034751 | chr13 | Mast4 | 103.033 | 7.741195003912194 | 20 | 3.068053343896148e-11 | 1.814700655443125e-08 | 5 | 60 | 10 | 5 |
| ENSMUSG00000031841 | chr8 | Cdh13 | 118.804 | 7.740988980001537 | 20 | 3.281199420804746e-11 | 1.815561731131091e-08 | 5 | 60 | 10 | 5 |
| ENSMUSG00000049690 | chr1 | Nckap5 | 126.372 | 7.740988980001537 | 20 | 3.281199420804746e-11 | 1.815561731131091e-08 | 5 | 60 | 10 | 5 |
| ENSMUSG00000022708 | chr16 | Zbtb20 | 43.275 | 6.871436686297166 | 20 | 2.508263765781603e-10 | 1.34450776170162e-07 | 5 | 60 | 10 | 5 |
| ENSMUSG00000056073 | chr10 | Grik2 | 49.442 | 6.590116846400034 | 20 | 4.943755748861007e-10 | 2.569704313945844e-07 | 5 | 60 | 10 | 5 |
| ENSMUSG00000060534 | chr18 | Dcc | 71.802 | 6.566980929562904 | 20 | 5.594506894959595e-10 | 2.710310642552901e-07 | 5 | 60 | 10 | 5 |
| ENSMUSG00000066392 | chr12 | Nrxn3 | 89.529 | 6.566980929562904 | 20 | 5.594506894959595e-10 | 2.710310642552901e-07 | 5 | 60 | 10 | 5 |
| ENSMUSG00000036019 | chr10 | Tmtc2 | 105.381 | 6.566980929562904 | 20 | 6.31313913324148e-10 | 2.710310642552901e-07 | 5 | 60 | 10 | 5 |
| ENSMUSG00000039697 | chr10 | Ncoa7 | 30.723 | 6.566980929562904 | 20 | 6.320318644092345e-10 | 2.710310642552901e-07 | 5 | 60 | 10 | 5 |
| ENSMUSG00000021991 | chr14 | Cacna2d3 | 29.313 | 6.566980929562904 | 20 | 6.320318644092345e-10 | 2.710310642552901e-07 | 5 | 60 | 10 | 5 |
| ENSMUSG00000069769 | chr11 | Msi2 | 88.529 | 6.566980929562904 | 20 | 6.320318644092345e-10 | 2.710310642552901e-07 | 5 | 60 | 10 | 5 |
| ENSMUSG00000028399 | chr4 | Ptprd | 76.268 | 6.566980929562904 | 20 | 6.320318644092345e-10 | 2.710310642552901e-07 | 5 | 60 | 10 | 5 |
| ENSMUSG00000008658 | chr16 | Rbfox1 | 6.648 | 6.307228022184571 | 20 | 1.206927493714482e-09 | 4.92914935706774e-07 | 5 | 60 | 10 | 5 |
| ENSMUSG00000002107 | chr2 | Celf2 | 6.968 | 6.307228022184571 | 20 | 1.206927493714482e-09 | 4.92914935706774e-07 | 5 | 60 | 10 | 5 |
| ENSMUSG00000020704 | chr11 | Asic2 | 81.424 | 5.874233769061759 | 20 | 3.34884154586137e-09 | 1.335876256654886e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000023826 | chr17 | Prkn | 11.452 | 5.633845954516532 | 20 | 5.96027961568568e-09 | 2.32356082381492e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000049176 | chrX | Frmpd4 | 167.96 | 5.630909782107293 | 20 | 6.137092145447497e-09 | 2.339323146019132e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000036766 | chr1 | Dner | 84.533 | 5.577656289096434 | 20 | 7.091881250388692e-09 | 2.644500849737331e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000030849 | chr7 | Fgfr2 | 131.643 | 5.513600417532399 | 20 | 8.646238381171568e-09 | 3.064781958875355e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000028033 | chr1 | Kcnq5 | 21.68 | 5.513600417532399 | 20 | 9.931811505965744e-09 | 3.064781958875355e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000040003 | chr5 | Magi2 | 19.966 | 5.513600417532399 | 20 | 9.931811505965744e-09 | 3.064781958875355e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000004637 | chr8 | Wwox | 114.896 | 5.513600417532399 | 20 | 9.931811505965744e-09 | 3.064781958875355e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000068205 | chr2 | Macrod2 | 141.394 | 5.513600417532399 | 20 | 1.107774042151647e-08 | 3.064781958875355e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000062991 | chr8 | Nrg1 | 32.35 | 5.513600417532399 | 20 | 1.107774042151647e-08 | 3.064781958875355e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000020166 | chr10 | Cnot2 | 116.533 | 5.513600417532399 | 20 | 1.107774042151647e-08 | 3.064781958875355e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000069670 | chr10 | Nkain2 | 32.29 | 5.513600417532399 | 20 | 1.107774042151647e-08 | 3.064781958875355e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000038368 | chr4 | Focad | 88.253 | 5.513600417532399 | 20 | 1.107774042151647e-08 | 3.064781958875355e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000022240 | chr15 | Ctnnd2 | 30.601 | 5.513600417532399 | 20 | 1.107774042151647e-08 | 3.064781958875355e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000031618 | chr8 | Nr3c2 | 77.072 | 5.513600417532399 | 20 | 1.107774042151647e-08 | 3.064781958875355e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000021699 | chr13 | Pde4d | 109.304 | 5.513600417532399 | 20 | 1.107774042151647e-08 | 3.064781958875355e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000010175 | chr1 | Prox1 | 190.144 | 5.513600417532399 | 20 | 1.107774042151647e-08 | 3.064781958875355e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000010517 | chr4 | Faf1 | 109.82 | 5.513600417532399 | 20 | 1.107774042151647e-08 | 3.064781958875355e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000022307 | chr15 | Oxr1 | 41.654 | 5.513600417532399 | 20 | 1.107774042151647e-08 | 3.064781958875355e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000037138 | chr1 | Aff3 | 38.421 | 5.513600417532399 | 20 | 1.107774042151647e-08 | 3.064781958875355e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000053580 | chr11 | Tanc2 | 105.76 | 5.421819949531997 | 20 | 1.39053047808069e-08 | 3.785995125479061e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000036469 | chr8 | March1 | 66.045 | 5.324065509929483 | 20 | 1.852120356912501e-08 | 4.741704549570169e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000053477 | chr18 | Tcf4 | 69.516 | 5.324065509929483 | 20 | 1.852120356912501e-08 | 4.741704549570169e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000038602 | chr10 | Slc35f1 | 52.901 | 5.324065509929483 | 20 | 1.852120356912501e-08 | 4.741704549570169e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000003746 | chr10 | Man1a | 53.991 | 5.324065509929483 | 20 | 1.852120356912501e-08 | 4.741704549570169e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000056004 | chr5 | 9330182L06Rik | 9.374 | 5.093182507025268 | 20 | 3.245835427015371e-08 | 8.068958707187632e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000041272 | chr4 | Tox | 6.839 | 5.093182507025268 | 20 | 3.245835427015371e-08 | 8.068958707187632e-06 | 5 | 60 | 10 | 5 |
| ENSMUSG00000015501 | chr10 | Hivep2 | 14.059 | 4.696790716475871 | 20 | 8.202896576416912e-08 | 2.010061213932561e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000026872 | chr2 | Zeb2 | 45.051 | 4.691399065282109 | 20 | 8.42401624778375e-08 | 2.035171136594854e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000052512 | chr7 | Nav2 | 49.285 | 4.527042357808055 | 20 | 1.440807558334766e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000063458 | chr14 | Lrmda | 22.538 | 4.527042357808055 | 20 | 1.588778873098107e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000017978 | chr6 | Cadps2 | 23.551 | 4.527042357808055 | 20 | 1.588778873098107e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000042348 | chr13 | Arl15 | 113.976 | 4.527042357808055 | 20 | 1.588778873098107e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000038056 | chr5 | Kmt2c | 25.385 | 4.527042357808055 | 20 | 1.588778873098107e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000074505 | chr9 | Fat3 | 16.206 | 4.527042357808055 | 20 | 1.588778873098107e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000021047 | chr12 | Nova1 | 46.757 | 4.527042357808055 | 20 | 1.588778873098107e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000056602 | chr5 | Fry | 150.308 | 4.527042357808055 | 20 | 1.588778873098107e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000102758 | chr3 | Naaladl2 | 24.291 | 4.527042357808055 | 20 | 1.588778873098107e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000033569 | chr1 | Adgrb3 | 25.449 | 4.527042357808055 | 20 | 1.588778873098107e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000036298 | chr15 | Slc2a13 | 91.42 | 4.527042357808055 | 20 | 1.588778873098107e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000028977 | chr4 | Casz1 | 148.88 | 4.527042357808055 | 20 | 1.588778873098107e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000028525 | chr4 | Pde4b | 102.347 | 4.527042357808055 | 20 | 1.667527501994164e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000004698 | chr12 | Hdac9 | 34.333 | 4.527042357808055 | 20 | 1.749600637848096e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000059974 | chr9 | Ntm | 29.479 | 4.527042357808055 | 20 | 1.749600637848096e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000036815 | chr1 | Dpp10 | 124.084 | 4.527042357808055 | 20 | 1.749600637848096e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000032452 | chr9 | Clstn2 | 97.739 | 4.527042357808055 | 20 | 1.749600637848096e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000022812 | chr16 | Gsk3b | 38.168 | 4.527042357808055 | 20 | 1.749600637848096e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000031822 | chr8 | Gse1 | 120.405 | 4.527042357808055 | 20 | 1.749600637848096e-07 | 2.971376211981028e-05 | nan | nan | nan | nan |
| ENSMUSG00000022012 | chr14 | Enox1 | 77.439 | 4.527042357808055 | 20 | 1.749600637848096e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000034813 | chr10 | Grip1 | 119.771 | 4.527042357808055 | 20 | 1.749600637848096e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000059187 | chr6 | Tafa1 | 96.385 | 4.527042357808055 | 20 | 1.749600637848096e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000026335 | chr1 | Pam | 97.945 | 4.527042357808055 | 20 | 1.749600637848096e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000024268 | chr18 | Celf4 | 25.616 | 4.527042357808055 | 20 | 1.749600637848096e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000028161 | chr3 | Ppp3ca | 136.804 | 4.527042357808055 | 20 | 1.749600637848096e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000050840 | chr1 | Cdh20 | 104.882 | 4.527042357808055 | 20 | 1.749600637848096e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000026721 | chr1 | Rabgap1l | 160.506 | 4.527042357808055 | 20 | 1.749600637848096e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000063760 | chr10 | Rnf217 | 31.551 | 4.527042357808055 | 20 | 1.749600637848096e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000039683 | chr5 | Sdk1 | 141.729 | 4.527042357808055 | 20 | 1.749600637848096e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000035189 | chr10 | Ano4 | 89.147 | 4.527042357808055 | 20 | 1.749600637848096e-07 | 2.971376211981028e-05 | 5 | 60 | 10 | 5 |
| ENSMUSG00000022521 | chr16 | Crebbp | 4.148 | 2.832574927767207 | 20 | 1.294380411459524e-05 | 0.0014703647150837 | nan | nan | nan | nan |
| ENSMUSG00000025862 | chrX | Stag2 | 42.213 | 3.533012983931836 | 20 | 2.460420974071137e-06 | 0.0002930805622794 | nan | nan | nan | nan |
| ENSMUSG00000024211 | chr6 | Grm8 | 27.705 | 1.051341166538855 | 10 | 0.0028644673549255 | 0.0888502866890381 | nan | nan | nan | nan |
"""

# ---------------------------------------------------------
# 2. Data Processing
# ---------------------------------------------------------

def get_data():
    # Read markdown table
    # Use dtype=str to read everything as string first to avoid parsing errors on the separator line
    df = pd.read_csv(io.StringIO(source_data_md), sep='|', dtype=str)
    
    # Clean column names (strip whitespace)
    df.columns = [c.strip() for c in df.columns]
    
    # Drop empty columns from markdown parsing (first and last often empty due to | borders)
    df = df.dropna(axis=1, how='all')
    
    # Filter out the separator row (contains '---')
    # We check the first column for the separator pattern
    if not df.empty:
        df = df[~df.iloc[:, 0].astype(str).str.contains('---')]
    
    # Clean string columns
    df['chromosome'] = df['chromosome'].str.strip()
    df['mouse_symbol'] = df['mouse_symbol'].str.strip()
    
    # Convert numeric columns
    numeric_cols = [
        'position_Mb', 'clipped_abs_log10_q', 'marker_size_binned_q', 
        'p_value', 'q_value', 
        'transposon_donor_chr_H', 'transposon_donor_position_H_Mb', 
        'transposon_donor_chr_S', 'transposon_donor_position_S_Mb'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
    return df

def get_chrom_info():
    # Standard Mouse Chromosome Lengths (Mb) - approximate for visualization
    # Order: 1..19, X, Y
    chrom_order = [f'chr{i}' for i in range(1, 20)] + ['chrX', 'chrY']
    
    # Approximate lengths based on mm10
    lengths = {
        'chr1': 195, 'chr2': 182, 'chr3': 160, 'chr4': 156, 'chr5': 151,
        'chr6': 150, 'chr7': 145, 'chr8': 129, 'chr9': 124, 'chr10': 130,
        'chr11': 122, 'chr12': 120, 'chr13': 120, 'chr14': 124, 'chr15': 104,
        'chr16': 98, 'chr17': 94, 'chr18': 90, 'chr19': 61, 'chrX': 171, 'chrY': 91
    }
    
    # Colors extracted from the image
    colors = {
        'chr1': '#4daf4a', 'chr2': '#e41a1c', 'chr3': '#984ea3', 'chr4': '#a65628',
        'chr5': '#377eb8', 'chr6': '#f781bf', 'chr7': '#999999', 'chr8': '#17becf',
        'chr9': '#e41a1c', 'chr10': '#ff7f00', 'chr11': '#4daf4a', 'chr12': '#984ea3',
        'chr13': '#a65628', 'chr14': '#f781bf', 'chr15': '#999999', 'chr16': '#17becf',
        'chr17': '#4daf4a', 'chr18': '#e41a1c', 'chr19': '#984ea3', 'chrX': '#a65628',
        'chrY': '#f781bf'
    }
    
    return chrom_order, lengths, colors

# ---------------------------------------------------------
# 3. Plotting Logic
# ---------------------------------------------------------

def main():
    output_file = sys.argv[1] if len(sys.argv) > 1 else "output.png"
    
    df = get_data()
    chrom_order, chrom_lengths, chrom_colors = get_chrom_info()
    
    # Setup Polar Plot
    fig = plt.figure(figsize=(10, 10), dpi=300)
    ax = fig.add_subplot(111, projection='polar')
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.axis('off')
    
    # Calculate Chromosome Arcs
    total_len = sum(chrom_lengths.values())
    gap_degrees = 1.5
    gap_rad = np.deg2rad(gap_degrees)
    total_gap_rad = gap_rad * len(chrom_order)
    available_rad = 2 * np.pi - total_gap_rad
    
    chrom_coords = {}
    current_angle = 0
    
    # Radius settings
    ideogram_radius = 80
    ideogram_width = 10
    scatter_base_radius = 95
    scatter_scale = 3 # Multiplier for log10_q
    
    # Draw Chromosomes
    for chrom in chrom_order:
        length = chrom_lengths[chrom]
        angle_span = (length / total_len) * available_rad
        start_angle = current_angle
        end_angle = current_angle + angle_span
        mid_angle = (start_angle + end_angle) / 2
        
        chrom_coords[chrom] = {
            'start': start_angle,
            'end': end_angle,
            'length_mb': length,
            'color': chrom_colors[chrom]
        }
        
        # Draw Ideogram Bar
        ax.bar(x=mid_angle, height=ideogram_width, width=angle_span, 
               bottom=ideogram_radius, color=chrom_colors[chrom], 
               edgecolor='white', linewidth=0.5, alpha=1.0)
        
        # Draw Chromosome Label (1, 2, X...)
        label = chrom.replace('chr', '')
        rot_deg = np.rad2deg(mid_angle)
        # Flip text if on the left side
        text_rot = -rot_deg
        if 90 < rot_deg < 270:
            text_rot += 180
            
        ax.text(mid_angle, ideogram_radius + ideogram_width/2, label, 
                ha='center', va='center', rotation=text_rot, 
                color='black', fontsize=8, fontweight='bold')
        
        current_angle += angle_span + gap_rad

    # Helper to map genomic position to polar angle
    def get_theta(chrom, pos_mb):
        if chrom not in chrom_coords: return 0
        coords = chrom_coords[chrom]
        # Normalize pos within chrom
        fraction = pos_mb / coords['length_mb']
        # Clamp fraction (some genes might be slightly outside approx length)
        fraction = max(0, min(1, fraction))
        return coords['start'] + fraction * (coords['end'] - coords['start'])

    # Draw Links (Bundles)
    # Bezier Curve Helper for Polar
    def plot_bezier(theta1, r1, theta2, r2, color, ax):
        # Convert to Cartesian
        x1 = r1 * np.sin(theta1)
        y1 = r1 * np.cos(theta1)
        x2 = r2 * np.sin(theta2)
        y2 = r2 * np.cos(theta2)
        
        # Control point: Center (0,0)
        verts = [(x1, y1), (0, 0), (x2, y2)]
        codes = [Path.MOVETO, Path.CURVE3, Path.CURVE3]
        path = Path(verts, codes)
        
        # Generate points along the curve
        t = np.linspace(0, 1, 50)
        # Quadratic Bezier formula with P1=(0,0): (1-t)^2 * P0 + t^2 * P2
        curve_x = (1-t)**2 * x1 + t**2 * x2
        curve_y = (1-t)**2 * y1 + t**2 * y2
        
        # Convert back to Polar
        curve_r = np.sqrt(curve_x**2 + curve_y**2)
        curve_theta = np.arctan2(curve_x, curve_y) # Note: using x,y for theta due to polar setup
        
        ax.plot(curve_theta, curve_r, color=color, alpha=0.2, linewidth=0.3)

    # Draw links
    for idx, row in df.iterrows():
        if pd.notna(row['transposon_donor_chr_H']):
            # Link H (Blue)
            donor_chr = f"chr{int(row['transposon_donor_chr_H'])}"
            donor_pos = row['transposon_donor_position_H_Mb']
            target_chr = row['chromosome']
            target_pos = row['position_Mb']
            
            theta_start = get_theta(donor_chr, donor_pos)
            theta_end = get_theta(target_chr, target_pos)
            
            plot_bezier(theta_start, ideogram_radius, theta_end, ideogram_radius, '#377eb8', ax)

        if pd.notna(row['transposon_donor_chr_S']):
            # Link S (Orange)
            donor_chr = f"chr{int(row['transposon_donor_chr_S'])}"
            donor_pos = row['transposon_donor_position_S_Mb']
            target_chr = row['chromosome']
            target_pos = row['position_Mb']
            
            theta_start = get_theta(donor_chr, donor_pos)
            theta_end = get_theta(target_chr, target_pos)
            
            plot_bezier(theta_start, ideogram_radius, theta_end, ideogram_radius, '#ff7f00', ax)

    # Draw Scatter Points
    for idx, row in df.iterrows():
        chrom = row['chromosome']
        if chrom not in chrom_coords: continue
        
        theta = get_theta(chrom, row['position_Mb'])
        # Radial position based on significance
        # Clip visual height to avoid extreme outliers
        val = min(row['clipped_abs_log10_q'], 12) 
        r = scatter_base_radius + val * scatter_scale
        
        size = row['marker_size_binned_q'] * 1.5 # Scale up slightly for visibility
        color = chrom_colors[chrom]
        
        ax.scatter(theta, r, s=size, c=color, edgecolors='black', linewidth=0.3, zorder=10)

    # Draw Labels
    # List of genes to label based on the image
    labels_to_show = [
        'Pten', 'Stag2', 'Frmpd4', 'Kcnq5', 'Dner', 'Nckap5', 'Celf2', 'Zeb2', 
        'Macrod2', 'Nlgn1', 'Ppp3ca', 'Runx1t1', 'Nfib', 'Trp73', 'Sema3e', 
        'Cacna2d1', 'Gabrb1', 'Grm8', 'Cntnap2', 'Foxp1', 'Nav2', 'Tead1', 
        'Nrg1', 'Zfhx3', 'Fat3', 'Clstn2', 'Ptprk', 'Ascc3', 'Anks1b', 'Syt1', 
        'Msi2', 'Asic2', 'Hdac9', 'Nova1', 'Nrxn3', 'Mast4', 'Cacna2d3', 'Gpc6', 
        'Ctnnd2', 'Crebbp', 'Rbfox1', 'Zbtb20', 'Robo1', 'Prkn', 'Nrxn1', 
        'Celf4', 'Dcc', 'Pip5k1b'
    ]
    
    boxed_labels = ['Pten', 'Nfib', 'Trp73', 'Crebbp']

    for idx, row in df.iterrows():
        gene = row['mouse_symbol']
        if gene in labels_to_show:
            chrom = row['chromosome']
            theta = get_theta(chrom, row['position_Mb'])
            val = min(row['clipped_abs_log10_q'], 12)
            r = scatter_base_radius + val * scatter_scale
            
            # Label placement logic
            label_r = r + 10
            
            rot_deg = np.rad2deg(theta)
            text_rot = -rot_deg
            ha = 'left'
            va = 'center'
            
            # Adjust rotation for readability
            if 90 < rot_deg < 270:
                text_rot += 180
                ha = 'right'
                label_r += 2 # Push out slightly more on left
            
            # Box properties
            bbox_props = None
            if gene in boxed_labels:
                bbox_props = dict(boxstyle="round,pad=0.3", fc="white", ec="black", lw=1)
            
            # Draw line from point to label
            # Simple radial line
            ax.plot([theta, theta], [r, label_r-2], color='black', linewidth=0.5, zorder=5)
            
            ax.text(theta, label_r, gene, rotation=text_rot, ha=ha, va=va, 
                    fontsize=9, bbox=bbox_props, zorder=20)

    # Add 'a' label for figure panel
    plt.figtext(0.05, 0.95, 'a', fontsize=20, fontweight='bold')

    plt.savefig(output_file, bbox_inches='tight', pad_inches=0.1)

if __name__ == "__main__":
    main()