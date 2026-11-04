"""house_core: the pure-Python description of the house (no bpy)."""
import json, math, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "code"))
import house_core, ofen  # noqa: E402

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
    assert house_core.PAINT == {"Putz": ral9010, "Rahmen": ral9010, "Laden": ral5014}
    assert len(house_core.ROOM_LIGHTS) == 23
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
    """input/ofen: corner stove 1.20 x 1.20 x 1.15 m with the free corner cut 0.70/0.70 (fire
    door over the whole diagonal), bed above it 1.90 along one wall (sketch: 2.00, shortened for the
    Stube door), 1.20 deep at the stove, 0.70 deep beyond it (along +y), underside at 1.45 m; long
    bench 1.60 (sketch: 2.00, shortened for the passage to the Essen). Corner of the room at the origin, walls along +x and +y."""
    bp = house_core.build_ofen()
    assert {c for c, _ in bp.geo} == {"Ofen"}

    def bbox(name):
        v = bp.geo[("Ofen", name)]["v"]
        return [round(min(p[k] for p in v), 3) for k in range(3)], [round(max(p[k] for p in v), 3) for k in range(3)]

    assert bbox("Ofen_Koerper") == ([0, 0, 0], [1.2, 1.2, 1.15])
    v = bp.geo[("Ofen", "Ofen_Koerper")]["v"]
    assert all(x + y <= 1.9 + 1e-9 for x, y, _ in v)                    # the chamfer
    r, H = ofen.OFEN_ASSUMED["r"], ofen.OFEN_H                           # top edge rounded like the
    top = [(x, y) for x, y, z in v if z > H - 1e-9]                       # vertical kinks: the top face
    assert top and all(x <= 1.2 - r + 0.003 and y <= 1.2 - r + 0.003 and x + y <= 1.9 - r * 2 ** 0.5 + 0.004
                       for x, y in top)                                   # is inset by r from the free faces
    assert min(x for x, y in top) == 0 and min(y for x, y in top) == 0    # but reaches the walls
    assert all(z <= H - r + 1e-9 for x, y, z in v if x > 1.2 - 1e-9)      # free faces end where the round starts
    lo, hi = bbox("Ofen_Feuertuer")
    assert 1.85 < lo[0] + hi[1] and lo[1] + hi[0] < 2.0                   # on the diagonal face
    door = bp.geo[("Ofen", "Ofen_Feuertuer")]["v"]
    along = [(x - y) / 2 ** 0.5 for x, y, _ in door]
    assert round(max(along) - min(along), 3) == 0.65 and round(max(along) + min(along), 3) == 0  # centred
    assert hi[2] == 1.05                                                  # 10 cm below the top
    bank = bp.geo[("Ofen", "Ofen_Bank")]["v"]
    right = [p for p in bank if p[1] > 1.2]                               # right of the door
    left = [p for p in bank if p[0] > 1.2]                                # along the wall, left
    span = lambda ps, k: round(max(p[k] for p in ps) - min(p[k] for p in ps), 3)
    assert span(right, 1) == 0.6 and max(p[0] for p in right) <= 0.7
    assert span(left, 0) == 1.6 and span(left, 1) == 0.6 and max(p[1] for p in left) <= 0.7
    assert len(left) + len(right) == len(bank)
    g, seat = bp.geo[("Ofen", "Ofen_Bank")], ofen.OFEN_ASSUMED["seat"]   # plain legs like
    parts = []                                                            # bank-schlicht.png: per bench
    for first, n in bp.parts[("Ofen", "Ofen_Bank")]:                     # four square legs and a
        ps = [g["v"][i] for f in g["f"][first:first + n] for i in f]     # stretcher across each end
        parts.append([round(max(p[k] for p in ps) - min(p[k] for p in ps), 3) for k in range(3)] + [min(p[2] for p in ps)])
    legs = [p for p in parts if p[0] == p[1] == 0.06 and p[3] == 0]
    rails = [p for p in parts if p[2] == 0.04 and 0.1 < p[3] < 0.25]
    assert len(legs) == 8 and all(abs(p[2] - (seat - 0.045)) < 1e-6 for p in legs)
    assert len(rails) == 4 and len(parts) == 2 + 8 + 4
    floor = [(x, y) for x, y, z in v if z == 0]                           # open underneath: only the
    tl = ofen.OFEN_ASSUMED["leg"]                                           # legs stand on the floor
    assert all(x >= 1.2 - tl - 1e-9 or y >= 1.2 - tl - 1e-9 or x + y >= 1.9 - tl * 2 ** 0.5 - 1e-9
               for x, y in floor)
    gaps = {(round(x, 3), round(y, 3)) for x, y in floor}                 # arches in all three faces
    assert {(1.2, 0.09), (1.2, 0.59), (0.09, 1.2), (0.59, 1.2)} <= gaps
    assert sum(1.899 < x + y < 1.901 and abs(abs(x - y) - 0.25 * 2 ** 0.5) < 1e-3 for x, y in floor) >= 2
    lo, hi = bbox("Ofen_Bett")
    assert lo[:2] == [0, 0] and hi[:2] == [1.2, 1.9]
    bed = bp.geo[("Ofen", "Ofen_Bett")]["v"]
    assert round(min(z for x, y, z in bed if y < 1.2), 3) == 1.45        # sitting height above the bench
    assert all(x <= 0.7 + 1e-9 for x, y, z in bed if y > 1.2 + 1e-9)
    g, BL = bp.geo[("Ofen", "Ofen_Bett")], ofen.OFEN_BED_L                # foot end: 3 rungs from the
    rungs = []                                                            # wall to the post (a ladder)
    for first, n in bp.parts[("Ofen", "Ofen_Bett")]:
        ps = [g["v"][i] for f in g["f"][first:first + n] for i in f]
        lo = [min(p[k] for p in ps) for k in range(3)]; hi = [max(p[k] for p in ps) for k in range(3)]
        if lo[0] < 0.02 and abs(hi[0] - 0.62) < 1e-9 and lo[1] >= BL - 0.08 - 1e-9 and hi[2] < 1.4:
            rungs.append((lo[2] + hi[2]) / 2)
    assert len(rungs) == 3 and all(abs(z - ofen.OFEN_BED * k / 4) < 1e-9 for z, k in zip(sorted(rungs), (1, 2, 3)))
    rim = bp.geo[("Ofen", "Ofen_Bettrand")]["v"]                          # rim: free edges only
    top, bottom = max(z for *_, z in rim), min(z for *_, z in rim)
    assert bottom == 1.49 and abs(top - (1.49 + 0.05)) < 1e-9             # 5 cm boards, upright
    assert max(x for x, y, z in rim if z == top) == max(x for x, y, z in rim if z == bottom) <= 1.2  # straight up
    assert len(bp.parts[("Ofen", "Ofen_Bettrand")]) == 3                  # one board per free edge
    assert min(x for x, y, z in rim) > 0.6                                # no board along the walls
    assert min(y for x, y, z in rim) >= 0.1 - 1e-9 and max(y for x, y, z in rim) <= 1.8 + 1e-9  # 10 cm at the ends
    assert not any(1.2 - 0.03 < x and 0.65 < y < 0.75 for x, y, z in rim if z == bottom)  # gap at the corner
    assert bp.dims and all(len(d) == 3 for d in bp.dims)


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

    assert bbox("EG_Ofen_Koerper") == ([9.06, 4.645, 0], [10.26, 5.845, 1.15])
    assert bbox("EG_Ofen_Bett")[1][0] <= 11.004 - 0.04                     # clear of the Stube door
    assert bbox("EG_Ofen_Bank")[0][1] >= 2.938 + 0.1                       # clear of the passage to Essen
    g = BP.geo[("EG", "EG_Ofen_Bank")]                                   # grain along the seats
    tops = {m for f, m in zip(g["f"], g["m"]) if all(abs(g["v"][i][2] - 0.45) < 1e-9 for i in f)}
    assert tops == {"FichteY"}
    assert "FichteX" in BP.geo[("EG", "EG_Ofen_Bett")]["m"]               # bed runs along x now


