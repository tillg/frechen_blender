"""Frechenlehen – Blender backend: turns the Blueprint of house_core.py into the scene.

Materials (node trees), meshes, room names (font curves), hidden reference plans, sun, world
and camera. All geometry, constants and MAT_DEF live in house_core.py.
Run inside Blender (e.g. via the Blender MCP server):  exec(open(".../code/build_house.py").read())
Re-running replaces the "Haus" collection.
"""
import bpy, importlib, math, os, sys
from mathutils import Vector

PROJECT = os.path.dirname(bpy.data.filepath) or PROJECT   # this clone: the open .blend's folder (unsaved, headless test: snapshot.py's)
sys.path.insert(0, os.path.join(PROJECT, "code"))
import ofen, desk, bad, kueche, gaeste_wc, regal, schrankbett, gaestebad, house_core; importlib.reload(ofen); importlib.reload(desk); importlib.reload(bad); importlib.reload(kueche); importlib.reload(gaeste_wc); importlib.reload(regal); importlib.reload(schrankbett); importlib.reload(gaestebad); importlib.reload(house_core)  # pick up core edits in a long session
from house_core import Z_OG, ROOM_NAMES


MAT = {}


def make_materials(mat_def):
    for name, d in mat_def.items():
        m = bpy.data.materials.get("FL_" + name) or bpy.data.materials.new("FL_" + name)
        m.use_nodes = True
        nt = m.node_tree
        nt.nodes.clear()
        N = nt.nodes.new
        L = nt.links.new
        out = N("ShaderNodeOutputMaterial")
        bsdf = N("ShaderNodeBsdfPrincipled")
        bsdf.name = "Principled BSDF"
        L(bsdf.outputs["BSDF"], out.inputs["Surface"])
        rgba = d.get("rgba") or (*[(a + b) / 2 for a, b in zip(*(d.get("wood") or d["speck"])[:2])], 1)
        m.diffuse_color = rgba
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = d.get("rough", 0.8)
        bsdf.inputs["Metallic"].default_value = d.get("metal", 0.0)
        if "alpha" in d:
            bsdf.inputs["Alpha"].default_value = d["alpha"]
            m.surface_render_method = "BLENDED"
        if "emit" in d:
            bsdf.inputs["Emission Color"].default_value = rgba
            bsdf.inputs["Emission Strength"].default_value = d["emit"]
        coord = N("ShaderNodeTexCoord")
        height = None
        if "wood" in d or "speck" in d:
            c1, c2 = (d.get("wood") or d["speck"])[:2]
            mp = N("ShaderNodeMapping")
            if "wood" in d:
                ax = d["wood"][2]
                mp.inputs["Scale"].default_value = [1.5 if a == ax else 60.0 for a in "xyz"]
            else:
                mp.inputs["Scale"].default_value = [d["speck"][2]] * 3
            noise = N("ShaderNodeTexNoise")
            noise.inputs["Detail"].default_value = 6
            noise.inputs["Roughness"].default_value = 0.6
            ramp = N("ShaderNodeValToRGB")
            ramp.color_ramp.elements[0].position, ramp.color_ramp.elements[1].position = 0.35, 0.68
            ramp.color_ramp.elements[0].color = (*c1, 1)
            ramp.color_ramp.elements[1].color = (*c2, 1)
            attr = N("ShaderNodeAttribute"); attr.attribute_name = "rnd"
            val = N("ShaderNodeMath"); val.operation = "MULTIPLY_ADD"
            val.inputs[1].default_value, val.inputs[2].default_value = 0.5, 0.75
            hue = N("ShaderNodeMath"); hue.operation = "MULTIPLY_ADD"
            hue.inputs[1].default_value = d.get("hue", 0.0)
            hue.inputs[2].default_value = 0.5 - d.get("hue", 0.0) / 2
            hs = N("ShaderNodeHueSaturation")
            L(coord.outputs["Object"], mp.inputs["Vector"])
            L(mp.outputs["Vector"], noise.inputs["Vector"])
            L(noise.outputs["Fac"], ramp.inputs["Fac"])
            L(ramp.outputs["Color"], hs.inputs["Color"])
            L(attr.outputs["Fac"], val.inputs[0]); L(val.outputs[0], hs.inputs["Value"])
            L(attr.outputs["Fac"], hue.inputs[0]); L(hue.outputs[0], hs.inputs["Hue"])
            L(hs.outputs["Color"], bsdf.inputs["Base Color"])
            if "wood" in d:
                height, strength = noise.outputs["Fac"], 0.15
        if "bump" in d:
            bn = N("ShaderNodeTexNoise")
            bn.inputs["Scale"].default_value = d["bump"][0]
            bn.inputs["Detail"].default_value = 8
            L(coord.outputs["Object"], bn.inputs["Vector"])
            height, strength = bn.outputs["Fac"], d["bump"][1]
        if height:
            bump = N("ShaderNodeBump")
            bump.inputs["Strength"].default_value = strength
            bump.inputs["Distance"].default_value = 0.01
            L(height, bump.inputs["Height"])
            L(bump.outputs["Normal"], bsdf.inputs["Normal"])
        if "image" in d:                       # screen: object space from the pivot, x/w and z/h
            mp = N("ShaderNodeMapping")
            mp.inputs["Scale"].default_value = (1 / d["size"][0], 1, 1 / d["size"][1])
            sep, comb = N("ShaderNodeSeparateXYZ"), N("ShaderNodeCombineXYZ")
            tex = N("ShaderNodeTexImage"); tex.extension = "CLIP"
            tex.image = bpy.data.images.load(PROJECT + "/web/public/" + d["image"], check_existing=True)
            L(coord.outputs["Object"], mp.inputs["Vector"]); L(mp.outputs["Vector"], sep.inputs[0])
            L(sep.outputs["X"], comb.inputs["X"]); L(sep.outputs["Z"], comb.inputs["Y"])
            L(comb.outputs[0], tex.inputs["Vector"])
            L(tex.outputs["Color"], bsdf.inputs["Base Color"])
            L(tex.outputs["Color"], bsdf.inputs["Emission Color"])
        MAT[name] = m


