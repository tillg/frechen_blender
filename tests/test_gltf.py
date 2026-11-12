"""export_gltf: Blueprint -> .glb, read back with the standard library only."""
import json, math, struct, subprocess, sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "code"))
import house_core  # noqa: E402

BP = house_core.build()
TYPES = {"SCALAR": 1, "VEC3": 3}


@pytest.fixture(scope="module")
def glb(tmp_path_factory):
    out = tmp_path_factory.mktemp("glb") / "frechenlehen.glb"
    subprocess.run([sys.executable, str(ROOT / "code" / "export_gltf.py"), str(out)], check=True)
    data = out.read_bytes()
    magic, version, length = struct.unpack_from("<4sII", data, 0)
    jlen, jtype = struct.unpack_from("<I4s", data, 12)
    gltf = json.loads(data[20:20 + jlen])
    blen, btype = struct.unpack_from("<I4s", data, 20 + jlen)
    binc = data[28 + jlen:28 + jlen + blen]
    return dict(magic=magic, version=version, length=length, size=len(data), jtype=jtype,
                btype=btype, blen=blen, jlen=jlen, gltf=gltf, bin=binc)


def read(g, acc_index):
    acc = g["gltf"]["accessors"][acc_index]
    bv = g["gltf"]["bufferViews"][acc["bufferView"]]
    n = acc["count"] * TYPES[acc["type"]]
    fmt = "<%d%s" % (n, "f" if acc["componentType"] == 5126 else "I")
    vals = struct.unpack_from(fmt, g["bin"], bv.get("byteOffset", 0) + acc.get("byteOffset", 0))
    k = TYPES[acc["type"]]
    return [vals[i:i + k] for i in range(0, n, k)] if k > 1 else list(vals)


def house_nodes(g):
    return [n for n in g["gltf"]["nodes"] if n["name"] != "GA_Grasbuschel"]


def node(g, name):
    return next(n for n in g["gltf"]["nodes"] if n["name"] == name)


def positions(g, name):
    mesh = g["gltf"]["meshes"][node(g, name)["mesh"]]
    return [p for prim in mesh["primitives"] for p in read(g, prim["attributes"]["POSITION"])]


def test_valid_glb(glb):
    assert glb["magic"] == b"glTF" and glb["version"] == 2 and glb["length"] == glb["size"]
    assert glb["jtype"] == b"JSON" and glb["btype"] == b"BIN\0"
    assert glb["size"] == 12 + 8 + glb["jlen"] + 8 + glb["blen"]


def test_vec3_min_max_equal_the_stored_data(glb):
    """Khronos validator: min/max must equal the float32 values (ACCESSOR_MIN/MAX_MISMATCH)."""
    for i, acc in enumerate(glb["gltf"]["accessors"]):
        if acc["type"] == "VEC3":
            vals = read(glb, i)
            assert acc["min"] == [min(v[k] for v in vals) for k in range(3)], i
            assert acc["max"] == [max(v[k] for v in vals) for k in range(3)], i


def test_one_node_per_geo_object(glb):
    got = {(n["extras"]["collection"], n["name"]) for n in house_nodes(glb)}
    assert got == set(BP.geo) and ("EG", "Laeden_Querbretter") in got
    assert len(house_nodes(glb)) == len(BP.geo)


def test_triangle_count(glb):
    want = sum(len(f) - 2 for g in BP.geo.values() for f in g["f"])
    got = sum(glb["gltf"]["accessors"][p["indices"]]["count"] // 3
              for n in house_nodes(glb) for p in glb["gltf"]["meshes"][n["mesh"]]["primitives"])
    assert got == want


def test_every_primitive_has_rnd_from_its_parts(glb):
    mats = glb["gltf"]["materials"]
    for n in house_nodes(glb):
        g = BP.geo[(n["extras"]["collection"], n["name"])]
        for p in glb["gltf"]["meshes"][n["mesh"]]["primitives"]:
            m = mats[p["material"]]["name"][3:]
            allowed = {struct.unpack("<f", struct.pack("<f", r))[0] for r, mm in zip(g["r"], g["m"]) if mm == m}
            assert set(read(glb, p["attributes"]["_RND"])) <= allowed, (n["name"], m)


def test_materials_carry_kind_and_paint(glb):
    mats = {m["name"]: m for m in glb["gltf"]["materials"]}
    assert set(mats) == {"FL_" + k for k in BP.mat_def}
    assert mats["FL_Laden"]["extras"]["paint"] == [99, 125, 150]
    assert mats["FL_Laerche"]["extras"]["kind"] == "wood" and mats["FL_Granit"]["extras"]["kind"] == "speck"
    assert mats["FL_Putz"]["extras"]["kind"] == "plain" and mats["FL_Putz"]["extras"]["bump"] == [45, 0.6]
    assert mats["FL_Glas"]["alphaMode"] == "BLEND"


