# Exploratory runs (branch explore, 08.–09.11.2026)

Chosen after the main results; descriptive only, no hypothesis is decided. Relative reduction as in the main report (positive favours the first method); Wilcoxon p without correction.

## Real datasets, seed 0 (32 datasets)

Bar set before running: raw products change the picture only with a positive median against base and at least 20 of 32 wins. **Result: median -0.23%, 15/17/0 → does not change the picture.**

| scope | comparison | method | reference | datasets | median_reduction | wins | losses | zeros | p | hl_estimate | ci95_low | ci95_high |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| all | raw products vs base | residual raw | base | 32 | -0.0023 | 15 | 17 | 0 | 0.4105 | -0.004 | -0.0306 | 0.0052 |
| all | raw vs centred products | residual raw | residual | 32 | 0.0031 | 17 | 14 | 1 | 0.6522 | 0.0027 | -0.0131 | 0.0134 |
| all | centred products vs base | residual | base | 32 | -0.0056 | 13 | 18 | 1 | 0.1264 | -0.0094 | -0.0266 | 0.0021 |
| all | cost: shuffled products vs base | shuffled | base | 32 | -0.0304 | 6 | 26 | 0 | 0.000234 | -0.0527 | -0.0836 | -0.0203 |
| all | information: products vs shuffled | residual | shuffled | 32 | 0.0239 | 25 | 7 | 0 | 0.000513 | 0.0309 | 0.0132 | 0.0806 |
| all | scaled sampling: products | residual scaled | residual | 32 | 0 | 15 | 14 | 3 | 0.5096 | 0.0019 | -0.0044 | 0.0206 |
| all | scaled sampling: shuffled | shuffled scaled | shuffled | 32 | 0.0063 | 20 | 10 | 2 | 0.1156 | 0.0074 | -0.0036 | 0.0231 |
| all | scaled products vs base | residual scaled | base | 32 | -0.0066 | 10 | 22 | 0 | 0.2312 | -0.0067 | -0.0235 | 0.0082 |
| all | scaled shuffled vs base | shuffled scaled | base | 32 | -0.0284 | 5 | 27 | 0 | 2.02e-05 | -0.0355 | -0.0741 | -0.0183 |
| classification | raw products vs base | residual raw | base | 16 | -0.0023 | 8 | 8 | 0 | 0.4637 | - | - | - |
| classification | raw vs centred products | residual raw | residual | 16 | -0.0025 | 6 | 9 | 1 | 0.9096 | - | - | - |
| classification | centred products vs base | residual | base | 16 | -0.0022 | 7 | 8 | 1 | 0.3942 | - | - | - |
| classification | cost: shuffled products vs base | shuffled | base | 16 | -0.0748 | 4 | 12 | 0 | 0.0443 | - | - | - |
| classification | information: products vs shuffled | residual | shuffled | 16 | 0.0365 | 13 | 3 | 0 | 0.029 | - | - | - |
| classification | scaled sampling: products | residual scaled | residual | 16 | -0.0062 | 6 | 10 | 0 | 1 | - | - | - |
| classification | scaled sampling: shuffled | shuffled scaled | shuffled | 16 | -0.000633 | 7 | 9 | 0 | 0.8209 | - | - | - |
| classification | scaled products vs base | residual scaled | base | 16 | -0.0056 | 6 | 10 | 0 | 0.7057 | - | - | - |
| classification | scaled shuffled vs base | shuffled scaled | base | 16 | -0.0364 | 3 | 13 | 0 | 0.0063 | - | - | - |
| regression | raw products vs base | residual raw | base | 16 | -0.0023 | 7 | 9 | 0 | 0.6322 | - | - | - |
| regression | raw vs centred products | residual raw | residual | 16 | 0.0063 | 11 | 5 | 0 | 0.2744 | - | - | - |
| regression | centred products vs base | residual | base | 16 | -0.0078 | 6 | 10 | 0 | 0.1167 | - | - | - |
| regression | cost: shuffled products vs base | shuffled | base | 16 | -0.0282 | 2 | 14 | 0 | 0.000305 | - | - | - |
| regression | information: products vs shuffled | residual | shuffled | 16 | 0.0146 | 12 | 4 | 0 | 0.0092 | - | - | - |
| regression | scaled sampling: products | residual scaled | residual | 16 | 0.0026 | 9 | 4 | 3 | 0.064 | - | - | - |
| regression | scaled sampling: shuffled | shuffled scaled | shuffled | 16 | 0.0096 | 13 | 1 | 2 | 0.0092 | - | - | - |
| regression | scaled products vs base | residual scaled | base | 16 | -0.0066 | 4 | 12 | 0 | 0.1297 | - | - | - |
| regression | scaled shuffled vs base | shuffled scaled | base | 16 | -0.0241 | 2 | 14 | 0 | 0.00058 | - | - | - |