# ---------------------------------------------------------------- geometry accumulator

def build_room_names():
    """Names in cream letters on the floor (text converted to mesh, 0.40 m high)."""
    for coll_name in ("EG", "OG"):
        z = (0.0 if coll_name == "EG" else Z_OG) + 0.0153
        me_all = []
        for name, c, x, y, rot in ROOM_NAMES:
            if c != coll_name:
                continue
            cu = bpy.data.curves.new("tmp_name", "FONT")
            cu.body, cu.size, cu.align_x, cu.align_y, cu.extrude = name, 0.40, "CENTER", "CENTER", 0.0008
            tmp = bpy.data.objects.new("tmp_name", cu)
            tmp.location, tmp.rotation_euler.z = (x, y, z), math.radians(rot)
            bpy.context.scene.collection.objects.link(tmp)
            me_all.append(tmp)
        bpy.context.view_layer.update()
        dg = bpy.context.evaluated_depsgraph_get()
        import bmesh
        bm = bmesh.new()
        for tmp in me_all:
            m = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
            m.transform(tmp.matrix_world)
            bm.from_mesh(m)
            bpy.data.meshes.remove(m)
            cu = tmp.data
            bpy.data.objects.remove(tmp)
            bpy.data.curves.remove(cu)
        me = bpy.data.meshes.new(coll_name + "_Raumnamen")
        bm.to_mesh(me); bm.free()
        me.materials.append(MAT["Schrift"])
        coll(coll_name).objects.link(bpy.data.objects.new(coll_name + "_Raumnamen", me))


# ---------------------------------------------------------------- reference plans (hidden)
PLANS = os.path.join(PROJECT, "input", "2026-11-03 input")   # current plans (LOG.md)
PT = 28.3465                                                  # PDF points per metre at 1:100


