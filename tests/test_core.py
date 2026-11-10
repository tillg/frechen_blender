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
    assert house_core.PAINT == {"Putz": ral9010, "Rahmen": ral9010, "Laden": ral5014, "Front": ral5014}
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
    above) and then 180° in place (keyboard and bench to the north), desk filling the wall between the two north french doors (10.919 .. 12.867), and a
    small workshop stove (input/2026-11-03 input/werkstattofen.jpeg) in the corner of the Flur wall
    and the wall stub at the offener Kamin, turned 45° to face the room."""
    g = BP.geo[("EG", "EG_Moebel")]
    on = lambda mat: {i for f, m in zip(g["f"], g["m"]) if m == mat for i in f}
    keys = [g["v"][i] for i in on("Keramik")]                            # white keys: one long box
    top = [(x, y) for x, y, z in keys if z == max(p[2] for p in keys)]
    (ax, ay), (bx, by) = next((p, q) for p in top for q in top if 1.09 < math.dist(p, q) < 1.105)  # long edge, 1.10
    assert abs(math.degrees(math.atan2(by - ay, bx - ax)) % 180 - 30) < 0.5        # 15°, then "etwas mehr"
    assert sum(y for _, y, _ in keys) / len(keys) > 11.4      # then 180° (2026-11-08): keyboard to the north
    desk = [(x, y) for x, y, z in g["v"] if z == 0.75 and y > 11 and 10 < x < 14.6]
    assert round(min(x for x, _ in desk), 3) == 10.919 and round(max(x for x, _ in desk), 3) == 12.867
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
    wall (sill 0.75 m above the floor: first 0.95, then twice 10 cm lower), and up to the ceiling."""
    house_core.build()                                                     # OPENINGS of the house
    west = [o for o in house_core.OPENINGS if o["ax"] == "y" and o["face"] == 0 and o["sill"] >= house_core.Z_OG - 1e-9
            and o["head"] > 4.0 and o["b"] - o["a"] > 0.9]
    assert sorted(round(o["a"], 2) for o in west) == [6.77, 8.96, 11.26]
    assert all(round(o["sill"] - house_core.Z_OG, 3) == 0.75 and o["head"] == house_core.Z_OG_TOP and o["kind"] == "W"
               for o in west)
    g = BP.geo[("OG", "OG_Fenster_Tueren")]
    glass = {i for f, m in zip(g["f"], g["m"]) if m == "Glas" for i in f}
    assert not any(g["v"][i][0] < 0.31 and g["v"][i][2] < house_core.Z_OG + 0.75 for i in glass)
    clad = BP.geo[("Dach", "Verschalung_West")]                            # no iron bars (small windows only)
    bars = [clad["v"][i] for f, m in zip(clad["f"], clad["m"]) if m == "Eisen" for i in f]
    assert bars and not any(any(o["a"] < y < o["b"] for o in west) and z > house_core.Z_OG for _, y, z in bars)


def test_fires_are_recorded_where_the_stoves_burn():
    """The flames are no longer static geometry: every stove records its fire (base = centre of
    the flame bed in the flame plane, u = unit along the width, w, h, d) in FIRES, and the
    animated fire component (code/fire.py, web/src/fire.js) draws them. Four in the house (Stube
    Ofen, Bibliothek and Schlafen SE workshop stoves, Küche Herd), one in the Ofen sub-model."""
    assert len(BP.fires) == 5 and len(house_core.build_ofen().fires) == 2   # the Ofen: front + back door
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
    assert sum(inside(f, ("EG", "EG_Herd")) for f in BP.fires) == 1
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


def test_og_flur_waschbecken_right_of_the_waschkueche_door():
    """OG Flur: a washbasin on the wall right of the Waschküche door (seen from the Flur: west of
    it, x < 7.15, wall face y 6.35; the plan draws a basin there) after input/2026-11-05 input/
    waschbecken-briol.jpeg: a deep ceramic sink on a dark stone panel, but one mixer tap."""
    zo = house_core.Z_OG
    parts = [p for p in part_list(("OG", "OG_Sanitaer")) if p[1][1] >= 6.35 - 1e-9 and 6.0 < p[1][0] and p[2][0] < 7.15]
    stone = [p for p in parts if p[0] == "Schiefer"]
    assert stone and "Schiefer" in house_core.MAT_DEF
    slo = [min(p[1][k] for p in stone) for k in range(3)]; shi = [max(p[2][k] for p in stone) for k in range(3)]
    assert shi[1] <= 6.38 and slo[2] <= zo + 0.02 and shi[2] >= zo + 1.5 and shi[0] <= 7.15 - 0.2
    sink = [p for p in parts if p[0] == "Keramik"]
    klo = [min(p[1][k] for p in sink) for k in range(3)]; khi = [max(p[2][k] for p in sink) for k in range(3)]
    assert abs(khi[2] - zo - 0.86) < 0.01 and khi[2] - klo[2] >= 0.25                   # deep trough
    assert 0.55 <= khi[0] - klo[0] <= 0.65 and khi[1] - 6.35 <= 0.5
    assert len(sink) >= 5                                                                # hollow, not a block
    cx = (klo[0] + khi[0]) / 2
    tap = [p for p in parts if p[0] == "Metall" and p[1][2] > khi[2]]
    assert tap and all(abs((lo[0] + hi[0]) / 2 - cx) < 0.05 for _, lo, hi, _ in tap)   # one mixer, centred


