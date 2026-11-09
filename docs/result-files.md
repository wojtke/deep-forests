# Result files

## Terms used in the code

- **task**: one method on one dataset, seed and outer fold.
- **check**: one sensitivity setting. In the main experiment there is a single check, `default`.
- **fold model**: the forests of one layer trained on two of the three inner parts of the outer-training
  rows. They predict the third part, and these out-of-fold (**OOF**) predictions feed the next layer.
- **P**: a layer's prediction columns.
- **XX** / **XP**: feature × feature / feature × prediction products.

The outer test rows pass through every layer as it is trained but never fit anything, so every layer's
test score is recorded and no model is stored.

## Per-run files

Each task writes `results/<experiment>/<check>/<dataset>/<method>/s<seed>-f<fold>.npz`, then the `.json`
next to it. The JSON holds a fingerprint of the task, its settings, the code and `uv.lock`, the data
and the split. A rerun skips a task only if its fingerprint still matches. JSON keys:

- `task` (with its full settings), `fingerprint`, `task_type`, `n_train`, `n_test`, `n_classes`, `d`.
- `best_layer`, `n_layers` (counted from 1), and `metrics`: the test metrics at the best layer.
- `layers`: per layer, `oof_score`, `metrics`, `cpu_seconds` and `selections`.
  - `oof_score` is the depth score of the OOF predictions: balanced accuracy, or MSE in regression. It is `null` for baselines.
  - `selections` has one dict per fold model, e.g. `{"residual_xx": {"pairs": [[i, j], ...], "pool": n}}`.
  - `pairs` index encoded features; for XP, j indexes the p_{t,c} columns, type-major.
  - `pool` counts the non-constant candidates.
  - `xp_mi` also stores `max_corr_with_P`.
- `info`: K, or LightGBM's chosen and tried settings.
- `cpu_seconds`, `wall_seconds`, and `worker_peak_rss_mb` (the worker's peak so far).

The NPZ holds `test_index` (rows of the prepared dataset), `y_true`, `pred_by_layer` (layers × test
rows × classes) and, for cascades and LightGBM, `inner_folds` (each outer-training row's inner fold).

## Summaries in git

`dfx report` writes `results/<experiment>/runs.csv`, `layers.csv` and `reports/<experiment>/`; it adds
accuracy, ROC AUC, average precision and R², computed from the NPZ predictions. These and
`manifest.json` (environment, commit, dataset hashes) are committed after each experiment.

The per-run files are not in git; they will be attached to a GitHub release. To rebuild a report from
them, extract the tarball into `results/` at the release's commit, run `uv run dfx data` (the report
checks each result's data and split hashes), then `uv run dfx report <experiment>`.
