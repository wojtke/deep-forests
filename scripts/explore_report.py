"""Summary of the exploratory runs on branch explore (08.–09.11.2026). Descriptive only; decides no
hypothesis.

    uv run python scripts/explore_report.py [--main ../deep-forest-features/results]

08.11: experiments/explore.toml and explore_synthetic.toml. 09.11: explore_encoding.toml (the three
number-coded datasets one-hot encoded), explore_sweep.toml (a planted interaction of growing strength),
scripts/interaction_strength.py and scripts/split_counts.py.

Writes results/explore*/runs.csv and layers.csv, and reports/explore/{summary.md, comparisons.csv,
synthetic.csv, true_pair.csv, encoding.csv, encoding_errors.csv, sweep.csv, interaction.csv, splits.csv}.
The identity check compares this branch's base and residual-XX test predictions with the main runs of
seed 0 (the main repo's per-run files), which must be equal bit for bit.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from dfx.data import ROOT
from dfx.datasets import SEMI
from dfx.report import ALPHA, HYPOTHESES, collect, comparisons, markdown, mean_errors, reductions, relative_reduction
from dfx.run import tasks

LABEL = {("default", "base"): "base", ("default", "residual_xx"): "residual",
         ("default", "shuffled_xx"): "shuffled", ("raw", "residual_xx"): "residual raw",
         ("split_scale", "residual_xx"): "residual scaled", ("split_scale", "shuffled_xx"): "shuffled scaled",
         ("default", "random_xx"): "random", ("default", "target_xx"): "target", ("raw", "target_xx"): "target raw",
         ("default", "rf"): "rf", ("default", "rf_target_xx"): "rf + target",
         ("raw", "rf_target_xx"): "rf + target raw", ("default", "lightgbm"): "lightgbm"}
# (name, method, reference): written down with the experiment file, before the runs.
PAIRS = [("raw products vs base", "residual raw", "base"),
         ("raw vs centred products", "residual raw", "residual"),
         ("centred products vs base", "residual", "base"),
         ("cost: shuffled products vs base", "shuffled", "base"),
         ("information: products vs shuffled", "residual", "shuffled"),
         ("scaled sampling: products", "residual scaled", "residual"),
         ("scaled sampling: shuffled", "shuffled scaled", "shuffled"),
         ("scaled products vs base", "residual scaled", "base"),
         ("scaled shuffled vs base", "shuffled scaled", "base")]
TRUE_PAIR = {"wide_xor": [0, 1], "wide_pair": [1, 2], "raw_xor": [1, 2], "raw_pair": [1, 2]}
SWEEP_PAIRS = [("products vs base", "residual_xx", "base"), ("RF + products vs RF", "rf_target_xx", "rf")]
DEPTHS = [("all", 0, 63), ("root", 0, 0), ("1-2", 1, 2), ("3-5", 3, 5), ("6-10", 6, 10), ("11+", 11, 63)]


def labelled(runs):
    return runs.assign(method=[LABEL[(c, m)] for c, m in zip(runs.check, runs.method)])


def collected(experiment: str, results: Path):
    """collect() and save runs.csv and layers.csv next to the per-run files."""
    runs, layers, missing = collect(experiment, results)
    runs.to_csv(results / experiment / "runs.csv", index=False)
    layers.to_csv(results / experiment / "layers.csv", index=False)
    return runs, missing


def identity(results: Path, main: Path, runs: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for method in ("base", "residual_xx"):
        same = total = 0
        for ds in sorted(runs.dataset.unique()):
            for fold in range(5):
                a = np.load(results / "explore" / "default" / ds / method / f"s0-f{fold}.npz")["pred_by_layer"]
                path = main / "main" / "default" / ds / method / f"s0-f{fold}.npz"
                if path.exists():
                    total += 1
                    same += np.array_equal(a, np.load(path)["pred_by_layer"])
        rows.append({"method": method, "runs compared": total, "identical": same})
    return pd.DataFrame(rows)


def true_pair_rates(results: Path) -> pd.DataFrame:
    hits = {}
    for f in (results / "explore_synthetic").glob("*/*/*/*.json"):
        if f.name == "manifest.json":
            continue
        r = json.loads(f.read_text())
        t = r["task"]
        label = LABEL.get((t["check"], t["method"]))
        for layer in r["layers"]:
            for sel in layer["selections"]:
                for kind, v in sel.items():
                    if "pairs" not in v or t["dataset"] not in TRUE_PAIR:
                        continue
                    key = (t["dataset"], label, "layer 1" if layer["layer"] == 1 else "layers 2+")
                    h = hits.setdefault(key, [0, 0])
                    h[0] += TRUE_PAIR[t["dataset"]] in v["pairs"]
                    h[1] += 1
    return pd.DataFrame([{"dataset": d, "method": m, "layers": l, "true pair chosen": f"{a}/{b}",
                          "share": round(a / b, 3)} for (d, m, l), (a, b) in sorted(hits.items())])


def encoding(results: Path, main_runs: pd.DataFrame):
    """The six comparisons of seed 0 as run, and with the three number-coded datasets one-hot encoded."""
    runs, missing = collected("explore_encoding", results)
    as_run = mean_errors(main_runs[main_runs.seed == 0])
    onehot = mean_errors(runs.assign(dataset=runs.dataset.str.removesuffix("_onehot")))
    swapped = as_run.copy()
    swapped.loc[onehot.index, onehot.columns] = onehot
    cols = ["comparison", "median_reduction", "wins", "losses", "zeros", "p", "p_holm"]
    table = comparisons(as_run, HYPOTHESES)[cols].merge(comparisons(swapped, HYPOTHESES)[cols], on="comparison",
                                                        suffixes=("_as_run", "_onehot"))
    errors = pd.DataFrame({"error_as_run": as_run.loc[onehot.index, onehot.columns].stack(),
                           "error_onehot": onehot.stack()})
    errors["change"] = errors.error_onehot / errors.error_as_run - 1
    seeds = {s: mean_errors(main_runs[(main_runs.seed == s) & main_runs.dataset.isin(onehot.index)]) for s in (0, 1, 2)}
    per = pd.DataFrame([{"dataset": ds, "comparison": name,
                         "as_run": float(relative_reduction(as_run.loc[ds, ref], as_run.loc[ds, m])),
                         "onehot": float(relative_reduction(onehot.loc[ds, ref], onehot.loc[ds, m])),
                         "seed_range": float(np.ptp([relative_reduction(e.loc[ds, ref], e.loc[ds, m])
                                                     for e in seeds.values()]))}
                        for ds in onehot.index for name, m, ref in HYPOTHESES])
    return table, errors.reset_index(), per, missing


def planted_pair(results: Path) -> dict:
    """Layer-1 selections that include (u1, u2). Both are numeric and the last raw columns, so after
    preprocessing they are the last two encoded features."""
    hits = {}
    for t in tasks("explore_sweep", methods=[m for _, m, _ in SWEEP_PAIRS]):
        r = json.loads(t.path(results).with_suffix(".json").read_text())
        for v in (v for sel in r["layers"][0]["selections"] for v in sel.values() if "pairs" in v):
            h = hits.setdefault((t.method, SEMI[t.dataset][1]), [0, 0])
            h[0] += [r["d"] - 2, r["d"] - 1] in v["pairs"]
            h[1] += 1
    return hits


def sweep(results: Path):
    runs, missing = collected("explore_sweep", results)
    strength = runs.dataset.map(lambda name: SEMI[name][1])
    hits = planted_pair(results)
    parts = [comparisons(mean_errors(g), SWEEP_PAIRS, family=False, ci=True).assign(strength=lam)
             for lam, g in runs.groupby(strength)]
    table = pd.concat(parts, ignore_index=True)
    table.insert(0, "variance_share", table.strength ** 2 / (1 + table.strength ** 2))  # Var(u1 u2) = 1
    table.insert(0, "strength", table.pop("strength"))
    table["planted_pair_layer1"] = [f"{hits[(m, s)][0]}/{hits[(m, s)][1]}" for m, s in zip(table.method, table.strength)]
    return table, missing


def interaction(results: Path, main_errors: pd.DataFrame):
    """Per dataset: error of LightGBM stumps and 31-leaf trees (mean over 5 folds) and the reduction
    from stumps to 31 leaves; for the 32 datasets also H1's and RF + products' reduction (main run)."""
    ia = pd.read_csv(results / "explore_interaction" / "interaction.csv")
    e = ia.groupby(["dataset", "model"]).error.mean().unstack()
    out = pd.DataFrame({"base_dataset": [SEMI[n][0] if n in SEMI else n for n in e.index],
                        "strength": [SEMI[n][1] if n in SEMI else np.nan for n in e.index],
                        "error_stumps": e.stumps, "error_deep": e.deep,
                        "measure": relative_reduction(e.stumps, e.deep)}, index=e.index)
    out["H1_reduction"] = reductions(main_errors, "residual_xx", "base")
    out["rf_products_reduction"] = reductions(main_errors, "rf_target_xx", "rf")
    return out.rename_axis("dataset").reset_index(), int(ia.cap_hit.sum())


def splits(results: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Layer 1, per dataset and method: the added columns' share of the columns, of the splits and of
    the samples reaching those splits, overall and by node depth."""
    sp = pd.read_csv(results / "explore_splits" / "splits.csv")
    widths = pd.read_csv(results / "explore_splits" / "widths.csv")
    sp, widths = sp[(sp.layer == 1) & (sp.method != "base")], widths[(widths.layer == 1) & (widths.method != "base")]
    cols = widths.pivot_table(index=["dataset", "method"], columns="group", values="columns")
    parts = []
    for label, lo, hi in DEPTHS:
        s = sp[sp.depth.between(lo, hi)].groupby(["dataset", "method", "group"])[["splits", "samples"]].sum()
        s = s.unstack(fill_value=0)
        parts.append(pd.DataFrame({"depth": label, "column_share": cols.added / cols.sum(axis=1),
                                   "split_share": s.splits.added / s.splits.sum(axis=1),
                                   "sample_share": s.samples.added / s.samples.sum(axis=1)}))
    return pd.concat(parts).reset_index(), pd.read_csv(results / "explore_splits" / "runs.csv")


