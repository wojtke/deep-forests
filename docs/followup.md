# Follow-up runs of 12–13.11.2026

**Exploratory.** Chosen after the main results, one seed (0) except the synthetic data; decides no hypothesis.
Each experiment file states its question, bars and predictions, written before the run (one exception,
`sampling_large_sum`, says so in its header). Drafted by Claude Code (Fable 5.2).

- **Numbers:** `uv run python scripts/followup_report.py` writes [reports/followup/summary.txt](../reports/followup/summary.txt)
  from the committed `results/<experiment>/runs.csv` and `layers.csv`.
- **Runs:** 6,789 tasks, 0 failed, on one laptop (10 processes). The commit of each run is in
  `results/<experiment>/manifest.json`:

  | Experiments | Tasks | Commit |
  |---|---|---|
  | `content`, `leaf`, `mixed`, `size`, `draws`, `synth`, `sweep_size`, `large`, `large64` | 6,129 | `aa28a38` |
  | `large_content` | 162 | `b5203e3` |
  | `sampling`, `sampling_large` | 480 | `5356091` |
  | `sampling_large_sum` | 18 | `99f44d7` |

  Later commits changed the compute files (the `max_features` setting, then comments and import order), so at
  the current commit `dfx run` counts these runs as out of date. To resume or check one, check out its commit.
  Defaults were unchanged throughout: sampled tasks reproduce the saved predictions bit for bit after each change.
- **Checks:** four independent reviews by Claude subagents (code and numbers, mechanism, two skeptical reviews
  of the conclusions). No bug found; the key numbers were recomputed independently; three readings were
  corrected and are given below in their corrected form.
- "Reduction" is the main report's relative error reduction; positive favours the first-named method.

## Bars

| Bar | Question | Prediction | Outcome |
|---|---|---|---|
| identity | New code equals the main runs of seed 0 | yes | **yes**, 640 of 640 runs bit for bit |
| C0 | Noise columns are worse than base | yes | **yes**: median −4.1%, 28 of 32 worse |
| C1 | Products beat noise columns | yes | **yes**: +3.5%, 26 of 32 |
| C2 | Products beat a sum or a copy in their place | no | **no**: vs sum −0.1% (14/18), vs copy +0.3% (17/15) |
| L1 | Noise penalty shrinks at leaf 5 | yes / open | chosen layer **no** (18 of 32); layer 1 **yes** (21 of 32) |
| L2 | At leaf 5 or 20 products clearly beat base | no | **no**; base itself gets worse (−3.8% at leaf 5, −7.4% at leaf 20) |
| M1 | Products for half the forests beat products for all | yes | **yes**: +0.8%, 25 of 32 |
| M2 | Half beats base | no | **no**: +0.2%, 17 of 32 |
| S1 | Noise penalty shrinks from 250 rows to full size | no at layer 1, yes at chosen | **no** at both (5 and 3 of 10) |
| S2 | Net effect of products grows with rows | open | not met (7 of 10; median −0.9% → +0.2%) |
| S3 | Products' advantage over noise falls with rows | open | **no** (it rises on 7 of 10) |
| V1 | Added columns raise the variance part | no / open | products: met (9 of 11) but **not robust** (see below); noise: **no** (2 of 11) |
| Z1 | Noise penalty shrinks from 1,000 rows to the largest size | yes | **no** (2 of 6) |
| Z2 | Products beat base at the largest size on 5 of 6 | no | formally 5 of 6; **honestly 3 of 6** (casp +0.06%, HIGGS +1.2% from one fold) |
| Z3 | Products gain more on HIGGS without engineered features | yes, small | **yes** at every size; the gap closes with rows |
| LC1 | On the large datasets the product beats sum and copy | sgemm, higgs_low yes | **only higgs_low** (all 3 folds); sgemm and covertype no |
| sweep | Planted product: strength needed at 250 / 1,000 rows | 20% / 6% | **as predicted** |

## What we learned

1. **A product column is worth no more than any other real column.** On the benchmark a sum x_i + x_j or a copy
   of x_i in place of the product does as well. "Real vs noise" therefore says nothing about interactions; the
   interaction-specific contrast is product vs sum or copy, and it is null.
2. **The cost of extra columns is smoothing, not overfitting.** Noise columns lower the variance (9 of 11
   datasets, median −23%) and raise bias (10 of 11, +6%; +12% at layer 1). A split on a noise column halves a
   node without narrowing it in the real features, so the trees behave as if they had larger leaves: across
   the 32 datasets the layer-1 noise penalty tracks the base cascade's own loss from minimum leaf 5 (Spearman
   0.95). In a direct check on three datasets the penalty rises steadily with the number of noise columns.
3. **The instructor's overfitting remark: a narrow yes, a practical no.** Real products raise the variance at
   layer 1 on 11 of 11 datasets, but variance is 5–10% of the squared error, the rise adds about 1%, and it is
   gone by layer 3 (1 of 11).
4. **More rows do not remove the cost.** Within 10 benchmark datasets (250 rows to full) and 6 large ones
   (1,000 to 64,000) the noise penalty does not shrink. Larger leaves shrink the cost and the accuracy
   together.
5. **Products for half the forests** only dilute the cost; they equal the base cascade.
6. **Synthetic data.** With an exact planted product the chosen products gain 31% (the true term: 40%). With an
   interaction that correlation cannot see they lose 10%, the same as random products, while the true term
   gains 32% (27% with 10 noise columns added). So a useful column survives noise columns; whether a better
   selector would find one on real data is open. The noise penalty depends on the target: −6% additive, −33%
   pure product.
