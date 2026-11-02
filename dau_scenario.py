"""Szenario: synthetische Slot-Börsen (nur numpy). Zufall nur über den übergebenen Generator, nie über `hash()`.

Vehikel: Auf einer Slot-Börse kaufen Spediteure Ladeslots (Wert b_i je Slot) und Betriebe verkaufen sie (Kosten s_j je Slot); jeder höchstens einen. Keine Personen-, Firmen- oder Börsendaten."""

from dataclasses import dataclass

import numpy as np

import dau_constants as C


@dataclass(frozen=True, eq=False)
class Market:
    b: np.ndarray       # Werte der Käufer (nb)
    s: np.ndarray       # Kosten der Verkäufer (ns)

    @property
    def nb(self) -> int:
        return len(self.b)

    @property
    def ns(self) -> int:
        return len(self.s)


def draw(kind: str, count: int, rng: np.random.Generator) -> np.ndarray:
    """Werte auf [0, VALUE_SCALE], stetig oder auf dem Raster RASTER_STEP (dann viele Gleichstände)."""
    x = rng.random(count) * C.VALUE_SCALE
    if kind == "raster":
        x = np.round(x / C.RASTER_STEP) * C.RASTER_STEP
    elif kind != "stetig":
        raise ValueError(f"unbekannte Erzeugerart {kind!r}")
    return x


def make_market(market: str, kind: str, nb: int, ns: int, seed: int) -> Market:
    """Deterministisch aus (market, kind, nb, ns, seed): gleiche Eingabe, gleicher Markt; Handbeispiele sind fest."""
    if market in C.HAND:
        b, s = C.HAND[market]
        return Market(np.array(b, dtype=float), np.array(s, dtype=float))
    if market != "zufall":
        raise ValueError(f"unbekannter Markt {market!r}")
    rng = np.random.default_rng(seed)
    return Market(draw(kind, nb, rng), draw(kind, ns, rng))