CPU-hours per configuration: base 0.93, residual 1.24, residual raw 1.27, residual scaled 1.46, shuffled 1.51, shuffled scaled 1.72

## Identity check against the main runs (seed 0)

| method | runs compared | identical |
|---|---|---|
| base | 160 | 160 |
| residual_xx | 160 | 160 |

## Synthetic controls, 3 seeds × 5 folds

score = balanced accuracy (xor) or RMSE (pair); reduction_vs_base on the error.

| dataset | method | mean | std | reduction_vs_base |
|---|---|---|---|---|
| raw_pair | base | 0.5858 | 0.0329 | 0 |
| raw_pair | lightgbm | 0.5809 | 0.0234 | 0.0084 |
| raw_pair | random | 0.6014 | 0.0377 | -0.0259 |
| raw_pair | residual | 0.6 | 0.0348 | -0.0237 |
| raw_pair | residual raw | 0.5588 | 0.0312 | 0.0461 |
| raw_pair | rf | 0.788 | 0.0405 | -0.2566 |
| raw_pair | rf + target | 0.6891 | 0.0312 | -0.1499 |
| raw_pair | rf + target raw | 0.5631 | 0.0264 | 0.0388 |
| raw_pair | shuffled | 0.5942 | 0.0339 | -0.0141 |
| raw_pair | target | 0.6009 | 0.0356 | -0.0251 |
| raw_pair | target raw | 0.5588 | 0.0312 | 0.0461 |
| raw_xor | base | 0.8505 | 0.0183 | 0 |
| raw_xor | lightgbm | 0.8491 | 0.0242 | -0.0093 |
| raw_xor | random | 0.8485 | 0.0208 | -0.0132 |
| raw_xor | residual | 0.8554 | 0.0207 | 0.0328 |
| raw_xor | residual raw | 0.8796 | 0.0198 | 0.1946 |
| raw_xor | rf | 0.8436 | 0.0242 | -0.0441 |
| raw_xor | rf + target | 0.8498 | 0.0201 | -0.0047 |
| raw_xor | rf + target raw | 0.8776 | 0.0185 | 0.1813 |
| raw_xor | shuffled | 0.8543 | 0.02 | 0.0254 |
| raw_xor | target | 0.8547 | 0.0205 | 0.0281 |
| raw_xor | target raw | 0.8803 | 0.0199 | 0.1993 |
| wide_pair | base | 2.4907 | 0.1851 | 0 |
| wide_pair | lightgbm | 1.4609 | 0.1456 | 0.4135 |
| wide_pair | random | 2.5244 | 0.266 | -0.0133 |
| wide_pair | residual | 1.0697 | 0.1389 | 0.5705 |
| wide_pair | residual raw | 1.0685 | 0.1365 | 0.571 |
| wide_pair | rf | 2.6768 | 0.1851 | -0.0695 |
| wide_pair | rf + target | 1.7298 | 0.1758 | 0.3055 |
| wide_pair | rf + target raw | 1.7329 | 0.1735 | 0.3043 |
| wide_pair | shuffled | 2.7114 | 0.1897 | -0.0814 |
| wide_pair | target | 1.0724 | 0.1361 | 0.5694 |
| wide_pair | target raw | 1.0708 | 0.1325 | 0.5701 |
| wide_xor | base | 0.603 | 0.0338 | 0 |
| wide_xor | lightgbm | 0.7748 | 0.061 | 0.4327 |
| wide_xor | random | 0.6967 | 0.1486 | 0.236 |
| wide_xor | residual | 0.8697 | 0.0197 | 0.6718 |
| wide_xor | residual raw | 0.8798 | 0.0202 | 0.6972 |
| wide_xor | rf | 0.6022 | 0.0371 | -0.002 |
| wide_xor | rf + target | 0.8674 | 0.0215 | 0.666 |
| wide_xor | rf + target raw | 0.8801 | 0.0209 | 0.698 |
| wide_xor | shuffled | 0.5535 | 0.0312 | -0.1109 |
| wide_xor | target | 0.8691 | 0.0207 | 0.6703 |
| wide_xor | target raw | 0.8795 | 0.0199 | 0.6965 |