def test_bibliothek_piano_desk_and_werkstattofen():
    """Bibliothek (Musikraum + Büro): grand piano turned 30° to the left (counter-clockwise from
    above), desk filling the wall between the two north french doors (10.919 .. 12.867), and a
    small workshop stove (input/2026-11-03 input/werkstattofen.jpeg) on the Flur wall, east of the
    wall stub at the offener Kamin."""
    g = BP.geo[("EG", "EG_Moebel")]
    on = lambda mat: {i for f, m in zip(g["f"], g["m"]) if m == mat for i in f}
    keys = [g["v"][i] for i in on("Keramik")]                            # white keys: one long box
    top = [(x, y) for x, y, z in keys if z == max(p[2] for p in keys)]
    (ax, ay), (bx, by) = next((p, q) for p in top for q in top if 1.09 < math.dist(p, q) < 1.105)  # long edge, 1.10
    assert abs(math.degrees(math.atan2(by - ay, bx - ax)) % 180 - 30) < 0.5        # 15°, then "etwas mehr"
    desk = [(x, y) for x, y, z in g["v"] if z == 0.75 and y > 11 and 10 < x < 14.6]
    assert round(min(x for x, _ in desk), 3) == 10.919 and round(max(x for x, _ in desk), 3) == 12.867
    assert max(y for _, y in desk) <= 12.473
    ofen = BP.geo[("EG", "EG_Werkstattofen")]
    lo = [round(min(p[k] for p in ofen["v"]), 3) for k in range(3)]
    hi = [round(max(p[k] for p in ofen["v"]), 3) for k in range(3)]
    assert 9.351 + 0.05 <= lo[0] < 9.6 and lo[1] >= 8.876 + 0.05 and hi[1] < 9.6   # on the Flur wall
    assert 1.0 <= hi[2] <= 1.1 and 0.38 <= hi[0] - lo[0] <= 0.45
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