def test_waschkueche_dryer_on_the_washer_and_table_along_the_back_wall():
    """Waschküche (OG, x 5.59 .. 8.59, y 2.79 .. 6.06, door in the north wall): a dryer stands on
    the washing machine (north one at the east wall), and a table 0.80 m deep runs the full width
    of the back (south) wall, with two stacks of neatly folded clothes on it; it replaces the low
    cupboard that stood in the SE corner."""
    zo = house_core.Z_OG
    room = [p for p in part_list(("OG", "OG_Moebel")) if 5.59 <= p[1][0] and p[2][0] <= 8.59 and 2.79 <= p[1][1] and p[2][1] <= 6.06]
    enamel = sorted((p for p in room if p[0] == "Emaille"), key=lambda p: (p[1][1], p[1][2]))
    assert len(enamel) == 3                                                   # washer, washer + dryer
    washer, dryer = enamel[1:]
    assert dryer[1][:2] == washer[1][:2] and dryer[2][:2] == washer[2][:2]     # same footprint
    assert abs(dryer[1][2] - washer[2][2]) < 0.002                            # stands on it
    top = [p for p in room if p[0] == "FichteX" and p[2][2] > zo + 0.7]
    assert len(top) == 1
    _, lo, hi, _ = top[0]
    assert lo[0] - 5.59 < 0.01 and 8.59 - hi[0] < 0.01 and lo[1] - 2.79 < 0.01   # full width, on the back wall
    assert hi[1] < enamel[0][1][1]                                            # clear of the south machine
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


def test_waschkueche_open_cupboard_with_laundry_baskets_on_the_west_wall():
    """Waschküche: on the right-hand wall seen from the door (west, x 5.59) an open spruce
    cupboard, 2.0 m high, between the table on the back wall and the door leaf: two sides,
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
            and 6.0 < min(l[0][1], l[1][1]) < 6.06][0]
    assert table[2][1] < lo[1] and hi[1] < min(leaf[0][1], leaf[1][1])        # clear of table and leaf
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
    back = [p for p in glass if p[2][0] < 2.358 + 0.01 and 7.3 < p[1][1] and p[2][1] < 8.6]
    front = [p for p in glass if p[1][0] > 12.0]
    assert len(back) == 1 and len(front) == 2
    _, lo, hi, _ = back[0]
    assert hi[2] - lo[2] > 0.7 and lo[2] > 0.9                       # upper part of the leaf


KUECHE_EAST = 8.557                                                           # east wall face of the Küche


def test_kueche_wamsler_herd_at_the_north_end_of_the_east_run():
    """Küche: a wood-fired Wamsler cooker after input/2026-11-05 input/wamsler.jpeg (grey enamelled
    steel, steel top with a rail, fire door with glass top left, ash door below, oven door with a
    window on the right, full-width drawer, flue on top) stands at the north end of the east run
    (where the plan draws the flue), front facing west, flush with the run's fronts; the run and
    its granite top end south of it. Its fire burns behind the glass (FIRES)."""
    herd = list(part_list(("EG", "EG_Herd")))
    body = [p for p in herd if p[0] == "Herd"]
    lo = [min(p[1][k] for p in body) for k in range(3)]; hi = [max(p[2][k] for p in body) for k in range(3)]
    assert 0.75 <= hi[1] - lo[1] <= 0.85 and 0.55 <= hi[0] - lo[0] <= 0.62 and 0.80 <= hi[2] <= 0.92
    assert KUECHE_EAST - 0.01 < hi[0] < KUECHE_EAST and hi[1] < 5.2 and lo[1] > 4.25    # north end of the run (v6)
    assert {"Herd", "Metall", "Eisen", "Ofenglas"} <= {p[0] for p in herd}
    front = min(p[1][0] for p in herd if p[2][2] < 0.9)                       # doors, handles
    assert 7.90 < front < 7.96
    kueche = list(part_list(("EG", "EG_Kueche")))
    run = [p for p in kueche if p[2][2] <= 0.901 and p[2][0] > 7.9 and p[2][1] > 3.7 and p[1][1] < lo[1]]   # not the sink run (v6)
    assert run and max(p[2][1] for p in run) < lo[1]                          # carcass, doors, granite
    fire = [f for f in BP.fires if abs(f["base"][0] - lo[0]) < 0.03 and lo[1] < f["base"][1] < hi[1]]
    assert len(fire) == 1 and fire[0]["base"][1] > (lo[1] + hi[1]) / 2       # fire door: top left, north
    assert "EG_Herd" not in BP.furniture                                      # built in, like the Ofen


def test_kueche_old_steel_hood_above_the_herd():
    """Küche: above the Herd a steel hood of the old form: a straight skirt with a rail in front,
    a sloping canopy narrowing to a flue stack that runs up to the ceiling."""
    herd = [p for p in part_list(("EG", "EG_Herd")) if p[0] == "Herd"]
    hy0, hy1 = min(p[1][1] for p in herd), max(p[2][1] for p in herd)
    hood = list(part_list(("EG", "EG_Haube")))
    assert {p[0] for p in hood} == {"Metall"}
    lo = [min(p[1][k] for p in hood) for k in range(3)]; hi = [max(p[2][k] for p in hood) for k in range(3)]
    assert lo[1] < hy0 + 0.01 and hi[1] > hy1 - 0.01 and abs((lo[1] + hi[1]) / 2 - (hy0 + hy1) / 2) < 0.01
    assert 1.55 <= lo[2] <= 1.75 and hi[2] > house_core.Z_EG_TOP              # up into the ceiling
    assert KUECHE_EAST - 0.01 < hi[0] < KUECHE_EAST and hi[0] - lo[0] >= 0.5
    def width(vs, z):                                                         # y extent at height z
        return max(v[1] for v in vs if v[2] == z) - min(v[1] for v in vs if v[2] == z)
    taper = [p for p in hood if len(set(p[3])) == 8 and len({v[2] for v in p[3]}) == 2
             and width(p[3], p[2][2]) < width(p[3], p[1][2]) - 0.3]
    assert len(taper) == 1                                                    # narrows upwards


def test_kueche_without_wall_cabinets_and_sealed_against_the_herd():
    """Request 2026-11-10: no wall cabinets; east of the sink, where the Herd stands in front of the
    sink run, a blind cabinet (no drawers, no grips) and the granite top runs right up to the Herd;
    south of the Herd the Ostzeile's top ends at it too (2 mm joint, no overlap with its rim)."""
    k = list(part_list(("EG", "EG_Kueche")))
    assert not [p for p in k if p[1][2] > 1.3 and p[1][0] > 6.01]              # nothing on the walls (Besenschrank aside)
    herd = [p for p in part_list(("EG", "EG_Herd"))]
    hy0, hy1 = min(p[1][1] for p in herd), max(p[2][1] for p in herd)       # incl. its top's rim
    hx0 = min(p[1][0] for p in herd if p[0] == "Herd")
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
    assert {p[0] for p in k} <= {"Front", "Metall", "Granit", "Fuge", "Eisen"}
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
    # cabinet C of the Speis (doors at y 3.13 .. 3.15 towards the dining table)
    sp = list(part_list(("EG", "EG_Speis")))
    c = [p for p in sp if p[1][1] >= 3.09 and p[2][1] <= 3.728 + 1e-6]
    assert {p[0] for p in c} == {"Front", "Metall", "Fuge"}
    assert len([p for p in c if hood(p)]) == 8 and len([p for p in c if p[0] == "Metall"]) == 16
    assert all(p[1][1] < 3.13 for p in c if p[0] == "Metall")
    panels = [p for p in c if p[0] == "Front" and p[1][1] > 3.135 and p[2][1] <= 3.15 + 1e-6]
    assert len(panels) == 8                                                   # 4 tall + 4 top doors
    besen = [p for p in k if p[2][0] < 6.01 and p[1][1] > 5.2 and p[0] == "Metall"]
    assert len(besen) == 2 and len([p for p in besen if hood(p)]) == 1        # its cup pull


