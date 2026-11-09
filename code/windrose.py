"""Compass rose (Windrose) on the ground next to the house. +Y = Norden, +X = Osten.

Lives in its own collection "Windrose" so build_house.py never touches it.
Run inside Blender: exec(open(".../code/windrose.py").read())  – re-running replaces only the rose.
"""
import bpy, importlib, math, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(bpy.data.filepath) or PROJECT, "code"))  # this clone: the open .blend's folder (unsaved, headless test: snapshot.py's PROJECT)
import house_core; importlib.reload(house_core)        # pick up core edits in a long session
from house_core import WINDROSE_CENTER as CENTER, WINDROSE_R as R   # SW of the house; main point length


def mat(name, rgba):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    m.diffuse_color = rgba
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = rgba
    return m


def main():
    c = bpy.data.collections.get("Windrose")
    if c:
        for ob in list(c.objects):
            bpy.data.objects.remove(ob)
    else:
        c = bpy.data.collections.new("Windrose")
        bpy.context.scene.collection.children.link(c)

    red, dark, light = mat("WR_Rot", (0.8, 0.05, 0.05, 1)), mat("WR_Dunkel", (0.1, 0.1, 0.12, 1)), \
        mat("WR_Hell", (0.9, 0.9, 0.9, 1))
    cx, cy, z = CENTER

    # star: 4 main points (N red) + 4 short diagonal points, each split into a dark and light half
    verts, faces, mats = [], [], []
    for i in range(8):
        a = math.radians(90 - i * 45)                   # 0 = north, clockwise
        length, width = (R, 0.45) if i % 2 == 0 else (R * 0.55, 0.3)
        tip = (cx + length * math.cos(a), cy + length * math.sin(a), z)
        l = (cx + width * math.cos(a + math.pi / 2), cy + width * math.sin(a + math.pi / 2), z)
        r = (cx + width * math.cos(a - math.pi / 2), cy + width * math.sin(a - math.pi / 2), z)
        for side, m in ((l, 1 if i else 0), (r, 2 if i else 0)):
            n = len(verts)
            verts += [(cx, cy, z + (0.01 if i % 2 == 0 else 0)), tip, side]
            faces.append((n, n + 1, n + 2))
            mats.append(m)
    me = bpy.data.meshes.new("Windrose")
    me.from_pydata(verts, [], faces)
    for m in (red, dark, light):
        me.materials.append(m)
    me.polygons.foreach_set("material_index", mats)
    for p in me.polygons:                               # make all faces point up
        if p.normal.z < 0:
            p.flip()
    c.objects.link(bpy.data.objects.new("Windrose", me))

    # labels
    for label, a in (("N", 90), ("O", 0), ("S", -90), ("W", 180)):
        cu = bpy.data.curves.new("WR_" + label, "FONT")
        cu.body, cu.size, cu.align_x, cu.align_y = label, 1.2, "CENTER", "CENTER"
        cu.extrude = 0.02
        ob = bpy.data.objects.new("WR_" + label, cu)
        d = R + 0.9
        ob.location = (cx + d * math.cos(math.radians(a)), cy + d * math.sin(math.radians(a)), z)
        ob.data.materials.append(red if label == "N" else dark)
        c.objects.link(ob)


main()
