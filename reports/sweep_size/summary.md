# Report: sweep_size

480 runs on 24 datasets. Error = 1 - balanced accuracy (classification) or RMSE (regression); relative reduction = (e_ref - e) / max(e_ref, e) of errors averaged over a dataset's runs; positive favours the method.

## Hypotheses (plan §5)

Not tested: some runs of the compared methods are unfinished.

## Depth rule of the base cascade (descriptive)
*picked*: share of base runs whose chosen layer is this depth. *median_test_vs_oof*: median over runs of (OOF error - test error) / max of the two, with the OOF error from the depth score (1 - balanced accuracy, or √MSE); positive = the test error is lower than the OOF error the rule sees. *median_reduction* to *p*: base cut at this depth vs base at its chosen layer, over datasets; positive = the fixed depth has the lower error.

| depth | picked | picked_classification | picked_regression | median_test_vs_oof | median_reduction | wins | losses | zeros | p |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 0.6625 | - | 0.6625 | 0.018 | -4.45e-05 | 6 | 12 | 6 | 0.0582 |
| 2 | 0.2708 | - | 0.2708 | 0.0566 | 0.006 | 21 | 3 | 0 | 5.13e-06 |
| 3 | 0.0167 | - | 0.0167 | 0.0712 | 0.0071 | 17 | 7 | 0 | 0.0018 |

## Common depth (descriptive)
Median relative reduction vs base at each depth reached by every cascade variant in a run; *runs* counts those runs, so deep rows rest on few.

| depth | residual_xx | datasets | runs |
|---|---|---|---|
| 1 | 0.036 | 24 | 120 |
| 2 | 0.0526 | 24 | 120 |
| 3 | 0.0632 | 24 | 120 |
| 4 | 0.1637 | 14 | 48 |
| 5 | 0.0631 | 4 | 5 |
| 6 | 0.04 | 3 | 4 |

## Per dataset: rmse mean ± sd (regression)
| dataset | base | residual_xx |
|---|---|---|
| semi_abalone_l000 | 2.298 ± 0.094 | 2.326 ± 0.1 |
| semi_abalone_l025 | 2.412 ± 0.12 | 2.405 ± 0.13 |
| semi_abalone_l050 | 2.749 ± 0.13 | 2.54 ± 0.15 |
| semi_abalone_l100 | 3.616 ± 0.34 | 2.775 ± 0.24 |
| semi_air_quality_l000 | 0.4985 ± 0.025 | 0.5025 ± 0.03 |
| semi_air_quality_l025 | 0.6047 ± 0.033 | 0.5733 ± 0.05 |
| semi_air_quality_l050 | 0.8476 ± 0.057 | 0.6719 ± 0.093 |
| semi_air_quality_l100 | 1.328 ± 0.15 | 0.8187 ± 0.14 |
| semi_ccpp_l000 | 4.505 ± 0.31 | 4.45 ± 0.31 |
| semi_ccpp_l025 | 5.84 ± 0.45 | 5.03 ± 0.41 |
| semi_ccpp_l050 | 8.104 ± 1.1 | 5.837 ± 0.95 |
| semi_ccpp_l100 | 12.17 ± 3.1 | 7.307 ± 1.5 |
| semi_communities_l000 | 0.1412 ± 0.0041 | 0.143 ± 0.0051 |
| semi_communities_l025 | 0.1516 ± 0.0068 | 0.1505 ± 0.0077 |
| semi_communities_l050 | 0.1821 ± 0.012 | 0.1738 ± 0.013 |
| semi_communities_l100 | 0.2692 ± 0.025 | 0.2251 ± 0.033 |
| semi_parkinsons_l000 | 10.96 ± 1.8 | 11.11 ± 1.5 |
| semi_parkinsons_l025 | 11.49 ± 1.9 | 11.36 ± 1.7 |
| semi_parkinsons_l050 | 12.1 ± 1.9 | 11.63 ± 1.7 |
| semi_parkinsons_l100 | 15.32 ± 1.8 | 13.07 ± 1.9 |
| semi_wine_red_l000 | 0.6496 ± 0.036 | 0.6577 ± 0.04 |
| semi_wine_red_l025 | 0.6826 ± 0.028 | 0.6796 ± 0.032 |
| semi_wine_red_l050 | 0.7667 ± 0.036 | 0.7226 ± 0.044 |
| semi_wine_red_l100 | 0.956 ± 0.092 | 0.7531 ± 0.067 |

