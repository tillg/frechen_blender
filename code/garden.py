"""Plants: tall meadow grass around the house (grass_in_front_of_house.png) and green, leafy
shrubs in the two soil beds along the walls (placement after bushes_around_the_house.png).

Lives in its own collection "Garten"; re-running replaces the collection. Where grass grows,
the clump shape and the shrub placements come from the garden layout in house_core.py.
The meadow is a Geometry Nodes scatter of grass-clump instances; the viewport shows 10 %.
Run inside Blender: exec(open(".../code/garden.py").read())
"""
import bpy, bmesh, importlib, math, os, random, sys
from mathutils import Vector, noise

sys.path.insert(0, os.path.join(os.path.dirname(bpy.data.filepath) or PROJECT, "code"))  # this clone: the open .blend's folder (unsaved, headless test: snapshot.py's PROJECT)
import ofen, desk, bad, kueche, gaeste_wc, regal, schrankbett, gaestebad, house_core; importlib.reload(ofen); importlib.reload(desk); importlib.reload(bad); importlib.reload(kueche); importlib.reload(gaeste_wc); importlib.reload(regal); importlib.reload(schrankbett); importlib.reload(gaestebad); importlib.reload(house_core)  # pick up core edits in a long session
from house_core import CELL, DENSITY, density


def collection():
    c = bpy.data.collections.get("Garten")
    if c:
        for ob in list(c.objects):
            me = ob.data
            bpy.data.objects.remove(ob)
            if me and me.users == 0:
                bpy.data.meshes.remove(me)
    else:
        c = bpy.data.collections.new("Garten")
        bpy.context.scene.collection.children.link(c)
    return c


def material(name, build):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes.clear()
    build(m.node_tree)
    return m


