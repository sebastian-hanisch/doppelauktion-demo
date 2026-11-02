"""Kennzahlen, Verdikt-Logik und Zählungen (Komposition der Regeln aus `dau_algorithm.py`; Verdikte sind reine Funktionen)."""

from dataclasses import dataclass

import numpy as np

import dau_algorithm as A
import dau_constants as C
from dau_scenario import Market, draw, make_market


@dataclass(frozen=True)
class Settings:
    market: str = C.DEFAULT_MARKET
    kind: str = C.DEFAULT_KIND
    nb: int = C.DEFAULT_NB
    ns: int = C.DEFAULT_NS
    seed: int = C.DEFAULT_SEED


@dataclass(frozen=True, eq=False)
class Analysis:
    market: Market
    outcomes: dict              # Mechanismus -> Outcome
    max_welfare: float
    gains: dict                 # Mechanismus -> größter Gewinn eines Teilnehmers durch Falschangabe in diesem Markt

    @property
    def k(self) -> int:
        return self.outcomes["mcafee"].k


def grid() -> np.ndarray:
    return np.arange(0.0, C.UTIL_MAX + 1e-9, C.UTIL_STEP)


def tempted_agent(b, s) -> int:
    """Index (Käufer zuerst, dann Verkäufer) des Teilnehmers mit dem größten Gewinn durch Falschangabe bei irgendeinem Mechanismus; ohne lohnende Falschangabe 0."""
    g = grid()
    best, who = C.GAIN_TOL, 0
    for i in range(len(b)):
        for m in C.MECHS:
            v = A.best_gain(m, b, s, "b", i, g)
            if v > best:
                best, who = v, i
    for j in range(len(s)):
        for m in C.MECHS:
            v = A.best_gain(m, b, s, "s", j, g)
            if v > best:
                best, who = v, len(b) + j
    return who


def analyse(settings: Settings) -> Analysis:
    mk = make_market(settings.market, settings.kind, settings.nb, settings.ns, settings.seed)
    outs = {m: A.MECH_FUNCS[m](mk.b, mk.s) for m in C.MECHS}
    g = grid()
    return Analysis(mk, outs, A.max_welfare(mk.b, mk.s), {m: A.max_gain(m, mk.b, mk.s, g) for m in C.MECHS})


# --- Verdikte als reine Funktionen -------------------------------------------------------------------------------------------------------

def _num(v: float, d: int = 2) -> str:
    return f"{v:.{d}f}".replace(".", ",")


def _pct(v: float, d: int = 1) -> str:
    return _num(100.0 * v, d)


def verdict_market(k: int, t: int, reduced: bool, p0: float | None, welfare: float, max_welfare: float, surplus: float) -> tuple[str, str]:
    """Kernfrage: Wie viel Handel verliert McAfee gegen den effizienten? k = effiziente Handelszahl, t = tatsächliche."""
    if k == 0:
        return "info", "Kein Käufer will mehr zahlen, als irgendein Verkäufer verlangt: Es gibt keinen Handel, der sich lohnt (k = 0)."
    if not reduced:
        return "success", (f"Alle k = {k} effizienten Paare handeln zum Preis p₀ = {_num(p0)}: Wohlfahrt {_num(welfare)} von {_num(max_welfare)}, kein Verlust, Überschuss der Börse {_num(surplus)}.")
    why = "es gibt keinen Rang k + 1 auf einer der Seiten, also keinen Preis p₀" if p0 is None else f"p₀ = {_num(p0)} liegt nicht zwischen dem Verkäufer- und dem Käufer-Grenzgebot"
    return "warning", (f"Von k = {k} effizienten Paaren handeln nur {t}: {why}, das am wenigsten wertvolle Paar wird gestrichen. Wohlfahrt {_num(welfare)} von {_num(max_welfare)} "
                      f"(Verlust {_num(max_welfare - welfare)}), die Börse behält {_num(surplus)}.")


