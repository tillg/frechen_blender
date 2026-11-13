"""2D plan export (code/export_plans.py) and the core records it draws from: DOORS, PLAN_ROOMS."""
import math, os, re, resource, subprocess, sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "code"))
import house_core  # noqa: E402

BP = house_core.build()


def test_every_opened_leaf_has_a_door_record():
    """panel_door, entrance_door and back_door record every hinged leaf (LEAVES also holds the
    three sliding leaves: the Bad's two and the Speis's)."""
    bp = house_core.build()                     # LEAVES is module state: other tests rebuild it
    doors, leaves = bp.doors, list(house_core.LEAVES)
    for c in ("EG", "OG"):
        hinged = [lv for lv in leaves if lv[0] == c]
        n_slide = len(bp.slide) + 1 if c == "EG" else 0
        extra = 2 if c == "EG" else 0                                    # Haustür, Hintertür
        assert len([d for d in doors if d["c"] == c]) == len(hinged) - n_slide + extra, c
    for d in doors:
        assert set(d) == {"c", "z", "hinge", "w", "closed", "open", "leaf"}
        assert 0.6 < d["w"] < 1.1
        assert abs(math.hypot(*d["closed"]) - 1) < 1e-9 and abs(math.hypot(*d["open"]) - 1) < 1e-9
        assert abs(d["closed"][0] * d["open"][0] + d["closed"][1] * d["open"][1]) < 1e-9   # at 90 deg
    k = [d for d in doors if d["c"] == "EG" and 6.0 < d["hinge"][0] < 6.2 and 5.8 < d["hinge"][1] < 6.4]
    assert len(k) == 1                                                   # the Küche door
    (x, y), = [k[0]["hinge"]]
    assert abs(x - 6.125) < 1e-9 and abs(y - 5.849) < 1e-9               # west jamb's lining, Küche face
    assert k[0]["open"] == (0, -1) and k[0]["closed"] == (1, 0)


def test_plan_room_anchors_lie_inside_the_footprint_and_outside_every_wall():
    """PLAN_ROOMS: the architect's names, one anchor per room; the anchor is a free spot of the
    room (inside the house or the annex, in no wall at sill height)."""
    rooms = BP.plan_rooms
    eg = [r[0] for r in rooms if r[1] == "EG"]
    og = [r[0] for r in rooms if r[1] == "OG"]
    assert len(eg) + len(og) == len(rooms)
    assert {"Großeltern", "Bad Großeltern", "WC Großeltern", "Flur", "WC", "Garderobe", "Bibliothek",
            "Neuer Windfang", "Küche", "Speis", "Stube", "Elektroraum", "Heizung"} == set(eg)
    assert {"Schlafen bzw. Yoga", "Schlafen", "Bad", "WC", "Flur", "Hauswirtschaftsraum"} == set(og)
    rects = list(house_core.FOOT) + [house_core.ANNEX]
    for name, st, x, y in rooms:
        assert any(x0 < x < x1 and y0 < y < y1 for x0, x1, y0, y1 in rects), name
        z = (0.0 if st == "EG" else house_core.Z_OG) + 1.0
        for (c, o), parts in BP.parts.items():
            if c != st or not (o.endswith("_Waende") or o == "EG_Anbau"):
                continue
            g = BP.geo[(c, o)]
            for first, n in parts:
                P = [g["v"][i] for f in g["f"][first:first + n] for i in f]
                lo = [min(p[k] for p in P) for k in range(3)]
                hi = [max(p[k] for p in P) for k in range(3)]
                assert not all(lo[k] <= v <= hi[k] for k, v in enumerate((x, y, z))), (name, o)


def test_every_object_named_in_the_plan_table_exists_in_the_model():
    """PLAN (the core's object classes for the plan sheets): every name and name part matches."""
    plan, objs = BP.plan, {o for _, o in BP.geo}
    for k in ("wall_objects", "ground", "extra_objects"):
        assert set(plan[k]) <= objs, (k, set(plan[k]) - objs)
    for k in ("wall_suffix", "frame_suffix"):
        assert any(o.endswith(plan[k]) for o in objs), k
    for w in plan["skip_words"]:
        assert any(w in o for o in objs), w
    assert set(plan["extra_collections"]) <= {c for c, _ in BP.geo}
    assert any(g["m"] and plan["wall_mat"] in g["m"] for g in BP.geo.values())


