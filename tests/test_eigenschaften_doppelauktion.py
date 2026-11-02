"""Eigenschaftstests (ORACLE-PLAYBOOK §5): Aussagen, die für jeden Markt gelten müssen, unabhängig von einem Vergleichswert."""

import numpy as np
import pytest

import dau_algorithm as A


def _markets(count=150, seed=1, rounded=False, sizes=((1, 1), (2, 3), (3, 3), (4, 5), (6, 6))):
    rng = np.random.default_rng(seed)
    for _ in range(count):
        nb, ns = sizes[int(rng.integers(len(sizes)))]
        b, s = rng.random(nb) * 10, rng.random(ns) * 10
        if rounded:
            b, s = np.round(b * 2) / 2, np.round(s * 2) / 2
        yield list(b), list(s)


def test_mcafee_trades_k_or_k_minus_one_and_loses_exactly_the_dropped_pair():
    for rounded in (False, True):
        for b, s in _markets(rounded=rounded):
            o = A.mcafee(b, s)
            k, bo, so = A.efficient_k(b, s)
            assert o.k == k and o.t in (k, max(k - 1, 0))
            loss = A.max_welfare(b, s) - o.welfare
            if o.reduced:
                assert loss == pytest.approx(b[bo[k - 1]] - s[so[k - 1]])
            else:
                assert loss == pytest.approx(0.0)
                if k:
                    assert o.p0 is not None and s[so[k - 1]] - 1e-12 <= o.p0 <= b[bo[k - 1]] + 1e-12


def test_mcafee_is_individually_rational_and_weakly_budget_balanced():
    for rounded in (False, True):
        for b, s in _markets(rounded=rounded):
            o = A.mcafee(b, s)
            assert (o.ub >= -1e-12).all() and (o.us >= -1e-12).all() and o.surplus >= -1e-12 and o.pb >= o.ps - 1e-12


def test_mcafee_welfare_is_at_least_one_minus_one_over_k_of_the_maximum():
    for b, s in _markets(300):
        o = A.mcafee(b, s)
        if o.k:
            assert o.welfare >= (1 - 1 / o.k) * A.max_welfare(b, s) - 1e-9


def test_the_traders_are_the_highest_buyers_and_the_lowest_sellers():
    for b, s in _markets(100, rounded=True):
        o = A.mcafee(b, s)
        bo, so = A.order(b, s)
        assert o.buyers == bo[:o.t] and o.sellers == so[:o.t]


def test_the_allocation_is_monotone_in_the_own_report():
    """Wer mit einem Gebot x handelt, handelt auch mit jedem besseren (Käufer: höher, Verkäufer: niedriger)."""
    for b, s in list(_markets(40, sizes=((3, 3), (4, 5)))):
        for i in range(len(b)):
            traded = [i in A.mcafee(b[:i] + [x] + b[i + 1:], s).buyers for x in np.arange(0.0, 12.01, 0.5)]
            assert traded == sorted(traded)                                       # False ... False True ... True
        for j in range(len(s)):
            traded = [j in A.mcafee(b, s[:j] + [x] + s[j + 1:]).sellers for x in np.arange(0.0, 12.01, 0.5)]
            assert traded == sorted(traded, reverse=True)


def test_scaling_all_values_scales_prices_and_welfare():
    for b, s in _markets(60):
        o, o3 = A.mcafee(b, s), A.mcafee([3 * x for x in b], [3 * x for x in s])
        assert (o3.t, o3.reduced) == (o.t, o.reduced) and o3.pb == pytest.approx(3 * o.pb) and o3.ps == pytest.approx(3 * o.ps) and o3.welfare == pytest.approx(3 * o.welfare)


def test_renaming_the_participants_changes_nothing_about_prices_and_welfare():
    rng = np.random.default_rng(5)
    for b, s in _markets(60):
        pb, ps = rng.permutation(len(b)), rng.permutation(len(s))
        o, o2 = A.mcafee(b, s), A.mcafee([b[i] for i in pb], [s[j] for j in ps])
        assert (o2.t, o2.reduced) == (o.t, o.reduced) and o2.pb == pytest.approx(o.pb) and o2.ps == pytest.approx(o.ps) and o2.welfare == pytest.approx(o.welfare)


def test_vcg_is_truthful_and_has_a_deficit_while_the_midpoint_price_is_manipulable():
    grid = np.arange(0.0, 12.01, 0.5)
    manipulable = 0
    for b, s in _markets(40, sizes=((3, 3), (4, 4)), rounded=True):
        v = A.vcg(b, s)
        assert A.max_gain("vcg", b, s, grid) == 0.0 and v.surplus <= 1e-12 and v.welfare == pytest.approx(A.max_welfare(b, s))
        assert A.max_gain("mcafee", b, s, grid) == 0.0
        manipulable += A.max_gain("mitte", b, s, grid) > 1e-9
    assert manipulable > 20


def test_with_one_buyer_and_one_seller_mcafee_never_trades():
    rng = np.random.default_rng(6)
    for _ in range(100):
        b, s = [float(rng.random() * 10)], [float(rng.random() * 10)]
        o = A.mcafee(b, s)
        assert o.t == 0 and o.welfare == 0.0 and o.surplus == 0.0


def test_adding_a_profitable_pair_never_lowers_the_maximum_welfare():
    for b, s in _markets(60):
        assert A.max_welfare(b + [100.0], s + [0.0]) >= A.max_welfare(b, s) - 1e-12        # ein neues Paar mit großem Gewinn kann die Wohlfahrt nur erhöhen
