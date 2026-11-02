"""Einheitentests des Kerns an von Hand gerechneten Mini-Märkten (DEMO-PLAYBOOK §1b)."""

import numpy as np
import pytest

import dau_algorithm as A
import dau_constants as C


def test_hand_example_a_all_pairs_trade_at_p0(hand_a):
    b, s = hand_a
    o = A.mcafee(b, s)
    assert (o.k, o.t, o.reduced) == (2, 2, False) and o.p0 == pytest.approx(6.5) and o.pb == pytest.approx(6.5) and o.ps == pytest.approx(6.5)
    assert o.buyers == [0, 1] and o.sellers == [0, 1] and o.welfare == pytest.approx(12.0) and o.surplus == pytest.approx(0.0) and A.max_welfare(b, s) == pytest.approx(12.0)
    assert o.ub.tolist() == pytest.approx([3.5, 1.5, 0.0]) and o.us.tolist() == pytest.approx([4.5, 2.5, 0.0])


def test_hand_example_b_has_no_p0_and_drops_a_pair(hand_b):
    b, s = hand_b
    o = A.mcafee(b, s)
    assert (o.k, o.t, o.reduced, o.p0) == (3, 2, True, None) and o.pb == pytest.approx(6.0) and o.ps == pytest.approx(5.5)
    assert o.welfare == pytest.approx(11.0) and A.max_welfare(b, s) == pytest.approx(11.5) and o.surplus == pytest.approx(1.0)
    assert o.buyers == [0, 1] and o.sellers == [0, 1]                       # das dritte Paar (6; 5,5) wird gestrichen


def test_hand_example_c_has_p0_outside_the_interval(hand_c):
    b, s = hand_c
    o = A.mcafee(b, s)
    assert (o.k, o.t, o.reduced) == (2, 1, True) and o.p0 == pytest.approx(8.7) and o.pb == pytest.approx(8.0) and o.ps == pytest.approx(7.5)
    assert o.welfare == pytest.approx(8.0) and A.max_welfare(b, s) == pytest.approx(8.5) and o.surplus == pytest.approx(0.5)


def test_vcg_by_hand(hand_a, hand_b, hand_c):
    for (b, s), pb, ps, deficit in ((hand_a, 6.0, 7.0, 2.0), (hand_b, 5.5, 6.0, 1.5), (hand_c, 7.9, 8.0, 0.2)):
        v = A.vcg(b, s)
        assert v.pb == pytest.approx(pb) and v.ps == pytest.approx(ps) and -v.surplus == pytest.approx(deficit) and v.t == v.k


def test_midpoint_by_hand(hand_a):
    b, s = hand_a
    o = A.midpoint(b, s)
    assert o.t == 2 and o.pb == pytest.approx(0.5 * (8.0 + 4.0)) and o.surplus == pytest.approx(0.0)           # (b_(2) + s_(2)) / 2 = 6


def test_no_profitable_trade_means_no_trade():
    for mech in A.MECH_FUNCS.values():
        o = mech([1.0, 2.0], [5.0, 6.0])
        assert (o.k, o.t) == (0, 0) and o.buyers == [] and o.welfare == 0.0 and o.surplus == 0.0


def test_one_buyer_and_one_seller_never_trade_with_mcafee():
    o = A.mcafee([9.0], [2.0])
    assert (o.k, o.t, o.reduced) == (1, 0, True) and o.welfare == 0.0
    assert A.vcg([9.0], [2.0]).t == 1 and A.vcg([9.0], [2.0]).pb == pytest.approx(2.0) and A.vcg([9.0], [2.0]).ps == pytest.approx(9.0)


def test_equal_bids_are_ordered_by_index():
    bo, so = A.order([5.0, 5.0, 5.0], [3.0, 3.0])
    assert bo == [0, 1, 2] and so == [0, 1]
    o = A.mcafee([5.0, 5.0, 5.0], [3.0, 3.0])
    assert o.k == 2 and o.t == 1 and o.buyers == [0] and o.sellers == [0]          # k = 2, kein zweiter Verkäufer-Rang 3: Reduktion auf ein Paar, die Indizes 0 handeln


def test_utility_when_reporting_by_hand(hand_a):
    b, s = hand_a
    assert A.utility_reporting("mcafee", b, s, "b", 0, 10.0) == pytest.approx(3.5)                          # wahr: 10 - 6,5
    assert A.utility_reporting("mcafee", b, s, "b", 0, 0.0) == pytest.approx(0.0)                           # meldet 0: nicht dabei
    assert A.utility_reporting("mcafee", b, s, "b", 0, 7.0) == pytest.approx(3.5)                           # niedrigere, aber ausreichende Meldung: gleicher Preis
    assert A.utility_reporting("mitte", b, s, "b", 0, 10.0) == pytest.approx(10.0 - 6.0)                    # Mittelpunktpreis (8 + 4) / 2 = 6
    assert A.utility_reporting("mitte", b, s, "b", 1, 6.0) == pytest.approx(8.0 - 0.5 * (6.0 + 4.0))        # Käufer 2 meldet 6: dann ist b_(2) = 6 und p = 5; Nutzen 3 statt 2
    assert A.utility_reporting("mitte", b, s, "b", 1, 8.0) == pytest.approx(2.0)


def test_the_midpoint_price_can_be_manipulated_by_hand(hand_a):
    b, s = hand_a
    truth = A.utility_reporting("mitte", b, s, "b", 1, 8.0)
    lie = A.utility_reporting("mitte", b, s, "b", 1, 6.0)
    assert lie > truth + 0.5 and A.best_gain("mitte", b, s, "b", 1, np.arange(0.0, 12.01, 0.25)) > 0.5
    assert A.best_gain("mcafee", b, s, "b", 1, np.arange(0.0, 12.01, 0.25)) == 0.0


def test_batch_matches_the_scalar_mechanism_on_ties_and_odd_shapes():
    rng = np.random.default_rng(1)
    for nb, ns in ((1, 1), (3, 5), (5, 3), (4, 4), (8, 8)):
        for rounded in (False, True):
            B, S = rng.random((120, nb)) * 10, rng.random((120, ns)) * 10
            if rounded:
                B, S = np.round(B * 2) / 2, np.round(S * 2) / 2
            r = A.batch(B, S)
            for i in range(120):
                o, v = A.mcafee(B[i], S[i]), A.vcg(B[i], S[i])
                assert (o.k, o.t, o.reduced) == (r["k"][i], r["t"][i], bool(r["reduced"][i]))
                assert o.welfare == pytest.approx(r["welfare"][i]) and A.max_welfare(B[i], S[i]) == pytest.approx(r["max_welfare"][i])
                assert o.surplus == pytest.approx(r["surplus"][i]) and -v.surplus == pytest.approx(r["vcg_deficit"][i])


def test_the_constants_of_the_hand_examples(hand_a, hand_b, hand_c):
    for key, (b, s) in zip(("hand_a", "hand_b", "hand_c"), (hand_a, hand_b, hand_c)):
        assert list(C.HAND[key][0]) == b and list(C.HAND[key][1]) == s