def reference_plane(name, img, top_left, z):
    path = os.path.join(PLANS, img)
    im = bpy.data.images.load(path, check_existing=True)
    w, h = 1190.4 / PT, 841.68 / PT                    # A3 landscape at 1:100 in metres
    cx, cy = top_left[0] + w / 2, top_left[1] - h / 2
    me = bpy.data.meshes.new(name)
    me.from_pydata([(cx - w / 2, cy - h / 2, z), (cx + w / 2, cy - h / 2, z),
                    (cx + w / 2, cy + h / 2, z), (cx - w / 2, cy + h / 2, z)], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new()
    for i, co in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[i].uv = co
    if bpy.data.materials.get(name):                   # left over from the last build: keep the name
        bpy.data.materials.remove(bpy.data.materials[name])
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    tex = nt.nodes.new("ShaderNodeTexImage"); tex.image = im
    nt.links.new(tex.outputs["Color"], nt.nodes["Principled BSDF"].inputs["Base Color"])
    me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    coll("Referenz").objects.link(ob)


def build_references():
    # page top-left in world coords: the outer SW corner sits at pt (388.67, 578.71) on the EG
    # sheet and at (383.15, 649.27) on the OG sheet; the OG drawing is offset by 0.195 / 0.57 m
    # against the EG walls
    reference_plane("Ref_Grundriss_EG", "grundriss_eg.png", (-388.67 / PT, 578.71 / PT), 0.02)
    reference_plane("Ref_Grundriss_OG", "grundriss_og.png",
                    (-383.15 / PT + 0.195, 649.27 / PT + 0.57), Z_OG + 0.02)


# ---------------------------------------------------------------- scene assembly
ROOT = "Haus"
SUBS = ["EG", "OG", "Dach", "Balkone", "Umgebung", "Referenz"]


def coll(name):
    return bpy.data.collections[name if name == ROOT else "FL_" + name]


def reset_collections():
    old = bpy.data.collections.get(ROOT)
    if old:
        for c in [old] + list(old.children_recursive):
            for ob in list(c.objects):
                me = ob.data
                bpy.data.objects.remove(ob)
                if me and me.users == 0:
                    bpy.data.meshes.remove(me)
        for c in list(old.children_recursive):
            bpy.data.collections.remove(c)
        bpy.data.collections.remove(old)
    root = bpy.data.collections.new(ROOT)
    bpy.context.scene.collection.children.link(root)
    for s in SUBS:
        root.children.link(bpy.data.collections.new("FL_" + s))


def flush_geometry(bp):
    import bmesh
    for (c, name), g in bp.geo.items():
        me = bpy.data.meshes.new(name)
        piv, turn = bp.pivot.get(name, (0, 0, 0)), (bp.turn or {}).get(name, 0.0)
        me.from_pydata([house_core.local(p, piv, turn) for p in g["v"]], [], g["f"])
        mats = sorted(set(g["m"]))
        for m in mats:
            me.materials.append(MAT[m])
        me.polygons.foreach_set("material_index", [mats.index(m) for m in g["m"]])
        me.attributes.new("rnd", "FLOAT", "FACE").data.foreach_set("value", g["r"])
        bm = bmesh.new(); bm.from_mesh(me)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(me); bm.free()
        if name in bp.smooth:
            me.shade_smooth()
        ob = bpy.data.objects.new(name, me)
        ob.location = piv
        ob.rotation_euler.z = math.radians(turn)
        coll(c).objects.link(ob)


def setup_scene():
    sc = bpy.context.scene
    cube = bpy.data.objects.get("Cube")
    if cube and cube.data.name == "Cube":
        bpy.data.objects.remove(cube)
    # sun
    sun = bpy.data.objects.get("FL_Sonne")
    if not sun:
        sun = bpy.data.objects.new("FL_Sonne", bpy.data.lights.new("FL_Sonne", "SUN"))
        sc.collection.objects.link(sun)
    sun.data.energy = 4.0
    sun.data.angle = math.radians(2)
    sun.rotation_euler = (math.radians(50), 0, math.radians(35))
    old_light = bpy.data.objects.get("Light")
    if old_light:
        old_light.hide_viewport = old_light.hide_render = True
    # world
    w = sc.world or bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes.get("Background")
    bg.inputs["Color"].default_value = (0.62, 0.76, 0.92, 1)
    bg.inputs["Strength"].default_value = 1.0
    # camera from south-east
    cam = sc.camera or bpy.data.objects.get("Camera")
    if cam:
        cam.location = (33.0, -24.0, 13.0)
        target = Vector((7.4, 6.4, 3.2))
        cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
        cam.data.lens = 40
        cam.data.clip_end = 500
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    # reference plans hidden by default
    lc = bpy.context.view_layer.layer_collection.children[ROOT].children["FL_Referenz"]
    lc.hide_viewport = True
    coll("Referenz").hide_render = True


def main():
    bp = house_core.default_layout(house_core.build())   # the variant Alternativ is the viewer's only
    make_materials(bp.mat_def)
    reset_collections()
    flush_geometry(bp)
    build_room_names()
    build_references()
    setup_scene()


main()
