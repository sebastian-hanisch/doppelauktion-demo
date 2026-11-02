"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12)."""

import time

import numpy as np
import pytest

import dau_algorithm as A
import dau_constants as C
import dau_evaluation as ev
import dau_scenario as S


def test_smallest_and_largest_random_markets_for_both_kinds():
    for kind in C.VALUE_KINDS:
        for nb, ns in ((C.NB_MIN, C.NS_MIN), (C.NB_MAX, C.NS_MAX), (C.NB_MIN, C.NS_MAX), (C.NB_MAX, C.NS_MIN)):
            a = ev.analyse(ev.Settings("zufall", kind, nb, ns, 3))
            assert a.market.nb == nb and a.market.ns == ns and a.outcomes["mcafee"].surplus >= -1e-12
            assert all(g >= 0.0 for g in a.gains.values()) and a.gains["mcafee"] == 0.0 and a.gains["vcg"] == 0.0


def test_the_hand_markets_ignore_the_random_settings():
    a1 = ev.analyse(ev.Settings("hand_a", "stetig", 1, 1, 1))
    a2 = ev.analyse(ev.Settings("hand_a", "raster", 12, 12, 999))
    assert a1.market.b.tolist() == a2.market.b.tolist() == [10.0, 8.0, 6.0] and a1.market.s.tolist() == a2.market.s.tolist() == [2.0, 4.0, 7.0]


def test_no_trade_at_all_is_fine_for_every_mechanism():
    mk = S.Market(np.array([1.0, 2.0]), np.array([8.0, 9.0]))
    for m in C.MECHS:
        o = A.MECH_FUNCS[m](mk.b, mk.s)
        assert o.k == 0 and o.t == 0 and o.welfare == 0.0
    assert ev.verdict_market(0, 0, False, None, 0.0, 0.0, 0.0)[0] == "info"


def test_a_price_exactly_on_the_boundary_counts_as_inside():
    """Der Bereich [s_(k), b_(k)] ist geschlossen; p0 in der Mitte, auf dem Rand und bei lauter gleichen Geboten."""
    o = A.mcafee([10.0, 6.0, 2.0], [4.0, 10.0, 10.0])
    assert (o.k, o.t, o.reduced) == (1, 1, False) and o.p0 == pytest.approx(8.0)
    o = A.mcafee([10.0, 4.0], [4.0, 10.0])                                       # p0 = (4 + 10)/2 = 7 in [4; 10]
    assert (o.k, o.t) == (1, 1) and o.p0 == pytest.approx(7.0)
    o = A.mcafee([6.0, 4.0], [4.0, 6.0])                                         # k = 1; p0 = 5 in [4; 6]
    assert (o.k, o.t) == (1, 1) and o.p0 == pytest.approx(5.0)
    o = A.mcafee([8.0, 8.0], [8.0, 8.0])                                         # k = 2, kein Rang 3: Reduktion, ein Paar handelt zu 8 und 8 (Gleichstand überall)
    assert (o.k, o.t, o.reduced) == (2, 1, True) and o.pb == pytest.approx(8.0) and o.ps == pytest.approx(8.0)


def test_unequal_market_sides_are_handled():
    o = A.mcafee([9.0, 8.0, 7.0, 6.0, 5.0], [1.0])
    assert o.k == 1 and o.t == 0 and o.reduced and o.p0 is None                 # nur ein Verkäufer: kein Rang 2 auf der Verkäuferseite, kein p0
    o = A.mcafee([9.0], [1.0, 2.0, 3.0, 4.0, 5.0])
    assert o.k == 1 and o.t == 0 and o.reduced and o.p0 is None                 # nur ein Käufer: kein p0
    o = A.mcafee([9.0, 3.0], [1.0, 2.0, 3.0, 4.0, 5.0])
    assert (o.k, o.t, o.reduced, o.p0) == (2, 1, True, None) and o.pb == pytest.approx(3.0) and o.ps == pytest.approx(2.0)      # b_(2) = 3 >= s_(2) = 2: k = 2, aber kein dritter Käufer


def test_the_generators_are_deterministic_and_on_the_grid():
    for kind in C.VALUE_KINDS:
        a, b = S.make_market("zufall", kind, 7, 6, 9), S.make_market("zufall", kind, 7, 6, 9)
        assert np.array_equal(a.b, b.b) and np.array_equal(a.s, b.s) and (a.b >= 0).all() and (a.b <= C.VALUE_SCALE).all()
        assert not np.array_equal(a.b, S.make_market("zufall", kind, 7, 6, 10).b)
    r = S.make_market("zufall", "raster", 12, 12, 1)
    assert np.allclose(r.b * 2, np.round(r.b * 2)) and np.allclose(r.s * 2, np.round(r.s * 2))
    with pytest.raises(ValueError):
        S.make_market("unbekannt", "stetig", 3, 3, 1)


def test_the_tempted_agent_is_a_valid_index_and_prefers_a_mechanism_with_a_gain(hand_a):
    b, s = hand_a
    who = ev.tempted_agent(b, s)
    assert 0 <= who < len(b) + len(s)
    side, idx = ("b", who) if who < len(b) else ("s", who - len(b))
    assert max(A.best_gain(m, b, s, side, idx, ev.grid()) for m in C.MECHS) > 0
    assert ev.tempted_agent([1.0, 2.0], [8.0, 9.0]) == 0                          # ohne lohnende Falschangabe: der erste Käufer


def test_the_counts_run_in_time():
    t = time.time()
    ev.truth_census()
    ev.efficiency_table()
    assert time.time() - t < 60


def test_the_efficiency_table_handles_one_pair_and_odd_sizes():
    rows = ev.efficiency_table(ns=(1, 2, 3), trials=500, seed=1)
    assert rows[0]["n"] == 1 and rows[0]["ratio"] == 0.0 and rows[0]["t"] == 0.0 and rows[0]["vcg_deficit"] == pytest.approx(1.0)
    assert 0 < rows[1]["ratio"] < rows[2]["ratio"] < 1 and all(r["surplus"] >= 0 for r in rows)
    rows = ev.efficiency_table(ns=(2, 30), trials=200, seed=2, vcg_max_n=2)
    assert rows[0]["vcg_deficit"] is not None and rows[1]["vcg_deficit"] is None
