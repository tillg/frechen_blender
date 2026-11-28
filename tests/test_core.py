"""house_core: the pure-Python description of the house (no bpy)."""
import json, math, sys

import pytest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "code"))
import house_core, ofen, waschkueche  # noqa: E402

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
    assert house_core.PAINT == {"Putz": ral9010, "Rahmen": ral9010, "Laden": ral5014, "Front": ral5014}
    assert len(house_core.ROOM_LIGHTS) == 1 and len(BP.wall_lights) == 29 + 30   # OG (#33, #32, 2026-11-25: Flur mirror's 2 gone), EG (#22, #34; #61: 29 Wandlampen + the Ofen bed's)
    assert BP.paint == house_core.PAINT and BP.room_lights == house_core.ROOM_LIGHTS
    assert "RAL =" not in (CODE / "paint.py").read_text()
    assert "ROOM_LIGHTS =" not in (CODE / "film.py").read_text()


def test_room_light_height_and_film_constants_come_from_the_core():
    """ADR-001-XEWL: film.py and the viewer read these facts, they don't repeat them."""
    assert house_core.ROOM_LIGHT_H == 2.1
    film = (CODE / "film.py").read_text()
    assert "z + 2." not in film and "Z_OG =" not in film and "HOUSE_C =" not in film


def test_annex_boards_are_wood():
    assert "Laden" not in BP.geo[("EG", "EG_Anbau")]["m"]
    assert "EG_Anbau" not in (CODE / "paint.py").read_text()


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


def test_ofen_submodel_after_the_sketches():
    """input/2026-11-04 input; #63 (input/2026-11-28 input/ofen_dreieck_optionen.svg, variant B): the stove a triangle in
    the corner, legs 1.00 along the Flur wall (x = 0) and the west wall (y = 0), its front (141) on the hypotenuse facing
    the room at 45°, 1.15 m high, its top edge along the front rounded; the fire door (65) centred in the front, an arch
    under it, open underneath on legs; the bed above it straight, 0.70 wide and 1.90 long along the Flur wall (sketch:
    2.00, shortened for the Stube door), underside at 1.45 m, one rim board along its free side, a post and a ladder at
    the foot; the benches where they stood: beside the stove along the Flur wall and 1.60 along the west wall, 70 cm
    clear of the fire door. Corner of the room at the origin, walls along +x and +y."""
    bp = house_core.build_ofen()
    assert {c for c, _ in bp.geo} == {"Ofen"}
    a = ofen.OFEN_A
    assert (a, ofen.OFEN_BED_W) == (1.00, 0.70)

    def bbox(name):
        v = bp.geo[("Ofen", name)]["v"]
        return [round(min(p[k] for p in v), 3) for k in range(3)], [round(max(p[k] for p in v), 3) for k in range(3)]

    assert bbox("Ofen_Koerper") == ([0, 0, 0], [a, a, 1.15])
    v = bp.geo[("Ofen", "Ofen_Koerper")]["v"]
    assert all(x + y <= a + 1e-9 for x, y, z in v)                        # a triangle: nothing beyond the front
    r, H = ofen.OFEN_ASSUMED["r"], ofen.OFEN_H
    top = [(x, y) for x, y, z in v if z > H - 1e-9]                       # top edge rounded: the top face
    assert top and all(x + y <= a - r * 2 ** 0.5 + 0.003 for x, y in top)  # inset by r from the front
    assert min(x for x, y in top) == 0 and min(y for x, y in top) == 0    # but reaches the walls
    door = bp.geo[("Ofen", "Ofen_Feuertuer")]["v"]                        # in the front, centred, 65 wide, facing 45°
    assert all(a - 1e-6 <= x + y <= a + 0.04 * 2 ** 0.5 + 1e-6 for x, y, z in door)
    front = [(x, y) for x, y, z in door if abs(x + y - a) < 1e-6]
    assert abs(max(math.dist(p, q) for p in front for q in front) - 0.65) < 1e-6
    assert abs(sum(x - y for x, y in front) / len(front)) < 1e-6 and abs(max(z for *_, z in door) - 1.05) < 1e-9
    floor = [(x, y) for x, y, z in v if z == 0]                           # open underneath: only the legs on the floor
    tl = ofen.OFEN_ASSUMED["leg"]
    assert all(x + y >= a - tl * 2 ** 0.5 - 1e-9 for x, y in floor)
    c = a / 2                                                             # the arch under the door: 50 wide
    assert any(abs(math.dist((x, y), (c, c)) - 0.25) < 1e-6 and abs(x + y - a) < 1e-9 for x, y in floor)
    bank = bp.geo[("Ofen", "Ofen_Bank")]["v"]
    right = [p for p in bank if p[1] > 1.2]                               # beside the stove, along the Flur wall
    left = [p for p in bank if p[0] > 1.2]                                # along the west wall
    span = lambda ps, k: round(max(p[k] for p in ps) - min(p[k] for p in ps), 3)
    assert span(right, 1) == 0.6 and max(p[0] for p in right) <= 0.7
    assert span(left, 0) == 1.6 and span(left, 1) == 0.6 and max(p[1] for p in left) <= 0.7
    assert len(left) + len(right) == len(bank)
    assert min(p[0] for p in left) - a / 2 >= 0.70 and min(p[1] for p in right) > a   # clear of the fire door, the stove
    lo, hi = bbox("Ofen_Bett")
    assert lo[:2] == [0, 0] and hi[:2] == [0.7, 1.9]                       # straight, 70 wide
    bed = bp.geo[("Ofen", "Ofen_Bett")]["v"]
    assert round(min(z for x, y, z in bed if y < 1.2 and x < 0.5), 3) == 1.45
    g, BL = bp.geo[("Ofen", "Ofen_Bett")], ofen.OFEN_BED_L                # foot end: 3 rungs from the wall to the post
    rungs = []
    for first, n in bp.parts[("Ofen", "Ofen_Bett")]:
        ps = [g["v"][i] for f in g["f"][first:first + n] for i in f]
        lo = [min(p[k] for p in ps) for k in range(3)]; hi = [max(p[k] for p in ps) for k in range(3)]
        if lo[0] < 0.02 and abs(hi[0] - 0.62) < 1e-9 and lo[1] >= BL - 0.08 - 1e-9 and hi[2] < 1.4:
            rungs.append((lo[2] + hi[2]) / 2)
    assert len(rungs) == 3 and all(abs(z - ofen.OFEN_BED * k / 4) < 1e-9 for z, k in zip(sorted(rungs), (1, 2, 3)))
    rim = bp.geo[("Ofen", "Ofen_Bettrand")]["v"]                          # rim: the free long side only
    top, bottom = max(z for *_, z in rim), min(z for *_, z in rim)
    assert bottom == 1.49 and abs(top - (1.49 + 0.05)) < 1e-9
    assert len(bp.parts[("Ofen", "Ofen_Bettrand")]) == 1 and min(x for x, y, z in rim) > 0.6
    assert min(y for x, y, z in rim) >= 0.1 - 1e-9 and max(y for x, y, z in rim) <= 1.8 + 1e-9
    assert bp.dims and all(len(d) == 3 for d in bp.dims)
    assert {"Ofen 100", "100", "Front 141", "Bett 190", "70"} <= {t for _, _, t in bp.dims}


def test_ofen_bed_mattress_without_blanket():
    """On the bed above the Ofen: a very thin cream mattress inside the rim; no blanket (the red
    checked one was removed on request)."""
    bp = house_core.build_ofen()
    g = bp.geo[("Ofen", "Ofen_Bettzeug")]
    zp = ofen.OFEN_BED + 0.04                                             # platform top
    mat_of = {}                                                           # vertex -> materials of its faces
    for f, mat in zip(g["f"], g["m"]):
        for i in f:
            mat_of.setdefault(i, set()).add(mat)
    matt = [g["v"][i] for i, ms in mat_of.items() if "Creme" in ms]
    assert matt and round(min(z for *_, z in matt), 3) == round(zp, 3)   # lies on the platform
    assert max(z for *_, z in matt) - zp <= 0.05                          # very thin
    assert all(x <= 1.2 - 0.025 and y <= ofen.OFEN_BED_L and x >= 0 and y >= 0
               and (x + y <= 1.9 - 0.025 * 2 ** 0.5 if y <= 1.2 else x <= 0.7 - 0.025)
               for x, y, _ in matt)                                       # inside the rim
    assert set(g["m"]) == {"Creme"}                                       # no blanket
    assert not {"Karo", "KaroHell"} & set(house_core.MAT_DEF)


def test_ofen_built_into_the_stube():
    """The Ofen sub-model sits in the Stube's NW corner (plan: "Kachelofen"), rotated so the bed runs
    along the north wall towards the Stube door and the long bench along the west wall; it replaces
    the old Ofenbett and its fire window to the Flur. No dimension lines in the house."""
    assert not any(c == "Ofen" for c, _ in BP.geo) and ("EG", "EG_Ofenbett") not in BP.geo
    assert BP.dims == ()
    names = {n for c, n in house_core.build_ofen().geo}
    assert {("EG", "EG_" + n) for n in names} <= set(BP.geo)
    house_core.build()                                                    # restore the registries

    def bbox(name):
        v = BP.geo[("EG", name)]["v"]
        return [round(min(p[k] for p in v), 3) for k in range(3)], [round(max(p[k] for p in v), 3) for k in range(3)]

    assert bbox("EG_Ofen_Koerper") == ([9.06, 4.845, 0], [10.06, 5.845, 1.15])    # the triangle in the corner (#63)
    fire = next(f for f in BP.fires if f["collection"] == "EG" and not f.get("back") and 9 < f["base"][0] < 10.1)
    assert abs(fire["u"][0] - 2 ** -0.5) < 1e-9 and abs(fire["u"][1] - 2 ** -0.5) < 1e-9   # its front faces the room (SE)
    assert bbox("EG_Ofen_Bett")[1][0] <= 11.004 - 0.04                     # clear of the Stube door
    assert bbox("EG_Ofen_Bank")[0][1] >= 2.938 + 0.1                       # clear of the passage to Essen
    g = BP.geo[("EG", "EG_Ofen_Bank")]                                   # grain along the seats
    tops = {m for f, m in zip(g["f"], g["m"]) if all(abs(g["v"][i][2] - 0.45) < 1e-9 for i in f)}
    assert tops == {"FichteY"}
    assert "FichteX" in BP.geo[("EG", "EG_Ofen_Bett")]["m"]               # bed runs along x now


def test_bibliothek_piano_desk_and_werkstattofen():
    """Bibliothek (Musikraum + Büro): grand piano turned 30° to the left (counter-clockwise from
    above) and then 180° in place (keyboard and bench to the north), desk between the two north french doors (cherry top 10.943 .. 12.843, #10), and a
    small workshop stove (input/2026-11-03 input/werkstattofen.jpeg) in the corner of the Flur wall
    and the wall stub at the offener Kamin, turned 45° to face the room."""
    g = BP.geo[("EG", "EG_Moebel")]
    on = lambda mat: {i for f, m in zip(g["f"], g["m"]) if m == mat for i in f}
    keys = [g["v"][i] for i in on("Keramik")]                            # white keys: one long box
    top = [(x, y) for x, y, z in keys if z == max(p[2] for p in keys)]
    (ax, ay), (bx, by) = next((p, q) for p in top for q in top if 1.09 < math.dist(p, q) < 1.105)  # long edge, 1.10
    assert abs(math.degrees(math.atan2(by - ay, bx - ax)) % 180 - 30) < 0.5        # 15°, then "etwas mehr"
    assert sum(y for _, y, _ in keys) / len(keys) > 11.4      # then 180° (2026-11-08): keyboard to the north
    t = BP.geo[("EG", "EG_Schreibtisch")]
    desk = [(x, y) for x, y, z in t["v"] if z == 0.75]
    assert round(min(x for x, _ in desk), 3) == 10.943 and round(max(x for x, _ in desk), 3) == 12.843
    assert max(y for _, y in desk) <= 12.473
    ofen = BP.geo[("EG", "EG_Werkstattofen")]
    lo = [round(min(p[k] for p in ofen["v"]), 3) for k in range(3)]
    hi = [round(max(p[k] for p in ofen["v"]), 3) for k in range(3)]
    assert 9.351 + 0.09 < lo[0] < 9.351 + 0.15 and 8.876 + 0.09 < lo[1] < 8.876 + 0.15   # in the corner
    assert 1.0 <= hi[2] <= 1.1 and 0.55 < hi[0] - lo[0] < 0.65                      # turned 45° (2026-11-08)
    (fire,) = [f for f in house_core.FIRES if 9.351 < f["base"][0] < 10.2 and 8.876 < f["base"][1] < 9.8]
    assert abs(fire["u"][0] + fire["u"][1]) < 1e-6 and fire["u"][0] > 0.7          # front (along u) faces NE
    assert {"Eisen", "Ofenglas"} <= set(ofen["m"])          # its fire: FIRES (test_fires_...)
    assert "EG_Werkstattofen" not in BP.furniture                        # built in, like the Ofen


def test_schlafen_se_headboard_wall_and_werkstattofen():
    """Master bedroom (OG, SE): the headboard block (divider + cupboard) is now a plain 15 cm
    wall right behind the bed, 1.20 m high; a second workshop stove like the Bibliothek's stands
    in the corner between the Bad wall (x 8.72) and the WC wall (y 3.84), turned to face the room."""
    zo = house_core.Z_OG

    def part_boxes(key):
        g = BP.geo[key]
        for first, n in BP.parts[key]:
            vs = [g["v"][i] for f in g["f"][first:first + n] for i in f]
            yield [round(min(p[k] for p in vs), 3) for k in range(3)], [round(max(p[k] for p in vs), 3) for k in range(3)]

    assert not any(lo[0] < 11.47 and hi[0] > 10.86 and lo[1] < 3.98 and hi[1] > 0.98
                   for lo, hi in part_boxes(("OG", "OG_Moebel")))            # block gone
    assert ([11.48, 0.98, round(zo, 3)], [11.63, 3.98, round(zo + 1.2, 3)]) in list(part_boxes(("OG", "OG_Waende")))
    ofen = BP.geo[("OG", "OG_Werkstattofen")]
    lo = [min(p[k] for p in ofen["v"]) for k in range(3)]
    hi = [max(p[k] for p in ofen["v"]) for k in range(3)]
    assert 8.72 + 0.09 < lo[0] < 8.72 + 0.15 and 3.84 - 0.15 < hi[1] < 3.84 - 0.09   # in the corner
    assert 0.55 < hi[0] - lo[0] < 0.65 and 1.0 <= hi[2] - zo <= 1.1                 # turned 45°
    assert {"Eisen", "Ofenglas"} <= set(ofen["m"])          # its fire: FIRES (test_fires_...) and "OG_Werkstattofen" not in BP.furniture
    eg = BP.geo[("EG", "EG_Werkstattofen")]["v"]                                    # same stove
    assert len(eg) == len(ofen["v"])


def test_wandlampe_after_the_photo():
    """Issue #19: the Wandlampe after input/2026-11-13 input/wandlampe.png (brass, opal glass; maker:
    shade Ø 16, 11 high, reaching 21 from the wall): rosette on the wall, gooseneck arm, gallery, opal
    bell, every part a closed solid; its light (50 cm out from the wall at the bulb's height) is in WALL_LIGHTS; it
    draws nothing from the global random stream."""
    import random
    from collections import Counter
    hc = house_core
    hc.GEO.clear(); hc.PARTS.clear(); hc.WALL_LIGHTS.clear()
    state = random.getstate()
    hc.wandlampe("T", 2.0, 5.0, 0, 1, 1.70)                 # wall face y 5.0, facing north, rosette centre 1.70
    assert random.getstate() == state
    g = hc.GEO[("T", "T_Wandlampen")]
    solids = [(g["m"][a], g["f"][a:a + n]) for a, n in hc.PARTS[("T", "T_Wandlampen")]]
    for m, fs in solids:                                    # closed: every edge in two faces
        assert set(Counter(tuple(sorted((f[i], f[(i + 1) % len(f)]))) for f in fs for i in range(len(f))).values()) == {2}, m
    assert {m for m, _ in solids} == {"Messing", "Opalglas"}
    pts = lambda mat: [g["v"][i] for m, fs in solids if mat in (None, m) for f in fs for i in f]
    span = lambda ps, k: (min(p[k] for p in ps), max(p[k] for p in ps))
    shade, every = pts("Opalglas"), pts(None)
    (sx0, sx1), (sy0, sy1), (sz0, sz1) = (span(shade, k) for k in range(3))
    assert abs(sx1 - sx0 - 0.16) < 0.002 and abs(sy1 - sy0 - 0.16) < 0.002          # Ø 16
    assert abs(sz1 - sz0 - 0.11) < 0.005                                              # 11 high
    (ay0, ay1), (az0, az1) = span(every, 1), span(every, 2)
    assert ay0 >= 5.0 - 1e-9 and abs(ay1 - 5.0 - 0.21) < 0.005                         # on the wall, reach 21
    assert az1 - 1.70 <= 0.0855 and az1 - az0 <= 0.21                                 # under a 2.20 ceiling at 2.10
    assert [m for m, _ in solids].count("Messing") >= 3                                # rosette, arm, gallery
    assert len(hc.WALL_LIGHTS) == 1
    x, y, z = hc.WALL_LIGHTS[0]
    assert abs(x - (sx0 + sx1) / 2) < 1e-6 and abs(y - 5.50) < 1e-6 and sz0 < z < sz1   # 50 cm out, at the bulb's height
    assert hc.MAT_DEF["Opalglas"].get("night") is True and "Messing" in hc.MAT_DEF
    house_core.build()                                      # restore the registries


def test_outside_lights_at_the_lamp_bulbs():
    """Every gooseneck wall lamp records its filament centre (0.38 m out from the wall, 8.5 cm below the
    rosette) so the viewer can switch the lamps on at dusk; the filament glows only then."""
    assert len(BP.outside_lights) == 8
    assert (5.55, -0.38, 1.865) in [tuple(round(c, 3) for c in p) for p in BP.outside_lights]
    assert all(round(z, 3) == 1.865 for *_, z in BP.outside_lights)
    assert house_core.MAT_DEF["Gluehfaden"].get("night") is True


def test_regal_submodel():
    """code/regal.py ("Schrank im Büro") after the agreed drawing input/2026-11-11 input/buero_regal_v2.svg,
    at its own origin (the Bibliothek's inner SE corner): the Tegernsee bookcase (2.38 high) around the
    east window: 94 column (north), the middle 94 centred on the 90 window (base below, top 5 under
    the sill; bridge from 2.02 above the 2.00 head), 94 column (south); 30 / 48 free to the walls;
    depth 42, middle base 48; books in it. With the three wall pieces: east wall with the window, north
    wall with the balcony door, Flur wall with the Büro door (106, moved 50 west), whose leaf opened
    90 deg stands 10.5 in front of the south column, its levers 5.5."""
    import regal as r
    bp = house_core.build_regal()
    leaves = [pts for c, pts in house_core.LEAVES if c == "Regal"]
    doors = [d for d in house_core.DOORS if d["c"] == "Regal"]
    house_core.build()                                                    # restore the registries
    assert r.REGAL_AT == (14.575, 8.876) and bp.garden is None
    assert {c for c, _ in bp.geo} == {"Regal"}
    assert {n for _, n in bp.geo} == {"Regal_Moebel", "Regal_Waende", "Regal_Fenster_Tueren", "Regal_Innentueren",
                                      "Regal_Laeden", "Regal_Buerotuer"}
    # the leaf is an object of its own, hinged at the east jamb's lining, swinging 90 deg to shut
    x0, y0 = r.REGAL_AT
    assert bp.swing == {"Regal_Buerotuer": 90.0}
    assert bp.pivot["Regal_Buerotuer"] == pytest.approx((r.TUER[1] - 0.025 - x0, r.FS - y0, 0.0))
    cm = lambda a, b: round(abs(b - a) * 100)
    case = [(m, [lo[0] + x0, lo[1] + y0, lo[2]], [hi[0] + x0, hi[1] + y0, hi[2]])
            for m, lo, hi in _parts(bp, ("Regal", "Regal_Moebel"))]
    wa, wb, sill, head = r.FENSTER[:4]
    assert (cm(wa, wb), cm(r.S0, r.M0), cm(r.M0, r.M1), cm(r.M1, r.N1)) == (90, 94, 94, 94)
    assert abs((r.M0 + r.M1) / 2 - (wa + wb) / 2) < 1e-9 and r.M0 < wa and r.M1 > wb
    assert (cm(r.FS, r.S0), cm(r.N1, r.FN)) == (48, 30)
    assert max(hi[2] for _, _, hi in case) == pytest.approx(2.38) and min(lo[2] for _, lo, _ in case) == 0.0
    cols = [lo[0] for _, lo, hi in case if hi[1] <= r.M0 + 1e-6 or lo[1] >= r.M1 - 1e-6 or lo[2] >= r.CORN - 1e-6]
    assert max(hi[0] for _, _, hi in case) < 14.575 and min(cols) == pytest.approx(14.575 - 0.42 - 0.045)   # knobs
    assert min(lo[1] for _, lo, _ in case) == pytest.approx(r.S0 - 0.03) and max(hi[1] for _, _, hi in case) == pytest.approx(r.N1 + 0.03)
    win = [(lo, hi) for _, lo, hi in case if lo[1] < wb and hi[1] > wa]
    assert not any(lo[2] < head and hi[2] > sill for lo, hi in win)       # the window stays free
    assert max(hi[2] for lo, hi in win if hi[2] < sill) == pytest.approx(0.95)
    assert min(lo[2] for lo, hi in win if lo[2] > head) == pytest.approx(2.02)
    base = [lo[0] for lo, hi in win if hi[2] < sill]
    assert min(base) == pytest.approx(14.575 - 0.48 - 0.045)               # 48 deep, its knobs in front
    assert {"NussX", "NussZ", "Buecher", "Eisen"} == {m for m, _, _ in case}
    assert sum(m == "Buecher" for m, _, _ in case) >= 150
    # walls: window, balcony door, the Büro door 106 at 13.017 .. 14.075, the old opening's east part closed
    H = (lambda p: [m for m, lo, hi in _parts(bp, ("Regal", "Regal_Waende"))
                    if lo[0] - 1e-6 <= p[0] - x0 <= hi[0] + 1e-6 and lo[1] - 1e-6 <= p[1] - y0 <= hi[1] + 1e-6
                    and lo[2] < p[2] < hi[2]])
    assert H((14.7, 10.76, 1.5)) == [] and H((14.7, 10.76, 0.5)) == ["Putz"] and H((14.7, 9.5, 1.5)) == ["Putz"]
    assert H((13.3, 12.6, 1.0)) == [] and H((14.2, 12.6, 1.0)) == ["Putz"]
    assert r.TUER[:2] == pytest.approx((13.017, 14.075)) and cm(*r.TUER[:2]) == 106
    assert H((13.5, 8.7, 1.0)) == [] and H((14.3, 8.7, 1.0)) == ["Putz"] and H((12.8, 8.7, 1.0)) == ["Putz"]
    # the leaf, opened 90 deg, reaches past the column's start and stays clear of it, levers too
    assert len(leaves) == 1 and len(doors) == 1
    xs = [p[0] + x0 for p in leaves[0]]
    assert max(p[1] + y0 for p in leaves[0]) > r.S0
    assert r.XF - max(xs) == pytest.approx(0.105)
    assert r.XF - (doors[0]["leaf"][1][0] + x0) == pytest.approx(0.055)                  # its levers
    texts = [t for *_, t in bp.dims]
    for t in ("48 frei", "Säule 94", "Mitte 94", "30 frei", "Fenster 90", "Unterteil 95", "Brücke 36", "Höhe 238",
              "Tiefe 42", "Tür 106", "10,5 Luft", "39 frei"):
        assert t in texts, t


def test_regal_built_into_the_house():
    """The bookcase stands in the house at REGAL_AT, every part the same (furniture: EG_Moebel, stage
    Eingerichtet); the window, the balcony door and the Büro door are the sub-model's; the old
    bookcase on the Flur wall is gone; no furniture in the moved door's swing."""
    import regal as r
    sub = house_core.build_regal()
    house_core.build()                                                    # restore the registries
    x0, y0 = r.REGAL_AT
    assert _solids(sub, ("Regal", "Regal_Moebel"), x0, y0) <= _solids(BP, ("EG", "EG_Moebel"))
    for n in ("Fenster_Tueren", "Innentueren", "Laeden", "Buerotuer"):
        assert _solids(sub, ("Regal", "Regal_" + n), x0, y0) <= _solids(BP, ("EG", "EG_" + n)), n
    assert BP.swing["EG_Buerotuer"] == 90.0 and BP.pivot["EG_Buerotuer"] == pytest.approx((r.TUER[1] - 0.025, r.FS, 0.0))
    assert "EG_Moebel" in BP.furniture
    assert not any(m == "Buecher" and lo[1] < 9.3 and hi[0] < 13.6 and lo[0] > 10.5
                   for m, lo, hi in _parts(BP, ("EG", "EG_Moebel")))                               # old bookcase
    leaf = [pts for c, pts in house_core.LEAVES if c == "EG" and abs(max(p[0] for p in pts) - (r.TUER[1] - 0.025)) < 0.01]
    assert len(leaf) == 1
    a, b = r.TUER[:2]
    for o in sorted(n for n in BP.furniture if n.startswith("EG_")):     # the swing's quarter circle
        for m, lo, hi in _parts(BP, ("EG", o)):
            assert not (lo[0] < b and hi[0] > b - (b - a) and lo[1] < r.FS + (b - a) and hi[1] > r.FS and lo[2] < 2.0), (o, lo)


def test_vitrine_52_in_the_nw_corner_behind_the_piano():
    """Request 2026-11-11: the Tegernsee set's narrow 52 element (a vitrine: base cabinet, glass door
    with glass shelves and wine glasses, cornice; 2.38 high, 42 deep) stands on the wall opposite the
    bookcase, behind the piano on the right: in the Bibliothek's NW corner (west wall x north wall),
    front to the east, clear of the piano and of the north window. Furniture (EG_Moebel)."""
    import regal as r
    xw, yn = r.VITRINE_AT
    assert (xw, yn) == (6.174, 12.473)
    box = [(m, lo, hi) for m, lo, hi in _parts(BP, ("EG", "EG_Moebel"))
           if lo[0] > xw - 1e-6 and hi[0] < 6.75 and lo[1] > 11.8 and hi[1] <= yn + 1e-6]
    xs = [lo[0] for _, lo, _ in box] + [hi[0] for _, _, hi in box]
    ys = [lo[1] for _, lo, _ in box] + [hi[1] for _, _, hi in box]
    assert min(xs) == pytest.approx(xw + 0.005) and max(ys) == pytest.approx(yn - 0.005)          # 5 mm off the walls
    case = [(m, lo, hi) for m, lo, hi in box if m.startswith("Nuss")]
    assert min(lo[1] for _, lo, _ in case) == pytest.approx(yn - 0.005 - 0.52 - 0.03)            # 52 + cornice
    assert max(hi[0] for _, _, hi in case) == pytest.approx(xw + 0.005 + 0.42 + 0.03)            # 42 + cornice
    assert max(hi[2] for _, _, hi in box) == pytest.approx(2.38)
    assert sum(m == "Glas" for m, _, _ in box) >= 12                                              # door, shelves, glasses
    piano = [(lo, hi) for m, lo, hi in _parts(BP, ("EG", "EG_Moebel")) if m == "Klavierlack"]
    assert max(xs) < min(lo[0] for lo, _ in piano) and max(xs) < 6.953                           # piano, north window


def _folded(bp, key, deg):
    """(down-state part box, vertices) per Part of object key, turned by deg/90 of its CRANK angle about
    the x axis through its PIVOT (deg 90: folded up); an object with a FOLD first folds about its own
    hinge (x) by the same share of its angle."""
    def rx(p, c, a):                                                      # turn p about the x axis through c
        y, z = p[1] - c[1], p[2] - c[2]
        return (p[0], c[1] + y * math.cos(a) - z * math.sin(a), c[2] + y * math.sin(a) + z * math.cos(a))
    g, piv = bp.geo[key], bp.pivot[key[1]]
    hinge, _, fdeg = (bp.fold or {}).get(key[1], (piv, None, 0.0))
    (axis, cdeg) = bp.crank[key[1]]
    assert axis == (1, 0, 0)
    move = lambda p: rx(rx(p, hinge, math.radians(fdeg * deg / 90)), piv, math.radians(cdeg * deg / 90))
    for (m, lo, hi), (first, n) in zip(_parts(bp, key), bp.parts[key]):
        yield (m, lo, hi), [move(g["v"][i]) for f in g["f"][first:first + n] for i in f]


def test_schrankbett_submodel():
    """Issue #7: code/schrankbett.py, the Yoga room's wall bed at its own origin (the room's inner NW
    corner since 2026-11-25: west wall x north wall; the room at y < 0, floor slab at z 0, 2.20 high):
    request 2026-11-25: on the north wall (opposite the old place by the Yoga door), slid into the corner
    with the west outer wall, no side cabinets, the bed 1.40 wide. A case 45 deep from the west wall, just
    as wide as the 1.46 niche plus its two sides, up to 3 mm under the ceiling, a Blende over the niche;
    the bed (lying area 1.40 x 2.00, one mattress) built folded down, an object of its own that folds up
    towards the north wall, -90 deg about x (CRANK); its feet an object of their own on the same axis that
    also fold onto the underside (FOLD +90 deg about their hinge); the underside framed with six raised
    panels like the doors (request 2026-11-13). With the pieces of the west wall (window) and the north wall."""
    import schrankbett as s
    bp = house_core.build_schrankbett()
    house_core.build()                                                    # restore the registries
    assert s.SCHRANKBETT_AT == (0.31, 12.485) and bp.garden is None
    assert {c for c, _ in bp.geo} == {"Schrankbett"}
    assert {"Schrankbett_Moebel", "Schrankbett_Klappbett", "Schrankbett_Klappfuesse", "Schrankbett_Waende"} <= {n for _, n in bp.geo}
    assert bp.crank == {"Schrankbett_Klappbett": ((1, 0, 0), -90), "Schrankbett_Klappfuesse": ((1, 0, 0), -90)}
    assert bp.pivot["Schrankbett_Klappfuesse"] == bp.pivot["Schrankbett_Klappbett"]
    (hx, hy, hz), axis, deg = bp.fold["Schrankbett_Klappfuesse"]
    assert list(bp.fold) == ["Schrankbett_Klappfuesse"] and axis == (1, 0, 0) and deg == 90
    assert hz == pytest.approx(s.ZU)                                     # hinged at the underside
    case = list(_parts(bp, ("Schrankbett", "Schrankbett_Moebel")))
    wood = [(lo, hi) for m, lo, hi in case if m != "Metall"]
    assert min(lo[0] for lo, _ in wood) == pytest.approx(0.0)            # in the corner with the west wall
    assert max(hi[1] for _, hi in wood) == pytest.approx(-0.005) and min(lo[1] for lo, _ in wood) == pytest.approx(-0.45)
    assert min(lo[2] for lo, _ in wood) == pytest.approx(0.012) and max(hi[2] for _, hi in wood) == pytest.approx(2.197)
    # the niche: what crosses the line z 1.0, y -0.2 is the two sides; between them 1.46 free, nothing beyond
    xs = sorted((lo[0], hi[0]) for lo, hi in wood if lo[1] < -0.2 < hi[1] and lo[2] < 1.0 < hi[2])
    assert len(xs) == 2
    n0, n1 = xs[0][1], xs[1][0]
    assert n1 - n0 == pytest.approx(1.46) and max(hi[0] for _, hi in wood) == pytest.approx(1.46 + 2 * 0.019)
    blende = [(lo, hi) for lo, hi in wood if lo[0] <= n0 + 1e-6 and hi[0] >= n1 - 1e-6 and lo[2] > 2.0]
    assert blende and min(lo[1] for lo, _ in blende) == pytest.approx(-0.45)
    # the bed, down: one mattress filling the 1.40 x 2.00 lying area, about 40 high, south of the case
    bed = list(_parts(bp, ("Schrankbett", "Schrankbett_Klappbett")))
    mat = [(lo, hi) for m, lo, hi in bed if m == "Leinen"]
    assert len(mat) == 1
    (mlo, mhi), = mat
    assert mhi[0] - mlo[0] == pytest.approx(1.40) and mhi[1] - mlo[1] == pytest.approx(2.0)
    assert 0.35 <= mhi[2] <= 0.50 and mlo[1] < -2.0 and mhi[1] < -0.1
    assert n0 < min(lo[0] for _, lo, _ in bed) and max(hi[0] for _, _, hi in bed) < n1
    face = [(m, lo, hi) for m, lo, hi in bed if lo[2] < s.ZU + 0.009]    # the underside: board, frame, fields
    assert len(face) >= 1 + 7 + 6 and min(lo[2] for _, lo, _ in face) == pytest.approx(s.ZU)
    feet = list(_parts(bp, ("Schrankbett", "Schrankbett_Klappfuesse")))
    assert len(feet) == 2 and all(lo[2] == pytest.approx(0.012) and hi[2] == pytest.approx(s.ZU) for _, lo, hi in feet)
    assert all(hi[1] < mlo[1] + 0.1 for _, lo, hi in feet)              # at the foot end (south)
    # walls: both plain (2026-11-25: the west window behind the bed is merged into the room's other one),
    # no window in the sub-model
    H = (lambda p: [m for m, lo, hi in _parts(bp, ("Schrankbett", "Schrankbett_Waende"))
                    if all(lo[k] - 1e-6 <= p[k] <= hi[k] + 1e-6 for k in range(2)) and lo[2] < p[2] < hi[2]])
    assert H((-0.15, -0.6, 1.5)) == ["Putz"] and H((-0.15, -1.5, 2.1)) == ["Putz"] and H((-0.15, -0.1, 1.5)) == ["Putz"]
    assert ("Schrankbett", "Schrankbett_Fenster_Tueren") not in bp.geo
    assert H((1.0, 0.15, 1.0)) == ["Putz"] and H((2.0, 0.15, 2.0)) == ["Putz"]


