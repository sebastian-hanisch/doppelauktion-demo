"""Doppelauktion mit Handelsreduktion - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 4 der Reihe „Marktmechanismen“: Auf einer Slot-Börse kaufen Spediteure und verkaufen Betriebe Ladeslots, beide Seiten kennen nur ihren eigenen Wert. McAfees Mechanismus streicht bei Bedarf das am wenigsten
wertvolle Paar und ist dafür wahrhaftig (in dominanten Strategien), individuell rational und ausgeglichen; die Demo misst, wie viel Effizienz das kostet und wie schnell der Verlust mit der Marktgröße schwindet.

Lauffähig mit: streamlit run app.py
"""

import numpy as np
import streamlit as st

import dau_algorithm as A
import dau_constants as C
from dau_evaluation import (
    Settings,
    analyse,
    efficiency_rows,
    efficiency_table,
    grid,
    hand_rows,
    tempted_agent,
    truth_census,
    truth_rows,
    verdict_census,
    verdict_curve,
    verdict_efficiency,
    verdict_lies,
    verdict_market,
)
from dau_layout import dunkles_design, kopf_css
from dau_presets import (
    bounds,
    init_session_state_defaults,
    load_permalink_settings,
    randomize_seed,
    sidebar_presets,
    sync_query_params,
)
from dau_visualization import build_efficiency, build_market, build_utility_curves