def pct(x) -> str:
    return f"{100 * x:+.2f}%"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=str(ROOT / "results"))
    ap.add_argument("--main", default=str(ROOT.parent / "deep-forest-features" / "results"),
                    help="results folder of the main runs (for the identity check and the 09.11 sections)")
    args = ap.parse_args()
    results, main_results, out = Path(args.results), Path(args.main), ROOT / "reports" / "explore"
    out.mkdir(parents=True, exist_ok=True)
    lines = ["# Exploratory runs (branch explore, 08.–09.11.2026)", "",
             "Chosen after the main results; descriptive only, no hypothesis is decided. Relative reduction as in "
             "the main report (positive favours the first method); Wilcoxon p without correction.", ""]

    runs, missing = collected("explore", results)
    if missing.sum():
        lines += [f"**INCOMPLETE: {missing.sum()} tasks missing ({dict(missing)}).**", ""]
    runs = labelled(runs)
    errors = mean_errors(runs)
    task_of = runs.groupby("dataset")["task"].first()
    table = []
    for scope in ("all", "classification", "regression"):
        sub = errors if scope == "all" else errors[task_of.reindex(errors.index) == scope]
        t = comparisons(sub, PAIRS, family=False, ci=scope == "all").assign(scope=scope)
        table.append(t)
    table = pd.concat(table, ignore_index=True)
    table.to_csv(out / "comparisons.csv", index=False)
    raw = table[(table.scope == "all") & (table.comparison == "raw products vs base")].iloc[0]
    changes = raw.median_reduction > 0 and raw.wins >= 20
    lines += ["## Real datasets, seed 0 (32 datasets)", "",
              f"Bar set before running: raw products change the picture only with a positive median against base "
              f"and at least 20 of 32 wins. **Result: median {100 * raw.median_reduction:+.2f}%, "
              f"{raw.wins}/{raw.losses}/{raw.zeros} → {'changes the picture' if changes else 'does not change the picture'}.**",
              "", markdown(table[["scope", "comparison", "method", "reference", "datasets", "median_reduction",
                                  "wins", "losses", "zeros", "p", "hl_estimate", "ci95_low", "ci95_high"]]), ""]
    cpu = runs.groupby("method").cpu_seconds.sum().div(3600).round(2)
    lines += ["CPU-hours per configuration: " + ", ".join(f"{m} {v}" for m, v in cpu.items()), ""]
    ident = identity(results, main_results, runs)
    lines += ["## Identity check against the main runs (seed 0)", "", markdown(ident), ""]

    srun, smissing = collected("explore_synthetic", results)
    srun = labelled(srun)
    srun["score"] = np.where(srun.task == "classification", srun.balanced_accuracy, srun.rmse)
    agg = srun.groupby(["dataset", "method"]).score.agg(["mean", "std"]).round(4).reset_index()
    base = agg[agg.method == "base"].set_index("dataset")["mean"]
    task = srun.groupby("dataset").task.first()
    err = lambda d, v: 1 - v if task[d] == "classification" else v  # noqa: E731
    agg["reduction_vs_base"] = [round((err(d, base[d]) - err(d, v)) / max(err(d, base[d]), err(d, v)), 4)
                                for d, v in zip(agg.dataset, agg["mean"])]
    agg.to_csv(out / "synthetic.csv", index=False)
    lines += ["## Synthetic controls, 3 seeds × 5 folds", "",
              "score = balanced accuracy (xor) or RMSE (pair); reduction_vs_base on the error.", "",
              markdown(agg), ""]
    if smissing.sum():
        lines += [f"**INCOMPLETE: {smissing.sum()} synthetic tasks missing.**", ""]
    tp = true_pair_rates(results)
    tp.to_csv(out / "true_pair.csv", index=False)
    lines += ["## True pair among the chosen products (synthetic)", "", markdown(tp), ""]

    main_runs = pd.read_csv(main_results / "main" / "runs.csv")
    enc, enc_errors, enc_per, emissing = encoding(results, main_runs)
    enc.to_csv(out / "encoding.csv", index=False)
    enc_errors.to_csv(out / "encoding_errors.csv", index=False)
    flips = (np.sign(enc.median_reduction_as_run) != np.sign(enc.median_reduction_onehot)) | \
            ((enc.p_holm_as_run < ALPHA) != (enc.p_holm_onehot < ALPHA))
    lines += ["## 09.11: categories one-hot encoded (seed 0, 32 datasets)", "",
              "Credit Default (SEX, EDUCATION, MARRIAGE), Auto MPG (origin) and Energy (orientation, glazing-area "
              "distribution) ran with these columns number-coded. Here they are one-hot encoded, as the plan says, "
              "and the six comparisons of seed 0 are recomputed with the three datasets swapped in. Seed streams "
              "depend on the dataset name, so the one-hot runs also differ by seed noise.", "",
              f"Bar set before running: the deviation matters only if a median changes sign or a Holm-adjusted p "
              f"crosses 0.05. **Result: {'matters' if flips.any() else 'does not matter'}** "
              f"({int(flips.sum())} of 6 comparisons change).", "", markdown(enc), "",
              "Per dataset: reduction of each comparison as run and one-hot (seed 0), against the range of the "
              "as-run reduction over seeds 0–2.", "", markdown(enc_per.round(4)), "",
              "Error change from one-hot encoding (seed 0, mean over 5 folds):", "",
              markdown(enc_errors.pivot(index="method", columns="dataset", values="change").round(4).reset_index()), ""]
    if emissing.sum():
        lines += [f"**INCOMPLETE: {emissing.sum()} encoding tasks missing.**", ""]

    sw, swmissing = sweep(results)
    sw.to_csv(out / "sweep.csv", index=False)
    prod = sw[sw.comparison == "products vs base"].set_index("strength")
    met = prod[(prod.median_reduction > 0) & (prod.wins >= 9)].index
    lines += ["## 09.11: how strong must an interaction be? (13 regression datasets, seed 0)", "",
              "Two standard-normal columns u1, u2 are added and the target becomes y + λ·sd(y)·u1·u2, so the "
              "interaction explains λ²/(1+λ²) of the new target's variance (0, 6, 20, 50%).", "",
              "Bar (ours), set before running: at a given λ products help if residual-XX vs base has a positive "
              f"median and at least 9 of 13 wins. **Result: met at λ = {', '.join(f'{s:g}' for s in met) or 'none'}; "
              f"smallest {met.min():g}.** Prediction written before the run: met at 1, probably at 0.5, open at "
              "0.25, not at 0.", "",
              markdown(sw.drop(columns=["method", "reference"])), "",
              "planted_pair_layer1: layer-1 selections (fold models) that include (u1, u2).", ""]
    if swmissing.sum():
        lines += [f"**INCOMPLETE: {swmissing.sum()} sweep tasks missing.**", ""]

    ia, caps = interaction(results, mean_errors(main_runs))
    ia.to_csv(out / "interaction.csv", index=False)
    real = ia[ia.strength.isna()]
    rho = spearmanr(real.measure, real.H1_reduction)
    rho_rf = spearmanr(real.measure, real.rf_products_reduction)
    grid = ia[ia.strength.notna()].pivot(index="base_dataset", columns="strength", values="measure")
    grid["as run"] = ia.set_index("dataset").measure.reindex(grid.index)
    lines += ["## 09.11: interaction measure (LightGBM stumps vs 31 leaves, seed 0, 5 folds)", "",
              f"measure = relative error reduction from stumps to 31-leaf trees. {caps} fits stopped at the tree cap. "
              f"Over the 32 datasets, Spearman ρ with H1's per-dataset reduction (main run) = {rho.statistic:.3f} "
              f"(p = {rho.pvalue:.3f}); with RF + products vs RF = {rho_rf.statistic:.3f} (p = {rho_rf.pvalue:.3f}). "
              f"The pilot gave ρ = 0.00 with H1.", "",
              markdown(real.sort_values("measure")[["dataset", "error_stumps", "error_deep", "measure", "H1_reduction",
                                                    "rf_products_reduction"]]), "",
              "Sweep datasets: the measure by λ, and on the dataset as run (without u1, u2).", "",
              markdown(grid.round(4).reset_index()), ""]

    sh, srn = splits(results)
    sh.to_csv(out / "splits.csv", index=False)
    med = sh.groupby(["method", "depth"], sort=False)[["column_share", "split_share", "sample_share"]].median()
    allsh = sh[(sh.depth == "all") & (sh.method == "shuffled_xx")].set_index("dataset")
    cost = reductions(errors, "shuffled", "base")
    rho_cost = spearmanr(allsh.split_share, cost[allsh.index])
    lines += ["## 09.11: where do the trees split? (seed 0, fold 0, layer 1)", "",
              f"{int(srn.identical.sum())} of {len(srn)} recounted runs reproduce the saved test predictions bit for "
              f"bit ({srn.cpu_seconds.sum() / 3600:.2f} CPU-hours). Median over the 32 datasets of the added "
              "columns' share of the columns, of the splits and of the samples reaching those splits, by node depth:",
              "", markdown(med.round(3).reset_index()), "",
              f"Expected if trees fit noise on the extra columns: shuffled products take a share of the splits near "
              f"their share of the columns, mostly deep, and across datasets a larger share goes with a larger cost "
              f"(ρ < 0). Spearman ρ of the shuffled split share with shuffled vs base (seed 0) = "
              f"{rho_cost.statistic:.3f} (p = {rho_cost.pvalue:.3f}).", ""]
    (out / "summary.md").write_text("\n".join(lines))
    print(f"wrote {out}/summary.md")


if __name__ == "__main__":
    main()