def test_schrankbett_fold_clears():
    """The bed folds up about its pivot (5 deg steps) without going through the case's back, the
    floor (finish 12 mm), the Blende or the ceiling, nor out of its niche sideways; folded up it lies
    in the case, its underside flush with the case's front (45 from the north wall). The feet fold onto the
    underside meanwhile: folded up they lie flat on it, standing out by their thickness only (3 cm).
    In the sub-model the room lies at y < 0: t = -y is the distance from the north wall."""
    import schrankbett as s
    bp = house_core.build_schrankbett()
    house_core.build()                                                    # restore the registries
    case = [(lo, hi) for m, lo, hi in _parts(bp, ("Schrankbett", "Schrankbett_Moebel")) if m != "Metall"]
    xs = sorted((lo[0], hi[0]) for lo, hi in case if lo[1] < -0.2 < hi[1] and lo[2] < 1.0 < hi[2])
    n0, n1 = next((a[1], b[0]) for a, b in zip(xs, xs[1:]) if b[0] > a[1] + 0.5)
    back = max(-lo[1] for lo, hi in case if -lo[1] < 0.05 and lo[0] <= n0 and hi[0] >= n1)
    under = min(lo[2] for lo, hi in case if lo[0] <= n0 + 1e-6 and hi[0] >= n1 - 1e-6 and lo[2] > 2.0)
    for o in ("Klappbett", "Klappfuesse"):
        key = ("Schrankbett", "Schrankbett_" + o)
        for deg in range(0, 91, 5):
            for (m, lo, hi), vs in _folded(bp, key, deg):
                for x, y, z in vs:
                    t = -y
                    assert n0 < x < n1 and z >= 0.012 - 1e-6 and t > back, (o, deg, m, x, t, z)
                    assert z < (under if t < 0.45 else 2.20) - 1e-6, (o, deg, m, x, t, z)
        for (m, lo, hi), vs in _folded(bp, key, 90):
            assert max(-y for _, y, _ in vs) <= 0.45 + (0.03 if o == "Klappfuesse" else 0.0) + 1e-6, (o, m, lo, hi)
            assert min(-y for _, y, _ in vs) >= 0.45 - 1e-6 or o == "Klappbett", (o, m, lo, hi)   # on the face


def test_schrankbett_built_into_the_house():
    """The Schrankbett stands in the Yoga room at SCHRANKBETT_AT on the OG floor, every part the same
    (case: furniture OG_Moebel; the bed and its feet: OG_Klappbett, OG_Klappfuesse, furniture, folding about x); the old Yoga
    bed is gone, and since 2026-11-25 nothing of the wall bed by the Yoga door; down, the bed lies inside the room,
    clear of the Yoga door's leaf, the north balcony door and the north wall's Wandlampe."""
    import schrankbett as s
    sub = house_core.build_schrankbett()
    house_core.build()                                                    # restore the registries
    (x0, y0), z0 = s.SCHRANKBETT_AT, house_core.Z_OG
    S = lambda bp, key, d=(0.0, 0.0, 0.0): {tuple(sorted({tuple(round(p[k] + d[k], 6) for k in range(3)) for p in ps}))
                                            for ps in _solids_pts(bp, key)}
    assert S(sub, ("Schrankbett", "Schrankbett_Moebel"), (x0, y0, z0)) <= S(BP, ("OG", "OG_Moebel"))
    for o in ("Klappbett", "Klappfuesse"):
        assert S(sub, ("Schrankbett", "Schrankbett_" + o), (x0, y0, z0)) == S(BP, ("OG", "OG_" + o))
        assert BP.crank["OG_" + o] == ((1, 0, 0), -90)
    (hx, hy, hz), axis, deg = sub.fold["Schrankbett_Klappfuesse"]
    assert BP.fold["OG_Klappfuesse"] == (pytest.approx((hx + x0, hy + y0, hz + z0)), axis, deg)
    px, py, pz = sub.pivot["Schrankbett_Klappbett"]
    assert BP.pivot["OG_Klappbett"] == pytest.approx((px + x0, py + y0, pz + z0))
    assert {"OG_Moebel", "OG_Klappbett", "OG_Klappfuesse"} <= BP.furniture
    assert not any(m == "Leinen" and lo[0] < 2.5 and lo[1] < 10.9 and hi[1] > 8.86
                   for m, lo, hi in _parts(BP, ("OG", "OG_Moebel")))                               # old bed
    bed = list(_parts(BP, ("OG", "OG_Klappbett"))) + list(_parts(BP, ("OG", "OG_Klappfuesse")))
    assert min(lo[0] for _, lo, _ in bed) > 0.31 and max(hi[1] for _, _, hi in bed) < 12.485
    assert min(lo[1] for _, lo, _ in bed) > 8.86 + 1.0                                        # well off the south wall
    yoga = [(m, lo, hi) for m, lo, hi in _parts(BP, ("OG", "OG_Moebel")) if lo[0] < 6.0 and lo[1] > 8.86 and hi[1] < 12.49
            and lo[2] > z0 - 0.1]
    assert yoga and all(hi[1] < 12.485 + 1e-6 and lo[1] > 12.0 and hi[0] < 1.82 for m, lo, hi in yoga)   # only the case, north
    lamp = [lo for m, lo, hi in _parts(BP, ("OG", "OG_Wandlampen")) if lo[1] > 12.2 and lo[0] < 3.0]
    assert lamp and max(hi[0] for m, lo, hi in yoga) < min(l[0] for l in lamp)              # the north lamp stays free
    _clear(bed, _leaf_boxes(BP, "OG", z0), "Yoga door leaf")


def _solids_pts(bp, key):
    """The vertices of each Part of object key."""
    g = bp.geo[key]
    return [[g["v"][i] for f in g["f"][a:a + n] for i in f] for a, n in bp.parts[key]]


def test_every_door_has_handles():
    """Request 2026-11-11: every door has handles. Hinged interior leaves (six-panel and glazed, also
    the swinging ones): black iron levers on both faces at the lock edge, 1.05 m; french and terrace
    doors (FD, GD): a handle on the room side of every leaf; sliding leaves (Bad, Speis): flush pulls
    on both faces. Front and back door had theirs already."""
    bp = house_core.build()
    for d in bp.doors:                                                    # the plan box covers the levers
        (x0, y0), (x1, y1) = d["leaf"]
        assert min(x1 - x0, y1 - y0) >= 0.14 - 1e-9 or d["w"] > 1.0, d
    for c in ("EG", "OG"):
        iron = [(lo, hi) for o in [n for cc, n in bp.geo if cc == c and "tuer" in n.lower()]
                for m, lo, hi in _parts(bp, (c, o)) if m == "Eisen"]
        leaves = [pts for cc, pts in house_core.LEAVES if cc == c]
        for pts in leaves:
            (ax, ay, az), (bx, by, bz) = pts
            box = [min(ax, bx) - 0.08, max(ax, bx) + 0.08, min(ay, by) - 0.08, max(ay, by) + 0.08]
            near = [(lo, hi) for lo, hi in iron if box[0] < lo[0] and hi[0] < box[1] and box[2] < lo[1] and hi[1] < box[3]
                    and abs((lo[2] + hi[2]) / 2 - min(az, bz) - 1.04) < 0.12]                 # 1.05 m above the floor
            thin = 0 if abs(bx - ax) < abs(by - ay) else 1                # the leaf's thin axis
            mid = (pts[0][thin] + pts[1][thin]) / 2
            assert any(hi[thin] < mid for lo, hi in near) and any(lo[thin] > mid for lo, hi in near), (c, pts)
    fo = [(m, lo, hi) for c in ("EG", "OG") for m, lo, hi in _parts(bp, (c, c + "_Fenster_Tueren"))]
    handles = [(lo, hi) for m, lo, hi in fo if m == "Metall"]
    for o in [o for o in house_core.OPENINGS if o["kind"] in ("FD", "GD")]:
        assert any(o["a"] - 1e-6 <= (lo[1] if o["ax"] == "y" else lo[0]) and (hi[1] if o["ax"] == "y" else hi[0]) <= o["b"] + 1e-6
                   and o["sill"] < lo[2] < o["head"] for lo, hi in handles), o


def test_window_and_balcony_door_handles():
    """The user (2026-11-16): „die Klinken der Fenster & Balkontüren … ersetze sie alle mit den Hebeln & Drehgriffen
    aus dem heutigen Input“. Every sash of every exterior window (W, also the big GD west windows) and every leaf of a
    french or terrace door (FD, GD from the floor) has one handle on its room side, on its stile towards the middle:
    doors the lever of input/2026-11-16 input/klinke-balkontüre.webp (oval rose 9 high centred 1.05 above the sill,
    ribbed neck, flat lever down to 13.5 under it); windows the turn handle of klinke-fenster.webp (pointed rose 7.5
    high at the sash's mid height, lever down to 10 under it). Rose, neck and lever, the rose shaped (at least 10
    corners; the old olive's was a box)."""
    bp = house_core.build()
    for o in [o for o in house_core.OPENINGS if o["kind"] in ("W", "FD", "GD")]:
        k, floor = (0, 1) if o["ax"] == "x" else (1, 0), house_core.Z_OG if o["sill"] >= house_core.Z_OG - 1e-6 else 0.0
        c = "OG" if floor else "EG"
        key = (c, c + "_Fenster_Tueren")
        corners = [len({tuple(round(x, 6) for x in v) for v in pts}) for pts in _solids_pts(bp, key)]
        ps = [(lo, hi, n) for (m, lo, hi), n in zip(_parts(bp, key), corners) if m == "Metall"
              and o["a"] < lo[k[0]] and hi[k[0]] < o["b"] and o["sill"] < lo[2] and hi[2] < o["head"]
              and abs((lo[k[1]] + hi[k[1]]) / 2 - o["face"]) < 0.6]
        groups = []                                                         # one handle = one axis u
        for lo, hi, nc in sorted(ps, key=lambda p: p[0][k[0]] + p[1][k[0]]):
            u = (lo[k[0]] + hi[k[0]]) / 2
            if groups and abs(groups[-1][0] - u) < 0.01:
                groups[-1][1].append((lo, hi, nc))
            else:
                groups.append((u, [(lo, hi, nc)]))
        n = max(2, round((o["b"] - o["a"]) / 0.95)) if o["kind"] == "GD" else 2 if o["b"] - o["a"] > 0.75 else 1
        assert len(groups) == n, (o, [g[0] for g in groups])
        door = o["kind"] in ("FD", "GD") and o["sill"] - floor < 0.1
        for u, g in groups:
            assert len(g) == 3 and g[0][2] >= 20, (o, u)                         # rose (2 x >= 10 corners), neck, lever
            top, bot = max(hi[2] for lo, hi, nc in g), min(lo[2] for lo, hi, nc in g)
            if door:
                assert abs(top - (o["sill"] + 1.05 + 0.045)) < 1e-6 and abs(bot - (o["sill"] + 1.05 - 0.135)) < 1e-6, (o, u)
            else:
                assert abs(top - bot - 0.1375) < 1e-6 and abs(top - 0.0375 - (o["sill"] + o["head"]) / 2) < 0.03, (o, u)


def test_west_og_windows_wall_below_up_to_the_ceiling():
    """The tall west windows in the OG (Yoga, Bad): no fixed glazing below any more but
    wall (sill 0.75 m above the floor: first 0.95, then twice 10 cm lower), and up to the ceiling.
    Request 2026-11-25: the Yoga room's window behind the wall bed (y 11.26 .. 12.23) is merged into its
    other one, which grows twice as wide (0.99 -> 1.98, both together), northwards from its south jamb,
    ending before the wall bed's case (y 10.987)."""
    house_core.build()                                                     # OPENINGS of the house
    west = [o for o in house_core.OPENINGS if o["ax"] == "y" and o["face"] == 0 and o["sill"] >= house_core.Z_OG - 1e-9
            and o["head"] > 4.0 and o["b"] - o["a"] > 0.9]
    assert sorted((round(o["a"], 3), round(o["b"], 3)) for o in west) == [(6.77, 7.76), (8.96, 10.94)]
    assert 10.94 < house_core.schrankbett.SCHRANKBETT_AT[1] - house_core.schrankbett.W   # clear of the case
    assert all(round(o["sill"] - house_core.Z_OG, 3) == 0.75 and o["head"] == house_core.Z_OG_TOP and o["kind"] == "W"
               for o in west)
    g = BP.geo[("OG", "OG_Fenster_Tueren")]
    glass = {i for f, m in zip(g["f"], g["m"]) if m == "Glas" for i in f}
    assert not any(g["v"][i][0] < 0.31 and g["v"][i][2] < house_core.Z_OG + 0.75 for i in glass)
    clad = BP.geo[("Dach", "Verschalung_West")]                            # no iron bars (small windows only)
    bars = [clad["v"][i] for f, m in zip(clad["f"], clad["m"]) if m == "Eisen" for i in f]
    assert bars and not any(any(o["a"] < y < o["b"] for o in west) and z > house_core.Z_OG for _, y, z in bars)


def test_grosseltern_werkstattofen():
    """Oma & Opa (issue #4): the Bibliothek's workshop stove once more, in the bedroom's NW corner
    between the north wall and the 14 cm wall stub north of the Bad opening, turned 45° to face
    the room (SE); an object of its own, so the Bibliothek's stays as it is."""
    ofen = BP.geo[("EG", "EG_Werkstattofen_Grosseltern")]
    lo = [min(p[k] for p in ofen["v"]) for k in range(3)]
    hi = [max(p[k] for p in ofen["v"]) for k in range(3)]
    assert 2.657 + 0.09 < lo[0] < 2.657 + 0.15 and 12.473 - 0.15 < hi[1] < 12.473 - 0.09   # in the corner
    assert 0.55 < hi[0] - lo[0] < 0.65 and 1.0 <= hi[2] <= 1.1                         # turned 45°
    assert len(ofen["v"]) == len(BP.geo[("EG", "EG_Werkstattofen")]["v"])             # same stove
    (fire,) = [f for f in BP.fires if lo[0] < f["base"][0] < hi[0] and lo[1] < f["base"][1] < hi[1]]
    assert abs(fire["u"][0] - fire["u"][1]) < 1e-6 and fire["u"][0] < -0.7 and fire["collection"] == "EG"  # faces SE
    assert "EG_Werkstattofen_Grosseltern" not in BP.furniture                         # built in


def test_fires_are_recorded_where_the_stoves_burn():
    """The flames are no longer static geometry: every stove records its fire (base = centre of
    the flame bed in the flame plane, u = unit along the width, w, h, d) in FIRES, and the
    animated fire component (code/fire.py, web/src/fire.js) draws them. Five in the house (Stube
    Ofen, Bibliothek, Oma & Opa and Schlafen SE workshop stoves, Küche Herd), one in the Ofen sub-model."""
    assert len(BP.fires) == 6 and len(house_core.build_ofen().fires) == 2   # the Ofen: front + back door
    house_core.build()                                                    # restore the registries
    assert not any(m == "Feuer" for g in BP.geo.values() for m in g["m"])

    def inside(f, key, pad=0.02):
        v = BP.geo[key]["v"]
        return all(min(p[k] for p in v) - pad <= f["base"][k] <= max(p[k] for p in v) + pad for k in range(3))

    for f in BP.fires:
        assert abs(math.hypot(*f["u"]) - 1) < 1e-9 and 0 < f["w"] < 0.6 and 0 < f["h"] < 0.5 and 0 < f["d"] < 0.02
    assert sum(inside(f, ("EG", "EG_Ofen_Feuertuer")) for f in BP.fires) == 1
    assert sum(inside(f, ("EG", "EG_Ofen_Hintertuer")) for f in BP.fires) == 1
    assert sum(inside(f, ("EG", "EG_Werkstattofen")) for f in BP.fires) == 1
    assert sum(inside(f, ("EG", "EG_Werkstattofen_Grosseltern")) for f in BP.fires) == 1
    assert sum(inside(f, ("OG", "OG_Werkstattofen")) for f in BP.fires) == 1
    assert sum(inside(f, ("EG", "EG_Herd")) for f in BP.fires) == 1
    og = next(f for f in BP.fires if f["base"][2] > house_core.Z_OG)
    assert abs(og["u"][0] - math.cos(math.radians(-135))) < 1e-9                     # turned with its stove
    # each fire knows the collection of its stove, so the viewer's cutaway hides it with the storey
    assert [f["collection"] for f in BP.fires].count("OG") == 1 and og["collection"] == "OG"
    assert all(f["collection"] == ("OG" if f is og else "EG") for f in BP.fires)
    assert [f["collection"] for f in house_core.build_ofen().fires] == ["Ofen", "Ofen"]
    house_core.build()                                                    # restore the registries


def test_ofen_back_door_to_the_flur():
    """The Ofen can also be fed from the Flur: a second fire door on its back (the wall side,
    sub-model x = 0); in the house it sits flush in the Flur face of the Stube/Flur wall
    (y 6.349), through an opening in that wall, with its own fire behind the glass."""
    sub = house_core.build_ofen()
    v = sub.geo[("Ofen", "Ofen_Hintertuer")]["v"]
    assert -0.03 - 1e-9 <= min(x for x, _, _ in v) and max(x for x, _, _ in v) <= 1e-9          # on the x = 0 face
    assert 0.4 < min(y for _, y, _ in v) and max(y for _, y, _ in v) < 1.0
    house_core.build()
    hv = BP.geo[("EG", "EG_Ofen_Hintertuer")]["v"]
    assert 6.349 - 0.01 <= min(y for _, y, _ in hv) and max(y for _, y, _ in hv) <= 6.349 + 0.031   # flush in the Flur face
    xs = [x for x, _, _ in hv]
    g = BP.geo[("EG", "EG_Waende")]
    for first, n in BP.parts[("EG", "EG_Waende")]:                      # the wall is open there
        ps = [g["v"][i] for f in g["f"][first:first + n] for i in f]
        lo = [min(p[k] for p in ps) for k in range(3)]; hi = [max(p[k] for p in ps) for k in range(3)]
        assert not (lo[0] < (min(xs) + max(xs)) / 2 < hi[0] and lo[1] < 6.1 < hi[1] and lo[2] < 0.68 < hi[2])


def test_ofen_bed_wandlampe():
    """Issue #22: over the Ofen bed's head end hangs the house's standard Wandlampe (it replaces the small
    gooseneck reading lamp), rosette at 2.10 on the head-end wall; in the house on the Stube's west wall
    (the Ofen 4 mm off it) facing east, its light among the wall lights. No always-on lamps any more."""
    sub = house_core.build_ofen()
    assert ("Ofen", "Ofen_Lampe") not in sub.geo
    assert _rosettes(sub, ("Ofen", "Ofen_Wandlampen")) == [((0.35, 0.0), 2.1, (0, 1))] and len(sub.wall_lights) == 1
    house_core.build()
    assert ("EG", "EG_Ofen_Lampe") not in BP.geo
    assert _rosettes(BP, ("EG", "EG_Ofen_Wandlampen")) == [((9.06, 5.495), 2.1, (1, 0))]
    assert any(math.dist(p, (9.06 + 0.5, 5.495, 2.05)) < 1e-6 for p in BP.wall_lights)
    assert not hasattr(BP, "lamp_lights") and not hasattr(house_core, "LAMP_LIGHTS")
    assert "GluehfadenAn" not in house_core.MAT_DEF and len(BP.outside_lights) == 8


def test_east_og_balcony_windows_are_french_doors():
    """The three east OG windows onto the long balcony (Schlafen SE y 1.74, 4.15; Schlafen NE
    y 9.86) are balcony doors now (on request), floor to 4.60 like the other french doors."""
    house_core.build()
    east = {round(o["a"], 2): o for o in house_core.OPENINGS
            if o["ax"] == "y" and o["face"] == house_core.W_OUT and o["sill"] >= house_core.Z_OG - 1e-9}
    for a in (1.74, 4.15, 9.86):
        assert east[a]["kind"] == "FD" and east[a]["sill"] == house_core.Z_OG and east[a]["head"] == 4.60


def part_list(key):
    """(material, lo, hi, vertices) per Part of object key."""
    g = BP.geo[key]
    for first, n in BP.parts[key]:
        vs = [g["v"][i] for f in g["f"][first:first + n] for i in f]
        yield g["m"][first], [min(p[k] for p in vs) for k in range(3)], [max(p[k] for p in vs) for k in range(3)], vs


def test_esstisch_after_tisch_briol():
    """Dining table after input/2026-11-05 input/tisch-briol.png: one table 2.00 m long (request
    2026-11-10, before two joined), in the middle of the former two, 8 chairs (3 per long side, one
    at each end); a top of three boards on an apron set back from its edge, legs splayed out mainly
    along the length, standing on a flat foot frame that rests on corner blocks; all inside the
    top's footprint, since the chairs stand right at its edge."""
    parts = list(part_list(("EG", "EG_Tisch")))
    x0, x1, cx = 5.055, 7.055, 6.055
    assert all(lo[0] >= x0 - 1e-9 and hi[0] <= x1 + 1e-9 and lo[1] >= 1.18 - 1e-9 and hi[1] <= 1.91 + 1e-9
               for _, lo, hi, _ in parts)
    boards = [p for p in parts if abs(p[2][2] - 0.76) < 1e-9]
    assert len(boards) == 3 and all(0.04 <= hi[2] - lo[2] <= 0.05 for _, lo, hi, _ in boards)
    assert {(round(lo[0], 6), round(hi[0], 6)) for _, lo, hi, _ in boards} == {(x0, x1)}       # 2.00 long
    blocks = [p for p in parts if abs(p[1][2] - 0.012) < 1e-9]
    assert len(blocks) == 4 and all(hi[2] < 0.08 for _, _, hi, _ in blocks)
    rails = [p for p in parts if p[1][2] > 0.05 and p[2][2] < 0.1 and p[2][2] - p[1][2] <= 0.03]
    assert len(rails) == 4 and all(min(hi[0] - lo[0], hi[1] - lo[1]) >= 0.08 for _, lo, hi, _ in rails)   # flat boards
    legs = [p for p in parts if p[0] == "FichteZ" and p[2][2] - p[1][2] > 0.5]
    assert len(legs) == 4
    for _, lo, hi, vs in legs:
        foot = [p for p in vs if p[2] < 0.2]; head = [p for p in vs if p[2] > 0.5]
        mean = lambda ps, k: sum(p[k] for p in ps) / len(ps)
        assert abs(mean(foot, 0) - cx) - abs(mean(head, 0) - cx) >= 0.08           # splayed along x
        assert 0 <= abs(mean(foot, 1) - 1.545) - abs(mean(head, 1) - 1.545) <= 0.05  # a little across
    seats = [p for p in part_list(("EG", "EG_Stuehle")) if abs(p[2][2] - 0.46) < 0.005 and p[2][2] - p[1][2] >= 0.04
             and p[2][1] < 2.5 and p[2][0] < 8.5]                                   # at the dining table
    assert len(seats) == 8
    centres = sorted((round((lo[0] + hi[0]) / 2, 3), round((lo[1] + hi[1]) / 2, 3)) for _, lo, hi, _ in seats)
    assert sum(abs(y - 1.545) < 0.01 for _, y in centres) == 2                  # one at each end
    assert min(x for x, _ in centres) < x0 and max(x for x, _ in centres) > x1
    sides = [x for x, y in centres if abs(y - 1.545) > 0.3]
    assert len(sides) == 6 and all(x0 + 0.2 < x < x1 - 0.2 for x in sides)


