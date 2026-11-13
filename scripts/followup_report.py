"""Summary of the exploratory follow-up runs of 12-13.11.2026 (docs/followup.md). Descriptive only; decides
no hypothesis. Checks the bars written in the headers of experiments/{content,leaf,mixed,size,draws,synth,
sweep_size,large,large64,large_content,sampling,sampling_large,sampling_large_sum}.toml.

    uv run python scripts/followup_report.py [results dir]

Reads results/<experiment>/runs.csv and layers.csv (committed) and writes reports/followup/summary.txt. The
bias-variance section needs the per-run prediction files of experiment draws; with them it also writes
reports/followup/bias_variance.csv, without them it prints that file. "Reduction" is the main report's relative
error reduction, (ref - e) / max(ref, e), of dataset mean errors; positive favours the first-named method.
"""
import contextlib
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import wilcoxon

ROOT = Path(__file__).resolve().parents[1]
RES = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "results"
OUT = ROOT / "reports" / "followup"
pd.set_option("display.width", 250, "display.max_columns", 40, "display.max_rows", 200)


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, text):
        for s in self.streams:
            s.write(text)

    def flush(self):
        for s in self.streams:
            s.flush()


def load(exp):
    p = RES / exp / "runs.csv"
    if not p.exists():
        return None, None
    return pd.read_csv(p), pd.read_csv(RES / exp / "layers.csv")


def red(ref, e):
    """Relative error reduction (ref - e) / max(ref, e); positive favours e."""
    top = np.maximum(ref, e)
    return ((ref - e) / top.where(top > 0, 1)).where(top > 0, 0.0)


def errs(df, by=("dataset",), col="error"):
    return df.groupby(list(by) + ["method"])[col].mean().unstack("method")


def line(name, r, need=None):
    r = r.dropna()
    w, l = int((r > 0).sum()), int((r < 0).sum())
    try:
        p = wilcoxon(r[r != 0]).pvalue if (r != 0).sum() > 5 else np.nan
    except ValueError:
        p = np.nan
    verdict = "" if need is None else ("  bar met" if r.median() > 0 and w >= need else
                                       "  bar met in reverse (count only; see p)" if r.median() < 0 and l >= need else "  bar not met")
    print(f"  {name:46s} median {100 * r.median():+6.2f}%  mean {100 * r.mean():+6.2f}%  W/L {w:2d}/{l:2d} of {len(r):2d}"
          f"  p={p:.3f}{verdict}")
    return r


def layer1(L):
    return L[L.layer == 1]


def head(t):
    print("\n" + "=" * 100 + "\n" + t + "\n" + "=" * 100)



