"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import numpy as np
import plotly.graph_objects as go

import dau_algorithm as A
import dau_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=360):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.28), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_market(b, s, out: A.Outcome) -> go.Figure:
    """Nachfrage (Käufer absteigend) und Angebot (Verkäufer aufsteigend) als Treppen über den Rang; die handelnden Paare sind gefüllt, ein gestrichenes Paar hohl; waagerecht die Preise von McAfee."""
    bo, so = A.order(b, s)
    nb, ns = len(b), len(s)
    traded_b, traded_s = set(out.buyers), set(out.sellers)
    fig = go.Figure()
    xb = list(range(1, nb + 1))
    xs = list(range(1, ns + 1))
    fig.add_trace(go.Scatter(x=xb, y=[b[i] for i in bo], mode="lines", line=dict(color=C.COLOR_BUY, width=2, shape="hv"), name="Nachfrage (Käufer, absteigend)", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=xs, y=[s[j] for j in so], mode="lines", line=dict(color=C.COLOR_SELL, width=2, shape="hv"), name="Angebot (Verkäufer, aufsteigend)", hoverinfo="skip"))
    sym_b = ["circle" if i in traded_b else "circle-open" for i in bo]
    sym_s = ["circle" if j in traded_s else "circle-open" for j in so]
    fig.add_trace(go.Scatter(x=xb, y=[b[i] for i in bo], mode="markers", marker=dict(size=11, color=C.COLOR_BUY, symbol=sym_b, line=dict(width=2, color=C.COLOR_BUY)), showlegend=False,
                             customdata=[i + 1 for i in bo], hovertemplate="Käufer %{customdata}: Wert %{y:.2f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=xs, y=[s[j] for j in so], mode="markers", marker=dict(size=11, color=C.COLOR_SELL, symbol=sym_s, line=dict(width=2, color=C.COLOR_SELL)), showlegend=False,
                             customdata=[j + 1 for j in so], hovertemplate="Verkäufer %{customdata}: Kosten %{y:.2f}<extra></extra>"))
    if out.t > 0:
        if abs(out.pb - out.ps) < 1e-12:
            fig.add_hline(y=out.pb, line=dict(color=C.COLOR_PRICE, width=2, dash="dash"), annotation_text=f"Preis {out.pb:.2f}".replace(".", ","), annotation_position="top right")
        else:
            fig.add_hline(y=out.pb, line=dict(color=C.COLOR_PRICE, width=2, dash="dash"), annotation_text=f"Käufer zahlen {out.pb:.2f}".replace(".", ","), annotation_position="top right")
            fig.add_hline(y=out.ps, line=dict(color=C.COLOR_PRICE, width=2, dash="dot"), annotation_text=f"Verkäufer erhalten {out.ps:.2f}".replace(".", ","), annotation_position="bottom right")
    fig.update_xaxes(title="Rang", dtick=1)
    fig.update_yaxes(title="Wert bzw. Kosten", rangemode="tozero")
    return _base(fig, 380)


def build_utility_curves(grid, curves: dict, true_x: float) -> go.Figure:
    """Nutzen eines Teilnehmers über seine Meldung für die drei Mechanismen; senkrecht die wahre Angabe."""
    fig = go.Figure()
    for m in C.MECHS:
        fig.add_trace(go.Scatter(x=grid, y=curves[m], mode="lines", name=C.MECH_LABEL[m], line=dict(color=C.COLOR_MECH[m], width=2, shape="hv")))
    fig.add_vline(x=true_x, line=dict(color="rgba(128,128,128,0.7)", dash="dot", width=1.5), annotation_text="wahre Angabe", annotation_position="top")
    fig.update_xaxes(title="gemeldeter Wert bzw. gemeldete Kosten")
    fig.update_yaxes(title="Nutzen")
    return _base(fig, 340)


def build_efficiency(rows) -> go.Figure:
    """Wohlfahrt gegen das Maximum und Anteil der Reduktion über die Marktgröße n (logarithmisch)."""
    x = [r["n"] for r in rows]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=[r["ratio"] for r in rows], mode="lines+markers", name="Wohlfahrt / Maximum", line=dict(color=C.COLOR_BUY, width=2)))
    fig.add_trace(go.Scatter(x=x, y=[r["reduced"] for r in rows], mode="lines+markers", name="Anteil Handelsreduktion", line=dict(color=C.COLOR_PRICE, width=2, dash="dot")))
    fig.update_xaxes(type="log", title="Marktgröße n (n Käufer, n Verkäufer)", tickvals=x, ticktext=[str(v) for v in x])
    fig.update_yaxes(title="Anteil", range=[0, 1.05])
    return _base(fig, 340)
