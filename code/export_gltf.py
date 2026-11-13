"""Frechenlehen – glTF backend: writes the Blueprint of house_core.py as a .glb for the web viewer.

Standard library only:  python3 code/export_gltf.py web/public/frechenlehen.glb
(`--ofen` / `--desk` / `--bad` / `--kueche` / `--gaeste-wc` / `--regal` / `--schrankbett` / `--gaestebad` / `--elternbad`: a
sub-model of house_core.build_ofen() / build_desk() / build_bad() / build_kueche() / build_gaeste_wc() /
build_regal() / build_schrankbett() / build_gaestebad() / build_elternbad() instead, with its dimension lines in scene.extras.dims)
- one node per GEO object (name = object name, translation = pivot, rotation = turn, extras.collection,
  extras.smooth for SMOOTH objects, extras.furniture for the furniture of the last stage)
- one primitive per material: POSITION, NORMAL, _RND (the Part's rnd), uint32 indices
- materials FL_<name>: a pbrMetallicRoughness approximation; the full MAT_DEF entry (+ paint)
  in extras, from which the viewer builds its own procedural material
- scene.extras: room lights, key constants, the garden layout, the Rundgang camera keys and the
  viewer's shorter routes (routes) and Standpunkte (spots) of
  tour.py (in z-up model coordinates)
- hidden node GA_Grasbuschel: the grass clump with _H (0 root .. 1 tip)
Axes: z-up model -> y-up glTF as (x, z, -y), like Blender's exporter.
"""
import json, math, os, struct, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fire, house_core, mesh_ops, tour  # noqa: E402


def yup(p):
    return (p[0], p[2], -p[1])


def unit(n):
    l = math.sqrt(mesh_ops.dot(n, n))
    return (n[0] / l, n[1] / l, n[2] / l) if l > 0 else (0.0, 0.0, 1.0)


def lin(rgb):
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return [f(v / 255) for v in rgb]


def jsonable(v):
    return [jsonable(x) for x in v] if isinstance(v, (tuple, list)) else v


def jsonable_dict(d):
    return {k: jsonable(v) for k, v in d.items()}


class Writer:
    def __init__(self):
        self.bin = bytearray()
        self.views, self.accessors = [], []

    def accessor(self, values, kind):
        """kind: 'VEC3' floats, 'SCALAR' floats or 'INDEX' uint32."""
        flat = [c for v in values for c in v] if kind == "VEC3" else list(values)
        fmt = "I" if kind == "INDEX" else "f"
        data = struct.pack("<%d%s" % (len(flat), fmt), *flat)
        self.views.append({"buffer": 0, "byteOffset": len(self.bin), "byteLength": len(data),
                           **({"target": 34963} if kind == "INDEX" else {"target": 34962})})
        self.bin += data + b"\0" * (-len(data) % 4)
        acc = {"bufferView": len(self.views) - 1, "componentType": 5125 if kind == "INDEX" else 5126,
               "count": len(values), "type": "SCALAR" if kind != "VEC3" else "VEC3"}
        if kind == "VEC3":                       # bounds of the stored float32 values
            f32 = struct.unpack("<%df" % len(flat), data)
            acc["min"] = [min(f32[k::3]) for k in range(3)]
            acc["max"] = [max(f32[k::3]) for k in range(3)]
        self.accessors.append(acc)
        return len(self.accessors) - 1


def object_primitives(g, parts, smooth, piv):
    """Per material: positions, normals, rnd and indices. One vertex per face corner; flat
    normals, or (smooth objects) normals averaged over equal positions within a Part.
    Returns ({material: (pos, nrm, rnd, idx)}, materials used by open Parts)."""
    prims, open_mats = {}, set()
    for first, n in parts:
        faces, is_open = mesh_ops.orient(g["v"], g["f"][first:first + n])
        if is_open:
            open_mats.update(g["m"][first:first + n])
        fn = [mesh_ops.newell([g["v"][i] for i in f]) for f in faces]
        if smooth:
            acc = {}
            for f, nv in zip(faces, fn):
                for i in f:
                    k = g["v"][i]
                    a = acc.get(k, (0.0, 0.0, 0.0))
                    acc[k] = (a[0] + nv[0], a[1] + nv[1], a[2] + nv[2])
        for j, (f, nv) in enumerate(zip(faces, fn)):
            mat, r = g["m"][first + j], g["r"][first + j]
            pos, nrm, rnd, idx = prims.setdefault(mat, ([], [], [], []))
            base = len(pos)
            pts = [g["v"][i] for i in f]
            for p in pts:
                pos.append(yup((p[0] - piv[0], p[1] - piv[1], p[2] - piv[2])))
                nrm.append(yup(unit(acc[p] if smooth else nv)))
                rnd.append(r)
            for t in mesh_ops.triangulate(pts):
                idx += [base + t[0], base + t[1], base + t[2]]
    return prims, open_mats


