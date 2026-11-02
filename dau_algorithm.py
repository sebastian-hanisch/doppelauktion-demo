"""Kern: Doppelauktion mit Einheitsnachfrage und -angebot (nur numpy).

nb Käufer mit Werten b_i, ns Verkäufer mit Kosten s_j. Sortiert: Käufer absteigend, Verkäufer aufsteigend (Gleichstand: kleinerer Index zuerst). k = größtes j mit b_(j) >= s_(j) ist die
effiziente Handelszahl. McAfee: p0 = (b_(k+1) + s_(k+1)) / 2 (falls beide Ränge existieren); liegt p0 in [s_(k), b_(k)], handeln alle k Paare zum Preis p0, sonst k - 1 Paare:
Käufer zahlen b_(k), Verkäufer erhalten s_(k), die Börse behält b_(k) - s_(k) je Paar."""

from dataclasses import dataclass

import numpy as np

import dau_constants as C


@dataclass(frozen=True, eq=False)
class Outcome:
    k: int                  # effiziente Handelszahl
    t: int                  # tatsächliche Handelszahl
    buyers: list            # handelnde Käufer (Indizes)
    sellers: list           # handelnde Verkäufer
    pb: float               # Preis für Käufer
    ps: float               # Preis für Verkäufer
    ub: np.ndarray          # Nutzen je Käufer (wahre Werte)
    us: np.ndarray          # Nutzen je Verkäufer
    welfare: float          # Summe b - s der Handelnden
    p0: float | None        # Mittelpunkt der ersten ausgeschlossenen Gebote (McAfee), sonst None
    reduced: bool           # ein Paar wurde gestrichen

    @property
    def surplus(self) -> float:
        """Überschuss der Börse (negativ = Defizit): Zahlungen der Käufer minus Auszahlungen an die Verkäufer."""
        return self.t * (self.pb - self.ps)


def order(b, s):
    bo = sorted(range(len(b)), key=lambda i: (-b[i], i))
    so = sorted(range(len(s)), key=lambda j: (s[j], j))
    return bo, so


def efficient_k(b, s):
    bo, so = order(b, s)
    k = 0
    while k < min(len(b), len(s)) and b[bo[k]] >= s[so[k]]:
        k += 1
    return k, bo, so


def max_welfare(b, s) -> float:
    k, bo, so = efficient_k(b, s)
    return float(sum(b[bo[i]] - s[so[i]] for i in range(k)))


def _outcome(b, s, k, t, buyers, sellers, pb, ps, p0, reduced) -> Outcome:
    ub, us = np.zeros(len(b)), np.zeros(len(s))
    for i in buyers:
        ub[i] = b[i] - pb
    for j in sellers:
        us[j] = ps - s[j]
    return Outcome(k, t, list(buyers), list(sellers), float(pb), float(ps), ub, us, float(sum(b[i] for i in buyers) - sum(s[j] for j in sellers)), p0, reduced)


def mcafee(b, s) -> Outcome:
    b, s = [float(x) for x in b], [float(x) for x in s]
    k, bo, so = efficient_k(b, s)
    if k == 0:
        return _outcome(b, s, 0, 0, [], [], 0.0, 0.0, None, False)
    p0 = 0.5 * (b[bo[k]] + s[so[k]]) if k < len(b) and k < len(s) else None
    if p0 is not None and s[so[k - 1]] <= p0 <= b[bo[k - 1]]:
        return _outcome(b, s, k, k, bo[:k], so[:k], p0, p0, p0, False)
    return _outcome(b, s, k, k - 1, bo[:k - 1], so[:k - 1], b[bo[k - 1]], s[so[k - 1]], p0, True)


def vcg(b, s) -> Outcome:
    """VCG: alle k Paare handeln, Käufer zahlen ihre Externalität max(s_(k), b_(k+1)), Verkäufer erhalten min(b_(k), s_(k+1)); die Börse hat ein Defizit."""
    b, s = [float(x) for x in b], [float(x) for x in s]
    k, bo, so = efficient_k(b, s)
    if k == 0:
        return _outcome(b, s, 0, 0, [], [], 0.0, 0.0, None, False)
    pb = max(s[so[k - 1]], b[bo[k]] if k < len(b) else -np.inf)
    ps = min(b[bo[k - 1]], s[so[k]] if k < len(s) else np.inf)
    return _outcome(b, s, k, k, bo[:k], so[:k], pb, ps, None, False)