def test_outside_lights_at_the_lamp_bulbs():
    """Every gooseneck wall lamp records its filament centre (0.38 m out from the wall, 8.5 cm below the
    rosette) so the viewer can switch the lamps on at dusk; the filament glows only then."""
    assert len(BP.outside_lights) == 8
    assert (5.55, -0.38, 1.865) in [tuple(round(c, 3) for c in p) for p in BP.outside_lights]
    assert all(round(z, 3) == 1.865 for *_, z in BP.outside_lights)
    assert house_core.MAT_DEF["Gluehfaden"].get("night") is True


def test_bibliothek_bookcase_on_the_flur_wall():
    """Old-style dark wooden bookcase, floor to ceiling, on the Flur wall opposite the desk: from
    the Büro door (architrave at 13.447) to 1 m from the workshop stove (east edge 9.861), with
    books in it; the Büro door now opens against the east wall (hinge side as in the plan)."""
    key = ("EG", "EG_Moebel")
    g = BP.geo[key]
    boxes = []
    for first, n in BP.parts[key]:
        vs = [g["v"][i] for f in g["f"][first:first + n] for i in f]
        boxes.append((g["m"][first], [min(p[k] for p in vs) for k in range(3)], [max(p[k] for p in vs) for k in range(3)]))
    case = [(m, lo, hi) for m, lo, hi in boxes if lo[1] < 9.4 and hi[1] > 8.87 and lo[0] > 9.9 and hi[0] < 13.5]
    xs = [lo[0] for _, lo, _ in case] + [hi[0] for _, _, hi in case]
    assert abs(min(xs) - 10.861) < 0.03 and 13.40 < max(xs) <= 13.447
    assert max(hi[2] for _, _, hi in case) > 2.38 and min(lo[2] for _, lo, _ in case) < 0.02    # floor to ceiling
    assert max(hi[2] for _, _, hi in case) < house_core.Z_EG_TOP
    assert min(lo[1] for _, lo, _ in case) > 8.876                                            # off the wall
    assert {"NussX", "NussZ", "Buecher"} <= {m for m, _, _ in case}
    assert sum(m == "Buecher" for m, _, _ in case) >= 200
    leaf = [pts for c, pts in house_core.LEAVES if c == "EG" and abs(pts[0][0] - 14.575) < 0.05]
    assert leaf and all(x > 14.4 for x, _, _ in leaf[0])                                       # along the east wall


def test_west_og_windows_wall_below_up_to_the_ceiling():
    """The three tall west windows in the OG (Yoga, Bad): no fixed glazing below any more but
    wall (sill 0.85 m above the floor: first 0.95, then 10 cm lower), and up to the ceiling."""
    house_core.build()                                                     # OPENINGS of the house
    west = [o for o in house_core.OPENINGS if o["ax"] == "y" and o["face"] == 0 and o["sill"] >= house_core.Z_OG - 1e-9
            and o["head"] > 4.0 and o["b"] - o["a"] > 0.9]
    assert sorted(round(o["a"], 2) for o in west) == [6.77, 8.96, 11.26]
    assert all(round(o["sill"] - house_core.Z_OG, 3) == 0.85 and o["head"] == house_core.Z_OG_TOP and o["kind"] == "W"
               for o in west)
    g = BP.geo[("OG", "OG_Fenster_Tueren")]
    glass = {i for f, m in zip(g["f"], g["m"]) if m == "Glas" for i in f}
    assert not any(g["v"][i][0] < 0.31 and g["v"][i][2] < house_core.Z_OG + 0.85 for i in glass)
    clad = BP.geo[("Dach", "Verschalung_West")]                            # no iron bars (small windows only)
    bars = [clad["v"][i] for f, m in zip(clad["f"], clad["m"]) if m == "Eisen" for i in f]
    assert bars and not any(any(o["a"] < y < o["b"] for o in west) and z > house_core.Z_OG for _, y, z in bars)