## True pair among the chosen products (synthetic)

| dataset | method | layers | true pair chosen | share |
|---|---|---|---|---|
| raw_pair | random | layer 1 | 14/45 | 0.311 |
| raw_pair | random | layers 2+ | 28/135 | 0.207 |
| raw_pair | residual | layer 1 | 45/45 | 1 |
| raw_pair | residual | layers 2+ | 81/135 | 0.6 |
| raw_pair | residual raw | layer 1 | 45/45 | 1 |
| raw_pair | residual raw | layers 2+ | 58/90 | 0.644 |
| raw_pair | rf + target | layer 1 | 15/15 | 1 |
| raw_pair | rf + target raw | layer 1 | 15/15 | 1 |
| raw_pair | shuffled | layer 1 | 45/45 | 1 |
| raw_pair | shuffled | layers 2+ | 97/135 | 0.719 |
| raw_pair | target | layer 1 | 45/45 | 1 |
| raw_pair | target | layers 2+ | 135/135 | 1 |
| raw_pair | target raw | layer 1 | 45/45 | 1 |
| raw_pair | target raw | layers 2+ | 90/90 | 1 |
| raw_xor | random | layer 1 | 12/45 | 0.267 |
| raw_xor | random | layers 2+ | 18/108 | 0.167 |
| raw_xor | residual | layer 1 | 45/45 | 1 |
| raw_xor | residual | layers 2+ | 28/93 | 0.301 |
| raw_xor | residual raw | layer 1 | 45/45 | 1 |
| raw_xor | residual raw | layers 2+ | 56/129 | 0.434 |
| raw_xor | rf + target | layer 1 | 15/15 | 1 |
| raw_xor | rf + target raw | layer 1 | 15/15 | 1 |
| raw_xor | shuffled | layer 1 | 45/45 | 1 |
| raw_xor | shuffled | layers 2+ | 50/114 | 0.439 |
| raw_xor | target | layer 1 | 45/45 | 1 |
| raw_xor | target | layers 2+ | 99/99 | 1 |
| raw_xor | target raw | layer 1 | 45/45 | 1 |
| raw_xor | target raw | layers 2+ | 132/132 | 1 |
| wide_pair | random | layer 1 | 4/45 | 0.089 |
| wide_pair | random | layers 2+ | 5/135 | 0.037 |
| wide_pair | residual | layer 1 | 45/45 | 1 |
| wide_pair | residual | layers 2+ | 189/189 | 1 |
| wide_pair | residual raw | layer 1 | 45/45 | 1 |
| wide_pair | residual raw | layers 2+ | 189/189 | 1 |
| wide_pair | rf + target | layer 1 | 15/15 | 1 |
| wide_pair | rf + target raw | layer 1 | 15/15 | 1 |
| wide_pair | shuffled | layer 1 | 45/45 | 1 |
| wide_pair | shuffled | layers 2+ | 138/138 | 1 |
| wide_pair | target | layer 1 | 45/45 | 1 |
| wide_pair | target | layers 2+ | 183/183 | 1 |
| wide_pair | target raw | layer 1 | 45/45 | 1 |
| wide_pair | target raw | layers 2+ | 189/189 | 1 |
| wide_xor | random | layer 1 | 3/45 | 0.067 |
| wide_xor | random | layers 2+ | 10/138 | 0.072 |
| wide_xor | residual | layer 1 | 45/45 | 1 |
| wide_xor | residual | layers 2+ | 140/153 | 0.915 |
| wide_xor | residual raw | layer 1 | 45/45 | 1 |
| wide_xor | residual raw | layers 2+ | 126/144 | 0.875 |
| wide_xor | rf + target | layer 1 | 15/15 | 1 |
| wide_xor | rf + target raw | layer 1 | 15/15 | 1 |
| wide_xor | shuffled | layer 1 | 45/45 | 1 |
| wide_xor | shuffled | layers 2+ | 165/165 | 1 |
| wide_xor | target | layer 1 | 45/45 | 1 |
| wide_xor | target | layers 2+ | 153/153 | 1 |
| wide_xor | target raw | layer 1 | 45/45 | 1 |
| wide_xor | target raw | layers 2+ | 138/138 | 1 |

## 09.11: categories one-hot encoded (seed 0, 32 datasets)

Credit Default (SEX, EDUCATION, MARRIAGE), Auto MPG (origin) and Energy (orientation, glazing-area distribution) ran with these columns number-coded. Here they are one-hot encoded, as the plan says, and the six comparisons of seed 0 are recomputed with the three datasets swapped in. Seed streams depend on the dataset name, so the one-hot runs also differ by seed noise.

