# Non-linear and interaction features for Deep Forest

Experiment code for an MSc project in ensemble learning at Warsaw University of Technology, by Wojciech
Jasiński and Sandra Adamiec.

Deep Forest stacks layers of tree ensembles. Each layer receives the input features and the previous
layer's predictions. We add new columns between layers and compare each variant with the same cascade
without them (the *base cascade*) on 32 public datasets.

## Documents

- **[Research plan](docs/plan.pdf)**: hypotheses H1–H5, methods and protocol, fixed before the runs.
- **[Short report](docs/short-report.pdf)** (draft): the plan and the results in 8 pages. Start here.
- **[The report in plain words](docs/plain-report.pdf)** (draft): the short report retold in everyday words,
  section by section, with a word list. For when the short report is still confusing.
- **[Results report](docs/results-report.pdf)** (draft): results, discussion and the exploratory
  follow-up runs. In short, none of H1–H5 is supported, while on synthetic data with a planted
  interaction the products do help.
- Generated summaries of each experiment: [main](reports/main/summary.md),
  [sensitivity](reports/sensitivity/summary.md), [positive control](reports/positive/summary.md),
  [exploratory follow-up](reports/explore/summary.md).
- [Settings and their sources](docs/decisions.md): the plan, the DF21 source, a library default, or ours.
- [Data audit](docs/data-audit.md): what each dataset contributes and what is excluded.
- [DF21 check](docs/df21-check.md): on four datasets, the base cascade scores within fold-to-fold noise
  of the official DF21 package.
- [Result files](docs/result-files.md): terms used in the code and the format of the saved files.

## Run it