def midpoint(b, s) -> Outcome:
    """Alle k Paare handeln zum Mittelpunkt (b_(k) + s_(k)) / 2: effizient und ausgeglichen, aber nicht wahrhaftig."""
    b, s = [float(x) for x in b], [float(x) for x in s]
    k, bo, so = efficient_k(b, s)
    if k == 0:
        return _outcome(b, s, 0, 0, [], [], 0.0, 0.0, None, False)
    p = 0.5 * (b[bo[k - 1]] + s[so[k - 1]])
    return _outcome(b, s, k, k, bo[:k], so[:k], p, p, None, False)


MECH_FUNCS = {"mcafee": mcafee, "vcg": vcg, "mitte": midpoint}


def utility_reporting(mech: str, b, s, side: str, idx: int, x: float) -> float:
    """Nutzen eines Teilnehmers (side 'b' Käufer / 's' Verkäufer) mit seinem WAHREN Wert b[idx] bzw. s[idx], wenn er stattdessen x meldet (die anderen melden wahr)."""
    bb, ss = list(b), list(s)
    if side == "b":
        bb[idx] = x
        out = MECH_FUNCS[mech](bb, ss)
        return float(b[idx] - out.pb) if idx in out.buyers else 0.0
    ss[idx] = x
    out = MECH_FUNCS[mech](bb, ss)
    return float(out.ps - s[idx]) if idx in out.sellers else 0.0


def utility_curve(mech: str, b, s, side: str, idx: int, grid) -> np.ndarray:
    return np.array([utility_reporting(mech, b, s, side, idx, float(x)) for x in grid])


def best_gain(mech: str, b, s, side: str, idx: int, grid) -> float:
    """Größter Gewinn durch Falschangabe auf `grid` gegenüber der wahren Angabe (0 = Wahrheit ist unter diesen Abweichungen am besten)."""
    truth = utility_reporting(mech, b, s, side, idx, float((b if side == "b" else s)[idx]))
    return max(0.0, float(utility_curve(mech, b, s, side, idx, grid).max()) - truth)


def max_gain(mech: str, b, s, grid) -> float:
    """Größter Gewinn irgendeines Teilnehmers durch Falschangabe."""
    return max([best_gain(mech, b, s, "b", i, grid) for i in range(len(b))] + [best_gain(mech, b, s, "s", j, grid) for j in range(len(s))])


# --- Vektorisierte Fassung für viele Instanzen ---------------------------------------------------------------------------------------------

def batch(B: np.ndarray, S: np.ndarray) -> dict:
    """McAfee, Maximum und VCG für T Instanzen zugleich (B: T x nb, S: T x ns, beliebig angeordnet). Nur Summen sortierter Werte: Gleichstände ändern die Zahlen nicht.
    Rückgabe (je Instanz): k, t, reduced, welfare (McAfee), max_welfare, surplus (McAfee), vcg_deficit (>= 0)."""
    Bs = -np.sort(-B, axis=1)
    Ss = np.sort(S, axis=1)
    T, nb = Bs.shape
    ns = Ss.shape[1]
    m = min(nb, ns)
    gain = Bs[:, :m] - Ss[:, :m]
    k = (gain >= 0).sum(axis=1)                              # b fällt, s steigt: die Bedingung gilt auf einem Anfangsstück
    rows = np.arange(T)
    cum = np.concatenate([np.zeros((T, 1)), np.cumsum(gain, axis=1)], axis=1)
    wmax = cum[rows, k]
    has_next = (k < nb) & (k < ns)
    p0 = 0.5 * (Bs[rows, np.minimum(k, nb - 1)] + Ss[rows, np.minimum(k, ns - 1)])
    kk = np.maximum(k - 1, 0)
    bk, sk = Bs[rows, kk], Ss[rows, kk]
    inside = has_next & (sk <= p0) & (p0 <= bk)
    reduced = (k > 0) & ~inside
    t = k - reduced
    welfare = cum[rows, t]
    surplus = np.where(reduced, (k - 1) * (bk - sk), 0.0)
    pb_v = np.maximum(sk, np.where(k < nb, Bs[rows, np.minimum(k, nb - 1)], -np.inf))
    ps_v = np.minimum(bk, np.where(k < ns, Ss[rows, np.minimum(k, ns - 1)], np.inf))
    deficit = np.where(k > 0, k * (ps_v - pb_v), 0.0)
    return {"k": k, "t": t, "reduced": reduced, "welfare": welfare, "max_welfare": wmax, "surplus": surplus, "vcg_deficit": deficit}