def verdict_lies(gains: dict) -> tuple[str, str]:
    """Wahrhaftigkeit in diesem Markt: Für welche Mechanismen lohnt sich irgendeine Falschangabe (Raster der Abweichungen)?"""
    paying = [m for m in C.MECHS if gains[m] > C.GAIN_TOL]
    if not paying:
        return "success", "In diesem Markt lohnt sich für keinen Teilnehmer eine Falschangabe, bei keinem der drei Mechanismen."
    names = ", ".join(f"{C.MECH_LABEL[m]} (bis {_num(gains[m])})" for m in paying)
    return "warning", f"Eine Falschangabe lohnt sich bei: {names}. Bei den übrigen Mechanismen ist Wahrheit die beste Antwort."


def verdict_curve(mech: str, truth_u: float, best_u: float, best_x: float, true_x: float) -> tuple[str, str]:
    """Nutzenkurve eines Teilnehmers über seine Meldung: wahrer Nutzen gegen den besten Nutzen auf dem Raster."""
    if best_u <= truth_u + C.GAIN_TOL:
        return "success", f"{C.MECH_LABEL[mech]}: Keine Meldung auf dem Raster ist besser als die wahre ({_num(true_x)}, Nutzen {_num(truth_u, 3)})."
    return "warning", f"{C.MECH_LABEL[mech]}: Mit der Meldung {_num(best_x)} statt der wahren {_num(true_x)} steigt der Nutzen von {_num(truth_u, 3)} auf **{_num(best_u, 3)}**."


def verdict_census(c: dict) -> tuple[str, str]:
    """Zählung über Zufallsprofile: Falschangaben je Mechanismus, Verstöße von McAfee, Anteil der Reduktion."""
    n = c["profiles"]
    return "info", (f"In {n} Profilen lohnt sich eine Falschangabe bei McAfee in **{c['lies']['mcafee']}**, bei VCG in **{c['lies']['vcg']}**, beim Mittelpunktpreis in **{c['lies']['mitte']}**. "
                    f"McAfee verletzt die individuelle Rationalität in {c['ir_bad']}, den schwachen Budgetausgleich in {c['wbb_bad']} Profilen; Handelsreduktion in {c['reduced']} von {n} Profilen.")


def verdict_efficiency(rows: list[dict]) -> tuple[str, str]:
    """Effizienz über die Marktgröße: Wohlfahrt gegen das Maximum bei der kleinsten und der größten Marktgröße, Fall n = 1."""
    first, last = rows[0], rows[-1]
    head = f"Wohlfahrt gegen das Maximum: {_pct(first['ratio'])} % bei n = {first['n']} und {_pct(last['ratio'], 2)} % bei n = {last['n']}."
    if first["n"] == 1:
        head += " Mit einem Käufer und einem Verkäufer handelt McAfee nie (jeder Handel wird gestrichen)."
    return "info", head + f" Der Anteil der Instanzen mit Handelsreduktion liegt bei n = {last['n']} bei {_pct(last['reduced'])} %."


# --- Handbeispiele, Zählungen über feste Instanzen ------------------------------------------------------------------------------------------------

def hand_rows() -> list[str]:
    """Zeilen der Handbeispiel-Tabelle (McAfee gegen VCG); App und README rechnen dieselben."""
    rows = []
    for key in ("hand_a", "hand_b", "hand_c"):
        mk = make_market(key, "stetig", 0, 0, 0)
        o, v = A.mcafee(mk.b, mk.s), A.vcg(mk.b, mk.s)
        rows.append(f"| {key[-1].upper()} | {o.k} | {o.t} | {_num(o.pb)} | {_num(o.ps)} | {_num(o.welfare)} von {_num(A.max_welfare(mk.b, mk.s))} | {_num(o.surplus)} | {_num(v.pb)} / {_num(v.ps)} | {_num(-v.surplus)} |")
    return rows