Needs [uv](https://docs.astral.sh/uv/). Python 3.12 is set in `.python-version` and every package
version in `uv.lock`. On macOS, LightGBM also needs OpenMP: `brew install libomp`.

```sh
uv sync
uv run pytest                      # unit tests and an end-to-end smoke run, about 1 min
uv run dfx data                    # download the 32 datasets and check their sha256 hashes
uv run dfx run main --workers 8    # 5,280 runs, 38 CPU-hours; rerun to resume
uv run dfx report main             # statistics, tables and figures -> reports/main/
```

The other experiments in `experiments/` run the same way:
- `sensitivity`: 3,840 runs, 59 CPU-hours;
- `positive`: 330 runs, 2 minutes; every method on two synthetic datasets with one planted interaction;
- `explore`, `explore_synthetic`, `explore_encoding`, `explore_sweep`: the exploratory follow-up runs of the
  results report (Appendix B), with `scripts/` for the interaction measure, the split counts and the summary;
- `content`, `leaf`, `mixed`, `size`, `draws`, `synth`, `sweep_size`, `large`, `large64`: the second exploratory
  follow-up (12.11.2026): what the added columns hold, leaf size, products for half the forests, fewer training
  rows, bias and variance, synthetic targets and six large datasets. Each file states its question, bar and
  prediction, written before the run. The large datasets need `uv run dfx data casp sgemm covertype miniboone
  higgs higgs_low`, and `large` and `large64` run outer folds 0–2 only (`--folds 0,1,2`).
- `large_content`, `sampling`, `sampling_large`: added on 13.11.2026 after reading those results: sum and copy
  controls on the large datasets, and cascades whose forests try all columns at each split. The two on the
  large datasets run outer folds 0–2 only.
- `smoke`: every method on tiny built-in data, 30 s; not a result.

The planned runs (`main`, `sensitivity`, `positive`) were made with the code of the repository's first commit.
The exploratory variants added later are off by default but change the code's fingerprint, so here those runs
count as out of date (rerun here, base and residual-XX reproduce the 320 runs of seed 0 bit for bit). To resume
or verify them, check out the first commit:
`git checkout $(git rev-list --max-parents=0 HEAD)`.

`dfx run -h` shows how to run a subset. CPU-hours are for an Apple M4 (10 cores); the main run took 7.5
hours on 8 workers, at most 0.7 GB of memory each. Every seed is fixed and none depends on the method,
the outer splits are committed in `splits/`, and results are identical with 1 or many workers.

## What is compared

Each layer of the base cascade has 2 random forests (RF) and 2 extremely randomized forests (ERF) of
100 trees, with the defaults of the DF21 0.1.7 package. The variants add columns to each layer's input:

| Method | Added columns | Chosen by | From layer | Tests |
|---|---|---|---|---|
| `base` | none | – | – | – |
| `random_xx` | K feature × feature products | at random, per layer and fold model | 1 | – |
| `target_xx` | K feature × feature products | correlation with the target | 1 | – |
| `residual_xx` | K feature × feature products | correlation with the previous layer's error | 1 | H1 vs base; H2a, H2b vs `random_xx`, `target_xx` |
| `xp_mi` | K feature × prediction products | mutual information with the target | 2 | H3 vs base |
| `nonlinear` | uncertainty of each forest type, disagreement between types | fixed | 2 | H4 vs base |
| `monotone` | sigmoid of every prediction column | fixed | 2 | H5 vs base |
| `combined` | `nonlinear` + `residual_xx` | as above | 1 / 2 | – |
| `rf`, `rf_target_xx` | no cascade: one 400-tree RF, without / with K target-chosen products | – | – | – |
| `lightgbm` | no cascade: LightGBM tuned over 10 random settings on 3 inner folds | – | – | – |

K = min(d, ⌊d(d−1)/8⌋), where d is the number of features after one-hot encoding. The error is
1 − balanced accuracy (classification) or RMSE (regression). Each hypothesis is a two-sided Wilcoxon
signed-rank test over the 32 datasets, with Holm's correction over the six; H2 needs both H2a and H2b.

## Layout

```
docs/          plan, reports (short, plain-words, full), settings, data audit, result-file format
experiments/   one TOML file per experiment: datasets, methods, seeds and settings
src/dfx/       the code
  datasets.py    the 32 dataset specs: source, target, exclusions, groups
  data.py        download, prepare, related-row groups, 20,000-row cap, splits, data audit
  prep.py        imputation, one-hot encoding, standardization; DF21 binning
  forest.py      RF and ERF with DF21 semantics, on scikit-learn trees
  features.py    the added columns, their selection, and which method adds which
  cascade.py     the cascade loop, depth rule and seed streams
  baselines.py   RF, RF + products, LightGBM
  metrics.py     test metrics
  run.py         experiment files -> tasks, worker pool, result files, resume
  report.py      statistics, tables, figures
  cli.py         the dfx command
results/       per experiment: runs.csv, layers.csv, manifest.json (per-run files are not in git)
reports/       per experiment: summary.md, tables and figures, written by dfx report
splits/        the outer folds of each dataset
tests/         unit tests and an end-to-end smoke test
scripts/       check_df21.py: the comparison with the official DF21 package (own environment)
data/          downloads and prepared arrays (not in git)
```

## Credits

- The cascade follows Zhou & Feng, *Deep Forest* (National Science Review, 2019) and the defaults of the
  official DF21 package, [LAMDA-NJU/Deep-Forest](https://github.com/LAMDA-NJU/Deep-Forest) 0.1.7. Its
  code is not copied; `forest.py` and `prep.py` reimplement its forests and binning on scikit-learn.
- Built on scikit-learn, LightGBM, NumPy, SciPy, pandas and matplotlib.
- Datasets: the UCI Machine Learning Repository (CC BY 4.0) and California Housing via scikit-learn.
  Sources are listed in `src/dfx/datasets.py`.

## AI assistance

The code was written with Claude Code (Opus 5.5) from the authors' research plan. The implementation
plan and the code were reviewed by Claude agents and by Codex (gpt-6-astra), and Claude Code applied the
findings. The authors decided the design and are responsible for the code and results.