def test_chairs_are_board_chairs_after_stuhl_png():
    """All chairs (8 at the dining table, one at the Bibliothek desk) after input/2026-11-05
    input/stuhl.png: a thick plank seat on two battens, four splayed tapering stick legs without
    stretchers, one tall backrest board leaning back with a pointed heart cut out near its top, its
    tenon wedged under the seat."""
    parts = list(part_list(("EG", "EG_Stuehle")))
    seats = [p for p in parts if abs(p[2][2] - 0.46) < 0.005 and p[2][2] - p[1][2] >= 0.04]
    assert len(seats) == 9
    centre = lambda p: ((p[1][0] + p[2][0]) / 2, (p[1][1] + p[2][1]) / 2)
    mean = lambda vs, k: sum(v[k] for v in vs) / len(vs)
    legs = [p for p in parts if p[1][2] < 0.01]
    assert len(legs) == 4 * 9
    for _, _, hi, vs in legs:
        foot = [v for v in vs if v[2] < 0.01]; head = [v for v in vs if v[2] > hi[2] - 0.001]
        c = min((centre(s) for s in seats), key=lambda q: math.dist(q, (mean(foot, 0), mean(foot, 1))))
        assert math.dist(c, (mean(foot, 0), mean(foot, 1))) - math.dist(c, (mean(head, 0), mean(head, 1))) > 0.04   # splayed
        assert max(v[0] for v in foot) - min(v[0] for v in foot) < max(v[0] for v in head) - min(v[0] for v in head) + 0.02   # tapering
    assert not [p for p in parts if p[1][2] > 0.02 and p[2][2] < 0.35]                       # no stretchers
    board = [p for p in parts if p[2][2] > 0.85]
    assert len(board) == 4 * 9                                                # two sides, above and below the heart
    assert sum(len(set(p[3])) == 10 for p in board) == 9                      # the piece notched by the heart's point
    for _, _, hi, vs in board:
        c = min((centre(s) for s in seats), key=lambda q: math.dist(q, (vs[0][0], vs[0][1])))
        top = [v for v in vs if v[2] > hi[2] - 0.001]; low = [v for v in vs if v[2] < min(w[2] for w in vs) + 0.001]
        lean = math.dist(c, (mean(top, 0), mean(top, 1))) - math.dist(c, (mean(low, 0), mean(low, 1)))
        assert lean > 0.12 * (top[0][2] - low[0][2])                         # leans back
    assert sum(0.90 <= p[2][2] <= 1.0 for p in board) == 3 * 9                # tall: about 0.95


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
    assert {n for _, n in bp.geo} == {"Desk_Moebel", "Desk_Stuehle", "Desk_Geraete", "Desk_Bildschirm_L", "Desk_Bildschirm_R"}
    v = bp.geo[("Desk", "Desk_Moebel")]["v"]
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
    assert len(bp.dims) >= 5 and any("194.8" in t for _, _, t in bp.dims)


