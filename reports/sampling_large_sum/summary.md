# Report: sampling_large_sum (INCOMPLETE: 12 tasks missing; only runs finished by every method are used)

18 runs on 6 datasets. Error = 1 - balanced accuracy (classification) or RMSE (regression); relative reduction = (e_ref - e) / max(e_ref, e) of errors averaged over a dataset's runs; positive favours the method.

## Hypotheses (plan §5)

Not tested: some runs of the compared methods are unfinished.

## Per dataset: balanced_accuracy mean ± sd (classification)
| dataset | target_sum_xx |
|---|---|
| covertype | 0.7489 ± 0.007 |
| higgs | 0.7097 ± 0.0049 |
| higgs_low | 0.6225 ± 0.0046 |
| miniboone | 0.9214 ± 0.0025 |

## Per dataset: log_loss mean ± sd (classification)
| dataset | target_sum_xx |
|---|---|
| covertype | 0.3926 ± 0.0094 |
| higgs | 0.5611 ± 0.0014 |
| higgs_low | 0.6436 ± 0.0028 |
| miniboone | 0.1683 ± 0.0045 |

## Per dataset: macro_f1 mean ± sd (classification)
| dataset | target_sum_xx |
|---|---|
| covertype | 0.7773 ± 0.0075 |
| higgs | 0.7097 ± 0.0048 |
| higgs_low | 0.6222 ± 0.0043 |
| miniboone | 0.9212 ± 0.0026 |

## Per dataset: accuracy mean ± sd (classification)
| dataset | target_sum_xx |
|---|---|
| covertype | 0.8497 ± 0.0046 |
| higgs | 0.7106 ± 0.0047 |
| higgs_low | 0.6265 ± 0.0051 |
| miniboone | 0.9362 ± 0.0022 |

## Per dataset: roc_auc mean ± sd (classification)
| dataset | target_sum_xx |
|---|---|
| covertype | 0.9775 ± 0.00071 |
| higgs | 0.7847 ± 0.0025 |
| higgs_low | 0.6764 ± 0.0078 |
| miniboone | 0.9795 ± 0.00076 |

## Per dataset: average_precision mean ± sd (classification)
| dataset | target_sum_xx |
|---|---|
| covertype | 0.8412 ± 0.0053 |
| higgs | 0.7793 ± 0.0024 |
| higgs_low | 0.6655 ± 0.0075 |
| miniboone | 0.9682 ± 0.0021 |

## Per dataset: cpu_seconds mean ± sd (classification)
| dataset | target_sum_xx |
|---|---|
| covertype | 860.8 ± 26 |
| higgs | 807.8 ± 3.5 |
| higgs_low | 624.8 ± 12 |
| miniboone | 1665 ± 49 |

## Per dataset: rmse mean ± sd (regression)
| dataset | target_sum_xx |
|---|---|
| casp | 3.836 ± 0.089 |
| sgemm | 0.09316 ± 0.0014 |

## Per dataset: mae mean ± sd (regression)
| dataset | target_sum_xx |
|---|---|
| casp | 2.717 ± 0.15 |
| sgemm | 0.06394 ± 0.00065 |

## Per dataset: r2 mean ± sd (regression)
| dataset | target_sum_xx |
|---|---|
| casp | 0.6091 ± 0.017 |
| sgemm | 0.9932 ± 0.00019 |

## Per dataset: cpu_seconds mean ± sd (regression)
| dataset | target_sum_xx |
|---|---|
| casp | 416.4 ± 70 |
| sgemm | 333 ± 1.2 |
