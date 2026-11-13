"""Fast checks of the pieces the results depend on: splits, preprocessing, forests, added columns,
the cascade's fold and test-row rules, the depth rule and the statistics."""
import numpy as np
import pandas as pd
import pytest

from dfx import cascade as cascade_module
from dfx import forest as forest_module
from dfx.cascade import CascadeConfig, depth_rule, fit_predict, new_columns_test
from dfx.data import fold_ids, inner_split, related_groups, subsample
from dfx.features import Monotone, NonLinear, Outputs, Products, k_products
from dfx.forest import grow_forest
from dfx.prep import Binner, Preprocessor
from dfx.report import (comparisons, hodges_lehmann, holm, mean_errors, paired, post_hoc_metrics,
                        relative_reduction)

TINY = CascadeConfig(n_trees=4, max_layers=3)


def problem(task="classification", n=240, d=5, seed=0):
    rng = np.random.default_rng(seed)
    X = rng.normal(size=(n, d))
    y = (X[:, 0] * X[:, 1] > 0).astype(int) if task == "classification" else X[:, 0] + 2 * X[:, 1] * X[:, 2]
    return X, y


def cascade(method, X, y, task="classification", X_te=None, cfg=TINY):
    prep = Preprocessor().fit(X, np.zeros(X.shape[1], bool))
    xs, xs_te = prep.transform(X), prep.transform(X if X_te is None else X_te)
    return fit_predict(xs, y, np.arange(len(y)), xs_te, method=method, task=task,
                       n_classes=2 if task == "classification" else 1, keys=(0, 1, 0), cfg=cfg)


def outputs(probs_rf, probs_erf):
    """Classification outputs: both RF forests give probs_rf, both ERF forests probs_erf."""
    return Outputs(np.stack([probs_rf, probs_rf, probs_erf, probs_erf], 1))


def regression_outputs(rf_mean, rf_sq):
    """One row; both RF forests predict `rf_mean` with mean squared tree prediction `rf_sq`."""
    forests = np.array([[[rf_mean], [rf_mean], [0.0], [0.0]]])
    return Outputs(forests, np.array([[rf_sq, rf_sq, 0.0, 0.0]]))


# --- data ---------------------------------------------------------------------------------------

def test_groups_join_duplicates_and_keys_but_not_missing_keys():
    X = np.array([[1.0, np.nan], [1.0, np.nan], [2.0, 3.0], [4.0, 5.0], [6.0, 7.0], [8.0, 9.0]])
    g = related_groups(X, key=np.array(["a", "b", "b", "c", None, None], dtype=object))
    assert g[0] == g[1] == g[2] != g[3]  # rows 0-1 identical, rows 1-2 share a key
    assert len({g[3], g[4], g[5]}) == 3  # missing keys do not join rows


def test_folds_keep_groups_together_and_are_deterministic():
    rng = np.random.default_rng(0)
    groups = np.repeat(np.arange(60), 3)
    y = rng.integers(0, 2, 180)
    for task in ("classification", "regression"):
        ids = fold_ids(y, groups, task, 5, seed=1)
        assert all(len(set(ids[groups == g])) == 1 for g in np.unique(groups))
        np.testing.assert_array_equal(ids, fold_ids(y, groups, task, 5, seed=1))
        for tr, va in inner_split(y, groups, task, 3, seed=2)[1]:
            assert not set(groups[tr]) & set(groups[va])


def test_subsample_keeps_whole_groups_and_proportions():
    rng = np.random.default_rng(0)
    groups = np.repeat(np.arange(3000), 10)
    y = np.repeat(rng.random(3000) < 0.2, 10).astype(int)
    keep = subsample(y, groups, "classification", 20_000, seed=0)
    assert len(keep) <= 20_000
    assert np.all(np.bincount(groups[keep])[np.unique(groups[keep])] == 10)
    assert abs(y[keep].mean() - y.mean()) < 0.01


# --- preprocessing and binning -------------------------------------------------------------------

def test_preprocessing_uses_training_rows_only():
    X = np.array([[0.0, 1.0], [1.0, 2.0], [0.0, np.nan], [1.0, 4.0]])
    prep = Preprocessor().fit(X, np.array([True, False]))
    assert prep.transform(X).shape[1] == 3  # two dummies, one numeric column
    out = prep.transform(np.array([[7.0, 100.0]]))  # unseen category, extreme value
    assert out[0, :2].tolist() == [0.0, 0.0]
    assert np.isclose(prep.transform(X)[:, 2].mean(), 0)  # standardized on training rows