def test_desk_built_into_the_bibliothek():
    """The desk sub-model stands in the Bibliothek at today's place (SW corner 10.919 / 11.48),
    unrotated; its devices and screens are loose furniture ("Eingerichtet"), the screens keep their
    pivots."""
    import desk
    sub = house_core.build_desk()
    house_core.build()                                                    # restore the registries
    x0, y0 = desk.DESK_AT
    for n in ("Geraete", "Bildschirm_L", "Bildschirm_R"):
        a, b = sub.geo[("Desk", "Desk_" + n)]["v"], BP.geo[("EG", "EG_" + n)]["v"]
        assert len(a) == len(b) and all(math.dist((p[0] + x0, p[1] + y0, p[2]), q) < 1e-9 for p, q in zip(a, b))
        assert "EG_" + n in BP.furniture
    px, py, pz = sub.pivot["Desk_Bildschirm_L"]
    assert math.dist(BP.pivot["EG_Bildschirm_L"], (px + x0, py + y0, pz)) < 1e-9
    assert BP.turn["EG_Bildschirm_L"] == sub.turn["Desk_Bildschirm_L"]
    assert desk.DESK_AT == (10.919, 11.48)


def test_back_door_has_lever_handles_inside_and_outside():
    """Back door (west wall): a black lever handle outside (on the lock plate) and inside (on its
    own backplate), at the lock (south side), levers pointing towards the hinge (north)."""
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
    assert pts("OG", [(0.4, 6.6), (1.2, 7.5), (2.5, 8.5), (2.1, 5.55), (2.1, 6.4)]) == {"Kalkstein"}  # Bad NW + alcove
    assert pts("OG", [(5.65, 0.45), (7.0, 1.5), (8.55, 2.55)]) == {"Kalkstein"}                       # Bad S
    assert pts("OG", [(4.0, 7.5), (7.0, 4.0)]) == {"Eiche"}                                            # Flur, HWR
    assert pts("EG", [(0.71, 11.656)]) == {"Kalkstein"} and pts("EG", [(1.81, 10.7)]) == {"Eiche"}   # Bad Großeltern
    assert pts("EG", [(1.6, 9.3)]) == {"Eiche"}                                                        # its Schrank
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


# the four WCs: (collection, floor z, interior rectangle, door span on the north wall)
WCS = [("EG", 0.0, (0.31, 2.358, 5.475, 6.574), (1.349, 2.288)),                 # by the back hall
       ("EG", 0.0, (0.31, 1.274, 8.656, 9.856), (0.31, 1.274)),                  # WC Großeltern: niche, north open
       ("OG", house_core.Z_OG, (0.31, 1.57, 5.46, 6.44), (0.48, 1.42)),          # WC 2,26
       ("OG", house_core.Z_OG, (8.72, 9.92, 3.98, 6.06), (8.69, 9.72))]          # WC 2,30


def test_wcs_have_green_tiles_to_hip_height():
    """Request 2026-11-08 after input/2026-11-08 input/bad_mallnitz.jpeg: green subway tiles about
    1.1 m high (with a cap row) on all WC walls, cut at the door; the Bäder have none."""
    for c, z, (x0, x1, y0, y1), (da, db) in WCS:
        key, d = (c, c + "_Fliesen"), 0.008
        na, nb = max(((x0, da), (db, x1)), key=lambda s: s[1] - s[0])            # wider tiled part
        walls = [((x0 + x1) / 2, y0 + d), (x0 + d, (y0 + y1) / 2), (x1 - d, (y0 + y1) / 2)]
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
               for x, y in ((1.0, 8.562), (7.0, 0.408), (5.598, 1.5)))                 # Bad NW, Bad S