def test_export_plans_names_no_model_object():
    """ADR-001-XEWL: the backend knows how to draw, the core knows what the objects are."""
    src = (Path(__file__).resolve().parent.parent / "code" / "export_plans.py").read_text()
    for name in ("_Waende", "EG_Anbau", "Balkone", "Gelaende", "Kiesel", "Kiesstreifen", "_Fenster_Tueren",
                 '"Boden"', '"Decke"', '"Putz"'):
        assert name not in src, name


# ---------------------------------------------------------------- the sheets (code/export_plans.py)
ROOT = Path(__file__).resolve().parent.parent
SHEETS = ["eg", "og", "nord", "ost", "sued", "west"]
SVG = "{http://www.w3.org/2000/svg}"


def run_export(out, seed):
    env = dict(os.environ, PYTHONHASHSEED=str(seed))
    subprocess.run([sys.executable, str(ROOT / "code" / "export_plans.py"), str(out)], check=True, env=env)


class Out(type(Path())):
    cpu = 0.0


@pytest.fixture(scope="module")
def sheets(tmp_path_factory):
    out = Out(tmp_path_factory.mktemp("plans"))
    t = resource.getrusage(resource.RUSAGE_CHILDREN)
    run_export(out, 1)
    u = resource.getrusage(resource.RUSAGE_CHILDREN)
    out.cpu = u.ru_utime + u.ru_stime - t.ru_utime - t.ru_stime
    return out


def test_sheets_are_a3_in_mm_with_a_1_m_10_mm_scale_bar(sheets):
    assert sorted(p.stem for p in sheets.glob("*.svg")) == sorted(SHEETS)
    for s in SHEETS:
        root = ET.parse(sheets / f"{s}.svg").getroot()
        assert (root.get("width"), root.get("height"), root.get("viewBox")) == ("420mm", "297mm", "0 0 420 297")
        bar = root.find(f".//{SVG}g[@id='scale']")
        xs = [(float(r.get("x")), float(r.get("x")) + float(r.get("width"))) for r in bar.iter(f"{SVG}rect")]
        assert len(xs) == 5 and max(b for _, b in xs) - min(a for a, _ in xs) == 50     # 5 m = 50 mm
        text = "".join(root.itertext())
        assert "M 1:100" in text and "Frechenlehen" in text
        assert (root.find(f".//{SVG}g[@id='north']") is not None) == (s in ("eg", "og"))


def test_the_model_state_changes_with_a_room_name_and_a_door():
    """The title block's hash names everything a sheet is drawn from, not only the geometry."""
    import dataclasses
    base = ep.model_state(BP)
    rooms = [("Gute Stube",) + BP.plan_rooms[0][1:]] + BP.plan_rooms[1:]
    doors = [dict(BP.doors[0], hinge=(BP.doors[0]["hinge"][0] + 0.01, BP.doors[0]["hinge"][1]))] + BP.doors[1:]
    assert ep.model_state(dataclasses.replace(BP, plan_rooms=rooms)) != base
    assert ep.model_state(dataclasses.replace(BP, doors=doors)) != base
    assert ep.model_state(dataclasses.replace(BP)) == base


@pytest.mark.slow
def test_export_is_byte_identical_across_processes(sheets, tmp_path):
    run_export(tmp_path, 2)
    for s in SHEETS:
        assert (tmp_path / f"{s}.svg").read_bytes() == (sheets / f"{s}.svg").read_bytes(), s


# ---------------------------------------------------------------- Grundriss: the section
import export_plans as ep  # noqa: E402

SECTIONS = {st: ep.section(BP, st) for st in ("EG", "OG")}
FLOOR = {"EG": 0.0, "OG": house_core.Z_OG}


def storey_of(z):
    return "OG" if z >= house_core.Z_OG - 0.1 else "EG"


def test_every_opening_spans_its_storeys_cut_height():
    """The cut height lies above every sill and below every head of the storey, so every window and
    door shows as a gap in the cut."""
    for o in house_core.OPENINGS:
        st = storey_of(o["sill"])
        assert o["sill"] < FLOOR[st] + ep.CUT[st] < o["head"], o
    for d in BP.doors:
        assert ep.CUT[d["c"]] < house_core.DOOR_H, d