Bar set before running: the deviation matters only if a median changes sign or a Holm-adjusted p crosses 0.05. **Result: does not matter** (0 of 6 comparisons change).

| comparison | median_reduction_as_run | wins_as_run | losses_as_run | zeros_as_run | p_as_run | p_holm_as_run | median_reduction_onehot | wins_onehot | losses_onehot | zeros_onehot | p_onehot | p_holm_onehot |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H1 | -0.0056 | 13 | 18 | 1 | 0.1264 | 0.6319 | -0.0056 | 13 | 18 | 1 | 0.1216 | 0.608 |
| H2a | 0.001 | 17 | 15 | 0 | 0.8465 | 1 | 0.0018 | 18 | 14 | 0 | 0.8177 | 1 |
| H2b | 0 | 13 | 14 | 5 | 0.7731 | 1 | 0 | 14 | 13 | 5 | 0.4279 | 1 |
| H3 | 0 | 10 | 15 | 7 | 0.1425 | 0.6319 | 0 | 11 | 13 | 8 | 0.1615 | 0.6461 |
| H4 | 0 | 12 | 13 | 7 | 0.4926 | 1 | 0 | 12 | 12 | 8 | 0.3914 | 1 |
| H5 | 0 | 9 | 15 | 8 | 0.0455 | 0.273 | 0 | 9 | 14 | 9 | 0.0516 | 0.3095 |

Per dataset: reduction of each comparison as run and one-hot (seed 0), against the range of the as-run reduction over seeds 0–2.

| dataset | comparison | as_run | onehot | seed_range |
|---|---|---|---|---|
| auto_mpg | H1 | -0.0105 | 0.0146 | 0.0476 |
| auto_mpg | H2a | -0.0289 | 0.011 | 0.0548 |
| auto_mpg | H2b | 0.0391 | 0.0285 | 0.0299 |
| auto_mpg | H3 | -0.0011 | 0 | 0.011 |
| auto_mpg | H4 | -0.001 | 0 | 0.0015 |
| auto_mpg | H5 | -0.0011 | 0 | 0.0049 |
| credit_default | H1 | 0.0026 | 0.0023 | 0.0033 |
| credit_default | H2a | -0.0017 | 0.0018 | 0.0043 |
| credit_default | H2b | 0.007 | 0.0115 | 0.0085 |
| credit_default | H3 | -0.0028 | 0.0017 | 0.0094 |
| credit_default | H4 | -0.0012 | -0.0022 | 0.0022 |
| credit_default | H5 | -0.0019 | -0.0041 | 0.0022 |
| energy | H1 | 0.0076 | -0.0376 | 0.0416 |
| energy | H2a | 0.0355 | -0.0142 | 0.0367 |
| energy | H2b | -0.023 | 0.2879 | 0.0521 |
| energy | H3 | 0.0062 | 0.0094 | 0.0281 |
| energy | H4 | -0.0047 | -0.0549 | 0.0022 |
| energy | H5 | 0.0003 | 0.0066 | 0.0223 |

Error change from one-hot encoding (seed 0, mean over 5 folds):

| method | auto_mpg | credit_default | energy |
|---|---|---|---|
| base | 0.0059 | -0.0007 | 0.0818 |
| combined | -0.0165 | 0.0072 | 0.1484 |
| lightgbm | 0.0003 | -0.0028 | 0.0588 |
| monotone | 0.0048 | 0.0016 | 0.0749 |
| nonlinear | 0.0049 | 0.0004 | 0.1392 |
| random_xx | 0.0212 | 0.0031 | 0.077 |
| residual_xx | -0.0192 | -0.0004 | 0.1326 |
| rf | 0.0086 | -0.0018 | 0.2792 |
| rf_target_xx | -0.0501 | -0.0006 | 1.8761 |
| target_xx | -0.0298 | 0.0041 | 0.628 |
| xp_mi | 0.0048 | -0.0051 | 0.0782 |

## 09.11: how strong must an interaction be? (13 regression datasets, seed 0)

Two standard-normal columns u1, u2 are added and the target becomes y + λ·sd(y)·u1·u2, so the interaction explains λ²/(1+λ²) of the new target's variance (0, 6, 20, 50%).

