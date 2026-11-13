"""Frechenlehen – flickering fire, as a reusable component.

A fire is a flame bed (house_core.FIRES: base = centre of the bed in the flame plane, u = unit
along its width, w, h, d); the stoves record theirs, so the same component burns in the Stube
Ofen and both workshop stoves, scaled to each bed. `tongues(w, h)` lays out the flame tongues
(pure Python: the glTF export hands the same layout to the viewer, web/src/fire.js).

In Blender this script builds collection "Feuer": per tongue a flat teardrop flame (outer, and an
inner brighter core; pure emission in the colours of MAT_DEF "Feuer" / "FeuerKern") whose height, width and sway flicker through F-curve
noise, plus a flickering warm light per fire. Re-running replaces the collection. Run after
build_house (same rebuild order as the others):
    exec(open(".../code/fire.py").read())
"""
import importlib, math, os, random, sys

try:
    import bpy
except ImportError:                       # imported by export_gltf.py / the tests: layout only
    bpy = None

SPACING = 0.06                            # one tongue per 6 cm of bed width
CORE = (0.55, 0.60)                       # inner flame: share of the tongue's width and height


def tongues(w, h, seed=0):
    """Flame tongues for a bed w wide, h high: dicts u (centre along the width), w, h, phase
    (radians) and speed (relative flicker rate). Taller in the middle, slightly irregular."""
    rng = random.Random(seed)
    n = max(2, round(w / SPACING))
    tw = w / n * 1.5
    out = []
    for i in range(n):
        u = -w / 2 + w * (i + 0.5) / n + rng.uniform(-0.15, 0.15) * w / n
        u = max(-w / 2 + tw / 2, min(w / 2 - tw / 2, u))
        mid = 1 - abs(u) / (w / 2)
        out.append(dict(u=u, w=tw, h=h * (0.45 + 0.55 * mid) * rng.uniform(0.82, 1.0),
                        phase=2 * math.pi * (i + rng.random()) / n, speed=rng.uniform(0.8, 1.3)))
    return out


def profile(k=12):
    """Teardrop outline of a unit flame (x across, z up): round bottom, pointed top."""
    s = [i / k for i in range(k + 1)]
    hw = [0.5 * math.sin(math.pi * (0.12 + 0.88 * t)) ** 0.5 * (1 - t) ** 0.6 for t in s]
    return [(-x, t) for x, t in zip(hw, s)] + [(x, t) for x, t in zip(hw[::-1], s[::-1])][1:-1]


# ---------------------------------------------------------------- Blender
def _collection(name):
    c = bpy.data.collections.get(name)
    if c:
        for ob in list(c.objects):
            data, store = ob.data, bpy.data.meshes if ob.type == "MESH" else bpy.data.lights
            bpy.data.objects.remove(ob)
            if data and data.users == 0:
                store.remove(data)
    else:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def _flame_mesh(name, d):
    pts = profile()
    n = len(pts)
    v = [(x, -d / 2, z) for x, z in pts] + [(x, d / 2, z) for x, z in pts]
    f = [list(range(n))[::-1], list(range(n, 2 * n))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.update()
    return me


def _noise(owner, path, index, strength, scale, phase):
    from bpy_extras import anim_utils
    owner.keyframe_insert(path, index=index, frame=1)          # index -1: a single value (energy)
    cb = anim_utils.action_get_channelbag_for_slot(owner.animation_data.action, owner.animation_data.action_slot)
    m = cb.fcurves.find(path, index=max(index, 0)).modifiers.new("NOISE")
    m.strength, m.scale, m.phase, m.depth = strength, scale, phase, 1


def _flame_material(name, d):
    """Pure emission (no diffuse: the fire light must not wash the flames out)."""
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    em, out = nt.nodes.new("ShaderNodeEmission"), nt.nodes.new("ShaderNodeOutputMaterial")
    em.inputs["Color"].default_value = d["rgba"]
    em.inputs["Strength"].default_value = d["emit"]
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return m


def burn(coll, f, i, outer, core):
    """One fire: tongues (outer + core) on bed f, and a flickering light in front of it."""
    (bx, by, bz), (ux, uy) = f["base"], f["u"]
    nx, ny = -uy, ux                                         # towards the viewer
    meshes = {}
    for kind, mat in (("", outer), ("_Kern", core)):
        meshes[kind] = _flame_mesh(f"Flamme_{i}{kind}", f["d"] * 0.5)
        meshes[kind].materials.append(mat)
    for j, t in enumerate(tongues(f["w"], f["h"], seed=i)):
        for kind, sw, sh, dn in (("", 1.0, 1.0, 0.0), ("_Kern", *CORE, f["d"] * 0.3)):
            ob = bpy.data.objects.new(f"Flamme_{i}_{j}{kind}", meshes[kind])
            ob.location = (bx + ux * t["u"] + nx * dn, by + uy * t["u"] + ny * dn, bz)
            ob.rotation_euler = (0, 0, math.atan2(uy, ux))
            ob.scale = (t["w"] * sw, 1, t["h"] * sh)
            coll.objects.link(ob)
            p, sp = t["phase"] * 10 + (7 if kind else 0), t["speed"]
            _noise(ob, "scale", 2, 0.55 * t["h"] * sh, 4.0 / sp, p)          # leaping height
            _noise(ob, "scale", 0, 0.25 * t["w"] * sw, 6.0 / sp, p + 3)      # breathing width
            _noise(ob, "rotation_euler", 1, 0.25, 8.0 / sp, p + 5)          # sway
    ld = bpy.data.lights.new(f"Feuerlicht_{i}", "POINT")
    ld.color, ld.energy, ld.shadow_soft_size = (1.0, 0.55, 0.22), 25 * f["w"], 0.1
    ld.use_shadow, ld.specular_factor = False, 0.0          # no highlight disc on the stove glass
    lo = bpy.data.objects.new(f"Feuerlicht_{i}", ld)
    lo.location = (bx + nx * 0.45, by + ny * 0.45, bz + f["h"] * 0.5)    # in the room, off the glass
    coll.objects.link(lo)
    _noise(ld, "energy", -1, 20 * f["w"], 3.0, i * 11.0)


def main():
    sys.path.insert(0, os.path.join(os.path.dirname(bpy.data.filepath) or PROJECT, "code"))  # this clone: the open .blend's folder (unsaved, headless test: snapshot.py's PROJECT)
    import ofen, desk, bad, kueche, gaeste_wc, regal, schrankbett, gaestebad, house_core
    importlib.reload(ofen); importlib.reload(desk); importlib.reload(bad); importlib.reload(kueche); importlib.reload(gaeste_wc); importlib.reload(regal); importlib.reload(schrankbett); importlib.reload(gaestebad); importlib.reload(house_core)    # pick up core edits in a long session
    bp = house_core.build()
    coll = _collection("Feuer")
    outer = _flame_material("Flamme", house_core.MAT_DEF["Feuer"])
    core = _flame_material("Flammenkern", house_core.MAT_DEF["FeuerKern"])
    for i, f in enumerate(bp.fires):
        burn(coll, f, i, outer, core)
    return len(bp.fires)


if bpy is not None:
    N_FIRES = main()