def test_the_west_cladding_is_cut_in_eg_and_og_the_east_cladding_in_neither():
    """Verschalung_West (collection Dach, z 0.25-7.55) stands in both cut planes; Verschalung_Ost
    starts at 4.90, above the OG cut (4.25)."""
    for st, sec in SECTIONS.items():
        west = [L for o, L in sec["cut"] if o == "Verschalung_West"]
        assert any(max(p[0] for l in L for p in l) <= 1e-6 for L in west), st      # boards on the west face
        for L in west:                                                           # all outside the masonry
            x0, x1, y0, y1 = ep.bbox([p for l in L for p in l])
            assert not in_walls(sec, (x0 + x1) / 2, (y0 + y1) / 2), (st, x0, y0)
        assert not [o for o, _ in sec["cut"] if o == "Verschalung_Ost"], st


def in_walls(sec, x, y):
    return any(ep.inside(L, x, y) for _, L in sec["walls"])


def test_the_eg_wall_outline_spans_the_footprint():
    pts = [p for p, q in SECTIONS["EG"]["outline"] for p in (p, q)]
    x0, x1 = min(p[0] for p in pts), max(p[0] for p in pts)
    y0, y1 = min(p[1] for p in pts), max(p[1] for p in pts)
    assert abs(x0 - house_core.ANNEX[0]) < 1e-6 and abs(y0) < 1e-6 and abs(y1 - house_core.D_OUT) < 1e-6
    assert house_core.W_OUT - 1e-6 < x1 < house_core.W_OUT + 0.05      # the Haustür's raised surround: 4 cm


def test_no_stroked_wall_edge_lies_inside_the_wall_union():
    for st, sec in SECTIONS.items():
        assert sec["outline"], st
        for p, q in sec["outline"]:
            L = math.hypot(q[0] - p[0], q[1] - p[1])
            nx, ny = -(q[1] - p[1]) / L * 1e-3, (q[0] - p[0]) / L * 1e-3
            mx, my = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
            assert in_walls(sec, mx + nx, my + ny) != in_walls(sec, mx - nx, my - ny), (st, p, q)


def test_each_exterior_opening_of_the_storey_is_a_gap_in_the_outline():
    for o in house_core.OPENINGS:
        sec = SECTIONS[storey_of(o["sill"])]
        u = (o["a"] + o["b"]) / 2
        for dt in (-0.02, 0.02):                                    # just inside the wall, either face
            x, y = (u, o["face"] + dt) if o["ax"] == "x" else (o["face"] + dt, u)
            assert not in_walls(sec, x, y), o


# ---------------------------------------------------------------- projection
@pytest.fixture(scope="module")
def faces():
    return ep.solid_faces(BP)


@pytest.fixture(scope="module")
def views(faces):
    v = {s: ep.project(faces, s) for s in ("nord", "ost", "sued", "west")}
    v.update({st: ep.plan_view(BP, faces, st) for st in ("EG", "OG")})
    return v


def test_ansicht_sued_outline(views):
    """The south elevation shows the whole roof: gable overhang to gable overhang, up to the ridge."""
    roof = [p for o, uv, _ in views["sued"] if o == "Dach" for p in uv]
    assert abs(min(p[0] for p in roof) + house_core.GABLE_OH) < 1e-6
    assert abs(max(p[0] for p in roof) - house_core.W_OUT - house_core.GABLE_OH) < 1e-6
    assert abs(max(p[1] for o, uv, _ in views["sued"] for p in uv) - house_core.RIDGE_Z) < 1e-6


def test_no_loose_furniture_on_any_sheet(views):
    for k, items in views.items():
        assert items, k
        assert not {o for o, _, _ in items} & BP.furniture, k


def test_plans_show_the_kitchen_below_the_cut_and_the_stair_only_as_its_symbol(views):
    eg = {o for o, _, _ in views["EG"]}
    assert "EG_Kueche" in eg and not any(o.startswith("OG_") for o in eg)
    assert "EG_Treppe" not in eg and "EG_Treppe" in BP.plan["stair_objects"]       # no cut treads: the symbol