## Per dataset: mae mean ± sd (regression)
| dataset | base | residual_xx |
|---|---|---|
| semi_abalone_l000 | 1.644 ± 0.071 | 1.656 ± 0.07 |
| semi_abalone_l025 | 1.737 ± 0.075 | 1.735 ± 0.08 |
| semi_abalone_l050 | 2.015 ± 0.099 | 1.84 ± 0.13 |
| semi_abalone_l100 | 2.573 ± 0.25 | 1.943 ± 0.15 |
| semi_air_quality_l000 | 0.3279 ± 0.014 | 0.3372 ± 0.021 |
| semi_air_quality_l025 | 0.4252 ± 0.02 | 0.3991 ± 0.04 |
| semi_air_quality_l050 | 0.5872 ± 0.039 | 0.443 ± 0.068 |
| semi_air_quality_l100 | 0.8799 ± 0.11 | 0.5047 ± 0.089 |
| semi_ccpp_l000 | 3.49 ± 0.25 | 3.464 ± 0.26 |
| semi_ccpp_l025 | 4.416 ± 0.39 | 3.824 ± 0.33 |
| semi_ccpp_l050 | 5.762 ± 0.83 | 4.22 ± 0.63 |
| semi_ccpp_l100 | 7.97 ± 2.1 | 4.765 ± 0.8 |
| semi_communities_l000 | 0.0988 ± 0.0058 | 0.1001 ± 0.0059 |
| semi_communities_l025 | 0.1093 ± 0.0065 | 0.108 ± 0.0075 |
| semi_communities_l050 | 0.1323 ± 0.009 | 0.1244 ± 0.011 |
| semi_communities_l100 | 0.1905 ± 0.016 | 0.1539 ± 0.024 |
| semi_parkinsons_l000 | 9.227 ± 2 | 9.299 ± 1.8 |
| semi_parkinsons_l025 | 9.544 ± 2 | 9.429 ± 1.9 |
| semi_parkinsons_l050 | 9.89 ± 1.8 | 9.548 ± 1.8 |
| semi_parkinsons_l100 | 11.98 ± 1.8 | 10.48 ± 1.8 |
| semi_wine_red_l000 | 0.5154 ± 0.028 | 0.5246 ± 0.032 |
| semi_wine_red_l025 | 0.5365 ± 0.019 | 0.5368 ± 0.024 |
| semi_wine_red_l050 | 0.5961 ± 0.02 | 0.5673 ± 0.031 |
| semi_wine_red_l100 | 0.715 ± 0.059 | 0.571 ± 0.047 |

