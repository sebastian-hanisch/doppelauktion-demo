"""Konstanten: Regler-Grenzen, feste Annahmen, Farben und Presets."""

MARKETS = ("zufall", "hand_a", "hand_b", "hand_c")
MARKET_LABEL = {"zufall": "Zufallsmarkt (Regler unten)", "hand_a": "Handbeispiel A: alle k Paare handeln", "hand_b": "Handbeispiel B: kein p₀, ein Paar wird gestrichen",
                "hand_c": "Handbeispiel C: p₀ außerhalb, ein Paar wird gestrichen"}
VALUE_KINDS = ("stetig", "raster")
VALUE_LABEL = {"stetig": "stetige Werte", "raster": "Raster 0,5 (viele Gleichstände)"}
MECHS = ("mcafee", "vcg", "mitte")
MECH_LABEL = {"mcafee": "McAfee (Handelsreduktion)", "vcg": "VCG", "mitte": "Mittelpunktpreis"}

# Regler. Komplexität am Maximum: Ein Mechanismus ist Sortieren und Summieren (n <= 12 je Seite: Mikrosekunden); die Nutzenkurve ruft ihn UTIL_GRID mal auf; die Zählung über Profile rechnet
# TRUTH_PROFILES Profile mit je (Teilnehmer x Abweichungsraster) Aufrufen für drei Mechanismen; die Effizienztabelle ist vektorisiert (Worst-Case-Test in tests/test_edge_cases.py).
NB_MIN, NB_MAX, DEFAULT_NB = 1, 12, 5
NS_MIN, NS_MAX, DEFAULT_NS = 1, 12, 5
SEED_MAX, DEFAULT_SEED = 999999, 8
DEFAULT_MARKET, DEFAULT_KIND = "zufall", "stetig"
VALUE_SCALE = 10.0              # Werte und Kosten sind gleichverteilt auf [0, VALUE_SCALE]
RASTER_STEP = 0.5

HAND = {
    "hand_a": ((10.0, 8.0, 6.0), (2.0, 4.0, 7.0)),
    "hand_b": ((10.0, 8.0, 6.0), (2.0, 5.0, 5.5)),
    "hand_c": ((10.0, 8.0, 7.9), (2.0, 7.5, 9.5)),
}

UTIL_STEP = 0.25                # Abweichungsraster der Falschangaben (Nutzenkurve und Zählung)
UTIL_MAX = 12.0
GAIN_TOL = 1e-9                 # ein Abweichungsgewinn darunter zählt nicht

# Zählungen über feste Instanzen (DEMO-PLAYBOOK §4: nie ein einzelner Seed)
TRUTH_PROFILES, TRUTH_SEED = 400, 4        # Profile mit 3 bis 4 Käufern und 3 bis 4 Verkäufern, Werte auf dem Raster 0,5
EFF_NS = (1, 2, 3, 5, 10, 20, 50)
EFF_TRIALS, EFF_SEED = 5000, 8             # Instanzen je Marktgröße, n Käufer und n Verkäufer, Werte und Kosten gleichverteilt auf [0, 1]
EFF_VCG_MAX_N = 20                         # das VCG-Defizit wird bis zu dieser Größe mitgerechnet

COLOR_BUY = "#2F6B65"
COLOR_SELL = "#c0392b"
COLOR_TRADE = "#7a6aa8"
COLOR_PRICE = "#e08a2c"
COLOR_MECH = {"mcafee": "#2F6B65", "vcg": "#4c78a8", "mitte": "#c0392b"}

PRESETS = {
    "Standardfall (Voreinstellung)": {"market": DEFAULT_MARKET, "kind": DEFAULT_KIND, "nb": DEFAULT_NB, "ns": DEFAULT_NS, "seed": DEFAULT_SEED},
    "Handbeispiel A: alle Paare handeln": {"market": "hand_a", "kind": DEFAULT_KIND, "nb": DEFAULT_NB, "ns": DEFAULT_NS, "seed": 1},
    "Handbeispiel B: ein Paar wird gestrichen": {"market": "hand_b", "kind": DEFAULT_KIND, "nb": DEFAULT_NB, "ns": DEFAULT_NS, "seed": 1},
    "Handbeispiel C: p₀ außerhalb": {"market": "hand_c", "kind": DEFAULT_KIND, "nb": DEFAULT_NB, "ns": DEFAULT_NS, "seed": 1},
    "Ein Käufer, ein Verkäufer: nie Handel": {"market": DEFAULT_MARKET, "kind": DEFAULT_KIND, "nb": 1, "ns": 1, "seed": 0},
    "Gleichstände: Raster 0,5": {"market": DEFAULT_MARKET, "kind": "raster", "nb": 8, "ns": 8, "seed": DEFAULT_SEED},
}
PRESET_HELP = {
    "Standardfall (Voreinstellung)": "Fünf Spediteure kaufen, fünf Betriebe verkaufen Ladeslots: McAfee handelt höchstens ein Paar weniger als effizient wäre.",
    "Handbeispiel A: alle Paare handeln": "Käufer (10; 8; 6), Verkäufer (2; 4; 7): Der Preis p₀ = 6,5 liegt im Bereich, alle zwei Paare handeln zu 6,5, nichts geht verloren.",
    "Handbeispiel B: ein Paar wird gestrichen": "Käufer (10; 8; 6), Verkäufer (2; 5; 5,5): Drei Paare wären effizient, aber es gibt keinen vierten Käufer für p₀: Ein Paar wird gestrichen, die Börse behält einen Überschuss.",
    "Handbeispiel C: p₀ außerhalb": "Käufer (10; 8; 7,9), Verkäufer (2; 7,5; 9,5): p₀ = 8,7 liegt über dem Gebot 8 des zweiten Käufers: Nur ein Paar handelt.",
    "Ein Käufer, ein Verkäufer: nie Handel": "Der Fall der Vorgängerdemo: Mit einem Paar gibt es keinen Rang k + 1, jeder Handel wird gestrichen; wahrhaftig und ausgeglichen, aber es wird nichts gehandelt.",
    "Gleichstände: Raster 0,5": "Werte und Kosten auf einem Raster von 0,5: Viele Gebote sind gleich, die Mechanismen entscheiden nach Index; McAfee bleibt wahrhaftig.",
}