def test_the_stair_is_drawn_as_in_the_architects_plan_with_the_arrow_up(sheets):
    """Request 2026-11-11: the stair as in the architect's plan, in EG and OG alike: its outline, a
    line at every riser (15 risers, 18.0/25.5), the walking line from a circle at the bottom step to
    an arrow at the top (always pointing up the stair, i.e. west); in EG also "15 STG 18.0/25.5"."""
    st, = BP.stairs
    assert st["storeys"] == ("EG", "OG") and len(st["risers"]) == 15
    assert st["risers"][0] > st["risers"][-1]                                         # rises westwards
    T = ep.plan_to_sheet()
    for name in ("eg", "og"):
        root = ET.parse(sheets / f"{name}.svg").getroot()
        g, = [e for e in root.iter() if e.get("id") == "stairs"]
        nums = lambda d: [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", d)]
        risers = [e for e in g if e.get("class") == "riser"]
        assert len(risers) == 13                                                      # the 13 inner risers
        xs = sorted(nums(e.get("d"))[0] for e in risers)
        assert xs == pytest.approx(sorted(T((x, 0))[0] for x in st["risers"][1:-1]), abs=0.01)
        (x0, y0), (x1, y1) = T(st["lo"]), T(st["hi"])
        out, = [e for e in g if e.get("class") == "outline"]
        assert sorted(nums(out.get("d"))[0::2]) [0] == pytest.approx(min(x0, x1), abs=0.01)
        circle, = [e for e in g if e.tag.endswith("circle")]
        cx, cy = float(circle.get("cx")), float(circle.get("cy"))
        bx, by = T((st["risers"][0], st["y"]))
        tx, ty = T((st["risers"][-1], st["y"]))
        assert abs(cy - by) < 0.01 and abs(cx - bx) < 1.0                           # at the bottom step
        arrow, = [e for e in g if e.get("class") == "arrow"]
        p = nums(arrow.get("d"))
        tip = (p[2], p[3])                                                           # M wing L tip L wing
        assert tip == pytest.approx((tx, ty), abs=0.01)
        assert p[0] > tip[0] and p[4] > tip[0]                                       # its wings trail east: up = west
        walk, = [e for e in g if e.get("class") == "walk"]
        assert nums(walk.get("d"))[0::2][:2] == pytest.approx([bx, tx], abs=0.01)
        labels = ["".join(e.itertext()) for e in g if e.tag.endswith("text")]
        assert labels == (["15 STG 18.0/25.5"] if name == "eg" else [])


def test_no_hinged_leaf_is_drawn_in_the_section(views):
    """Conventional door symbol: the leaf is drawn only as the 90 deg line of its swing, so the leaf
    as built (opened flat against the wall, at 90 deg, or closed) is neither cut nor seen below the cut."""
    def within(pts, box):
        (x0, y0), (x1, y1) = box
        a0, a1, b0, b1 = ep.bbox(pts)
        return x0 - 1e-6 <= a0 and a1 <= x1 + 1e-6 and y0 - 1e-6 <= b0 and b1 <= y1 + 1e-6
    for st, sec in SECTIONS.items():
        for d in [d for d in BP.doors if d["c"] == st]:
            assert not [o for o, L in sec["cut"] if within([p for l in L for p in l], d["leaf"])], (st, d["hinge"])
            assert not [o for o, uv, _ in views[st] if within(uv, d["leaf"])], (st, d["hinge"])


def test_size_and_time_budget(sheets):
    """Six sheets in <= 30 s of CPU (the machine may be busy), each <= 2 MB."""
    assert sheets.cpu <= 30, sheets.cpu
    for s in SHEETS:
        assert (sheets / f"{s}.svg").stat().st_size <= 2_000_000, s


# ---------------------------------------------------------------- door swings
def test_one_arc_per_door_of_the_storey_centred_on_its_hinge_radius_leaf_width(sheets):

    T = ep.plan_to_sheet()
    for st in ("EG", "OG"):
        doors = [d for d in BP.doors if d["c"] == st]
        g = ET.parse(sheets / f"{st.lower()}.svg").getroot().find(f".//{SVG}g[@id='doors']")
        paths = [p.get("d") for p in g.iter(f"{SVG}path")]
        assert len(paths) == len(doors), st
        for d, path in zip(doors, paths):
            n = [float(v) for v in re.findall(r"-?\d+\.\d+", path)]
            (ox, oy), (hx, hy), (cx, cy), r = n[0:2], n[2:4], n[4:6], n[6]
            assert (hx, hy) == tuple(float(ep.num(v)) for v in T(d["hinge"])), d          # leaf from the hinge
            assert abs(r - d["w"] * ep.S) < 0.01                                         # arc radius = leaf
            for x, y in ((ox, oy), (cx, cy)):
                assert abs(math.hypot(x - hx, y - hy) - r) < 0.02, d
            assert re.search(r"A[\d.]+ [\d.]+ 0 0 [01] " + ep.num(ox) + " " + ep.num(oy), path), path


def test_every_door_opens_to_its_leafs_side_and_its_arc_sweeps_from_closed_to_open(sheets):
    """All records: a leaf built open (flat or at 90 deg) lies on the `open` side of its hinge; the two
    leaves built closed (Haustür, Hintertür) open into the house. On the sheet the arc runs the
    quarter turn from the closed to the open leaf end."""
    rects = list(house_core.FOOT) + [house_core.ANNEX]
    closed_leaves = 0
    for d in BP.doors:
        (x0, y0), (x1, y1) = d["leaf"]
        (hx, hy), (ox, oy), (cx, cy) = d["hinge"], d["open"], d["closed"]
        mx, my = (x0 + x1) / 2 - hx, (y0 + y1) / 2 - hy
        if mx * cx + my * cy < 0.25 * d["w"]:                    # not along the closed position: built open
            assert mx * ox + my * oy > 0, d
        else:
            closed_leaves += 1
            px, py = hx + 0.5 * ox, hy + 0.5 * oy
            assert any(a < px < b and c < py < e for a, b, c, e in rects), d
    assert closed_leaves == 2
    T = ep.plan_to_sheet()
    for st in ("EG", "OG"):
        g = ET.parse(sheets / f"{st.lower()}.svg").getroot().find(f".//{SVG}g[@id='doors']")
        for d, path in zip([d for d in BP.doors if d["c"] == st], [p.get("d") for p in g.iter(f"{SVG}path")]):
            sweep = int(re.search(r"A[\d.]+ [\d.]+ 0 0 ([01]) ", path).group(1))
            (hx, hy) = T(d["hinge"])
            ends = [T((d["hinge"][0] + d["w"] * v[0], d["hinge"][1] + d["w"] * v[1])) for v in (d["closed"], d["open"])]
            a_c, a_o = (math.degrees(math.atan2(y - hy, x - hx)) for x, y in ends)    # sheet: y down
            turn = round((a_o - a_c) % 360)                                          # SVG sweep 1 = increasing angle
            assert turn in (90, 270) and sweep == (turn == 90), (st, d["hinge"], turn, sweep)


# ---------------------------------------------------------------- rooms
ROOMS = {st: ep.room_regions(BP, st) for st in ("EG", "OG")}


def test_each_plan_room_is_its_own_region():
    for st, (regions, anchors) in ROOMS.items():
        assert None not in anchors.values(), st                      # every anchor lies in a room
        assert len(set(anchors.values())) == len(anchors), st          # no region holds two anchors
        for k, r in anchors.items():
            assert not regions[r]["outside"], BP.plan_rooms[k]


def test_no_room_label_overlaps_a_wall():
    """The label as room_labels writes it (name lines, then the area; centred on the anchor, sheet mm
    -> model m: / S), its text box approximated (width = characters x 0.55 x size, glyphs from 0.75 x
    size above to 0.2 x size below the baseline), sampled on a grid against the wall hatch."""
    for st, (regions, anchors) in ROOMS.items():
        sec = SECTIONS[st]
        for k, r in anchors.items():
            name, _, x, y = BP.plan_rooms[k]
            lines, size = ([name], 2.5) if regions[r]["area"] >= 2.0 else (name.split(" "), 1.6)
            rows = [(ln, size, i * size * 1.15) for i, ln in enumerate(lines)]
            rows.append((ep.fmt_area(regions[r]["area"]), size * 0.88, len(lines) * size * 1.15 + 0.3))
            for ln, sz, dy in rows:
                w, top, bot = len(ln) * 0.55 * sz / ep.S, y - (dy - 0.75 * sz) / ep.S, y - (dy + 0.2 * sz) / ep.S
                for i in range(9):
                    for j in range(3):
                        px, py = x - w / 2 + w * i / 8, bot + (top - bot) * j / 2
                        assert not in_walls(sec, px, py), (st, name, ln)


def test_an_anchor_inside_a_wall_raises_valueerror_naming_the_room():
    import dataclasses
    bp = dataclasses.replace(BP, plan_rooms=[("Testraum", "EG", 5.0, house_core.D_OUT - 0.2)])   # in the north wall
    with pytest.raises(ValueError, match="Testraum"):
        ep.room_regions(bp, "EG")


def test_text_escapes_ampersand_and_angle_brackets():
    assert ">A &amp; B &lt;C&gt;</text>" in ep.text(0, 0, "A & B <C>")


def test_a_sub_model_build_leaves_no_door_records_behind():
    try:
        for sub in (house_core.build_ofen, house_core.build_desk):
            house_core.build()
            sub()
            assert not house_core.DOORS, sub.__name__
    finally:
        house_core.build()                      # module state (OPENINGS, LEAVES …) as the other tests expect


def test_bad_grosseltern_area_is_its_inner_dimensions_without_the_niche():
    """bad.py: W x D, the niche (NICHE deep) apart behind its lintel; the shaft in the NE corner."""
    import bad
    regions, anchors = ROOMS["EG"]
    k = next(k for k, r in enumerate(BP.plan_rooms) if r[0] == "Bad Großeltern")
    shaft = (2.358 - 2.04) * (12.471 - 12.12)
    assert abs(regions[anchors[k]]["area"] - (bad.W * (bad.D - bad.NICHE) - shaft)) <= 0.01


def test_the_area_label_uses_a_decimal_comma_and_two_decimals(sheets):
    assert ep.fmt_area(24.0612) == "24,06 m²" and ep.fmt_area(4.5) == "4,50 m²"
    for st in ("eg", "og"):
        g = ET.parse(sheets / f"{st}.svg").getroot().find(f".//{SVG}g[@id='rooms']")
        areas = [t.text for t in g.iter(f"{SVG}text") if t.text.endswith(" m²")]
        assert len(areas) == len([r for r in BP.plan_rooms if r[1] == st.upper()])
        assert all(re.fullmatch(r"\d+,\d\d m²", a) for a in areas), areas


# ---------------------------------------------------------------- dimension chains
CHAINS = {st: ep.chains(BP, st, SECTIONS[st]) for st in ("EG", "OG")}


def test_notation():
    assert [ep.fmt_dim(v) for v in (0.31, 0.415, 2.05, 4.015, 14.885, 1.0, 0.15)] == \
        ["31", "41⁵", "2.05", "4.01⁵", "14.88⁵", "1.00", "15"]


def test_every_chain_sums_to_its_overall_dimension():
    for st, sides in CHAINS.items():
        for side, (ops, walls, overall) in sides.items():
            assert len(overall) == 2 and len(ops) > 2 and len(walls) > 2, (st, side)
            for ch in (ops, walls):
                assert ch == sorted(ch) and (ch[0], ch[-1]) == tuple(overall), (st, side)
                assert abs(sum(b - a for a, b in zip(ch, ch[1:])) - (overall[1] - overall[0])) < 1e-9


def test_the_eg_overall_chains_are_w_out_and_d_out():
    for side, (_, _, (a, b)) in CHAINS["EG"].items():
        assert ep.fmt_dim(b - a) == ep.fmt_dim(house_core.W_OUT if side in "NS" else house_core.D_OUT), side


def test_the_north_opening_chain_has_the_edges_of_the_north_openings():
    north = [o for o in house_core.OPENINGS if o["ax"] == "x" and abs(o["face"] - house_core.D_OUT) < 1e-6
             and o["sill"] < house_core.Z_OG - 0.1]
    assert len(north) == 5
    assert set(CHAINS["EG"]["N"][0]) == {ep.half_cm(v) for o in north for v in (o["a"], o["b"])} | \
        set(CHAINS["EG"]["N"][2])


def test_chains_are_drawn_on_the_floor_plans(sheets):
    g = ET.parse(sheets / "eg.svg").getroot().find(f".//{SVG}g[@id='dims']")
    assert g is not None and "14.88⁵" in "".join(ET.parse(sheets / "eg.svg").getroot().itertext())


# ---------------------------------------------------------------- elevation annotation
def test_ansicht_sued_marks_the_levels_and_the_width_chain_spans_the_facade(sheets):
    root = ET.parse(sheets / "sued.svg").getroot()
    levels = "".join(root.find(f".//{SVG}g[@id='levels']").itertext())
    for z in (0.0, house_core.Z_OG, house_core.RIDGE_Z):
        assert ep.fmt_level(z) in levels, z
    assert ["±0,00", "+2,70", "+7,67"] == [ep.fmt_level(z) for z in (0.0, house_core.Z_OG, house_core.RIDGE_Z)]
    ch = ep.width_chain("sued")
    assert (ch[0], ch[-1]) == (ep.half_cm(house_core.ANNEX[0]), ep.half_cm(house_core.W_OUT))
    assert ep.fmt_dim(ch[-1] - ch[0]) in "".join(root.find(f".//{SVG}g[@id='width']").itertext())
    for side in ("nord", "ost", "west"):
        assert len(ep.width_chain(side)) >= 2, side


# ---------------------------------------------------------------- committed plans
@pytest.mark.slow
def test_plans_equal_a_fresh_export(sheets):
    """plans/ is committed: after a core change, re-run python3 code/export_plans.py plans/."""
    for s in SHEETS:
        assert (ROOT / "plans" / f"{s}.svg").read_bytes() == (sheets / f"{s}.svg").read_bytes(), \
            f"plans/{s}.svg is out of date: python3 code/export_plans.py plans/"


def test_the_walls_chain_runs_inside_the_rooms_not_inside_the_facade_wall():
    """East: the south part of the wall is 53.5 cm thick; the scan line lies beyond it, so the chain
    reads the south wall, the Stube, the Stube/Flur wall … – not the terrace door's jambs."""
    h = ep.half_cm
    assert CHAINS["EG"]["E"][1][:4] == [0.0, h(0.415), h(5.849), h(6.349)]
    assert CHAINS["OG"]["E"][1][:4] == [0.0, h(0.40), h(6.06), h(6.35)]
    for st, sides in CHAINS.items():                      # no chain of walls is the chain of openings
        for side, (ops, walls, _) in sides.items():
            assert ops != walls, (st, side)


# ---------------------------------------------------------------- generation date (GitHub Pages only)
def test_the_title_block_names_the_generation_time_only_when_asked(tmp_path):
    """export_plans.py --generated (the Pages workflow) writes the Berlin time into the title block;
    without it the sheets stay byte-identical, so plans/ in the repo carries no date."""
    import datetime
    utc = datetime.datetime(2026, 11, 12, 19, 34, tzinfo=datetime.timezone.utc)
    assert ep.generated(utc) == "generiert: 12. November 2026 20:34 Uhr"                 # CET
    assert ep.generated(utc.replace(month=7)) == "generiert: 12. Juli 2026 21:34 Uhr"    # CEST
    assert "generiert" not in ep.sheet("Ost", "", "abc")
    assert ">generiert: 12. November 2026 20:34 Uhr</text>" in ep.sheet("Ost", "", "abc", stamp=ep.generated(utc))


def test_sheets_leave_the_variant_out(sheets):
    """The plan sheets show the default layout (#5): drawn from house_core.default_layout(), which the
    model state in the title block names."""
    svg = (sheets / "eg.svg").read_text()
    assert f"Modellstand {ep.model_state(house_core.default_layout(BP))}" in svg
    assert ep.model_state(BP) != ep.model_state(house_core.default_layout(BP))


def test_every_sheet_carries_the_viewers_title_top_left(sheets):
    """'Frechenlehen' at the top left of every sheet, set like the viewer's title (Georgia, regular)."""
    for key, _ in ep.SHEETS:
        svg = (sheets / f"{key}.svg").read_text()
        m = re.search(r'<text x="([\d.]+)" y="([\d.]+)" font-size="([\d.]+)"[^>]*font-family="Georgia[^"]*"[^>]*>Frechenlehen</text>', svg)
        assert m, key
        x, y, size = map(float, m.groups())
        assert x < 30 and y < 40 and size >= 8, (key, x, y, size)
