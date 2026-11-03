"""house_core: the pure-Python description of the house (no bpy)."""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "code"))
import house_core  # noqa: E402

BP = house_core.build()


def test_build_runs_without_bpy():
    assert "bpy" not in sys.modules
    assert ("EG", "EG_Waende") in BP.geo
    assert any(c == "Dach" for c, _ in BP.geo)


def test_build_is_deterministic():
    assert house_core.build().geo == BP.geo


CODE = Path(__file__).resolve().parent.parent / "code"


def test_paint_and_room_lights_live_in_the_core():
    ral9010, ral5014 = (241, 236, 225), (99, 125, 150)
    assert house_core.PAINT == {"Putz": ral9010, "Rahmen": ral9010, "Laden": ral5014, "Kachel": ral5014}
    assert len(house_core.ROOM_LIGHTS) == 23
    assert BP.paint == house_core.PAINT and BP.room_lights == house_core.ROOM_LIGHTS
    assert "RAL =" not in (CODE / "paint.py").read_text()
    assert "ROOM_LIGHTS =" not in (CODE / "film.py").read_text()


def test_shed_battens_are_wood():
    assert "Laden" not in BP.geo[("Umgebung", "Schuppen_Holz")]["m"]
    assert "Schuppen_Holz" not in (CODE / "paint.py").read_text()


def part_bbox(g, first, n):
    pts = [g["v"][i] for f in g["f"][first:first + n] for i in f]
    return [min(p[k] for p in pts) for k in range(3)], [max(p[k] for p in pts) for k in range(3)]


BOARDS = {"EG": ("EG", "Laeden_Querbretter"), "OG": ("OG", "OG_Laeden_Querbretter")}


def test_cross_boards_four_boxes_per_shutter_in_its_storey():
    """The OG boards live in the OG collection, so the viewer's "Nur EG" cutaway hides them."""
    for c, key in BOARDS.items():
        shutters = len(BP.parts[(c, c + "_Laeden")])
        boards = BP.parts[key]
        assert shutters > 0 and len(boards) == 4 * shutters, c
        g = BP.geo[key]
        assert set(g["m"]) == {"Rahmen"}
        for first, n in boards:
            lo, hi = part_bbox(g, first, n)
            size = sorted(round(hi[k] - lo[k], 6) for k in range(2))
            assert round(hi[2] - lo[2], 6) == 0.1 and size[0] == 0.012
            assert (hi[2] < house_core.Z_OG) == (c == "EG")


def test_cross_boards_dont_shift_rnd(monkeypatch):
    monkeypatch.setattr(house_core, "build_cross_boards", lambda: None)
    plain = house_core.build()
    for key, g in plain.geo.items():
        assert BP.geo[key]["r"] == g["r"], key


FIX = json.loads((Path(__file__).parent / "fixtures" / "garden_blender.json").read_text())
WR_NAMES = ("Windrose", "WR_N", "WR_O", "WR_S", "WR_W")


def close(a, b, tol=1e-4):
    return all(abs(x - y) < tol for x, y in zip(a, b))


def test_garden_no_grass_equals_todays_house_rects():
    want = [r for n, r in FIX["rects"].items() if n not in WR_NAMES]
    got = BP.garden.no_grass
    assert len(got) == len(want) and all(close(a, b) for a, b in zip(got, want))


def test_garden_windrose_rects():
    wr = BP.garden.windrose
    assert len(wr) == 5 and close(wr[0], FIX["rects"]["Windrose"])
    for (x0, x1, y0, y1), name in zip(wr[1:], WR_NAMES[1:]):
        a, b, c, d = FIX["rects"][name]
        assert x0 < (a + b) / 2 < x1 and y0 < (c + d) / 2 < y1, name


def test_garden_density():
    d, (hx, hy) = house_core.density, house_core.HOUSE_C
    assert d(hx, hy) == 1 and abs(d(hx + house_core.FAR + 1, hy) - house_core.FAR_DENS) < 1e-12
    vals = [d(hx + r / 10, hy) for r in range(0, 400)]
    assert all(a >= b for a, b in zip(vals, vals[1:]))


def test_garden_clump_is_todays():
    cl = BP.garden.clump
    assert len(cl["v"]) == 6 * 4 * 2 and min(cl["h"]) == 0 and max(cl["h"]) == 1
    assert all(close(a, b, 1e-6) for a, b in zip(cl["v"], FIX["clump_v"]))
    assert [list(f) for f in cl["f"]] == FIX["clump_f"]


def test_garden_shrubs():
    sh = BP.garden.shrubs
    assert sh == house_core.build().garden.shrubs                       # deterministic
    for bed in ("Beet_Ost", "Beet_West"):
        x0, x1, y0, y1 = [v + s for v, s in zip(FIX["rects"][bed], (0.05, -0.05, 0.05, -0.05))]
        ys = sorted(y for x, y, r, h in sh if x0 < x < x1 and y0 < y < y1)
        gaps = [b - a for a, b in zip(ys, ys[1:])]
        assert len(ys) >= 3 and all(0.57 < g < 0.67 or 1.15 < g < 1.33 for g in gaps), bed
        assert all(1.15 < g for g in gaps[2::3]) and all(g < 0.67 for i, g in enumerate(gaps) if i % 3 != 2)


def test_parts_cover_all_faces():
    for key, g in BP.geo.items():
        nxt = 0
        for first, n in BP.parts[key]:
            assert first == nxt and n > 0, key
            nxt += n
        assert nxt == len(g["f"]), key
