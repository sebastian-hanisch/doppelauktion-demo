"""Gemeinsame Fixtures: die Mini-Märkte, an denen jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


@pytest.fixture
def hand_a():
    """Käufer (10; 8; 6), Verkäufer (2; 4; 7): k = 2, p0 = (6 + 7)/2 = 6,5 liegt in [4; 8]: beide Paare handeln zu 6,5, Wohlfahrt 12 von 12, Überschuss 0;
    VCG: Käufer zahlen max(s_(2), b_(3)) = 6, Verkäufer erhalten min(b_(2), s_(3)) = 7, Defizit 2 (2 Paare mal 1)."""
    return [10.0, 8.0, 6.0], [2.0, 4.0, 7.0]


@pytest.fixture
def hand_b():
    """Käufer (10; 8; 6), Verkäufer (2; 5; 5,5): k = 3, kein Rang 4 für p0: Reduktion, zwei Paare handeln, Käufer zahlen 6, Verkäufer erhalten 5,5, Überschuss 2 mal 0,5 = 1,
    Wohlfahrt 11 von 11,5; VCG: 3 Paare, Käufer zahlen max(5,5; -inf) = 5,5, Verkäufer erhalten min(6; inf) = 6, Defizit 3 mal 0,5 = 1,5."""
    return [10.0, 8.0, 6.0], [2.0, 5.0, 5.5]


@pytest.fixture
def hand_c():
    """Käufer (10; 8; 7,9), Verkäufer (2; 7,5; 9,5): k = 2, p0 = (7,9 + 9,5)/2 = 8,7 liegt über b_(2) = 8: Reduktion, ein Paar handelt, Käufer zahlt 8, Verkäufer erhält 7,5, Überschuss 0,5,
    Wohlfahrt 8 von 8,5; VCG: Käufer zahlen max(7,5; 7,9) = 7,9, Verkäufer erhalten min(8; 9,5) = 8, Defizit 2 mal 0,1 = 0,2."""
    return [10.0, 8.0, 7.9], [2.0, 7.5, 9.5]