def test_binner_is_exact_for_few_values_and_has_255_bins():
    few = np.array([[3.0], [1.0], [2.0], [2.0]])
    np.testing.assert_array_equal(Binner().fit(few).transform(few)[:, 0], [2, 0, 1, 1])
    many = np.random.default_rng(0).normal(size=(5000, 1))
    assert len(np.unique(Binner().fit(many).transform(many))) == 255
    np.testing.assert_array_equal(Binner(0).fit(many).transform(many), many.astype(np.float32))


def test_binner_keeps_repeated_thresholds_like_df21():
    col = np.r_[np.zeros(500), np.arange(1.0, 501)][:, None]  # half zeros: 127 thresholds are 0
    bins = Binner().fit(col).transform(col)[:, 0]
    assert bins[0] == 0 and bins[500] == 127 and bins.max() == 254  # bin numbers 1-126 unused


def test_monotone_columns_bin_like_raw_predictions():
    p = np.random.default_rng(0).random((400, 4))
    sig = 1 / (1 + np.exp(-p))
    np.testing.assert_array_equal(Binner().fit(p).transform(p), Binner().fit(sig).transform(sig))


# --- forests ------------------------------------------------------------------------------------

def test_trees_see_distinct_bootstrap_rows_and_sqrt_features(monkeypatch):
    seen = []

    class Recording(forest_module.DecisionTreeClassifier):
        def fit(self, X, y, **kw):
            seen.append({"rows": len(X), "distinct": len(np.unique(X, axis=0)), "features": self.max_features,
                         "splitter": self.splitter})
            return super().fit(X, y, **kw)

    monkeypatch.setattr(forest_module, "DecisionTreeClassifier", Recording)
    X, y = problem()
    [(pred, _)] = grow_forest("erf", "classification", 5, X, y, [X], 3, seed=0)  # 3 classes, one unseen
    assert all(t["rows"] == t["distinct"] < len(X) for t in seen)
    assert all(t["features"] == "sqrt" and t["splitter"] == "random" for t in seen)
    assert pred.shape == (len(X), 3) and np.allclose(pred[:, 2], 0) and np.allclose(pred.sum(1), 1)


# --- added columns ------------------------------------------------------------------------------

def test_k_rule():
    assert [k_products(d) for d in (2, 4, 5, 8, 60)] == [0, 1, 2, 7, 60]
    assert k_products(8, "half") == 4 and k_products(7, "half") == 3 and k_products(8, "double") == 14


def test_products_find_a_pure_interaction_and_drop_constant_candidates():
    X, _ = problem("regression", n=600, d=6)
    y = np.sign(X[:, 1] * X[:, 3])
    for selector in ("target", "residual"):
        p = Products("xx", selector, 1).fit(X, None, y, task="regression", n_classes=1, seed=0)
        assert p.info["pairs"] == [[1, 3]]
    D = np.column_stack([X[:, :2], (X[:, 2] > 0), (X[:, 2] <= 0)]).astype(float)  # two dummies of one feature
    p = Products("xx", "random", 50).fit(D, None, y, task="regression", n_classes=1, seed=0)
    assert [2, 3] not in p.info["pairs"] and len(p.info["pairs"]) == 5  # their product is constant 0


def test_residual_selection_uses_the_layer_error():
    X, _ = problem("regression", n=600, d=4)
    first, second = X[:, 0] * X[:, 1], X[:, 2] * X[:, 3]
    y = first + 0.5 * second
    prev = Outputs(np.repeat(first[:, None, None], 4, axis=1))  # the layer already predicts `first`
    pick = {s: Products("xx", s, 1).fit(X, prev, y, task="regression", n_classes=1, seed=0).info["pairs"]
            for s in ("target", "residual")}
    assert pick == {"target": [[0, 1]], "residual": [[2, 3]]}


def test_entropy_and_disagreement_by_hand():
    out = outputs(np.array([[0.5, 0.5]]), np.array([[1.0, 0.0]]))
    h_rf, h_erf, d = NonLinear().fit(None, out, None).transform(None, out)[0]
    assert np.isclose(h_rf, np.log(2)) and h_erf == 0 and np.isclose(d, 1.0)


