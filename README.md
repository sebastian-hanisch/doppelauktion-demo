# Doppelauktion mit Handelsreduktion – Streamlit-Demo

**[→ Demo live ausprobieren](https://sebastianhanisch-doppelauktion-demo.streamlit.app/)**

Viertes Stück der Methodenreihe **Marktmechanismen** in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Ein Mechanismus macht aus Geboten, Budgets oder Überzeugungen Preise und eine Zuteilung; die Reihe prüft ihn an Effizienz, Anreizen, Budgetausgleich und Erlös und rechnet ihn, wo es geht, als Programm. Nach dem [Fisher-Markt](https://github.com/sebastian-hanisch/fisher-markt-demo), der [Positionsauktion](https://github.com/sebastian-hanisch/positionsauktion-demo) und dem [Pacing-Gleichgewicht](https://github.com/sebastian-hanisch/pacing-gleichgewicht-demo) kommt hier erstmals ein Markt mit **zwei Seiten**, die beide private Information haben. Er setzt die Vorgängerdemo [`myerson-satterthwaite-demo`](https://github.com/sebastian-hanisch/myerson-satterthwaite-demo) fort (ein Käufer, ein Verkäufer; „doppelte Auktion: eigenes Thema“). Vehikel: **eine Slot-Börse**, auf der Spediteure Ladeslots kaufen und Betriebe sie verkaufen.

## Warum dieses Problem

Für einen Käufer und einen Verkäufer gilt nach Myerson und Satterthwaite: Es gibt keinen Mechanismus, der zugleich effizient, ehrlich, freiwillig und ausgeglichen ist. Mit **vielen** Teilnehmern gibt es einen Ausweg, der nur ein kleines Stück Effizienz kostet: **McAfees Mechanismus** streicht bei Bedarf das am wenigsten wertvolle Paar und ist dafür **wahrhaftig** (in dominanten Strategien), **individuell rational** und **schwach ausgeglichen** (die Börse macht nie Verlust). Die Kernfrage der Demo: **Wie viel Handel kostet die Wahrhaftigkeit, und wie schnell schwindet dieser Verlust mit der Marktgröße?**

## Modell

$n_B$ Käufer mit Wert $b_i$, $n_S$ Verkäufer mit Kosten $s_j$, Einheitsnachfrage und -angebot. Sortiert: Käufer absteigend, Verkäufer aufsteigend (Gleichstand: kleinerer Index zuerst). Die **effiziente Handelszahl** ist $k = \max\{ j : b_{(j)} \ge s_{(j)} \}$.

**McAfee:** Sei $p_0 = \tfrac12 (b_{(k+1)} + s_{(k+1)})$, falls beide Ränge existieren. Liegt $p_0$ in $[s_{(k)},\, b_{(k)}]$, handeln **alle $k$ Paare zu $p_0$**. Sonst handeln **$k-1$ Paare**: die Käufer zahlen $b_{(k)}$, die Verkäufer erhalten $s_{(k)}$, die Börse behält $b_{(k)} - s_{(k)}$ je Paar. **Vergleich:** **VCG** (alle $k$ Paare, Käufer zahlen $\max(s_{(k)}, b_{(k+1)})$, Verkäufer erhalten $\min(b_{(k)}, s_{(k+1)})$: wahrhaftig, aber die Börse zahlt zu) und der **Mittelpunktpreis** (alle $k$ Paare zu $\tfrac12 (b_{(k)} + s_{(k)})$: effizient und ausgeglichen, aber nicht wahrhaftig).

Die Märkte sind synthetisch (Zufallswerte gleichverteilt auf [0, 10] oder auf einem Raster von 0,5, oder drei feste Handbeispiele); es gibt keine Börsendaten.

## Methodik

- **Mechanismen als reine Funktionen** auf Sortieren und Summen; für viele Instanzen eine **vektorisierte Fassung**, die in den Tests gegen die Einzelversion gelaufen ist (auch bei Gleichständen und bei $n = 1$).
- **Wahrhaftigkeit** wird nicht behauptet, sondern an **jeder Einzelabweichung** auf einem Raster von 0,25 in [0, 12] geprüft: der Nutzen eines Teilnehmers mit seinem wahren Wert, wenn er etwas anderes meldet und alle anderen wahr melden.
- **Effizienz über die Marktgröße:** Monte Carlo mit festen Seeds, $n$ Käufer und $n$ Verkäufer, Werte und Kosten gleichverteilt auf [0, 1]; Verhältnis der Summen über alle Instanzen.

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen sind deterministisch (feste Seeds, reine Arithmetik ohne lineare Algebra) und stehen in `tests/test_claims.py`.

**Tabelle 1: Drei Handbeispiele** (jeder Wert von Hand nachrechenbar; Beispiel A: Käufer (10; 8; 6), Verkäufer (2; 4; 7); B: Käufer (10; 8; 6), Verkäufer (2; 5; 5,5); C: Käufer (10; 8; 7,9), Verkäufer (2; 7,5; 9,5)).

| Beispiel | k | handeln | Käufer zahlen | Verkäufer erhalten | Wohlfahrt | Überschuss | VCG: zahlen / erhalten | VCG-Defizit |
|---|---|---|---|---|---|---|---|---|
| A | 2 | 2 | 6,50 | 6,50 | 12,00 von 12,00 | 0,00 | 6,00 / 7,00 | 2,00 |
| B | 3 | 2 | 6,00 | 5,50 | 11,00 von 11,50 | 1,00 | 5,50 / 6,00 | 1,50 |
| C | 2 | 1 | 8,00 | 7,50 | 8,00 von 8,50 | 0,50 | 7,90 / 8,00 | 0,20 |

In A liegt $p_0 = 6{,}5$ im Bereich [4; 8]: Beide Paare handeln, nichts geht verloren. In B gibt es keinen vierten Käufer, also kein $p_0$: Das dritte Paar (6; 5,5) wird gestrichen, der Verlust ist sein Gewinn 0,5. In C liegt $p_0 = (7{,}9 + 9{,}5)/2 = 8{,}7$ über dem Gebot 8 des zweiten Käufers: Nur ein Paar handelt, der Verlust ist 0,5.

**Standardmarkt** (5 Käufer mit Werten 3,27 / 9,87 / 3,19 / 7,89 / 8,70, 5 Verkäufer mit Kosten 3,91 / 4,38 / 3,73 / 1,07 / 4,79; Seed 8): $k = 3$, aber $p_0 = 3{,}82$ liegt unter dem Verkäufer-Grenzgebot 3,91: Nur **2** Paare handeln, die Wohlfahrt ist **13,77 von 17,75**, die Börse behält **7,95**; VCG hätte ein Defizit von **1,40**. Beim Mittelpunktpreis gewinnt Käufer 2 (Wert 9,87) bis zu **1,94**, wenn er 4,00 meldet statt 9,87.

**Tabelle 2: Wahrhaftigkeit** (400 Zufallsprofile mit 3 bis 4 Käufern und 3 bis 4 Verkäufern, Werte auf dem Raster 0,5 in [0, 10] – also mit vielen Gleichständen; Seed 4; jeder Teilnehmer jedes Profils darf alles auf dem Raster 0,25 in [0, 12] melden).

| Mechanismus | Profile mit lohnender Falschangabe | Anteil |
|---|---|---|
| McAfee (Handelsreduktion) | 0 von 400 | 0,0 % |
| VCG | 0 von 400 | 0,0 % |
| Mittelpunktpreis | 352 von 400 | 88,0 % |

McAfee verletzt in diesen 400 Profilen weder die individuelle Rationalität noch den schwachen Budgetausgleich (je 0 Verstöße); der Verlust gegen das Maximum ist in **jedem** Profil genau das gestrichene Paar (0 Abweichungen), und die Wohlfahrt liegt nie unter dem Anteil $1 - 1/k$ des Maximums (0 Verstöße). In **201 von 400** Profilen wird ein Paar gestrichen. Beim Mittelpunktpreis ist der größte Gewinn einer Falschangabe im Median **1,25**, höchstens **4,25**; das VCG-Defizit der Börse beträgt im Median **1,50** je Profil.

**Tabelle 3: Effizienz über die Marktgröße** ($n$ Käufer und $n$ Verkäufer, Werte und Kosten gleichverteilt auf [0, 1], 5 000 Instanzen je $n$, Seed 8; Verhältnis der Summen; Verlust = 1 − Wohlfahrt / Maximum; „Überschuss“ = was die Börse behält; das VCG-Defizit ist bis $n = 20$ gerechnet).

| n | Reduktion | Wohlfahrt / Maximum | Verlust · n | Verlust · n² | Überschuss / Maximum | VCG-Defizit / Maximum |
|---|---|---|---|---|---|---|
| 1 | 50,8 % | 0,00 % | 1,000 | 1,00 | 0,0 % | 100,0 % |
| 2 | 41,2 % | 76,77 % | 0,465 | 0,93 | 8,3 % | 50,2 % |
| 3 | 42,2 % | 87,71 % | 0,369 | 1,11 | 8,5 % | 33,5 % |
| 5 | 43,5 % | 94,76 % | 0,262 | 1,31 | 8,3 % | 20,3 % |
| 10 | 46,8 % | 98,36 % | 0,164 | 1,64 | 6,6 % | 10,0 % |
| 20 | 49,0 % | 99,54 % | 0,093 | 1,85 | 4,2 % | 5,0 % |
| 50 | 49,4 % | 99,92 % | 0,038 | 1,92 | 1,8 % | – |

**Mit $n = 1$ handelt McAfee nie** (es gibt keinen Rang $k+1$, jeder Handel wird gestrichen): Wohlfahrt 0 % des Maximums. Das ist der Fall der Vorgängerdemo, hier mit der Antwort „wahrhaftig und ausgeglichen, aber es wird nichts gehandelt“. Schon mit zwei Paaren sind es 76,77 %, mit zehn 98,36 %, mit fünfzig 99,92 %. Die zweite Nachkommastelle schwankt mit dem Seed (bei $n = 10$ um etwa 0,04 Prozentpunkte); die 98,36 % bedeuten also rund 98,4 %. Der Anteil der Instanzen, in denen ein Paar gestrichen wird, liegt bei großen Märkten um 50 %; das gestrichene Paar ist aber das am wenigsten wertvolle und kostet kaum etwas. **Der Verlust fällt schneller als $1/n$:** Verlust · $n$ sinkt von 0,465 bei $n = 2$ auf 0,038 bei $n = 50$, Verlust · $n^2$ liegt zwischen 0,93 und 1,92 und scheint sich bei etwa 2 abzuflachen. Das ist eine **Beobachtung dieser Messung**, keine Aussage der Literatur (Rustichini, Satterthwaite und Williams rechnen eine andere Auktion, die Gebotsauktion mit gleichen Preisen). Das VCG-Defizit ist bis $n = 5$ mehr als doppelt so groß wie der Überschuss, den McAfee behält, und fällt auf 5,0 % bei $n = 20$, nur noch geringfügig über den Überschuss von 4,2 %.

## Ehrliche Grenzen

- **Einheitsnachfrage und -angebot, unabhängige private Werte:** Wer mehrere Slots will oder anbietet, braucht einen anderen Mechanismus.
- **Keine Kollusion:** McAfee ist nicht kollusionsfest; abgesprochene Meldungen werden nicht untersucht.
- **Schwacher Budgetausgleich:** Die Börse behält bei einer Reduktion einen Überschuss. Die **stark** ausgeglichene Variante (SBBA, zufälliges Streichen) wird nicht gerechnet.
- **Wahrhaftigkeit durch Einzelabweichungen auf einem Raster geprüft, kein Beweis.** Die Tests prüfen zusätzlich **jedes** Profil eines kleinen ganzzahligen Rasters (2 Käufer, 2 Verkäufer, Werte 0 bis 4) gegen alle Meldungen der anderen; die Dominanz folgt aus der Preisbildung (Preis unabhängig vom eigenen Gebot, solange man handelt; der $k$-te Käufer setzt den Preis, handelt aber im reduzierten Fall nicht).
- **Verteilungen:** Die Effizienzzahlen gelten für gleichverteilte Werte und Kosten; für schiefe Verteilungen oder Klumpen sind sie nicht gemessen. Die Regel „Verlust ~ $1/n^2$“ ist eine Beobachtung dieser Messung.
- **Ein Durchgang ohne Zeit:** Echte Börsen sind kontinuierlich; Wiederholung und Lernen sind nicht Teil des Modells.
- **Literatur:** Alle Angaben beruhen auf Titel, Abstract und Sekundärquellen, nicht auf Volltexten; das Original McAfee 1992 wurde im Volltext nicht gefunden.

## Verifikation

- **Kern:** die drei Handbeispiele von Hand (McAfee, VCG, Mittelpunktpreis); $k = 0$; ein Käufer und ein Verkäufer; Gleichstände nach Index; Nutzen bei Falschmeldung von Hand; vektorisierte Fassung gegen die Einzelfassung in 1 200 Instanzen (fünf Marktformen, stetig und auf dem Raster).
- **Orakel (anderer Rechenweg):** **kritische Werte**: Der Preis eines Handelnden ist sein kleinstes noch gewinnendes Gebot (Käufer) bzw. sein größtes noch gewinnendes (Verkäufer), gefunden durch Bisektion über die Handelsentscheidung als Black Box; **vollständige Aufzählung** aller Profile eines kleinen ganzzahligen Rasters gegen alle Einzelabweichungen (auch gegen alle Meldungen der anderen), individuelle Rationalität und schwacher Budgetausgleich; VCG durch **Neuberechnung der Externalität** (beste Zuordnung mit und ohne den Teilnehmer, Aufzählung aller Teilmengen); die effiziente Handelszahl durch Aufzählung.
- **Eigenschaftstests:** Handelszahl $k$ oder $k-1$, Verlust genau das gestrichene Paar, Wohlfahrt mindestens $(1 - 1/k)$ mal Maximum, individuelle Rationalität, Überschuss ≥ 0, Handelnde sind die höchsten Käufer und niedrigsten Verkäufer, monotone Allokation, Skalierung, Umbenennen, VCG wahrhaftig mit Defizit, Mittelpunktpreis manipulierbar, bei $n = 1$ nie Handel.
- **Randfälle:** kleinste und größte Märkte, Handbeispiele unabhängig von den Reglern, kein Handel, Preis genau auf dem Rand des Bereichs, ungleiche Seiten, Raster, Laufzeit.
- **Verdikte** als reine Funktionen an handgesetzten Werten; **Presets, Layout, AppTest-Rauchtest** (jeder Button, jeder Regler an Minimum und Maximum), **Footer**, **Laufzeit-Importe**.
- **Behauptungen:** `tests/test_claims.py` rechnet jede Zahl dieser Datei nach.
- **Umfang:** siehe `pytest tests/`; `tools/readme_rows.py` ist kein Test, sondern erzeugt die Tabellen, die `test_claims.py` prüft.
- **Nicht gelaufen:** Mutationstests (seit 2026-10-28 nicht mehr Teil des Ablaufs); die Aussagenprüfung durch unabhängige Prüfer steht noch aus.

## Dateistruktur

| Datei | Zweck |
|---|---|
| `.github/workflows/tests.yml` | CI: Push, Pull Request, wöchentlicher Canary |
| `.gitignore` | venv, Caches, Streamlit-Secrets |
| `.streamlit/config.toml` | Streamlit-Einstellungen (keine Nutzungsstatistik) |
| `app.py` | Streamlit-App: Ergebnis, Kernfrage, zwei Experimente, Grenzen, Formeln |
| `dau_algorithm.py` | Kern: McAfee, VCG, Mittelpunktpreis, Nutzen bei Falschmeldung, vektorisierte Fassung |
| `dau_constants.py` | Regler-Grenzen, Seeds, Handbeispiele, Presets |
| `dau_evaluation.py` | Analyse, Zählungen über feste Instanzen, Effizienztabelle, Tabellenzeilen, Verdikte (reine Funktionen) |
| `dau_layout.py` | Fester Kopf (Stylesheet) |
| `dau_presets.py` | Permalink (Begrenzen), Presets, Zufalls-Seed-Button, Auswahlregler |
| `dau_scenario.py` | Märkte (stetig, Raster), Handbeispiele |
| `dau_visualization.py` | Plotly-Abbildungen (Achsen gesperrt) |
| `tools/readme_rows.py` | erzeugt die README-Tabellen über dieselben Funktionen wie die App |
| `requirements-dev.txt` | Laufzeit plus pytest |
| `requirements.txt` | Laufzeit-Bibliotheken (ungepinnt) |
| `tests/` | Mini-Märkte, Orakel, Eigenschaften, Randfälle, Claims, Presets, Layout, AppTest, Footer, Laufzeit-Importe |

## Bewusst nicht umgesetzt

- **SBBA** (stark ausgeglichen, zufälliges Streichen), **Kollusion**, **mehrere Einheiten je Teilnehmer** und **Bayes-Nash-Mechanismen** (der Vorgänger rechnet sie für ein Paar).
- **Konvergenzrate aus der Literatur:** Die Demo misst nur, wie der Verlust in dieser Auktion mit $n$ fällt.
- **Echte Börsendaten** und kontinuierlichen Handel.

## Lokal ausführen

```bash
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt
streamlit run app.py
```

Die CI läuft mit Python 3.12; für die Streamlit Community Cloud ist die Python-Version im Dashboard einzustellen (3.12 empfohlen).

## Tests ausführen

```bash
pip install -r requirements-dev.txt
pytest tests/ -v
```

Gebaut mit Streamlit, Plotly und NumPy.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Marktmechanismen: von Preisen bis Marktmachern](https://sebastianhanisch.net/konzepte-marktmechanismen.html).