def test_bounding_box_y_up(glb):
    walls = positions(glb, "EG_Waende")
    src = BP.geo[("EG", "EG_Waende")]["v"]
    for k, (lo, hi) in enumerate(((0, 14.885), (0, 2.40), (0, 12.887))):     # x, height, north
        got = [(p[0], p[1], -p[2])[k] for p in walls]
        want = [p[(0, 2, 1)[k]] for p in src]
        assert min(got) == pytest.approx(min(want), abs=1e-5) and max(got) == pytest.approx(max(want), abs=1e-5)
        assert min(got) == pytest.approx(lo, abs=1e-5) and hi - 1e-5 <= max(got) < hi + 0.05
    roof = positions(glb, "Dach")
    assert abs(max(p[1] for p in roof) - 7.67) < 0.05
    assert min(p[0] for p in roof) < -1.4 and max(p[0] for p in roof) > 14.885 + 1.4      # gable overhangs


def test_haustuer_translation_is_its_pivot(glb):
    x, y, z = BP.pivot["EG_Haustuer"]
    assert node(glb, "EG_Haustuer")["translation"] == pytest.approx([x, z, -y])


def test_garden_extras(glb):
    ex = glb["gltf"]["scenes"][0]["extras"]
    lay = BP.garden
    assert len(ex["garden"]["no_grass"]) == len(lay.no_grass) and len(ex["garden"]["windrose"]) == 5
    assert len(ex["garden"]["shrubs"]) == len(lay.shrubs)
    assert ex["garden"]["DENSITY"] == house_core.DENSITY and ex["garden"]["FAR_DENS"] == house_core.FAR_DENS
    assert len(ex["room_lights"]) == 23 and ex["Z_OG"] == house_core.Z_OG
    assert ex["ROOM_LIGHT_H"] == house_core.ROOM_LIGHT_H
    assert ex["outside_lights"] == [list(p) for p in BP.outside_lights] and len(ex["outside_lights"]) == 8
    assert ex["lamp_lights"] == [list(p) for p in BP.lamp_lights] and len(ex["lamp_lights"]) == 1
    import fire                                                           # the fire component's layout
    assert len(ex["fires"]) == len(BP.fires) == 6 and ex["fires"][0]["tongues"] == fire.tongues(BP.fires[0]["w"], BP.fires[0]["h"], seed=0)
    assert all(set(f) >= {"base", "u", "w", "h", "d", "tongues"} for f in ex["fires"])
    assert ex["fire"]["profile"] == [list(p) for p in fire.profile()] and ex["fire"]["core"] == list(fire.CORE)
    assert ex["fire"]["outer"] == house_core.MAT_DEF["Feuer"] | {"rgba": list(house_core.MAT_DEF["Feuer"]["rgba"])}
    clump = glb["gltf"]["meshes"][node(glb, "GA_Grasbuschel")["mesh"]]["primitives"][0]
    f32 = lambda x: struct.unpack("<f", struct.pack("<f", x))[0]
    assert sorted(read(glb, clump["attributes"]["_H"])) == sorted(map(f32, lay.clump["h"]))


def test_smooth_objects_are_marked(glb):
    assert node(glb, "Kiesel")["extras"].get("smooth") and node(glb, "Aussenleuchten")["extras"].get("smooth")
    assert "smooth" not in node(glb, "EG_Waende")["extras"]


def test_open_lamp_cones_are_double_sided(glb):
    mats = {m["name"]: m for m in glb["gltf"]["materials"]}
    assert mats["FL_Eisen"].get("doubleSided") and mats["FL_Emaille"].get("doubleSided")
    assert not mats["FL_Putz"].get("doubleSided")


def test_export_creates_missing_directories(tmp_path):
    """A fresh clone has no web/public/ (it only holds the git-ignored .glb)."""
    out = tmp_path / "a" / "b" / "frechenlehen.glb"
    subprocess.run([sys.executable, str(ROOT / "code" / "export_gltf.py"), str(out)], check=True,
                   capture_output=True)
    assert out.read_bytes()[:4] == b"glTF"


def test_furniture_objects_are_marked(glb):
    for name in ("EG_Moebel", "OG_Moebel", "EG_Tisch", "EG_Stuehle"):
        assert node(glb, name)["extras"].get("furniture"), name
    assert "furniture" not in node(glb, "EG_Kueche")["extras"]
    assert node(glb, "OG_Moebel")["extras"]["collection"] == "OG"      # "Nur EG" hides it