def test_regression_uncertainty_is_the_pooled_tree_std():
    assert np.isclose(regression_outputs(3.0, 10.0).tree_std()[0, 0], 1.0)  # trees 2 and 4: mean 3, sd 1


def test_test_rows_average_columns_not_predictions():
    """Plan §3: each added column is the mean of its values computed from each fold model."""
    first, second = np.array([[1.0, 0.0]]), np.array([[0.0, 1.0]])
    a, b = outputs(first, first), outputs(second, second)
    p, cols = new_columns_test([NonLinear()], np.zeros((1, 0)), [a, b])
    np.testing.assert_allclose(p, [[0.5, 0.5] * 4])  # P is averaged
    np.testing.assert_allclose(cols, [[0.0, 0.0, 0.0]])  # entropy of each is 0; of the mean, log 2
    c, d = regression_outputs(0.0, 1.0), regression_outputs(10.0, 101.0)  # each has tree std 1
    _, cols = new_columns_test([NonLinear()], np.zeros((1, 0)), [c, d])
    assert np.isclose(cols[0, 0], 1.0)  # not the std of the pooled trees (about 5.1)


def test_fitted_scalers_are_applied_unchanged_to_test_rows():
    train = Outputs(np.array([[0.0, 0, 0, 0], [5.0, 5, 0, 0]])[:, :, None])  # two rows
    test = regression_outputs(10.0, 101.0)
    mono = Monotone("relu").fit(None, train, None, task="regression")  # min 0, max 5 per column
    np.testing.assert_allclose(mono.transform(None, test)[0, :2], [2.0, 2.0])  # (10 - 0) / 5, not refitted
    xs = np.ones((2, 1))
    xp = Products("xp", "random", 1).fit(xs, train, np.array([0.0, 1.0]), task="regression", n_classes=1, seed=0)
    assert np.isclose(xp.transform(np.ones((1, 1)), test)[0, 0], 3.0)  # (10 - 2.5) / 2.5: training-row scale


# --- the cascade --------------------------------------------------------------------------------

def test_variants_match_the_base_cascade_where_inputs_coincide():
    X, y = problem()
    one = CascadeConfig(n_trees=4, max_layers=1)
    layer1 = {m: cascade(m, X, y, cfg=one).layers[0]
              for m in ("base", "nonlinear", "monotone", "xp_mi", "target_xx", "residual_xx")}
    for m in ("nonlinear", "monotone", "xp_mi"):
        np.testing.assert_array_equal(layer1[m].test_pred, layer1["base"].test_pred)
    np.testing.assert_array_equal(layer1["residual_xx"].test_pred, layer1["target_xx"].test_pred)
    same = [list(sel.values()) for sel in layer1["residual_xx"].selections]
    assert same == [list(sel.values()) for sel in layer1["target_xx"].selections]


@pytest.mark.parametrize("method", ["residual_xx", "xp_mi", "combined"])
def test_test_rows_never_change_training(method):
    X, y = problem()
    rng = np.random.default_rng(5)
    a = cascade(method, X, y, X_te=rng.normal(size=(30, 5)))
    b = cascade(method, X, y, X_te=rng.normal(size=(50, 5)) * 10)
    assert [la.oof_score for la in a.layers] == [lb.oof_score for lb in b.layers]
    assert [la.selections for la in a.layers] == [lb.selections for lb in b.layers] and a.best == b.best


def test_selection_sees_only_the_fold_models_training_rows_at_layer_1():
    X, y = problem("regression")
    cfg = CascadeConfig(n_trees=2, max_layers=1)
    a = cascade("target_xx", X, y, "regression", cfg=cfg)
    va = np.flatnonzero(a.inner_folds == 0)
    y2 = y.copy()
    y2[va] = np.random.default_rng(1).permutation(y2[va]) * 5  # labels the fold-0 model never trains on
    b = cascade("target_xx", X, y2, "regression", cfg=cfg)
    np.testing.assert_array_equal(a.inner_folds, b.inner_folds)
    assert a.layers[0].selections[0] == b.layers[0].selections[0]


def test_new_columns_are_binned_on_the_fold_models_training_rows(monkeypatch):
    fitted_rows = []

    class Recording(Binner):
        def fit(self, Z):
            fitted_rows.append(len(Z))
            return super().fit(Z)

    monkeypatch.setattr(cascade_module, "Binner", Recording)
    X, y = problem()
    result = cascade("residual_xx", X, y, cfg=CascadeConfig(n_trees=2, max_layers=2, patience=5))
    train_sizes = [int((result.inner_folds != f).sum()) for f in range(3)]
    assert fitted_rows == [len(y)] + train_sizes * 2  # X once on all rows; then per layer, per fold model