Bar (ours), set before running: at a given λ products help if residual-XX vs base has a positive median and at least 9 of 13 wins. **Result: met at λ = 0.25, 0.5, 1; smallest 0.25.** Prediction written before the run: met at 1, probably at 0.5, open at 0.25, not at 0.

| strength | variance_share | comparison | datasets | median_reduction | wins | losses | zeros | p | hl_estimate | ci95_low | ci95_high | planted_pair_layer1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0 | products vs base | 13 | -0.0089 | 3 | 10 | 0 | 0.2163 | -0.0071 | -0.027 | 0.015 | 4/195 |
| 0 | 0 | RF + products vs RF | 13 | -0.008 | 3 | 10 | 0 | 0.3054 | -0.008 | -0.018 | 0.0979 | 0/65 |
| 0.25 | 0.0588 | products vs base | 13 | 0.0166 | 11 | 2 | 0 | 0.0479 | 0.0354 | 0.000911 | 0.0876 | 128/195 |
| 0.25 | 0.0588 | RF + products vs RF | 13 | 0.0099 | 8 | 5 | 0 | 0.1909 | 0.0541 | -0.0085 | 0.1289 | 45/65 |
| 0.5 | 0.2 | products vs base | 13 | 0.1009 | 13 | 0 | 0 | 0.000244 | 0.1347 | 0.0785 | 0.2313 | 182/195 |
| 0.5 | 0.2 | RF + products vs RF | 13 | 0.1079 | 12 | 1 | 0 | 0.000488 | 0.1365 | 0.0659 | 0.2424 | 60/65 |
| 1 | 0.5 | products vs base | 13 | 0.2504 | 13 | 0 | 0 | 0.000244 | 0.2465 | 0.1879 | 0.3309 | 195/195 |
| 1 | 0.5 | RF + products vs RF | 13 | 0.2617 | 13 | 0 | 0 | 0.000244 | 0.2808 | 0.1937 | 0.3854 | 65/65 |

planted_pair_layer1: layer-1 selections (fold models) that include (u1, u2).

## 09.11: interaction measure (LightGBM stumps vs 31 leaves, seed 0, 5 folds)

measure = relative error reduction from stumps to 31-leaf trees. 0 fits stopped at the tree cap. Over the 32 datasets, Spearman ρ with H1's per-dataset reduction (main run) = -0.126 (p = 0.493); with RF + products vs RF = -0.172 (p = 0.348). The pilot gave ρ = 0.00 with H1.

| dataset | error_stumps | error_deep | measure | H1_reduction | rf_products_reduction |
|---|---|---|---|---|---|
| heart_statlog | 0.1533 | 0.1958 | -0.217 | 0.0158 | -0.0218 |
| cardiotocography | 0.1656 | 0.2058 | -0.1954 | -0.0702 | -0.0761 |
| climate_crashes | 0.284 | 0.3185 | -0.1082 | 0.0825 | 0.1442 |
| vehicle | 0.2277 | 0.2464 | -0.0759 | -0.0609 | 0.0287 |
| parkinsons | 10.6617 | 11.4139 | -0.0659 | 0.0066 | -0.0055 |
| concrete_slump | 3.637 | 3.8662 | -0.0593 | -0.0688 | -0.0164 |
| qsar_biodeg | 0.1643 | 0.172 | -0.0445 | -0.0055 | -0.0202 |
| german_credit | 0.3321 | 0.3452 | -0.0379 | 0.0089 | 0.0531 |
| communities | 0.1365 | 0.1376 | -0.0077 | -0.0066 | -0.0135 |
| wine_red | 0.6461 | 0.6423 | 0.006 | -0.0087 | -0.0088 |
| air_quality | 0.4651 | 0.4611 | 0.0087 | 0.0029 | -0.0041 |
| adult | 0.2147 | 0.2112 | 0.0165 | 0.0059 | -0.0106 |
| abalone | 2.1905 | 2.1534 | 0.0169 | -0.0113 | -0.0102 |
| spectf | 0.3719 | 0.3632 | 0.0233 | -0.0579 | -0.0652 |
| student_math | 4.1252 | 4.0242 | 0.0245 | 0.000894 | -0.0241 |
| real_estate | 7.6763 | 7.4749 | 0.0262 | -0.0105 | -0.01 |
| auto_mpg | 2.9905 | 2.9039 | 0.0289 | 0.0134 | -0.0524 |
| credit_default | 0.3519 | 0.3404 | 0.0328 | 0.0016 | -6.16e-05 |
| bank_marketing | 0.4129 | 0.3874 | 0.0618 | 0.0127 | 0.01 |
| page_blocks | 0.1998 | 0.1829 | 0.0849 | -0.0394 | 0.0778 |
| sonar | 0.1953 | 0.1779 | 0.0892 | -0.0999 | -0.1235 |
| steel_plates | 0.2277 | 0.2059 | 0.0956 | -0.0394 | -0.0829 |
| servo | 0.8537 | 0.766 | 0.1027 | 0.0207 | 0.1263 |
| spambase | 0.0574 | 0.0499 | 0.13 | 0.0365 | -0.0435 |
| automobile | 3692.2632 | 3115.4582 | 0.1562 | -0.0895 | -0.0536 |
| california | 0.5574 | 0.4511 | 0.1908 | -0.0066 | 0.000445 |
| ccpp | 3.9781 | 3.1591 | 0.2059 | -0.0301 | -0.0307 |
| superconductivity | 12.8077 | 10.0095 | 0.2185 | 0.0094 | -0.0046 |
| phishing | 0.0646 | 0.05 | 0.2251 | -0.012 | -0.0138 |
| bike_sharing | 100.8109 | 47.7203 | 0.5266 | -0.023 | -0.1265 |
| energy | 1.0617 | 0.4154 | 0.6088 | 0.0119 | 0.1884 |
| tictactoe | 0.0248 | 0.0083 | 0.6655 | -0.4158 | -0.5463 |