st.set_page_config(page_title="Doppelauktion – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner="Rechne die drei Mechanismen und prüfe alle Falschangaben …")
def _analysis(settings):
    return analyse(settings)


@st.cache_data(show_spinner=False)
def _hand():
    return hand_rows()


@st.cache_data(show_spinner="Zähle Falschangaben über 400 Zufallsprofile (einige Sekunden) …")
def _census():
    return truth_census()


@st.cache_data(show_spinner="Rechne die Effizienz für sieben Marktgrößen …")
def _efficiency():
    return efficiency_table()


def _de(v, d=2):
    return f"{v:.{d}f}".replace(".", ",")


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in dau_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("⚖️ Doppelauktion mit Handelsreduktion")
st.markdown(
    """
Auf einer **Slot-Börse** kaufen Spediteure und verkaufen Betriebe Ladeslots; jeder höchstens einen, und jeder kennt nur seinen eigenen Wert (Käufer) oder seine Kosten (Verkäufer). Die Vorgängerdemo `myerson-satterthwaite-demo` zeigt für **einen** Käufer und
**einen** Verkäufer: Nichts ist zugleich effizient, ehrlich, freiwillig und ausgeglichen. **McAfees Mechanismus** gibt bei vielen Teilnehmern die Effizienz nur ein kleines Stück auf: Er **streicht bei Bedarf das am wenigsten wertvolle Paar** und
ist dafür **wahrhaftig** (in dominanten Strategien), **individuell rational** und **ausgeglichen** (die Börse macht nie Verlust). Die Demo prüft das an jeder Einzelabweichung und misst, wie viel Handel verloren geht und wie schnell das mit der Marktgröße schwindet.
Viertes Stück der Reihe **Marktmechanismen**; alle Märkte sind synthetisch, es gibt keine Börsendaten.

Weiter unten: zwei Abschnitte **🔬 Experiment**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So funktioniert der Mechanismus", expanded=True):
    st.markdown(
        """
1. **Sortieren.** Käufer absteigend nach Wert, Verkäufer aufsteigend nach Kosten. $k$ ist die größte Zahl, für die der $k$-te Käufer noch mindestens so viel bietet, wie der $k$-te Verkäufer verlangt: So viele Paare würden effizient handeln.
2. **Der Preis $p_0$.** Der Mittelpunkt zwischen dem $(k+1)$-ten Käufer und dem $(k+1)$-ten Verkäufer, den beiden ersten, die nicht mehr handeln würden.
3. **Liegt $p_0$ im Bereich** zwischen den Grenzgeboten des $k$-ten Paares, handeln **alle $k$ Paare zu $p_0$**: Käufer zahlen $p_0$, Verkäufer erhalten $p_0$, nichts geht verloren.
4. **Sonst** handeln nur **$k-1$ Paare**: Die Käufer zahlen das Gebot des $k$-ten Käufers, die Verkäufer erhalten die Kosten des $k$-ten Verkäufers; die Börse behält den Unterschied. Der Preis hängt dann von keinem Handelnden ab, deshalb lohnt sich Lügen nicht.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    market = st.radio("Markt", C.MARKETS, key="market_radio", format_func=lambda k: C.MARKET_LABEL[k], help="Ein Zufallsmarkt mit den Reglern unten oder eines der drei Handbeispiele.")
    is_random = market == "zufall"
    kind = st.radio("Werte", C.VALUE_KINDS, key="kind_radio", format_func=lambda k: C.VALUE_LABEL[k], disabled=not is_random, help="Stetige Zufallswerte oder ein Raster von 0,5 (viele gleiche Gebote).")
    nb = st.slider("Käufer", *bounds("nb_slider"), key="nb_slider", disabled=not is_random, help="Wie viele Spediteure kaufen wollen.")
    ns = st.slider("Verkäufer", *bounds("ns_slider"), key="ns_slider", disabled=not is_random, help="Wie viele Betriebe verkaufen wollen.")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1, disabled=not is_random, help="Bestimmt Werte und Kosten des Zufallsmarktes.")
    if not is_random:
        st.caption("Die Regler gelten nur für den Zufallsmarkt; das Handbeispiel ist fest.")
    st.button("🎲 Neuer Markt", width="stretch", on_click=randomize_seed, disabled=not is_random)

sync_query_params({"market_radio": market, "kind_radio": kind, "nb_slider": int(nb), "ns_slider": int(ns), "seed_input": int(seed)})

settings = Settings(market, kind, int(nb), int(ns), int(seed))
a = _analysis(settings)
mk = a.market
mc, vc, mid = a.outcomes["mcafee"], a.outcomes["vcg"], a.outcomes["mitte"]

# --- Ergebnis ------------------------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Ergebnis")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Effiziente Handelszahl k", f"{mc.k}", delta=f"{mk.nb} Käufer, {mk.ns} Verkäufer", delta_color="off")
m2.metric("McAfee handelt", f"{mc.t} {'Paar' if mc.t == 1 else 'Paare'}", delta="eines gestrichen" if mc.reduced else "keines gestrichen", delta_color="off")
m3.metric("Wohlfahrt", f"{_de(100 * mc.welfare / a.max_welfare, 1)} %" if a.max_welfare > 0 else "–", delta=f"{_de(mc.welfare)} von {_de(a.max_welfare)}", delta_color="off")
m4.metric("Überschuss der Börse", _de(mc.surplus), delta=f"VCG: Defizit {_de(-vc.surplus)}", delta_color="off")
st.plotly_chart(build_market(mk.b, mk.s, mc), width="stretch", key="main_chart")
st.caption("Nachfrage (grün, absteigend) und Angebot (rot, aufsteigend) als Treppen über den Rang; gefüllte Punkte handeln bei McAfee, hohle nicht. Wo die Treppen sich kreuzen, ist die effiziente Handelszahl k; die gestrichelten Linien sind die Preise.")
rows = ["| Mechanismus | Handelszahl | Käufer zahlen | Verkäufer erhalten | Wohlfahrt | Überschuss der Börse | wahrhaftig in diesem Markt? |", "|---|---|---|---|---|---|---|"]
for m in C.MECHS:
    o = a.outcomes[m]
    rows.append(f"| {C.MECH_LABEL[m]} | {o.t} | {_de(o.pb)} | {_de(o.ps)} | {_de(o.welfare)} | {_de(o.surplus)} | {'ja' if a.gains[m] <= C.GAIN_TOL else f'nein (Gewinn bis {_de(a.gains[m])})'} |")
st.markdown("\n".join(rows))
st.caption("Überschuss: Zahlungen der Käufer minus Auszahlungen an die Verkäufer; negativ heißt, die Börse müsste zuzahlen. „Wahrhaftig in diesem Markt“: Kein Teilnehmer gewinnt durch eine andere Meldung auf dem Raster 0,25 bis 12.")
with st.expander("Drei Handbeispiele zum Nachrechnen"):
    head = ["| Beispiel | k | handeln | Käufer zahlen | Verkäufer erhalten | Wohlfahrt | Überschuss | VCG: zahlen / erhalten | VCG-Defizit |", "|---|---|---|---|---|---|---|---|---|"]
    st.markdown("\n".join(head + _hand()))
    st.caption("A: Käufer (10; 8; 6), Verkäufer (2; 4; 7), $p_0 = 6{,}5$ im Bereich [4; 8]. B: Käufer (10; 8; 6), Verkäufer (2; 5; 5,5): drei Paare wären effizient, aber es gibt keinen vierten Käufer, also kein $p_0$. "
               "C: Käufer (10; 8; 7,9), Verkäufer (2; 7,5; 9,5): $p_0 = 8{,}7$ liegt über dem Gebot 8.")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Wie viel Handel kostet die Wahrhaftigkeit – und wann wird ein Paar gestrichen?")
kind_v, text_v = verdict_market(mc.k, mc.t, mc.reduced, mc.p0, mc.welfare, a.max_welfare, mc.surplus)
getattr(st, kind_v)(text_v)

st.markdown("---")

# --- Experiment 1: Wer darf lügen? ---------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Wer darf lügen? – Nutzen über die eigene Meldung")
kind_l, text_l = verdict_lies(a.gains)
getattr(st, kind_l)(text_l)
labels = [f"Käufer {i + 1} (Wert {_de(float(mk.b[i]))})" for i in range(mk.nb)] + [f"Verkäufer {j + 1} (Kosten {_de(float(mk.s[j]))})" for j in range(mk.ns)]
pick = st.selectbox("Teilnehmer", list(range(len(labels))), index=tempted_agent(mk.b, mk.s), format_func=lambda i: labels[i], key=f"who_{market}_{kind}_{mk.nb}_{mk.ns}_{int(seed)}",
                    help="Dessen Nutzen wird über seine gemeldete Angabe gezeichnet; alle anderen melden wahr. Vorausgewählt ist der Teilnehmer mit dem größten Anreiz zu lügen (sonst der erste Käufer).")
side, idx = ("b", int(pick)) if pick < mk.nb else ("s", int(pick) - mk.nb)
true_x = float((mk.b if side == "b" else mk.s)[idx])
g = grid()
curves = {m: A.utility_curve(m, mk.b, mk.s, side, idx, g) for m in C.MECHS}
st.plotly_chart(build_utility_curves(g, curves, true_x), width="stretch", key="utility_chart")
for m in C.MECHS:
    truth_u = A.utility_reporting(m, mk.b, mk.s, side, idx, true_x)
    best = int(np.argmax(curves[m]))
    kind_c, text_c = verdict_curve(m, truth_u, float(curves[m][best]), float(g[best]), true_x)
    getattr(st, kind_c)(text_c)
st.caption("Bei McAfee und VCG ist die wahre Meldung auf der Kurve am höchsten (dominant); beim Mittelpunktpreis kann ein Käufer, der weniger meldet, oder ein Verkäufer, der mehr meldet, den Preis zu seinen Gunsten verschieben.")
if st.button("📊 Falschangaben über 400 Zufallsprofile zählen", key="census_button", help=f"{C.TRUTH_PROFILES} Zufallsprofile mit 3 bis 4 Käufern und 3 bis 4 Verkäufern auf einem Raster von 0,5 (viele Gleichstände)."):
    st.session_state["census_done"] = True
if st.session_state.get("census_done"):
    c = _census()
    kind_n, text_n = verdict_census(c)
    getattr(st, kind_n)(text_n)
    st.markdown("\n".join(["| Mechanismus | Profile mit lohnender Falschangabe | Anteil |", "|---|---|---|"] + truth_rows(c)))
    st.caption(f"Jeder Teilnehmer jedes Profils darf alles auf dem Raster 0,25 bis 12 melden; Seed {C.TRUTH_SEED}. Beim Mittelpunktpreis ist der größte Gewinn im Median {_de(c['mid_gain_median'])} und höchstens {_de(c['mid_gain_max'])}; "
               f"das VCG-Defizit der Börse beträgt im Median {_de(c['vcg_deficit_median'])} je Profil. Bei McAfee ist der Verlust in jedem Profil genau das gestrichene Paar (Abweichungen: {c['loss_bad']}), und die Wohlfahrt liegt nie unter dem Anteil 1 − 1/k des Maximums (Verstöße: {c['bound_bad']}).")

st.markdown("---")

# --- Experiment 2: Effizienz über die Marktgröße ---------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 2: Wie schnell schwindet der Verlust mit der Marktgröße?")
st.markdown("Je mehr Teilnehmer, desto weniger kostet das gestrichene Paar: Es ist das am wenigsten wertvolle, und mit vielen Paaren liegt sein Gewinn nahe bei null. Mit **einem** Käufer und **einem** Verkäufer wird dagegen jeder Handel gestrichen.")
if st.button("📈 Effizienz für n = 1 bis 50 rechnen", key="eff_button", help=f"{C.EFF_TRIALS} Zufallsinstanzen je Marktgröße (n Käufer, n Verkäufer, Werte und Kosten gleichverteilt auf [0, 1])."):
    st.session_state["eff_done"] = True
if st.session_state.get("eff_done"):
    eff = _efficiency()
    st.plotly_chart(build_efficiency(eff), width="stretch", key="eff_chart")
    kind_e, text_e = verdict_efficiency(eff)
    getattr(st, kind_e)(text_e)
    head = ["| n | Reduktion | Wohlfahrt / Maximum | Verlust · n | Verlust · n² | Überschuss / Maximum | VCG-Defizit / Maximum |", "|---|---|---|---|---|---|---|"]
    st.markdown("\n".join(head + efficiency_rows(eff)))
    st.caption(f"{C.EFF_TRIALS} Instanzen je n (Seed {C.EFF_SEED}); Verhältnis der Summen über alle Instanzen. Verlust = 1 − Wohlfahrt / Maximum. „Verlust · n“ und „Verlust · n²“ sind **gemessene** Größen: "
               f"Der Verlust fällt hier schneller als 1/n; das ist eine Beobachtung dieser Messung, keine Aussage der Literatur (Rustichini, Satterthwaite und Williams rechnen eine andere Auktion).")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist | Wer setzt an |
|---|---|---|
| **Einheitsnachfrage und -angebot** | Wer mehrere Slots will oder anbietet, braucht einen anderen Mechanismus (mehrere Einheiten, fallender Grenznutzen). | – |
| **Unabhängige private Werte, keine Absprache** | McAfee ist nicht kollusionsfest: Wer sich mit Handelnden abspricht, kann den Preis verschieben. | – |
| **Schwacher Budgetausgleich** | Die Börse behält bei Reduktion einen Überschuss; ein **stark** ausgeglichener Mechanismus (SBBA, zufälliges Streichen) wird nicht gerechnet. | – |
| **Gleichverteilte Werte** in den Zählungen | Die Zahlen zur Effizienz hängen von der Verteilung ab; für schiefe Verteilungen oder Klumpen werden sie nicht gemessen. | – |
| **Ein Durchgang, keine Zeit** | Echte Börsen sind kontinuierlich; Wiederholung und Lernen sind nicht Teil des Modells. | – |
| **Synthetische Märkte** | Die Zahlen gelten für diese Zufallsmärkte, nicht für echte Slot-Börsen. | – |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Modell.** Käufer $i$ mit Wert $b_i$, Verkäufer $j$ mit Kosten $s_j$, je eine Einheit. Sortiert: $b_{(1)} \ge b_{(2)} \ge \dots$, $s_{(1)} \le s_{(2)} \le \dots$ (Gleichstand: kleinerer Index zuerst).
Die effiziente Handelszahl ist $k = \max\{ j : b_{(j)} \ge s_{(j)} \}$, die größte Wohlfahrt $W^* = \sum_{j \le k} (b_{(j)} - s_{(j)})$.

**McAfee.** $p_0 = \tfrac12 (b_{(k+1)} + s_{(k+1)})$, falls beide Ränge existieren. Gilt $s_{(k)} \le p_0 \le b_{(k)}$: Die Paare $1..k$ handeln zum Preis $p_0$ (Käufer zahlen $p_0$, Verkäufer erhalten $p_0$).
Sonst: Die Paare $1..k-1$ handeln; Käufer zahlen $b_{(k)}$, Verkäufer erhalten $s_{(k)}$; die Börse behält $(k-1)(b_{(k)} - s_{(k)})$. Der Verlust ist im zweiten Fall genau $b_{(k)} - s_{(k)}$, das gestrichene Paar, und damit höchstens $W^*/k$.

**Warum wahrhaftig.** Der Preis, den ein handelnder Käufer zahlt, hängt nur von $b_{(k)}$, $b_{(k+1)}$, $s_{(k)}$, $s_{(k+1)}$ und nicht von seinem eigenen Gebot ab, solange er handelt (der $k$-te Käufer setzt den Preis, handelt aber im reduzierten Fall nicht); sein Gebot entscheidet nur, ob er handelt, und er handelt genau dann, wenn sein Wert über dem Preis liegt (kritischer Wert). Dasselbe gilt für Verkäufer. Das ist eine **dominante Strategie**, keine Bayes-Nash-Aussage.
Die Demo prüft es durch Einzelabweichungen auf einem Raster, nicht durch einen Beweis.

**VCG.** Alle $k$ Paare handeln; ein Käufer zahlt $\max(s_{(k)}, b_{(k+1)})$, ein Verkäufer erhält $\min(b_{(k)}, s_{(k+1)})$; die Börse zahlt zu: $k\,(\min(b_{(k)}, s_{(k+1)}) - \max(s_{(k)}, b_{(k+1)})) \ge 0$.

**Mittelpunktpreis.** Alle $k$ Paare handeln zu $\tfrac12 (b_{(k)} + s_{(k)})$: effizient und ausgeglichen, aber nicht wahrhaftig (ein Käufer verschiebt den Preis durch ein niedrigeres Gebot).

**Literatur** (nur Titel, Abstract und Sekundärquellen geprüft, keine Volltexte). McAfee: *A dominant strategy double auction.* Journal of Economic Theory 56(2), 1992.
Myerson, Satterthwaite: *Efficient mechanisms for bilateral trading.* Journal of Economic Theory 29, 1983 (Vorgängerdemo).
Segal-Halevi, Hassidim, Aumann: *SBBA: a Strongly-Budget-Balanced Double-Auction Mechanism.* arXiv 1607.05139 (nur genannt).
Rustichini, Satterthwaite, Williams: *Convergence to efficiency in a simple market with incomplete information.* Econometrica 62(5), 1994 (andere Auktion, nur zur Einordnung).
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zu den Demos: [Interaktive Demos](https://sebastianhanisch.net/demos.html)."
)