## Per dataset: r2 mean ± sd (regression)
| dataset | base | residual_xx |
|---|---|---|
| semi_abalone_l000 | 0.491 ± 0.032 | 0.4783 ± 0.036 |
| semi_abalone_l025 | 0.4625 ± 0.034 | 0.4651 ± 0.044 |
| semi_abalone_l050 | 0.3984 ± 0.039 | 0.4857 ± 0.05 |
| semi_abalone_l100 | 0.3405 ± 0.11 | 0.6112 ± 0.061 |
| semi_air_quality_l000 | 0.877 ± 0.019 | 0.875 ± 0.02 |
| semi_air_quality_l025 | 0.8294 ± 0.024 | 0.8455 ± 0.033 |
| semi_air_quality_l050 | 0.715 ± 0.037 | 0.8185 ± 0.049 |
| semi_air_quality_l100 | 0.5576 ± 0.098 | 0.8294 ± 0.058 |
| semi_ccpp_l000 | 0.93 ± 0.01 | 0.9317 ± 0.0097 |
| semi_ccpp_l025 | 0.89 ± 0.016 | 0.9184 ± 0.013 |
| semi_ccpp_l050 | 0.8183 ± 0.048 | 0.9051 ± 0.031 |
| semi_ccpp_l100 | 0.7324 ± 0.13 | 0.9051 ± 0.039 |
| semi_communities_l000 | 0.6311 ± 0.027 | 0.6216 ± 0.03 |
| semi_communities_l025 | 0.5932 ± 0.019 | 0.5988 ± 0.026 |
| semi_communities_l050 | 0.4925 ± 0.034 | 0.5367 ± 0.055 |
| semi_communities_l100 | 0.2961 ± 0.04 | 0.5029 ± 0.11 |
| semi_parkinsons_l000 | -0.1989 ± 0.21 | -0.2562 ± 0.29 |
| semi_parkinsons_l025 | -0.221 ± 0.2 | -0.2059 ± 0.25 |
| semi_parkinsons_l050 | -0.1073 ± 0.11 | -0.02785 ± 0.13 |
| semi_parkinsons_l100 | -0.06314 ± 0.089 | 0.2291 ± 0.086 |
| semi_wine_red_l000 | 0.3475 ± 0.061 | 0.3308 ± 0.07 |
| semi_wine_red_l025 | 0.3153 ± 0.049 | 0.321 ± 0.06 |
| semi_wine_red_l050 | 0.2599 ± 0.061 | 0.3413 ± 0.079 |
| semi_wine_red_l100 | 0.2728 ± 0.13 | 0.5475 ± 0.083 |

## Per dataset: cpu_seconds mean ± sd (regression)
| dataset | base | residual_xx |
|---|---|---|
| semi_abalone_l000 | 3.323 ± 0.92 | 3.555 ± 1 |
| semi_abalone_l025 | 3.547 ± 0.92 | 4.478 ± 1.6 |
| semi_abalone_l050 | 3.464 ± 1 | 4.401 ± 1.7 |
| semi_abalone_l100 | 4.394 ± 1.8 | 5.046 ± 1.7 |
| semi_air_quality_l000 | 3.539 ± 0.91 | 3.808 ± 1.2 |
| semi_air_quality_l025 | 3.574 ± 1 | 4.945 ± 2.2 |
| semi_air_quality_l050 | 4.151 ± 1.6 | 5.056 ± 1.9 |
| semi_air_quality_l100 | 4.462 ± 1.9 | 5.515 ± 2 |
| semi_ccpp_l000 | 3.75 ± 0.83 | 3.806 ± 0.96 |
| semi_ccpp_l025 | 4.037 ± 1.3 | 4.386 ± 1.1 |
| semi_ccpp_l050 | 4.409 ± 1.8 | 4.776 ± 1.6 |
| semi_ccpp_l100 | 4.996 ± 1.7 | 4.96 ± 1.4 |
| semi_communities_l000 | 5.296 ± 2.2 | 7.038 ± 3.5 |
| semi_communities_l025 | 5.366 ± 2.4 | 9.526 ± 5.3 |
| semi_communities_l050 | 5.548 ± 2.3 | 9.586 ± 6.4 |
| semi_communities_l100 | 5.788 ± 2.4 | 11.26 ± 7.3 |
| semi_parkinsons_l000 | 5.68 ± 1.6 | 6.584 ± 3.7 |
| semi_parkinsons_l025 | 5.642 ± 1.9 | 7.407 ± 4 |
| semi_parkinsons_l050 | 6.284 ± 2.7 | 5.814 ± 2.8 |
| semi_parkinsons_l100 | 4.889 ± 0.94 | 4.561 ± 1.6 |
| semi_wine_red_l000 | 3.214 ± 0.87 | 3.484 ± 1.1 |
| semi_wine_red_l025 | 3.426 ± 1.1 | 3.891 ± 1.4 |
| semi_wine_red_l050 | 3.461 ± 1.1 | 4.174 ± 1.6 |
| semi_wine_red_l100 | 4.388 ± 1.9 | 4.61 ± 1.3 |