def test_fires_are_recorded_where_the_stoves_burn():
    """The flames are no longer static geometry: every stove records its fire (base = centre of
    the flame bed in the flame plane, u = unit along the width, w, h, d) in FIRES, and the
    animated fire component (code/fire.py, web/src/fire.js) draws them. Three in the house (Stube
    Ofen, Bibliothek and Schlafen SE workshop stoves), one in the Ofen sub-model."""
    assert len(BP.fires) == 4 and len(house_core.build_ofen().fires) == 2   # the Ofen: front + back door
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
    assert sum(inside(f, ("OG", "OG_Werkstattofen")) for f in BP.fires) == 1
    og = next(f for f in BP.fires if f["base"][2] > house_core.Z_OG)
    assert abs(og["u"][0] - math.cos(math.radians(-135))) < 1e-9                     # turned with its stove


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


def test_small_lamp_above_the_ofen_bed():
    """Like the photo (ofenbett-1200x800.jpg): a small gooseneck lamp on the wall above the bed's
    head end, the outdoor lamp at reduced scale; not one of the outside lights."""
    sub = house_core.build_ofen()
    v = sub.geo[("Ofen", "Ofen_Lampe")]["v"]
    lo = [min(p[k] for p in v) for k in range(3)]; hi = [max(p[k] for p in v) for k in range(3)]
    assert lo[1] >= -1e-9 and lo[2] > ofen.OFEN_BED + 0.4 and hi[2] < house_core.Z_EG_TOP     # on the wall, above the bed
    assert max(h - l for h, l in zip(hi, lo)) < 0.25                                           # small
    assert "GluehfadenAn" in sub.geo[("Ofen", "Ofen_Lampe")]["m"]                           # switched on
    house_core.build()
    assert ("EG", "EG_Ofen_Lampe") in BP.geo and "EG_Ofen_Lampe" in BP.smooth
    assert len(BP.outside_lights) == 8


def test_east_og_balcony_windows_are_french_doors():
    """The three east OG windows onto the long balcony (Schlafen SE y 1.74, 4.15; Schlafen NE
    y 9.86) are balcony doors now (on request), floor to 4.60 like the other french doors."""
    house_core.build()
    east = {round(o["a"], 2): o for o in house_core.OPENINGS
            if o["ax"] == "y" and o["face"] == house_core.W_OUT and o["sill"] >= house_core.Z_OG - 1e-9}
    for a in (1.74, 4.15, 9.86):
        assert east[a]["kind"] == "FD" and east[a]["sill"] == house_core.Z_OG and east[a]["head"] == 4.60


def test_ofen_lamp_is_switched_on():
    """The small lamp above the Ofen bed is on: its filament glows by day too (not "night") and
    it records a light (LAMP_LIGHTS) at the filament, for Blender and the viewer."""
    sub = house_core.build_ofen()
    assert len(sub.lamp_lights) == 1
    house_core.build()
    assert len(BP.lamp_lights) == 1 and len(BP.outside_lights) == 8
    g = BP.geo[("EG", "EG_Ofen_Lampe")]
    fil = [g["v"][i] for f, m in zip(g["f"], g["m"]) if m == "GluehfadenAn" for i in f]
    assert fil and "night" not in house_core.MAT_DEF["GluehfadenAn"]
    x, y, z = BP.lamp_lights[0]
    assert min(p[0] for p in fil) - 0.01 <= x <= max(p[0] for p in fil) + 0.01
    assert min(p[1] for p in fil) - 0.01 <= y <= max(p[1] for p in fil) + 0.01
    assert min(p[2] for p in fil) - 0.01 <= z <= max(p[2] for p in fil) + 0.01
