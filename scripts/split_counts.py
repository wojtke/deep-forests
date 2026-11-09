"""Where do the trees split? Exploratory, branch explore (09.11.2026); decides nothing.

    uv run python scripts/split_counts.py [--workers 10]

Re-runs seed 0, fold 0 of base, residual_xx and shuffled_xx (experiments/explore.toml, check
"default") on the 32 datasets with tree classes that record, after each fit, the column and depth of
every split. Columns fall into three groups, in the order cascade.fit_predict stacks them: the original
features, the previous layer's predictions P (from layer 2), and the K added columns. The question: do
the forests split on shuffled products, which carry no information about the row? If they take a share
of the splits close to their share of the columns, mostly deep in the trees, the cost of extra columns
fits trees fitting noise on them. Recording changes nothing else: every task's test predictions must
equal the saved run in results/explore bit for bit.

Writes results/explore_splits/{splits.csv, widths.csv, runs.csv}.
"""
import argparse
import tempfile
import time
import warnings
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd
from threadpoolctl import threadpool_limits

from dfx.data import ROOT, load, outer_split
from dfx.features import k_products
from dfx.prep import Preprocessor
from dfx.run import run_task, tasks

GROUPS = ("original", "P", "added")
MAX_DEPTH = 64  # deeper splits are counted at depth 63
METHODS = ["base", "residual_xx", "shuffled_xx"]
STATE = {"patched": False}


def node_depths(tree) -> np.ndarray:
    depth, frontier = np.zeros(tree.node_count, dtype=int), np.array([0])
    while frontier.size:
        left, right = tree.children_left[frontier], tree.children_right[frontier]
        inner = left >= 0
        depth[left[inner]] = depth[right[inner]] = depth[frontier[inner]] + 1
        frontier = np.r_[left[inner], right[inner]]
    return depth


def record(tree) -> None:
    inner = tree.children_left >= 0
    group = np.searchsorted(STATE["bounds"], tree.feature[inner], side="right")
    depth = np.minimum(node_depths(tree)[inner], MAX_DEPTH - 1)
    counts = STATE["counts"].setdefault(STATE["layer"], np.zeros((2, len(GROUPS), MAX_DEPTH)))
    np.add.at(counts[0], (group, depth), 1)
    np.add.at(counts[1], (group, depth), tree.n_node_samples[inner])


def patch() -> None:
    """Swap in recording tree classes and a grow_forest that tracks the layer (once per worker)."""
    if STATE["patched"]:
        return
    import dfx.cascade as cascade
    import dfx.forest as forest

    def recording(base):
        class Recording(base):
            def fit(self, X, y, *args, **kwargs):
                super().fit(X, y, *args, **kwargs)
                record(self.tree_)
                return self
        Recording.__name__ = base.__name__
        return Recording

    forest.DecisionTreeClassifier = recording(forest.DecisionTreeClassifier)
    forest.DecisionTreeRegressor = recording(forest.DecisionTreeRegressor)
    original = cascade.grow_forest

    def grow_forest(kind, task, n_trees, Z, *args, **kwargs):
        layer = STATE["calls"] // STATE["per_layer"] + 1  # calls go layer, inner fold, forest
        STATE["calls"] += 1
        d, p, k = STATE["d"], 0 if layer == 1 else STATE["p"], STATE["k"]
        if Z.shape[1] != d + p + k:
            raise RuntimeError(f"layer {layer}: {Z.shape[1]} columns, expected {d} + {p} + {k}")
        STATE.update(layer=layer, bounds=np.array([d, d + p]), widths={**STATE["widths"], layer: (d, p, k)})
        return original(kind, task, n_trees, Z, *args, **kwargs)

    cascade.grow_forest = grow_forest
    STATE["patched"] = True


def one(task):
    threadpool_limits(1)
    warnings.filterwarnings("ignore", category=UserWarning)
    patch()
    cpu = time.process_time()
    data = load(task.dataset)
    fold_of, _ = outer_split(data, task.seed, task.outer_folds)
    train = np.flatnonzero(fold_of != task.fold)
    d = Preprocessor().fit(data.X[train], data.categorical).transform(data.X[train[:5]]).shape[1]
    cfg = task.cascade
    STATE.update(calls=0, per_layer=cfg.oof_folds * 2 * cfg.n_forests, d=d, p=2 * cfg.n_forests * data.n_classes,
                 k=k_products(d, cfg.k_mode) if task.method.endswith("_xx") else 0, counts={}, widths={})
    with tempfile.TemporaryDirectory() as tmp:
        rec = run_task(task, Path(tmp), "split-count")
        pred = np.load(task.path(Path(tmp)).with_suffix(".npz"))["pred_by_layer"]
    saved = np.load(task.path(ROOT / "results").with_suffix(".npz"))["pred_by_layer"]
    key = {"dataset": task.dataset, "method": task.method}
    splits = [{**key, "layer": layer, "group": GROUPS[g], "depth": depth, "splits": int(c[0, g, depth]),
               "samples": int(c[1, g, depth])}
              for layer, c in STATE["counts"].items() for g in range(len(GROUPS))
              for depth in np.flatnonzero(c[0, g])]
    widths = [{**key, "layer": layer, "group": GROUPS[g], "columns": w}
              for layer, ws in STATE["widths"].items() for g, w in enumerate(ws)]
    run = {**key, "task": data.task, "identical": bool(np.array_equal(pred, saved)), "best_layer": rec["best_layer"],
           "n_layers": rec["n_layers"], "cpu_seconds": round(time.process_time() - cpu, 1)}
    return splits, widths, run


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=10)
    args = ap.parse_args()
    todo = tasks("explore", checks=["default"], methods=METHODS, seeds=[0], folds=[0])
    size = {t.dataset: len(load(t.dataset).y) for t in todo}
    todo.sort(key=lambda t: -size[t.dataset])  # largest first
    with ProcessPoolExecutor(args.workers) as pool:
        out = list(pool.map(one, todo))
    folder = ROOT / "results" / "explore_splits"
    folder.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([r for s, _, _ in out for r in s]).to_csv(folder / "splits.csv", index=False)
    pd.DataFrame([r for _, w, _ in out for r in w]).to_csv(folder / "widths.csv", index=False)
    runs = pd.DataFrame([r for _, _, r in out])
    runs.to_csv(folder / "runs.csv", index=False)
    print(f"wrote {folder}: {len(runs)} tasks, {runs.identical.sum()} identical to the saved runs, "
          f"{runs.cpu_seconds.sum() / 3600:.2f} CPU-h")


if __name__ == "__main__":
    main()
