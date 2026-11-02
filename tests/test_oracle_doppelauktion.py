"""Orakel-Tests des Kerns gegen unabhängige Rechenwege (DEMO-PLAYBOOK §12, ORACLE-PLAYBOOK §2).

Orakel: (1) **kritische Werte**: Der Preis eines handelnden Käufers ist sein kleinstes noch gewinnendes Gebot, der eines Verkäufers sein größtes noch gewinnendes (Bisektion über die Handelsentscheidung als
Black Box); (2) **vollständige Aufzählung** aller Profile eines kleinen ganzzahligen Rasters gegen alle Einzelabweichungen (dominante Strategie: gegen alle Meldungen der anderen), individuelle
Rationalität, schwacher Budgetausgleich; (3) VCG durch Neuberechnung der Externalität (beste Zuordnung mit und ohne den Teilnehmer, Aufzählung aller Teilmengen); (4) Handbeispiele von Hand. Alle < 10 s."""

import itertools

import numpy as np
import pytest

import dau_algorithm as A

DEV = np.arange(0.0, 4.01, 0.5)


def best_welfare(b, s):
    """Größte Wohlfahrt durch Aufzählung aller Teilmengen gleicher Größe (kleine Märkte)."""
    best = 0.0
    for r in range(1, min(len(b), len(s)) + 1):
        for bs in itertools.combinations(range(len(b)), r):
            for ss in itertools.combinations(range(len(s)), r):
                best = max(best, sum(b[i] for i in bs) - sum(s[j] for j in ss))
    return best


def critical_value(mech, b, s, side, idx, lo=0.0, hi=30.0):
    """Kleinstes Gebot (Käufer) bzw. größte Kosten (Verkäufer), bei denen der Teilnehmer noch handelt: Bisektion, alle anderen melden wahr."""
    def trades(x):
        bb, ss = list(b), list(s)
        if side == "b":
            bb[idx] = x
            return idx in A.MECH_FUNCS[mech](bb, ss).buyers
        ss[idx] = x
        return idx in A.MECH_FUNCS[mech](bb, ss).sellers
    if side == "b":
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if trades(mid):
                hi = mid
            else:
                lo = mid
        return hi
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if trades(mid):
            lo = mid
        else:
            hi = mid
    return lo


def test_prices_are_the_critical_values_in_random_markets():
    rng = np.random.default_rng(1)
    for _ in range(60):
        nb, ns = int(rng.integers(2, 6)), int(rng.integers(2, 6))
        b, s = list(rng.random(nb) * 10), list(rng.random(ns) * 10)
        o = A.mcafee(b, s)
        for i in o.buyers:
            assert critical_value("mcafee", b, s, "b", i) == pytest.approx(o.pb, abs=1e-6)
        for j in o.sellers:
            assert critical_value("mcafee", b, s, "s", j) == pytest.approx(o.ps, abs=1e-6)


def test_vcg_prices_are_the_critical_values_in_random_markets():
    rng = np.random.default_rng(2)
    for _ in range(40):
        nb, ns = int(rng.integers(2, 6)), int(rng.integers(2, 6))
        b, s = list(rng.random(nb) * 10), list(rng.random(ns) * 10)
        o = A.vcg(b, s)
        for i in o.buyers:
            assert critical_value("vcg", b, s, "b", i) == pytest.approx(o.pb, abs=1e-6)
        for j in o.sellers:
            assert critical_value("vcg", b, s, "s", j) == pytest.approx(o.ps, abs=1e-6)


def test_every_profile_of_a_small_grid_against_every_single_deviation():
    """2 Käufer, 2 Verkäufer, Werte 0 bis 4 ganzzahlig (viele Gleichstände), Meldungen auf dem Raster 0,5: Kein Teilnehmer gewinnt durch eine andere Meldung als die wahre, gleich welche
    Meldungen die anderen abgeben (dominante Strategie); individuelle Rationalität und schwacher Budgetausgleich bei jedem Profil von McAfee und VCG."""
    ints = range(5)
    for mech in ("mcafee", "vcg"):
        for true in ints:
            for others in itertools.product(DEV, repeat=3):
                for agent in range(4):
                    reports = list(others)
                    reports.insert(agent, float(true))
                    b, s = reports[:2], reports[2:]
                    side, idx = ("b", agent) if agent < 2 else ("s", agent - 2)
                    truth = A.utility_reporting(mech, b, s, side, idx, float(true))
                    for x in DEV:
                        assert A.utility_reporting(mech, b, s, side, idx, float(x)) <= truth + 1e-12, (mech, b, s, side, idx, x)
    for b in itertools.product(DEV, repeat=2):
        for s in itertools.product(DEV, repeat=2):
            o = A.mcafee(list(b), list(s))
            assert (o.ub >= -1e-12).all() and (o.us >= -1e-12).all() and o.surplus >= -1e-12
            if o.k:
                assert o.welfare >= (1 - 1 / o.k) * A.max_welfare(list(b), list(s)) - 1e-9


def test_vcg_utility_is_the_marginal_contribution_by_enumeration():
    rng = np.random.default_rng(3)
    for _ in range(40):
        nb, ns = int(rng.integers(1, 5)), int(rng.integers(1, 5))
        b, s = list(np.round(rng.random(nb) * 20) / 2), list(np.round(rng.random(ns) * 20) / 2)
        o = A.vcg(b, s)
        w = best_welfare(b, s)
        assert o.welfare == pytest.approx(w)
        for i in range(nb):
            want = w - best_welfare(b[:i] + b[i + 1:], s)
            assert o.ub[i] == pytest.approx(want, abs=1e-9)
        for j in range(ns):
            want = w - best_welfare(b, s[:j] + s[j + 1:])
            assert o.us[j] == pytest.approx(want, abs=1e-9)


def test_the_efficient_trade_count_and_welfare_by_enumeration():
    rng = np.random.default_rng(4)
    for _ in range(60):
        nb, ns = int(rng.integers(1, 5)), int(rng.integers(1, 5))
        b, s = list(np.round(rng.random(nb) * 20) / 2), list(np.round(rng.random(ns) * 20) / 2)
        assert A.max_welfare(b, s) == pytest.approx(best_welfare(b, s))


def test_the_midpoint_price_is_not_truthful_on_a_small_grid():
    found = 0
    for b in itertools.product(DEV, repeat=2):
        for s in itertools.product(DEV, repeat=2):
            found += A.max_gain("mitte", list(b), list(s), DEV) > 1e-9
    assert found > 100


def test_hand_examples_against_the_critical_values(hand_a, hand_b, hand_c):
    for b, s in (hand_a, hand_b, hand_c):
        o = A.mcafee(b, s)
        for i in o.buyers:
            assert critical_value("mcafee", b, s, "b", i) == pytest.approx(o.pb, abs=1e-6)