def test_tour_keys_in_scene_extras(glb):
    import tour
    t = glb["gltf"]["scenes"][0]["extras"]["tour"]
    keys = tour.build_tour()
    assert t["fps"] == tour.FPS and len(t["frames"]) == len(keys)
    for got, want in zip(t["frames"][::97], keys[::97]):
        assert len(got) == 6 and all(abs(a - b) < 1e-4 for a, b in zip(got, want))


def test_desk_export(tmp_path):
    """--desk: the desk sub-model with its dimension lines; the screen panes are nodes translated to
    their pivot, their materials carry the image and the pane size."""
    out = tmp_path / "desk.glb"
    subprocess.run([sys.executable, str(ROOT / "code" / "export_gltf.py"), str(out), "--desk"], check=True)
    data = out.read_bytes()
    jlen = struct.unpack_from("<I", data, 12)[0]
    g = json.loads(data[20:20 + jlen])
    names = {n["name"] for n in g["nodes"]}
    assert {"Desk_Moebel", "Desk_Schreibtisch", "Desk_Handrad", "Desk_Geraete", "Desk_Bildschirm_L", "Desk_Bildschirm_R",
            "Desk_Stuehle"} == names
    bp = house_core.build_desk()
    house_core.build()
    lifted = {n["name"]: n["extras"]["lift"] for n in g["nodes"] if "lift" in n["extras"]}     # #10: the desk cranks up
    assert lifted == {o: pytest.approx(0.30) for o in ("Desk_Schreibtisch", "Desk_Geraete", "Desk_Bildschirm_L", "Desk_Bildschirm_R")}
    wheel = next(n for n in g["nodes"] if n["name"] == "Desk_Handrad")
    assert wheel["extras"]["crank"] == pytest.approx([1, 0, 0, 8 * math.pi])       # glTF axis, radians: 4 turns
    hx, hy, hz = bp.pivot["Desk_Handrad"]
    assert wheel["translation"] == pytest.approx([hx, hz, -hy])
    assert [n["name"] for n in g["nodes"] if "crank" in n["extras"]] == ["Desk_Handrad"]
    pane = next(n for n in g["nodes"] if n["name"] == "Desk_Bildschirm_L")
    x, y, z = bp.pivot["Desk_Bildschirm_L"]
    assert pane["translation"] == pytest.approx([x, z, -y])
    a = math.radians(bp.turn["Desk_Bildschirm_L"]) / 2                     # about glTF y = model z
    assert pane["rotation"] == pytest.approx([0, math.sin(a), 0, math.cos(a)])
    m = g["materials"][g["meshes"][pane["mesh"]]["primitives"][0]["material"]]
    assert m["extras"]["image"] == "textures/screen_a12.jpg" and m["extras"]["size"] == [0.697, 0.392]
    assert len(g["scenes"][0]["extras"]["dims"]) == len(bp.dims)


def test_bad_export(tmp_path):
    """--bad: the Bad Großeltern sub-model with its dimension lines, no Rundgang."""
    out = tmp_path / "bad.glb"
    subprocess.run([sys.executable, str(ROOT / "code" / "export_gltf.py"), str(out), "--bad"], check=True)
    data = out.read_bytes()
    jlen = struct.unpack_from("<I", data, 12)[0]
    g = json.loads(data[20:20 + jlen])
    names = {n["name"] for n in g["nodes"]}
    assert {"Bad_Waende", "Bad_Innentueren", "Bad_Sanitaer", "Bad_Fliesen", "Bad_Schrank", "Bad_Bodenbelag",
            "Bad_Boden", "Bad_Schiebetuer_hinten", "Bad_Schiebetuer_vorne"} == names
    slide = {n["name"]: n["extras"]["slide"] for n in g["nodes"] if "slide" in n["extras"]}   # glTF (x, z, -y)
    assert {k: [round(c, 3) + 0.0 for c in v] for k, v in slide.items()} == {
        "Bad_Schiebetuer_hinten": [-0.964, 0.0, 0.0], "Bad_Schiebetuer_vorne": [-0.964, 0.0, 0.0]}
    bp = house_core.build_bad()
    house_core.build()
    ex = g["scenes"][0]["extras"]
    assert len(ex["dims"]) == len(bp.dims) and "tour" not in ex


def test_kueche_export(tmp_path):
    """--kueche: the Küche sub-model with its dimension lines and the Wamsler's fire, no Rundgang."""
    out = tmp_path / "kueche.glb"
    subprocess.run([sys.executable, str(ROOT / "code" / "export_gltf.py"), str(out), "--kueche"], check=True)
    data = out.read_bytes()
    jlen = struct.unpack_from("<I", data, 12)[0]
    g = json.loads(data[20:20 + jlen])
    assert {n["name"] for n in g["nodes"]} == {"Kueche_Kueche", "Kueche_Herd", "Kueche_Haube", "Kueche_Waende"}
    bp = house_core.build_kueche()
    house_core.build()
    ex = g["scenes"][0]["extras"]
    assert len(ex["dims"]) == len(bp.dims) and "tour" not in ex and len(ex["fires"]) == 1