def test_wc_fixtures_after_the_photo():
    """WCs after the same photo: floor-standing toilet with a close-coupled cistern, the hand
    basins on chrome console legs, a black frame round their mirror. The Bäder keep theirs."""
    zo = house_core.Z_OG
    at = lambda wx, wy, fx, fy: lambda u, v: (wx + fx * v - fy * u, wy + fy * v + fx * u)
    for c, z, *w in [("EG", 0.0, 0.31 + 0.482, 8.656, 0, 1), ("EG", 0.0, 1.325, 5.475, 0, 1),
                     ("OG", zo, 0.31, 6.0, 1, 0), ("OG", zo, 9.26, 3.98, 0, 1)]:
        M, key = at(*w), (c, c + "_Sanitaer")
        assert _part_at(key, *M(0, 0.10), z + 0.60) == "Keramik", w            # cistern
        assert _part_at(key, *M(0, 0.40), z + 0.03) == "Keramik", w            # pedestal on the floor
    for c, z, *w in [("OG", zo, 9.92, 5.2, -1, 0)]:                         # the Bad Großeltern's WC has none
        M, key = at(*w), (c, c + "_Sanitaer")
        assert {_part_at(key, *M(s * 0.16, 0.25), z + 0.30) for s in (-1, 1)} == {"Metall"}, w   # legs
        assert {_part_at(key, *M(s * 0.27, 0.02), z + 1.60) for s in (-1, 1)} == {"Eisen"}, w    # frame
    assert _part_at(("OG", "OG_Sanitaer"), *at(6.11, 0.40, 0, 1)(0.27, 0.02), zo + 1.6) != "Eisen"


def _parts(bp, key):
    """(material, lo, hi) per Part of object key of Blueprint bp."""
    g = bp.geo.get(key, {"v": [], "f": [], "m": []})
    for first, n in bp.parts.get(key, []):
        vs = [g["v"][i] for f in g["f"][first:first + n] for i in f]
        yield g["m"][first], [min(p[k] for p in vs) for k in range(3)], [max(p[k] for p in vs) for k in range(3)]


def _mat_at(bp, key, x, y, z):
    return next((m for m, lo, hi in _parts(bp, key) if all(lo[k] < p < hi[k] for k, p in enumerate((x, y, z)))), None)