def test_stube_sitzecke_in_the_se_corner():
    """Small seating corner in the Stube, in the corner between the two big windows (south wall
    face y 0.415, east wall face x 14.351): a round pedestal side table (input/2026-11-05 input/
    tischchen.jpeg: turned column, three curved feet) and two small cocktail armchairs (sessel-klein.jpg:
    bouclé upholstery with piping, flared back, splayed wooden legs), one either side of it; loose
    furniture of the "Eingerichtet" stage."""
    assert {"Boucle", "Paspel", "TeakX", "TeakZ"} <= set(house_core.MAT_DEF)
    parts = [p for p in part_list(("EG", "EG_Moebel")) if p[0] in ("Boucle", "Paspel", "TeakX", "TeakZ")]
    assert parts and "EG_Moebel" in BP.furniture
    lo = [min(p[1][k] for p in parts) for k in range(3)]; hi = [max(p[2][k] for p in parts) for k in range(3)]
    assert 12.4 < lo[0] and hi[0] <= 14.351 - 0.01 and lo[1] >= 0.415 + 0.01 and hi[1] < 2.4   # in the corner
    assert lo[2] >= 0.012 - 1e-9 and hi[2] < 0.9
    seats = [p for p in parts if p[0] == "Paspel"]                                    # one piping per chair
    assert len(seats) == 2
    (ax, ay), (bx, by) = [((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2) for _, lo, hi, _ in seats]
    assert abs((14.351 - ax) - (by - 0.415)) < 0.02 and abs((ay - 0.415) - (14.351 - bx)) < 0.02   # mirror images
    top = max((p for p in parts if p[0] == "TeakX"), key=lambda p: p[2][2])
    tx, ty = (top[1][0] + top[2][0]) / 2, (top[1][1] + top[2][1]) / 2
    assert abs((14.351 - tx) - (ty - 0.415)) < 0.01 and 0.6 < top[2][2] < 0.75       # on the diagonal
    assert 0.45 <= top[2][0] - top[1][0] <= 0.6                                        # small round top
    assert min(math.dist((tx, ty), (x, y)) for x, y in ((ax, ay), (bx, by))) > 0.5     # chairs either side


def test_og_flur_bauernschrank_between_the_two_doors():
    """Request 2026-11-25: on the OG Flur wall between the two doors to the south rooms (wall face y 6.35),
    where the Waschtisch with its basin, mirror and two lamps stood (#40, #19), a big Bauernschrank:
    old pine like the Waschtisch, centred between the two door openings, 1.80 wide, 60 deep (follow-up
    2026-11-25; the Rundgang passes further north), about 2.05 high under the 2.20 ceiling; two doors with
    raised panels, iron knobs; furniture (stage Eingerichtet); clear of the door leaves."""
    zo = house_core.Z_OG
    wall = [p for p in part_list(("OG", "OG_Waende")) if abs(p[1][1] - 6.06) < 1e-6 and abs(p[2][1] - 6.35) < 1e-6
            and abs(p[1][2] - zo) < 1e-6 and p[1][0] < 6.5 < p[2][0]]
    assert len(wall) == 1 and wall[0][0] == "Putz"                                      # full height, plain plaster
    wa, wb = wall[0][1][0], wall[0][2][0]
    X = (wa + wb) / 2
    near = lambda p: p[2][1] <= 7.3 and p[1][1] >= 6.35 - 1e-9 and wa < p[2][0] and p[1][0] < wb and p[1][2] > zo - 0.1
    for o in ("Sanitaer", "Spiegel", "Wandlampen", "Fliesen"):                         # basin, mirror, lamps gone
        assert not [p for p in part_list(("OG", "OG_" + o)) if near(p)], o
    sch = [p for p in part_list(("OG", "OG_Moebel")) if near(p)]
    wood = [p for p in sch if p[0] in ("Innentuer", "Stufe")]
    assert len(wood) >= 20 and {p[0] for p in sch} == {"Innentuer", "Stufe", "Eisen"}
    lo = [min(p[1][k] for p in sch) for k in range(3)]; hi = [max(p[2][k] for p in sch) for k in range(3)]
    assert abs((lo[0] + hi[0]) / 2 - X) < 1e-6 and 1.80 <= hi[0] - lo[0] <= 1.90       # centred, 1.80 + cornice
    assert abs(lo[1] - 6.35) < 1e-6 and 0.60 <= hi[1] - 6.35 <= 0.65                    # against the wall, 60 deep
    assert abs(lo[2] - (zo + 0.012)) < 1e-6 and 2.0 <= hi[2] - zo <= 2.10              # under the ceiling
    leaves = sorted((p for p in wood if p[2][0] - p[1][0] > 0.6 and p[2][2] - p[1][2] > 1.5 and p[1][1] > 6.35 + 0.4),
                    key=lambda p: p[1][0])
    assert len(leaves) == 2 and leaves[0][2][0] < X < leaves[1][1][0]                  # two doors
    assert len([p for p in wood if p[2][1] > 6.35 + 0.60 and p[2][2] - p[1][2] > 0.35 and p[2][2] - p[1][2] < 1.0]) == 4
    assert len([p for p in sch if p[0] == "Eisen"]) >= 2
    assert "OG_Moebel" in BP.furniture
    _clear([(m, a, b) for m, a, b, _ in sch], _leaf_boxes(BP, "OG", zo), "door leaf")



def test_waschkueche_dryer_on_the_washer_and_table_along_the_back_wall():
    """Waschküche (OG, x 5.59 .. 8.59, y 2.79 .. 6.06, door in the north wall): a dryer stands on
    the washing machine at the east wall, and a table 0.80 m deep runs the full width
    of the back (south) wall, with two stacks of neatly folded clothes on it; it replaces the low
    cupboard that stood in the SE corner. The user (follow-up to #29): „In der Waschküche reichen zwei
    Waschmaschinen … behalte den Turm … nimm die dritte, die daneben steht weg. Dadurch können die beiden
    Waschmaschinen, die übereinander stehen, etwas näher an den Tisch verrutschen“: the tower only, 3–5 cm
    from the table."""
    zo = house_core.Z_OG
    room = [p for p in part_list(("OG", "OG_Moebel")) if 5.59 <= p[1][0] and p[2][0] <= 8.59 and 2.79 <= p[1][1] and p[2][1] <= 6.06]
    enamel = sorted((p for p in room if p[0] == "Emaille"), key=lambda p: (p[1][1], p[1][2]))
    assert len(enamel) == 2                                                   # the tower: washer + dryer
    washer, dryer = enamel
    assert dryer[1][:2] == washer[1][:2] and dryer[2][:2] == washer[2][:2]     # same footprint
    assert abs(dryer[1][2] - washer[2][2]) < 0.002                            # stands on it
    assert 8.59 - washer[2][0] < 0.01                                         # against the east wall
    top = [p for p in room if p[0] == "FichteX" and p[2][2] > zo + 0.7]
    assert len(top) == 1
    _, lo, hi, _ = top[0]
    assert lo[0] - 5.59 < 0.01 and 8.59 - hi[0] < 0.01 and lo[1] - 2.79 < 0.01   # full width, on the back wall
    assert 0.03 <= washer[1][1] - hi[1] <= 0.05                               # the tower 3–5 cm from the table
    assert hi[1] - lo[1] > 0.78                                               # deep enough to fold on
    assert enamel[-1][2][1] < 5.5                                             # machines clear of the door
    cloth = [p for p in room if p[0] in ("Leinen", "Bettwaesche", "Creme", "Jeans", "Wolle")
             and abs(p[1][2] - hi[2]) < 0.30 and lo[0] <= p[1][0] and p[2][0] <= hi[0] and p[2][1] <= hi[1]]
    assert cloth and min(p[1][2] for p in cloth) >= hi[2] - 0.001             # on the table top
    stacks = {}
    for q in cloth:
        assert q[2][2] - q[1][2] <= 0.05                                      # folded, flat
        stacks.setdefault(round((q[1][0] + q[2][0]) / 2, 1), []).append(q)
    assert len(stacks) == 2 and all(len(v) >= 5 for v in stacks.values())
    for v in stacks.values():                                                 # neat: piled on each other
        v.sort(key=lambda q: q[1][2])
        assert all(abs(b[1][2] - a[2][2]) < 0.002 for a, b in zip(v, v[1:]))
    assert not [p for p in room if p[0] == "FichteZ" and p[2][2] - zo > 0.85
                and p[1][0] > 7.9 and p[2][1] < 3.4]                          # SE corner cupboard gone


def test_waschkueche_ohne_dusche():
    """Issue #61: the shower cabin of #29 in the Waschküche's NW corner is gone: no glass, no shower head or drain,
    no limestone on the west and north walls; the floor stays the room's limestone (#28); the basket cupboard runs
    again up to y 5.95 (as before #29) and the room door's leaf (open 90°) stays clear of it."""
    zo, (x0, x1, y0, y1) = house_core.Z_OG, waschkueche.ROOM
    assert not hasattr(waschkueche, "DUSCHE") and not hasattr(waschkueche, "dusche")
    room = lambda lo, hi: x0 - 0.05 < lo[0] and hi[0] < x1 + 0.05 and y0 - 0.05 < lo[1] and hi[1] < y1 + 0.05
    san = [(m, lo, hi) for m, lo, hi in _parts(BP, ("OG", "OG_Sanitaer")) if room(lo, hi)]
    assert not [1 for m, lo, hi in san if m == "Glas"]
    assert not [1 for m, lo, hi in san if hi[0] < 7.0]                         # only the Briol on the east wall
    assert not [1 for m, lo, hi in _parts(BP, ("OG", "OG_Fliesen")) if room(lo, hi) and m == "Kalkstein"]
    assert _floor_at("OG", 6.1, 5.5) == "Kalkstein"


def test_waschkueche_basin():
    """Issue #29: a basin on the Waschküche's east wall north of the washer tower, on Taubenblau tiles 84 wide
    (12 beyond it each side) on the wall behind it, a mirror 80 x 85 in a 10 cm wooden frame above (bottom 1.17),
    the tower's Wandlampe centred over it at 2.10; ≥ 5 cm outside the room door leaf's sweep, 60 cm free in front,
    clear of the machines. The user's follow-up („das Waschbecken kann auch noch etwas in diese Richtung und von der
    Tür weg“): moved south with the tower, centred y 4.70 (was 5.28), the tiles 3 cm and the basin 15 cm from the
    tower. Then („anstatt unseres Standard-Waschbeckens das große Waschbecken aus dem Briol“): the deep ceramic sink
    of input/2026-11-05 input/waschbecken-briol.jpeg, 60 x 45, rim at 85, 30 high, hollow, hung on the wall (no
    Ständer: nothing of it below 35), two wall taps with cross handles side by side above it, under the mirror."""
    zo, T, by = house_core.Z_OG, house_core.WC_TILE_T, waschkueche.BY
    assert by == 4.70
    face = 8.59 - T                                                             # the tiles' face
    parts = [(m, lo, hi) for m, lo, hi in _parts(BP, ("OG", "OG_Sanitaer")) if m in ("Keramik", "Metall")
             and lo[0] > face - 0.48 and hi[0] <= face + 0.002 and by - 0.33 < lo[1] and hi[1] < by + 0.33
             and zo < lo[2] and hi[2] < zo + 1.17]
    ker = [(lo, hi) for m, lo, hi in parts if m == "Keramik"]
    assert len(ker) >= 8                                                        # hollow, with a lip, not a block
    assert abs(min(lo[1] for lo, hi in ker) - (by - 0.30)) < 1e-6 and abs(max(hi[1] for lo, hi in ker) - (by + 0.30)) < 1e-6
    assert abs(max(hi[0] for lo, hi in ker) - face) < 1e-6 and abs(min(lo[0] for lo, hi in ker) - (face - 0.45)) < 1e-6
    assert abs(max(hi[2] for lo, hi in ker) - (zo + 0.85)) < 1e-6 and abs(min(lo[2] for lo, hi in ker) - (zo + 0.55)) < 1e-6
    bowl = (face - 0.22, by, zo + 0.62)                                         # deep inside the bowl: empty
    assert not any(all(lo[k] < p < hi[k] for k, p in enumerate(bowl)) for lo, hi in ker)
    assert min(lo[2] for m, lo, hi in parts) > zo + 0.35                        # wall-hung, no Ständer
    taps = {round((lo[1] + hi[1]) / 2 - by, 2) for m, lo, hi in parts
            if m == "Metall" and hi[0] > face - 0.005 and zo + 1.0 < lo[2] and hi[2] < zo + 1.15}
    assert taps == {-0.07, 0.07}                                                # two wall taps, rosettes on the tiles
    fl = ("OG", "OG_Fliesen")
    assert {_part_at(fl, 8.582, by + d, z) for d in (-0.38, 0, 0.38) for z in (zo + 0.2, zo + 0.9)} <= {"Fliese", None}
    assert "Fliese" in {_part_at(fl, 8.582, by + d, zo + 0.5) for d in (-0.28, -0.23)}
    tiles = [(lo, hi) for m, lo, hi in _parts(BP, fl) if lo[0] > 8.5 and hi[0] < 8.6 and 3.6 < lo[1] and hi[1] < 6.06 and lo[2] < zo + 1.2]
    assert abs(min(lo[1] for lo, hi in tiles) - (by - 0.42)) < 0.01 and abs(max(hi[1] for lo, hi in tiles) - (by + 0.42)) < 0.01
    tower = max(hi[1] for m, lo, hi in _parts(BP, ("OG", "OG_Moebel")) if m == "Emaille" and lo[0] > 7.9)
    assert 0.02 <= min(lo[1] for lo, hi in tiles) - tower <= 0.04                # the tiles 3 cm from the tower
    assert 0.13 <= min(lo[1] for m, lo, hi in parts) - tower <= 0.17             # the basin about 15 cm from it
    frame = [(lo, hi) for m, lo, hi in _parts(BP, ("OG", "OG_Spiegel")) if m == "Kiefer" and lo[0] > 8.5 and 3.6 < lo[1] < 6.0]
    assert len(frame) == 4
    assert abs(min(lo[1] for lo, hi in frame) - (by - 0.40)) < 1e-6 and abs(max(hi[1] for lo, hi in frame) - (by + 0.40)) < 1e-6
    assert abs(min(lo[2] for lo, hi in frame) - (zo + 1.17)) < 1e-6 and abs(max(hi[2] for lo, hi in frame) - (zo + 2.02)) < 1e-6
    assert ((8.59, by), round(zo + house_core.WANDLAMPE_SPIEGEL_H, 3), (-1, 0)) in \
        [((round(x, 3), round(y, 3)), z, f) for (x, y), z, f in _rosettes(BP, ("OG", "OG_Wandlampen"))]
    door, = [d for d in BP.doors if d["c"] == "OG" and abs(d["hinge"][1] - 6.06) < 0.01 and 7.1 < d["hinge"][0] < 7.2]
    h = door["hinge"][:2]
    r = max(math.dist(h, p[:2]) for p in door["leaf"])
    corners = lambda lo, hi: [(x, y) for x in (lo[0], hi[0]) for y in (lo[1], hi[1])]
    assert all(math.dist(h, p) >= r + 0.05 for m, lo, hi in parts for p in corners(lo, hi))   # outside the sweep
    machines = [(lo, hi) for m, lo, hi in _parts(BP, ("OG", "OG_Moebel")) if m == "Emaille" and lo[0] > 7.9]
    _clear(parts, machines, "machines")
    bl, bh = [min(lo[k] for m, lo, hi in parts) for k in range(3)], [max(hi[k] for m, lo, hi in parts) for k in range(3)]
    front = ((bl[0] - 0.60, bl[1], zo + 0.05), (bl[0], bh[1], zo + 1.8))
    for o in ("Moebel", "Sanitaer", "Fliesen", "Spiegel", "Wandlampen"):
        _clear(list(_parts(BP, ("OG", "OG_" + o))), [front], o)


def test_waschkueche_open_cupboard_with_laundry_baskets_on_the_west_wall():
    """Waschküche: on the right-hand wall seen from the door (west, x 5.59) an open spruce
    cupboard, 2.0 m high, from the table to y 5.95 (#61: the shower cabin of #29 gone, as before it): two sides,
    continuous shelves without dividers, three coarsely woven wicker laundry baskets per shelf."""
    zo = house_core.Z_OG
    room = [p for p in part_list(("OG", "OG_Moebel")) if 5.59 <= p[1][0] and p[2][0] <= 8.59 and 2.79 <= p[1][1] and p[2][1] <= 6.06]
    table = [p for p in room if p[0] == "FichteX" and p[2][2] > zo + 0.7][0]
    carcass = [p for p in room if p[0] in ("FichteY", "FichteZ") and p[2][0] < 6.3 and p[1][1] > table[2][1]]
    assert carcass
    lo = [min(p[1][k] for p in carcass) for k in range(3)]; hi = [max(p[2][k] for p in carcass) for k in range(3)]
    assert 5.59 < lo[0] < 5.62 and hi[0] - lo[0] > 0.5                       # against the west wall
    assert abs(hi[2] - zo - 2.0) < 0.01
    leaf = [l for c, l in house_core.LEAVES if c == "OG" and 7.0 < max(l[0][0], l[1][0]) < 7.3
            and 5.0 < min(l[0][1], l[1][1]) < 6.06][0]                       # (open 90°, #29)
    assert table[2][1] < lo[1] and hi[0] < min(leaf[0][0], leaf[1][0])        # clear of table and leaf
    assert abs(hi[1] - 5.95) < 1e-6                                           # to 5.95 (#61)
    uprights = [p for p in carcass if p[0] == "FichteZ" and p[2][0] - p[1][0] > 0.3]
    assert len(uprights) == 2                                                 # the two sides, no dividers
    boards = [p for p in carcass if p[0] == "FichteY" and p[2][2] - p[1][2] < 0.03]
    assert len(boards) == 4 and all(b[2][1] - b[1][1] > hi[1] - lo[1] - 0.05 for b in boards)   # continuous
    baskets = [p for p in room if p[0] == "Weide"]
    bottoms = [p for p in baskets if p[2][2] - p[1][2] < 0.02]
    assert len(bottoms) == 9
    assert len(baskets) > 9 * 100                                             # woven from strands
    front = [p for p in baskets if 0.02 < p[2][2] - p[1][2] < 0.04 and p[1][2] - bottoms[0][1][2] < 0.2
             and abs(p[2][0] - bottoms[0][2][0]) < 0.015 and p[2][1] - p[1][1] > p[2][0] - p[1][0]]
                                                                              # weavers along the fronts
    assert len({round(p[2][0], 3) for p in front}) == 2                       # strands in and out: a weave
    assert all(lo[k] <= p[1][k] and p[2][k] <= hi[k] for p in baskets for k in range(3))   # inside it
    laundry = [p for p in room if p[0] in ("Leinen", "Bettwaesche", "Creme")]
    assert all(any(b[1][0] < p[1][0] and p[2][0] < b[2][0] and b[1][1] < p[1][1] and p[2][1] < b[2][1]
                   and abs(p[1][2] - b[2][2]) < 0.002 for p in laundry) for b in bottoms)   # laundry in each


def test_stube_sofa_facing_the_corner_pier():
    """Stube: a three-seater sofa after input/2026-11-05 input/sofa.tiff (linen, low base, square
    arms, loose seat and back cushions, two scatter pillows), facing the corner pier between the
    two big windows (room corner 14.351, 0.415); its centre 3/4 of the way from there to the Ofen
    block's room corner (10.96, 4.64, bed included)."""
    s, o = (14.351, 0.415), (10.96, 4.64)
    c = (s[0] + 0.75 * (o[0] - s[0]), s[1] + 0.75 * (o[1] - s[1]))
    linen = [p for p in part_list(("EG", "EG_Moebel")) if p[0] == "Leinen" and 9.06 < p[1][0] and p[2][1] < 5.85]
    vs = [v for p in linen for v in p[3]]
    assert len(linen) >= 3 + 3 + 3 + 2                              # base + arms/back, 3 + 3 cushions, 2 pillows
    lo = [min(v[k] for v in vs) for k in range(3)]; hi = [max(v[k] for v in vs) for k in range(3)]
    cx, cy = sum(v[0] for v in vs) / len(vs), sum(v[1] for v in vs) / len(vs)
    d = ((s[0] - c[0]) / math.dist(s, c), (s[1] - c[1]) / math.dist(s, c))   # towards the pier
    u = (-d[1], d[0])
    along = [(v[0] - c[0]) * u[0] + (v[1] - c[1]) * u[1] for v in vs]
    across = [(v[0] - c[0]) * d[0] + (v[1] - c[1]) * d[1] for v in vs]
    assert 2.1 <= max(along) - min(along) <= 2.4                    # three seats
    assert abs(max(along) + min(along)) < 0.02 and abs(max(across) + min(across)) < 0.02   # centred on c
    assert 0.85 <= max(across) - min(across) <= 1.05 and 0.7 <= hi[2] <= 0.95
    for _, _, phi, pv in linen:                                     # back cushions, pillows: away from the pier
        if phi[2] > 0.8:
            assert sum((v[0] - c[0]) * d[0] + (v[1] - c[1]) * d[1] for v in pv) < 0


def test_back_windfang_door_glazed_like_the_front_one():
    """The door between the Flur and the back Windfang (wall x 2.358 .. 2.657, opening y 7.408 ..
    8.506) is glazed like the front Windfang door (door_windfang.jpg): frosted glass above,
    raised panels below; one leaf, opened 90° into the Windfang."""
    glass = [p for p in part_list(("EG", "EG_Innentueren")) if p[0] == "Milchglas"]
    back = [p for p in part_list(("EG", "EG_Windfangtuer")) if p[0] == "Milchglas"     # own object: it swings
            and p[2][0] < 2.358 + 0.01 and 7.3 < p[1][1] and p[2][1] < 8.6]
    front = [p for p in glass if p[1][0] > 12.0]
    assert len(back) == 1 and len(front) == 2
    _, lo, hi, _ = back[0]
    assert hi[2] - lo[2] > 0.7 and lo[2] > 0.9                       # upper part of the leaf


KUECHE_EAST = 8.557                                                           # east wall face of the Küche


def test_kueche_wamsler_herd_at_the_north_end_of_the_east_run():
    """Küche: a wood-fired Wamsler cooker after input/2026-11-05 input/wamsler.jpeg (stainless
    steel since 2026-11-10, steel top with a rail, fire door with glass top left, ash door below, oven door with a
    window on the right, full-width drawer, flue on top) stands at the north end of the east run
    (where the plan draws the flue), front facing west, flush with the run's fronts; the run and
    its granite top end south of it. Its fire burns behind the glass (FIRES)."""
    herd = list(part_list(("EG", "EG_Herd")))
    body = _herd_body()
    lo = [min(p[1][k] for p in body) for k in range(3)]; hi = [max(p[2][k] for p in body) for k in range(3)]
    assert 0.75 <= hi[1] - lo[1] <= 0.85 and 0.55 <= hi[0] - lo[0] <= 0.62 and 0.80 <= hi[2] <= 0.92
    assert KUECHE_EAST - 0.01 < hi[0] < KUECHE_EAST and hi[1] < 5.2 and lo[1] > 4.25    # north end of the run (v6)
    assert {"Stahl", "Eisen", "Ofenglas"} <= {p[0] for p in herd}
    front = min(p[1][0] for p in herd if p[2][2] < 0.9)                       # doors, handles
    assert 7.90 < front < 7.96
    kueche = list(part_list(("EG", "EG_Kueche")))
    run = [p for p in kueche if p[2][2] <= 0.901 and p[2][0] > 7.9 and p[2][1] > 3.7 and p[1][1] < lo[1]]   # not the sink run (v6)
    assert run and max(p[2][1] for p in run) < lo[1]                          # carcass, doors, granite
    fire = [f for f in BP.fires if abs(f["base"][0] - lo[0]) < 0.03 and lo[1] < f["base"][1] < hi[1]]
    assert len(fire) == 1 and fire[0]["base"][1] > (lo[1] + hi[1]) / 2       # fire door: top left, north
    assert "EG_Herd" not in BP.furniture                                      # built in, like the Ofen


def _kochfeld():
    """The Halbinsel's cooktop: the Eisen plate on the worktop (lo, hi)."""
    (_, lo, hi, _), = [p for p in part_list(("EG", "EG_Kueche")) if p[0] == "Eisen" and 0.89 < p[1][2] < 0.901]   # (not the Muldenlüfter's slot on it)
    return lo, hi


def test_kueche_muldenluefter():
    """Issue #61: the hood over the Halbinsel is gone (with its spot strip and light, #22, #26); the cooktop draws the
    air down at its middle: a Muldenlüfter, a slotted vent along y between the left and the right burners, on the
    cooktop, inside its outline and clear of the burner rings; nothing hangs over the Halbinsel any more."""
    assert ("EG", "EG_Haube") not in BP.geo
    clo, chi = _kochfeld()
    vent = [p for p in part_list(("EG", "EG_Kueche")) if p[1][2] >= chi[2] - 1e-6 and p[2][2] <= chi[2] + 0.01
            and clo[0] < p[1][0] and p[2][0] < chi[0] and clo[1] < p[1][1] and p[2][1] < chi[1]
            and p[0] in ("Fuge", "Metall") and p[2][1] - p[1][1] > 0.3]
    assert vent, "no vent along y on the cooktop"
    lo = [min(p[1][k] for p in vent) for k in range(3)]; hi = [max(p[2][k] for p in vent) for k in range(3)]
    assert 0.08 <= hi[0] - lo[0] <= 0.14 and abs((lo[0] + hi[0]) / 2 - (clo[0] + chi[0]) / 2) < 0.03
    rings = [p for p in part_list(("EG", "EG_Kueche")) if p[0] == "Metall" and clo[0] < p[1][0] and p[2][0] < chi[0]
             and clo[1] < p[1][1] and p[2][1] < chi[1] and 0.1 < p[2][1] - p[1][1] < 0.2
             and abs((p[2][0] - p[1][0]) - (p[2][1] - p[1][1])) < 1e-6]                   # round: as wide as deep
    assert len(rings) == 4 and all(p[2][0] < lo[0] or p[1][0] > hi[0] for p in rings)
    above = [(k[1], m) for k in BP.geo if k[0] == "EG" and k[1] not in ("EG_Waende", "EG_Decke")
             for m, plo, phi in _parts(BP, k) if plo[2] > chi[2] + 0.3 and plo[2] < house_core.Z_EG_TOP
             and plo[0] < chi[0] and phi[0] > clo[0] and plo[1] < chi[1] and phi[1] > clo[1]]
    assert above == [], above


def test_nothing_above_the_wamsler_but_its_pipe():
    """Issue #26: the hood is gone from the Wamsler; above its top only its own pipe (riser, start of the leg to
    the Kaminschacht, #26b) - no EG part but walls and ceiling overlaps its footprint higher up."""
    body = _herd_body()
    lo = [min(p[1][k] for p in body) for k in range(3)]; hi = [max(p[2][k] for p in body) for k in range(3)]
    above = [(k[1], m, plo, phi) for k in BP.geo if k[0] == "EG" and not any(w in k[1] for w in ("_Waende", "Decke"))
             for m, plo, phi in _parts(BP, k)
             if plo[2] >= hi[2] + 0.05 and all(plo[j] < hi[j] - 1e-6 and phi[j] > lo[j] + 1e-6 for j in (0, 1))]
    assert len(above) == 2 and {a[0] for a in above} == {"EG_Herd"} and {a[1] for a in above} == {"Eisen"}, above
    pipe, vert, horiz, _ = _wamsler_pipe()
    assert sorted(a[2] for a in above) == sorted(p[1] for p in vert + horiz)


def _herd_body():
    """The Wamsler's body: its one Stahl part taller than 0.5 m."""
    return [p for p in part_list(("EG", "EG_Herd")) if p[0] == "Stahl" and p[2][2] - p[1][2] > 0.5]


def _wamsler_pipe():
    """The Wamsler's pipe parts (Eisen above the top plate): (all, vertical, horizontal along y, rosette)."""
    top = max(p[2][2] for p in _herd_body())
    pipe = [p for p in part_list(("EG", "EG_Herd")) if p[0] == "Eisen" and p[2][2] > top + 0.1]
    size = lambda p: [p[2][k] - p[1][k] for k in range(3)]
    vert = [p for p in pipe if size(p)[2] > 0.5]
    horiz = [p for p in pipe if size(p)[1] > 0.15 and size(p)[2] < 0.15]
    rosette = [p for p in pipe if size(p)[1] < 0.02 and size(p)[0] > 0.17 and size(p)[2] > 0.17]
    return pipe, vert, horiz, rosette


def test_wamsler_pipe_from_its_left_into_the_kaminschacht():
    """Issue #26, follow-up #26b (user 2026-11-16): the Wamsler's black pipe (Ø 12) leaves its top on the LEFT half
    as seen from the front (north, above the firebox), rises to just under 2 m, bends by 90 deg north and runs into
    the Kaminschacht in the upper left corner - the Abzug (kueche.ABZUG, plastered flue box in the NE corner from
    1.80 m) - ending in a rosette (Ø ~20) on its south face, wholly under the box's underside; nothing else in the
    pipe, and it clears the Küche's cabinets, the hood and every wall but the shaft it enters."""
    import kueche
    pipe, vert, horiz, rosette = _wamsler_pipe()
    body = _herd_body()
    blo = [min(p[1][k] for p in body) for k in range(3)]; bhi = [max(p[2][k] for p in body) for k in range(3)]
    assert len(vert) == len(horiz) == len(rosette) == 1 and len(pipe) == 3
    (_, vlo, vhi, _), (_, hlo, hhi, _), (_, rlo, rhi, _) = vert[0], horiz[0], rosette[0]
    assert abs(vhi[0] - vlo[0] - 0.12) < 0.005 and abs(hhi[2] - hlo[2] - 0.12) < 0.005     # Ø 12
    assert vlo[1] > (blo[1] + bhi[1]) / 2 and vhi[1] < bhi[1]                               # left (north) half
    ax0, ay0, az = kueche.ABZUG
    zc = (hlo[2] + hhi[2]) / 2
    assert vlo[2] <= bhi[2] + 0.1 and 1.80 < zc <= 2.00                                    # collar .. bend
    assert hlo[2] < vhi[2] < hhi[2] and hlo[1] <= vlo[1] + 0.001                           # the elbow: riser ends inside
    assert abs((hlo[0] + hhi[0]) / 2 - (vlo[0] + vhi[0]) / 2) < 1e-6
    assert hhi[1] > ay0 + 0.01 and ax0 < hlo[0] and hhi[0] < kueche.XE                    # into the shaft
    assert abs(rhi[1] - ay0) < 1e-6 and rhi[0] - rlo[0] >= 0.18                            # rosette on its face
    assert ax0 < rlo[0] and rhi[0] < kueche.XE and rlo[2] > az                             # .. within it, below 1.80 free
    assert abs((rlo[2] + rhi[2]) / 2 - zc) < 1e-6 and abs((rlo[0] + rhi[0]) / 2 - (hlo[0] + hhi[0]) / 2) < 1e-6
    shaft = [(lo, hi) for m, lo, hi in _parts(BP, ("EG", "EG_Waende"))
             if abs(lo[0] - ax0) < 1e-6 and abs(lo[1] - ay0) < 1e-6 and abs(lo[2] - az) < 1e-6]
    assert len(shaft) == 1
    others = [(lo, hi) for o in ("EG_Kueche", "EG_Waende", "EG_Wandlampen", "EG_Fenster_Tueren")
              for m, lo, hi in _parts(BP, ("EG", o)) if (lo, hi) not in shaft]
    _clear([p[:3] for p in pipe], others, "Ofenrohr")


def test_kueche_hood_sink_tap_and_wamsler_in_steel():
    """Request 2026-11-10: hood, sink, tap and the Wamsler in steel, metal-coloured. Stahl is light
    and less than half metallic, so the viewer (no environment map, where metal=1 renders black)
    shows it as bright steel; the Wamsler keeps its black plinth, flue, firebox and oven window."""
    d = house_core.MAT_DEF["Stahl"]
    assert min(d["rgba"][:3]) >= 0.5 and d["metal"] < 0.5
    assert "Herd" not in house_core.MAT_DEF
    assert {p[0] for p in part_list(("EG", "EG_Herd"))} == {"Stahl", "Eisen", "Ofenglas"}
    assert len(_herd_body()) == 1
    zt = max(p[2][2] for p in part_list(("EG", "EG_Kueche")) if p[0] == "Granit")
    sink = [p for p in part_list(("EG", "EG_Kueche")) if 7.2 < p[1][0] and p[2][0] < 7.7 and 5.29 < p[1][1]
            and p[2][1] < 5.81 and p[1][2] >= zt - 1e-6]                      # basin, rim, tap
    assert len(sink) == 4 and {p[0] for p in sink} == {"Stahl"}


def test_kueche_without_wall_cabinets_and_sealed_against_the_herd():
    """Request 2026-11-10: no wall cabinets; east of the sink, where the Herd stands in front of the
    sink run, a blind cabinet (no drawers, no grips) and the granite top runs right up to the Herd;
    south of the Herd the Ostzeile's top ends at it too (2 mm joint, no overlap with its rim)."""
    k = list(part_list(("EG", "EG_Kueche")))
    assert not [p for p in k if p[1][2] > 1.3 and p[1][0] > 6.01]              # nothing on the walls (Besenschrank aside)
    herd = [p for p in part_list(("EG", "EG_Herd")) if p[1][2] < 0.95]     # not the pipe (to the Abzug, #26b)
    hy0, hy1 = min(p[1][1] for p in herd), max(p[2][1] for p in herd)       # incl. its top's rim
    hx0 = min(p[1][0] for p in _herd_body())
    assert not [p for p in k if p[0] == "Metall" and p[2][0] > 7.85 and p[1][1] > hy1 - 0.01 and p[2][2] < 0.9]
    for y in (hy1 + 0.003, (hy1 + 5.249) / 2):                               # north of the Herd: top + filler
        assert _mat_at(BP, ("EG", "EG_Kueche"), 8.3, y, 0.88) == "Granit", y
        assert _mat_at(BP, ("EG", "EG_Kueche"), 7.967, y, 0.5) == "Front", y
    assert _mat_at(BP, ("EG", "EG_Kueche"), 8.3, hy0 - 0.003, 0.88) == "Granit"
    granit = [p for p in k if p[0] == "Granit"]
    assert all(p[2][1] <= hy0 - 0.001 or p[1][1] >= hy1 + 0.001 for p in granit if p[2][0] > hx0)
    assert any(abs(p[2][1] - (hy0 - 0.002)) < 1e-6 for p in granit) and any(abs(p[1][1] - (hy1 + 0.002)) < 1e-6 for p in granit)


def test_kueche_and_speis_fronts_after_mallnitz():
    """Request 2026-11-10: the kitchen's cabinets and the big cabinet C beside the dining table in
    the style of input/2026-11-10 input/kueche_mallnitz.png, but in the house's RAL 5014: frame
    fronts (a recessed panel in a frame), on every blue front (drawers and doors) a chrome cup pull
    as in Mallnitz (a plate and a hood open at the bottom); carcasses painted alike (FL_Front), no
    spruce left in the kitchen. The cabinet under the cooktop has drawers on both sides: towards
    the kitchen and towards the dining table."""
    assert house_core.PAINT["Front"] == house_core.RAL_5014 and "rgba" in house_core.MAT_DEF["Front"]
    k = list(part_list(("EG", "EG_Kueche")))
    assert {p[0] for p in k} <= {"Front", "Metall", "Granit", "Fuge", "Eisen", "Stahl"}
    hood = lambda p: p[0] == "Metall" and len(set(map(tuple, p[3]))) > 8
    # Ostzeile (front face x 7.957, y 3.66 .. 4.26): three drawers, each a frame round a recessed
    # panel, each with a cup pull
    ost = [p for p in k if p[0] == "Front" and 3.66 - 1e-6 <= p[1][1] and p[2][1] <= 4.26 + 1e-6 and p[1][0] < 7.98]
    frame = [p for p in ost if abs(p[1][0] - 7.957) < 1e-6]
    panel = [p for p in ost if p[1][0] > 7.962]
    assert len(frame) == 3 * 4 and len(panel) == 3
    assert all(abs(p[2][0] - 7.977) < 1e-6 for p in ost)
    grips = [p for p in k if p[0] == "Metall" and 7.9 < p[1][0] and p[2][0] <= 7.957 + 1e-6 and 3.66 < p[1][1] and p[2][1] < 4.26]
    hoods = [p for p in grips if hood(p)]
    assert len(hoods) == 3 and len(grips) == 6
    for _, lo, hi, vs in hoods:                                               # open at the bottom: a shell
        assert 0.015 <= 7.957 - lo[0] <= 0.03 and not any(abs(v[0] - lo[0]) < 1e-6 and v[2] < lo[2] + 0.002 for v in vs)
    # Halbinsel: towards the kitchen (front face y 3.66) a door and three drawers under the
    # cooktop, towards the dining table (y 3.03) three drawers under the cooktop
    north = [p for p in k if hood(p) and p[1][1] >= 3.66 - 1e-6 and p[2][1] < 3.72 and p[2][2] < 0.86]
    assert len([p for p in north if p[2][0] < 7.165]) == 1 and len([p for p in north if p[1][0] > 7.165]) == 3
    south = [p for p in k if hood(p) and p[2][1] <= 3.03 + 1e-6 and p[1][1] > 2.98 and p[2][2] < 0.86]
    assert len(south) == 3 and all(7.165 < p[1][0] and p[2][0] < 7.957 for p in south)
    sfr = [p for p in k if p[0] == "Front" and abs(p[1][1] - 3.03) < 1e-6 and p[2][2] < 0.86]
    assert len(sfr) == 3 * 4 and all(7.165 < p[1][0] and p[2][0] < 7.957 for p in sfr)
    # every door has a cup pull too, no knobs anywhere
    assert not [p for p in k if p[0] == "Metall" and len(set(map(tuple, p[3]))) >= 48]
    sink = [p for p in k if hood(p) and p[1][1] > 5.2 and p[2][2] < 0.86]
    assert len(sink) == 2 and all(p[2][0] < 7.85 for p in sink)               # the blind corner has none
    besen = [p for p in k if p[2][0] < 6.01 and p[1][1] > 5.2 and p[0] == "Metall"]
    assert len(besen) == 2 and len([p for p in besen if hood(p)]) == 1        # its cup pull


def test_chairs_are_board_chairs_after_stuhl_png():
    """The 8 chairs at the dining table after input/2026-11-05 input/stuhl.png (the Bibliothek desk has
    an office chair since #48: test_buerostuhl_after_photo): a thick plank seat on two battens, four splayed tapering stick legs without
    stretchers, one tall backrest board leaning back with a pointed heart cut out near its top, its
    tenon wedged under the seat."""
    parts = list(part_list(("EG", "EG_Stuehle")))
    seats = [p for p in parts if abs(p[2][2] - 0.46) < 0.005 and p[2][2] - p[1][2] >= 0.04]
    assert len(seats) == 8
    centre = lambda p: ((p[1][0] + p[2][0]) / 2, (p[1][1] + p[2][1]) / 2)
    mean = lambda vs, k: sum(v[k] for v in vs) / len(vs)
    legs = [p for p in parts if p[1][2] < 0.01]
    assert len(legs) == 4 * 8
    for _, _, hi, vs in legs:
        foot = [v for v in vs if v[2] < 0.01]; head = [v for v in vs if v[2] > hi[2] - 0.001]
        c = min((centre(s) for s in seats), key=lambda q: math.dist(q, (mean(foot, 0), mean(foot, 1))))
        assert math.dist(c, (mean(foot, 0), mean(foot, 1))) - math.dist(c, (mean(head, 0), mean(head, 1))) > 0.04   # splayed
        assert max(v[0] for v in foot) - min(v[0] for v in foot) < max(v[0] for v in head) - min(v[0] for v in head) + 0.02   # tapering
    assert not [p for p in parts if p[1][2] > 0.02 and p[2][2] < 0.35]                       # no stretchers
    board = [p for p in parts if p[2][2] > 0.85]
    assert len(board) == 4 * 8                                                # two sides, above and below the heart
    assert sum(len(set(p[3])) == 10 for p in board) == 8                      # the piece notched by the heart's point
    for _, _, hi, vs in board:
        c = min((centre(s) for s in seats), key=lambda q: math.dist(q, (vs[0][0], vs[0][1])))
        top = [v for v in vs if v[2] > hi[2] - 0.001]; low = [v for v in vs if v[2] < min(w[2] for w in vs) + 0.001]
        lean = math.dist(c, (mean(top, 0), mean(top, 1))) - math.dist(c, (mean(low, 0), mean(low, 1)))
        assert lean > 0.12 * (top[0][2] - low[0][2])                         # leans back
    assert sum(0.90 <= p[2][2] <= 1.0 for p in board) == 3 * 8                # tall: about 0.95


def test_buerostuhl_after_photo():
    """Issue #48: the chair at the Büro desk is an office chair after input/2026-11-13 input/bürostuhl.png (its own
    furniture object <c>_Buerostuhl, in the house and in the desk sub-model): a black five-star base on ten twin-castor
    wheels, a black gas column, a grey upholstered seat, a light-grey mesh back in a black frame leaning back, a mesh
    headrest above it and two black T-armrests; centred on the desk, facing it, seat front just short of the top's
    front edge; no clash with the desk, its frame, the walls, the bookcase, windows and doors (the Büro door too)."""
    import desk
    x0, y0 = desk.DESK_AT
    assert "EG_Buerostuhl" in house_core.FURNITURE
    parts = list(part_list(("EG", "EG_Buerostuhl")))
    assert {m for m, *_ in parts} == {"Kunststoff", "Polster", "Netz"}
    cx = x0 + desk.DESK_W / 2
    wheels = [p for p in parts if p[2][2] <= 0.06]
    assert len(wheels) == 10 and all(p[1][2] < 1e-9 for p in wheels)                  # on the floor
    forks = [p for p in parts if abs(p[2][2] - 0.077) < 1e-6]
    assert len(forks) == 5 and all(any(f[1][2] < w[2][2] - 0.001 and math.dist(((f[1][0] + f[2][0]) / 2,), ((w[1][0] + w[2][0]) / 2,)) < 0.03
                                       for f in forks) for w in wheels)                 # each wheel reaches into its fork
    for part in parts:                                                                   # one piece: every part overlaps another
        m, a, b, _ = part
        assert any(q is not part and all(a[k] < q[2][k] - 0.001 and b[k] > q[1][k] + 0.001 for k in range(3)) for q in parts), (m, a, b)
    spokes = [p for p in parts if p[0] == "Kunststoff" and 0.05 < p[1][2] and p[2][2] < 0.14
              and max(p[2][0] - p[1][0], p[2][1] - p[1][1]) > 0.15]
    assert len(spokes) == 5                                                            # five-star base
    assert all(math.dist(((p[1][0] + p[2][0]) / 2, (p[1][1] + p[2][1]) / 2), (cx, y0 + desk.CHAIR[1])) < 0.36 for p in wheels)
    seat = [p for p in parts if p[0] == "Polster"]
    assert len(seat) == 1
    _, lo, hi, _ = seat[0]
    assert 0.47 <= hi[2] <= 0.53 and 0.46 <= hi[0] - lo[0] <= 0.54                      # seat height, width
    assert abs((lo[0] + hi[0]) / 2 - cx) < 1e-6                                          # centred on the desk
    assert y0 - 0.15 < hi[1] < y0                                                        # front just short of the top
    mesh = [p for p in parts if p[0] == "Netz"]
    assert len(mesh) == 2                                                                # back, headrest
    back, head = sorted(mesh, key=lambda p: p[1][2])
    assert back[2][1] < lo[1] + 0.05 and back[2][2] > 1.0 and head[2][2] > 1.15          # behind the seat: faces the desk
    top = [v for v in back[3] if v[2] > back[2][2] - 0.001]; low = [v for v in back[3] if v[2] < back[1][2] + 0.001]
    assert max(v[1] for v in top) < max(v[1] for v in low) - 0.05                       # leans back
    pads = [p for p in parts if p[0] == "Kunststoff" and 0.62 < p[1][2] and p[2][2] < 0.70 and p[2][1] - p[1][1] > 0.2]
    assert len(pads) == 2 and sorted(p[1][0] < cx for p in pads) == [False, True]       # armrests both sides
    others = [p for o in ("EG_Waende", "EG_Fenster_Tueren", "EG_Innentueren", "EG_Moebel", "EG_Schreibtisch", "EG_Geraete",
                          "EG_Buerotuer", "EG_Stuehle", "EG_Wandlampen")
              for p in _parts(BP, ("EG", o))]
    near = [(lo, hi) for m, lo, hi in others if lo[0] < cx + 1.0 and hi[0] > cx - 1.0 and lo[1] < y0 + 0.2 and hi[1] > y0 - 1.2]
    assert near
    _clear([(m, lo, hi) for m, lo, hi, _ in parts], near + _leaf_boxes(BP, "EG", 0.0), "Buerostuhl")
    bp = house_core.build_desk()
    assert ("Desk", "Desk_Buerostuhl") in bp.geo and ("Desk", "Desk_Stuehle") not in bp.geo


def test_desk_submodel():
    """code/desk.py: the Büro desk (today's table, 1.948 x 0.991 x 0.75 m) as its own sub-model
    (web/desk.html), at its own origin: two LG 32" monitors showing the screenshots of
    input/2026-11-06 input/ (a12 left, pilcrow right), edge to edge at about 170°, turned towards
    the chair; the MacBook Pro closed, left, partly under the left monitor, a softly lit Apple logo
    on its lid; a white keyboard and a white trackpad in front; all standing on the top; the chair
    at it; dimension lines."""
    import desk
    bp = house_core.build_desk()
    assert {c for c, _ in bp.geo} == {"Desk"} and bp.garden is None
    assert {n for _, n in bp.geo} == {"Desk_Moebel", "Desk_Schreibtisch", "Desk_Handrad", "Desk_Buerostuhl", "Desk_Geraete",
                                      "Desk_Bildschirm_L", "Desk_Bildschirm_R"}
    v = bp.geo[("Desk", "Desk_Schreibtisch")]["v"]
    lo, hi = [min(p[k] for p in v) for k in range(3)], [max(p[k] for p in v) for k in range(3)]
    assert [round(a, 3) for a in lo[:2] + hi] == [0, 0, desk.DESK_W, desk.DESK_D, 0.75]
    W, D, T = desk.DESK_W, desk.DESK_D, 0.75
    g = bp.geo[("Desk", "Desk_Geraete")]
    assert all(-1e-9 <= x <= W and -1e-9 <= y <= D and z >= T - 1e-9 for x, y, z in g["v"])   # on the top
    assert {"Alu", "Tasten", "Apfel", "Eisen"} <= set(g["m"])
    panes = {}
    for side, img in (("L", "screen_a12"), ("R", "screen_pilcrow")):
        name = "Desk_Bildschirm_" + side
        pg = bp.geo[("Desk", name)]
        (m,) = set(pg["m"])
        d = bp.mat_def[m]
        assert d["image"] == f"textures/{img}.jpg" and (CODE.parent / "web" / "public" / d["image"]).exists()
        w, h = d["size"]
        assert abs(w / h - 16 / 9) < 0.01 and 0.69 < w < 0.71                 # 31.5" 16:9 panel
        loc = [house_core.local(p, bp.pivot[name], bp.turn[name]) for p in pg["v"]]   # pivot: lower-left
        assert abs(min(p[0] for p in loc)) < 1e-9 and abs(max(p[0] for p in loc) - w) < 1e-9
        assert abs(min(p[2] for p in loc)) < 1e-9 and abs(max(p[2] for p in loc) - h) < 1e-9
        assert max(abs(p[1]) for p in loc) < 0.003                            # flat in its plane
        panes[side] = pg["v"]
    assert abs(bp.turn["Desk_Bildschirm_L"] - bp.turn["Desk_Bildschirm_R"] - (180 - 170)) < 1e-9   # 170° apart,
    assert bp.turn["Desk_Bildschirm_L"] > 0                                   # front sides towards the chair
    inner = max(panes["L"], key=lambda p: p[0] - p[2]), min(panes["R"], key=lambda p: p[0] + p[2])   # lower inner corners
    assert math.dist(*inner) < 2 * 0.0085 + 0.004                             # only the two bezels between: touching
    lid = [g["v"][i] for f, m in zip(g["f"], g["m"]) if m == "Apfel" for i in f]
    mac = desk.MAC_X, desk.MAC_X + desk.MAC[0]
    assert all(mac[0] < p[0] < mac[1] and abs(p[2] - T - 0.0168) < 0.001 for p in lid)   # logo on the closed lid
    assert bp.mat_def["Apfel"]["emit"] <= 1.0                                 # softly lit
    left = [p[0] for p in panes["L"]]
    assert mac[0] < min(left) < mac[1]                                        # partly under the left monitor
    assert T + desk.MAC[2] < min(p[2] for p in panes["L"]) - 0.05
    keys = [g["v"][i] for f, m in zip(g["f"], g["m"]) if m == "Tasten" for i in f]
    assert max(p[1] for p in keys) < 0.5 and max(p[2] for p in keys) < T + 0.02   # flat, in front
    assert len(bp.dims) >= 5 and any("Tisch 190" in t for _, _, t in bp.dims)


def test_desk_built_into_the_bibliothek():
    """The desk sub-model stands in the Bibliothek (SW corner 10.943 / 11.471: #10 kept the old centre in x and the back edge),
    unrotated; its devices and screens are loose furniture ("Eingerichtet"), the screens keep their
    pivots."""
    import desk
    sub = house_core.build_desk()
    house_core.build()                                                    # restore the registries
    x0, y0 = desk.DESK_AT
    for n in ("Geraete", "Bildschirm_L", "Bildschirm_R", "Schreibtisch", "Handrad"):
        a, b = sub.geo[("Desk", "Desk_" + n)]["v"], BP.geo[("EG", "EG_" + n)]["v"]
        assert len(a) == len(b) and all(math.dist((p[0] + x0, p[1] + y0, p[2]), q) < 1e-9 for p, q in zip(a, b))
        assert "EG_" + n in BP.furniture
    px, py, pz = sub.pivot["Desk_Bildschirm_L"]
    assert math.dist(BP.pivot["EG_Bildschirm_L"], (px + x0, py + y0, pz)) < 1e-9
    assert BP.turn["EG_Bildschirm_L"] == sub.turn["Desk_Bildschirm_L"]
    assert desk.DESK_AT == (10.943, 11.471)


def test_back_door_has_lever_handles_inside_and_outside():
    """Back door (west wall): a black lever handle outside (on the lock plate) and inside (on its
    own backplate), at the lock (south side), levers pointing towards the hinge (north): open, the
    leaf lies along the back hall's north wall (request 2026-11-10)."""
    levers = [(lo, hi) for m, lo, hi, _ in part_list(("EG", "EG_Hintertuer"))
              if m == "Eisen" and 1.0 < lo[2] and hi[2] < 1.15 and hi[1] - lo[1] > 0.12]
    assert any(hi[0] < -0.04 for lo, hi in levers)                           # outside the leaf
    assert any(lo[0] > 0.09 for lo, hi in levers)                            # inside
    assert all(lo[1] < 7.408 + 0.09 + 0.12 for lo, hi in levers)             # at the lock, south side


def _floor_at(coll, x, y):
    """Material of the floor-cover piece under (x, y) (None in a joint)."""
    g = BP.geo[(coll, coll + "_Bodenbelag")]
    for first, n in BP.parts[(coll, coll + "_Bodenbelag")]:
        vs = [g["v"][i] for f in g["f"][first:first + n] for i in f]
        if min(v[0] for v in vs) < x < max(v[0] for v in vs) and min(v[1] for v in vs) < y < max(v[1] for v in vs):
            return g["m"][first]


def test_bathrooms_have_limestone_like_the_eg_corridor():
    """Request 2026-11-08: Bäder get the limestone of the EG Flur; the Bad of the Großeltern a
    limestone strip on its west side (shower, WC; request 2026-11-09), oak elsewhere."""
    pts = lambda c, ps: {_floor_at(c, x, y) for x, y in ps} - {None}
    assert pts("OG", [(0.4, 6.6), (1.2, 7.5), (2.5, 8.5), (2.1, 5.55), (2.1, 6.4)]) == {"Kalkstein"}  # Gästebad + shower
    assert pts("OG", [(1.0, 6.49), (1.62, 6.0), (1.62, 6.49), (0.8, 6.0)]) == {"Kalkstein"}   # Gästebad: where the
                                                                                               # old walls stood
    gb = [(lo, hi) for m, lo, hi in _parts(BP, ("OG", "OG_Bodenbelag")) if lo[0] < 2.57 and 5.46 < hi[1] and lo[1] < 8.57]
    assert not [(a, b) for i, a in enumerate(gb) for b in gb[i + 1:]                       # no stone twice
                if all(a[0][k] < b[1][k] - 1e-6 and b[0][k] < a[1][k] - 1e-6 for k in range(2))]
    assert pts("OG", [(5.65, 0.45), (7.0, 1.5), (8.55, 2.55)]) == {"Kalkstein"}                       # Bad S
    assert pts("OG", [(4.0, 7.5)]) == {"Eiche"} and pts("OG", [(7.0, 4.0)]) == {"Kalkstein"}          # Flur; HWR (#28)
    assert pts("EG", [(0.71, 11.656)]) == {"Kalkstein"} and pts("EG", [(1.81, 10.7)]) == {"Eiche"}   # Bad Großeltern
    assert pts("EG", [(1.6, 9.3)]) == {"Kalkstein"}                                                    # its WC (#61)
    assert pts("EG", [(5.0, 7.5)]) == {"Kalkstein"}                                                    # EG Flur


def _part_at(key, x, y, z):
    """Material of the first part of GEO object `key` whose bounding box holds (x, y, z)."""
    if key not in BP.geo:
        return None
    g = BP.geo[key]
    for first, n in BP.parts[key]:
        vs = [g["v"][i] for f in g["f"][first:first + n] for i in f]
        if all(min(v[k] for v in vs) < p < max(v[k] for v in vs) for k, p in enumerate((x, y, z))):
            return g["m"][first]


# the WCs walled on three sides: (collection, floor z, interior rectangle, door span on the north wall); the
# Gästebad's WC (glass on its west side since #32) is checked in test_gaestebad_clearances
WCS = [("EG", 0.0, (0.31, 1.458, 5.475, 6.774), (0.68, 1.44), "snw"),          # Duschbad by the back hall (#61):
                                                                                 # its WC part, east the shower glass
       ("EG", 0.0, (0.31, 1.458, 8.656, 9.956), (0.31, 1.458), "sw"),            # WC Großeltern: niche, north open,
                                                                                 # east the shower glass (#63)
       ("OG", house_core.Z_OG, (8.72, 9.92, 3.98, 6.06), (8.69, 9.72))]          # WC 2,30


def test_wcs_have_green_tiles_to_hip_height():
    """Request 2026-11-08 after input/2026-11-08 input/bad_mallnitz.jpeg: green subway tiles about
    1.1 m high (with a cap row) on all WC walls, cut at the door; the Bäder have none."""
    for c, z, (x0, x1, y0, y1), (da, db), *sides in WCS:
        key, d = (c, c + "_Fliesen"), 0.008
        na, nb = max(((x0, da), (db, x1)), key=lambda s: s[1] - s[0])            # wider tiled part
        walls = [((x0 + x1) / 2, y0 + d), (x0 + d, (y0 + y1) / 2)] + [(x1 - d, (y0 + y1) / 2)] * ("e" in (sides or ["e"])[0])
        if nb - na > 0.05:                                                       # north wall not all open
            walls.append(((na + nb) / 2 - 0.025, y1 - d))
        for x, y in walls:
            hits = {_part_at(key, x + dx, y, z + h) for h in (0.3, 0.45, 0.6, 0.75) for dx in (0.0, 0.05)}
            assert "Fliese" in hits, (c, x, y)
            assert _part_at(key, x, y, z + 1.4) is None
        for dd in (0.003, 0.008, 0.012):
            assert _part_at(key, (da + db) / 2, y1 - dd, z + 0.6) is None              # door left free
    zo = house_core.Z_OG
    assert ("OG", "OG_Fliesen") in BP.geo
    assert all(_part_at(("OG", "OG_Fliesen"), x, y, zo + 0.6) is None
               for x, y in ((1.0, 8.562), (7.0, 0.408)))                               # Gästebad, Bad S
    assert _part_at(("OG", "OG_Fliesen"), 5.598, 1.5, zo + 0.6) in ("Fuge", "Kalkstein")   # Bad S west wall: showers (#33)


def test_wc_fixtures_after_the_photo():
    """WCs after the same photo: floor-standing toilet with a close-coupled cistern, the hand
    basins on chrome console legs, a black frame round their mirror. The Bäder keep theirs."""
    zo = house_core.Z_OG
    at = lambda wx, wy, fx, fy: lambda u, v: (wx + fx * v - fy * u, wy + fy * v + fx * u)
    for c, z, *w in [("EG", 0.0, 0.31 + 0.482, 8.656, 0, 1), ("EG", 0.0, 0.8145, 5.475, 0, 1),
                     ("OG", zo, 1.9445, 5.46, 0, 1), ("OG", zo, 9.26, 3.98, 0, 1)]:
        M, key = at(*w), (c, c + "_Sanitaer")
        assert _part_at(key, *M(0, 0.10), z + 0.60) == "Keramik", w            # cistern
        assert _part_at(key, *M(0, 0.40), z + 0.03) == "Keramik", w            # pedestal on the floor
    for c, z, *w in [("OG", zo, 9.92, 4.95, -1, 0)]:                        # the Bad Großeltern's WC has none
        M, key = at(*w), (c, c + "_Sanitaer")
        assert {_part_at(key, *M(s * 0.20, 0.36), z + 0.30) for s in (-1, 1)} == {"Metall"}, w   # Ständer legs
        assert {_part_at((c, c + "_Spiegel"), *M(s * 0.27, 0.02), z + 1.60) for s in (-1, 1)} == {"Eisen"}, w    # frame
    assert _part_at(("OG", "OG_Spiegel"), *at(6.11, 0.40, 0, 1)(0.27, 0.02), zo + 1.6) != "Eisen"


def _waschbecken(key, wall, w, d, taps, z, tile=0.0, bp=None):
    """Check one Waschbecken (input/2026-11-12 input/) of object `key`: wall = (wx, wy, fx, fy), the
    basin's centre on the wall face, facing into the room; `tile` = what stands between plaster and
    basin. Rectangular ceramic basin w x d, top z + 0.85, 17 cm high, hollow; `taps` mixers; one
    drain; on the Ständer: two legs to the floor at the front corners with a rail at 0.52 between
    them, side rails back to the wall, a trap under the drain. Returns the basin's and Ständer's parts (material, lo, hi) in world coordinates."""
    bp = bp or BP
    wx, wy, fx, fy = wall
    ox, oy = wx + fx * tile, wy + fy * tile
    uv = lambda x, y: (-(x - ox) * fy + (y - oy) * fx, (x - ox) * fx + (y - oy) * fy)

    def span(lo, hi):                                                      # (u0, u1, v0, v1) of a box
        us, vs = zip(*(uv(x, y) for x in (lo[0], hi[0]) for y in (lo[1], hi[1])))
        return min(us), max(us), min(vs), max(vs)

    top, zb = z + 0.85, z + 0.68
    parts = [(m, lo, hi) for m, lo, hi in _parts(bp, key) if m in ("Keramik", "Metall") and z - 1e-6 <= lo[2]
             and hi[2] <= top + 0.25 and (s := span(lo, hi)) and -w / 2 - 0.03 <= s[0] and s[1] <= w / 2 + 0.03
             and -0.002 <= s[2] and s[3] <= d + 0.03]
    ker = [(lo, hi) for m, lo, hi in parts if m == "Keramik"]
    met = [(lo, hi) for m, lo, hi in parts if m == "Metall"]
    assert len(ker) >= 5, key                                              # hollow, not a block
    sp = [span(lo, hi) for lo, hi in ker]
    assert abs(min(s[0] for s in sp) + w / 2) < 1e-6 and abs(max(s[1] for s in sp) - w / 2) < 1e-6, key
    assert abs(min(s[2] for s in sp)) < 1e-6 and abs(max(s[3] for s in sp) - d) < 1e-6, key
    assert abs(max(hi[2] for lo, hi in ker) - top) < 1e-6 and abs(min(lo[2] for lo, hi in ker) - zb) < 1e-6, key
    mid = lambda lo, hi: ((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2)
    bowl = (lambda u, v: (ox + fx * v - fy * u, oy + fy * v + fx * u))(0.0, d * 0.6)
    assert not any(all(lo[k] < p < hi[k] for k, p in enumerate((*bowl, top - 0.05))) for lo, hi in ker), key
    assert len([1 for lo, hi in met if abs(lo[2] - top) < 1e-6]) == taps, key           # mixer bodies on the deck
    drains = [(lo, hi) for lo, hi in met if abs(lo[2] - (zb + 0.03)) < 1e-6 and hi[2] - lo[2] < 0.01]
    assert len(drains) == 1, key
    du, dv = uv(*mid(*drains[0]))
    assert abs(du) < 1e-6, key                                                           # one drain, centred
    legs = [uv(*mid(lo, hi)) for lo, hi in met if lo[2] <= z + 0.02 and hi[2] >= zb - 0.03]
    assert sorted(round(u, 3) for u, v in legs) == [round(-w / 2 + 0.05, 3), round(w / 2 - 0.05, 3)], key
    assert all(abs(v - (d - 0.05)) < 1e-6 for u, v in legs), key
    rail = [span(lo, hi) for lo, hi in met if abs((lo[2] + hi[2]) / 2 - (z + 0.52)) < 1e-3]
    assert any(s[1] - s[0] >= w - 0.12 for s in rail), key                                # front rail
    assert len([s for s in rail if s[2] <= 0.002 and s[3] - s[2] >= d - 0.12]) >= 2, key  # side rails to the wall
    assert any(abs(uv(*mid(lo, hi))[0]) < 1e-6 and lo[2] < z + 0.40 and hi[2] <= zb for lo, hi in met), key   # trap
    return parts


def _clear(parts, boxes, what):
    """No part's box intersects any of the boxes ((x0, y0, z0), (x1, y1, z1))."""
    for m, lo, hi in parts:
        for a, b in boxes:
            assert not all(lo[k] < b[k] - 1e-6 and hi[k] > a[k] + 1e-6 for k in range(3)), (what, m, lo, hi, a, b)


def _leaf_boxes(bp, c, z, h=2.0):
    """The door leaves of storey c as built (Blueprint.doors), as boxes."""
    return [((min(a[0], b[0]), min(a[1], b[1]), z), (max(a[0], b[0]), max(a[1], b[1]), z + h))
            for d in bp.doors if d["c"] == c for a, b in [d["leaf"]]]


def test_waschbecken_og_wc():
    """OG WC next to the Hauswirtschaftsraum (request 2026-11-12): a Waschbecken einzeln 50 x 40 on
    its Ständer on the east wall, in front of the tiles, between the toilet and the door leaf (open
    90 deg into the WC); its black-framed mirror moves with it."""
    zo = house_core.Z_OG
    parts = _waschbecken(("OG", "OG_Sanitaer"), (9.92, 4.95, -1, 0), 0.50, 0.40, 1, zo, house_core.WC_TILE_T)
    _clear(parts, _leaf_boxes(BP, "OG", zo), "door leaf")
    toilet = [(lo, hi) for m, lo, hi in _parts(BP, ("OG", "OG_Sanitaer")) if m == "Keramik"
              and 8.9 < lo[0] and hi[0] < 9.6 and 3.98 <= lo[1] and hi[1] < 4.75]
    assert toilet
    _clear(parts, toilet, "toilet")


def test_keramik_bright_white():
    """Request 2026-11-12: the Waschbecken are bright white, not beige: Keramik is a neutral white."""
    r, g, b, _ = house_core.MAT_DEF["Keramik"]["rgba"]
    assert r == g == b >= 0.95


def test_waschbecken_og_baeder():
    """OG Bäder (request 2026-11-12): a Waschbecken on its Ständer on the north wall of the Gästebad at the
    end of the Flur (NW, #18); #32: einzeln 60 between the tub and the door, above it a mirror 80 x 85
    in a 10 cm wooden frame (like the OG Flur's); clear of the door leaves, the shower and the tub. Nadine & Till's
    Bad (S) has a single one since #33 (test_elternbad_layout); nothing there reaches into the window reveal."""
    zo, key = house_core.Z_OG, ("OG", "OG_Sanitaer")
    showers = [((0.31, 5.46, zo), (1.319, 6.855, zo + 2.05)), ((0.31, 6.856, zo), (1.074, 8.57, zo + 0.58))]   # + tub
    for wall, w in (((1.46, 8.57, 0, -1), 0.60),):                                # NW: Gästebad (#18, #32)
        parts = _waschbecken(key, wall, w, 0.47, 1, zo)
        _clear(parts, _leaf_boxes(BP, "OG", zo) + showers, wall)
        cx, cy = wall[:2]
        mixers = sorted(round((lo[0] + hi[0]) / 2 - cx, 3) for m, lo, hi in parts
                        if m == "Metall" and abs(lo[2] - zo - 0.85) < 1e-6)
        assert mixers == [0.0], wall
        mir = [(lo, hi) for m, lo, hi in _parts(BP, ("OG", "OG_Spiegel")) if m == "Spiegel" and abs(lo[1] - cy) < 0.02
               and lo[0] < cx < hi[0]]
        assert len(mir) == 1 and abs((mir[0][0][0] + mir[0][1][0]) / 2 - cx) < 1e-6, wall
        mw = 1.10 if cy < 1 else 0.80                 # Bad S: 110, Gästebad: 80 (#32), x 85 in a 10 cm wooden frame (like the Flur's)
        frame = [(lo, hi) for m, lo, hi in _parts(BP, ("OG", "OG_Spiegel")) if m == "Kiefer" and abs(lo[1] - cy) < 0.05
                 and lo[0] < cx + 1 and hi[0] > cx - 1]
        assert len(frame) == 4
        assert abs(min(lo[0] for lo, hi in frame) - (cx - mw / 2)) < 1e-6 and abs(max(hi[0] for lo, hi in frame) - (cx + mw / 2)) < 1e-6
        assert abs(min(lo[2] for lo, hi in frame) - (zo + 1.17)) < 1e-6 and abs(max(hi[2] for lo, hi in frame) - (zo + 2.02)) < 1e-6
        assert abs(mir[0][1][0] - mir[0][0][0] - (mw - 0.20)) < 1e-6
    assert max(hi[0] for m, lo, hi in _parts(BP, key) if lo[1] < 0.9 and 5.5 < lo[0] < 6.9 and hi[2] > zo + 0.5) \
        <= 6.84 - 0.15 + 1e-6                                                # clear of the window reveal
    assert not hasattr(house_core, "basin")


def _parts(bp, key):
    """(material, lo, hi) per Part of object key of Blueprint bp."""
    g = bp.geo.get(key, {"v": [], "f": [], "m": []})
    for first, n in bp.parts.get(key, []):
        vs = [g["v"][i] for f in g["f"][first:first + n] for i in f]
        yield g["m"][first], [min(p[k] for p in vs) for k in range(3)], [max(p[k] for p in vs) for k in range(3)]


def _rosettes(bp, key):
    """(wall point (x, y), rosette centre height z, facing (fx, fy)) of every Wandlampe in object key: its
    rosette is the Messing disc 8.4 across and about 2 deep (0.5 mm off the wall), facing the side its shade hangs on."""
    parts = list(_parts(bp, key))
    shades = [((lo[0] + hi[0]) / 2, (lo[1] + hi[1]) / 2) for m, lo, hi in parts if m == "Opalglas"]
    out = []
    for m, lo, hi in parts:
        d = [hi[k] - lo[k] for k in range(3)]
        thin = 0 if d[0] < d[1] else 1                                   # the axis across the wall
        if m != "Messing" or abs(d[2] - 0.084) > 0.002 or abs(d[1 - thin] - 0.084) > 0.002 or d[thin] > 0.025:
            continue
        c = [(lo[k] + hi[k]) / 2 for k in range(3)]
        s = min(shades, key=lambda p: math.dist(p, c[:2]))
        f = [0, 0]
        f[thin] = 1 if s[thin] > c[thin] else -1
        w = list(c[:2])
        w[thin] = lo[thin] - 0.0005 if f[thin] > 0 else hi[thin] + 0.0005  # it stands 0.5 mm off the wall
        out.append(((round(w[0], 3), round(w[1], 3)), round(c[2], 3), tuple(f)))
    return out


def test_wandlampen_over_the_og_mirrors():
    """Issue #19: the Gästebad's mirror becomes 140 x 85, the Flur's 110 x 85 (bottoms stay at 1.17); over
    them 4 and 2 Wandlampen, each centred on its equal share of the mirror's width, rosette centre at
    WANDLAMPE_SPIEGEL_H and clear above the frame. #32: the Gästebad's mirror is 80 x 85 with 2 lamps;
    the west-wall lamp between the windows (now in the shower) went to the north wall over the tub's
    head end, at the same height."""
    zo, H = house_core.Z_OG, house_core.WANDLAMPE_SPIEGEL_H
    assert H == 2.10
    got = _rosettes(BP, ("OG", "OG_Wandlampen"))
    want = [((round(1.46 + d, 3), 8.57), (0, -1)) for d in (-0.2, 0.2)]                     # Gästebad mirror
    want += [((0.703, 8.57), (0, -1))]                                                   # Gästebad tub (0.31 .. 1.095)
    for w, f in want:
        assert (w, round(zo + H, 3), f) in got, (w, f, got)
    for x, y in ((1.46, 8.57),):                                         # the frames end 3+ cm under the rosettes
        top = max(hi[2] for m, lo, hi in _parts(BP, ("OG", "OG_Spiegel")) if m == "Kiefer" and abs(lo[1] - y) < 0.05
                  and lo[0] < x < hi[0])
        assert abs(top - (zo + 2.02)) < 1e-6 and zo + H - 0.042 - top > 0.03


def test_wandlampen_og_placements():
    """Issue #19: 29 Wandlampen in the OG, each centred in the free wall span the request names (two in
    one span at its thirds); at WANDLAMPE_H (1.70, rosette centre above the floor) unless over a mirror
    (WANDLAMPE_SPIEGEL_H). Readings (proposal): "vorne" = east; Jugend's "vorderes Bett" = the east bunk."""
    zo, L, S = house_core.Z_OG, house_core.WANDLAMPE_H, house_core.WANDLAMPE_SPIEGEL_H
    assert L == 1.70
    m = lambda a, b: round((a + b) / 2, 3)
    want = {
        "Gästebad": [((round(1.46 + d, 3), 8.57), S, (0, -1)) for d in (-0.2, 0.2)]           # #32: mirror,
                    + [((m(0.31, 1.095), 8.57), S, (0, -1)), ((2.57, m(5.46, 6.34)), L, (-1, 0))],   # tub, toilet
        "Flur": [((m(4.15, 6.31), 8.57), L, (0, -1)),                                  # Yoga .. Jugend door
                   ((round(7.20 + 4.20 / 3, 3), 8.57), L, (0, -1)), ((round(7.20 + 2 * 4.20 / 3, 3), 8.57), L, (0, -1)),   # .. Bichlach door (11.40)
                   ((m(11.51, 14.35), 6.35), L, (0, 1))],                                # Schlafzimmer door .. east end
        "Yoga": [((6.05, m(8.86, 12.485)), L, (-1, 0)),                                  # middle of the Jugend wall
                 ((m(0.31, 3.88), 12.485), L, (0, -1)),                                  # NW corner .. balcony door
                 ((m(5.074, 6.05), 8.86), L, (0, 1))],                                   # open leaf's end .. SE corner
        "Jugend": [((m(7.20, 8.13), 8.86), L, (0, 1)),                                   # door .. east bunk
                   ((9.08, m(10.96, 12.485)), L, (-1, 0))],                              # east bunk .. north wall
        "Bichlach": [((m(12.28, 14.575), 8.86), L, (0, 1)),                              # door (2026-11-25) .. east wall
                     ((m(10.95, 12.91), 12.485), L, (0, -1))],                           # the two north balcony doors
        "Schlafzimmer": [((m(10.70, 12.84), 0.40), L, (0, 1)),                           # balcony door .. window
                         ((14.35, m(2.67, 4.15)), L, (-1, 0)),                           # the two east balcony doors
                         ((10.07, m(3.84, 5.266)), L, (1, 0))],                          # WC corner .. open leaf's end
        "WC": [((9.26, 3.98), L, (0, 1)), ((9.92, 4.95), S, (-1, 0))],                   # cistern, mirror
        "Waschküche": [((round(5.59 + 0.375 + 0.75 * k, 3), 2.79), waschkueche.LAMPE_H, (0, 1)) for k in range(4)]   # over the table,
                                                                                         # #30: under the glazing
                      + [((8.59, 4.70), S, (-1, 0))],                                    # #29: over the basin's mirror
        "Saschi": [((5.44, m(3.37, 6.06)), L, (-1, 0))],                                 # nightstand .. Flur wall
        "Bad Nadine & Till": [((8.59, round(2.14 + d, 3)), S, (-1, 0)) for d in (-0.20, 0.20)]
                             + [((m(7.72, 8.59), 0.40), L, (0, 1))],                # #33: mirror (east wall), window
    }
    got = sorted(_rosettes(BP, ("OG", "OG_Wandlampen")))
    flat = sorted((w, round(zo + h, 3), f) for room in want.values() for w, h, f in room)
    same = lambda a, b: math.dist(a[0], b[0]) < 0.0015 and a[1:] == b[1:]     # 1.5 mm: positions at half mm round either way
    miss = ([g for g in got if not any(same(g, w) for w in flat)], [w for w in flat if not any(same(g, w) for g in got)])
    assert len(flat) == 29 and len(got) == len(flat) and miss == ([], []), miss        # 2026-11-25: the Flur
    assert len([p for p in BP.wall_lights if p[2] > house_core.Z_OG]) == 29             # mirror's two are gone


def test_wandlampen_eg_placements():
    """Issue #22: the Wandlampen of the EG at the places agreed on the drawing (input/2026-11-14 input/
    lampen_eg_v1.svg; numbers as there), at WANDLAMPE_H, over the back hall's mirror at WANDLAMPE_SPIEGEL_H.
    Lamp 1 sits between the open Windfang leaf (13.324) and the front door's leaf opened by the film (13.825).
    11, 12 (the Essen's west wall) went with the default layout (#34); 13, 14 hang on the drywall behind B (#61).
    Off the plan sheets (PLAN skip_words)."""
    L, S = house_core.WANDLAMPE_H, house_core.WANDLAMPE_SPIEGEL_H
    n, s, e, w = (0, 1), (0, -1), (1, 0), (-1, 0)                         # facing: into the room
    both = [((13.5745, 6.349), L, n),                                     # 1 Windfang: south wall
            ((14.36, 8.576), L, s),                                       # 2 Windfang: Bürotür .. NE corner
            ((13.4485, 5.849), L, s),                                     # 3 Stube: door leaf .. east wall
            ((14.351, 0.8345), L, w),                                     # 4 Stube: SE corner, east pier
            ((9.056, 4.0727), L, e),                                      # 5 Stube: over the bench
            ((7.46, 5.849), L, s), ((8.557, 3.96), L, w),                 # 7, 8 Küche: sink; right of the Wamsler
            ((5.674, 0.415), L, n),                                       # 10 Essen: terrace door .. window
            ((11.72, 8.576), L, s), ((6.334, 8.576), L, s), ((3.4965, 8.576), L, s),   # 15-17 Flur, north
            ((3.7813, 6.349), 2.2, n), ((4.9057, 6.349), 2.2, n),         # 18, 19 Flur, south: over the Garderobe (#61)
            ((8.285, 6.349), L, n),                                       # 20
            ((10.5497, 8.876), L, n), ((11.7483, 8.876), L, n), ((8.7015, 8.876), L, n),   # 21-23 Bibliothek
            ((6.174, 9.89), L, e), ((6.174, 10.904), L, e), ((8.4515, 12.473), L, s),       # 24-26
            ((2.657, 9.366), L, e), ((3.2615, 12.473), L, s),             # 27, 28 Oma & Opa
            ((0.71, 12.473), S, s), ((0.792, 8.656), L, n),               # 29 Bad: over the mirror (#63), 30 WC (31: gone, #61)
            ((0.31, 6.55), S, e),                                         # 32 Duschbad: over the mirror (#61; 33, 34 gone)
            ((0.85, 5.475), L, n), ((0.31, 7.1655), L, e),                # 35, 36 Duschbad; back hall
            ((3.9035, 3.64), L, s), ((4.7245, 3.64), L, s)]               # 13, 14 Essen: on the drywall behind B (#61)
    same = lambda a, b: math.dist(a[0], b[0]) < 0.0015 and abs(a[1] - b[1]) < 0.0015 and a[2] == b[2]
    got = [((x, y), z, f) for (x, y), z, f in _rosettes(BP, ("EG", "EG_Wandlampen"))]
    miss = ([g for g in got if not any(same(g, x) for x in both)], [x for x in both if not any(same(g, x) for g in got)])
    assert len(got) == len(both) == 29 and miss == ([], []), miss
    near = lambda pts, xs: all(any(math.dist(p[:2], (x + 0.5 * f[0], y + 0.5 * f[1])) < 0.002 for p in pts) for (x, y), _, f in xs)
    assert near(BP.wall_lights, both)
    assert "Wandlampen" in house_core.PLAN["skip_words"]


def test_eg_lamps_clear():
    """Issue #22: every EG lamp (the Ofen bed's too, the hood's strip excluded) hangs on solid wall (B's
    wooden back for 13, 14), clear of every EG object but walls, floors and ceilings, of the door leaves as
    built and of the front door as the film opens it (90 deg about its hinge)."""
    keys = [k for k in BP.geo if k[0] == "EG" and "Wandlampen" in k[1]]
    assert sorted(k[1] for k in keys) == ["EG_Ofen_Wandlampen", "EG_Wandlampen"]
    skip = ("_Waende", "Boden", "Decke", "Wandlampen")
    leaves = _leaf_boxes(BP, "EG", 0.0)
    px, py = 14.73, 6.528                                                  # the front door, opened by film.py
    leaves.append(((px - (7.433 - py), py + (14.65 - px), 0.0), (px - (6.532 - py), py + (14.81 - px), 2.125)))
    others = [(lo, hi) for k in BP.geo if k[0] == "EG" and not any(w in k[1] for w in skip) for m, lo, hi in _parts(BP, k)]
    for key in keys:
        _clear(list(_parts(BP, key)), others + leaves, key[1])
        for (x, y), z, (fx, fy) in _rosettes(BP, key):
            backing = ("EG", "EG_Speis_Rueckwand") if abs(y - 3.715) < 1e-3 else ("EG", "EG_Waende")   # 13, 14: B's back
            for s, h in ((0, 0), (0.042, 0), (-0.042, 0), (0, 0.042), (0, -0.042)):
                p = (x - fx * 0.006 - fy * s, y - fy * 0.006 + fx * s, z + h)   # just behind the rosette
                assert _part_at(backing, *p) is not None, (key[1], (x, y, z), p)


def test_room_lights_only_the_speis():
    """Issue #22: the Wandlampen light the rooms at dusk; only the Speis (no lamp) keeps a fill light. The
    OG Bad Nadine & Till's fill light goes too (it has six lamps since #3)."""
    assert house_core.ROOM_LIGHTS == [(4.0, 4.79, 0)]


def test_wandlampen_clear():
    """Issue #19: every Wandlampe hangs on solid wall (its rosette backed by a wall part all round, so
    not over an opening), clear of every door leaf as built, the OG furniture and fixtures, and at
    least 1 cm under the ceiling."""
    zo, key = house_core.Z_OG, ("OG", "OG_Wandlampen")
    lamps = list(_parts(BP, key))
    assert max(hi[2] for m, lo, hi in lamps) <= house_core.Z_OG_TOP - 0.01
    others = [(lo, hi) for k in (("OG", "OG_Moebel"), ("OG", "OG_Klappbett"), ("OG", "OG_Sanitaer"), ("OG", "OG_Fliesen"))
              for m, lo, hi in _parts(BP, k)] + _leaf_boxes(BP, "OG", zo)
    _clear(lamps, others, "Wandlampe")
    for (x, y), z, (fx, fy) in _rosettes(BP, key):
        for s, h in ((0, 0), (0.042, 0), (-0.042, 0), (0, 0.042), (0, -0.042)):
            p = (x - fx * 0.01 - fy * s, y - fy * 0.01 + fx * s, z + h)       # 1 cm into the wall
            assert _part_at(("OG", "OG_Waende"), *p) == "Putz", ((x, y, z), p)


def _mat_at(bp, key, x, y, z):
    return next((m for m, lo, hi in _parts(bp, key) if all(lo[k] < p < hi[k] for k, p in enumerate((x, y, z)))), None)


def test_bad_submodel():
    """code/bad.py: the Großeltern's bathroom at its own origin (the room's inner SW corner, 2.048 x 3.817 m). Issue #63
    (variant B of input/2026-11-28 input/bad_grosseltern_optionen.svg): the niche in the south 1.30 clear (its 12 cm front
    wall moved 22 cm north), WC and shower in one room as in the Duschbad: the toilet in the west behind an opening of
    102.4 under a lintel, a walk-in shower 90 x 130 east of it (glass 75 from the south wall on its west side, entry 55,
    limestone on its walls to 2.0, head on the east wall); the Einbauschrank, the old shower, the low wall and its glass
    are gone; one sliding leaf, built open in front of the front wall, rolls over the opening; the Waschbecken einzeln
    60 on the north wall in the NW corner under a mirror 60 x 85 in a wooden frame."""
    import bad
    bp = house_core.build_bad()
    leaves = [pts for c, pts in house_core.LEAVES if c == "Bad"]
    house_core.build()                                                    # restore the registries
    assert {c for c, _ in bp.geo} == {"Bad"} and bp.garden is None
    assert {n for _, n in bp.geo} == {"Bad_Waende", "Bad_Innentueren", "Bad_Sanitaer", "Bad_Fliesen", "Bad_Spiegel",
                                      "Bad_Bodenbelag", "Bad_Boden", "Bad_Schiebetuer"}
    W, D, H = 2.048, 3.817, 2.40
    assert all(-1e-9 <= x <= W + 1e-9 and -1e-9 <= y <= D + 1e-9 and -1e-9 <= z <= H + 1e-9
               for g in bp.geo.values() for x, y, z in g["v"])                # no part outside the room
    box = lambda m, lo, hi: [m, [round(a, 3) for a in lo], [round(a, 3) for a in hi]]
    walls = [box(*p) for p in _parts(bp, ("Bad", "Bad_Waende"))]
    assert ["Putz", [1.024, 1.3, 0], [W, 1.42, 2.4]] in walls                  # front wall, 22 cm north (#63)
    assert all(w[1][1] >= 1.3 - 1e-6 and w[2][1] <= 1.42 + 1e-6 for w in walls)   # no low wall, no middle wall
    for u in (0.5, 1.5):                                                       # lintel over the opening
        assert _mat_at(bp, ("Bad", "Bad_Waende"), u, 1.36, 2.2) == "Putz"
    assert _mat_at(bp, ("Bad", "Bad_Waende"), 0.5, 1.36, 2.0) is None and _mat_at(bp, ("Bad", "Bad_Waende"), 1.5, 1.36, 1.0)
    san, til = ("Bad", "Bad_Sanitaer"), ("Bad", "Bad_Fliesen")
    # the shower: one pane on its west side (x 1.148) from the south wall, 75 long, to 2.0; the entry 55 north of it
    glass = [(lo, hi) for m, lo, hi in _parts(bp, san) if m == "Glas"]
    assert len(glass) == 1
    (glo, ghi), = glass
    assert abs((glo[0] + ghi[0]) / 2 - 1.148) < 1e-6 and 0.0 <= glo[1] <= 0.012 and abs(ghi[1] - 0.754) < 1e-6 and ghi[2] == 2.0
    assert round(1.30 - 0.75, 3) == 0.55
    for x, y, z in ((W - 0.009, 0.6, 1.9), (1.6, 0.009, 1.9), (1.6, 1.291, 1.9)):   # east, south, front wall
        assert _mat_at(bp, til, x, y, z) == "Kalkstein", (x, y, z)
    assert _mat_at(bp, til, W - 0.009, 0.6, 2.1) is None
    assert not [1 for m, lo, hi in _parts(bp, til) if m == "Kalkstein" and (lo[0] < 1.148 or hi[1] > 1.30)]   # old shower gone
    drain = [(lo, hi) for m, lo, hi in _parts(bp, san) if m == "Metall" and hi[2] < 0.03]
    assert len(drain) == 1 and 1.148 < drain[0][0][0] and drain[0][1][0] < W and drain[0][1][1] < 1.30
    head = [(lo, hi) for m, lo, hi in _parts(bp, san) if m == "Metall" and lo[2] >= 1.0 - 1e-6 and lo[0] > 1.5]
    assert head and min(lo[1] for lo, hi in head) > 0.2 and max(hi[1] for lo, hi in head) < 1.0   # on the east wall
    assert not any(m == "Keramik" and lo[0] > 1.148 for m, lo, hi in _parts(bp, san))       # no tray: flush
    # one sliding leaf, built open in front of the front wall, 4 cm over the opening
    assert len(leaves) == 1
    lb = [([min(p[k] for p in l) for k in range(3)], [max(p[k] for p in l) for k in range(3)]) for l in leaves]
    (llo, lhi), = lb
    assert abs(llo[0] - 0.979) < 0.005 and abs(lhi[0] - (W - 0.005)) < 0.005 and lhi[2] >= 1.98 and llo[1] > 1.42
    inn, leaf = ("Bad", "Bad_Innentueren"), ("Bad", "Bad_Schiebetuer")
    assert {_mat_at(bp, leaf, 0.48, 1.45, z) for z in (0.5, 1.0, 1.5)} == {None}           # the opening free
    assert _mat_at(bp, leaf, 1.5, 1.45, 1.0)                                                # the leaf over the wall
    assert not [1 for m, lo, hi in _parts(bp, inn) if m != "Metall"]          # Innentueren: only the rail
    assert bp.slide == {"Bad_Schiebetuer": (-0.979, 0.0, 0.0)}
    assert any(m == "Metall" and lo[0] <= 0.01 and hi[0] >= W - 0.01 and 1.999 <= lo[2] for m, lo, hi in _parts(bp, inn))  # rail
    for lo, hi in lb:                                                          # no leaf in a wall
        assert not any(all(a[k] < hi[k] - 1e-6 and lo[k] + 1e-6 < b[k] for k in range(3)) for _, a, b in _parts(bp, ("Bad", "Bad_Waende")))
    # WC: toilet on the south wall, Taubenblau tiles on the south wall up to the glass and on the west wall
    assert _mat_at(bp, san, 0.482, 0.10, 0.60) == "Keramik" and _mat_at(bp, san, 0.482, 0.40, 0.03) == "Keramik"
    for x, y in ((0.482, 0.008), (0.008, 0.6), (1.0, 0.008)):
        assert "Fliese" in {_mat_at(bp, til, x + dx, y, h) for h in (0.3, 0.45, 0.6) for dx in (0.0, 0.05)}, (x, y)
    assert not any(m == "Fliese" and (hi[0] > 1.148 + 1e-6 or hi[1] > 1.30 + 1e-6) for m, lo, hi in _parts(bp, til))
    # Waschbecken einzeln 60 x 47 on the north wall, axis x 0.40 (west of the north window, house x 1.109), a mirror
    # 60 x 85 in a pine frame above it
    _waschbecken(san, (0.40, D, 0, -1), 0.60, 0.47, 1, 0.0, bp=bp)
    mir = list(_parts(bp, ("Bad", "Bad_Spiegel")))
    assert {m for m, lo, hi in mir} == {"Kiefer", "Spiegel"}
    assert round(min(lo[0] for m, lo, hi in mir), 3) == 0.1 and round(max(hi[0] for m, lo, hi in mir), 3) == 0.7
    assert round(min(lo[2] for m, lo, hi in mir), 3) == 1.17 and round(max(hi[2] for m, lo, hi in mir), 3) == 2.02
    assert max(hi[0] for m, lo, hi in mir) < 1.109 - 0.31                     # clear of the north window
    texts = sorted(t for _, _, t in bp.dims)
    assert texts == sorted(["Dusche 90", "Glas 75", "Einstieg 55", "Öffnung 102.4", "130 tief", "HWB 60",
                            "Spiegel 60 × 85", "Raumbreite 204.8", "Raumtiefe 381.7"])
    # floor: limestone in the niche (WC and shower) and in a strip along the west wall, oak elsewhere, none under
    # the front wall; a dark base under the joints
    fl = list(_parts(bp, ("Bad", "Bad_Bodenbelag")))
    at = lambda x, y: {m for m, lo, hi in fl if lo[0] < x < hi[0] and lo[1] < y < hi[1]}
    for x, y in ((0.3, 0.6), (0.4, 3.0), (0.4, 1.36), (0.05, 3.79), (1.5, 0.3), (1.6, 1.0), (2.0, 0.6)):
        assert at(x, y) <= {"Kalkstein"} and at(x + 0.004, y + 0.004) | at(x, y) == {"Kalkstein"}, (x, y)
    for x, y in ((1.5, 2.0), (1.2, 3.6), (2.03, 3.79)):
        assert at(x, y) <= {"Eiche"} and at(x + 0.004, y + 0.004) | at(x, y) == {"Eiche"}, (x, y)
    assert min(lo[1] for m, lo, hi in fl if m == "Eiche") >= 1.42 - 1e-6
    assert at(1.5, 1.36) == set()                                              # front wall
    assert [m for m, lo, hi in _parts(bp, ("Bad", "Bad_Boden"))] == ["Fuge"]


def test_bad_built_into_the_grosseltern():
    """The Bad sub-model stands in the house at BAD_AT, unrotated, every part the same; the wall
    between the old WC and Bad and its sliding door are gone; the bedroom wall ends at the niche
    front (#63: 22 cm further north), so Bad and bedroom are open to each other; limestone in the niche (WC and
    shower) and in the strip along the west wall, oak elsewhere."""
    import bad
    sub = house_core.build_bad()
    house_core.build()                                                    # restore the registries
    x0, y0 = bad.BAD_AT
    assert bad.BAD_AT == (0.31, 8.656)

    def solids(bp, key, dx=0.0, dy=0.0):
        g = bp.geo[key]
        return {tuple(sorted({(round(g["v"][i][0] + dx, 6), round(g["v"][i][1] + dy, 6), round(g["v"][i][2], 6))
                              for f in g["f"][a:a + n] for i in f})) for a, n in bp.parts[key]}

    for n in ("Waende", "Innentueren", "Sanitaer", "Fliesen", "Spiegel", "Bodenbelag", "Boden", "Schiebetuer"):
        assert solids(sub, ("Bad", "Bad_" + n), x0, y0) <= solids(BP, ("EG", "EG_" + n)), n
    assert BP.slide == {"EG_Schiebetuer": (-0.979, 0.0, 0.0)}
    wl = list(_parts(BP, ("EG", "EG_Waende")))
    assert not any(lo[1] > 10.0 and hi[1] < 10.3 and lo[0] >= 0.3 and hi[0] <= 2.36 for _, lo, hi in wl)   # WC/Bad wall
    assert not any(lo[0] >= 2.35 and hi[0] <= 2.66 and lo[1] < 12.3 and hi[1] > 10.08 and lo[2] < 2.0 for _, lo, hi in wl)
    assert any(lo[0] >= 2.35 and hi[0] <= 2.66 and abs(hi[1] - 10.076) < 1e-6 and lo[2] < 0.1 for _, lo, hi in wl)   # #63
    assert not any(lo[1] > 10.2 and hi[1] < 10.35 and hi[0] < 2.36 for _, lo, hi in _parts(BP, ("EG", "EG_Innentueren")))
    assert len([1 for c, l in house_core.LEAVES if c == "EG" and 0.3 < l[0][0] < 2.4 and 10.0 < l[0][1] < 10.2]) == 1
    assert _floor_at("EG", 0.71, 11.656) == "Kalkstein" and _floor_at("EG", 1.81, 10.7) == "Eiche"   # strip, Bad
    assert _floor_at("EG", 0.8, 9.3) == "Kalkstein" and _floor_at("EG", 1.9, 9.3) == "Kalkstein"   # WC, shower (#63)


def test_gaestebad_og_walls():
    """Gästebad im 1. Stock (#18): the WC 2,26's wall with its door is gone, the niche is open. #32 (the user's
    addition, decision run-2026-11-15-1633-17): the partition between shower and WC is gone too, replaced by a
    glass wall on its west face line (x 1.319) from the south wall, 9 cm further forward than the wall's 6.15,
    then ("das glas der Dusche … bitte noch 10cm länger", run-2026-11-15-1633-18) 10 cm more: to y 6.34; north
    of it the shower's entrance."""
    zo, key, san = house_core.Z_OG, ("OG", "OG_Waende"), ("OG", "OG_Sanitaer")
    assert all(_part_at(key, x, y, zo + 1.0) is None for x in (1.33, 1.369, 1.41) for y in (5.5, 5.8, 6.1))   # no wall
    assert [_part_at(san, 1.319, y, zo + 1.0) for y in (5.5, 6.0, 6.2, 6.3)] == ["Glas"] * 4                # glass
    assert all(_part_at(san, 1.319, y, zo + h) is None for y in (6.4, 6.6, 6.8) for h in (1.0, 1.9))        # entrance
    glass, = [(lo, hi) for m, lo, hi in _parts(BP, san) if m == "Glas" and 1.3 < lo[0] < 1.33 and lo[1] < 7.0]
    assert abs(glass[1][1] - (6.34 + 0.004)) < 1e-6 and glass[1][1] - 6.15 > 0.15 and glass[1][2] >= zo + 2.0 - 1e-6
    assert _part_at(key, 1.62, 6.0, zo + 1.0) is None                                        # old partition
    assert all(_part_at(key, x, 6.49, zo + h) is None for x in (0.4, 1.0, 1.3) for h in (1.0, 2.3))   # old WC wall
    assert not [d for d in BP.doors if d["c"] == "OG" and d["hinge"][0] < 2.5 and 6.3 < d["hinge"][1] < 6.7]
    assert not [l for c, l in house_core.LEAVES if c == "OG" and max(l[0][0], l[1][0]) < 2.5
                and 6.0 < min(l[0][1], l[1][1]) < 6.7]


def _gaestebad_boxes(bp, c="OG", dx=0.0, dy=0.0):
    """The (material, lo, hi) of every Part the Gästebad brings into the room (fixtures, glass, tiles, limestone,
    mirror, lamps), in house coordinates."""
    out = []
    for o in ("Sanitaer", "Fliesen", "Spiegel", "Wandlampen", "Waende"):
        for m, lo, hi in _parts(bp, (c, c + "_" + o)):
            lo, hi = (lo[0] + dx, lo[1] + dy, lo[2]), (hi[0] + dx, hi[1] + dy, hi[2])
            if 0.30 < lo[0] and hi[0] < 2.575 and 5.44 < lo[1] and hi[1] < 8.575 and (o != "Waende" or hi[0] - lo[0] < 0.2):
                out.append((m, lo, hi))
    return out


def test_gaestebad_og_shower_and_tub():
    """Issue #32: coming in through the Flur door one faces the back wall (west): on the left, in the SW corner,
    the walk-in shower (west wall to the glass, south wall to the tub, head on the south wall); to its right the
    tub 170 x 75 built in along the west wall from y 6.87 to the north wall under the big window: white shell,
    rim 58 under the window's 75 sill, the window over most of it (to look out of), a limestone apron (east) and
    end (south), a deck mixer on the south rim. The user's addition (-17): no tray, the limestone floor runs
    through; the back (west) and side (south) wall in limestone to 2.0, the west wall's small window left free."""
    zo, key = house_core.Z_OG, ("OG", "OG_Sanitaer")
    near = lambda a, b: all(abs(p - q) < 1e-6 for p, q in zip(a, b))
    room = [(m, lo, hi) for m, lo, hi in _gaestebad_boxes(BP)]
    assert not [1 for m, lo, hi in room if m == "Keramik" and hi[0] < 1.33 and hi[1] < 6.87]   # no tray
    assert [_floor_at("OG", x, y) for x, y in ((0.8, 6.0), (1.369, 5.8), (1.9, 6.5))] == ["Kalkstein"] * 3
    drain = [(lo, hi) for m, lo, hi in room if m == "Metall" and abs(lo[2] - zo - 0.018) < 1e-6 and hi[1] < 6.87]
    assert len(drain) == 1 and near(((drain[0][0][0] + drain[0][1][0]) / 2,), ((0.31 + 1.319) / 2,))
    stone = [(lo, hi) for m, lo, hi in room if m == "Kalkstein"]
    west = [b for b in stone if b[0][0] > 0.31 and b[1][0] < 0.323 and b[1][1] < 6.87]
    south = [b for b in stone if b[0][1] > 5.46 and b[1][1] < 5.473 and b[1][0] < 1.33]
    for slabs, k in ((west, 1), (south, 0)):
        assert slabs and abs(max(b[1][2] for b in slabs) - zo - 2.0) < 0.003 and min(b[0][2] for b in slabs) < zo + 0.03
        assert sum((b[1][k] - b[0][k]) * (b[1][2] - b[0][2]) for b in slabs) > 0.85 * (1.4 if k else 1.0) * 2.0 - 0.36
    assert not [b for b in west if b[1][1] > 5.72 and b[0][1] < 6.32 and b[1][2] > zo + 1.48 + 0.003]   # window free
    assert max(b[1][0] for b in south) < 1.319 - 0.004                                       # short of the glass
    riser = [(lo, hi) for m, lo, hi in _parts(BP, key) if m == "Metall" and abs(lo[2] - zo - 1.0) < 1e-6
             and lo[0] < 2.6 and 5.4 < lo[1] < 5.6]
    assert len(riser) == 1 and 0.31 < (riser[0][0][0] + riser[0][1][0]) / 2 < 1.319 and riser[0][0][1] >= 5.472 - 1e-6
    # the user's third addition (run-2026-11-15-1633-19): „die Badewanne ersetzen durch eine wie im heutigen input
    # directory. Mit dem Kopfende zur Dusche. Und zwischen der Dusche und der Badewanne auch eine Glasscheibe“
    # (input/2026-11-15 input/badewanne.webp): a freestanding slipper tub 165 x 75 on four claw feet
    tub = [(lo, hi) for m, lo, hi in room if m == "Keramik" and lo[1] > 6.86 and hi[0] < 1.12]
    lo = [min(b[0][k] for b in tub) for k in range(3)]
    hi = [max(b[1][k] for b in tub) for k in range(3)]
    assert 0.33 < lo[0] and hi[0] < 1.11 and 6.87 < lo[1] and hi[1] < 8.555                 # free of the walls
    assert abs(hi[0] - lo[0] - 0.75 - 0.024) < 0.01 and abs(hi[1] - lo[1] - 1.65 - 0.024) < 0.01   # 165 x 75 (+ roll)
    assert abs(lo[2] - zo) < 1e-6 and hi[2] < zo + 0.75                                      # on the floor, under the sill
    assert min(7.76, hi[1]) - max(6.77, lo[1]) > 0.85                                        # the window over the tub
    top = lambda y0, y1: max(h[2] for l, h in tub if y0 < (l[1] + h[1]) / 2 < y1)
    assert top(6.8, 7.15) > top(8.2, 8.6) + 0.10 and top(8.2, 8.6) > zo + 0.55              # head end at the shower
    feet = [(l, h) for l, h in tub if abs(l[2] - zo) < 1e-6]
    assert len(feet) == 4 and all(h[2] < zo + 0.25 for l, h in feet)                         # four claw feet
    assert not [b for b in stone if b[0][1] > 6.86 and b[1][0] < 1.12]                       # no apron
    # the fourth addition (-20): „der Wasserhahn aus der Wand an der anderen Seite … an der Außenwand nicht diese
    # Stange, die mitten im Raum steht“: the tap on the west (outer) wall at the foot end, nothing on the floor
    tap = [(l, h) for m, l, h in room if m == "Metall" and l[0] < 0.315 and l[2] > zo + 0.6 and l[1] > 6.9]
    cy = (lo[1] + hi[1]) / 2
    assert tap and all(l[1] > cy + 0.3 and h[1] < hi[1] for l, h in tap)                    # wall, foot end
    assert [1 for m, l, h in room if m == "Metall" and h[0] > 0.45 and l[1] > cy + 0.3 and l[2] > zo + 0.6]   # spout
    assert not [(m, l, h) for m, l, h in _parts(BP, key) if l[2] < zo + 0.3 and 6.87 < l[1] < 8.05
                and hi[0] < l[0] < 1.6]                                                       # no standpipe
    pane = [(l, h) for m, l, h in room if m == "Glas" and h[1] - l[1] < 0.01 and l[1] > 6.8]
    assert len(pane) == 1 and pane[0][0][0] < 0.33 and pane[0][1][0] > hi[0]                # glass shower | tub
    assert pane[0][1][1] < lo[1] and pane[0][0][1] > 6.84 and pane[0][1][2] >= zo + 2.0 - 1e-6


def test_gaestebad_clearances():
    """Issue #32: the shower opens east north of the glass, ≥ 50 cm clear to the tub (60 before the user made the
    glass 10 cm longer, run-2026-11-15-1633-18), nothing in front of the
    opening; the toilet centred between the glass and the east wall, ≥ 20 free each side, ≥ 60 in front,
    Taubenblau tiles on the south and east wall behind and beside it; the
    basin (single 60) on the north wall between tub and door, ≥ 5 from the tub, 60 free in front; nothing of the
    Gästebad within the Flur door leaf's swing (so the leaf, open flat against the east wall, touches nothing)."""
    zo = house_core.Z_OG
    boxes = _gaestebad_boxes(BP)
    hits = lambda a, b: [(m, lo, hi) for m, lo, hi in boxes
                         if all(lo[k] < b[k] - 1e-6 and hi[k] > a[k] + 1e-6 for k in range(3))]
    part = [(lo, hi) for m, lo, hi in boxes if m in ("Glas", "Metall") and 1.3 < lo[0] and hi[0] < 1.34 and hi[1] < 6.6]
    tub = [(lo, hi) for m, lo, hi in boxes if m == "Keramik" and lo[1] > 6.86 and hi[0] < 1.12]
    pane = [(lo, hi) for m, lo, hi in boxes if m in ("Glas", "Metall") and lo[1] > 6.8 and hi[1] - lo[1] < 0.03
            and hi[0] - lo[0] > 0.5]
    yp, yt = max(hi[1] for lo, hi in part), min(lo[1] for lo, hi in pane)
    assert yt - yp >= 0.50                                                                  # shower entrance
    assert not hits((0.9, yp, zo + 0.1), (1.75, yt, zo + 1.9))
    toilet = [(lo, hi) for m, lo, hi in boxes if m == "Keramik" and lo[0] > 1.33 and hi[1] < 6.3]
    tl, th = [min(b[0][k] for b in toilet) for k in range(3)], [max(b[1][k] for b in toilet) for k in range(3)]
    assert abs((tl[0] + th[0]) / 2 - (1.319 + 2.57) / 2) < 1e-6                              # centred: glass .. wall
    assert tl[0] - 1.319 - 0.004 >= 0.20 and 2.57 - 0.01 - th[0] >= 0.20                     # 20 free each side
    fl = ("OG", "OG_Fliesen")
    assert "Fliese" in {_part_at(fl, x, 5.468, zo + 0.6) for x in (1.9, 1.95)} and "Fliese" in {
        _part_at(fl, 2.562, y, zo + 0.6) for y in (5.8, 5.85)}                               # tiles: south, east
    assert not hits((tl[0], th[1], zo + 0.05), (th[0], th[1] + 0.60, zo + 1.5))              # 60 in front
    basin = [(lo, hi) for m, lo, hi in boxes if m == "Keramik" and abs(hi[2] - zo - 0.85) < 1e-6 and lo[1] > 8.0]
    bl, bh = [min(b[0][k] for b in basin) for k in range(3)], [max(b[1][k] for b in basin) for k in range(3)]
    assert abs(bh[0] - bl[0] - 0.60) < 1e-6 and bl[0] - max(hi[0] for lo, hi in tub) >= 0.05
    assert not hits((bl[0], bl[1] - 0.60, zo + 0.05), (bh[0], bl[1], zo + 1.8))              # 60 in front
    door, = [d for d in BP.doors if d["c"] == "OG" and abs(d["hinge"][0] - 2.57) < 0.01 and 7.6 < d["hinge"][1] < 7.7]
    h = door["hinge"][:2]
    r = max(math.dist(h, p[:2]) for p in door["leaf"])
    corners = lambda lo, hi: [(x, y) for x in (lo[0], hi[0]) for y in (lo[1], hi[1])]
    near = [(m, lo, hi) for m, lo, hi in boxes if any(math.dist(h, p) < r + 0.05 for p in corners(lo, hi))
            or (lo[1] < h[1] < hi[1] and h[0] - hi[0] < r + 0.05)]
    assert near == []


def test_gaestebad_submodel():
    """Issue #18: code/gaestebad.py, the Gästebad at its own origin (the room's inner SW corner; floor
    at z 0) with the pieces of its four walls and its dimension lines (web/gaestebad.html); in the
    house it stands at GAESTEBAD_AT on the OG floor, every fixture, glass and tile the same."""
    import gaestebad as g
    bp = house_core.build_gaestebad()
    house_core.build()                                                    # restore the registries
    assert g.GAESTEBAD_AT == (0.31, 5.46) and bp.garden is None
    assert {c for c, _ in bp.geo} == {"Gaestebad"}
    assert {"Gaestebad_Waende", "Gaestebad_Sanitaer", "Gaestebad_Fliesen", "Gaestebad_Innentueren"} <= {n for _, n in bp.geo}
    x0, y0 = g.GAESTEBAD_AT
    sub = lambda n: {tuple(sorted({(round(v[0] + x0, 5), round(v[1] + y0, 5), round(v[2] + house_core.Z_OG, 5))
                                   for f in g_["f"][a:a + k] for i in f for v in [g_["v"][i]]}))
                     for g_ in [bp.geo[("Gaestebad", "Gaestebad_" + n)]] for a, k in bp.parts[("Gaestebad", "Gaestebad_" + n)]}
    house = lambda n: {tuple(sorted({(round(v[0], 5), round(v[1], 5), round(v[2], 5)) for f in g_["f"][a:a + k] for i in f
                                     for v in [g_["v"][i]]}))
                       for g_ in [BP.geo[("OG", "OG_" + n)]] for a, k in BP.parts[("OG", "OG_" + n)]}
    assert sub("Sanitaer") <= house("Sanitaer") and sub("Fliesen") <= house("Fliesen")
    labels = [d[2] for d in bp.dims]
    assert len(bp.wall_lights) == 4 and len(bp.parts[("Gaestebad", "Gaestebad_Wandlampen")]) == 4 * 8   # #32: its four lamps,
    for x, y, z in bp.wall_lights:                                                           # where the house has them
        assert any(math.dist((x + x0, y + y0, z + house_core.Z_OG), q) < 1e-6 for q in BP.wall_lights), (x, y, z)
    for t in ("WC 125", "Dusche 101 × 141", "Glas 88", "Durchgang 53", "Wanne 165 × 75", "Kopfende 74", "Rand 60", "Waschbecken 60",
              "Spiegel 80 × 85", "Tür 81"):
        assert t in labels, (t, labels)


def test_elternbad_layout():
    """Issue #3, Bad Nadine & Till (OG, x 5.59 .. 8.59, y 0.40 .. 2.62; code/elternbad.py): the door to the
    Schlafzimmer at the south end of the east wall (0.65 .. 1.58, hinged south, open 90 deg into the Bad), the old
    opening is wall. Issue #33: two walk-in showers on one strip 90 deep along the back wall (west, opposite the
    door): heads in the back corners (SW, NW), one pane each from its side wall, 60 clear between them in the
    middle; limestone on the strip's walls, on the north wall (the Waschküche partition, #30 glazes its top, #61
    its top half metre) only to 1.70. The toilet on the north wall between glass and basin (≥ 20 free each side, ≥ 60 in front), the
    basin (single 60) with a wood mirror 80 x 85 and two Wandlampen on the east wall north of the door, a lamp
    left of the window; Taubenblau tiles on the north wall from the glass and on the east wall down to the door.
    Nothing on the north wall above 1.70; the open leaf touches nothing; the passage is free."""
    zo, T = house_core.Z_OG, house_core.WC_TILE_T
    near = lambda a, b: all(abs(p - q) < 1e-6 for p, q in zip(a, b))
    box = lambda lo, hi: (tuple(lo), tuple(hi))
    # door
    wk = ("OG", "OG_Waende")
    assert all(_part_at(wk, 8.65, y, zo + h) == "Putz" for y in (1.7, 2.1, 2.5) for h in (0.5, 1.5))   # old opening
    assert all(_part_at(wk, 8.65, y, zo + 1.0) is None for y in (0.7, 1.0, 1.4))                     # new one
    doors = [d for d in BP.doors if d["c"] == "OG" and abs(d["hinge"][0] - 8.59) < 0.01 and d["hinge"][1] < 2.62]
    assert len(doors) == 1 and near(doors[0]["hinge"], (8.59, 0.675)) and near(doors[0]["open"], (-1, 0))
    leaf = [(lo, hi) for m, lo, hi in _parts(BP, ("OG", "OG_Innentueren")) if 7.6 < lo[0] and hi[0] < 8.6
            and 0.6 < lo[1] and hi[1] < 0.85 and lo[2] > zo]
    assert leaf and min(lo[0] for lo, hi in leaf) < 7.75                              # 90 deg: along x
    san = list(_parts(BP, ("OG", "OG_Sanitaer")))
    room = lambda lo, hi: 5.58 < lo[0] and hi[0] < 8.6 and 0.38 < lo[1] and hi[1] < 2.64 and lo[2] > zo - 1e-6
    # the strip: walk-in (no tray), the room's limestone runs through; one drain per shower
    assert not [1 for m, lo, hi in san if m == "Keramik" and room(lo, hi) and hi[0] < 6.5 and hi[2] < zo + 0.1]
    assert {_floor_at("OG", x, y) for x in (5.8, 6.3) for y in (0.6, 1.5, 2.4)} - {None} == {"Kalkstein"}
    drain = sorted(box(lo, hi) for m, lo, hi in san if m == "Metall" and room(lo, hi) and hi[2] < zo + 0.05)
    assert len(drain) == 2 and all(abs(lo[2] - (zo + 0.018)) < 1e-6 and hi[0] < 6.49 for lo, hi in drain)
    assert drain[0][1][1] < 1.51 < drain[1][0][1]                                     # one each side of the middle
    # glass: one pane per shower at x 6.49 (from the floor, to 2.0), from its side wall; 60 clear between their Parts
    glass = sorted(box(lo, hi) for m, lo, hi in san if m == "Glas" and room(lo, hi))
    assert len(glass) == 2 and all(abs(lo[2] - (zo + 0.018)) < 1e-6 and abs(hi[2] - (zo + 2.0)) < 1e-6 for lo, hi in glass)
    assert all(near((lo[0], hi[0]), (6.49 - 0.004, 6.49 + 0.004)) for lo, hi in glass)
    assert glass[0][0][1] <= 0.40 and glass[1][1][1] >= 2.62                          # side wall to side wall
    pane = [box(lo, hi) for m, lo, hi in san if room(lo, hi) and lo[0] < 6.49 < hi[0] and lo[1] < 2.62 and hi[2] > zo + 1.0]
    a, b = max(hi[1] for lo, hi in pane if hi[1] < 1.51), min(lo[1] for lo, hi in pane if lo[1] > 1.51)
    assert abs(b - a - 0.60) < 1e-6 and abs((a + b) / 2 - 1.51) < 1e-6, (a, b)       # the passage: 60, in the middle
    passage = ((6.49 - 0.60, a, zo + 0.019), (6.49 + 0.60, b, zo + 2.0))              # free 60 deep on both sides
    # heads: risers on the west wall's slabs, 30 from the south and north wall
    riser = sorted(box(lo, hi) for m, lo, hi in san if m == "Metall" and abs(lo[2] - zo - 1.0) < 1e-6 and room(lo, hi))
    assert len(riser) == 2 and all(abs(lo[0] - (5.59 + 0.012)) < 1e-6 for lo, hi in riser)
    assert near([(lo[1] + hi[1]) / 2 for lo, hi in riser], (0.70, 2.32))
    # toilet: on the north wall's tiles, ≥ 20 free to the glass and the basin, nothing within 60 in front
    toilet = [(m, lo, hi) for m, lo, hi in san if m in ("Keramik", "Metall") and 6.6 < lo[0] and hi[0] < 7.8
              and 1.8 < lo[1] and room(lo, hi) and hi[2] < zo + 0.85]                     # (in the room: #29)
    cistern = [(lo, hi) for m, lo, hi in toilet if m == "Keramik" and near((lo[2], hi[2]), (zo + 0.42, zo + 0.78))]
    assert len(cistern) == 1
    (lo, hi), = cistern
    assert abs((lo[0] + hi[0]) / 2 - 7.15) < 1e-6 and abs(hi[1] - (2.62 - T)) < 1e-6
    tx0, tx1 = min(lo[0] for m, lo, hi in toilet), max(hi[0] for m, lo, hi in toilet)
    ty0 = min(lo[1] for m, lo, hi in toilet)
    assert ty0 < 2.15                                                                 # faces south
    # basin on the east wall's tiles, centred between the door's architrave + 1 cm and the north wall
    basin = _waschbecken(("OG", "OG_Sanitaer"), (8.59, 2.14, -1, 0), 0.60, 0.47, 1, zo, T)
    bx0 = min(lo[0] for m, lo, hi in basin)
    assert tx0 - 6.494 >= 0.20 and bx0 - tx1 >= 0.20, (tx0, tx1, bx0)
    _clear([(m, lo, hi) for m, lo, hi in san if room(lo, hi)], [((tx0, ty0 - 0.60, zo + 0.02), (tx1, ty0 - 1e-6, zo + 2.0))],
           "in front of the toilet")
    # mirror 80 x 85 in a 10 cm frame over the basin, bottom at 1.17
    frame = [(lo, hi) for m, lo, hi in _parts(BP, ("OG", "OG_Spiegel")) if m == "Kiefer" and lo[0] > 8.5 and 0.4 < lo[1] < 2.62]
    assert len(frame) == 4
    assert near((min(lo[1] for lo, hi in frame), max(hi[1] for lo, hi in frame)), (2.14 - 0.40, 2.14 + 0.40))
    assert near((min(lo[2] for lo, hi in frame), max(hi[2] for lo, hi in frame)), (zo + 1.17, zo + 2.02))
    # tiles: north wall from the glass to the east wall, east wall down to the door; limestone on the strip
    fk = ("OG", "OG_Fliesen")
    tile = lambda x, y, h, dx, dy: "Fliese" in {_part_at(fk, x + k * dx, y + k * dy, zo + h) for k in (0, 0.04)}
    assert all(tile(x, 2.62 - 0.008, h, 1, 0) for x in (6.55, 7.5, 8.3) for h in (0.3, 0.6))      # 4 cm apart: never two joints
    assert all(tile(8.59 - 0.008, y, h, 0, 1) for y in (1.67, 2.0, 2.5) for h in (0.3, 0.6))
    assert all(_part_at(fk, 8.59 - 0.008, y, zo + h) is None for y in (1.0, 1.4, 1.64) for h in (0.3, 0.6, 0.9))
    stone = lambda x, y, h, dx, dy: "Kalkstein" in {_part_at(fk, x + k * dx, y + k * dy, zo + h) for k in (0, 0.03, 0.06)}
    assert all(stone(5.59 + 0.009, y, h, 0, 1) for y in (0.45, 1.0, 1.5, 2.0, 2.55) for h in (0.1, 1.0, 1.95))   # west
    assert all(stone(x, 0.40 + 0.009, h, 1, 0) for x in (5.65, 6.0, 6.4) for h in (0.1, 1.0, 1.95))           # south
    assert all(stone(x, 2.62 - 0.009, h, 1, 0) for x in (5.65, 6.0, 6.4) for h in (0.1, 1.0))                  # north
    slabs = [(lo, hi) for m, lo, hi in _parts(BP, fk) if m == "Kalkstein" and room(lo, hi)]
    assert max(hi[0] for lo, hi in slabs) < 6.49 - 0.004 and max(hi[2] for lo, hi in slabs) <= zo + 2.0 + 1e-6
    # #30: nothing on the north wall (the Waschküche partition) above its sill (1.70, #61), but the panes' ends
    for o in ("Fliesen", "Sanitaer", "Spiegel", "Wandlampen"):
        on = [(m, lo, hi) for m, lo, hi in _parts(BP, ("OG", "OG_" + o)) if room(lo, hi) and lo[1] > 2.62 - 0.03
              and hi[2] > zo + 1.70 + 1e-6 and not lo[0] < 6.49 < hi[0]]
        assert not on, (o, on)
    # lamps: two over the mirror, one left of the window (seen from inside)
    S, L = round(zo + house_core.WANDLAMPE_SPIEGEL_H, 3), round(zo + house_core.WANDLAMPE_H, 3)
    got = [r for r in _rosettes(BP, ("OG", "OG_Wandlampen")) if 5.5 < r[0][0] < 8.6 and r[0][1] < 2.7]
    want = [((8.59, round(2.14 + d, 3)), S, (-1, 0)) for d in (-0.20, 0.20)] + [((round((7.72 + 8.59) / 2, 3), 0.40), L, (0, 1))]
    same = lambda a, b: math.dist(a[0], b[0]) < 0.002 and a[1:] == b[1:]
    assert len(got) == len(want) and all(any(same(g, w) for g in got) for w in want), (got, want)
    # the open leaf clears lamps, toilet, basin, showers; nothing stands in the passage
    lamps = [(lo, hi) for m, lo, hi in _parts(BP, ("OG", "OG_Wandlampen")) if room(lo, hi)]
    _clear([("leaf", lo, hi) for lo, hi in leaf], lamps + [(lo, hi) for m, lo, hi in toilet + basin] + drain + glass + riser, "leaf")
    _clear([(m, lo, hi) for o in ("Sanitaer", "Fliesen", "Spiegel", "Wandlampen") for m, lo, hi in _parts(BP, ("OG", "OG_" + o))
            if room(lo, hi)], [passage], "passage")


def test_oberlicht_bad_waschkueche():
    """Issue #30: the partition between the Bad Nadine & Till and the Waschküche (y 2.62 .. 2.79) is glazed in its
    top half metre (#61: half as high as the first metre, at the ceiling): a pine lining of the full wall depth from
    its sill at 1.70 up to the 2.20 ceiling, 10 cm short of the
    side walls, three panes of Milchglas between two mullions, one of them on the shower glass line (x 6.49);
    plaster below and in the piers. Nothing of either room reaches into the glazing but the north shower pane and
    its rail, which end on that mullion; the same in the sub-model (web/elternbad.html). The plans still part the
    two rooms on the wall line (areas about 3.00 x 2.22 and 3.00 x 3.27)."""
    import elternbad as e, export_plans
    zo, ft = house_core.Z_OG, ("OG", "OG_Innentueren")
    wall = lambda lo, hi: 5.59 <= lo[0] and hi[0] <= 8.59 and 2.62 - 1e-6 <= lo[1] and hi[1] <= 2.79 + 1e-6
    own = [(m, lo, hi) for m, lo, hi in _parts(BP, ft) if wall(lo, hi) and lo[2] >= zo + 1.0]
    glass = sorted((lo, hi) for m, lo, hi in own if m == "Milchglas")
    assert len(glass) == 3 and {m for m, lo, hi in own} == {"Innentuer", "Milchglas"}
    assert e.SILL == 1.70 and abs(min(lo[2] for m, lo, hi in own) - (zo + 1.70)) < 1e-6   # 0.50 high (#61),
    assert abs(max(hi[2] for m, lo, hi in own) - (zo + 2.20)) < 1e-6                  # its top at the ceiling
    assert abs(min(lo[0] for m, lo, hi in own) - 5.69) < 1e-6 and abs(max(hi[0] for m, lo, hi in own) - 8.49) < 1e-6
    assert all(abs((lo[1] + hi[1]) / 2 - 2.705) < 1e-6 and hi[1] - lo[1] < 0.01 for lo, hi in glass)   # in the middle
    assert any(m == "Innentuer" and abs(lo[1] - 2.62) < 1e-6 and abs(hi[1] - 2.79) < 1e-6 and lo[0] < 6.49 - 0.012
               and hi[0] > 6.49 + 0.012 for m, lo, hi in own)                         # mullion on the glass line
    post = [(lo, hi) for m, lo, hi in own if m == "Innentuer" and lo[0] < e.XG < hi[0] and hi[0] - lo[0] < 0.1]
    end = [(lo, hi) for m, lo, hi in _parts(BP, ("OG", "OG_Sanitaer")) if lo[0] < e.XG < hi[0] and 2.5 < hi[1] < 2.64
           and hi[2] > zo + 1.70]                                             # the north pane and its rail, above the sill
    assert len(post) == 1 and len(end) == 2
    assert all(post[0][0][0] <= lo[0] and hi[0] <= post[0][1][0] and post[0][0][1] <= hi[1] for lo, hi in end)  # end on it
    wk = ("OG", "OG_Waende")
    assert all(_part_at(wk, x, 2.70, zo + h) is None for x in (6.0, 7.0, 8.0) for h in (1.75, 1.95, 2.15))
    assert all(_part_at(wk, x, 2.70, zo + h) == "Putz" for x in (6.0, 7.0, 8.0) for h in (0.6, 1.15, 1.65))
    assert all(_part_at(wk, x, 2.70, zo + 1.9) == "Putz" for x in (5.64, 8.54))      # the piers
    # nothing of the OG reaches into the glazing (3 cm in front of each face), but the north shower pane's end
    box = ((5.69, 2.62 - 0.03, zo + 1.70), (8.49, 2.79 + 0.03, zo + 2.20))
    for key in BP.geo:
        if key[0] == "OG":
            _clear([(m, lo, hi) for m, lo, hi in _parts(BP, key) if not (key == ft and wall(lo, hi))
                    and not (key[1] == "OG_Sanitaer" and lo[0] < e.XG < hi[0] and hi[1] < 2.64 and hi[2] <= zo + 2.02 + 1e-6)],
                   [box], key)
    # the four lamps over the Waschküche table hang under it
    lamps = [hi for m, lo, hi in _parts(BP, ("OG", "OG_Wandlampen")) if 5.59 < lo[0] < 8.5 and 2.79 <= lo[1] < 3.1]
    assert lamps and max(hi[2] for hi in lamps) < zo + 1.20
    regions, anchors = export_plans.room_regions(BP, "OG")
    area = {n: round(regions[anchors[k]]["area"], 3) for k, (n, st, x, y) in enumerate(BP.plan_rooms) if k in anchors}
    assert abs(area["Bad"] - 6.66) < 0.02 and abs(area["Hauswirtschaftsraum"] - 9.81) < 0.02, area   # 5 mm gaps
    # the sub-model: the same glazing
    bp = house_core.build_elternbad()
    house_core.build()                                                    # restore the registries
    x0, y0 = e.ELTERNBAD_AT
    sg = sorted(([lo[0] + x0, lo[1] + y0, lo[2] + zo], [hi[0] + x0, hi[1] + y0, hi[2] + zo])
                for m, lo, hi in _parts(bp, ("Elternbad", "Elternbad_Innentueren")) if m == "Milchglas")
    assert len(sg) == 3 and all(all(abs(p - q) < 1e-6 for p, q in zip(a + b, c + d)) for (a, b), (c, d) in zip(sg, glass))


def test_elternbad_submodel():
    """Issue #3: code/elternbad.py, the Bad Nadine & Till at its own origin (the room's inner SW corner; floor
    at z 0) with the pieces of its four walls and its dimension lines (web/elternbad.html); in the house it
    stands at ELTERNBAD_AT on the OG floor, every fixture, tile and lamp the same."""
    import elternbad as e
    bp = house_core.build_elternbad()
    house_core.build()                                                    # restore the registries
    assert e.ELTERNBAD_AT == (5.59, 0.40) and bp.garden is None
    assert {c for c, _ in bp.geo} == {"Elternbad"}
    assert {"Elternbad_Waende", "Elternbad_Sanitaer", "Elternbad_Fliesen", "Elternbad_Innentueren", "Elternbad_Spiegel",
            "Elternbad_Wandlampen", "Elternbad_Fenster_Tueren"} <= {n for _, n in bp.geo}
    x0, y0 = e.ELTERNBAD_AT
    sub = lambda n: {tuple(sorted({(round(v[0] + x0, 5), round(v[1] + y0, 5), round(v[2] + house_core.Z_OG, 5))
                                   for f in g_["f"][a:a + k] for i in f for v in [g_["v"][i]]}))
                     for g_ in [bp.geo[("Elternbad", "Elternbad_" + n)]] for a, k in bp.parts[("Elternbad", "Elternbad_" + n)]}
    house = lambda n: {tuple(sorted({(round(v[0], 5), round(v[1], 5), round(v[2], 5)) for f in g_["f"][a:a + k] for i in f
                                     for v in [g_["v"][i]]}))
                       for g_ in [BP.geo[("OG", "OG_" + n)]] for a, k in BP.parts[("OG", "OG_" + n)]}
    for n in ("Sanitaer", "Fliesen", "Spiegel"):                          # the lamps: by their lights below
        assert sub(n) <= house(n), n
    assert len(bp.wall_lights) == 3 and len(bp.parts[("Elternbad", "Elternbad_Wandlampen")]) == 3 * 8
    for x, y, z in bp.wall_lights:
        assert any(math.dist((x + x0, y + y0, z + house_core.Z_OG), q) < 1e-6 for q in BP.wall_lights), (x, y, z)
    # the floor (request 2026-11-13): the house's limestone, also on the page (in the house: floor_cover, BATHS_OG)
    fl = [(m, lo, hi) for m, lo, hi in _parts(bp, ("Elternbad", "Elternbad_Bodenbelag"))]
    assert fl and {m for m, lo, hi in fl} == {"Kalkstein"}
    assert all(abs(hi[2] - 0.018) < 1e-6 and abs(lo[2] - 0.002) < 1e-6 for m, lo, hi in fl)
    assert ("Elternbad", "Elternbad_Laeden") in bp.geo                    # the window's shutters, as in the house
    area = sum((hi[0] - lo[0]) * (hi[1] - lo[1]) for m, lo, hi in fl)
    assert 0.95 * (e.WO - e.WI) * (e.YN - e.YS) < area <= (e.WO - e.WI) * (e.YN - e.YS) + 1e-6    # the whole room
    assert min(lo[0] for m, lo, hi in fl) >= -1e-6 and max(hi[0] for m, lo, hi in fl) <= e.WO - e.WI + 1e-6
    labels = [d[2] for d in bp.dims]
    for t in ("Duschen 90", "Glas 80", "Durchgang 60", "Waschbecken 60", "Spiegel 80 × 85", "Tür 93", "Fenster 88"):
        assert t in labels, (t, labels)


def test_waschkueche_has_a_tile_floor():
    """Issue #28: „Die Waschküche soll keinen Holzboden bekommen, sondern einen Fliesenboden.“ The whole Waschküche
    (x 5.59 .. 8.59, y 2.79 .. 6.06) gets the limestone of the OG baths, none under its walls, no oak left in it, no
    two floor slabs overlap (no z-fight)."""
    zo, (x0, x1, y0, y1) = house_core.Z_OG, waschkueche.ROOM
    assert (x0, x1, y0, y1) == (5.59, 8.59, 2.79, 6.06)
    fl = [(m, lo, hi) for m, lo, hi in _parts(BP, ("OG", "OG_Bodenbelag"))
          if lo[0] < x1 - 1e-6 and x0 + 1e-6 < hi[0] and lo[1] < y1 - 1e-6 and y0 + 1e-6 < hi[1]]
    assert {m for m, lo, hi in fl} == {"Kalkstein"}                                  # no oak in the room
    assert all(x0 - 1e-6 <= lo[0] and hi[0] <= x1 + 1e-6 and y0 - 1e-6 <= lo[1] and hi[1] <= y1 + 1e-6
               and abs(hi[2] - zo - 0.018) < 1e-6 for m, lo, hi in fl)           # none under the walls, tile plane
    area = sum((hi[0] - lo[0]) * (hi[1] - lo[1]) for m, lo, hi in fl)
    assert 0.95 * (x1 - x0) * (y1 - y0) < area <= (x1 - x0) * (y1 - y0) + 1e-6     # the whole room
    assert not [(a, b) for i, a in enumerate(fl) for b in fl[i + 1:]                 # no slab twice (the cabin's)
                if all(a[1][k] < b[2][k] - 1e-6 and b[1][k] < a[2][k] - 1e-6 for k in range(2))]
    pts = lambda ps: {_floor_at("OG", x, y) for x, y in ps} - {None}
    assert pts([(6.64, 5.5), (6.74, 5.5), (6.1, 4.91), (6.1, 5.01), (8.5, 2.85)]) == {"Kalkstein"}
    assert pts([(7.0, 6.3), (5.0, 4.0)]) == {"Eiche"}                                # Flur, Bad side: unchanged


def test_wcs_have_limestone_floors():
    """Request 2026-11-08: all toilets get stone floors (the limestone of the EG Flur and the
    Bäder): the three WCs of WCS and the Bad Großeltern's niche (since #63 WC and shower)."""
    for c, z, (x0, x1, y0, y1), *_ in WCS:                                  # incl. the WC Großeltern
        assert _floor_at(c, (x0 + x1) / 2 + 0.02, (y0 + y1) / 2 + 0.03) == "Kalkstein", (c, x0, y0)
    assert _floor_at("EG", 1.9, 9.3) == "Kalkstein"                       # its shower (#63)


def _solids(bp, key, dx=0.0, dy=0.0):
    g = bp.geo[key]
    return {tuple(sorted({(round(g["v"][i][0] + dx, 6), round(g["v"][i][1] + dy, 6), round(g["v"][i][2], 6))
                          for f in g["f"][a:a + n] for i in f})) for a, n in bp.parts[key]}


def test_kueche_submodel():
    """code/kueche.py: the Küche after the agreed drawing input/2026-11-09 input/speis_kueche_v6.svg,
    at its own origin (the room's inner NW corner: Speis wall x Flur wall, so y <= 0): the sink run
    from the kitchen door's frame into the NE corner, under the flue box (from 1.80 m up); the east
    run 60 from the peninsula's front, the Wamsler right south of it; the Besenschrank 51 x 55 x
    2.20 in the NW corner behind the open kitchen door; peninsula unchanged. In the house it stands
    at KUECHE_AT, every part the same."""
    import kueche
    sub = house_core.build_kueche()
    house_core.build()                                                    # restore the registries
    assert kueche.KUECHE_AT == (5.49, 5.849)
    x0, y0 = kueche.KUECHE_AT
    assert {c for c, _ in sub.geo} == {"Kueche"} and sub.garden is None
    assert {n for _, n in sub.geo} == {"Kueche_Kueche", "Kueche_Herd", "Kueche_Waende"}   # no hood (#61)
    assert all(-1e-9 <= x <= 3.067 + 1e-9 and -2.845 <= y <= 1e-9 for (_, n), g in sub.geo.items() for x, y, z in g["v"]
               if n != "Kueche_Herd")                                # (the Wamsler's pipe runs into the wall;
                                                                     # y: the cup pulls towards the dining table)
    for n in ("Kueche", "Herd", "Waende"):
        assert _solids(sub, ("Kueche", "Kueche_" + n), x0, y0) <= _solids(BP, ("EG", "EG_" + n)), n
    k = list(part_list(("EG", "EG_Kueche")))
    base = [p for p in k if p[2][2] <= 0.901 and p[1][2] < 0.2]
    sink = [p for p in base if p[1][1] > 5.2 and p[1][0] > 6.5]                # sink run: carcass, fronts, plinth
    assert abs(min(p[1][0] for p in sink) - 7.05) < 0.005 and max(p[2][0] for p in sink) > 8.55
    top = [p for p in k if p[0] == "Granit" and p[1][1] > 5.0]                 # (to the Herd since 2026-11-10)
    assert top and abs(min(p[1][0] for p in top) - 7.05) < 0.005 and max(p[2][0] for p in top) > 8.55
    east = [p for p in base if p[1][0] > 7.9 and 3.6 < p[1][1] and p[2][1] < 4.3]
    fronts = [p for p in k if p[0] == "Front" and 7.95 < p[1][0] < 7.96 and p[2][2] < 0.9 and p[2][1] < 4.5]
    assert east and abs(max(p[2][1] for p in fronts) - min(p[1][1] for p in fronts) - 0.60) < 0.01
    herd = _herd_body()
    assert abs(min(p[1][1] for p in herd) - 4.30) < 0.005 and abs(max(p[2][1] for p in herd) - 5.10) < 0.005
    besen = [p for p in k if p[1][0] < 5.5 and p[1][1] > 5.2]
    lo = [min(p[1][i] for p in besen) for i in range(3)]; hi = [max(p[2][i] for p in besen) for i in range(3)]
    assert abs(lo[0] - 5.492) < 0.003 and abs(hi[0] - 6.002) < 0.003 and abs(lo[1] - 5.297) < 0.003
    assert hi[1] <= 5.849 and abs(hi[2] - 2.20) < 0.01
    flue = [p for p in part_list(("EG", "EG_Waende")) if p[1][0] > 8.2 and p[1][1] > 5.5 and p[2][0] < 8.56 and p[2][1] < 5.85]
    assert len(flue) == 1 and abs(flue[0][1][2] - 1.80) < 0.005 and flue[0][0] == "Putz"
    assert not any(p[2][2] > flue[0][1][2] and p[1][2] < 2.4 and p[2][0] > flue[0][1][0] and p[2][1] > flue[0][1][1]
                   for p in k)                                                # nothing in the flue box
    labels = {t for _, _, t in sub.dims}
    assert {"Spülzeile 150.5", "Ostzeile 60", "Herd 80", "Besenschrank 51", "55 tief", "Abzug ab 180",
            "Halbinsel 198.5", "Abzug 30 tief (angenommen)"} <= labels


def test_kuechentuer_as_built():
    """The kitchen door to the Flur where it really is (photo 2026-11-09, speis_kueche_v6.svg):
    architraves 6.03-7.03, clear 81 cm; hinged west, the leaf opened 90 deg into the Küche, east of
    the Besenschrank; the plan's opening further east is wall."""
    w = ("EG", "EG_Waende")
    assert _mat_at(BP, w, 6.5, 6.1, 1.0) is None and _mat_at(BP, w, 7.5, 6.1, 1.0) == "Putz"
    assert _mat_at(BP, w, 6.05, 6.1, 1.0) == "Putz" and _mat_at(BP, w, 7.0, 6.1, 1.0) == "Putz"
    leaf = [l for c, l in house_core.LEAVES if c == "EG" and 6.0 < min(l[0][0], l[1][0]) < 6.3
            and max(l[0][1], l[1][1]) < 5.86 and min(l[0][1], l[1][1]) < 5.2]
    assert len(leaf) == 1
    (a, b), = leaf
    assert min(a[0], b[0]) > 6.002 + 0.05 and max(a[0], b[0]) < 6.25                     # clear of the Besenschrank
    trim = [p for p in part_list(("EG", "EG_Innentueren")) if 5.8 < p[1][1] < 5.86 and 5.9 < p[1][0] < 7.1]
    assert abs(min(p[1][0] for p in trim) - 6.03) < 0.005 and abs(max(p[2][0] for p in trim) - 7.03) < 0.005


def test_speis_v6():
    """Speis after speis_kueche_v6.svg: from the Flur wall south shelf A (60, open), the aisle 91.9
    (west end free), shelf B (60, open to the aisle) and its closed back towards the Essen in
    place of the Speis/Essen wall, all to the ceiling; the Speis/Küche wall ends at B's back (y 3.73)
    and has a panel door over the aisle (#61: in place of the saloon leaves, test_speis_essen)."""
    w = ("EG", "EG_Waende")
    assert _mat_at(BP, w, 4.0, 3.2, 1.0) is None                                          # Speis/Essen wall gone
    assert _mat_at(BP, w, 5.36, 3.5, 1.0) is None and ("EG", "EG_Speis_Waende") not in BP.geo   # no stub (#34)
    assert _mat_at(BP, w, 5.36, 4.2, 1.0) == "Putz"
    assert _mat_at(BP, w, 5.36, 4.8, 1.0) is None and _mat_at(BP, w, 5.36, 3.05, 1.0) is None
    sp = list(part_list(("EG", "EG_Speis")))
    assert sp and "EG_Speis" not in BP.furniture
    for ya, yb in ((5.249, 5.847), (3.732, 4.33)):                                        # A, B
        band = [p for p in sp if p[1][1] >= ya - 1e-6 and p[2][1] <= yb + 1e-6]
        assert band and abs(min(p[1][1] for p in band) - ya) < 0.003 and abs(max(p[2][1] for p in band) - yb) < 0.003
        assert min(p[1][0] for p in band) < 2.78 and max(p[2][0] for p in band) > 5.23
        assert 2.39 <= max(p[2][2] for p in band) < 2.40
    assert not any(p[2][1] > 4.34 and p[1][1] < 5.24 for p in sp)                          # the aisle is free
    assert not any(p[2][0] > 2.78 and p[1][0] < 5.24 and p[2][1] > 3.13 and p[1][1] < 5.85
                   for p in part_list(("EG", "EG_Moebel")))                                # old shelves gone
    leaves = [l for c, l in house_core.LEAVES if c == "EG" and 5.49 < min(l[0][0], l[1][0]) < 5.6]
    assert len(leaves) == 1 and max(l[1] for l in leaves[0]) <= 4.33 + 1e-6    # the Speis door (#61), open flat


def test_bad_windows():
    """Request 2026-11-25: the Bad Großeltern's north french door became a window (sill 1.00, head 2.00, shutters).
    Issue #63: the old shower in the NW corner and its glass are gone; the west wall, free between the niche's front
    wall (y 10.076) and the north wall, takes a window 198 wide, centred, sill 0.75 up to the EG ceiling like the OG's
    west windows, larch trims round it in the west cladding; no Wandlampe in its way."""
    import bad
    x0, y0, D = *bad.BAD_AT, bad.D
    north = lambda k: [op for op in house_core.OPENINGS if op["kind"] == k and op["ax"] == "x"
                       and abs(op["face"] - house_core.D_OUT) < 0.4 and op["a"] < 2.0]
    assert north("FD") == []
    win = north("W")
    assert len(win) == 1 and (win[0]["a"], win[0]["b"], win[0]["sill"], win[0]["head"]) == (1.109, 2.008, 1.0, 2.0)
    west = [op for op in house_core.OPENINGS if op["ax"] == "y" and abs(op["face"]) < 0.4 and op["a"] > 10.0]
    assert len(west) == 1 and west[0]["kind"] == "W"
    a, b, sill, head = west[0]["a"], west[0]["b"], west[0]["sill"], west[0]["head"]
    assert round(b - a, 3) == 1.98 and (sill, head) == (0.75, house_core.Z_EG_TOP)
    assert abs((a - 10.076) - (y0 + D - b)) < 0.0015                           # centred on the free wall (mm)
    og = [op for op in house_core.OPENINGS if op["ax"] == "y" and abs(op["face"]) < 0.4 and op["sill"] > house_core.Z_OG]
    assert {round(op["head"], 3) for op in og if op["sill"] == house_core.Z_OG + 0.75} == {house_core.Z_OG_TOP}   # like these
    assert not [p for p in part_list(("EG", "EG_Sanitaer")) if p[0] == "Glas" and p[1][1] > y0 + bad.NICHE and p[2][0] < 2.4]
    assert not [p for p in part_list(("EG", "EG_Waende")) if x0 < p[1][0] and p[2][0] < 2.358 and 10.1 < p[1][1] < 12.47]   # no low wall
    trims = [p for p in part_list(("Dach", "Verschalung_West")) if p[2][0] < 0.0 and abs(p[1][2] - (head)) < 1e-6]
    assert trims and min(p[1][1] for p in trims) <= a and max(p[2][1] for p in trims) >= b   # head trim over the window
    lamps = [p for p in part_list(("EG", "EG_Wandlampen")) if p[1][0] < 0.5 and p[2][1] > a and p[1][1] < b]
    assert not lamps


def test_wc_tiles_in_ral_5014():
    """Request 2026-11-10: the formerly green WC / Bad tiles in the house's RAL 5014 Taubenblau:
    their speckle's two colours lie around RAL 5014 (linear), no longer green; no green tiles left."""
    lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    ral = [lin(v / 255) for v in house_core.RAL_5014]
    c1, c2, _ = house_core.MAT_DEF["Fliese"]["speck"]
    mid = [(a + b) / 2 for a, b in zip(c1, c2)]
    assert all(abs(m - r) < 0.01 for m, r in zip(mid, ral)), mid
    assert all(c[2] > c[1] > c[0] for c in (c1, c2))                        # blue, not green


def test_stone_floor_runs_through_the_back_windfang_door():
    """Request 2026-11-10: in the doorway from the Flur to the back Windfang (glazed door in the
    wall x 2.358 .. 2.657) the limestone runs through, no oak threshold."""
    for x in (2.40, 2.50, 2.62):
        for y in (7.5, 7.95, 8.45):
            assert _floor_at("EG", x, y) == "Kalkstein", (x, y)


def test_speis_shelves_stocked():
    """Request 2026-11-10, for illustration: the Speis's open shelves A and B stocked with food
    (spaghetti and cereal cartons, jars of tomato sauce and pickles, cans, flour bags) and now and
    then a bigger grey plastic crate for odds and ends; standing on the boards, clear of the
    uprights and the board above, near the aisle side; loose things of the "Eingerichtet" stage."""
    key = ("EG", "EG_Vorrat")
    assert key in BP.geo and "EG_Vorrat" in BP.furniture
    parts = list(part_list(key))
    tops = [0.10, 0.48, 0.86, 1.24, 1.62, 2.00]
    x0, x1, n = 2.774, 5.238, 3
    posts = [(x0 + (x1 - x0 - 0.02) * k / n, x0 + (x1 - x0 - 0.02) * k / n + 0.02) for k in range(n + 1)]
    for m, lo, hi, _ in parts:
        assert x0 + 0.02 < lo[0] and hi[0] < x1 - 0.02, (m, lo)
        assert 5.254 < lo[1] and hi[1] < 5.842 or 3.737 < lo[1] and hi[1] < 4.325, (m, lo)
        assert not any(a < hi[0] and lo[0] < b for a, b in posts), (m, lo)          # clear of the uprights
        z = max(t for t in tops if t <= lo[2] + 1e-9)
        assert lo[2] - z < 0.30 and hi[2] < z + 0.38 - 0.025 - 0.01, (m, lo, hi)   # under the board above
    feet = [lo for m, lo, hi, _ in parts if any(abs(lo[2] - t - 0.001) < 1e-6 for t in tops)]
    assert len(feet) > 80                                                         # well stocked
    mats = {m for m, _, _, _ in parts}
    assert {"Kiste", "Metall", "Gurken", "PackRot", "PackBlau", "PackGelb", "PackWeiss"} <= mats
    crates = [p for p in parts if p[0] == "Kiste" and p[2][0] - p[1][0] > 0.35]
    assert 4 <= len(crates) // 2 <= 16                                            # body + lid each, now and then
    for _, lo, hi, _ in crates:
        assert 0.18 < hi[2] - lo[2] < 0.30 or hi[2] - lo[2] < 0.02                 # body or its lid
    for side, face in (("A", 5.249), ("B", 4.33)):                                # near the aisle
        sp = [p for p in parts if (p[1][1] > 5.0) == (side == "A")]
        assert sp and min(abs(p[1][1] - face) if side == "A" else abs(p[2][1] - face) for p in sp) < 0.06


def test_gaeste_wc_submodel():
    """Issue #61 (variant B, the user 2026-11-27): the back hall's Gäste-WC and Garderobe are one Duschbad, its north
    wall 20 cm further north (room 205 x 130), at its own origin (the room's inner SW corner): no partition; a walk-in
    shower 90 x 130 in the east (glass 75 from the south wall, entry 55, limestone to 2.0, head on the east wall, the
    drain in its middle, no tray), the toilet on the south wall in the west (Taubenblau tiles on the WC part's walls,
    60 free in front), a Waschbecken einzeln 40 on its Ständer on the west wall north of the window under a mirror
    40 x 60 in a wooden frame; the door 76 in the north wall's west part, opened 90 deg outward into the back hall,
    hinged east; the Flur basin is gone."""
    import gaeste_wc as g
    bp = house_core.build_gaeste_wc()
    leaves = [pts for c, pts in house_core.LEAVES if c == "GaesteWC"]
    house_core.build()                                                    # restore the registries
    assert g.WC_AT == (0.31, 5.475) and bp.garden is None
    assert {c for c, _ in bp.geo} == {"GaesteWC"}
    assert {n for _, n in bp.geo} == {"GaesteWC_Waende", "GaesteWC_Innentueren", "GaesteWC_Sanitaer", "GaesteWC_Spiegel",
                                      "GaesteWC_Fliesen", "GaesteWC_Schuhregal", "GaesteWC_Kleidung", "GaesteWC_WC_Tuer",
                                      "GaesteWC_Windfangtuer", "GaesteWC_Hintertuer", "GaesteWC_Fenster_Tueren"}
    x0, y0 = g.WC_AT
    cm = lambda a, b: round(abs(b - a) * 100)
    K = lambda n: ("GaesteWC", "GaesteWC_" + n)
    H = (lambda p: [m for m, lo, hi in _parts(bp, K("Waende"))
                    if lo[0] - 1e-6 <= p[0] - x0 <= hi[0] + 1e-6 and lo[1] - 1e-6 <= p[1] - y0 <= hi[1] + 1e-6
                    and lo[2] < p[2] < hi[2]])                              # wall material at a house point
    # the room: 205 x 130, the north wall 20 cm north of the old one, no partition
    assert (cm(g.WI, g.WO), cm(g.YS, g.YN), cm(g.YN, g.YF), round(g.YN - 6.574, 3)) == (205, 130, 15, 0.2)
    assert not [1 for m, lo, hi in _parts(bp, K("Waende")) if lo[1] + y0 < g.YN - 1e-6]
    for x in (0.40, 1.80, 2.30):
        assert H((x, 6.85, 1.0)) == ["Putz"] and H((x, 6.65, 1.0)) == []
    assert H((1.06, 6.85, 1.0)) == [] and H((1.06, 6.85, 2.2)) == ["Putz"]      # the door, 2.00 high
    assert (cm(g.WI, g.DA), cm(g.DA, g.DB)) == (37, 76)
    # the WC leaf (the other: the Windfang door's), opened 90 deg into the back hall, at its east jamb
    assert len(leaves) == 2
    lo, hi = ([f(a, b) for a, b in zip(*leaves[0])] for f in (min, max))
    assert hi[0] - lo[0] < 0.05 and g.DB - 0.10 < lo[0] + x0 and hi[0] + x0 <= g.DB
    assert lo[1] + y0 >= g.YF - 1e-6 and hi[1] + y0 > g.YF + 0.65
    # shower: 90 wide, the pane 75 from the south wall, entry 55; drain in its middle, head on the east wall
    san = list(_parts(bp, K("Sanitaer")))
    glass = [(lo, hi) for m, lo, hi in san if m == "Glas"]
    assert len(glass) == 1 and abs((glass[0][0][0] + glass[0][1][0]) / 2 + x0 - g.XS) < 1e-6
    assert (cm(g.XS, g.WO), cm(0, glass[0][1][1] - 0.004 + y0 - g.YS), cm(g.YS + g.GL, g.YN)) == (90, 75, 55)
    drain = [(lo, hi) for m, lo, hi in san if m == "Metall" and abs(lo[2] - 0.018) < 1e-6 and hi[2] - lo[2] < 0.01]
    assert len(drain) == 1 and abs((drain[0][0][0] + drain[0][1][0]) / 2 + x0 - (g.XS + g.WO) / 2) < 1e-6
    riser = [(lo, hi) for m, lo, hi in san if m == "Metall" and hi[2] - lo[2] > 1.0]
    assert len(riser) == 1 and riser[0][1][0] + x0 > g.WO - 0.06                  # on the east wall
    til = list(_parts(bp, K("Fliesen")))
    stone = [(lo, hi) for m, lo, hi in til if m == "Kalkstein"]
    assert stone and all(lo[0] + x0 >= g.XS - 1e-6 and hi[2] <= 2.0 + 1e-6 for lo, hi in stone)
    for x, y in ((g.WO - 0.009, 5.8), (g.WO - 0.009, 6.6), (1.9, g.YS + 0.009), (1.9, g.YN - 0.009)):
        assert _mat_at(bp, K("Fliesen"), x - x0, y - y0, 1.5) in ("Kalkstein", "Fuge"), (x, y)
    assert not [1 for m, lo, hi in san if m == "Keramik" and lo[0] + x0 > g.XS]           # no tray
    # toilet on the south wall in the WC part, 60 free in front of it, clear of the glass
    toilet = [(lo, hi) for m, lo, hi in san if m == "Keramik" and lo[1] + y0 < g.YS + 0.8 and lo[0] + x0 > g.WI + 0.3]
    cis = [(lo, hi) for lo, hi in toilet if abs(hi[2] - 0.78) < 1e-6]
    assert len(cis) == 1 and abs((cis[0][0][0] + cis[0][1][0]) / 2 + x0 - g.TX) < 1e-6
    assert cm(max(hi[1] for lo, hi in toilet) + y0, g.YN) >= 55 and max(hi[0] for lo, hi in toilet) + x0 < g.XS - 0.2
    # Taubenblau tiles only in the WC part, to about 112
    fl = [(lo, hi) for m, lo, hi in til if m == "Fliese"]
    assert fl and all(hi[0] + x0 <= g.XS + 1e-6 for lo, hi in fl) and cm(0, max(hi[2] for lo, hi in fl)) == 112
    # basin on the west wall north of the window, its mirror above, both clear of the window (y 5.724 .. 6.324)
    wb = _waschbecken(K("Sanitaer"), (g.WI - x0, g.BM - y0, 1, 0), g.BW, g.BD, 1, 0.0, house_core.WC_TILE_T, bp=bp)
    assert min(lo[1] for m, lo, hi in wb) + y0 > 6.324 and max(hi[1] for m, lo, hi in wb) + y0 < g.YN
    mir = list(_parts(bp, K("Spiegel")))
    assert min(lo[1] for m, lo, hi in mir) + y0 > 6.324 and max(hi[1] for m, lo, hi in mir) + y0 < g.YN
    gl, = [(lo, hi) for m, lo, hi in mir if m == "Spiegel"]
    flo = [min(lo[k] for m, lo, hi in mir) for k in range(3)]; fhi = [max(hi[k] for m, lo, hi in mir) for k in range(3)]
    assert (cm(flo[1], fhi[1]), cm(flo[2], fhi[2]), cm(0, flo[2])) == (40, 60, 120)
    # the basin and toilet clear of the three leaves in both states
    for n in ("Hintertuer", "WC_Tuer", "Windfangtuer"):
        (px, py, _), vs = bp.pivot["GaesteWC_" + n], bp.geo[K(n)]["v"]
        for a in (0.0, math.radians(bp.swing["GaesteWC_" + n])):
            rot = [(px + (x - px) * math.cos(a) - (y - py) * math.sin(a),
                    py + (x - px) * math.sin(a) + (y - py) * math.cos(a), z) for x, y, z in vs]
            _clear(wb + list(_parts(bp, K("Schuhregal"))), [tuple(tuple(f(v[k] for v in rot) for k in range(3)) for f in (min, max))], n)
    # everything below the ceiling; dimension lines from the core
    assert all(-1e-9 <= z <= 2.40 + 1e-9 for gg in bp.geo.values() for x, y, z in gg["v"])
    labels = [d[2] for d in bp.dims]
    for t in ("Raumbreite 205", "Raumtiefe 130", "Dusche 90", "Glas 75", "Einstieg 55", "Tür 76", "HWB 40",
              "Spiegel 40 × 60", "Schuhregal 80", "33 tief", "200 hoch"):
        assert t in labels, t


def test_schuhregal():
    """Issue #61: in the back hall, on the Duschbad's north wall east of its door, a spruce shoe rack 80 wide (to the
    east wall), 33 deep, 2 m high with nine levels of about 20 cm, about half full of shoes spread over the levels (<c>_Kleidung); rack and shoes
    are furniture (stage Eingerichtet); nothing clashes with walls, lamps and the three door leaves in both states."""
    import gaeste_wc as g
    assert {"EG_Schuhregal", "EG_Kleidung"} <= house_core.FURNITURE
    cm = lambda a, b: round(abs(b - a) * 100)
    rack = list(_parts(BP, ("EG", "EG_Schuhregal")))
    assert all(g.SX - 1e-6 <= lo[0] and hi[0] <= g.WO + 1e-6 and g.YF - 1e-6 <= lo[1] and hi[1] <= g.YF + g.SHOE_D + 1e-6
               for m, lo, hi in rack)
    boards = sorted([(lo, hi) for m, lo, hi in rack if m == "FichteX" and hi[1] - lo[1] > 0.3], key=lambda b: b[0][2])
    assert len(boards) == 10 and all(cm(lo[1], hi[1]) == 33 and cm(lo[0], hi[0]) == 76 for lo, hi in boards)
    assert all(19 <= cm(a[1][2], b[0][2]) <= 20 for a, b in zip(boards, boards[1:]))          # nine levels of ~20
    assert abs(max(hi[2] for m, lo, hi in rack) - 2.0) < 1e-6                                # 2 m high (#61)
    shoes = [(m, lo, hi) for m, lo, hi in _parts(BP, ("EG", "EG_Kleidung")) if lo[1] < g.YF + g.SHOE_D + 0.01
             and lo[0] < g.WO and hi[0] > g.SX]
    soles = [(lo, hi) for m, lo, hi in shoes if m == "Gummi"]
    assert len(soles) == 2 * g.SHOE_PAIRS and 12 <= g.SHOE_PAIRS <= 15                     # about half of 27 places
    tops = [z + g.SHOE_T for z in g.SHOE_Z[:-1]]
    per = [sum(abs(lo[2] - t) < 0.003 for lo, hi in soles) for t in tops]
    assert sum(per) == len(soles) and max(per) <= 6 and sum(1 for n in per if n) >= 6           # spread, not all below
    assert any(n for n in per[5:])                                                            # also high up
    for m, lo, hi in shoes:
        level = max(t for t in tops if t <= lo[2] + 0.003)
        assert hi[2] < level + 0.20 - 0.02 and hi[1] < g.YF + g.SHOE_D, (m, lo, hi)
    others = [("EG", "EG_" + n) for n in ("Waende", "Wandlampen", "Fenster_Tueren", "Innentueren", "Hintertuer",
                                         "WC_Tuer", "Windfangtuer")]
    _clear(rack + [p for p in shoes], [(lo, hi) for k in others for m, lo, hi in _parts(BP, k)], "Schuhregal")
    for n in ("Hintertuer", "WC_Tuer", "Windfangtuer"):                             # the leaves swung
        (px, py, _), vs = BP.pivot["EG_" + n], BP.geo[("EG", "EG_" + n)]["v"]
        a = math.radians(BP.swing["EG_" + n])
        rot = [(px + (x - px) * math.cos(a) - (y - py) * math.sin(a),
                py + (x - px) * math.sin(a) + (y - py) * math.cos(a), z) for x, y, z in vs]
        _clear(rack + shoes, [tuple(tuple(f(v[k] for v in rot) for k in range(3)) for f in (min, max))], n)

def test_gaeste_wc_built_into_the_house():
    """The Duschbad sub-model stands in the house at WC_AT, unrotated, every part the same; the old
    WC door (into the WC) and its toilet are gone; limestone in the whole room (#61: also where the partition and
    the old north wall stood) and in the back hall."""
    import gaeste_wc as g
    sub = house_core.build_gaeste_wc()
    house_core.build()                                                    # restore the registries
    x0, y0 = g.WC_AT
    for n in ("Waende", "Innentueren", "Sanitaer", "Fliesen", "Schuhregal", "Kleidung", "WC_Tuer", "Windfangtuer",
              "Hintertuer", "Fenster_Tueren"):
        assert _solids(sub, ("GaesteWC", "GaesteWC_" + n), x0, y0) <= _solids(BP, ("EG", "EG_" + n)), n
    eg = [pts for c, pts in house_core.LEAVES if c == "EG"]
    assert not any(min(a[0], b[0]) > 1.3 and max(a[0], b[0]) < 2.3 and min(a[1], b[1]) < 6.6 and max(a[1], b[1]) > 5.5
                   for a, b in eg)                                                                 # old leaf
    assert any(abs(max(a[0], b[0]) - (g.DB - 0.025)) < 0.01 and max(a[1], b[1]) > 7.5 for a, b in eg)   # WC leaf
    cist = [lo for m, lo, hi in _parts(BP, ("EG", "EG_Sanitaer")) if m == "Keramik" and abs(hi[2] - 0.78) < 1e-6
            and 5.4 < lo[1] < 6.6 and lo[0] < 2.4]
    assert len(cist) == 1 and abs(cist[0][0] + 0.20 - g.TX) < 1e-6
    for x, y in ((0.8, 6.0), (1.9, 6.0), (1.37, 6.0), (1.0, 6.65), (2.0, 6.7), (1.0, 7.0)):
        assert _floor_at("EG", x, y) == "Kalkstein", (x, y)


def test_gaeste_wc_doors_swing():
    """Request 2026-11-10: the three doors by the back hall (Hintertür, WC door, Windfang door) open
    and close at random in the viewer to show where they get in each other's way. Each leaf is its
    own object with its origin at the hinge (PIVOT) and SWING = the yaw (degrees, about z) from as
    built to its other state: the back door (closed) opens 90 deg into the Flur, the WC and Windfang
    doors (open 90 deg) close into their linings. The same in the sub-model, shifted by WC_AT."""
    import gaeste_wc as g
    sub = house_core.build_gaeste_wc()
    house_core.build()                                                    # restore the registries
    x0, y0 = g.WC_AT
    assert BP.swing == {"EG_Hintertuer": 90.0, "EG_WC_Tuer": 90.0, "EG_Windfangtuer": 90.0,   # back door, Windfang: hinged north
                        "EG_Buerotuer": 90.0}                                                  # (and the Büro door, code/regal.py;
                                                                                               # the saloon leaves gone, #61)
    assert sub.swing == {"GaesteWC_Hintertuer": 90.0, "GaesteWC_WC_Tuer": 90.0, "GaesteWC_Windfangtuer": 90.0}
    for n in ("Hintertuer", "WC_Tuer", "Windfangtuer"):
        px, py, pz = sub.pivot["GaesteWC_" + n]
        assert math.dist(BP.pivot["EG_" + n], (px + x0, py + y0, pz)) < 1e-9, n

    def turned(n, pts=False):                                             # the leaf at its other state
        (px, py, _), a = BP.pivot[n], math.radians(BP.swing[n])
        g = BP.geo[("EG", n)]                                             # its body: the levers stand proud
        body = {i for f, m in zip(g["f"], g["m"]) if m != "Eisen" for i in f}
        vs = [(px + (x - px) * math.cos(a) - (y - py) * math.sin(a), py + (x - px) * math.sin(a) + (y - py) * math.cos(a))
              for x, y, z in (g["v"][i] for i in sorted(body))]
        return vs if pts else ([min(v[k] for v in vs) for k in (0, 1)], [max(v[k] for v in vs) for k in (0, 1)])

    lo, hi = turned("EG_WC_Tuer")                                         # closed: in the WC door's lining
    assert g.DA < lo[0] and hi[0] < g.DB and g.YN < lo[1] and hi[1] <= g.YF + 1e-6
    lo, hi = turned("EG_Windfangtuer")                                    # closed: in the Windfang door's lining
    assert 2.358 - 0.03 < lo[0] and hi[0] < 2.657                          # (its lever 2.5 cm proud) and 7.408 < lo[1] and hi[1] < 8.506
    lo, hi = turned("EG_Hintertuer")                                      # open: in the Flur, clear of its frame
    assert lo[0] > 0.0 and hi[0] > 0.8 and lo[1] > 7.408 and hi[1] > 8.1                  # at the north jamb
    assert all(y < 8.377 - 0.09 for x, y in turned("EG_Hintertuer", True) if x < 0.31)   # in the wall: clear of the jamb
    # as built (open): the Windfang leaf lies along the back hall's north wall (8.506), in front of it
    g = BP.geo[("EG", "EG_Windfangtuer")]                                 # its body (the levers stand proud)
    wl = [g["v"][i] for i in sorted({i for f, m in zip(g["f"], g["m"]) if m != "Eisen" for i in f})]
    assert 8.506 - 0.10 < min(v[1] for v in wl) and max(v[1] for v in wl) <= 8.506 + 1e-6 and max(v[0] for v in wl) <= 2.358 + 1e-6


def test_desk_cherry_top_on_the_crank_frame():
    """Issue #10: a 190 x 100 solid cherry top (4 cm) on the cast-iron crank frame of
    input/2026-11-12 input/schreibtischgestell.jpg: the static frame (legs, foot tube, gearboxes,
    drive rods) is furniture in Desk_Moebel, inside the top's footprint and below it; the lifted
    parts (top, top bars, spindles) are Desk_Schreibtisch; the hand wheel Desk_Handrad turns about
    its hub (PIVOT) along x. The top and everything on it lift 30 cm (75 -> 105) in the viewer."""
    import desk
    bp = house_core.build_desk()
    house_core.build()
    assert (desk.DESK_W, desk.DESK_D, desk.DESK_H) == (1.90, 1.00, 0.75)
    W, D = desk.DESK_W, desk.DESK_D
    t = bp.geo[("Desk", "Desk_Schreibtisch")]
    wood = [t["v"][i] for f, m in zip(t["f"], t["m"]) if m == "Kirschbaum" for i in f]
    box = lambda vs: [round(min(p[k] for p in vs), 3) for k in range(3)] + [round(max(p[k] for p in vs), 3) for k in range(3)]
    assert box(wood) == [0, 0, 0.71, W, D, 0.75]
    assert bp.mat_def["Kirschbaum"]["wood"][2] == "x"                       # grain along the top
    assert set(t["m"]) == {"Kirschbaum", "Eisen"}                          # + top bars, spindles
    iron = [t["v"][i] for f, m in zip(t["f"], t["m"]) if m == "Eisen" for i in f]
    assert max(p[2] for p in iron) <= 0.71 + 1e-9
    assert min(p[2] for p in iron) + desk.LIFT_DZ < desk.GEAR_TOP          # spindles stay in their housings
    fr = bp.geo[("Desk", "Desk_Moebel")]
    assert set(fr["m"]) == {"Eisen"}
    lo, hi = box(fr["v"])[:3], box(fr["v"])[3:]
    assert lo[0] > 0 and lo[1] > 0 and lo[2] == 0 and hi[0] < W and hi[1] < D and hi[2] < 0.70
    assert bp.lift == {o: desk.LIFT_DZ for o in ("Desk_Schreibtisch", "Desk_Geraete", "Desk_Bildschirm_L", "Desk_Bildschirm_R")}
    assert desk.LIFT_DZ == 0.30
    assert bp.crank == {"Desk_Handrad": ((1, 0, 0), 4 * 360)}
    wh, (px, py, pz) = bp.geo[("Desk", "Desk_Handrad")]["v"], bp.pivot["Desk_Handrad"]
    assert px >= hi[0] - 1e-9 and max(p[0] for p in wh) < W               # on the leg's outer face, under the top
    assert 0.12 < max(math.hypot(p[1] - py, p[2] - pz) for p in wh) < 0.14  # wheel about 26 cm
    texts = [t for _, _, t in bp.dims]
    assert "Tisch 190" in texts and "100" in texts and "75–105" in texts


def test_desk_lifted_clears_the_room():
    """In the house the lifted desk (top, bars, spindles, devices, screens) at both heights and in
    between overlaps no Part of any other object; only the spindles run inside the frame's housings
    and legs (by design), never outside their footprint."""
    import desk
    moving = {"EG_Schreibtisch", "EG_Geraete", "EG_Bildschirm_L", "EG_Bildschirm_R"}
    assert moving == set(BP.lift)

    def boxes(key):
        g = BP.geo[key]
        for first, n in BP.parts[key]:
            vs = [g["v"][i] for f in g["f"][first:first + n] for i in f]
            yield [min(p[k] for p in vs) for k in range(3)], [max(p[k] for p in vs) for k in range(3)]

    swept = [(lo, hi[:2] + [hi[2] + desk.LIFT_DZ]) for o in moving for lo, hi in boxes(("EG", o))]
    assert len(swept) > 10
    spindle = lambda lo, hi: hi[0] - lo[0] < 0.031 and hi[1] - lo[1] < 0.031 and hi[2] - desk.LIFT_DZ < 0.71
    inside = lambda lo, hi, a, b: all(a[k] <= lo[k] and hi[k] <= b[k] for k in range(2))   # in plan
    hits = [(key, a, b) for key in BP.geo if key[1] not in moving for a, b in boxes(key)
            for lo, hi in swept if all(a[k] < hi[k] - 1e-6 and b[k] > lo[k] + 1e-6 for k in range(3))
            and not (key[1] == "EG_Moebel" and spindle(lo, hi) and inside(lo, hi, a, b))]
    assert hits == []


def test_desk_keeps_the_global_random_stream():
    """desk_neu() draws exactly the five global random values the old table drew, so every part
    built after it keeps its rnd (its own parts use their own generators)."""
    import random, desk
    random.seed(1)
    desk.desk_neu("T")
    after = random.getstate()
    random.seed(1)
    for _ in range(5):
        random.random()
    five = random.getstate()
    house_core.build()
    assert after == five


def test_jugend_tuer_und_stockbett():
    """Issue #6: the Jugend door no longer opens onto the stairwell: seen from the stairwell it moves
    left (west), its opening 10 cm from the room's west wall (6.21) and clear of the stair hole; the
    west bunk bed moves to the middle of the west wall, clear of the leaf (open 90 deg along that wall)."""
    zo = house_core.Z_OG
    door = [d for d in BP.doors if d["c"] == "OG" and 8.5 < d["hinge"][1] < 8.9 and 6.21 < d["hinge"][0] < 9.08]
    assert len(door) == 1
    lin = 0.025                                                    # the hinge sits on the lining
    a = door[0]["hinge"][0] - lin
    assert abs(a - (6.21 + 0.10)) < 0.005
    assert a + door[0]["w"] + 2 * lin < house_core.STAIR_HOLE[0]       # clear of the stair hole
    bunks = [(lo, hi) for m, lo, hi in _parts(BP, ("OG", "OG_Moebel")) if m.startswith("Fichte")
             and 6.21 <= lo[0] and hi[0] <= 9.08 and 8.86 <= lo[1] and hi[1] <= 12.485 and lo[2] >= zo]
    west = [(lo, hi) for lo, hi in bunks if hi[0] < 7.4]
    assert west
    y0, y1 = min(lo[1] for lo, hi in west), max(hi[1] for lo, hi in west)
    assert abs((y0 + y1) / 2 - (8.86 + 12.485) / 2) < 0.15            # middle of the west wall
    _clear([("Fichte", lo, hi) for lo, hi in bunks], _leaf_boxes(BP, "OG", zo), "door leaf")


def test_one_eg_layout():
    """Issue #34: the EG layout Alternativ (#5) is the only one; the default layout's own objects and
    the layout switch (VARIANT, default_layout(), the wall lights' layout tags) are gone."""
    names = {o for c, o in BP.geo}
    assert not names & {"EG_Speis_C", "EG_Speis_Schiebetuer", "EG_Speis_Waende", "EG_Wandlampen_Essen"}
    assert not [o for o in names if o.startswith("EG_Alt")]
    assert "EG_Speis_Rueckwand" in names
    assert not names & {"EG_Essen_Schrank", "EG_Geschirr", "EG_Pendeltuer_S", "EG_Pendeltuer_N"}   # #61
    assert not hasattr(house_core, "VARIANT") and not hasattr(house_core, "default_layout")
    assert not hasattr(BP, "variant") and not hasattr(BP, "wall_variant")


def test_speis_essen():
    """Issue #5, #61: B's closed back towards the Essen and the drywall in front of it; on the Essen's west wall, on the
    middle of the wall (south wall .. drywall), a big wooden Bauernschrank (2.10 wide, 2.25 high, 60 deep: the OG Flur's, turned to face east,
    in place of the painted cabinet C and its dishes); in the opening Küche -> Speis a panel door, hinged south, open
    flat against the Küche face of the wall (the saloon leaves are gone)."""
    others = [p for o in ("EG_Waende", "EG_Fenster_Tueren", "EG_Stuehle", "EG_Tisch", "EG_Speis", "EG_Vorrat",
                          "EG_Speis_Rueckwand", "EG_Wandlampen") for p in _parts(BP, ("EG", o))]
    boxes = lambda ps: [(lo, hi) for m, lo, hi in ps]
    ym, xw, w, h = house_core.BAUERNSCHRANK_EG
    cab = [(m, lo, hi) for m, lo, hi in _parts(BP, ("EG", "EG_Moebel")) if 2.7 < lo[0] and hi[0] < 3.5 and lo[1] < 2.8]
    lo = [min(p[1][k] for p in cab) for k in range(3)]; hi = [max(p[2][k] for p in cab) for k in range(3)]
    assert (w, h) == (2.10, 2.25) and abs(ym - (0.415 + house_core.TROCKENWAND[2]) / 2) < 1e-6   # mid-wall
    assert abs(lo[0] - 2.774) < 1e-6 and 3.37 < hi[0] < 3.43 and abs(hi[2] - 2.25) < 1e-6
    assert abs((lo[1] + hi[1]) / 2 - ym) < 1e-6 and 2.10 < hi[1] - lo[1] < 2.20
    assert {m for m, a, b in cab} == {"Innentuer", "StufeY", "Eisen"}                    # wood, iron fittings
    _clear(cab, boxes(others), "Bauernschrank")
    back = list(_parts(BP, ("EG", "EG_Speis_Rueckwand")))
    assert back and all(3.70 < a[1] and b[1] < 3.732 for m, a, b in back)
    assert min(a[0] for m, a, b in back) < 2.78 and max(b[0] for m, a, b in back) > 5.23
    door, = [d for d in BP.doors if d["c"] == "EG" and 5.2 < d["hinge"][0] < 5.6 and 4.3 < d["hinge"][1] < 4.4]
    (lx0, ly0), (lx1, ly1) = door["leaf"]
    assert 5.49 < lx0 and lx1 < 5.65 and ly1 <= 4.33 + 1e-6 and ly0 < 3.6                # flat on the Küche face
    assert 0.8 < door["w"] < 0.92
    assert not [o for o in BP.swing if "Pendeltuer" in o]
    besen = [(lo, hi) for m, lo, hi in _parts(BP, ("EG", "EG_Kueche")) if lo[0] < 6.01 and lo[1] > 5.2]
    _clear([("leaf", [lx0, ly0, 0.0], [lx1, ly1, 2.0])], besen + boxes(others), "Speistür")


def test_bichlach_door_by_the_stair_double_bed_sofa_flur_desk():
    """Request 2026-11-25: the Bichlach door (Flur wall y 8.57 .. 8.86) moves towards the stair, its opening
    15 cm east of the stair hole (x 11.40 .. 12.28, was 12.30 .. 13.18), hinged west, opened 90 deg into the
    room; the bed, which stood with its head at that wall in the way, turns (decision 2026-11-25): head on
    the west wall (x 9.25). Follow-up: one double bed (two mattresses side by side) instead of the two single
    beds, a nightstand either side, clear of the leaf and 90 cm before the north balcony door; the small desk
    of #44 belongs in the Flur: on the freed wall piece between door and east wall, its Flur face (y 8.57),
    centred there, top 110 x 55 at 0.78, the chair to the south; in its place in the room a two-seater sofa
    against the wall, facing north. All furniture (OG_Moebel)."""
    zo = house_core.Z_OG
    hole = house_core.STAIR_HOLE
    wall = [p for p in part_list(("OG", "OG_Waende")) if abs(p[1][1] - 8.57) < 1e-6 and abs(p[2][1] - 8.86) < 1e-6
            and p[1][2] < zo + 0.1 and p[2][2] > zo + 1.5]
    gaps = sorted((a[2][0], b[1][0]) for a in wall for b in wall if 0.5 < b[1][0] - a[2][0] < 1.2 and b[1][0] > 11.0)
    assert gaps and gaps[0] == (pytest.approx(hole[1] + 0.15), pytest.approx(12.28))
    leaf = [l for l in _leaf_boxes(BP, "OG", zo) if l[0][1] > 8.86 - 1e-6 and 11.3 < l[0][0] < 12.4]
    assert len(leaf) == 1 and leaf[0][1][1] - leaf[0][0][1] > 0.7                       # 90 deg into the room
    mob = [(m, lo, hi) for m, lo, hi, _ in part_list(("OG", "OG_Moebel")) if 9.25 <= lo[0] and hi[0] <= 14.575
           and 8.86 <= lo[1] and hi[1] <= 12.485 and lo[2] < zo + 2.5 and lo[2] > zo - 0.1]
    bed = [(m, lo, hi) for m, lo, hi in mob if lo[0] < 11.4 and hi[1] < 12.1]
    mats = sorted((lo, hi) for m, lo, hi in bed if m == "Leinen")
    assert len(mats) == 2 and all(hi[0] - lo[0] > 1.8 and 0.85 < hi[1] - lo[1] < 1.0 for lo, hi in mats)   # east-west
    (a0, a1), (b0, b1) = mats
    assert 0 < b0[1] - a1[1] <= 0.02 and a0[0] == b0[0] and a1[0] == b1[0]              # side by side: one bed
    frame = [(lo, hi) for m, lo, hi in bed if m == "FichteX" and hi[1] - lo[1] > 1.8 and hi[2] - lo[2] < 0.3]
    assert len(frame) == 1 and 1.75 <= frame[0][1][1] - frame[0][0][1] <= 1.90           # a double bed
    heads = [(lo, hi) for m, lo, hi in mob if lo[0] < 9.27 and hi[2] > zo + 0.85]
    assert len(heads) == 1                                                              # headboard on the west wall
    stands = [(lo, hi) for m, lo, hi in bed if m == "FichteX" and abs(hi[2] - (zo + 0.50)) < 1e-6]
    assert len(stands) == 2 and stands[0][1][1] < frame[0][0][1] < frame[0][1][1] < stands[1][0][1]   # either side
    assert max(hi[0] for _, lo, hi in bed) < hole[1] + 0.15                             # clear of the door
    _clear(mob, _leaf_boxes(BP, "OG", zo), "door leaf")
    assert max(hi[1] for _, lo, hi in mob if lo[0] < 10.95 and hi[0] > 10.03) < 12.485 - 0.9   # 90 cm before the balcony door
    xm = (12.35 + 14.575) / 2
    sofa = [(m, lo, hi) for m, lo, hi in mob if lo[0] > 12.3 and hi[1] < 10.0]
    assert sofa and {m for m, _, _ in sofa} == {"Leinen"}
    lo = [min(p[1][k] for p in sofa) for k in range(3)]; hi = [max(p[2][k] for p in sofa) for k in range(3)]
    assert 1.5 <= hi[0] - lo[0] <= 1.7 and (lo[0] + hi[0]) / 2 == pytest.approx(xm)      # two seats, centred
    assert 8.86 < lo[1] < 8.88 and 0.95 < hi[1] - lo[1] < 1.0 and hi[2] - zo < 1.0       # back to the wall
    backs = [(a, b) for m, a, b in sofa if abs(b[2] - zo - 0.87) < 1e-6]                # two back cushions, at the
    assert len(backs) == 2 and all(b[1] < 9.4 for a, b in backs)                        # wall: it faces north
    assert not [p for p in part_list(("OG", "OG_Moebel")) if p[1][0] > 12.3 and 8.86 < p[2][1] < 9.9
                and p[1][2] > zo - 0.1 and p[0].startswith("Kiefer")]                   # no desk in the room
    _clear(sofa, [(a, b) for m, a, b in mob if not (a[0] > 12.3 and b[1] < 10.0)], "Bichlach furniture")
    flur = [(m, lo, hi) for m, lo, hi, _ in part_list(("OG", "OG_Moebel")) if 12.3 < lo[0] and hi[0] <= 14.575
            and 6.4 < lo[1] and hi[1] <= 8.57 and zo - 0.1 < lo[2] < zo + 2.5]
    tops = [(lo, hi) for m, lo, hi in flur if m == "KieferX" and abs(hi[2] - (zo + 0.78)) < 1e-6]
    assert len(tops) == 1
    lo, hi = tops[0]
    assert hi[0] - lo[0] == pytest.approx(1.10) and hi[1] - lo[1] == pytest.approx(0.55)
    assert hi[1] == pytest.approx(8.565) and (lo[0] + hi[0]) / 2 == pytest.approx(xm)
    assert min(a[1] for _, a, b in flur) < lo[1] - 0.1 and max(b[2] for _, a, b in flur) < zo + 0.9   # the chair south
    assert min(a[1] for _, a, b in flur) > 7.50 + 0.2                                   # clear of the balcony door's leaves


def test_bath_submodels_dimension_room_width_and_depth():
    """Request 2026-11-25: every sub-model with a bath, toilet or shower (Bad Großeltern, Gäste-WC, Gästebad,
    Bad Nadine & Till) has a dimension line of the room's width (west-east, "Raumbreite") and depth
    (south-north, "Raumtiefe"), from wall face to wall face; the Gäste-WC's room is the Duschbad (#61)."""
    import bad, gaeste_wc as g, gaestebad as gb, elternbad as e
    rooms = {"build_bad": (bad.W, bad.D, 1),
             "build_gaeste_wc": (g.WO - g.WI, g.YN - g.YS, 0),
             "build_gaestebad": (gb.WO - gb.WI, gb.YN - gb.YS, 0),
             "build_elternbad": (e.WO - e.WI, e.YN - e.YS, 0)}
    try:
        for b, (w, d, nd) in rooms.items():
            dims = {t.split()[0]: (p, q, t) for p, q, t in getattr(house_core, b)().dims if t.startswith("Raum")}
            assert set(dims) == {"Raumbreite", "Raumtiefe"}, b
            for k, (n, ax) in {"Raumbreite": (w, 0), "Raumtiefe": (d, 1)}.items():
                p, q, t = dims[k]
                assert t == f"{k} {round(n * 100, nd):g}", (b, t)
                assert min(p[ax], q[ax]) == pytest.approx(0, abs=1e-6) and abs(q[ax] - p[ax]) == pytest.approx(n), (b, k)
                assert p[1 - ax] == pytest.approx(q[1 - ax]) and p[2] == q[2] and 0 <= p[2] <= 2.40, (b, k)
    finally:
        house_core.build()                                                    # restore the registries


def test_kleiner_schreibtisch_schlafzimmer():
    """Issue #44 (input/2026-11-15 input/kleiner-schreibtisch.webp): in the Schlafzimmer Nadine & Till a small
    country desk (top 110 x 55 at 0.78, four turned legs, one drawer with a knob on the sitter's side) stands
    behind the low wall at the bed's head end (x 11.48 .. 11.63, y 0.98 .. 3.98, 1.20 high), its back to it;
    on its far side a small matching ladder-back chair, pushed in. One furniture object OG_Schreibplatz,
    in nothing else, 60 cm walkways to the Kamin and the south wall."""
    zo = house_core.Z_OG
    assert "OG_Schreibplatz" in house_core.FURNITURE and "OG_Schreibplatz" in BP.furniture
    parts = list(part_list(("OG", "OG_Schreibplatz")))
    tops = [p for p in parts if abs(p[2][2] - (zo + 0.78)) < 1e-6]
    assert len(tops) == 1
    _, tlo, thi, _ = tops[0]
    assert abs(thi[0] - tlo[0] - 0.55) < 1e-6 and abs(thi[1] - tlo[1] - 1.10) < 1e-6   # 55 deep, 110 long
    assert 11.47 <= thi[0] < 11.48 and 0.98 < tlo[1] and thi[1] < 3.98                 # behind the low wall
    legs = [p for p in parts if abs(p[1][2] - (zo + 0.012)) < 1e-6 and p[1][0] > tlo[0] and p[2][2] > zo + 0.6]
    assert len(legs) == 4 and all(p[2][0] - p[1][0] < 0.065 for p in legs)              # four slim turned legs
    knobs = [p for p in parts if p[2][0] < tlo[0] + 0.05 and p[1][0] > tlo[0] - 0.05 and zo + 0.62 < p[1][2] < zo + 0.75
             and p[2][1] - p[1][1] < 0.05]
    assert knobs and all(p[1][0] < tlo[0] + 0.04 for p in knobs)                        # drawer knob: sitter's side (west)
    chair = [p for p in parts if p[2][2] < zo + 0.95 and p[1][0] < tlo[0] - 0.01                 # seat, back legs, slats
             or p[2][2] < zo + 0.45 and p[1][0] > tlo[0] and abs((p[1][1] + p[2][1]) / 2 - (tlo[1] + thi[1]) / 2) < 0.2]
    assert len(chair) == 10                          # + front legs, side and front stretchers
    clo = [min(p[1][k] for p in chair) for k in range(3)]; chi = [max(p[2][k] for p in chair) for k in range(3)]
    assert 0.85 < chi[2] - zo < 0.95 and chi[1] - clo[1] < 0.45 and chi[0] - clo[0] < 0.45   # small, high back
    assert tlo[0] < chi[0] < thi[0] and tlo[1] < clo[1] and chi[1] < thi[1]             # pushed in, under the top
    seat = [p for p in chair if abs(p[2][2] - (zo + 0.455)) < 1e-6]
    assert len(seat) == 1
    lo = [min(p[1][k] for p in parts) for k in range(3)]; hi = [max(p[2][k] for p in parts) for k in range(3)]
    others = [(a, b) for (c, o) in BP.geo if c == "OG" and o != "OG_Schreibplatz" and not o.endswith("_Boden")
              for _, a, b, _ in part_list((c, o)) if a[2] < zo + 1.0 and b[2] > zo + 0.02]
    _clear([(m, a, b) for m, a, b, _ in parts], others, "OG part")                       # walls, bed, Kamin ...
    _clear([(m, a, b) for m, a, b, _ in parts], _leaf_boxes(BP, "OG", zo), "door leaf")
    ofen = [(a, b) for (c, o) in BP.geo if o == "OG_Werkstattofen" for _, a, b, _ in part_list((c, o))]
    olo = [min(a[k] for a, _ in ofen) for k in range(2)]; ohi = [max(b[k] for _, b in ofen) for k in range(2)]
    assert math.hypot(*[max(olo[k] - hi[k], lo[k] - ohi[k], 0) for k in range(2)]) >= 0.60   # walkway to the Kamin
    assert lo[1] - 0.40 >= 0.60                                                         # and along the south wall


def test_speis_trockenwand():
    """Issue #61: a drywall 7.4 cm thick on the Essen side of shelf B's board back (1 mm off it), from the Essen's
    west wall (cabinet C gone) to the Küche wall's end, closing the corner at that wall (x 5.24 .. 5.49, from y 3.73); full
    height, plastered (EG_Waende: a wall on the plan sheets). Speis, B's back and C stay as they were; the Essen's two
    Wandlampen hang on its face (test_wandlampen_eg_placements)."""
    xa, xb, ya, yb = house_core.TROCKENWAND
    assert (xa, xb, ya, yb) == (2.772, 5.49, 3.64, 3.714)
    walls = [(lo, hi) for m, lo, hi in _parts(BP, ("EG", "EG_Waende")) if m == "Putz"
             and abs(lo[0] - xa) < 1e-6 and abs(lo[1] - ya) < 1e-6]
    walls += [(lo, hi) for m, lo, hi in _parts(BP, ("EG", "EG_Waende")) if abs(lo[0] - 5.24) < 1e-6 and abs(lo[1] - ya) < 1e-6]
    assert walls == [([xa, ya, 0.0], [5.24, yb, house_core.Z_EG_TOP]), ([5.24, ya, 0.0], [xb, 3.73, house_core.Z_EG_TOP])]
    back = [lo[1] for m, lo, hi in _parts(BP, ("EG", "EG_Speis_Rueckwand"))]
    assert min(back) == 3.715 and yb < 3.715


def test_flur_garderobe():
    """Issue #61 (G1, the user 2026-11-27): the Garderobe moved from the back hall into the big Flur, on its south
    wall (the Speis's back) far west, x 2.80 .. 4.80: an old-spruce hook board 2 m long (1.35 .. 2.00) with many
    iron hooks in two staggered rows (150 / 165), a hat shelf 28 deep at 1.95 on brackets above (EG_Garderobe, a
    built-in); six coats in five fabrics hang from the upper hooks in front of the board (EG_Kleidung, furniture),
    their hems above 0.5; the two Flur Wandlampen there sit over the shelf (rosettes at 2.20); under it a wooden bench
    after the user's photo. Nothing clashes with
    walls, lamps, doors and their leaves."""
    import garderobe as gd
    cm = lambda a, b: round(abs(b - a) * 100)
    assert (gd.GA, gd.GB, gd.YW) == (2.80, 4.80, 6.349)
    assert "EG_Garderobe" not in house_core.FURNITURE and "EG_Kleidung" in house_core.FURNITURE
    gar = list(_parts(BP, ("EG", "EG_Garderobe")))
    assert all(gd.GA - 1e-6 <= lo[0] and hi[0] <= gd.GB + 1e-6 and gd.YW - 1e-6 <= lo[1] and hi[1] <= gd.YW + 0.30
               for m, lo, hi in gar)
    board = [(lo, hi) for m, lo, hi in gar if m == "FichteZ" and hi[0] - lo[0] > 1.9]
    assert len(board) == 1 and abs(board[0][0][1] - gd.YW) < 1e-6 and cm(board[0][0][2], board[0][1][2]) == 65
    arms = [(lo, hi) for m, lo, hi in gar if m == "Eisen" and abs(hi[1] - lo[1] - 0.10) < 1e-6]
    rows = {}
    for lo, hi in arms:
        rows.setdefault(round(lo[2] + 0.005, 2), []).append(round((lo[0] + hi[0]) / 2, 4))
    assert sorted(rows) == [1.50, 1.65] and (len(rows[1.65]), len(rows[1.50])) == (20, 19)
    assert all(min(abs(x - u) for u in rows[1.65]) > 0.03 for x in rows[1.50])               # staggered
    shelf = [(lo, hi) for m, lo, hi in gar if abs(lo[2] - 1.95) < 1e-6 and hi[0] - lo[0] > 1.9]
    assert len(shelf) == 1 and cm(shelf[0][0][1], shelf[0][1][1]) == 28
    kl = [(m, lo, hi) for m, lo, hi in _parts(BP, ("EG", "EG_Kleidung")) if lo[1] < 7.0 and lo[0] > 2.6]
    fabrics = {"Loden", "Kamel", "Anthrazit", "Jeans", "Wolle"}
    bodies = [(m, lo, hi) for m, lo, hi in kl if m in fabrics and hi[2] - lo[2] > 0.6]
    assert len(bodies) == 6 and {m for m, lo, hi in bodies} == fabrics
    assert all(gd.GA <= lo[0] and hi[0] <= gd.GB and lo[2] > 0.5 and hi[2] <= 1.70 for m, lo, hi in bodies)
    xs = sorted([lo[0], hi[0]] for m, lo, hi in bodies)
    assert all(a[1] < b[0] for a, b in zip(xs, xs[1:]))                                     # side by side
    L = [r for r in _rosettes(BP, ("EG", "EG_Wandlampen")) if abs(r[0][1] - gd.YW) < 1e-6 and r[0][0] < 6.0]
    assert len(L) == 2 and all(abs(z - 2.2) < 0.0015 for xy, z, f in L)
    assert all(any(abs(x - w) < 0.0015 for (x, y), z, f in L) for w in (3.7813, 4.9057))
    others = [("EG", "EG_" + n) for n in ("Waende", "Wandlampen", "Fenster_Tueren", "Innentueren")]
    boxes = [(lo, hi) for k in others for m, lo, hi in _parts(BP, k)]
    _clear(gar + kl, boxes + _leaf_boxes(BP, "EG", 0.0), "Garderobe")
    _clear(kl, [(lo, hi) for m, lo, hi in gar if m != "Eisen"], "Mäntel")
    # the bench under it (#61, after the user's photo): a dark old plank on green battens and four splayed green legs,
    # seat at 0.45, under the board, the coats' hems above it; furniture
    bank = list(_parts(BP, ("EG", "EG_Garderobenbank")))
    assert "EG_Garderobenbank" in house_core.FURNITURE and {m for m, lo, hi in bank} == {"HolzX", "Gruen"}
    blo = [min(lo[k] for m, lo, hi in bank) for k in range(3)]; bhi = [max(hi[k] for m, lo, hi in bank) for k in range(3)]
    assert gd.GA < blo[0] and bhi[0] < gd.GB and gd.YW < blo[1] and bhi[1] < gd.YW + 0.32 and abs(bhi[2] - 0.45) < 1e-6
    assert len([1 for m, lo, hi in bank if m == "Gruen" and hi[2] - lo[2] > 0.3]) == 4                 # four legs
    assert min(lo[2] for m, lo, hi in bodies) > 0.45 + 0.05
    _clear(bank, boxes + [(lo, hi) for m, lo, hi in gar + kl], "Bank")


def test_umbau_61_keeps_the_rnd_of_untouched_parts():
    """Issue #61 rebuilt rooms (Küche hood, Bad niche, Duschbad, Waschküche shower and cupboard, the EG floor's rooms);
    each rebuilt builder burns the old draw count (house_core.restream), so parts built later keep the rnd they had
    before (values from main at ad293e6): the rafters, the garden's gravel, the OG floor."""
    r = lambda c, o: BP.geo[(c, o)]["r"][0]
    assert r("Dach", "Dach_Sparren") == pytest.approx(0.846392514163397, abs=1e-12)
    assert r("Umgebung", "Kiesel") == pytest.approx(0.06888543133916303, abs=1e-12)
    assert r("OG", "OG_Bodenbelag") == pytest.approx(0.8321332667309882, abs=1e-12)
    assert house_core.EG_FLOOR_DRAWS == 1575


def test_og_bauernschraenke_in_place_of_the_wardrobes():
    """Issue #61: in Saschi's room (west wall), in the Schlafzimmer Nadine & Till (north wall) and in the Bichlach (east
    wall, north of the balcony door, 1.40 wide) a freestanding wooden Bauernschrank, like the OG Flur's, in place of the
    built-in wardrobes; each against its wall, under the 2.20 ceiling, clear of walls, windows, doors and their leaves."""
    zo = house_core.Z_OG
    walls = [(lo, hi) for o in ("OG_Waende", "OG_Fenster_Tueren", "OG_Innentueren", "OG_Wandlampen")
             for m, lo, hi in _parts(BP, ("OG", o))] + _leaf_boxes(BP, "OG", zo)
    for name, (x0, x1, y0, y1), width, wall in (("Saschi", (2.70, 3.40, 3.4, 6.1), 1.80, ("x", 2.712)),
                                                 ("Schlafzimmer", (11.7, 14.4, 5.3, 6.07), 1.80, ("y", 6.058)),
                                                 ("Bichlach", (13.9, 14.58, 10.9, 12.48), 1.40, ("x", 14.573))):
        sch = [(m, lo, hi) for m, lo, hi in _parts(BP, ("OG", "OG_Moebel"))
               if x0 <= lo[0] and hi[0] <= x1 and y0 <= lo[1] and hi[1] <= y1 and lo[2] > zo - 0.1]
        assert {m for m, lo, hi in sch} == {"Innentuer", "Stufe" if wall[0] == "y" else "StufeY", "Eisen"}, name
        lo = [min(p[1][k] for p in sch) for k in range(3)]; hi = [max(p[2][k] for p in sch) for k in range(3)]
        along = 0 if wall[0] == "y" else 1
        assert width <= hi[along] - lo[along] <= width + 0.10, name                  # its width + cornice
        k = 1 - along
        assert min(abs(lo[k] - wall[1]), abs(hi[k] - wall[1])) < 1e-6 and 0.60 <= hi[k] - lo[k] <= 0.65, name
        assert 2.0 <= hi[2] - zo <= 2.10, name
        _clear(sch, walls, name)
    assert not [p for p in part_list(("OG", "OG_Moebel")) if p[0] == "FichteZ" and 2.70 < p[1][0] and p[2][0] < 3.40
                and 3.4 < p[1][1] and p[2][1] < 6.1]                                    # the built-in wardrobe gone