Sweep datasets: the measure by λ, and on the dataset as run (without u1, u2).

| base_dataset | 0.0 | 0.25 | 0.5 | 1.0 | as run |
|---|---|---|---|---|---|
| abalone | 0.0129 | 0.0494 | 0.1585 | 0.3689 | 0.0169 |
| air_quality | 0.0006 | 0.1739 | 0.388 | 0.5918 | 0.0087 |
| auto_mpg | 0.0306 | 0.0888 | 0.2577 | 0.3898 | 0.0289 |
| automobile | 0.0867 | 0.0562 | 0.101 | 0.1624 | 0.1562 |
| ccpp | 0.157 | 0.3955 | 0.5802 | 0.7089 | 0.2059 |
| communities | -0.008 | 0.0113 | 0.0879 | 0.2734 | -0.0077 |
| concrete_slump | -0.0599 | 0 | 0.0886 | 0.0909 | -0.0593 |
| energy | 0.4009 | 0.5207 | 0.5897 | 0.6387 | 0.6088 |
| parkinsons | -0.0624 | -0.0566 | -0.0714 | 0.1327 | -0.0659 |
| real_estate | -0.0015 | 0.0267 | 0.1099 | 0.3203 | 0.0262 |
| servo | -0.0198 | 0.002 | 0.1104 | 0.2336 | 0.1027 |
| student_math | 0.034 | 0.0316 | 0.1029 | 0.2502 | 0.0245 |
| wine_red | 0.0083 | 0.0103 | 0.075 | 0.2676 | 0.006 |

## 09.11: where do the trees split? (seed 0, fold 0, layer 1)

96 of 96 recounted runs reproduce the saved test predictions bit for bit (1.02 CPU-hours). Median over the 32 datasets of the added columns' share of the columns, of the splits and of the samples reaching those splits, by node depth:

| method | depth | column_share | split_share | sample_share |
|---|---|---|---|---|
| residual_xx | all | 0.5 | 0.485 | 0.46 |
| shuffled_xx | all | 0.5 | 0.447 | 0.289 |
| residual_xx | root | 0.5 | 0.526 | 0.527 |
| shuffled_xx | root | 0.5 | 0.046 | 0.046 |
| residual_xx | 1-2 | 0.5 | 0.521 | 0.492 |
| shuffled_xx | 1-2 | 0.5 | 0.158 | 0.107 |
| residual_xx | 3-5 | 0.5 | 0.482 | 0.491 |
| shuffled_xx | 3-5 | 0.5 | 0.368 | 0.235 |
| residual_xx | 6-10 | 0.5 | 0.486 | 0.472 |
| shuffled_xx | 6-10 | 0.5 | 0.45 | 0.371 |
| residual_xx | 11+ | 0.5 | 0.481 | 0.464 |
| shuffled_xx | 11+ | 0.5 | 0.492 | 0.449 |

Expected if trees fit noise on the extra columns: shuffled products take a share of the splits near their share of the columns, mostly deep, and across datasets a larger share goes with a larger cost (ρ < 0). Spearman ρ of the shuffled split share with shuffled vs base (seed 0) = -0.063 (p = 0.730).