def test_bad_submodel():
    """code/bad.py: the Großeltern's bathroom after plan_grosseltern_bad.jpeg (input/2026-11-08 input/)
    and the agreed drawing grosseltern_v4.svg (same folder), at its own origin (the room's inner SW
    corner, 2.048 x 3.817 m): walk-in shower 0.80 wide in the NW corner, 35 cm glass from the north
    wall, a 1.20 m wall 1.00 high with glass to the ceiling, the Waschtrog on its east face; in the
    south a 1.20 m niche split by a 12 cm wall into WC and Schrank, closed by two interlocking
    sliding leaves (the WC leaf open behind the Schrank leaf)."""
    import bad
    bp = house_core.build_bad()
    leaves = [pts for c, pts in house_core.LEAVES if c == "Bad"]
    house_core.build()                                                    # restore the registries
    assert {c for c, _ in bp.geo} == {"Bad"} and bp.garden is None
    assert {n for _, n in bp.geo} == {"Bad_Waende", "Bad_Innentueren", "Bad_Sanitaer", "Bad_Fliesen", "Bad_Schrank",
                                      "Bad_Bodenbelag", "Bad_Boden", "Bad_Schiebetuer_hinten", "Bad_Schiebetuer_vorne"}
    W, D, H = 2.048, 3.817, 2.40
    assert all(-1e-9 <= x <= W + 1e-9 and -1e-9 <= y <= D + 1e-9 and -1e-9 <= z <= H + 1e-9
               for g in bp.geo.values() for x, y, z in g["v"])                # no part outside the room
    box = lambda m, lo, hi: [m, [round(a, 3) for a in lo], [round(a, 3) for a in hi]]
    walls = [box(*p) for p in _parts(bp, ("Bad", "Bad_Waende"))]
    assert ["Putz", [0.964, 0, 0], [1.084, 1.2, 2.4]] in walls                # niche wall: WC, Schrank 96.4 each
    assert ["Putz", [0.8, 2.267, 0], [0.92, 3.467, 1.0]] in walls             # low wall 120 x 12, 1.00 high
    for u in (0.5, 1.5):                                                       # lintel over the niche
        assert _mat_at(bp, ("Bad", "Bad_Waende"), u, 1.14, 2.2) == "Putz"
        assert _mat_at(bp, ("Bad", "Bad_Waende"), u, 1.14, 2.0) is None
    san = ("Bad", "Bad_Sanitaer")
    # glass: one L-shaped pane in the low wall's centre plane (request 2026-11-09): on the wall to the
    # ceiling, and 35 cm from the north wall down to the floor
    g = bp.geo[san]
    panes = [{tuple(round(c, 3) for c in g["v"][i]) for f in g["f"][a:a + n] for i in f}
             for a, n in bp.parts[san] if g["m"][a] == "Glas"]
    assert len(panes) == 1
    assert {round(x, 3) for x, _, _ in panes[0]} == {0.787, 0.799}            # 12 mm, flush with the FD jamb (2026-11-10)
    assert {(y, z) for _, y, z in panes[0]} == {(2.267, 1.0), (3.467, 1.0), (3.467, 0.0), (3.817, 0.0),
                                                (3.817, 2.4), (2.267, 2.4)}
    # the passage between the low wall's south end and the front sliding leaf
    pas = [(p0, p1) for p0, p1, t in bp.dims if t.startswith("Durchgang")]
    assert len(pas) == 1 and sorted(round(p[1], 3) for p in pas[0]) == [1.3, 2.267]
    assert {round(p[0], 3) for p in pas[0]} == {0.86}                          # on the wall's centre line
    # sliding leaves: two tracks 5 cm apart, both over the Schrank half (WC leaf open behind it)
    assert len(leaves) == 2
    lb = sorted(([min(p[k] for p in l) for k in range(3)], [max(p[k] for p in l) for k in range(3)]) for l in leaves)
    lb.sort(key=lambda b: b[0][1])
    (rlo, rhi), (flo, fhi) = lb                                                # rear = WC, front = Schrank
    for lo, hi in lb:
        assert abs(lo[0] - 0.964) < 0.005 and abs(hi[0] - W) < 0.005 and hi[2] >= 1.98
    assert abs((flo[1] - rlo[1]) - 0.05) < 0.002 and rhi[1] < flo[1] and rlo[1] > 1.20
    inn = ("Bad", "Bad_Innentueren")
    rear, front = ("Bad", "Bad_Schiebetuer_hinten"), ("Bad", "Bad_Schiebetuer_vorne")   # one object each (animated)
    assert {_mat_at(bp, k, 0.48, y, z) for k, y in ((rear, 1.23), (front, 1.28)) for z in (0.5, 1.0, 1.5)} == {None}   # WC half open
    assert _mat_at(bp, rear, 1.5, 1.23, 1.0) and _mat_at(bp, front, 1.5, 1.28, 1.0)  # both leaves over the Schrank
    assert not [1 for m, lo, hi in _parts(bp, inn) if m != "Metall"]          # Innentueren: only the rail
    # each leaf rolls to the other end of the rail: over the WC half, HALF to the west
    assert bp.slide == {"Bad_Schiebetuer_hinten": (-0.964, 0.0, 0.0), "Bad_Schiebetuer_vorne": (-0.964, 0.0, 0.0)}
    assert any(m == "Metall" and lo[0] <= 0.01 and hi[0] >= W - 0.01 and 1.999 <= lo[2] for m, lo, hi in _parts(bp, inn))  # rail
    for lo, hi in lb:                                                          # no leaf in a wall
        assert not any(all(a[k] < hi[k] - 1e-6 and lo[k] + 1e-6 < b[k] for k in range(3)) for _, a, b in _parts(bp, ("Bad", "Bad_Waende")))
    # WC half: toilet in its middle on the south wall, green tiles; none in the Schrank
    assert _mat_at(bp, san, 0.482, 0.10, 0.60) == "Keramik" and _mat_at(bp, san, 0.482, 0.40, 0.03) == "Keramik"
    til = ("Bad", "Bad_Fliesen")
    for x, y in ((0.482, 0.008), (0.008, 0.6), (0.956, 0.6)):
        assert "Fliese" in {_mat_at(bp, til, x + dx, y, h) for h in (0.3, 0.45, 0.6) for dx in (0.0, 0.05)}, (x, y)
    assert not any(m == "Fliese" and hi[0] > 0.97 for m, lo, hi in _parts(bp, til))
    # walk-in shower: limestone on the west and north walls to 2.0, on the low wall's west face to 1.0
    for x, y, z in ((0.009, 3.0, 1.9), (0.4, 3.808, 1.9), (0.791, 2.8, 0.5)):
        assert _mat_at(bp, til, x, y, z) == "Kalkstein", (x, y, z)
    assert _mat_at(bp, til, 0.009, 3.0, 2.1) is None and _mat_at(bp, til, 0.791, 2.8, 1.5) is None
    assert not any(m == "Keramik" and hi[0] < 0.8 and lo[1] > 2.2 for m, lo, hi in _parts(bp, san))   # no tray: flush
    # Waschtrog: one 1.00 m trough on the low wall's east face, centred on it, top 0.85, two mixers
    trog = [(lo, hi) for m, lo, hi in _parts(bp, san) if m == "Keramik" and lo[1] > 2.2]
    lo = [min(b[0][k] for b in trog) for k in range(3)]
    hi = [max(b[1][k] for b in trog) for k in range(3)]
    assert [round(a, 3) for a in (lo[0], lo[1], hi[1], hi[2])] == [0.92, 2.367, 3.367, 0.85] and hi[0] <= 1.42 + 1e-9
    assert abs((lo[1] + hi[1]) / 2 - (2.267 + 3.467) / 2) < 1e-9
    assert _mat_at(bp, san, 1.2, 2.867, 0.80) is None                          # one open bowl
    mix = {round((lo[1] + hi[1]) / 2, 2) for m, lo, hi in _parts(bp, san)
           if m == "Metall" and lo[0] > 0.92 and lo[2] >= 0.85 - 1e-9 and hi[2] > 0.9}
    assert mix == {2.62, 3.12}
    assert not any("Spiegel" in g["m"] for g in bp.geo.values())
    # Schrank: back cabinet 60 deep over the full width; nothing in front of it, so it can be reached
    # (request 2026-11-09: the hanging wardrobe against the niche wall is gone)
    sch = ("Bad", "Bad_Schrank")
    cab = [(lo, hi) for m, lo, hi in _parts(bp, sch) if hi[1] <= 0.6 + 1e-9]
    assert round(min(b[0][0] for b in cab), 3) == 1.084 and round(max(b[1][0] for b in cab), 3) == W
    assert sum(1 for lo, hi in cab if hi[0] - lo[0] > 0.9 and hi[2] - lo[2] < 0.04) >= 4   # shelves
    assert not [1 for m, lo, hi in _parts(bp, sch) if hi[1] > 0.6 + 1e-9]
    assert all(m == "Rahmen" for m, lo, hi in _parts(bp, sch))                                        # white
    nums = sorted(float(t.split()[0] if t[0].isdigit() else t.split()[-1]) for _, _, t in bp.dims)
    assert nums == sorted([80, 35, 120, 100, 100, 96.4, 12, 96.4, 120, 60, 96.7])
    # floor (request 2026-11-09): part of the sub-model; a limestone strip as wide as the WC from the
    # south wall behind the toilet to the north wall at the shower's end, oak elsewhere, none under
    # the walls; a dark base under the joints
    fl = list(_parts(bp, ("Bad", "Bad_Bodenbelag")))
    at = lambda x, y: {m for m, lo, hi in fl if lo[0] < x < hi[0] and lo[1] < y < hi[1]}
    for x, y in ((0.3, 0.6), (0.4, 3.0), (0.94, 2.0), (0.94, 3.6), (0.05, 3.79)):
        assert at(x, y) <= {"Kalkstein"} and at(x + 0.004, y + 0.004) | at(x, y) == {"Kalkstein"}, (x, y)
    for x, y in ((1.5, 2.0), (1.5, 0.3), (1.2, 3.6), (2.03, 3.79)):
        assert at(x, y) <= {"Eiche"} and at(x + 0.004, y + 0.004) | at(x, y) == {"Eiche"}, (x, y)
    assert max(hi[0] for m, lo, hi in fl if m == "Kalkstein") <= 0.964 <= min(lo[0] for m, lo, hi in fl if m == "Eiche")
    assert at(0.86, 2.8) == set() and at(1.02, 0.6) == set()                    # low wall, niche wall
    assert [m for m, lo, hi in _parts(bp, ("Bad", "Bad_Boden"))] == ["Fuge"]