def grass_shader(nt):
    N, L = nt.nodes.new, nt.links.new
    out, bsdf = N("ShaderNodeOutputMaterial"), N("ShaderNodeBsdfPrincipled")
    L(bsdf.outputs["BSDF"], out.inputs["Surface"])
    h = N("ShaderNodeAttribute"); h.attribute_name = "h"
    ramp = N("ShaderNodeValToRGB")
    el = ramp.color_ramp.elements
    el[0].position, el[0].color = 0.0, (0.015, 0.04, 0.008, 1)
    el[1].position, el[1].color = 1.0, (0.28, 0.40, 0.07, 1)
    mid = el.new(0.45); mid.color = (0.07, 0.20, 0.025, 1)
    rnd = N("ShaderNodeObjectInfo")
    hs = N("ShaderNodeHueSaturation")
    mad = N("ShaderNodeMath"); mad.operation = "MULTIPLY_ADD"
    mad.inputs[1].default_value, mad.inputs[2].default_value = 0.06, 0.47
    L(h.outputs["Fac"], ramp.inputs["Fac"])
    L(ramp.outputs["Color"], hs.inputs["Color"])
    L(rnd.outputs["Random"], mad.inputs[0]); L(mad.outputs[0], hs.inputs["Hue"])
    L(hs.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.6


def leaf_shader(nt):
    """Green leaves; per-leaf shade from the face attribute "rnd"."""
    N, L = nt.nodes.new, nt.links.new
    out, bsdf = N("ShaderNodeOutputMaterial"), N("ShaderNodeBsdfPrincipled")
    L(bsdf.outputs["BSDF"], out.inputs["Surface"])
    attr = N("ShaderNodeAttribute"); attr.attribute_name = "rnd"
    ramp = N("ShaderNodeValToRGB")
    el = ramp.color_ramp.elements
    el[0].color, el[1].color = (0.012, 0.045, 0.008, 1), (0.10, 0.26, 0.035, 1)
    mid = el.new(0.6); mid.color = (0.035, 0.12, 0.018, 1)
    L(attr.outputs["Fac"], ramp.inputs["Fac"])
    L(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.55


# ---------------------------------------------------------------- meadow
def grass_clump(c, mat, cl):
    """One clump from the layout: 6 curved, tapering blades. Vertex attribute h = 0 root .. 1 tip."""
    me = bpy.data.meshes.new("GA_Grasbuschel")
    me.from_pydata(cl["v"], [], cl["f"])
    me.attributes.new("h", "FLOAT", "POINT").data.foreach_set("value", cl["h"])
    me.materials.append(mat)
    ob = bpy.data.objects.new("GA_Grasbuschel", me)
    c.objects.link(ob)
    ob.hide_viewport = ob.hide_render = True
    return ob


def emitter(c, layout):
    """Grid of CELL quads on the ground, minus cells touching house / terrace / beds / windrose;
    vertex attribute dens = relative grass density (1 near the house, FAR_DENS far away)."""
    x0, x1, y0, y1, z = layout.ground
    rects = layout.no_grass + layout.windrose
    nx, ny = int((x1 - x0) / CELL), int((y1 - y0) / CELL)
    keep = [[not any(a < x0 + (i + 1) * CELL and x0 + i * CELL < b and cc < y0 + (j + 1) * CELL
                     and y0 + j * CELL < d for a, b, cc, d in rects)
             for j in range(ny)] for i in range(nx)]
    vid, v, f, dens = {}, [], [], []

    def vert(i, j):
        if (i, j) not in vid:
            x, y = x0 + i * CELL, y0 + j * CELL
            vid[(i, j)] = len(v)
            v.append((x, y, z))
            dens.append(density(x, y))
        return vid[(i, j)]

    for i in range(nx):
        for j in range(ny):
            if keep[i][j]:
                f.append((vert(i, j), vert(i + 1, j), vert(i + 1, j + 1), vert(i, j + 1)))
    me = bpy.data.meshes.new("GA_Wiese")
    me.from_pydata(v, [], f)
    me.attributes.new("dens", "FLOAT", "POINT").data.foreach_set("value", dens)
    ob = bpy.data.objects.new("GA_Wiese", me)
    c.objects.link(ob)
    return ob


def sock(sockets, name, typ):
    return next(s for s in sockets if s.name == name and s.type == typ and s.enabled)


def scatter_nodes(clump):
    ng = bpy.data.node_groups.get("GA_Wiese_Streuung")
    if ng:
        bpy.data.node_groups.remove(ng)
    ng = bpy.data.node_groups.new("GA_Wiese_Streuung", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    N, L = ng.nodes.new, ng.links.new
    gin, gout = N("NodeGroupInput"), N("NodeGroupOutput")
    dist = N("GeometryNodeDistributePointsOnFaces"); dist.distribute_method = "RANDOM"
    attr = N("GeometryNodeInputNamedAttribute"); attr.data_type = "FLOAT"
    attr.inputs["Name"].default_value = "dens"
    view = N("GeometryNodeIsViewport")
    sw = N("GeometryNodeSwitch"); sw.input_type = "FLOAT"
    sw.inputs["False"].default_value, sw.inputs["True"].default_value = DENSITY, DENSITY * 0.1
    mul = N("ShaderNodeMath"); mul.operation = "MULTIPLY"
    info = N("GeometryNodeObjectInfo"); info.inputs["Object"].default_value = clump
    info.inputs["As Instance"].default_value = True
    inst = N("GeometryNodeInstanceOnPoints")
    rot = N("FunctionNodeRandomValue"); rot.data_type = "FLOAT_VECTOR"
    sock(rot.inputs, "Max", "VECTOR").default_value = (0.15, 0.15, 2 * math.pi)
    sock(rot.inputs, "Min", "VECTOR").default_value = (-0.15, -0.15, 0)
    scl = N("FunctionNodeRandomValue"); scl.data_type = "FLOAT"
    sock(scl.inputs, "Min", "VALUE").default_value = 0.6
    sock(scl.inputs, "Max", "VALUE").default_value = 1.3
    sock(scl.inputs, "Seed", "INT").default_value = 7
    L(gin.outputs[0], dist.inputs["Mesh"])
    L(view.outputs[0], sw.inputs["Switch"])
    L(attr.outputs[0], mul.inputs[0]); L(sw.outputs[0], mul.inputs[1])
    L(mul.outputs[0], dist.inputs["Density"])
    L(dist.outputs["Points"], inst.inputs["Points"])
    L(info.outputs["Geometry"], inst.inputs["Instance"])
    L(sock(rot.outputs, "Value", "VECTOR"), inst.inputs["Rotation"])
    L(sock(scl.outputs, "Value", "VALUE"), inst.inputs["Scale"])
    L(inst.outputs["Instances"], gout.inputs[0])
    return ng


# ---------------------------------------------------------------- shrubs
def bush(c, mat, x, y, r, h):
    """Rounded shrub: dark core blob covered with ~1400 small leaves (diamond quads, facing
    roughly outwards), each leaf with its own shade (face attribute rnd)."""
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=3, radius=1.0)
    seed = Vector((x * 3.1, y * 2.7, 0))
    shape = lambda n: 1 + 0.15 * noise.noise(n * 2.5 + seed) + 0.06 * noise.noise(n * 9 + seed)
    surf = lambda n, k: Vector((n.x * r * k, n.y * r * k, max(n.z, -0.1) * h * k * 0.9 + h * 0.1))
    for v in bm.verts:
        n = v.co.normalized()
        v.co = surf(n, shape(n) * 0.85)
    shades = [0.0] * len(bm.faces)
    for _ in range(1400):
        n = Vector((random.gauss(0, 1), random.gauss(0, 1), random.gauss(0, 1) + 0.35)).normalized()
        p = surf(n, shape(n) * random.uniform(0.86, 1.0))
        out = (n + Vector((random.gauss(0, 0.5), random.gauss(0, 0.5), random.gauss(0, 0.5)))).normalized()
        t1 = out.cross(Vector((0, 0, 1)) if abs(out.z) < 0.9 else Vector((1, 0, 0))).normalized()
        t2 = out.cross(t1)
        sz = random.uniform(0.028, 0.05)
        q = [bm.verts.new(p + t1 * sz), bm.verts.new(p + t2 * sz * 0.45),
             bm.verts.new(p - t1 * sz), bm.verts.new(p - t2 * sz * 0.45)]
        bm.faces.new(q)
        shades.append(random.random() ** 0.8 * (0.6 + 0.4 * max(n.z, 0)))   # lighter on top
    me = bpy.data.meshes.new("GA_Strauch")
    bm.to_mesh(me); bm.free()
    me.attributes.new("rnd", "FLOAT", "FACE").data.foreach_set("value", shades)
    me.materials.append(mat)
    ob = bpy.data.objects.new("GA_Strauch", me)
    ob.location = (x, y, -0.03)
    c.objects.link(ob)


def main():
    layout = house_core.build().garden
    c = collection()
    grass = material("GA_Gras", grass_shader)
    clump = grass_clump(c, grass, layout.clump)
    em = emitter(c, layout)
    mod = em.modifiers.new("Wiese", "NODES")
    mod.node_group = scatter_nodes(clump)
    leaves = material("GA_Blaetter", leaf_shader)
    random.seed(7)                            # leaves: own stream, apart from the layout's
    for x, y, r, h in layout.shrubs:          # groups of three with a gap, like the photo
        bush(c, leaves, x, y, r, h)
    return len(em.data.polygons)


N_CELLS = main()