def test_depth_rule_follows_df21():
    assert depth_rule([0.80, 0.800005], "classification", 1e-5, 2) == (1, False)
    assert depth_rule([0.80, 0.800005, 0.79], "classification", 1e-5, 2) == (1, True)
    assert depth_rule([0.70, 0.75, 0.74, 0.76], "classification", 1e-5, 2) == (4, False)
    assert depth_rule([5.0, 4.0, 4.5, 4.2], "regression", 1e-5, 2) == (2, True)


# --- statistics ---------------------------------------------------------------------------------

def test_relative_reduction_and_holm():
    np.testing.assert_allclose(relative_reduction([0.2, 0.0, 0.1], [0.1, 0.0, 0.2]), [0.5, 0.0, -0.5])
    np.testing.assert_allclose(holm([0.01, 0.04, 0.03]), [0.03, 0.06, 0.06])


def test_mean_errors_tie_when_only_the_summation_order_differs():
    runs = pd.DataFrame({"dataset": "a", "method": ["base", "x"], "error": [0.1 + 0.2 + 0.3, 0.6]})
    assert comparisons(mean_errors(runs), [("t", "x", "base")], family=False).zeros.item() == 1


def test_hodges_lehmann_interval_uses_the_exact_signed_rank_table():
    x = np.random.default_rng(0).normal(size=10)
    i, j = np.triu_indices(10)
    walsh = np.sort((x[i] + x[j]) / 2)
    # n = 10, two-sided 5%: the lower critical value of the signed-rank statistic is 8 (Wilcoxon tables).
    assert hodges_lehmann(x) == (np.median(walsh), walsh[8], walsh[55 - 1 - 8])


def test_post_hoc_metrics_match_scikit_learn():
    from sklearn.metrics import average_precision_score, r2_score, roc_auc_score

    rng = np.random.default_rng(0)
    y, p = rng.integers(0, 3, 90), rng.dirichlet(np.ones(3), 90)
    m = post_hoc_metrics(y, p, "classification")
    assert m["accuracy"] == pytest.approx(np.mean(p.argmax(1) == y))
    assert m["roc_auc"] == pytest.approx(roc_auc_score(y, p, multi_class="ovr"))
    assert m["average_precision"] == pytest.approx(average_precision_score(np.eye(3)[y], p))
    y2, p2 = rng.integers(0, 2, 90), rng.dirichlet(np.ones(2), 90)
    assert post_hoc_metrics(y2, p2, "classification")["roc_auc"] == pytest.approx(roc_auc_score(y2, p2[:, 1]))
    y01 = np.minimum(y, 1)  # class 2 absent from the test fold: skipped
    expected = np.mean([roc_auc_score(y01 == c, p[:, c]) for c in (0, 1)])
    assert post_hoc_metrics(y01, p, "classification")["roc_auc"] == pytest.approx(expected)
    t = rng.normal(size=50)
    assert post_hoc_metrics(t, (t + 0.3)[:, None], "regression")["r2"] == pytest.approx(r2_score(t, t + 0.3))


def test_interim_report_pairs_runs():
    runs = pd.DataFrame({"check": "default", "dataset": "a", "method": ["base", "base", "rf"], "seed": 0,
                         "fold": [0, 1, 0]})
    assert paired(runs).fold.tolist() == [0, 0]


# --- exploratory variants (branch explore, 08.11.2026) ---------------------------------------------

def test_uncentred_features_bin_like_centred_ones():
    """product_origin = "raw" divides by the sd without centring; the binned features must not change."""
    rng = np.random.default_rng(3)
    X = np.column_stack([rng.uniform(1, 4, 500), rng.lognormal(size=500), rng.integers(0, 7, 500).astype(float)])
    cat = np.zeros(3, bool)
    a = Preprocessor().fit(X, cat).transform(X)
    b = Preprocessor(center=False).fit(X, cat).transform(X)
    assert not np.allclose(a, b)
    assert np.array_equal(Binner().fit(a).transform(a), Binner().fit(b).transform(b))


