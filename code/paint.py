"""Colour scheme (RAL) + white cross boards on the shutters. Only edits materials and adds the
object "Laeden_Querbretter"; the house geometry (incl. manual edits) stays untouched.
Run inside Blender: exec(open(".../code/paint.py").read())  – re-running is safe.

  Fassade      RAL 9010 Reinweiß     Fenster  RAL 9010 Reinweiß
  Fensterläden RAL 5014 Taubenblau (weiße Querbretter), Ofenkacheln ebenso
  Türen bleiben Naturholz (Materialien aus build_house.py)
"""
import bpy, bmesh

RAL = {"9010": (241, 236, 225), "5014": (99, 125, 150)}


def lin(rgb):
    f = lambda c: c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    return tuple(f(v / 255) for v in rgb) + (1.0,)


def set_color(mat_name, rgb):
    m = bpy.data.materials[mat_name]
    col = lin(rgb)
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = col
    m.diffuse_color = col


def cross_boards():
    """Two white boards across every shutter panel (on its outer face)."""
    c = bpy.data.collections["FL_EG"]
    old = bpy.data.objects.get("Laeden_Querbretter")
    if old:
        bpy.data.objects.remove(old)
    verts, faces = [], []
    for name in ("EG_Laeden", "OG_Laeden"):
        ob = bpy.data.objects.get(name)
        if not ob:
            continue
        bm = bmesh.new(); bm.from_mesh(ob.data)
        bm.verts.ensure_lookup_table()
        seen = set()
        for v in bm.verts:                      # one island = one shutter box
            if v.index in seen:
                continue
            stack, isl = [v], []
            while stack:
                w = stack.pop()
                if w.index in seen:
                    continue
                seen.add(w.index); isl.append(w.co.copy())
                stack += [e.other_vert(w) for e in w.link_edges]
            xs, ys, zs = [p.x for p in isl], [p.y for p in isl], [p.z for p in isl]
            x0, x1, y0, y1, z0, z1 = min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)
            thin_x = (x1 - x0) < (y1 - y0)       # shutter lies in a YZ plane (east/west wall)
            h = z1 - z0
            for zc in (z0 + 0.18 * h, z1 - 0.18 * h):
                bz0, bz1 = zc - 0.05, zc + 0.05
                if thin_x:                       # boards on both faces: outer side is unknown here
                    bx = [(x0 - 0.012, x0), (x1, x1 + 0.012)]
                    boxes = [(a, b, y0, y1, bz0, bz1) for a, b in bx]
                else:
                    boxes = [(x0, x1, a, b, bz0, bz1) for a, b in [(y0 - 0.012, y0), (y1, y1 + 0.012)]]
                for bx0, bx1, by0, by1, zz0, zz1 in boxes:
                    n = len(verts)
                    verts += [(x, y, z) for z in (zz0, zz1)
                              for x, y in ((bx0, by0), (bx1, by0), (bx1, by1), (bx0, by1))]
                    faces += [(n, n + 3, n + 2, n + 1), (n + 4, n + 5, n + 6, n + 7),
                              (n, n + 1, n + 5, n + 4), (n + 1, n + 2, n + 6, n + 5),
                              (n + 2, n + 3, n + 7, n + 6), (n + 3, n, n + 4, n + 7)]
        bm.free()
    me = bpy.data.meshes.new("Laeden_Querbretter")
    me.from_pydata(verts, [], faces)
    me.materials.append(bpy.data.materials["FL_Rahmen"])     # RAL 9010 white
    c.objects.link(bpy.data.objects.new("Laeden_Querbretter", me))
    return len(faces) // 6


def main():
    set_color("FL_Putz", RAL["9010"])
    set_color("FL_Rahmen", RAL["9010"])
    set_color("FL_Laden", RAL["5014"])
    set_color("FL_Kachel", RAL["5014"])
    # shed battens used the shutter material – keep them wood
    shed = bpy.data.objects.get("Schuppen_Holz")
    if shed:
        for i, m in enumerate(shed.data.materials):
            if m and m.name == "FL_Laden":
                shed.data.materials[i] = bpy.data.materials["FL_Holz"]
    return cross_boards()


N_BOARDS = main()