def truth_census(profiles: int = C.TRUTH_PROFILES, seed: int = C.TRUTH_SEED) -> dict:
    """Zufallsprofile mit 3 bis 4 Käufern und 3 bis 4 Verkäufern (Werte auf dem Raster 0,5 in [0, 10], also mit Gleichständen): Anteil mit lohnender Falschangabe je Mechanismus,
    Verstöße von McAfee gegen individuelle Rationalität und schwachen Budgetausgleich, Abweichung des Verlusts vom gestrichenen Paar, Wohlfahrt unter (1 - 1/k) Maximum, Zahl der Reduktionen."""
    rng = np.random.default_rng(seed)
    g = grid()
    lies = {m: 0 for m in C.MECHS}
    mid_gains, deficits = [], []
    ir_bad = wbb_bad = loss_bad = bound_bad = reduced = 0
    for _ in range(profiles):
        nb, ns = int(rng.integers(3, 5)), int(rng.integers(3, 5))
        b, s = list(draw("raster", nb, rng)), list(draw("raster", ns, rng))
        o = A.mcafee(b, s)
        ir_bad += bool((o.ub < -1e-12).any() or (o.us < -1e-12).any())
        wbb_bad += o.surplus < -1e-12
        wmax = A.max_welfare(b, s)
        loss = wmax - o.welfare
        if o.reduced:
            reduced += 1
            bo, so = A.order(b, s)
            loss_bad += abs(loss - (b[bo[o.k - 1]] - s[so[o.k - 1]])) > 1e-9
        else:
            loss_bad += abs(loss) > 1e-9
        if o.k > 0:
            bound_bad += o.welfare < (1 - 1 / o.k) * wmax - 1e-9
        deficits.append(-A.vcg(b, s).surplus)
        for m in C.MECHS:
            gain = A.max_gain(m, b, s, g)
            if gain > C.GAIN_TOL:
                lies[m] += 1
                if m == "mitte":
                    mid_gains.append(gain)
    return {"profiles": profiles, "lies": lies, "ir_bad": int(ir_bad), "wbb_bad": int(wbb_bad), "loss_bad": int(loss_bad), "bound_bad": int(bound_bad), "reduced": reduced,
            "mid_gain_median": float(np.median(mid_gains)) if mid_gains else 0.0, "mid_gain_max": max(mid_gains) if mid_gains else 0.0, "vcg_deficit_median": float(np.median(deficits))}


def efficiency_table(ns=C.EFF_NS, trials: int = C.EFF_TRIALS, seed: int = C.EFF_SEED, vcg_max_n: int = C.EFF_VCG_MAX_N) -> list[dict]:
    """Je Marktgröße n (n Käufer, n Verkäufer, Werte und Kosten unabhängig gleichverteilt auf [0, 1]): Anteil der Reduktion, Wohlfahrt / Maximum (Verhältnis der Mittelwerte),
    Verlust mal n und mal n², Überschuss der Börse und VCG-Defizit relativ zum Maximum, mittlere Handelszahl gegen die effiziente."""
    rows = []
    for n in ns:
        rng = np.random.default_rng(seed + n)
        r = A.batch(rng.random((trials, n)), rng.random((trials, n)))
        wmax = float(r["max_welfare"].sum())
        ratio = float(r["welfare"].sum()) / wmax if wmax > 0 else float("nan")
        loss = 1.0 - ratio
        rows.append({"n": n, "trials": trials, "reduced": float(r["reduced"].mean()), "ratio": ratio, "loss_n": loss * n, "loss_n2": loss * n * n, "surplus": float(r["surplus"].sum()) / wmax,
                     "vcg_deficit": float(r["vcg_deficit"].sum()) / wmax if n <= vcg_max_n else None, "t": float(r["t"].mean()), "k": float(r["k"].mean())})
    return rows


def truth_rows(c: dict) -> list[str]:
    """Zeilen der Wahrhaftigkeits-Tabelle (App und README rechnen dieselben)."""
    n = c["profiles"]
    return [f"| {C.MECH_LABEL[m]} | {c['lies'][m]} von {n} | {_pct(c['lies'][m] / n)} % |" for m in C.MECHS]


def efficiency_rows(rows: list[dict]) -> list[str]:
    """Zeilen der Effizienz-Tabelle (App und README rechnen dieselben)."""
    out = []
    for r in rows:
        deficit = "–" if r["vcg_deficit"] is None else f"{_pct(r['vcg_deficit'])} %"
        out.append(f"| {r['n']} | {_pct(r['reduced'])} % | {_pct(r['ratio'], 2)} % | {_num(r['loss_n'], 3)} | {_num(r['loss_n2'], 2)} | {_pct(r['surplus'])} % | {deficit} |")
    return out