def test_bad_built_into_the_grosseltern():
    """The Bad sub-model stands in the house at BAD_AT, unrotated, every part the same; the wall
    between the old WC and Bad and its sliding door are gone; the bedroom wall ends at the niche
    front, so Bad and bedroom are open to each other; limestone in the Bad, oak in WC and Schrank."""
    import bad
    sub = house_core.build_bad()
    house_core.build()                                                    # restore the registries
    x0, y0 = bad.BAD_AT
    assert bad.BAD_AT == (0.31, 8.656)

    def solids(bp, key, dx=0.0, dy=0.0):
        g = bp.geo[key]
        return {tuple(sorted({(round(g["v"][i][0] + dx, 6), round(g["v"][i][1] + dy, 6), round(g["v"][i][2], 6))
                              for f in g["f"][a:a + n] for i in f})) for a, n in bp.parts[key]}

    for n in ("Waende", "Innentueren", "Sanitaer", "Fliesen", "Schrank", "Bodenbelag", "Boden", "Schiebetuer_hinten",
              "Schiebetuer_vorne"):
        assert solids(sub, ("Bad", "Bad_" + n), x0, y0) <= solids(BP, ("EG", "EG_" + n)), n
    assert BP.slide == {"EG_Schiebetuer_hinten": (-0.964, 0.0, 0.0), "EG_Schiebetuer_vorne": (-0.964, 0.0, 0.0)}
    wl = list(_parts(BP, ("EG", "EG_Waende")))
    assert not any(lo[1] > 10.0 and hi[1] < 10.3 and lo[0] >= 0.3 and hi[0] <= 2.36 for _, lo, hi in wl)   # WC/Bad wall
    assert not any(lo[0] >= 2.35 and hi[0] <= 2.66 and lo[1] < 12.3 and hi[1] > 9.9 and lo[2] < 2.0 for _, lo, hi in wl)
    assert any(lo[0] >= 2.35 and hi[0] <= 2.66 and abs(hi[1] - 9.856) < 1e-6 and lo[2] < 0.1 for _, lo, hi in wl)
    assert not any(lo[1] > 10.2 and hi[1] < 10.35 and hi[0] < 2.36 for _, lo, hi in _parts(BP, ("EG", "EG_Innentueren")))
    assert len([1 for c, l in house_core.LEAVES if c == "EG" and 0.3 < l[0][0] < 2.4 and 9.8 < l[0][1] < 10.0]) == 2
    assert _floor_at("EG", 0.71, 11.656) == "Kalkstein" and _floor_at("EG", 1.81, 10.7) == "Eiche"   # shower, Bad
    assert _floor_at("EG", 0.8, 9.3) == "Kalkstein" and _floor_at("EG", 1.6, 9.3) == "Eiche"   # WC, Schrank


