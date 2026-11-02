"""Verdikte an von Hand gesetzten Werten (DEMO-PLAYBOOK §12): jede Zahl im Text und jede Schwelle der Art steht hier."""

import dau_evaluation as ev


def test_market_verdict_branches():
    kind, text = ev.verdict_market(0, 0, False, None, 0.0, 0.0, 0.0)
    assert kind == "info" and "k = 0" in text and "keinen Handel" in text
    kind, text = ev.verdict_market(2, 2, False, 6.5, 12.0, 12.0, 0.0)
    assert kind == "success" and "Alle k = 2 effizienten Paare handeln zum Preis p₀ = 6,50" in text and "Wohlfahrt 12,00 von 12,00" in text and "kein Verlust" in text and "Überschuss der Börse 0,00" in text
    kind, text = ev.verdict_market(3, 2, True, None, 11.0, 11.5, 1.0)
    assert kind == "warning" and "Von k = 3 effizienten Paaren handeln nur 2" in text and "keinen Rang k + 1" in text and "(Verlust 0,50)" in text and "die Börse behält 1,00" in text
    kind, text = ev.verdict_market(2, 1, True, 8.7, 8.0, 8.5, 0.5)
    assert kind == "warning" and "p₀ = 8,70 liegt nicht zwischen" in text and "handeln nur 1" in text


def test_lies_verdict_branches():
    kind, text = ev.verdict_lies({"mcafee": 0.0, "vcg": 0.0, "mitte": 0.0})
    assert kind == "success" and "bei keinem der drei Mechanismen" in text
    kind, text = ev.verdict_lies({"mcafee": 0.0, "vcg": 0.0, "mitte": 1.94})
    assert kind == "warning" and "Mittelpunktpreis (bis 1,94)" in text and "McAfee" not in text.split("bei:")[1].split(".")[0]
    assert ev.verdict_lies({"mcafee": 1e-10, "vcg": 0.0, "mitte": 0.0})[0] == "success"                      # unter der Schwelle 1e-9
    kind, text = ev.verdict_lies({"mcafee": 0.5, "vcg": 0.0, "mitte": 1.0})
    assert "McAfee (Handelsreduktion) (bis 0,50)" in text and "Mittelpunktpreis (bis 1,00)" in text


def test_curve_verdict_branches():
    kind, text = ev.verdict_curve("mcafee", 1.987, 1.987, 9.87, 9.87)
    assert kind == "success" and "McAfee (Handelsreduktion): Keine Meldung auf dem Raster" in text and "(9,87, Nutzen 1,987)" in text
    kind, text = ev.verdict_curve("mitte", 3.975, 5.917, 4.0, 9.87)
    assert kind == "warning" and "Mit der Meldung 4,00 statt der wahren 9,87" in text and "von 3,975 auf **5,917**" in text
    assert ev.verdict_curve("vcg", 2.0, 2.0 + 1e-10, 3.0, 5.0)[0] == "success"                                 # Rundungsrauschen zählt nicht


def test_census_verdict():
    c = {"profiles": 400, "lies": {"mcafee": 0, "vcg": 0, "mitte": 352}, "ir_bad": 0, "wbb_bad": 0, "reduced": 201}
    kind, text = ev.verdict_census(c)
    assert kind == "info" and "In 400 Profilen" in text and "bei McAfee in **0**" in text and "bei VCG in **0**" in text and "beim Mittelpunktpreis in **352**" in text
    assert "individuelle Rationalität in 0" in text and "Budgetausgleich in 0 Profilen" in text and "Handelsreduktion in 201 von 400" in text


def test_efficiency_verdict_branches():
    rows = [{"n": 1, "ratio": 0.0, "reduced": 0.508}, {"n": 50, "ratio": 0.9992, "reduced": 0.494}]
    kind, text = ev.verdict_efficiency(rows)
    assert kind == "info" and "0,0 % bei n = 1 und 99,92 % bei n = 50" in text and "handelt McAfee nie" in text and "bei n = 50 bei 49,4 %" in text
    kind, text = ev.verdict_efficiency([{"n": 2, "ratio": 0.7677, "reduced": 0.412}, {"n": 20, "ratio": 0.9954, "reduced": 0.49}])
    assert "76,8 % bei n = 2" in text and "handelt McAfee nie" not in text


def test_table_rows_use_the_rounding_of_the_verdicts():
    c = {"profiles": 400, "lies": {"mcafee": 0, "vcg": 0, "mitte": 352}}
    assert ev.truth_rows(c) == ["| McAfee (Handelsreduktion) | 0 von 400 | 0,0 % |", "| VCG | 0 von 400 | 0,0 % |", "| Mittelpunktpreis | 352 von 400 | 88,0 % |"]
    rows = [{"n": 10, "reduced": 0.4684, "ratio": 0.98364, "loss_n": 0.16364, "loss_n2": 1.6364, "surplus": 0.0656, "vcg_deficit": 0.1004},
            {"n": 50, "reduced": 0.494, "ratio": 0.9992, "loss_n": 0.04, "loss_n2": 2.0, "surplus": 0.0184, "vcg_deficit": None}]
    assert ev.efficiency_rows(rows) == ["| 10 | 46,8 % | 98,36 % | 0,164 | 1,64 | 6,6 % | 10,0 % |", "| 50 | 49,4 % | 99,92 % | 0,040 | 2,00 | 1,8 % | – |"]
    assert ev.hand_rows()[0] == "| A | 2 | 2 | 6,50 | 6,50 | 12,00 von 12,00 | 0,00 | 6,00 / 7,00 | 2,00 |"
    assert ev.hand_rows()[1] == "| B | 3 | 2 | 6,00 | 5,50 | 11,00 von 11,50 | 1,00 | 5,50 / 6,00 | 1,50 |"
    assert ev.hand_rows()[2] == "| C | 2 | 1 | 8,00 | 7,50 | 8,00 von 8,50 | 0,50 | 7,90 / 8,00 | 0,20 |"