def test_gaeste_wc_export(tmp_path):
    """--gaeste-wc: the Gäste-WC sub-model with its dimension lines, no Rundgang, nothing sliding."""
    out = tmp_path / "gaeste_wc.glb"
    subprocess.run([sys.executable, str(ROOT / "code" / "export_gltf.py"), str(out), "--gaeste-wc"], check=True)
    data = out.read_bytes()
    jlen = struct.unpack_from("<I", data, 12)[0]
    g = json.loads(data[20:20 + jlen])
    assert {n["name"] for n in g["nodes"]} == {"GaesteWC_Waende", "GaesteWC_Innentueren", "GaesteWC_Sanitaer",
                                              "GaesteWC_Fliesen", "GaesteWC_Garderobe", "GaesteWC_WC_Tuer",
                                              "GaesteWC_Windfangtuer", "GaesteWC_Hintertuer", "GaesteWC_Fenster_Tueren"}
    assert not any("slide" in n["extras"] for n in g["nodes"])
    swing = {n["name"]: round(n["extras"]["swing"], 6) for n in g["nodes"] if "swing" in n["extras"]}   # radians about glTF y
    assert swing == {"GaesteWC_Hintertuer": round(math.pi / 2, 6), "GaesteWC_WC_Tuer": round(math.pi / 2, 6),
                     "GaesteWC_Windfangtuer": round(math.pi / 2, 6)}
    assert all("translation" in n for n in g["nodes"] if n["name"] in swing)       # origin at the hinge
    bp = house_core.build_gaeste_wc()
    house_core.build()
    ex = g["scenes"][0]["extras"]
    assert len(ex["dims"]) == len(bp.dims) and "tour" not in ex



def test_regal_export(tmp_path):
    """--regal: the "Schrank im Büro" sub-model with its wall pieces and dimension lines, no Rundgang,
    nothing sliding; the Büro door swings."""
    out = tmp_path / "regal.glb"
    subprocess.run([sys.executable, str(ROOT / "code" / "export_gltf.py"), str(out), "--regal"], check=True)
    data = out.read_bytes()
    jlen = struct.unpack_from("<I", data, 12)[0]
    g = json.loads(data[20:20 + jlen])
    assert {n["name"] for n in g["nodes"]} == {"Regal_Moebel", "Regal_Waende", "Regal_Fenster_Tueren",
                                              "Regal_Innentueren", "Regal_Laeden", "Regal_Buerotuer"}
    assert not any("slide" in n["extras"] for n in g["nodes"])
    swing = {n["name"]: round(n["extras"]["swing"], 6) for n in g["nodes"] if "swing" in n["extras"]}
    assert swing == {"Regal_Buerotuer": round(math.pi / 2, 6)}
    assert all("translation" in n for n in g["nodes"] if n["name"] in swing)       # origin at the hinge
    bp = house_core.build_regal()
    house_core.build()
    ex = g["scenes"][0]["extras"]
    assert len(ex["dims"]) == len(bp.dims) and "tour" not in ex

def test_routes_and_spots_in_scene_extras(glb):
    """The viewer's extra routes (all but the film's, which stays extras.tour) and its Standpunkte."""
    import tour
    ex = glb["gltf"]["scenes"][0]["extras"]
    assert [r["name"] for r in ex["routes"]] == [n for n, _ in tour.ROUTES[1:]]
    for r, (_, route) in zip(ex["routes"], tour.ROUTES[1:]):
        keys = tour.build_tour(route)
        assert len(r["frames"]) == len(keys)
        for got, want in zip(r["frames"][::97], keys[::97]):
            assert len(got) == 6 and all(abs(a - b) < 1e-4 for a, b in zip(got, want))
    assert [s["name"] for s in ex["spots"]] == [s[0] for s in tour.SPOTS]
    assert ex["spots"][0] == {"name": "Von Südosten", "group": "Außen", "entries": ["haus"],
                              "cam": [33, -24, 13], "at": [7.4, 6.4, 3.2], "fov": 28}


def test_variant_extras(glb):
    """Issue #5: the objects of one layout only carry extras.variant ("main" / "alt"), which the
    viewer's Erdgeschoss - Alternativ switches on; shared objects carry none."""
    gltf = glb["gltf"]
    got = {n["name"]: n["extras"]["variant"] for n in gltf["nodes"] if "variant" in n.get("extras", {})}
    assert got == house_core.build().variant and "alt" in got.values() and "main" in got.values()