def main():
    global C, CL, S, SL
    # ---------------------------------------------------------------------------------------------- identity
    C, CL = load("content")
    M, _ = load("main")
    head("Identity: content (new code) vs main seed 0, same method/dataset/fold")
    if C is not None and M is not None:
        k = ["dataset", "method", "fold"]
        j = C.merge(M[M.seed == 0], on=k, suffixes=("", "_main"))
        same = (j.error == j.error_main)
        print(f"  {len(j)} shared runs, error bit-identical in {int(same.sum())}; max abs diff {float((j.error - j.error_main).abs().max()):.3g}")
        print("  by method:", j.assign(same=same).groupby("method").same.agg(["sum", "size"]).to_dict("index"))

    # ---------------------------------------------------------------------------------------------- content
    head("N2 content: what is in a product column (32 datasets, seed 0)")
    if C is not None:
        E, E1 = errs(C), errs(layer1(CL))
        for lab, e in [("chosen layer", E), ("layer 1", E1)]:
            print(f" [{lab}]")
            line("C0 noise vs base", red(e.base, e.target_noise_xx), 20)
            line("C1 target_xx vs noise", red(e.target_noise_xx, e.target_xx), 20)
            line("C2 target_xx vs sum", red(e.target_sum_xx, e.target_xx), 20)
            line("C2 target_xx vs copy", red(e.target_copy_xx, e.target_xx), 20)
            for m in ["target_xx", "target_sum_xx", "target_copy_xx", "random_xx", "residual_xx"]:
                line(f"   {m} vs base", red(e.base, e[m]), 20)
            line("   sum vs noise", red(e.target_noise_xx, e.target_sum_xx), 20)
            line("   copy vs noise", red(e.target_noise_xx, e.target_copy_xx), 20)
            line("   random_xx vs noise", red(e.target_noise_xx, e.random_xx), 20)
        if (RES / "explore/runs.csv").exists():
            X = pd.read_csv(RES / "explore/runs.csv")
            ex = errs(X[X.seed == 0]) if "seed" in X else errs(X)
            if "shuffled_xx" in ex:
                print(" [old shuffled control vs repaired noise control, chosen layer]")
                line("old shuffled_xx vs base", red(E.base, ex.shuffled_xx.reindex(E.index)), 20)
                line("repaired noise vs old shuffled", red(ex.shuffled_xx.reindex(E.index), E.target_noise_xx), 20)
        t = pd.DataFrame({m: 100 * red(E.base, E[m]) for m in E.columns if m != "base"})
        t["n"] = C[C.method == "base"].groupby("dataset").n_train.mean()
        t["task"] = C.groupby("dataset").task.first().str[:3]
        print(t.sort_values("n").round(2).to_string())
        print(" mean layers trained / chosen layer:", C.groupby("method")[["n_layers", "best_layer"]].mean().round(2).to_dict("index"))

    # ---------------------------------------------------------------------------------------------- leaf
    head("E2 leaf size (leaf 1 = content)")
    F, FL = load("leaf")
    if F is not None and C is not None:
        ntr = C[C.method == "base"].groupby("dataset").n_train.mean()
        big = ntr.index[ntr >= 1000]
        allr = pd.concat([C.assign(check="leaf1"), F])
        alll = pd.concat([CL.assign(check="leaf1"), FL])
        for lab, src in [("chosen layer", allr), ("layer 1", layer1(alll))]:
            e = errs(src, ("check", "dataset"))
            print(f" [{lab}]")
            pen = {}
            for c in ["leaf1", "leaf5", "leaf20"]:
                ec = e.loc[c]
                if c == "leaf20":
                    ec = ec.loc[ec.index.isin(big)]
                pen[c] = line(f"{c}: noise vs base", red(ec.base, ec.target_noise_xx), None)
                line(f"{c}: residual_xx vs base (L2)", red(ec.base, ec.residual_xx), 20 if c != "leaf20" else int(np.ceil(len(ec) * 20 / 32)))
                line(f"{c}: target_xx vs base", red(ec.base, ec.target_xx), None)
                line(f"{c}: target_xx vs noise", red(ec.target_noise_xx, ec.target_xx), None)
                if c != "leaf1":
                    b1 = e.loc["leaf1"].base.reindex(ec.index)
                    line(f"{c}: base vs base at leaf 1", red(b1, ec.base), None)
                    line(f"{c}: residual_xx vs BASE AT LEAF 1", red(b1, ec.residual_xx), None)
            d5 = (pen["leaf5"] - pen["leaf1"])
            print(f"  L1: penalty smaller at leaf 5 than leaf 1 on {int((d5 > 0).sum())} of {len(d5)} (bar 20); median change {100 * d5.median():+.2f} pts")
            d20 = (pen["leaf20"] - pen["leaf1"].reindex(pen["leaf20"].index))
            print(f"      penalty smaller at leaf 20 than leaf 1 on {int((d20 > 0).sum())} of {len(d20)} (>=1,000 rows); median change {100 * d20.median():+.2f} pts")
        # best leaf per dataset, chosen by test error (optimistic for both): product vs base
        e = errs(allr, ("check", "dataset"))
        bb, br = e.base.unstack("check").min(axis=1), e.residual_xx.unstack("check").min(axis=1)
        line("best-leaf residual_xx vs best-leaf base (test-picked)", red(bb, br), 20)

    # ---------------------------------------------------------------------------------------------- mixed
    head("N5 mixed: products for half of the forests ('all' and base = content)")
    H, HL = load("mixed")
    if H is not None and C is not None:
        for lab, a, h in [("chosen layer", errs(C), errs(H)), ("layer 1", errs(layer1(CL)), errs(layer1(HL)))]:
            print(f" [{lab}]")
            for m in ["residual_xx", "target_xx", "random_xx"]:
                line(f"M1 half vs all: {m}", red(a[m], h[m]), 20)
                line(f"M2 half vs base: {m}", red(a.base, h[m]), 20)
                line(f"   all vs base: {m}", red(a.base, a[m]), 20)

    # ---------------------------------------------------------------------------------------------- size
    head("N1 size study (10 datasets; full = content)")
    S, SL = load("size")
    if S is not None and C is not None:
        ds = sorted(S.dataset.unique())
        allr = pd.concat([S, C[C.dataset.isin(ds)].assign(check="full")])
        alll = pd.concat([SL, CL[CL.dataset.isin(ds)].assign(check="full")])
        order = ["n250", "n1000", "n4000", "full"]
        for lab, src in [("chosen layer", allr), ("layer 1", layer1(alll))]:
            e = errs(src, ("check", "dataset"))
            print(f" [{lab}]")
            for name, ref, m in [("S1 noise vs base", "base", "target_noise_xx"), ("S2 residual_xx vs base", "base", "residual_xx"),
                                 ("   target_xx vs base", "base", "target_xx"), ("   random_xx vs base", "base", "random_xx"),
                                 ("S3 target_xx vs noise", "target_noise_xx", "target_xx"),
                                 ("   random_xx vs noise", "target_noise_xx", "random_xx")]:
                t = (100 * red(e[ref], e[m])).unstack("check")[order]
                up = int((t.full > t.n250).sum())
                print(f"  {name:24s} median by size: " + "  ".join(f"{c} {t[c].median():+6.2f}%" for c in order)
                      + f"   higher at full than at 250 on {up}/10; wins at each size: " + "/".join(str(int((t[c] > 0).sum())) for c in order))
                if name.startswith("S"):
                    print(t.round(2).to_string())
        print(" d and K by size:\n", allr[allr.method == "base"].groupby(["dataset", "check"])[["d", "K", "n_train"]].mean().unstack("check").round(0).to_string())
        print(" mean chosen layer by size:\n", allr.groupby(["check", "method"]).best_layer.mean().unstack("method").round(2).loc[order].to_string())

    # ---------------------------------------------------------------------------------------------- draws
    head("N4 bias and variance (11 datasets, 4 disjoint draws of 1,000 rows)")
    D, _ = load("draws")
    BV = OUT / "bias_variance.csv"
    if D is not None:
        if (RES / "draws" / "d0").exists():
            rows = []
            for (ds, m), g in D.groupby(["dataset", "method"]):
                task = g.task.iloc[0]
                for where in ["chosen", "layer1"]:
                    tot = var = bias = n = 0.0
                    for f in sorted(g.fold.unique()):
                        preds, y = [], None
                        for c in ["d0", "d1", "d2", "d3"]:
                            z = np.load(RES / "draws" / c / ds / m / f"s0-f{f}.npz")
                            bl = int(g[(g.check == c) & (g.fold == f)].best_layer.iloc[0]) if where == "chosen" else 1
                            preds.append(z["pred_by_layer"][bl - 1].astype(float))
                            y = z["y_true"]
                        P = np.stack(preds)  # draws x rows x outputs
                        Y = np.eye(P.shape[2])[y.astype(int)] if task == "classification" else y.reshape(-1, 1)
                        v = ((P - P.mean(0)) ** 2).sum(2).mean(0) * 4 / 3  # unbiased spread of 4 draws
                        mse = ((P - Y) ** 2).sum(2).mean(0)
                        tot += mse.sum(); var += v.sum(); bias += (mse - v).sum(); n += len(y)
                    rows.append(dict(dataset=ds, method=m, where=where, mse=tot / n, variance=var / n, bias_noise=bias / n))
            B = pd.DataFrame(rows)
            B.to_csv(BV, index=False)
        else:
            print(" per-run prediction files not found: reading", BV.relative_to(ROOT))
            B = pd.read_csv(BV)
        for where in ["chosen", "layer1"]:
            b = B[B["where"] == where].set_index(["dataset", "method"])
            print(f" [{where}]  (squared error of probabilities / of y; variance = spread over draws; bias+noise = rest)")
            for m in ["residual_xx", "target_noise_xx"]:
                x, base = b.xs(m, level="method"), b.xs("base", level="method")
                t = pd.DataFrame({"mse %": 100 * (x.mse / base.mse - 1), "var %": 100 * (x.variance / base.variance - 1),
                                  "bias %": 100 * (x.bias_noise / base.bias_noise - 1),
                                  "var share base": base.variance / base.mse,
                                  "d var / base mse %": 100 * (x.variance - base.variance) / base.mse,
                                  "d bias / base mse %": 100 * (x.bias_noise - base.bias_noise) / base.mse})
                print(f"  {m} vs base: variance higher on {int((t['var %'] > 0).sum())}/11 (bar 9), bias+noise higher on "
                      f"{int((t['bias %'] > 0).sum())}/11; medians: " + ", ".join(f"{c} {t[c].median():+.2f}" for c in t.columns))
                print(t.round(2).to_string())
        e = errs(D)
        line("draws: residual_xx vs base (error, 4 draws x 5 folds)", red(e.base, e.residual_xx), 9)
        line("draws: noise vs base", red(e.base, e.target_noise_xx), 9)

    # ---------------------------------------------------------------------------------------------- synth
    head("N3 synthetic: selection or representation (1,000 rows, 3 seeds x 5 folds)")
    Y, YL = load("synth")
    if Y is not None:
        e, e1 = errs(Y), errs(layer1(YL))
        print(" mean error (chosen layer):\n", e.round(4).to_string())
        print(" mean error (layer 1, cascade methods):\n", e1.round(4).to_string())
        for t in ["add", "prod", "hidden"]:
            b = e.loc[f"syn_{t}", "base"]
            print(f" [{t}] reduction vs base cascade on plain data: "
                  + ", ".join(f"{m} {100 * (b - e.loc[f'syn_{t}', m]) / max(b, e.loc[f'syn_{t}', m]):+.1f}%" for m in e.columns if m != "base")
                  + f" | oracle (base) {100 * (b - e.loc[f'syn_{t}_oracle', 'base']) / b:+.1f}%"
                  + f" | oracle+10 noise (base) {100 * (b - e.loc[f'syn_{t}_oracle_noise', 'base']) / b:+.1f}%")
        s = Y.groupby(["dataset", "method", "seed"]).error.mean().unstack("seed")
        print(" per-seed errors:\n", s.round(4).to_string())

    head("N3b planted product at fewer rows (6 datasets; full = explore_sweep)")
    W, _ = load("sweep_size")
    X, _ = load("explore_sweep")
    if W is not None:
        parts = [W]
        if X is not None:
            parts.append(X[X.dataset.isin(W.dataset.unique()) & X.method.isin(["base", "residual_xx"])].assign(check="full"))
        A = pd.concat(parts)
        A["lam"] = A.dataset.str[-4:]
        A["src"] = A.dataset.str[5:-5]
        e = errs(A, ("check", "lam", "src"))
        r = 100 * red(e.base, e.residual_xx)
        g = r.groupby(level=["check", "lam"])
        out = pd.DataFrame({"median %": g.median(), "wins of 6": g.apply(lambda x: int((x > 0).sum()))})
        out["bar met"] = (out["median %"] > 0) & (out["wins of 6"] >= 5)
        print(out.unstack("lam").round(2).to_string())
        print(r.unstack("lam").round(2).to_string())

    # ---------------------------------------------------------------------------------------------- large
    head("E1 large data (6 datasets, folds 0-2)")
    G, GL = load("large")
    G64, GL64 = load("large64")
    if G is not None:
        if G64 is not None:
            G, GL = pd.concat([G, G64]), pd.concat([GL, GL64])
        order = [c for c in ["n1000", "n4000", "n16000", "n64000"] if c in set(G.check)]
        print(" tasks:", G.groupby("check").size().to_dict(), "| CPU-hours:", round(G.cpu_seconds.sum() / 3600, 1))
        for lab, src in [("chosen layer", G), ("layer 1", layer1(GL))]:
            e = errs(src, ("check", "dataset"))
            print(f" [{lab}]")
            if lab == "chosen layer":
                print("  mean error:\n", e.unstack("check").swaplevel(axis=1).sort_index(axis=1).reindex(columns=order, level=0).round(4).to_string())
            pairs = [("Z1 noise vs base", "base", "target_noise_xx"), ("Z2 residual_xx vs base", "base", "residual_xx"),
                     ("   random_xx vs base", "base", "random_xx"), ("   residual_xx vs noise", "target_noise_xx", "residual_xx"),
                     ("   random_xx vs noise", "target_noise_xx", "random_xx")]
            if lab == "chosen layer":
                pairs += [("   base vs lightgbm", "lightgbm", "base"), ("   base vs rf", "rf", "base")]
            for name, ref, m in pairs:
                if m not in e or ref not in e:
                    continue
                t = (100 * red(e[ref], e[m])).unstack("check").reindex(columns=order)
                print(f"  {name}\n" + t.round(2).to_string())
        print(" mean chosen layer:\n", G.groupby(["check", "method"]).best_layer.mean().unstack("method").round(2).to_string())
        print(" per-fold residual_xx vs base (sign consistency):")
        pf = G.pivot_table(index=["dataset", "check", "fold"], columns="method", values="error")
        print((100 * red(pf.base, pf.residual_xx)).unstack("fold").round(2).to_string())

    # ---------------------------------------------------------------------------------------------- large_content
    head("LC1 large_content: products, sums and copies on the large datasets (base etc. = large)")
    LC, LCL = load("large_content")
    G0, GL0 = load("large")
    if LC is not None and G0 is not None:
        R, L = pd.concat([LC, G0]), layer1(pd.concat([LCL, GL0]))
        sizes = ["n1000", "n4000", "n16000"]
        for lab, src in [("chosen layer", R), ("layer 1", L)]:
            e = src[src.check.isin(sizes)].groupby(["dataset", "check", "method"]).error.mean().unstack("method")
            t = pd.DataFrame({m + " vs base": 100 * red(e.base, e[m]) for m in
                              ["target_xx", "target_sum_xx", "target_copy_xx", "residual_xx", "random_xx", "target_noise_xx"]})
            print(f" [{lab}]\n" + t.round(2).reindex(sizes, level=1).to_string())
        pf = R[R.check == "n16000"].pivot_table(index=["dataset", "fold"], columns="method", values="error")
        print(" LC1 per fold at 16,000 rows: products vs sums, products vs copies")
        print(pd.DataFrame({"vs sum": 100 * red(pf.target_sum_xx, pf.target_xx),
                            "vs copy": 100 * red(pf.target_copy_xx, pf.target_xx)}).round(2).unstack("fold").to_string())

    # ---------------------------------------------------------------------------------------------- sampling


    def sampling_table(ea, es):
        t = pd.DataFrame({"base all vs sqrt": 100 * red(es.base, ea.base)})
        for m, n in [("target_noise_xx", "noise"), ("target_xx", "target"), ("residual_xx", "resid"),
                     ("target_copy_xx", "copy"), ("target_sum_xx", "sum")]:
            if m in es and m in ea:
                t[n + "|sqrt"], t[n + "|all"] = 100 * red(es.base, es[m]), 100 * red(ea.base, ea[m])
        return t


    head("F5-F7 sampling: all columns tried at each split, 10 benchmark datasets at 4,000 rows (sqrt = size n4000)")
    A, AL = load("sampling")
    if A is not None and S is not None:
        for lab, a, s in [("chosen layer", A, S[S.check == "n4000"]), ("layer 1", layer1(AL), layer1(SL[SL.check == "n4000"]))]:
            ea = errs(a[a.check == "all"])
            es = errs(pd.concat([s, a[a.check == "sqrt_copy"]]))
            t = sampling_table(ea, es)
            print(f" [{lab}]  x|sqrt, x|all: reduction of x against base, both with that sampling\n" + t.round(2).to_string())
            print("  median:", t.median().round(2).to_dict())
            print("  better on:", (t > 0).sum().to_dict(), f"of {len(t)}")
            print(f"  F5 noise penalty closer to zero with all columns: {int((t['noise|all'].abs() < t['noise|sqrt'].abs()).sum())} of {len(t)}")

    head("F1-F4 sampling_large: all columns, six large datasets (sqrt = large and large_content; sum = sampling_large_sum)")
    B2, BL2 = load("sampling_large")
    SM, SML = load("sampling_large_sum")
    if B2 is not None and G0 is not None and LC is not None:
        if SM is not None:
            B2, BL2 = pd.concat([B2, SM]), pd.concat([BL2, SML])
        B2, BL2 = B2.assign(check=B2.check.str[4:]), BL2.assign(check=BL2.check.str[4:])
        ref, refl = pd.concat([G0, LC]), pd.concat([GL0, LCL])
        for lab, a, s in [("chosen layer", B2, ref), ("layer 1", layer1(BL2), layer1(refl))]:
            ea = errs(a, ("dataset", "check"))
            es = errs(s[s.check.isin(["n4000", "n16000"])], ("dataset", "check")).reindex(ea.index)
            print(f" [{lab}]\n" + sampling_table(ea, es).round(2).to_string())
        pf = B2[B2.check == "n16000"].pivot_table(index=["dataset", "fold"], columns="method", values="error")
        cols = {"products vs base": (pf.base, pf.target_xx), "products vs copies": (pf.target_copy_xx, pf.target_xx),
                "copies vs base": (pf.base, pf.target_copy_xx)}
        if "target_sum_xx" in pf:
            cols |= {"sums vs base": (pf.base, pf.target_sum_xx), "products vs sums": (pf.target_sum_xx, pf.target_xx)}
        print(" per fold at 16,000 rows, all columns:")
        print(pd.DataFrame({k: 100 * red(*v) for k, v in cols.items()}).round(2).unstack("fold").to_string())


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "summary.txt", "w") as f, contextlib.redirect_stdout(Tee(sys.stdout, f)):
        main()
