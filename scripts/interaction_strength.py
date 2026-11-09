"""How much interaction does a dataset hold? Exploratory, branch explore (09.11.2026); decides nothing.

    uv run python scripts/interaction_strength.py [--workers 10]

Per dataset, seed 0, the 5 outer folds of the main run: LightGBM with stumps (2 leaves, an additive model)
against LightGBM with 31 leaves (its default). The relative error reduction from stumps to 31 leaves is
the measure: 0 when an additive model does as well, larger when interactions matter. Run on the 32
datasets and the interaction-sweep datasets (src/dfx/datasets.py: SEMI), so the real datasets can be
placed on the sweep's scale. Settings are ours: learning rate 0.1 (LightGBM's default), at most 20,000
trees (in a test, 5,000 left the stumps on Servo at the cap), early stopping with patience 50 on inner
fold 0 of 5 (grouped); the model at its best iteration predicts the outer test fold.
Writes results/explore_interaction/interaction.csv.
"""
import argparse
import time
import warnings
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from dfx.baselines import _predict
from dfx.data import ROOT, inner_split, load, outer_split
from dfx.datasets import ALL, SEMI
from dfx.metrics import error, metrics
from dfx.prep import Preprocessor

SEED, FOLDS, MAX_TREES, PATIENCE = 0, 5, 20000, 50
MODELS = {"stumps": {"num_leaves": 2, "max_depth": 1}, "deep": {"num_leaves": 31}}


def one(args):
    name, fold = args
    import lightgbm as lgb

    threadpool_limits(1)
    warnings.filterwarnings("ignore", category=UserWarning)
    cpu = time.process_time()
    data = load(name)
    fold_of, _ = outer_split(data, SEED, FOLDS)
    train, test = np.flatnonzero(fold_of != fold), np.flatnonzero(fold_of == fold)
    prep = Preprocessor().fit(data.X[train], data.categorical)
    xs_tr, xs_te, y_tr = prep.transform(data.X[train]), prep.transform(data.X[test]), data.y[train]
    _, folds = inner_split(y_tr, data.groups[train], data.task, 5, SEED)
    tr, va = folds[0]
    model_class = lgb.LGBMClassifier if data.task == "classification" else lgb.LGBMRegressor
    rows = []
    for model_name, params in MODELS.items():
        model = model_class(n_estimators=MAX_TREES, learning_rate=0.1, n_jobs=1, deterministic=True,
                            force_row_wise=True, verbose=-1, random_state=SEED, **params)
        model.fit(xs_tr[tr], y_tr[tr], eval_X=(xs_tr[va],), eval_y=(y_tr[va],),
                  callbacks=[lgb.early_stopping(PATIENCE, verbose=False)])
        pred = _predict(model, xs_te, data.task, data.n_classes)
        trees = model.best_iteration_ or MAX_TREES
        rows.append({"dataset": name, "task": data.task, "fold": fold, "model": model_name,
                     "error": error(metrics(data.y[test], pred, data.task), data.task), "trees": trees,
                     "cap_hit": trees >= MAX_TREES})
    for r in rows:
        r["cpu_seconds"] = round((time.process_time() - cpu) / len(rows), 3)
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=10)
    args = ap.parse_args()
    names = list(ALL) + sorted(SEMI)
    size = {n: len(load(n).y) for n in names}
    jobs = sorted(((n, f) for n in names for f in range(FOLDS)), key=lambda j: -size[j[0]])  # largest first
    with ProcessPoolExecutor(args.workers) as pool:
        rows = [r for rs in pool.map(one, jobs) for r in rs]
    out = ROOT / "results" / "explore_interaction"
    out.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows).sort_values(["dataset", "fold", "model"])
    df.to_csv(out / "interaction.csv", index=False)
    print(f"wrote {out / 'interaction.csv'}: {len(df)} fits, {df.cap_hit.sum()} at the tree cap, "
          f"{df.cpu_seconds.sum() / 3600:.2f} CPU-h")


if __name__ == "__main__":
    main()