7. **Six larger datasets** (self-chosen, one seed, 3 test folds). Products beat base on sgemm (+14 to +26%),
   covertype (+3 to +6%) and HIGGS without its engineered features (+1.4 to +3.9%, shrinking with rows); about
   zero on casp and HIGGS; worse on miniboone (−4.6% at 64,000). But on sgemm a plain copy gains as much as the
   product, and on covertype a sum does: these gains are not about interactions. A reviewer's single-forest
   check suggests they come from the forests' square-root feature sampling (sgemm) and from products of one-hot
   columns acting as merged categories (covertype). Only HIGGS without engineered features shows a
   product-specific gain: the dataset built to favour products.
8. **The old shuffled control understated the penalty a little** (repaired control 0.5% worse, 24 of 32).

## Caveats

- One seed everywhere except the synthetic data; the six large datasets were chosen by us after the fact.
- The four draws of the bias–variance study are disjoint in rows, not in groups (matters for parkinsons), and
  share model seeds. "Bias" includes irreducible noise.
- In the size study d and K change with rows on adult. ccpp has K = 1.
- The sweep's full-size row comes from the earlier `explore_sweep` run (older code).
- The feature-sampling explanation for sgemm and covertype comes from single forests outside the cascade; it
  is not yet tested in the cascade.

## Feature-sampling control (run 13.11, 09:53–13:35; 480 tasks, 0 failed; commit `5356091`)

Every cascade forest tries all columns at each split (`max_features = 1.0`) instead of sqrt(m). Experiments
`sampling` (10 benchmark datasets, 4,000 rows) and `sampling_large` (six large datasets, 4,000 and 16,000
rows, folds 0–2). Checked by a fourth reviewer: code and numbers confirmed, one reading corrected (below).

| Bar | Question | Prediction | Outcome |
|---|---|---|---|
| F1 | All columns improves base on sgemm and covertype | yes | **yes**: +22.6% and +6.8% at 16,000 rows |
| F2 | With all columns the sgemm and covertype gains fall below half | yes | **sgemm yes** (copy +10.8% → −4.6%; products +9.4% → +4.4%); **covertype no** at the chosen layer (+4.2% → +4.8%, but no product gain in 2 of 3 folds: +0.3, 0.0, +12.7), yes at layer 1 (+8.9% → +2.3%) |
| F3 | On higgs_low products still beat base and copy in all 3 folds | yes | **yes** (+1.8%) |
| F4 | Layer-1 noise penalty is smaller with all columns on 5 of 6 large datasets | yes | **yes**, 6 of 6; still −21% on covertype and −22% on sgemm |
| F5 | The same on the 10 benchmark datasets | yes | **yes**: layer 1 on 10 of 10 (median −6.6% → −2.5%), chosen layer 8 of 10 (−3.0% → −2.6%) |
| F6 | With all columns products are still no clear win on the benchmark | no clear win | **as predicted**: residual-XX better on 4 of 10, median −0.5% |
| F7 | All columns is a better base on the benchmark | no | **as predicted**: 5 of 10, median −0.4% |

Reading (corrected after review):

- sqrt(m) sampling explains most of the copy and product gains on sgemm and part of the noise penalty.
- **No product-specific gain on sgemm.** With all columns the products gain +4.4% (all 3 folds), but the
  reviewer's diagnostic with sums of the same pairs gives +6.0% (errors 0.0930, 0.0919, 0.0946 against base
  0.0986, 0.0997, 0.0991). My first reading ("a product-specific gain remains on sgemm") was wrong.
- **The copy is not a valid control with all columns.** A duplicated column changes nothing for the best-split
  forests; the −4.6% comes entirely from the random-threshold forests.
- **higgs_low holds but is thin:** products +1.8% (folds +0.6, +4.1, +0.6), above sums and copies in all 3.
- **Covertype:** no product gain with all columns; fold 2's base error is an outlier.
- **Noise penalty at layer 1:** ratio all/sqrt 0.44–0.55 on four large datasets, 0.70 on covertype and sgemm.
  At the chosen layer it is smaller on only 3 of 6 (sgemm −12.8% → −13.6%). Even with all columns the
  best-split forests on sgemm lose 27% to noise columns, so the "blurring" mechanism stands.
- Trying all columns is a no-sampling control, not a tuned model: the two RFs of a layer then differ only by
  their bootstrap. Note that an integer `max_features = 1` in a TOML file would mean one column per split.
- **Official sum control** (`sampling_large_sum`, 18 tasks, 0 failed, commit `99f44d7`; not blind) confirms
  the diagnostic. With all columns at 16,000 rows, sums vs base / products vs base: sgemm +6.0% / +4.4%
  (products below sums in 2 of 3 folds), higgs_low −0.2% / +1.8% (products above sums in 3 of 3),
  covertype +2.3% / +4.8% (products above sums in 3 of 3, but neither beats base in folds 0 and 1),
  higgs +0.6% / −0.3%, casp +0.1% / −1.2%, miniboone −3.4% / −6.7%.

## Open

- A share of columns between sqrt(m) and all is untested.
- Noise columns at K/2 and 2K on the benchmark (dose).
- Seeds 1 and 2 on the large datasets.
- A selector that looks for interactions directly, with small K.
