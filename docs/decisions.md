# Settings and their sources

Every setting the code uses, where it comes from, and whether a sensitivity check varies it.
**Source** is the research plan ([plan.pdf](plan.pdf)), the DF21 package source (deep-forest
0.1.7, [github.com/LAMDA-NJU/Deep-Forest](https://github.com/LAMDA-NJU/Deep-Forest) at tag v0.1.7,
paths relative to `deepforest/`), a library default, or **ours** (our choice, not sourced).
DF21 line numbers were read from the v0.1.7 source on 22.10.2026.

## Cascade (`src/dfx/cascade.py`, `forest.py`, `prep.py`)

| Setting | Value | Source | Sensitivity check |
|---|---|---|---|
| Forests per layer | 2 RF + 2 ERF (`n_forests` = 2 per type) | DF21 `cascade.py` L1337–1360 (`n_estimators=2`), doubled in `_layer.py` L74 | 4 + 4 (Zhou & Feng 2019) |
| Trees per forest | 100, fully grown, min_samples_leaf 1 | DF21 | 500 (Zhou & Feng 2019) |
| Features per split | √m, in classification and regression | DF21 `tree/tree.py` L245–247 | – |
| ERF | random thresholds (ExtraTrees style) | DF21 `forest.py` | – |
| Bootstrap | both forest types; each tree fit on the distinct drawn rows, unweighted | DF21 `forest.py` L117–129 | – |
| Split criterion | gini / squared error | DF21 | – |
| Layer outputs passed on | every forest's output, concatenated (RF first); binary keeps both columns | DF21 `_layer.py` L201–254 | – |
| Layer predictions for training rows | 3-fold out-of-fold, same folds at every layer | plan (Zhou & Feng 2019); DF21 uses out-of-bag | 5 folds |
| Test-row inputs | P = mean of the fold models' predictions; each added column = mean of its values from each fold model | plan §3 | – |
| Binning | 255 percentile bins, midpoint thresholds, repeated thresholds kept (tied columns skip bin numbers), exact for ≤255 distinct values; checked bin for bin against DF21's `Binner` | DF21 `_binner.py` L23–86 | no binning |
| Binner scope | X once on all outer-training rows; P and added columns per fold model on its training rows | ours, adapted from DF21 (X once; new columns per layer) | – |
| Depth rule | a layer improves if it beats the best so far by 1e-5; stop after 2 layers without improvement; at most 20 layers, the first included | DF21 `cascade.py` L718–747, L930–962 | – |
| Depth score | balanced accuracy / mean squared error | plan (DF21: accuracy / MSE) | – |
| Output | mean of the 4 forests × 3 fold models of the best layer | plan; DF21 keeps the last layer if the 20-layer cap is hit right after a non-improving layer | – |
| Seeds | inside a task: `SeedSequence([seed, crc32(dataset), outer fold, layer, inner fold, stream, index])` (`cascade.seed_for`), independent of the method; outer splits: seeds 0, 1, 2 (`experiments/main.toml`); 20,000-row subsample: seed 0 (`data.SUBSAMPLE_SEED`) | ours | – |

## Added columns (`src/dfx/features.py`)

| Setting | Value | Source | Sensitivity check |
|---|---|---|---|
| Products K | min(d, ⌊d(d−1)/8⌋), d = encoded features of the outer fold | plan (our rule) | ⌈K/2⌉, 2K |
| Candidates | XX: x_i x_j, i < j; XP: x_i p_{t,c} with p_t the mean of the type's two forests | plan | – |
| Excluded candidates | constant on the fold model's training rows (variance ≤ 1e-12); this removes products of two dummies of one categorical, which are always 0 | plan; threshold ours | – |
| Fewer candidates than K | all are taken | ours | – |
| Target / residual score | max over classes of \|corr\| with y_c or y_c − p̄_c; p̄ = mean of all forests' OOF outputs, original scale | plan | – |
| Undefined correlation, ties | 0; ties broken by candidate order (stable sort) | ours | – |
| Random-XX | redrawn for every layer and fold model | plan | – |
| XP ranking | mutual information, 3 neighbours, `discrete_features="auto"` | plan; scikit-learn defaults | – |
| XP in regression | p_t standardized with the fold model's training rows | plan; scaling rows ours | – |
| Non-linear columns | entropy of p_t and Σ\|p_RF − p_ERF\|; regression: std of the type's tree predictions (pooled, ddof 0) and \|mean_RF − mean_ERF\| | plan eq. 3; ddof numpy default | – |
| Monotone activation | sigmoid of every P column; regression scaled to [0, 1] with the training rows' min/max, not clipped | plan; scaling rows ours | ReLU, GELU without binning |

## Data and validation (`src/dfx/data.py`, `datasets.py`)

| Setting | Value | Source |
|---|---|---|
| Preprocessing | median / mode imputation; one-hot encoding; numeric standardization, all fitted on outer-training rows | plan §4 |
| Preprocessing scope | once per outer training set, reused by the inner folds of every method | ours (no labels involved) |
| Constant columns | dropped | ours |
| Row cap | at most 20,000 rows: whole groups, class-stratified (19,999 for the classification sets) | plan; procedure ours |
| Rows without any feature value | dropped (330 Air Quality rows with every sensor missing) | ours |
| Related rows | identical inputs, plus the dataset's group key: patient (Parkinsons), recording (Cardiotocography), material (Superconductivity), day (Air Quality, Bike Sharing); rows with a missing key are not joined by it | plan §5 |
| Outer validation | 5 folds × 3 seeds; StratifiedGroupKFold / GroupKFold with shuffling | plan; seeds ours |
| Excluded columns | ids, timestamps, sampling weights, columns revealing the target; per dataset in `datasets.py` and docs/data-audit.md | plan §4; plan-silent cases (other targets, time columns, coding) marked PROPOSED in the audit, kept as run (decided 25.10.2026) |

## Baselines (`src/dfx/baselines.py`)

| Setting | Value | Source |
|---|---|---|
| RF | 400 trees, same forest code and binning as a cascade layer | plan (400 = trees of one layer); binning ours |
| RF + target-XX | K target-chosen XX products on outer-training rows | plan |
| LightGBM search | 10 random settings: learning rate 0.01–0.3 and L2 0.1–10 log-uniform, max depth 3–8, row and column subsampling 0.6–1 uniform | plan ranges; distributions ours |
| LightGBM training | ≤ 1,000 trees, early stopping on LightGBM's default metric (log-loss / L2), patience 50, `subsample_freq=1`, `num_leaves` 31 | plan; default metric (ours, 22.10.2026); patience **ours, not sourced**; num_leaves LightGBM default |
| LightGBM choice and refit | best mean inner-fold primary metric on the cascade's 3 inner folds; refit on all outer-training rows with the rounded mean best iteration | plan; refit rule ours |

## Analysis (`src/dfx/report.py`)

| Setting | Value | Source |
|---|---|---|
| Error | 1 − balanced accuracy, or RMSE, averaged over a dataset's 15 runs; the means are rounded to 12 significant digits before comparing, so the same errors summed in another order tie (before 25.10.2026 one such tie, XP-MI vs base on German Credit, counted as a win) | plan §5; rounding ours |
| Relative reduction | (ē_ref − ē) / max(ē_ref, ē), 0 if both are 0 | plan §5 |
| Tests | two-sided Wilcoxon signed-rank over the 32 datasets; Holm over H1, H2a, H2b, H3, H4, H5; supported iff adjusted p < 0.05 and median > 0; H2 needs H2a and H2b | plan §5 |
| Zero differences | scipy default (`zero_method="wilcox"` drops them; with zeros present scipy uses the normal approximation); their number is reported; all zero → not supported. The median in the decision rule and the HL interval keep them | scipy default; ours |
| Descriptive | overall and by task: the other methods vs base (incl. combined), mean ranks, Friedman + Nemenyi CD diagram; the six comparisons on every other metric, by task; common depth; XP–P correlation; per-dataset mean ± sd of every metric and CPU time | plan §5; Nemenyi from Demšar (2006); other metrics: instructor's feedback |
| Post-hoc metrics | accuracy; ROC AUC and average precision (mAP), one-vs-rest and macro over the classes present in the test fold (so both classes of a binary task); R². Computed by `report.py` from the saved float32 test predictions of every layer, not in `metrics.py`, whose edit would re-run everything | instructor's feedback on the plan (23.10.2026); scikit-learn; averaging rule ours |
| By task | the six comparisons within classification and within regression (16 datasets each), Holm over these 12; exploratory, decides no hypothesis | instructor's feedback; family ours |
| Confidence intervals | Hodges–Lehmann estimate of each hypothesis's reduction (a pseudo-median; it equals the median only for symmetric reductions) and its 95% interval from the exact signed-rank distribution; zeros kept | Hollander, Wolfe & Chicken (2014), ch. 3; level 1 − α |
| Fixed depth, depth rule | the six comparisons with every cascade cut at each depth that every cascade run trained (1–3; the plan's comparison "at each depth that all of them trained", tested since 25.10.2026); for base per depth: how often the rule picks it, the median gap between OOF and test error, and base at that depth vs base at its chosen layer | ours, after the results review of 23.10.2026 |
| Sensitivity | each check vs the main run of the same method (seed 0), and each variant vs base under the same setting (the check's own base, the no-binning base for ReLU/GELU, or main base for the K checks); no tests | plan §5; comparison design ours |
| Complete case | the hypothesis tests run only when every run of the 7 methods in the six comparisons is finished; an interim report compares only runs every method finished | ours |

## Caveats

- ReLU is the identity on [0, 1], so in the no-binning check its columns copy P. That still tests
  whether more weight for P among the columns tried at a split helps, which is the plan's rationale.
- With the same folds at every layer (as in gcForest), OOF predictions on a fold model's training
  rows (layer ≥ 2) come from models that saw its validation rows. So from layer 2 a fold model's
  selection and training columns carry second-order information about its validation labels (review
  of 08.11.2026: permuting them changes the selection in 8 of 10 trials at layer 2, never at
  layer 1), and the OOF depth score could be optimistic. Measured, the opposite dominates: the base cascade's test error is lower than
  its OOF error, and more so at deeper layers (main report, *Depth rule*: a median 2–9% at layers
  1–3). A probable cause, not verified: a test prediction averages three fold models, an OOF
  prediction comes from one. The depth rule therefore undervalues deeper layers and stops early
  (layer 2 beats the chosen layer on 19 of 32 datasets). Outer test folds are unaffected, and the
  hypothesis comparisons are no better at fixed depths 1–3 (*fixed depth* table).
- When the base cascade and a variant that adds columns only from layer 2 (XP-MI, non-linear,
  monotone) both stop at layer 1, their predictions are identical and the dataset contributes a
  zero difference.
- LightGBM's early stopping and its choice of setting use the same inner validation folds, so the
  inner scores are optimistic; the outer test folds are unaffected. The chosen setting's mean tree count
  reaches the 1,000-tree cap in 6 of 480 runs of the main run; only the rounded mean is saved, so single
  inner fits that hit the cap are not counted.
- Test predictions are saved as float32. Balanced accuracy recomputed from them differs from the
  recorded value in 22 of 2,640 classification runs of the main run (at most 0.0083 at the chosen layer,
  0.021 at any layer; ties in the argmax); the primary metric is always the recorded one, the post-hoc
  metrics come from the saved predictions. Recomputed from the saved predictions, the six comparisons
  decide the same (e.g. H4 p 0.889 → 0.849; Codex audit of 08.11.2026).
- In 306 of 2,640 classification runs of the main run, some test row gives its true class probability
  0 (108 of them single forests; mostly on Page Blocks, Adult and Bank Marketing). scikit-learn's log-loss
  clips it at float64 epsilon (about 36 per row), so log-loss there depends on the clip.
- Categories stored as numbers are kept as numeric columns in three datasets, although plan §4
  one-hot encodes categorical features: Credit Default (SEX, EDUCATION, MARRIAGE), Auto MPG (origin)
  and Energy Efficiency (X6 orientation, X8 glazing-area distribution). Found in the review of
  08.11.2026, after the runs; kept as run. It changes their candidate products and, through d,
  sometimes K.
- The data hash in the fingerprint covers X, y and the groups but not the categorical flags, and
  `datasets.py` is not a compute file. Changing a dataset's `categorical` tuple therefore does not
  mark its results stale; re-run that dataset into a fresh results folder. The smoke datasets are
  hashed by name, so a change to their generator is not detected either. `dfx run --dry-run` can
  create a missing split file (`run.py` asks for the fingerprints, which create splits, before it
  checks the flag). All three are left as run, since fixing them edits compute files.

## Exploratory follow-up of 12.11.2026

Chosen after the main results; all off by default (the defaults reproduce the earlier runs bit for bit).

| Setting | Value | Source |
|---|---|---|
| Content of the added columns (`target_sum_xx`, `target_copy_xx`, `target_noise_xx`) | the pairs of target-XX; sum x_i + x_j, copy of x_i, or noise: per row, the products of a random training row of the fold model | ours |
| Minimum leaf size (`min_leaf`) | 1 (DF21); 5 and 20 in `leaf` | ours |
| Forests that get the added columns (`added_forests`) | all; in `mixed` the first RF and the first ERF of each layer | ours |
| Training rows (`train_rows`, `train_draws`, `train_draw`) | all; nested stratified subsets of 250 to 64,000 rows, or 4 disjoint draws of 1,000 | ours |
| Rows of the large datasets | at most 100,000, subsampled as in the plan | ours |
| Large datasets | Covertype, MiniBooNE, HIGGS (OpenML 23512, with and without its 7 high-level features), SGEMM (target: log of the mean of 4 runs), CASP | ours |
| Synthetic targets (`syn_*`) | 1,000 rows, 10 N(0,1) features; x0 + x1 + x2, x0 + 3 x1 x2, x0 + 1.5 sign(x1) x2^2, noise sd 0.5 | ours |