def test_shuffled_products_keep_values_and_choices_but_not_rows():
    X, y = problem()
    xs = Preprocessor().fit(X, np.zeros(X.shape[1], bool)).transform(X)
    kw = dict(task="classification", n_classes=2, seed=7)
    real = Products("xx", "residual", 3).fit(xs, None, y, **kw)
    shuf = Products("xx", "residual", 3, shuffle=True).fit(xs, None, y, **kw)
    assert real.info == shuf.info
    a, b = real.transform(xs, None), shuf.transform(xs, None)
    assert not np.array_equal(a, b) and np.array_equal(np.sort(a, 0), np.sort(b, 0))


def test_split_scale_leaves_the_base_cascade_unchanged():
    X, y = problem()
    plain = cascade("base", X, y)
    scaled = cascade("base", X, y, cfg=CascadeConfig(n_trees=4, max_layers=3, split_scale=True))
    for p, s in zip(plain.layers, scaled.layers):
        assert np.array_equal(p.test_pred, s.test_pred)


# --- exploratory follow-up (branch explore, 09.11.2026) --------------------------------------------

def test_interaction_sweep_adds_a_pure_product_and_keeps_rows_groups_and_folds(monkeypatch):
    from dfx import data as data_module
    from dfx import datasets

    base = datasets.smoke_dataset("smoke_diabetes")
    monkeypatch.setattr(data_module, "load", lambda name: base)
    for lam in (0.0, 1.0):
        monkeypatch.setitem(datasets.SEMI, f"semi_test_{lam}", ("smoke_diabetes", lam))
    zero, one = datasets.semi_dataset("semi_test_0.0"), datasets.semi_dataset("semi_test_1.0")
    assert np.array_equal(zero.y, base.y) and np.array_equal(one.X[:, :-2], base.X)
    assert np.array_equal(zero.X, one.X) and np.array_equal(one.groups, base.groups)  # same u1, u2
    u = one.X[:, -2:]
    assert np.allclose(one.y - base.y, base.y.std() * u[:, 0] * u[:, 1])
    for seed in range(3):
        assert np.array_equal(fold_ids(one.y, one.groups, "regression", 5, seed),
                              fold_ids(base.y, base.groups, "regression", 5, seed))


def test_onehot_specs_list_the_number_coded_categories_and_stay_out_of_all():
    from dfx.data import encode
    from dfx.datasets import ALL, DATASETS, ONEHOT

    assert len(ALL) == 32 and not {s.name for s in ONEHOT} & set(ALL)
    for spec in ONEHOT:
        orig = DATASETS[spec.name.removesuffix("_onehot")]
        assert spec.categorical and not orig.categorical
        assert (spec.task, spec.target, spec.drop, spec.group) == (orig.task, orig.target, orig.drop, orig.group)
    _, cat = encode(pd.DataFrame({"a": [1, 2, 1], "b": [0.5, 0.1, 0.2]}), ("a",))
    assert cat.tolist() == [True, False]


# --- exploratory follow-up (12.11.2026; course folder pro/followup-2026-11-12) ----------------------

def test_content_variants_keep_the_target_chosen_pairs():
    X, y = problem()
    xs = Preprocessor().fit(X, np.zeros(X.shape[1], bool)).transform(X)
    kw = dict(task="classification", n_classes=2, seed=7)
    fitted = {c: Products("xx", "target", 3, content=c).fit(xs[:200], None, y[:200], **kw)
              for c in ("product", "sum", "copy", "noise")}
    assert all(f.info == fitted["product"].info for f in fitted.values())
    i, j = fitted["product"].i, fitted["product"].j
    np.testing.assert_array_equal(fitted["sum"].transform(xs, None), xs[:, i] + xs[:, j])
    np.testing.assert_array_equal(fitted["copy"].transform(xs, None), xs[:, i])
    noise, donor = fitted["noise"], xs[:200, i] * xs[:200, j]
    a = noise.transform(xs, None)
    assert {tuple(r) for r in a} <= {tuple(r) for r in donor}  # whole training rows of products
    np.testing.assert_array_equal(a, noise.transform(xs, None))  # a row set always gets the same noise
    assert not np.array_equal(a[:200], donor)
    assert not np.array_equal(noise.transform(xs[:50], None), a[:50])  # another row set, another draw
    assert noise.transform(xs[:1], None).shape == (1, 3)


