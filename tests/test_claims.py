"""Jede Zahl der README steht hier und wird über dieselben Funktionen wie in der App nachgerechnet (DEMO-PLAYBOOK §4, §11a).

Die Tabellen der README werden Zeile für Zeile gegen `tools/readme_rows.py` geprüft (dieselbe Rundung wie die App); die einzelnen Sätze der README
haben je einen Test unter der Bedingung, die in der README daneben steht."""

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import dau_algorithm as A  # noqa: E402
import dau_constants as C  # noqa: E402
import dau_evaluation as ev  # noqa: E402
import readme_rows as R  # noqa: E402

README = (ROOT / "README.md").read_text(encoding="utf-8")


def test_the_tables_in_the_readme_are_the_computed_rows():
    for name, rows in (("Tabelle 1", R.hand_rows()), ("Tabelle 2", R.truth_rows()), ("Tabelle 3", R.efficiency_rows())):
        for row in rows:
            assert row in README, (name, row)


def test_the_hand_example_sentences():
    for key, text in (("hand_a", "Käufer (10; 8; 6), Verkäufer (2; 4; 7)"), ("hand_b", "Käufer (10; 8; 6), Verkäufer (2; 5; 5,5)"), ("hand_c", "Käufer (10; 8; 7,9), Verkäufer (2; 7,5; 9,5)")):
        assert text in README
    assert C.HAND["hand_a"] == ((10.0, 8.0, 6.0), (2.0, 4.0, 7.0)) and C.HAND["hand_b"] == ((10.0, 8.0, 6.0), (2.0, 5.0, 5.5)) and C.HAND["hand_c"] == ((10.0, 8.0, 7.9), (2.0, 7.5, 9.5))
    a, b, c = (A.mcafee(*C.HAND[k]) for k in ("hand_a", "hand_b", "hand_c"))
    assert a.p0 == pytest.approx(6.5) and (b.k, b.t) == (3, 2) and b.p0 is None and c.p0 == pytest.approx(8.7)
    for part in ("In A liegt $p_0 = 6{,}5$ im Bereich [4; 8]", "Das dritte Paar (6; 5,5) wird gestrichen, der Verlust ist sein Gewinn 0,5", "$p_0 = (7{,}9 + 9{,}5)/2 = 8{,}7$ über dem Gebot 8", "der Verlust ist 0,5"):
        assert part in README, part
    assert A.max_welfare(*C.HAND["hand_b"]) - b.welfare == pytest.approx(0.5) and A.max_welfare(*C.HAND["hand_c"]) - c.welfare == pytest.approx(0.5)


def test_the_standard_market_numbers():
    a = ev.analyse(ev.Settings())
    mk, o = a.market, a.outcomes["mcafee"]
    assert (C.DEFAULT_SEED, mk.nb, mk.ns) == (8, 5, 5)
    assert [f"{x:.2f}" for x in mk.b] == ["3.27", "9.87", "3.19", "7.89", "8.70"] and [f"{x:.2f}" for x in mk.s] == ["3.91", "4.38", "3.73", "1.07", "4.79"]
    assert (o.k, o.t) == (3, 2) and f"{o.p0:.2f}" == "3.82" and f"{o.welfare:.2f}" == "13.77" and f"{a.max_welfare:.2f}" == "17.75" and f"{o.surplus:.2f}" == "7.95" and f"{-a.outcomes['vcg'].surplus:.2f}" == "1.40"
    who = ev.tempted_agent(mk.b, mk.s)
    assert who == 1 and f"{a.gains['mitte']:.2f}" == "1.94"
    assert f"{A.best_gain('mitte', mk.b, mk.s, 'b', 1, ev.grid()):.2f}" == "1.94" and abs(A.utility_reporting("mitte", mk.b, mk.s, "b", 1, 4.0) - A.utility_reporting("mitte", mk.b, mk.s, "b", 1, float(mk.b[1])) - a.gains["mitte"]) < 0.01
    for part in ("$k = 3$, aber $p_0 = 3{,}82$ liegt unter dem Verkäufer-Grenzgebot 3,91", "Nur **2** Paare handeln", "**13,77 von 17,75**", "die Börse behält **7,95**", "Defizit von **1,40**", "bis zu **1,94**"):
        assert part in README, part
    assert o.p0 < float(mk.s[np.argsort(mk.s)[2]])                                                # das Verkäufer-Grenzgebot s_(3) = 3,91


def test_the_truthfulness_sentences():
    c = R.census_result()
    assert (c["profiles"], c["ir_bad"], c["wbb_bad"], c["loss_bad"], c["bound_bad"], c["reduced"]) == (400, 0, 0, 0, 0, 201)
    assert (f"{c['mid_gain_median']:.2f}", f"{c['mid_gain_max']:.2f}", f"{c['vcg_deficit_median']:.2f}") == ("1.25", "4.25", "1.50")
    assert (C.TRUTH_PROFILES, C.TRUTH_SEED, C.UTIL_STEP, C.UTIL_MAX) == (400, 4, 0.25, 12.0)
    for part in ("**201 von 400**", "im Median **1,25**, höchstens **4,25**", "im Median **1,50** je Profil", "(je 0 Verstöße)", "(0 Abweichungen)", "(0 Verstöße)", "400 Zufallsprofile mit 3 bis 4 Käufern und 3 bis 4 Verkäufern", "Seed 4"):
        assert part in README, part


def test_the_efficiency_sentences():
    rows = {r["n"]: r for r in R.efficiency_result()}
    assert (C.EFF_TRIALS, C.EFF_SEED, C.EFF_NS, C.EFF_VCG_MAX_N) == (5000, 8, (1, 2, 3, 5, 10, 20, 50), 20)
    assert rows[1]["ratio"] == 0.0 and rows[1]["t"] == 0.0
    assert [f"{100 * rows[n]['ratio']:.2f}" for n in (2, 10, 50)] == ["76.77", "98.36", "99.92"]
    assert f"{rows[2]['loss_n']:.3f}" == "0.465" and f"{rows[50]['loss_n']:.3f}" == "0.038"
    n2 = [rows[n]["loss_n2"] for n in (2, 3, 5, 10, 20, 50)]
    assert f"{min(n2):.2f}" == "0.93" and f"{max(n2):.2f}" == "1.92" and n2 == sorted(n2)
    assert f"{100 * rows[20]['vcg_deficit']:.1f}" == "5.0" and rows[50]["vcg_deficit"] is None
    for part in ("Schon mit zwei Paaren sind es 76,77 %, mit zehn 98,36 %, mit fünfzig 99,92 %", "sinkt von 0,465 bei $n = 2$ auf 0,038 bei $n = 50$", "zwischen 0,93 und 1,92", "fällt auf 5,0 % bei $n = 20$", "Wohlfahrt 0 % des Maximums"):
        assert part in README, part


def test_the_readme_sentences_about_the_verification():
    assert "1 200 Instanzen" in README and "Werte 0 bis 4" in README
    assert "Aufzählung aller Teilmengen" in README and "Bisektion" in README
