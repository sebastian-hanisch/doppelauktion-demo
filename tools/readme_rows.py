"""Zeilen der README-Tabellen, gerechnet über dieselben Funktionen wie in der App (dau_evaluation) und in der Rundung der App.

`tests/test_claims.py` prüft jede dieser Zeilen gegen die README; `python tools/readme_rows.py` druckt sie zum Einfügen.
Alle Zahlen sind deterministisch (feste Seeds, reine Arithmetik ohne lineare Algebra: auf jedem Rechner dieselben Werte)."""

import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import dau_evaluation as ev  # noqa: E402


@lru_cache(maxsize=None)
def census_result() -> dict:
    return ev.truth_census()


@lru_cache(maxsize=None)
def efficiency_result() -> list:
    return ev.efficiency_table()


def hand_rows() -> list[str]:
    return ev.hand_rows()


def truth_rows() -> list[str]:
    return ev.truth_rows(census_result())


def efficiency_rows() -> list[str]:
    return ev.efficiency_rows(efficiency_result())


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    print("Handbeispiele"); print("\n".join(hand_rows()))
    print("\nFalschangaben"); print("\n".join(truth_rows())); c = census_result(); print({k: v for k, v in c.items() if k != "lies"})
    print("\nEffizienz"); print("\n".join(efficiency_rows()))
    a = ev.analyse(ev.Settings()); o = a.outcomes["mcafee"]
    print("\nStandardmarkt: k", o.k, "t", o.t, "p0", o.p0, "Wohlfahrt", round(o.welfare, 3), "von", round(a.max_welfare, 3), "Überschuss", round(o.surplus, 3), "VCG-Defizit", round(-a.outcomes["vcg"].surplus, 3),
          "Lügen", {m: round(g, 3) for m, g in a.gains.items()})
    print("tempted:", ev.tempted_agent(a.market.b, a.market.s), "b", a.market.b.round(2).tolist(), "s", a.market.s.round(2).tolist())
