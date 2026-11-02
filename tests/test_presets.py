"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen."""

import numpy as np

import dau_constants as C
import dau_evaluation as ev
import dau_presets as P


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name]


def test_preset_values_are_inside_the_slider_bounds():
    for name, preset in C.PRESETS.items():
        assert preset["market"] in C.MARKETS and preset["kind"] in C.VALUE_KINDS, name
        assert C.NB_MIN <= preset["nb"] <= C.NB_MAX and C.NS_MIN <= preset["ns"] <= C.NS_MAX and 0 <= preset["seed"] <= C.SEED_MAX, name


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS["Standardfall (Voreinstellung)"]) == ev.Settings()


def test_setting_specs_cover_every_preset_key():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)


def test_every_preset_runs_and_mcafee_is_truthful():
    for name, preset in C.PRESETS.items():
        a = ev.analyse(ev.Settings(**preset))
        assert a.gains["mcafee"] == 0.0 and a.gains["vcg"] == 0.0 and a.outcomes["mcafee"].surplus >= -1e-12, name


def test_the_presets_show_what_their_help_says():
    by = {name: ev.analyse(ev.Settings(**p)) for name, p in C.PRESETS.items()}
    std = by["Standardfall (Voreinstellung)"].outcomes["mcafee"]
    assert std.reduced and std.k == 3 and std.t == 2                              # der Standardmarkt zeigt eine Reduktion
    assert by["Standardfall (Voreinstellung)"].gains["mitte"] > 1.0              # und eine lohnende Lüge beim Mittelpunktpreis
    a, b, c = (by[f"Handbeispiel {x}"] for x in ("A: alle Paare handeln", "B: ein Paar wird gestrichen", "C: p₀ außerhalb"))
    assert (a.k, a.outcomes["mcafee"].t) == (2, 2) and (b.k, b.outcomes["mcafee"].t) == (3, 2) and (c.k, c.outcomes["mcafee"].t) == (2, 1)
    one = by["Ein Käufer, ein Verkäufer: nie Handel"]
    assert (one.market.nb, one.market.ns, one.k, one.outcomes["mcafee"].t) == (1, 1, 1, 0)
    grid = by["Gleichstände: Raster 0,5"]
    assert np.allclose(grid.market.b * 2, np.round(grid.market.b * 2)) and len(set(grid.market.b.tolist()) | set(grid.market.s.tolist())) < grid.market.nb + grid.market.ns