def material(name, d, paint):
    base = d.get("rgba") or (*[(a + b) / 2 for a, b in zip(*(d.get("wood") or d["speck"])[:2])], 1)
    base = list(base)
    if name in paint:
        base = lin(paint[name]) + [base[3]]
    kind = "wood" if "wood" in d else "speck" if "speck" in d else "plain"
    m = {"name": "FL_" + name,
         "pbrMetallicRoughness": {"baseColorFactor": base, "metallicFactor": d.get("metal", 0.0),
                                  "roughnessFactor": d.get("rough", 0.8)},
         "extras": {"kind": kind, **{k: jsonable(v) for k, v in d.items()}}}
    if name in paint:
        m["extras"]["paint"] = list(paint[name])
    if "alpha" in d:
        m["alphaMode"] = "BLEND"
    if "emit" in d:
        m["emissiveFactor"] = list(base[:3])
    return m


def export(path, bp=None):
    bp = bp or house_core.build()
    w = Writer()
    names = list(bp.mat_def)
    mats = [material(n, bp.mat_def[n], bp.paint) for n in names]
    nodes, meshes = [], []
    for (coll, name), g in bp.geo.items():
        piv, turn = bp.pivot.get(name, (0.0, 0.0, 0.0)), (bp.turn or {}).get(name, 0.0)
        if turn:                                             # stored unturned, the node turns it
            g = {**g, "v": [house_core.local(p, piv, turn) for p in g["v"]]}
        prims, open_mats = object_primitives(g, bp.parts[(coll, name)], name in bp.smooth, (0.0, 0.0, 0.0) if turn else piv)
        for m in open_mats:
            mats[names.index(m)]["doubleSided"] = True
        meshes.append({"name": name, "primitives": [
            {"attributes": {"POSITION": w.accessor(pos, "VEC3"), "NORMAL": w.accessor(nrm, "VEC3"),
                            "_RND": w.accessor(rnd, "SCALAR")},
             "indices": w.accessor(idx, "INDEX"), "material": names.index(m)}
            for m, (pos, nrm, rnd, idx) in prims.items()]})
        node = {"name": name, "mesh": len(meshes) - 1, "extras": {"collection": coll}}
        if name in bp.smooth:
            node["extras"]["smooth"] = True
        if name in bp.furniture:
            node["extras"]["furniture"] = True
        if name in (bp.variant or {}):                       # one layout only: "main" / "alt" (Erdgeschoss - Alternativ)
            node["extras"]["variant"] = bp.variant[name]
        if name in bp.pivot:
            node["translation"] = list(yup(piv))
        if name in (bp.slide or {}):                         # the sub-model viewer rolls it there and back
            node["extras"]["slide"] = list(yup(bp.slide[name]))
        if name in (bp.swing or {}):                         # the viewer swings it about its hinge (glTF y)
            node["extras"]["swing"] = math.radians(bp.swing[name])
        if name in (bp.lift or {}):                          # the viewer lifts it (glTF y) with the others
            node["extras"]["lift"] = bp.lift[name]
        if name in (bp.crank or {}):                         # and turns it about its pivot meanwhile
            axis, deg = bp.crank[name]
            node["extras"]["crank"] = [*yup(axis), math.radians(deg)]
        if name in (bp.fold or {}):                          # and folds about its own hinge meanwhile
            hinge, axis, deg = bp.fold[name]
            node["extras"]["fold"] = [*yup([h - q for h, q in zip(hinge, piv)]), *yup(axis), math.radians(deg)]
        if turn:                                             # about the vertical: glTF y
            node["rotation"] = [0.0, math.sin(math.radians(turn) / 2), 0.0, math.cos(math.radians(turn) / 2)]
        nodes.append(node)
    extras = {"coordinates": "z-up model metres (x east, y north); glTF positions are (x, z, -y)"}
    if bp.garden:                                            # the house (not the Ofen sub-model)
        # grass clump (hidden; instanced by the viewer)
        cl = bp.garden.clump
        vn = [(0.0, 0.0, 0.0)] * len(cl["v"])
        idx = []
        for f in cl["f"]:
            nv = mesh_ops.newell([cl["v"][i] for i in f])
            for i in f:
                vn[i] = tuple(a + b for a, b in zip(vn[i], nv))
            idx += [f[0], f[1], f[2], f[0], f[2], f[3]]
        meshes.append({"name": "GA_Grasbuschel", "primitives": [
            {"attributes": {"POSITION": w.accessor([yup(p) for p in cl["v"]], "VEC3"),
                            "NORMAL": w.accessor([yup(unit(n)) for n in vn], "VEC3"),
                            "_H": w.accessor(cl["h"], "SCALAR")},
             "indices": w.accessor(idx, "INDEX")}]})
        nodes.append({"name": "GA_Grasbuschel", "mesh": len(meshes) - 1,
                      "extras": {"collection": "Garten", "hidden": True}})
        lay = bp.garden
        extras.update({
            "room_lights": jsonable(bp.room_lights), "ROOM_LIGHT_H": house_core.ROOM_LIGHT_H,
            "outside_lights": jsonable(bp.outside_lights),
            "lamp_lights": jsonable(bp.lamp_lights), "wall_lights": jsonable(bp.wall_lights),
            "Z_OG": house_core.Z_OG, "W_OUT": house_core.W_OUT, "D_OUT": house_core.D_OUT,
            "RIDGE_Z": house_core.RIDGE_Z,
            "garden": {"ground": jsonable(lay.ground), "no_grass": jsonable(lay.no_grass),
                       "windrose": jsonable(lay.windrose), "shrubs": jsonable(lay.shrubs),
                       "DENSITY": house_core.DENSITY, "NEAR": house_core.NEAR, "FAR": house_core.FAR,
                       "FAR_DENS": house_core.FAR_DENS, "HOUSE_C": jsonable(house_core.HOUSE_C),
                       "CELL": house_core.CELL},
            "tour": {"fps": tour.FPS, "frames": [[round(v, 4) for v in k] for k in tour.build_tour()]},
            "routes": [{"name": n, "frames": [[round(v, 4) for v in k] for k in tour.build_tour(r)]}
                       for n, r in tour.ROUTES[1:]],             # the viewer's shorter walks
            "spots": [{"name": n, "group": g, "entries": list(e), "cam": list(c), "at": list(a), "fov": f}
                      for n, g, e, c, a, f in tour.SPOTS],       # the viewer's Standpunkte
        })
    if bp.dims:
        extras["dims"] = jsonable(bp.dims)
    if bp.fires:                                             # the fire component (code/fire.py, fire.js)
        md = bp.mat_def
        extras["fires"] = [{**jsonable_dict(f), "tongues": fire.tongues(f["w"], f["h"], seed=i)}
                           for i, f in enumerate(bp.fires)]
        extras["fire"] = {"profile": jsonable(fire.profile()), "core": list(fire.CORE),
                          "outer": jsonable_dict(md["Feuer"]), "inner": jsonable_dict(md["FeuerKern"])}
    gltf = {"asset": {"version": "2.0", "generator": "frechenlehen export_gltf.py"},
            "scene": 0, "scenes": [{"name": "Frechenlehen", "nodes": list(range(len(nodes))), "extras": extras}],
            "nodes": nodes, "meshes": meshes, "materials": mats,
            "accessors": w.accessors, "bufferViews": w.views, "buffers": [{"byteLength": len(w.bin)}]}
    js = json.dumps(gltf, separators=(",", ":")).encode()
    js += b" " * (-len(js) % 4)
    total = 12 + 8 + len(js) + 8 + len(w.bin)
    Path(path).parent.mkdir(parents=True, exist_ok=True)      # fresh clone: no web/public/ yet
    tmp = f"{path}.{os.getpid()}.tmp"                          # atomic: a reader (the dev server) never
    with open(tmp, "wb") as fh:                               # sees a half-written file
        fh.write(struct.pack("<4sII", b"glTF", 2, total))
        fh.write(struct.pack("<I4s", len(js), b"JSON")); fh.write(js)
        fh.write(struct.pack("<I4s", len(w.bin), b"BIN\0")); fh.write(w.bin)
    os.replace(tmp, path)
    return total


if __name__ == "__main__":
    sub = {"--ofen": house_core.build_ofen, "--desk": house_core.build_desk,
           "--bad": house_core.build_bad, "--kueche": house_core.build_kueche,
           "--gaeste-wc": house_core.build_gaeste_wc, "--regal": house_core.build_regal,
           "--schrankbett": house_core.build_schrankbett, "--gaestebad": house_core.build_gaestebad,
           "--elternbad": house_core.build_elternbad}.get(next((a for a in sys.argv[2:] if a.startswith("--")), None))
    size = export(sys.argv[1], sub and sub())
    print(f"wrote {sys.argv[1]} ({size / 1e6:.1f} MB)")