def test_min_leaf_and_half_forests_change_only_what_they_should():
    X, y = problem()
    base = cascade("base", X, y)
    for cfg in (CascadeConfig(n_trees=4, max_layers=3, min_leaf=1),
                CascadeConfig(n_trees=4, max_layers=3, added_forests="half")):
        for p, s in zip(base.layers, cascade("base", X, y, cfg=cfg).layers):
            assert np.array_equal(p.test_pred, s.test_pred)
    assert not np.array_equal(base.layers[0].test_pred,
                              cascade("base", X, y, cfg=CascadeConfig(n_trees=4, max_layers=3, min_leaf=20))
                              .layers[0].test_pred)
    # "half": the second RF and the second ERF grow the base cascade's trees at layer 1
    seen = {}

    def spy(kind, task, n_trees, Z, *args, **kwargs):
        seen.setdefault(mode, []).append(Z.shape[1])
        return grow_forest(kind, task, n_trees, Z, *args, **kwargs)

    import pytest as _pytest
    with _pytest.MonkeyPatch.context() as mp:
        mp.setattr(cascade_module, "grow_forest", spy)
        for mode in ("all", "half"):
            cascade("target_xx", X, y, cfg=CascadeConfig(n_trees=4, max_layers=1, added_forests=mode))
    d, k = X.shape[1], k_products(X.shape[1])
    assert seen["all"] == [d + k] * 12 and seen["half"] == [d + k, d, d + k, d] * 3


def test_max_features_default_is_sqrt_and_a_share_changes_the_trees():
    X, y = problem()
    base = cascade("base", X, y)
    same = cascade("base", X, y, cfg=CascadeConfig(n_trees=4, max_layers=3, max_features=0.0))
    assert all(np.array_equal(p.test_pred, s.test_pred) for p, s in zip(base.layers, same.layers))
    full = cascade("base", X, y, cfg=CascadeConfig(n_trees=4, max_layers=3, max_features=1.0))
    assert not np.array_equal(base.layers[0].test_pred, full.layers[0].test_pred)
    seen = []

    def spy(*args, **kwargs):
        seen.append(kwargs["max_features"])
        return grow_forest(*args, **kwargs)

    import pytest as _pytest
    with _pytest.MonkeyPatch.context() as mp:
        mp.setattr(cascade_module, "grow_forest", spy)
        cascade("target_xx", X, y, cfg=CascadeConfig(n_trees=4, max_layers=1, max_features=1.0))
        with _pytest.raises(ValueError):
            cascade("base", X, y, cfg=CascadeConfig(n_trees=4, max_layers=1, max_features=1.0, split_scale=True))
        cascade("target_xx", X, y, cfg=CascadeConfig(n_trees=4, max_layers=1, max_features=1))  # int from TOML
    assert seen == [1.0] * 24 and all(type(v) is float for v in seen)


def test_train_subsets_are_nested_disjoint_and_stratified():
    from dfx.data import train_subset

    y = np.random.default_rng(0).choice(3, 3000, p=[0.6, 0.3, 0.1])
    small, large = (train_subset(y, "classification", n, 1, 0, seed=5) for n in (250, 1000))
    assert set(small) <= set(large) and len(small) == 250 and len(np.unique(large)) == 1000
    assert np.abs(np.bincount(y[small]) / 250 - np.bincount(y) / 3000).max() < 0.01
    draws = [train_subset(y, "classification", 500, 4, j, seed=5) for j in range(4)]
    assert len(set(np.concatenate(draws))) == 2000
    assert all(np.abs(np.bincount(y[d]) / 500 - np.bincount(y) / 3000).max() < 0.02 for d in draws)
    with pytest.raises(ValueError):
        train_subset(y, "classification", 1000, 4, 0, seed=5)
    assert len(train_subset(y.astype(float), "regression", 100, 1, 0, seed=5)) == 100


def test_synthetic_variants_share_target_groups_and_folds():
    from dfx.data import load

    plain, oracle, noisy = (load(f"syn_prod{e}") for e in ("", "_oracle", "_oracle_noise"))
    assert oracle.X.shape[1] == 11 and noisy.X.shape[1] == 21
    for other in (oracle, noisy):
        assert np.array_equal(plain.y, other.y) and np.array_equal(plain.groups, other.groups)
        assert np.array_equal(plain.X, other.X[:, :10])
    np.testing.assert_allclose(oracle.X[:, 10], 3 * plain.X[:, 1] * plain.X[:, 2])
    hidden = load("syn_hidden")
    assert abs(np.corrcoef(hidden.X[:, 1] * hidden.X[:, 2], hidden.y)[0, 1]) < 0.1