def test_wcs_have_limestone_floors():
    """Request 2026-11-08: all toilets get stone floors (the limestone of the EG Flur and the
    Bäder): the three WCs of WCS and the WC half of the Bad Großeltern's niche; its Schrank half
    keeps oak."""
    for c, z, (x0, x1, y0, y1), _ in WCS:                                   # incl. the WC Großeltern
        assert _floor_at(c, (x0 + x1) / 2 + 0.02, (y0 + y1) / 2 + 0.03) == "Kalkstein", (c, x0, y0)
    assert _floor_at("EG", 1.6, 9.3) == "Eiche"                           # its Schrank


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
    assert {n for _, n in sub.geo} == {"Kueche_Kueche", "Kueche_Herd", "Kueche_Haube", "Kueche_Waende"}
    assert all(-1e-9 <= x <= 3.067 + 1e-9 and -2.845 <= y <= 1e-9 for (_, n), g in sub.geo.items() for x, y, z in g["v"]
               if n != "Kueche_Herd")                                # (the Wamsler's pipe runs into the wall;
                                                                     # y: the cup pulls towards the dining table)
    for n in ("Kueche", "Herd", "Haube", "Waende"):
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
    herd = [p for p in part_list(("EG", "EG_Herd")) if p[0] == "Herd"]
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
    (west end free), shelf B (60, open to the aisle) and back to back with it cabinet C (60, doors
    to the Essen) in place of the Speis/Essen wall, all to the ceiling; the Speis/Küche wall ends at
    C's front (y 3.13) and is open over the aisle; a sliding leaf on the kitchen side, slid open to
    the south (left as seen from the Küche)."""
    w = ("EG", "EG_Waende")
    assert _mat_at(BP, w, 4.0, 3.2, 1.0) is None                                          # Speis/Essen wall gone
    assert _mat_at(BP, w, 5.36, 3.5, 1.0) == "Putz" and _mat_at(BP, w, 5.36, 4.2, 1.0) == "Putz"
    assert _mat_at(BP, w, 5.36, 4.8, 1.0) is None and _mat_at(BP, w, 5.36, 3.05, 1.0) is None
    sp = list(part_list(("EG", "EG_Speis")))
    assert sp and "EG_Speis" not in BP.furniture
    for ya, yb in ((5.249, 5.847), (3.732, 4.33), (3.13, 3.728)):                         # A, B, C
        band = [p for p in sp if p[1][1] >= ya - 1e-6 and p[2][1] <= yb + 1e-6]
        assert band and abs(min(p[1][1] for p in band) - ya) < 0.003 and abs(max(p[2][1] for p in band) - yb) < 0.003
        assert min(p[1][0] for p in band) < 2.78 and max(p[2][0] for p in band) > 5.23
        assert 2.39 <= max(p[2][2] for p in band) < 2.40
    assert not any(p[2][1] > 4.34 and p[1][1] < 5.24 for p in sp)                          # the aisle is free
    doors = [p for p in sp if p[1][1] >= 3.13 - 1e-6 and p[2][1] <= 3.15 + 1e-6 and p[0] != "Metall"]
    assert len(doors) >= 4
    assert not any(p[2][0] > 2.78 and p[1][0] < 5.24 and p[2][1] > 3.13 and p[1][1] < 5.85
                   for p in part_list(("EG", "EG_Moebel")))                                # old shelves gone
    leaf = [l for c, l in house_core.LEAVES if c == "EG" and 5.49 < min(l[0][0], l[1][0]) < 5.6]
    assert len(leaf) == 1
    (a, b), = leaf
    assert abs(min(a[1], b[1]) - 3.28) < 0.01 and abs(max(a[1], b[1]) - 4.28) < 0.01


def test_bad_glass_ends_at_the_french_door_jamb():
    """Request 2026-11-10: the glass pane on the 1 m low wall is moved towards the shower so that,
    towards the north french door, it ends flush with the door's jamb (the wall edge) instead of
    standing in front of the opening; it still stands on the low wall (on its limestone edge), and
    the shower's north cladding stops at the glass."""
    import bad
    fd = [op for op in house_core.OPENINGS if op["kind"] == "FD" and op["ax"] == "x"
          and abs(op["face"] - house_core.D_OUT) < 0.4 and op["a"] < 2.0]
    assert len(fd) == 1 and bad.FD_JAMB == fd[0]["a"]
    glass = [p for p in part_list(("EG", "EG_Sanitaer")) if p[0] == "Glas"]
    assert len(glass) == 1
    _, lo, hi, _ = glass[0]
    low = bad.BAD_AT[0] + bad.SHOWER                                           # low wall's west face
    assert abs(hi[0] - fd[0]["a"]) < 1e-9 and 0.008 <= hi[0] - lo[0] <= 0.015
    assert lo[0] >= low - 0.014 and hi[0] <= low                              # on the wall's cladding edge
    north = [p for p in part_list(("EG", "EG_Fliesen")) if p[1][1] > bad.BAD_AT[1] + bad.D - 0.02]
    assert north and max(p[2][0] for p in north) <= lo[0] + 1e-9


def test_wc_tiles_in_ral_5014():
    """Request 2026-11-10: the formerly green WC / Bad tiles in the house's RAL 5014 Taubenblau:
    their speckle's two colours lie around RAL 5014 (linear), no longer green; no green tiles left."""
    lin = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    ral = [lin(v / 255) for v in house_core.RAL_5014]
    c1, c2, _ = house_core.MAT_DEF["Fliese"]["speck"]
    mid = [(a + b) / 2 for a, b in zip(c1, c2)]
    assert all(abs(m - r) < 0.01 for m, r in zip(mid, ral)), mid
    assert all(c[2] > c[1] > c[0] for c in (c1, c2))                        # blue, not green
